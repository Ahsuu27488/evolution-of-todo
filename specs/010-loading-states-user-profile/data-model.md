# Data Model: Loading States & User Profile Enhancement

**Feature**: 010-loading-states-user-profile
**Date**: 2025-01-24
**Status**: Final

## Overview

This document defines the data model changes required to support first/last name fields in the User entity. The model maintains backward compatibility with the existing single `name` field while supporting the new separated fields.

---

## Entity: User

### Description
Represents an application user with authentication credentials and profile information. Extended to support separate first and last name fields with inclusive validation.

### Attributes

| Field | Type | Constraints | Description | Migration Phase |
|-------|------|-------------|-------------|-----------------|
| `id` | UUID | Primary key, auto-generated | Unique user identifier | Existing |
| `email` | VARCHAR(255) | Unique, indexed, required | User's email address for login | Existing |
| `hashed_password` | VARCHAR | Required, bcrypt | Bcrypt hashed password for authentication | Existing |
| `first_name` | VARCHAR(50) | Required after Phase 4, nullable in Phases 1-3 | User's given name | **NEW - Phase 1** |
| `last_name` | VARCHAR(50) | Optional, nullable | User's family name | **NEW - Phase 1** |
| `name` | VARCHAR(100) | Legacy field, retained for compatibility | Original single name field | Existing (kept for migration) |
| `display_name` | COMPUTED | Read-only property | Computed display name (first_name + last_name or first_name or name or email) | **NEW - Phase 2** |
| `created_at` | TIMESTAMPTZ | Required, default=now() | Account creation timestamp | Existing |

### Relationships

| Relationship | Type | Target Entity | Cardinality | Description |
|--------------|------|---------------|-------------|-------------|
| `tasks` | One-to-Many | Task | One user, many tasks | User owns tasks (existing) |
| `task_logs` | One-to-Many | TaskLog | One user, many logs | Audit trail for user actions (existing) |

---

## State Transitions

### User Name Fields Migration

```
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 1: Schema Change (Deployment 1)                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User Table State:                                                  │
│  ┌─────────────┬──────────────┬──────────────┬───────────┐        │
│  │ email       │ name         │ first_name   │ last_name │        │
│  ├─────────────┼──────────────┼──────────────┼───────────┤        │
│  │ existing@   │ johndoe      │ NULL         │ NULL      │        │
│  └─────────────┴──────────────┴──────────────┴───────────┘        │
│                                                                    │
│  Code Behavior:                                                     │
│  - Old code: Reads from 'name' column (unchanged)                  │
│  - New code: Not yet deployed                                      │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 2: Backward-Compatible Code (Deployment 2)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User Table State: Unchanged                                        │
│                                                                    │
│  Code Behavior:                                                     │
│  - Old code: Still reads from 'name'                               │
│  - New code: Uses display_name property (checks first_name,       │
│    falls back to 'name')                                            │
│                                                                    │
│  display_name Property Logic:                                       │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ if first_name exists:                                      │   │
│  │     return f"{first_name} {last_name or ''}".strip()       │   │
│  │ else:                                                      │   │
│  │     return name  # Legacy fallback                         │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 3: Background Migration (Deployment 2 - Async Job)             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User Table State (after migration):                               │
│  ┌─────────────┬──────────────┬──────────────┬───────────┐        │
│  │ email       │ name         │ first_name   │ last_name │        │
│  ├─────────────┼──────────────┼──────────────┼───────────┤        │
│  │ existing@   │ johndoe      │ johndoe      │ NULL      │        │
│  └─────────────┴──────────────┴──────────────┴───────────┘        │
│                                                                    │
│  Migration Logic:                                                  │
│  FOR each user WHERE first_name IS NULL:                           │
│    SET first_name = name  # Legacy value becomes first_name       │
│    SET last_name = NULL    # Per spec clarification               │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 4: Enforce Constraints (Subsequent Release)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User Table State: Unchanged                                        │
│                                                                    │
│  Schema Changes:                                                    │
│  ALTER TABLE users                                                  │
│    ALTER COLUMN first_name SET NOT NULL                            │
│    -- Optionally: DROP COLUMN name (after verification period)    │
│                                                                    │
│  Code Behavior:                                                     │
│  - All code uses display_name property                             │
│  - Legacy 'name' column can be deprecated                          │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Validation Rules

### Frontend Validation (Zod Schema)

```typescript
import { z } from 'zod'

