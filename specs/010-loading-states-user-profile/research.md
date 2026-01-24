# Technical Research: Loading States & User Profile Enhancement

**Feature**: 010-loading-states-user-profile
**Date**: 2025-01-24
**Status**: Complete

## Overview

This document captures technical research findings and architectural decisions for implementing dual-ring loading states and first/last name user profile fields. All decisions align with the Phase II full-stack architecture and maintain backward compatibility.

---

## Research Area 1: Loading Animation Implementation

### Decision: Pure CSS Dual-Ring Spinner

**Choice**: Implement dual-ring spinner using CSS keyframe animations without JavaScript animation libraries.

**Rationale**:
- **Performance**: CSS animations run on compositor thread, no JS overhead
- **Simplicity**: No additional dependencies (Framer Motion used for component transitions, not spinner)
- **Theming**: Direct CSS custom property integration with existing `--custom-primary` and `--custom-secondary` colors
- **Maintainability**: Standard CSS patterns, well-understood by frontend developers

**Alternatives Considered**:
1. **Framer Motion spinner**: Rejected - Adds unnecessary complexity for continuous rotation, Framer Motion better suited for layout transitions
2. **SVG with JavaScript**: Rejected - More complex than CSS, harder to theme dynamically
3. **Lottie animation**: Rejected - Additional dependency, larger bundle size, overkill for simple spinner
4. **skeleton enhancement**: Rejected - Spec requires creative animation, not subtle skeleton improvement

**Implementation Details**:
```css
/* Dual-ring spinner using CSS custom properties */
@keyframes rotate-cw { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes rotate-ccw { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }

.dual-ring-spinner {
  --spinner-size: 40px;
  --ring-width: 3px;
  --outer-color: var(--custom-primary);  /* Neon cyan #00f5ff */
  --inner-color: var(--custom-secondary); /* Neon purple #a855f7 */
}

.outer-ring {
  animation: rotate-cw 1.5s linear infinite;
}

.inner-ring {
  animation: rotate-ccw 1s linear infinite;
}
```

**Performance Targets**:
- Visible within 100ms of data fetch (SC-001)
- Fade-out within 300ms of data arrival (SC-002)
- Minimum 400ms display duration to prevent flash (FR-005)

### Decision: Inline Error Card for Loading Failures

**Choice**: Display error card inline within task list area with retry button.

**Rationale**:
- **Context**: Error appears where user expected content (task list)
- **Non-blocking**: Doesn't interrupt other dashboard interactions
- **Actionable**: Clear retry button to re-initiate request
- **UX Pattern**: Matches common error handling patterns (GitHub, Twitter, etc.)

**Alternatives Considered**:
1. **Modal dialog**: Rejected - Too disruptive for single-component failure
2. **Toast notification**: Rejected - Easy to miss, no context of what failed
3. **Full-page error**: Rejected - Overkill for non-critical component failure
4. **Silent retry**: Rejected - Users need visibility into failures

**Implementation Details**:
```typescript
// Error state component
interface LoadingErrorProps {
  message: string;
  onRetry: () => void;
}

// Usage in dashboard-content.tsx
{isError && (
  <LoadingErrorCard
    message="Unable to load tasks. Please check your connection."
    onRetry={() => refetch()}
  />
)}
```

---

## Research Area 2: Database Schema Migration Strategy

### Decision: Four-Phase Zero-Downtime Migration

**Choice**: Implement multi-phase migration using alembic with backward compatibility throughout.

**Rationale**:
- **Zero downtime**: Service remains fully available (SC-005)
- **Safety**: Each phase can be tested and rolled back independently
- **Data integrity**: Legacy data preserved, no information loss
- **Industry standard**: Pattern used by GitHub, Stripe, and other large-scale services

**Alternatives Considered**:
1. **Single ALTER TABLE with downtime**: Rejected - Violates SC-005 zero-downtime requirement
2. **Create new table and swap**: Rejected - More complex, requires foreign key updates
3. **Application-level migration**: Rejected - Slower, harder to rollback, doesn't scale
4. **Live migration with accepted errors**: Rejected - Poor UX, data inconsistency risk

**Implementation Phases**:

#### Phase 1: Add Nullable Columns (Deployment 1)
```sql
ALTER TABLE users ADD COLUMN first_name VARCHAR(50);
ALTER TABLE users ADD COLUMN last_name VARCHAR(50);
-- Keep existing 'name' column
```
- Old code: Reads from `name` column
- New code: Checks if `first_name` exists, falls back to `name`

