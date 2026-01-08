# Implementation Plan: Fix Authentication Integration

**Branch**: `001-fix-auth-integration`
**Date**: 2025-12-30
**Spec**: [spec.md](./spec.md)

## Summary

Fix Better Auth and FastAPI backend authentication integration. The backend is incorrectly trying to parse Better Auth session tokens instead of verifying JWT tokens. The frontend is missing the JWT plugin configuration. Implement proper token verification in FastAPI using jose library and add comprehensive error handling for debugging.

## Technical Context

### Extracted from Feature Spec

**Primary Requirements**:
- FR-001: Better Auth JWT Configuration with HS256 algorithm and 7-day expiration
- FR-002: Backend JWT verification using shared BETTER_AUTH_SECRET
- FR-003: Token retrieval and propagation via `/api/auth/token` endpoint
- FR-004: Protected route middleware for `/dashboard`
- FR-005: Error handling and logging for debugging
- FR-006: CORS configuration for cross-origin requests
- FR-007: User isolation (user_id in URL must match JWT subject)

**Current Issues Identified**:
1. Backend `app/auth.py` parses `session_token=<user_id>` format instead of JWT verification
2. Backend uses hardcoded secret check instead of JWT signature verification
3. Frontend `lib/auth.ts` is missing `jwt()` plugin configuration
4. Frontend `app/actions/tasks.ts` attempts to call `/api/auth/token` (JWT-only endpoint) instead of using `getSession` which returns token in headers
5. No try-catch error blocks in API client
6. Missing environment variable validation for required secrets

## Architecture

### Current State (Before Fix)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Next.js Frontend (Port 3000)                          │
│                                                                          │
│  ┌─────────────────────┐  ┌────────────────────────────────────────────────────────┐  │
│  │                   │  │                                             │  │
│  │  Better Auth Server│  │         FastAPI Backend (Port 8000)        │  │
│  │  - Uses Session     │  │                                             │  │
│  │    Tokens          │  │         - Routes: /api/{user_id}/tasks         │  │
│  │                   │  │         - Auth: Parses session tokens            │  │
│  │                   │  │                                             │  │
│  │                   │  │         - DB: Neon PostgreSQL (shared)          │  │
│  └─────────────────────┘  └─────────────────────────────────────────────────────────┘  │
│                                                                          │
│                    ❌ Issues:                                                │
│                    1. Backend expects session tokens, sends JWT        │
│                    2. Frontend missing JWT plugin config              │
│                    3. No proper error handling                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Target State (After Fix)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Next.js Frontend (Port 3000)                          │
│                                                                          │
│  ┌─────────────────────┐  ┌────────────────────────────────────────────────────────┐  │
│  │                   │  │                                             │  │
│  │  Better Auth Server│  │         FastAPI Backend (Port 8000)        │  │
│  │  - Uses JWT         │  │         - Routes: /api/{user_id}/tasks         │  │
│  │    Tokens           │  │                                             │  │
│  │                   │  │         - Auth: Verifies JWT signature        │  │
│  │                   │  │                                             │  │
│  │                   │  │         - DB: Neon PostgreSQL (shared)          │  │
│  └─────────────────────┘  └─────────────────────────────────────────────────────────┘  │
│                    ✅ Working:                                              │
│                    1. JWT plugin enabled on frontend                 │
│                    2. Backend verifies JWT with jose                │
│                    3. Comprehensive error handling                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
specs/001-fix-auth-integration/
├── spec.md                 # This file
├── checklists/
│   └── requirements.md   # Quality checklist
└── plan.md                 # This file

backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLModel models
│   ├── db.py                # Database connection
│   ├── auth.py              # FIX: Implement JWT verification
│   └── routes/
│       ├── __init__.py
│       └── tasks.py           # Task CRUD endpoints
├── .env                    # DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS
├── requirements.txt           # Add: python-jose, python-dotenv
└── pyproject.toml

