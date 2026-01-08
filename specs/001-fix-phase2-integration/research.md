# Research Documentation: Phase II Integration Fixes

**Feature**: 001-fix-phase2-integration
**Date**: 2026-01-06
**Phase**: 0 - Research & Documentation

## Purpose

This document consolidates findings from official documentation (via Context7 MCP) to resolve all NEEDS CLARIFICATION items from the Technical Context and guide implementation.

---

## 1. Better Auth JWT Plugin Configuration

### Context7 Source
- **Library**: `better-auth/better-auth`
- **Topic**: JWT plugin, token generation, server configuration

### Key Findings

#### JWT Plugin Setup
The Better Auth JWT plugin must be configured in the server configuration:

```typescript
// frontend/lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins/jwt"

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // For development
  },
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
        // issuer: APP_URL,  // Optional: defaults to app URL
        // audience: [API_URL],  // Optional: for backend verification
      },
    }),
  ],
})
```

#### Token Endpoint
The JWT plugin automatically exposes the following endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/sign-in` | POST | Sign in (returns session + JWT) |
| `/api/auth/sign-up` | POST | Sign up (returns session + JWT) |
| `/api/auth/session` | GET | Get current session (includes JWT in response) |

**Important**: The JWT token is included in the session response, not a separate `/api/auth/token` endpoint. This was a key finding—previous assumptions were incorrect.

#### Retrieving JWT Token on Client

```typescript
// frontend/lib/auth-client.ts
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
})

// Server Action to get JWT token for API calls
export async function getAuthToken() {
  const session = await authClient.api.getSession({
    query: {},  // No body needed
  })

  return session.data?.token // JWT token included in session
}
```

#### Environment Variables Required

```bash
# frontend/.env.local
DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-key-here
BETTER_AUTH_URL=http://localhost:3000  # Frontend URL for JWKS
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Decision
**Use Better Auth's built-in JWT plugin** which includes tokens in session response. No separate token endpoint needed.

### Alternatives Considered
- **Manual JWT signing**: More control but requires custom implementation
- **Separate token endpoint**: Not necessary—Better Auth includes JWT in session

---

## 2. FastAPI JWT Verification

### Context7 Source
- **Library**: `fastapi/fastapi`
- **Topics**: Dependencies, Security, Authentication

### Key Findings

#### JWT Verification Pattern

FastAPI recommends using dependency injection for authentication:

```python
# backend/app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

security = HTTPBearer()

async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token and return payload."""
    token = credentials.credentials
    secret = os.getenv("BETTER_AUTH_SECRET")

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Better Auth doesn't set aud by default
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Usage in routes
@app.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    # token_payload contains userId and other claims
    if token_payload.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    # ... proceed
```

#### Better Auth JWT Structure

Better Auth JWT tokens contain:

| Claim | Description |
|-------|-------------|
| `userId` | User's unique ID (string) |
| `iat` | Issued at timestamp |
| `exp` | Expiration timestamp |

### Decision
**Use PyJWT with HTTPBearer dependency injection** for clean, reusable authentication.

### Alternatives Considered
- **JWKS fetching**: More complex, requires frontend to be running
- **Passlib integration**: Overkill for simple JWT verification

---

## 3. SQLModel + NeonDB SSL Configuration

### Context7 Source
- **Library**: `sqlmodel_tiangolo`
- **Topics**: Database connection, Session management, PostgreSQL

### Key Findings

#### NeonDB Connection String

Neon Serverless PostgreSQL requires SSL. The connection string MUST include SSL mode:

```bash
# Correct format
DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=require

# For production (certificate verification)
DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=verify-ca
```

#### SQLModel Connection Setup

```python
# backend/app/db.py
from sqlmodel import SQLModel, create_engine, Session
from os import getenv
from typing import AsyncGenerator

DATABASE_URL = getenv("DATABASE_URL")

# Neon-specific engine settings
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL debugging
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,  # Recycle connections after 5 min (serverless friendly)
    connect_args={
        "sslmode": "require",  # Explicit SSL requirement
    }
)

def get_session() -> AsyncGenerator[Session, None]:
    """Get database session with proper cleanup."""
    with Session(engine) as session:
        yield session
```

