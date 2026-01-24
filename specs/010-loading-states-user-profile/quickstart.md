# Quickstart Guide: Loading States & User Profile Enhancement

**Feature**: 010-loading-states-user-profile
**Branch**: `010-loading-states-user-profile`
**Last Updated**: 2025-01-24

## Overview

This guide provides setup instructions and development workflow for implementing dual-ring loading states and first/last name user profile fields.

---

## Prerequisites

### Required Software

- **Python**: 3.13.0 or higher ([Download](https://www.python.org/downloads/))
- **Node.js**: 20.x or higher ([Download](https://nodejs.org/))
- **UV**: Latest Python package manager (`pip install uv`)
- **Git**: For version control

### Required Services

- **Neon Serverless PostgreSQL**: Free account at [https://neon.tech](https://neon.tech)
- **GitHub**: For code repository

---

## Setup Instructions

### 1. Repository Setup

```bash
# Clone repository (if not already done)
git clone https://github.com/YOUR-ORG/evolution-of-todo.git
cd evolution-of-todo

# Checkout feature branch
git checkout 010-loading-states-user-profile

# Verify Python version
python --version  # Should show Python 3.13.0+
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with UV
uv venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required variables:
#   - DATABASE_URL=postgresql://user:pass@host/db
#   - BETTER_AUTH_SECRET=your-secret-key-min-32-chars
#   - JWT_SECRET=your-jwt-secret-min-32-chars

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your configuration
# Required variables:
#   - NEXT_PUBLIC_API_URL=http://localhost:8000
#   - BETTER_AUTH_SECRET=your-secret-key-min-32-chars

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Development Workflow

### Phase 1: Database Schema Changes

1. **Create migration script**:
   ```bash
   cd backend
   alembic revision -m "add_first_last_name"
   ```

2. **Edit migration file**: `alembic/versions/010_add_first_last_name.py`
   - Add nullable `first_name` and `last_name` columns
   - Keep existing `name` column for compatibility
   - Add check constraints

3. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

4. **Verify schema**:
   ```bash
   psql $DATABASE_URL -c "\d users"
   ```

### Phase 2: Backend Model Updates

1. **Update User model**: `backend/src/models/user.py`
   ```python
   class User(SQLModel, table=True):
       first_name: Optional[str] = Field(default=None, max_length=50)
       last_name: Optional[str] = Field(default=None, max_length=50)

       @property
       def display_name(self) -> str:
           if self.first_name:
               if self.last_name:
                   return f"{self.first_name} {self.last_name}"
               return self.first_name
           return self.name or self.email
   ```

2. **Update auth routes**: `backend/src/routes/auth.py`
   - Modify `UserCreate` schema to accept `first_name` (required) and `last_name` (optional)
   - Update signup endpoint validation
   - Update response models to include new fields

3. **Test backend**:
   ```bash
   cd backend
   pytest tests/ -v
   ```

### Phase 3: Frontend Component Updates

1. **Create DualRingSpinner component**: `frontend/src/components/ui/dual-ring-spinner.tsx`
   ```typescript
   export function DualRingSpinner({ className }: { className?: string }) {
     return (
       <div className={cn("dual-ring-spinner", className)}>
         <div className="outer-ring" />
         <div className="inner-ring" />
       </div>
     )
   }
   ```

2. **Add spinner styles**: `frontend/app/globals.css`
   ```css
   .dual-ring-spinner {
     --spinner-size: 40px;
     --ring-width: 3px;
     position: relative;
     width: var(--spinner-size);
     height: var(--spinner-size);
   }

   .outer-ring {
     position: absolute;
     inset: 0;
     border: var(--ring-width) solid var(--custom-primary);
     border-radius: 50%;
     animation: rotate-cw 1.5s linear infinite;
   }

   .inner-ring {
     position: absolute;
     inset: 6px;
     border: var(--ring-width) solid var(--custom-secondary);
     border-radius: 50%;
     animation: rotate-ccw 1s linear infinite;
   }

   @keyframes rotate-cw {
     from { transform: rotate(0deg); }
     to { transform: rotate(360deg); }
   }

   @keyframes rotate-ccw {
     from { transform: rotate(360deg); }
     to { transform: rotate(0deg); }
   }
   ```

3. **Update signup form**: `frontend/components/auth/signup-form.tsx`
   - Add `firstName` and `lastName` fields
   - Mark `firstName` as required
   - Update validation schema

4. **Update dashboard**: `frontend/components/dashboard/dashboard-content.tsx`
   - Integrate `DualRingSpinner` with TanStack Query loading states
   - Add inline error card with retry button

5. **Update header**: `frontend/components/layout/user-nav.tsx`
   - Display `displayName` instead of `name`
   - Handle optional last name

6. **Update user types**: `frontend/lib/types/user.ts`
   - Add `firstName`, `lastName`, `displayName` to User interface

7. **Test frontend**:
   ```bash
   cd frontend
   npm test
   ```

### Phase 4: Background Migration

1. **Create migration script**: `backend/src/services/migration.py`
   ```python
   async def migrate_user_names(session: AsyncSession):
       result = await session.exec(
           select(User).where(User.first_name.is_(None))
       )
       for user in result:
           user.first_name = user.name
           user.last_name = None
       await session.commit()
   ```

2. **Run migration**:
   ```bash
   cd backend
   python -m src.services.migration
   ```

3. **Verify migration**:
   ```bash
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM users WHERE first_name IS NULL;"
   ```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_user_model.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run with coverage
npm test -- --coverage
```

### Manual Testing Checklist

**Loading States**:
- [ ] Navigate to dashboard → see dual-ring spinner
- [ ] Wait for tasks to load → spinner fades out smoothly
- [ ] Click "Pending" tab → see brief spinner
- [ ] Click "Done" tab → see brief spinner
- [ ] Disconnect network → see error card with retry button
- [ ] Click retry → spinner reappears

**User Profile**:
- [ ] Navigate to signup → see first name (required) and last name (optional) fields
- [ ] Submit with only first name → account created successfully
- [ ] Submit with first and last name → both stored correctly
- [ ] Submit without first name → validation error shown
- [ ] Sign in → see correct name in header dropdown
- [ ] View profile → see full name displayed

**Migration**:
- [ ] Existing user signs in → name displays correctly
- [ ] Background migration completes → legacy names converted to first_name
- [ ] New user signs up → uses new name fields
- [ ] Zero service interruption during migration

---

## Troubleshooting

### Backend Issues

**Problem**: Migration fails with "column already exists"
```bash
# Solution: Check current migration version
alembic current

# Rollback if needed
alembic downgrade -1

# Re-run migration
alembic upgrade head
```

**Problem**: Tests fail with "AttributeError: 'User' object has no attribute 'first_name'"
```bash
# Solution: Ensure migrations applied
alembic upgrade head

# Reset database (WARNING: destroys data)
dropdb your_database_name
createdb your_database_name
alembic upgrade head
```

### Frontend Issues

**Problem**: Spinner not visible
```css
/* Solution: Check z-index and positioning */
.dual-ring-spinner {
  z-index: 10;
  position: relative;
}
```

**Problem**: Name not displaying in header
```typescript
// Solution: Check user object structure
console.log(user)  // Should have firstName, lastName, displayName
```

### Performance Issues

**Problem**: Spinner flickers
```typescript
// Solution: Add minimum display duration
const [showSpinner, setShowSpinner] = useState(false)
const MIN_DISPLAY_DURATION = 400  // ms
```

---

## Deployment

### Backend Deployment

1. **Build Docker image**:
   ```bash
   cd backend
   docker build -t todo-backend:010 .
   ```

2. **Tag and push**:
   ```bash
   docker tag todo-backend:010 registry.example.com/todo-backend:010
   docker push registry.example.com/todo-backend:010
   ```

3. **Run migrations in production**:
   ```bash
   kubectl exec -it deployment/todo-backend -- alembic upgrade head
   ```

### Frontend Deployment

1. **Build production bundle**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to Vercel**:
   ```bash
   vercel --prod
   ```

---

## Rollback Procedures

### Immediate Rollback

**Frontend**:
```bash
git revert <commit-hash>
git push
# Vercel auto-deploys
```

**Backend**:
```bash
git revert <commit-hash>
git push
# CI/CD auto-deploys to staging/production
```

### Database Rollback

```bash
# Rollback to previous migration
alembic downgrade -1

# Verify data integrity
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
```

---

## Success Criteria Verification

### SC-001: Loading animation appears within 100ms
```javascript
// Test with browser DevTools
performance.mark('fetch-start')
// ... trigger data fetch
performance.mark('spinner-visible')
performance.measure('spinner-time', 'fetch-start', 'spinner-visible')
console.log(performance.getEntriesByName('spinner-time')[0].duration) // Should be < 100ms
```

### SC-002: Animation fades within 300ms
```css
/* Verify transition duration */
.dual-ring-spinner.fade-out {
  transition: opacity 300ms ease-out;  /* Should be 300ms */
}
```

### SC-004: 100% of signups include first name
```sql
-- Verify no NULL first_name in new signups
SELECT COUNT(*) FROM users
WHERE created_at > '2025-01-24'
  AND first_name IS NULL;
-- Should return 0
```

### SC-005: Zero downtime during migration
```bash
# Monitor uptime during migration
# Verify response times stay < 200ms P95
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/auth/me
```

---

## Additional Resources

- **Feature Specification**: `specs/010-loading-states-user-profile/spec.md`
- **Implementation Plan**: `specs/010-loading-states-user-profile/plan.md`
- **Data Model**: `specs/010-loading-states-user-profile/data-model.md`
- **API Contracts**: `specs/010-loading-states-user-profile/contracts/`
- **Research Decisions**: `specs/010-loading-states-user-profile/research.md`
- **Project Constitution**: `.specify/memory/constitution.md`

---

## Getting Help

1. **Check documentation**: Read all linked docs above
2. **Review tests**: Check test files for usage examples
3. **Context7 lookup**: Use Context7 MCP for library documentation
4. **Ask questions**: Use `/sp.clarify` for spec ambiguities

## Checklist

Before marking this feature complete:

- [ ] All backend tests passing
- [ ] All frontend tests passing
- [ ] Manual testing checklist complete
- [ ] Zero service interruption during migration
- [ ] All 8 success criteria verified
- [ ] Code committed to feature branch
- [ ] PHR created and documented
- [ ] Ready for `/sp.tasks` command
