---
name: better-auth-guide
description: Fetch Better Auth documentation and apply JWT authentication best practices. Use when implementing user authentication, JWT tokens, or securing API endpoints (Phase II+).
version: 2.0.0
---

# Better Auth + JWT Mastery Skill

## Theoretical Foundation

Better Auth is a framework-agnostic TypeScript authentication library that provides:
- **Session Management**: httpOnly cookie-based sessions with configurable expiration
- **JWT Plugin**: Token generation for cross-service authentication
- **Plugin Architecture**: Extensible with community plugins (2FA, SSO, OAuth)
- **Type Safety**: Full TypeScript inference for user sessions

### Authentication Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUTHENTICATION FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Frontend (Next.js)              Better Auth              Backend (FastAPI) │
│  ┌──────────────┐               ┌──────────────┐         ┌──────────────┐   │
│  │ User Login   │──────────────▶│ Auth Server  │         │ API Endpoint  │   │
│  │ Form         │ credentials   │              │         │              │   │
│  └──────────────┘               └──────┬───────┘         └──────┬───────┘   │
│                                         │                         │           │
│                                         │ Set Cookie              │ Verify JWT │
│                                         │ better-auth.session     │ Bearer     │
│                                         │ token                   │ header     │
│                                         ▼                         ▼           │
│  ┌──────────────┐               ┌──────────────┐         ┌──────────────┐   │
│  │ Session      │◀──────────────│ JWT Plugin   │────────▶│ Protected    │   │
│  │ Established  │   /api/auth   │              │   JWT   │ Resource     │   │
│  └──────────────┘               └──────────────┘         └──────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Session Cookie**: httpOnly cookie containing session identifier (frontend auth)
2. **JWT Token**: Signed token for backend API authentication (cross-service)
3. **Shared Secret**: Both services use same BETTER_AUTH_SECRET for JWT signing
4. **nextCookies Plugin**: Enables cookie setting in Next.js Server Actions
5. **Middleware**: Route protection via session validation

## When to Use This Skill

Activation triggers:
- Implementing user authentication (signup, login, logout)
- Securing API endpoints with JWT verification
- Setting up session management in Next.js
- Configuring middleware for protected routes
- Cross-stack authentication (Next.js + FastAPI)

## Context7 Research Results

**Library ID**: `/better-auth/better-auth`
**Source**: https://better-auth.com
**Reputation**: High
**Code Snippets**: 2135+

### Key Configuration Patterns

```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  database: pool,
  baseURL: process.env.BETTER_AUTH_URL,

  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },

  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,
    cookieCache: { enabled: true, maxAge: 60 * 5 },
  },

  plugins: [
    nextCookies(),
    jwt({
      algorithm: "HS256",
      expiresIn: "7d",
      issuer: process.env.BETTER_AUTH_URL,
      audience: [process.env.API_URL],
    }),
  ],
});
```

## Implementation Guidelines

### 1. Frontend: Next.js Server Action Authentication

```typescript
// app/actions/auth.ts
"use server";

import { auth } from "@/lib/auth";

export async function signIn(email: string, password: string) {
  const result = await auth.api.signInEmail({
    body: { email, password },
  });

  if (result.error) {
    return { error: "Invalid credentials" };
  }

  return { success: true };
}

export async function signOut() {
  await auth.api.signOut();
}
```

### 2. Frontend: JWT Token Retrieval

```typescript
// app/api/auth/token/route.ts
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function GET() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    return new Response("Unauthorized", { status: 401 });
  }

  // JWT plugin generates token from session
  const token = await auth.api.getJWT({
    body: {
      userId: session.user.id
    }
  });

  return Response.json({ token });
}
```

### 3. Backend: FastAPI JWT Verification

```python
# backend/auth/jwt.py
from jwt import PyJWTError, decode
from os import getenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET = getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = decode(
            credentials.credentials,
            SECRET,
            algorithms=[ALGORITHM],
            audience=getenv("API_URL"),
            issuer=getenv("BETTER_AUTH_URL"),
        )
        return payload
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

# Usage in endpoints
@app.get("/api/tasks")
async def get_tasks(user: dict = Depends(verify_token)):
    return {"tasks": [], "user_id": user["sub"]}
```

### 4. Middleware: Route Protection

```typescript
// middleware.ts (Next.js 15.2.0+)
import { NextRequest, NextResponse } from "next/server";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";

export async function middleware(request: NextRequest) {
  // Skip API routes
  if (request.nextUrl.pathname.startsWith("/api")) {
    return NextResponse.next();
  }

  // Check session
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  const publicRoutes = ["/", "/login", "/signup"];
  const isPublicRoute = publicRoutes.some(route =>
    request.nextUrl.pathname === route ||
    request.nextUrl.pathname.startsWith(route)
  );

  if (!isPublicRoute && !session) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (session && (request.nextUrl.pathname === "/login" ||
                  request.nextUrl.pathname === "/signup")) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  runtime: "nodejs",
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

## Security Best Practices

### ✅ ALWAYS DO

| Practice | Implementation |
|----------|----------------|
| Use environment variables for secrets | `BETTER_AUTH_SECRET` in `.env` |
| Set httpOnly on cookies | Automatic with better-auth |
| Validate token expiration | JWT `expiresIn` + backend verification |
| Implement CORS | Restrict to frontend origin only |
| Use strong passwords | `minPasswordLength: 8` |
| Share secret across services | Same `BETTER_AUTH_SECRET` on frontend + backend |

### ❌ NEVER DO

| Anti-Pattern | Risk |
|--------------|------|
| Log JWT tokens | Credential leakage |
| Store tokens in localStorage | XSS vulnerability |
| Use weak JWT secrets | Token forgery |
| Skip token validation | Unauthorized access |
| Expose secret in code | Secret compromise |

## Common Pitfalls

### 1. Missing nextCookies Plugin
**Symptom**: Cookies not set in Server Actions
**Fix**: Add `nextCookies()` plugin to auth configuration

### 2. Mismatched JWT Secrets
**Symptom**: 401 Unauthorized on backend
**Fix**: Ensure same `BETTER_AUTH_SECRET` on both services

### 3. Missing Audience/Issuer
**Symptom**: Token validation fails
**Fix**: Set matching `issuer` and `audience` in JWT config

### 4. Runtime Configuration
**Symptom**: Middleware fails with "headers not available"
**Fix**: Add `runtime: "nodejs"` to middleware config

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| JWT setup | "JWT plugin configuration HS256 expiration" |
| Next.js integration | "nextCookies plugin Server Actions middleware" |
| Session validation | "getSession API route headers authentication" |
| Email/password | "signInEmail emailAndPassword configuration" |
| Security best practices | "httpOnly cookies CSRF protection session" |

## Code Standards

1. **Environment Variables**:
   - `BETTER_AUTH_SECRET`: 32+ character random string
   - `BETTER_AUTH_URL`: Frontend base URL
   - `DATABASE_URL`: PostgreSQL connection string

2. **Type Safety**:
   - Use `typeof auth.$Infer.Session` for session types
   - Use `typeof auth.$Infer.User` for user types

3. **Error Handling**:
   - Always check `result.error` from auth APIs
   - Return user-friendly error messages
   - Never expose internal errors to clients

## References

- **Documentation**: https://better-auth.com
- **GitHub**: https://github.com/better-auth/better-auth
- **Context7 ID**: `/better-auth/better-auth`