frontend/
├── lib/
│   ├── auth.ts              # FIX: Add jwt() plugin
│   ├── auth-client.ts       # Client helpers
│   ├── api.ts              # FIX: Add error handling
│   └── utils.ts
├── app/
│   ├── dashboard/
│   │   └── page.tsx       # Server component
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx    # Client component
│   │   └── signup/
│   │       └── page.tsx
│   ├── actions/
│   │   └── tasks.ts         # FIX: Use getSession for token
│   └── api/
│       └── auth/[...all]/
│           └── route.ts     # Better Auth API handler
├── middleware.ts              # Route protection (keep as-is)
├── .env.local               # DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL
└── package.json              # Add: python-jose-cryptography
```

## Constitution Check

- [x] No violations detected
- [x] Authentication uses industry-standard JWT with HS256
- [x] Database is shared via connection string (Best Auth requirement)
- [x] Environment variables are properly used
- [x] Error handling follows security best practices

## Phase 0: Research & Analysis

**Completed**:
- Analyzed existing backend authentication implementation
- Analyzed existing frontend authentication implementation
- Researched Better Auth JWT plugin documentation
- Identified root causes of authentication failures

**Findings**:
1. Better Auth uses **session tokens** by default, NOT JWT
2. JWT plugin must be explicitly enabled in auth.ts
3. `/api/auth/token` endpoint only exists when JWT plugin is enabled
4. Backend should use `python-jose` library for JWT verification, not manual parsing

## Phase 1: Frontend Configuration

### 1.1 Enable Better Auth JWT Plugin

**File**: `frontend/lib/auth.ts`

**Changes Required**:
```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL environment variable is not set")
}

if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error("BETTER_AUTH_SECRET environment variable is not set")
}

export const auth = betterAuth({
  database: {
    connectionString: process.env.DATABASE_URL,
  },
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  plugins: [
    jwt({
      algorithm: "HS256",
      expiresIn: "7d",
      issuer: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
      audience: [process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"],
    }),
    nextCookies(), // Enables cookies in Server Actions
  ],
})
```

**Rationale**:
- JWT plugin generates and verifies JWT tokens
- Tokens can be retrieved via `/api/auth/token` endpoint
- Token included in `set-auth-jwt` response header from `getSession`

### 1.2 Update API Client Error Handling

**File**: `frontend/lib/api.ts`

**Changes Required**:
```typescript
import type { Task, TaskCreate, TaskList, TaskUpdate } from "@/types/task"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface ApiError {
  detail: string
  statusCode: number
}

interface ApiErrorResponse {
  error: string
  message?: string
  details?: any
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })

    if (!response.ok) {
      let errorDetail: string
      let statusCode = response.status

      try {
        const error: ApiErrorResponse = await response.json()
        errorDetail = error.error || error.detail || `Request failed with status ${statusCode}`
        statusCode = error.statusCode || statusCode
      } catch {
        errorDetail = `Request failed with status ${statusCode}`
      }

      console.error(`[API Error ${statusCode}]`, {
        url,
        method: options.method,
        status: statusCode,
        error: errorDetail,
      })

      throw new Error(errorDetail)
    }

    return response.json()
  }
```

**Rationale**:
- Try-catch ensures errors are handled gracefully
- Detailed error logging for debugging
- Client receives both error status and message

## Phase 2: Backend JWT Verification

### 2.1 Implement JWT Verification with python-jose

**New File**: `backend/app/jwt_middleware.py`

**Implementation**:
```python
"""
JWT verification middleware using python-jose library.

Verifies JWT tokens issued by Better Auth and extracts user ID.
"""
import os
from typing import Optional
from datetime import datetime, timedelta

from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from dotenv import load_dotenv

load_dotenv()

# Configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set")

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 7 * 24 * 60  # 7 days in seconds
JWT_ISSUER = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
JWT_AUDIENCE = [JWT_ISSUER]

security = HTTPBearer()


class JWTVerificationResult:
    """Result of JWT verification with detailed error information."""
    user_id: str
    expires_at: Optional[datetime]
    error_code: str
    error_message: str

    def is_valid(self) -> bool:
        return self.error_code == "OK"