#### Phase 2: Deploy Backward-Compatible Code (Deployment 2)
```python
# User model with property for backward compatibility
class User(SQLModel, table=True):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: str  # Legacy field, not removed

    @property
    def display_name(self) -> str:
        if self.first_name:
            return f"{self.first_name} {self.last_name or ''}".strip()
        return self.name  # Fallback to legacy
```
- All endpoints use `display_name` property
- Frontend displays `first_name + " " + last_name` if available, otherwise `name`

#### Phase 3: Background Migration Job (Deployment 2 - Background Task)
```python
async def migrate_user_names(session: AsyncSession):
    """Copy legacy name to first_name for existing users"""
    result = await session.exec(
        select(User).where(User.first_name.is_(None))
    )
    for user in result:
        user.first_name = user.name  # Legacy name becomes first_name
        user.last_name = None  # Leave null per spec clarification
    await session.commit()
```
- Runs asynchronously after deployment
- Processes records in batches to avoid locking
- Resumable if interrupted

#### Phase 4: Enforce Constraints (Subsequent Release)
```sql
ALTER TABLE users ALTER COLUMN first_name SET NOT NULL;
-- Optionally drop 'name' column after verification period
```
- Only after 95%+ migration success confirmed
- Monitored for rollback readiness

### Decision: Use Alembic for Schema Versioning

**Choice**: Leverage existing alembic setup for database migrations.

**Rationale**:
- **Established pattern**: Already in use for Phase II database schema
- **Rollback support**: Built-in downgrade paths
- **Branching**: Supports parallel development with merge resolution
- **Production-ready**: Battle-tested at scale

**Implementation Details**:
```bash
# Generate migration
alembic revision -m "add_first_last_name"

# Output: alembic/versions/010_add_first_last_name.py
```

---

## Research Area 3: Name Field Validation Strategy

### Decision: Inclusive Name Validation (First Name Required, Last Name Optional)

**Choice**: Require first name, make last name optional to support mononyms (e.g., "Madonna", "Prince").

**Rationale**:
- **Inclusivity**: Respect cultural naming conventions (mononyms, binomial, patronymic)
- **Data quality**: At least one name field required for display
- **UX flexibility**: Users can provide full name or single name
- **International**: Supports diverse global naming patterns

**Alternatives Considered**:
1. **Both fields required**: Rejected - Excludes mononym users, not inclusive
2. **Either field sufficient**: Rejected - Confusing UX, harder to display consistently
3. **Optional for both**: Rejected - Risk of empty names, poor UX
4. **Placeholder last name**: Rejected - Degrades data quality ("Not Set" appears unprofessional)

**Validation Rules**:
```typescript
// Frontend validation (Zod schema)
const signupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  firstName: z.string()
    .min(1, "First name is required")
    .max(50, "First name must be 50 characters or less")
    .refine(val => !/<[^>]*>/.test(val), "Invalid characters"), // XSS prevention
  lastName: z.string()
    .max(50, "Last name must be 50 characters or less")
    .optional()  // Optional field
});
```

```python
# Backend validation (SQLModel + Pydantic)
from typing import Optional
from pydantic import field_validator

class UserCreate(SQLModel):
    email: str
    password: str
    first_name: str  # Required
    last_name: Optional[str] = None  # Optional

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) > 50:
            raise ValueError('Name field must be 50 characters or less')
        if '<' in v or '>' in v:
            raise ValueError('Invalid characters')
        return v
```

**Display Logic**:
```python
# Backend: Computed display_name property
@property
def display_name(self) -> str:
    """Return user's display name with inclusive logic"""
    if self.first_name and self.last_name:
        return f"{self.first_name} {self.last_name}"
    if self.first_name:
        return self.first_name
    return self.email  # Ultimate fallback
```

---

## Research Area 4: Frontend Loading State Integration

### Decision: TanStack Query Loading State Integration

**Choice**: Leverage existing TanStack Query (React Query) infrastructure for loading states.

**Rationale**:
- **Established pattern**: Already used for `useTaskFilters` hook
- **Built-in states**: `isLoading`, `isError`, `data` available out-of-box
- **Caching**: Automatic cache management reduces redundant fetches
- **Retry logic**: Built-in retry with configurable backoff

**Implementation Details**:
```typescript
// dashboard-content.tsx
import { useQuery } from '@tanstack/react-query'
import { DualRingSpinner } from '@/components/ui/dual-ring-spinner'

export function DashboardContent() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['tasks', filters.status, filters.priority],
    queryFn: () => api.getTasks({ status: filters.status }),
  })

  if (isLoading) {
    return <DualRingSpinner />  // Centered in task list area
  }

  if (isError) {
    return <LoadingErrorCard message="Unable to load tasks" onRetry={() => refetch()} />
  }

  return <TaskList tasks={data.tasks} />
}
```