export const signupSchema = z.object({
  email: z.string()
    .email("Invalid email address")
    .min(1, "Email is required")
    .max(255, "Email too long"),

  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .max(100, "Password too long"),

  firstName: z.string()
    .min(1, "First name is required")
    .max(50, "First name must be 50 characters or less")
    .refine(
      (val) => !/<[^>]*>/.test(val),
      "Invalid characters detected"
    )
    .refine(
      (val) => /^\S/.test(val),
      "First name cannot start with a space"
    ),

  lastName: z.string()
    .max(50, "Last name must be 50 characters or less")
    .optional()  // Optional field
    .refine(
      (val) => val === undefined || !/<[^>]*>/.test(val || ''),
      "Invalid characters detected"
    )
    .refine(
      (val) => val === undefined || val === '' || /^\S/.test(val),
      "Last name cannot start with a space"
    )
})

export type SignupInput = z.infer<typeof signupSchema>
```

### Backend Validation (Pydantic/SQLModel)

```python
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class UserCreate(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)
    first_name: str = Field(min_length=1, max_length=50)  # Required
    last_name: Optional[str] = Field(default=None, max_length=50)  # Optional

    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Email must contain @ symbol')
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_names(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if len(v) > 50:
            raise ValueError('Name field must be 50 characters or less')

        # XSS prevention
        if '<' in v or '>' in v:
            raise ValueError('Invalid characters: HTML tags not allowed')

        # Must not start with whitespace
        if v != v.strip():
            raise ValueError('Name cannot start or end with whitespace')

        return v

    @field_validator('last_name')
    @classmethod
    def last_name_allows_empty_string(cls, v: Optional[str]) -> Optional[str]:
        # Allow empty string (treat as None)
        if v == '':
            return None
        return v
```

---

## Display Name Logic

### Computed Property Implementation

```python
# backend/app/models/user.py

class User(SQLModel, table=True):
    """User model with first/last name support"""

    # Primary fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field()

    # Name fields (Phase II)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)

    # Legacy field (kept for migration)
    name: Optional[str] = Field(default=None, max_length=100)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Computed property
    @property
    def display_name(self) -> str:
        """
        Return user's display name with inclusive fallback logic.

        Priority:
        1. first_name + last_name (if both present)
        2. first_name only (if first_name present)
        3. name (legacy field for migrated users)
        4. email (ultimate fallback)

        Examples:
            - ("John", "Doe") → "John Doe"
            - ("Madonna", None) → "Madonna"
            - (None, None, "legacyuser") → "legacyuser"
            - (None, None, None, "user@example.com") → "user@example.com"
        """
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.first_name

        if self.name:
            return self.name

        return self.email
```

### Frontend Type Definitions

```typescript
// frontend/src/lib/types/user.ts

export interface User {
  id: string
  email: string
  firstName: string | null
  lastName: string | null
  displayName: string  // Computed by backend
  createdAt: string
}

// Helper function for display (fallback for legacy data)
export function getDisplayName(user: User): string {
  // Backend provides displayName, but frontend has fallback
  return user.displayName ||
    user.firstName && user.lastName
      ? `${user.firstName} ${user.lastName}`
      : user.firstName || user.email
}
```

---

## Database Schema (PostgreSQL)

### Table Definition

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,

    -- Phase II: New name fields
    first_name VARCHAR(50),  -- Required after Phase 4
    last_name VARCHAR(50),   -- Always optional

    -- Legacy field (kept for migration compatibility)
    name VARCHAR(100),

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT users_first_name_not_empty
        CHECK (first_name IS NULL OR first_name != ''),

    CONSTRAINT users_last_name_not_empty_if_provided
        CHECK (last_name IS NULL OR last_name != '')
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_first_name ON users(first_name) WHERE first_name IS NOT NULL;

-- Comments for documentation
COMMENT ON COLUMN users.first_name IS 'User given name (required after Phase 4, nullable during migration)';
COMMENT ON COLUMN users.last_name IS 'User family name (optional, supports mononyms)';
COMMENT ON COLUMN users.name IS 'Legacy single name field (retained for migration compatibility)';
```

### Migration Script (Alembic)

```python
# alembic/versions/010_add_first_last_name.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '010_add_first_last_name'
down_revision = '009_previous_migration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Phase 1: Add nullable columns without removing legacy field"""
    op.add_column('users',
        sa.Column('first_name', sa.VARCHAR(50), nullable=True)
    )
    op.add_column('users',
        sa.Column('last_name', sa.VARCHAR(50), nullable=True)
    )

    # Add check constraints (will be validated in Phase 4)
    op.execute("""
        ALTER TABLE users
        ADD CONSTRAINT users_first_name_not_empty
        CHECK (first_name IS NULL OR first_name != '')
    """)

    op.execute("""
        ALTER TABLE users
        ADD CONSTRAINT users_last_name_not_empty_if_provided
        CHECK (last_name IS NULL OR last_name != '')
    """)

def downgrade() -> None:
    """Rollback: Remove new columns, keep legacy field"""
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_last_name_not_empty_if_provided")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_first_name_not_empty")
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
```

---

## Entity Relationships Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        User                             │
├─────────────────────────────────────────────────────────┤
│ PK │ id              UUID                               │
│    │ email           VARCHAR(255) UNIQUE                │
│    │ hashed_password VARCHAR                            │
│ ───┼────────────────────────────────────────────────── │
│    │ first_name      VARCHAR(50)        (NEW)           │
│    │ last_name       VARCHAR(50)        (NEW)           │
│    │ name            VARCHAR(100)       (Legacy)        │
│    │ display_name    COMPUTED           (NEW)           │
│ ───┼────────────────────────────────────────────────── │
│    │ created_at      TIMESTAMPTZ                        │
└────────┬────────────────────────────────────────────────┘
         │
         │ 1:N
         ├──────────────────────────────────────────┐
         │                                          │
         ▼                                          ▼
┌──────────────────┐                    ┌──────────────────┐
│      Task        │                    │    TaskLog       │
├──────────────────┤                    ├──────────────────┤
│ PK │ id          │                    │ PK │ id          │
│ FK │ user_id     │◄────────────────────│ FK │ user_id     │
│    │ title       │                    │    │ action       │
│    │ description │                    │    │ timestamp    │
│    │ completed   │                    └──────────────────┘
│    │ created_at  │
└──────────────────┘
```

---

## Data Integrity Rules

### Constraints

1. **Email Uniqueness**: No two users can have the same email address
2. **First Name Required** (Phase 4): After migration, first_name must NOT NULL
3. **Name Field Validation**: HTML tags prohibited (XSS prevention)
4. **Character Limits**: Both name fields max 50 characters
5. **Whitespace Handling**: Names cannot start or end with whitespace

### Triggers (Optional Enhancement)

```sql
-- Auto-trim whitespace on insert/update
CREATE OR REPLACE FUNCTION trim_name_fields() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.first_name IS NOT NULL THEN
        NEW.first_name = TRIM(NEW.first_name);
    END IF;

    IF NEW.last_name IS NOT NULL THEN
        NEW.last_name = TRIM(NEW.last_name);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trim_user_names
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION trim_name_fields();
```

---

## Migration Rollback Strategy

### Safe Rollback at Each Phase

| Phase | Rollback Action | Data Loss Risk | Recovery Time |
|-------|-----------------|----------------|---------------|
| Phase 1 | Drop new columns | None | Instant (ALTER TABLE DROP) |
| Phase 2 | Revert code deployment | None | Instant (git revert) |
| Phase 3 | Re-run migration with corrections | Low (resumable) | Minutes |
| Phase 4 | Make columns nullable again | None | Instant (ALTER TABLE ALTER) |

### Monitoring Points

```python
# Migration progress monitoring
async def get_migration_progress(session: AsyncSession) -> dict:
    """Check how many users have been migrated"""
    total = await session.exec(select(func.count(User.id)))
    migrated = await session.exec(
        select(func.count(User.id)).where(User.first_name.is_not(None))
    )

    return {
        "total_users": total,
        "migrated_users": migrated,
        "progress_percentage": (migrated / total * 100) if total > 0 else 0
    }
```

---

## Summary

**New Entities**: None (extending existing User entity)
**New Fields**: 2 (first_name, last_name)
**Computed Properties**: 1 (display_name)
**Relationships**: No changes (existing relationships preserved)
**Migration Complexity**: Medium (4-phase zero-downtime approach)
**Data Integrity**: Maintained through constraints and validation
**Backward Compatibility**: Full (legacy name field retained)