async def verify_jwt_token(token: str) -> JWTVerificationResult:
    """
    Verify JWT token issued by Better Auth.

    Args:
        token: JWT token string from Authorization header

    Returns:
        JWTVerificationResult with user_id and validation status

    Raises:
        HTTPException: 401 for invalid/expired tokens
    """
    if not token:
        return JWTVerificationResult(
            user_id="",
            expires_at=None,
            error_code="MISSING_TOKEN",
            error_message="No authorization token provided"
        )

    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["iss", "sub", "aud", "exp"],
                "issuer": JWT_ISSUER,
                "audience": JWT_AUDIENCE,
            }
        )

        user_id = payload.get("sub")
        if not user_id:
            return JWTVerificationResult(
                user_id="",
                expires_at=None,
                error_code="INVALID_PAYLOAD",
                error_message="Invalid JWT payload: missing user ID"
            )

        # Check expiration
        expires_at = datetime.fromtimestamp(payload.get("exp", 0))
        now = datetime.utcnow()

        if expires_at <= now:
            return JWTVerificationResult(
                user_id=user_id,
                expires_at=expires_at,
                error_code="TOKEN_EXPIRED",
                error_message=f"Token expired at {expires_at.isoformat()}"
            )

        # Return successful verification
        return JWTVerificationResult(
            user_id=user_id,
            expires_at=expires_at,
            error_code="OK",
            error_message=""
        )

    except JWTError as e:
        return JWTVerificationResult(
            user_id="",
            expires_at=None,
            error_code="INVALID_SIGNATURE",
            error_message=f"Invalid JWT signature: {str(e)}"
        )
    except Exception as e:
        return JWTVerificationResult(
            user_id="",
            expires_at=None,
            error_code="VERIFICATION_ERROR",
            error_message=f"Token verification failed: {str(e)}"
        )


def get_current_user_id(
    payload: JWTVerificationResult = Security(verify_jwt_token),
) -> str:
    """
    Extract user ID from verified JWT token.

    Raises:
        HTTPException: 401 if token is invalid or expired

    Args:
        payload: Verified JWT result from verify_jwt_token

    Returns:
        User ID string
    """
    result = payload.credentials

    if not result.is_valid():
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": result.error_code,
                "message": result.error_message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    return result.user_id
```

**Rationale**:
- Uses industry-standard `python-jose` library
- Proper JWT signature verification with HS256 algorithm
- Checks token expiration
- Validates issuer and audience claims
- Returns detailed error information for debugging

### 2.2 Replace Old Auth Implementation

**File**: `backend/app/auth.py`

**Changes Required**:
Replace entire file content with:

```python
"""Authentication middleware imports and configuration.

Deprecates old session token parsing.
Now uses JWT verification via python-jose middleware.
"""
from app.jwt_middleware import (
    get_current_user_id,
    BETTER_AUTH_SECRET,
    verify_jwt_token,
    JWTVerificationResult
)

# Re-export for backward compatibility
verify_session = get_current_user_id
get_current_user_id = get_current_user_id
```

**Rationale**:
- Maintains backward compatibility with existing imports
- Delegates JWT verification to dedicated middleware
- Old implementation deprecated and will be removed after migration

### 2.3 Update Task Routes Logging

**File**: `backend/app/routes/tasks.py`

**Changes Required**:
```python
"""Task CRUD endpoints with enhanced error logging and validation."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select

from app.db import get_session
from app.auth import get_current_user_id
from app.models import Task, TaskCreate, TaskList, TaskPublic, TaskUpdate


router = APIRouter(prefix="/api/{user_id}/tasks", tags=["Tasks"])


def verify_user_access(user_id: str, current_user: str) -> None:
    """Verify that URL user_id matches authenticated user with detailed logging.

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "USER_ID_MISMATCH",
                "message": f"User ID mismatch: {user_id} != {current_user}",
                "expected_user_id": current_user,
                "provided_user_id": user_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