#### Serverless Best Practices

NeonDB is serverless, which means connections can be dropped. Key settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| `pool_pre_ping` | `True` | Test connections before use |
| `pool_recycle` | `300` | Recycle before serverless auto-sleep |
| `connect_args.sslmode` | `"require"` | Force SSL encryption |

### Decision
**Use explicit `sslmode=require` with connection pooling settings** optimized for Neon's serverless architecture.

### Alternatives Considered
- **Direct psycopg2**: More control but loses SQLModel benefits
- **Connection string without SSL**: Will fail with Neon

---

## 4. FastAPI CORS Configuration

### Context7 Source
- **Library**: `fastapi/fastapi`
- **Topic**: CORS Middleware

### Key Findings

#### CORSMiddleware Setup

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware
import os

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Specific origins (better than "*")
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],  # All HTTP methods
    allow_headers=["*"],  # All headers (including Authorization)
)
```

#### Key Points

1. **`allow_credentials=True`** is required for cookie-based auth
2. **Specific origins** instead of `"*"` when using credentials
3. **Frontend URL** must match exactly (port matters!)

### Decision
**Configure CORS with specific origins, credentials enabled** for proper cookie and JWT header handling.

### Alternatives Considered
- **Wildcard origins (`*`)**: Won't work with credentials
- **Proxy setup**: Unnecessary complexity for local development

---

## 5. Component Architecture Fixes

### Current Issues Identified

From codebase exploration, the following components may have errors:

| Component | Issue | Fix Required |
|-----------|-------|--------------|
| `frontend/components/tasks/task-list.tsx` | May have prop type mismatches | Align with Task type |
| `frontend/components/tasks/task-form.tsx` | Form validation may be incomplete | Add proper validation |
| `frontend/lib/api.ts` | JWT header attachment may be broken | Fix Authorization header |

### Task Type Alignment

```typescript
// frontend/types/task.ts
export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string  // ISO 8601 datetime
  updated_at: string  // ISO 8601 datetime
}

// Backend response matches this structure via Pydantic model
```

---

## 6. Shared Secret Configuration

### Critical Requirement

Both frontend and backend MUST use the **same** `BETTER_AUTH_SECRET`:

```bash
# backend/.env
BETTER_AUTH_SECRET=your-exactly-32-character-secret

# frontend/.env.local
BETTER_AUTH_SECRET=your-exactly-32-character-secret  # MUST MATCH
```

### Secret Generation

```bash
# Generate secure 32-character secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 7. Database Schema Alignment

### Better Auth Users Table

Better Auth creates its own `user` table:

```sql
-- Better Auth creates this automatically
CREATE TABLE user (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table (Backend)

```sql
-- Must reference Better Auth's user.id
CREATE TABLE task (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_completed ON task(completed);
```

### Important Note

The `user_id` in the Task table is **TEXT type** to match Better Auth's string-based user IDs, not integer.

---

## Summary of Decisions

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| Use Better Auth JWT plugin | Built-in, less custom code | Manual JWT implementation |
| JWT from session response | Better Auth includes token in session | Separate token endpoint |
| PyJWT for verification | Simple, no JWKS dependency | JWKS fetching (complex) |
| SSL mode required | Neon requirement | No SSL (will fail) |
| Specific CORS origins | Required for credentials | Wildcard (won't work) |
| TEXT user_id type | Matches Better Auth schema | Integer (mismatch) |

---

## NEEDS CLARIFICATION Status: ✅ ALL RESOLVED

All items from Technical Context have been resolved through official documentation research.

| Original Uncertainty | Resolution Source |
|---------------------|-------------------|
| Better Auth JWT endpoint | Better Auth docs (JWT in session) |
| JWT verification approach | FastAPI docs (HTTPBearer) |
| Neon SSL configuration | SQLModel docs (sslmode=require) |
| CORS setup | FastAPI docs (CORSMiddleware) |