**Minimum Duration Handling**:
```typescript
// Use timeout to prevent flash
const [showLoading, setShowLoading] = useState(false)
const minLoadingDuration = 400  // ms

useEffect(() => {
  if (isLoading) {
    const timer = setTimeout(() => setShowLoading(true), 100)  // 100ms delay
    return () => clearTimeout(timer)
  } else {
    const timer = setTimeout(() => setShowLoading(false), minLoadingDuration)
    return () => clearTimeout(timer)
  }
}, [isLoading])
```

---

## Research Area 5: API Contract Updates

### Decision: OpenAPI 3.1 Specification for Updated Endpoints

**Choice**: Document updated authentication endpoints with OpenAPI 3.1 spec.

**Rationale**:
- **Type safety**: Auto-generate TypeScript types from OpenAPI spec
- **Documentation**: Clear API contract for frontend/backend integration
- **Validation**: Request/response validation against schema
- **Testing**: Generate mock servers for testing

**Updated Endpoints**:

1. **POST /api/auth/signup** - Accept first_name (required), last_name (optional)
2. **GET /api/auth/me** - Return first_name, last_name, display_name
3. **GET /api/auth/token** - Return user object with new name fields
4. **GET /api/users/{id}** - Return first_name, last_name separately
5. **Internal: /api/migrate-names** - Background migration trigger

**Contract Example**:
```yaml
# /contracts/openapi.yaml (partial)
paths:
  /api/auth/signup:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password, firstName]
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
                firstName:
                  type: string
                  minLength: 1
                  maxLength: 50
                lastName:
                  type: string
                  maxLength: 50
      responses:
        201:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserPublic'
```

---

## Research Area 6: Testing Strategy

### Decision: Multi-Level Testing Approach

**Choice**: Combine unit, integration, and E2E tests for comprehensive coverage.

**Rationale**:
- **Unit tests**: Fast feedback on component logic
- **Integration tests**: Verify backend API contracts
- **E2E tests**: Validate complete user flows
- **Acceptance criteria**: Every spec scenario mapped to test

**Test Coverage**:

#### Frontend Tests
```typescript
// dual-ring-spinner.test.tsx
describe('DualRingSpinner', () => {
  it('renders with correct colors', () => {
    render(<DualRingSpinner />)
    expect(screen.getByTestId('outer-ring')).toHaveStyle({
      borderColor: 'var(--custom-primary)'
    })
  })

  it('has minimum display duration', async () => {
    const { rerender } = render(<DualRingSpinner show={true} />)
    // Test 400ms minimum duration
  })
})

// signup-form.test.tsx
describe('SignupForm', () => {
  it('requires first name', async () => {
    // Test validation
  })

  it('accepts only first name (mononym)', async () => {
    // Test optional last name
  })
})
```

#### Backend Tests
```python
# test_user_model.py
def test_user_display_name_with_both_fields():
    user = User(first_name="John", last_name="Doe")
    assert user.display_name == "John Doe"

def test_user_display_name_first_name_only():
    user = User(first_name="Madonna", last_name=None)
    assert user.display_name == "Madonna"

def test_user_display_name_legacy_fallback():
    user = User(name="legacyuser", first_name="legacyuser", last_name=None)
    assert user.display_name == "legacyuser"
```

---

## Summary of Technical Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| **Loading Animation** | Pure CSS dual-ring spinner | Performance, simplicity, theming |
| **Error Handling** | Inline error card with retry | Contextual, actionable, non-blocking |
| **Migration Strategy** | 4-phase zero-downtime with alembic | No service interruption, safe rollback |
| **Name Validation** | First name required, last name optional | Inclusive, data quality, flexible |
| **Loading Integration** | TanStack Query loading states | Leverages existing patterns |
| **API Documentation** | OpenAPI 3.1 specification | Type safety, clear contracts |
| **Testing** | Multi-level (unit/integration/E2E) | Comprehensive coverage |

## Dependencies Requiring Context7 Lookup

Per Constitution §III.1, the following libraries MUST be queried via Context7 before implementation:

1. **Framer Motion 12+** - For component fade transitions (not spinner itself)
2. **Alembic 1.13+** - For database migration scripts
3. **TanStack Query v5+** - For loading state integration patterns
4. **Zod 3+** - For frontend schema validation
5. **FastAPI 0.115+** - For Pydantic validation integration
6. **SQLModel 0.014+** - For model property definitions

**Compliance**: All implementation tasks will reference Context7 documentation before writing code.

---

## Unresolved Questions

**None** - All technical decisions finalized and documented.