def get_task_or_404(
    task_id: int,
    user_id: str,
    session: Session
) -> Task:
    """Get a task by ID, ensuring it belongs to the user with detailed logging.

    Raises:
        HTTPException: 404 if task not found or doesn't belong to user
    """
    task = session.exec(
        select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "TASK_NOT_FOUND",
                "message": f"Task {task_id} not found for user {user_id}",
                "user_id": user_id,
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    return task


@router.get("", response_model=TaskList)
def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> TaskList:
    """List all tasks for the authenticated user with detailed logging."""
    try:
        # Log the request details for debugging
        import sys
        sys.stderr.write(f"[INFO] List tasks request - user_id: {user_id}, authenticated_as: {current_user}\n")

        verify_user_access(user_id, current_user)

        tasks = session.exec(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        ).all()

        return TaskList(
            tasks=[TaskPublic.model_validate(t) for t in tasks],
            total=len(tasks),
        )

    except Exception as e:
        # Log unexpected errors
        import sys
        import traceback
        sys.stderr.write(f"[ERROR] List tasks failed: {str(e)}\n")
        sys.stderr.write(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to retrieve tasks",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


@router.post("", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: str = Depends(get_current_user_id),
    session: Session = Depends(get_session),
) -> TaskPublic:
    """Create a new task with detailed logging and validation."""
    import sys

    try:
        sys.stderr.write(f"[INFO] Create task request - user_id: {user_id}\n")

        verify_user_access(user_id, current_user)

        # Validate input
        if not task_data.title or not task_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": "Title is required and cannot be empty",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        if task_data.description and len(task_data.description) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "message": "Description cannot exceed 1000 characters",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        task = Task(
            user_id=user_id,
            title=task_data.title.strip(),
            description=task_data.description.strip() if task_data.description else None,
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        sys.stderr.write(f"[INFO] Task created - id: {task.id}, title: {task.title}\n")

        return TaskPublic.model_validate(task)

    except HTTPException:
        # Re-raise HTTPException with context
        raise
    except Exception as e:
        import sys
        import traceback
        sys.stderr.write(f"[ERROR] Create task failed: {str(e)}\n")
        sys.stderr.write(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_ERROR",
                "message": "Failed to create task",
                "details": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
```

**Rationale**:
- Added comprehensive logging for debugging
- Input validation with detailed error messages
- Full traceback logging for server errors
- Structured error responses with error codes

### 2.4 Update requirements.txt

**File**: `backend/requirements.txt`

**Add dependencies**:
```text
fastapi>=0.104.0
sqlmodel>=0.0.12
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
psycopg2-binary>=2.9.0
psycopg>=2.9.0
```

**Rationale**:
- python-jose[cryptography] is the recommended library for JWT operations
- python-dotenv for environment variable loading
- psycopg2 for PostgreSQL async operations

### 2.5 Update Frontend Package Dependencies

**File**: `frontend/package.json`

**Add dependencies**:
```json
{
  "dependencies": {
    "python-jose-cryptography": "^3.3.0"
  }
}
```

**Rationale**:
- Required for verifying backend JWT responses in frontend (optional, for advanced validation)

## Phase 3: Testing

### 3.1 Unit Tests for JWT Verification

**New File**: `backend/tests/test_jwt_middleware.py`

```python
"""Unit tests for JWT verification middleware."""
import pytest
from datetime import datetime, timedelta
from app.jwt_middleware import (
    verify_jwt_token,
    JWTVerificationResult,
    JWT_EXPIRATION_MINUTES,
    BETTER_AUTH_SECRET,
    JWT_ISSUER,
)

# Test secret for testing
TEST_SECRET = "test-secret-key-for-jwt-verification-only"


def test_verify_valid_token():
    """Test verification of a valid JWT token."""
    import jose

    # Create a valid token
    now = datetime.utcnow()
    exp = now + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": "test-user-123",
        "iss": JWT_ISSUER,
        "aud": JWT_ISSUER,
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
    }

    token = jose.encode(payload, TEST_SECRET, algorithm="HS256")

    # Mock os.getenv for testing
    import os
    original_getenv = os.getenv

    def mock_getenv(key, default=None):
        if key == "BETTER_AUTH_SECRET":
            return TEST_SECRET
        return original_getenv(key, default)

    # Patch os.getenv
    os.getenv = mock_getenv

    result = verify_jwt_token(token)

    assert result.error_code == "OK"
    assert result.user_id == "test-user-123"


def test_verify_expired_token():
    """Test verification of an expired JWT token."""
    import jose
    import os

    # Create an expired token
    now = datetime.utcnow() - timedelta(hours=24)
    payload = {
        "sub": "test-user-123",
        "iss": JWT_ISSUER,
        "aud": JWT_ISSUER,
        "exp": int(now.timestamp()),
    }

    token = jose.encode(payload, TEST_SECRET, algorithm="HS256")

    import os
    original_getenv = os.getenv

    def mock_getenv(key, default=None):
        if key == "BETTER_AUTH_SECRET":
            return TEST_SECRET
        return original_getenv(key, default)

    os.getenv = mock_getenv

    result = verify_jwt_token(token)

    assert result.error_code == "TOKEN_EXPIRED"
    assert result.user_id == "test-user-123"


def test_verify_invalid_signature():
    """Test verification of a token with invalid signature."""
    import jose

    # Create a valid token
    now = datetime.utcnow()
    payload = {
        "sub": "test-user-123",
        "iss": JWT_ISSUER,
        "aud": JWT_ISSUER,
        "exp": int((now + timedelta(days=7)).timestamp()),
    }

    token = jose.encode(payload, TEST_SECRET, algorithm="HS256")

    # Tamper with different secret
    tampered_token = token.replace("...", "invalid")

    import os
    original_getenv = os.getenv

    def mock_getenv(key, default=None):
        if key == "BETTER_AUTH_SECRET":
            return TEST_SECRET
        return original_getenv(key, default)

    os.getenv = mock_getenv

    result = verify_jwt_token(tampered_token)

    assert result.error_code == "INVALID_SIGNATURE"
    assert result.user_id == ""


def test_verify_missing_user_id():
    """Test that tokens without user_id are rejected."""
    import jose

    # Create a token without sub claim
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_ISSUER,
        "exp": int((datetime.utcnow() + timedelta(days=7)).timestamp()),
    }

    token = jose.encode(payload, TEST_SECRET, algorithm="HS256")

    import os
    original_getenv = os.getenv

    def mock_getenv(key, default=None):
        if key == "BETTER_AUTH_SECRET":
            return TEST_SECRET
        return original_getenv(key, default)

    os.getenv = mock_getenv

    result = verify_jwt_token(token)

    assert result.error_code == "INVALID_PAYLOAD"
    assert result.user_id == ""


if __name__ == "__main__":
    pytest.main([__file__])
```

**Rationale**:
- Unit tests ensure JWT verification works correctly
- Tests cover valid, expired, and invalid signature scenarios
- Tests can be run independently for debugging

## Implementation Tasks

### Task 1: Update frontend/lib/auth.ts with JWT plugin

**File**: `frontend/lib/auth.ts`

**Description**: Add JWT plugin configuration to enable Better Auth to issue and verify JWT tokens.

**Acceptance Criteria**:
- JWT plugin is added to plugins array with HS256 algorithm
- Token expiration is set to 7 days
- Issuer and audience are configured correctly
- Environment variables are validated

**Implementation Notes**:
- The JWT plugin adds `/api/auth/token` endpoint for token retrieval
- `getSession` returns token in `set-auth-jwt` response header
- Frontend should use `getSession` instead of directly calling `/api/auth/token`

### Task 2: Create backend/app/jwt_middleware.py

**File**: `backend/app/jwt_middleware.py` (NEW FILE)

**Description**: Implement JWT verification using python-jose library.

**Acceptance Criteria**:
- JWT tokens are verified using HS256 algorithm
- Token expiration is checked
- Issuer and audience are validated
- User ID is extracted from `sub` claim
- Detailed error messages are returned for debugging

**Implementation Notes**:
- Uses `python-jose` library for JWT operations
- Returns `JWTVerificationResult` with error_code and error_message
- Compatible with FastAPI's Security dependency injection

### Task 3: Update backend/app/auth.py

**File**: `backend/app/auth.py`

**Description**: Replace old session token parsing with new JWT verification imports.

**Acceptance Criteria**:
- Old implementation is deprecated
- New JWT verification is imported from jwt_middleware
- Backward compatible imports are maintained

**Implementation Notes**:
- Keep `verify_session` and `get_current_user_id` exports
- These functions now delegate to JWT verification middleware

### Task 4: Update backend/requirements.txt

**File**: `backend/requirements.txt`

**Description**: Add python-jose[cryptography] and related dependencies.

**Acceptance Criteria**:
- python-jose[cryptography]>=3.3.0
- python-dotenv>=1.0.0
- psycopg2-binary>=2.9.0
- psycopg>=2.9.0

**Implementation Notes**:
- python-jose is the maintained library for JWT operations
- python-dotenv for loading environment variables

### Task 5: Update frontend/lib/api.ts

**File**: `frontend/lib/api.ts`

**Description**: Add comprehensive error handling to API client.

**Acceptance Criteria**:
- All API errors are caught and logged
- Error responses include status code, error code, and message
- Network errors are handled gracefully
- Errors don't cause application crashes

**Implementation Notes**:
- Try-catch blocks for each request
- Structured error objects for debugging
- Console logging with request context

### Task 6: Update backend/app/routes/tasks.py

**File**: `backend/app/routes/tasks.py`

**Description**: Add detailed logging to all task CRUD operations.

**Acceptance Criteria**:
- All operations log request details
- Unexpected errors include full traceback
- HTTPExceptions are re-raised with context
- Validation errors return detailed error responses

**Implementation Notes**:
- Use sys.stderr for logging
- Include timestamp in all error responses
- Log user_id for debugging access control

### Task 7: Create backend/tests/test_jwt_middleware.py

**File**: `backend/tests/test_jwt_middleware.py` (NEW FILE)

**Description**: Add unit tests for JWT verification.

**Acceptance Criteria**:
- Tests verify valid JWT tokens
- Tests reject expired tokens
- Tests reject tokens with invalid signatures
- Tests reject tokens without user_id

**Implementation Notes**:
- Tests use mocking for os.getenv
- Tests can be run with: `pytest backend/tests/test_jwt_middleware.py -v`
- pytest fixtures for test secret

## Order of Execution

Tasks should be executed in this order:

1. **Phase 0** (Parallel - Research Complete):
   - Task 1: Update frontend/lib/auth.ts
   - Task 2: Create backend/app/jwt_middleware.py

2. **Phase 1** (Sequential):
   - Task 3: Update backend/app/auth.py
   - Task 4: Update backend/requirements.txt

3. **Phase 2** (Sequential):
   - Task 5: Update frontend/lib/api.ts
   - Task 6: Update backend/app/routes/tasks.py

4. **Phase 3** (Testing):
   - Task 7: Create backend/tests/test_jwt_middleware.py

## Dependencies

### Python Dependencies
```
fastapi>=0.104.0
sqlmodel>=0.0.12
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
psycopg2-binary>=2.9.0
```

### Node.js Dependencies
```
better-auth>=1.0.0
better-auth@latest
next@16
typescript@5
python-jose-cryptography@^3.3.0 (optional, for frontend validation)
```

## Rollout Plan

If implementation needs to be rolled back:

1. Remove `backend/app/jwt_middleware.py`
2. Restore original `backend/app/auth.py` with JWT verification
3. Remove python-jose dependency from requirements.txt

## Risk Mitigation

### Risk 1: Breaking Changes During Migration
**Risk**: Users may be logged out when JWT verification is deployed
**Mitigation**:
- Keep old session-based auth as fallback temporarily
- Deploy backend changes during low-traffic period
- Monitor for 401 errors in production

### Risk 2: Environment Variable Mismatch
**Risk**: Frontend and backend have different BETTER_AUTH_SECRET values
**Mitigation**:
- Use same `.env.example` file for both services
- Add environment variable validation at startup
- Log warnings when environment variables differ

### Risk 3: Database Connection Pool Exhaustion
**Risk**: High concurrent load may exhaust Neon connection pool
**Mitigation**:
- Configure connection pool settings in SQLModel
- Implement connection retry logic
- Monitor database connection metrics

## Open Questions

None at this time. The specification is complete and implementation plan addresses all identified issues.

---

**Next Steps**:
1. Run `/sp.tasks` to generate actionable task list
2. Run `/sp.implement` to execute tasks
3. Test the authentication flow end-to-end
