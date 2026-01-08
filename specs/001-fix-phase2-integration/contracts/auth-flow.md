# Authentication Flow Diagram

**Feature**: 001-fix-phase2-integration
**Date**: 2026-01-06

## Better Auth JWT + FastAPI Integration Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AUTHENTICATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │   Browser    │
  │              │
  └──────┬───────┘
         │
         │ 1. Visit App
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                         Next.js Frontend                             │
  │                        (localhost:3000)                               │
  ├─────────────────────────────────────────────────────────────────────┤
  │                                                                     │
  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐     │
  │  │  Login Page  │───▶│ Signup Form  │───▶│   Dashboard      │     │
  │  └──────────────┘    └──────────────┘    │   (Protected)     │     │
  │                                              │                  │     │
  │  ┌────────────────────────────────────────────────────────────┐   │
  │  │              Better Auth Server Configuration              │   │
  │  │   (lib/auth.ts)                                            │   │
  │  │                                                           │   │
  │  │  - JWT plugin enabled                                       │   │
  │  │  - PostgreSQL adapter (NeonDB)                             │   │
  │  │  - Email/password authentication                           │   │
  │  │  - Session management with httpOnly cookies                │   │
  │  └────────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────────┘
         │
         │ 2. Submit Signup/Login
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                      Better Auth API Handler                        │
  │                      (/api/auth/sign-in, /sign-up)                  │
  ├─────────────────────────────────────────────────────────────────────┤
  │                                                                     │
  │  Action:                                                             │
  │  1. Validate email/password                                        │
  │  2. Create user record in NeonDB (if signup)                       │
  │  3. Generate session + JWT token                                    │
  │  4. Set httpOnly cookie with session                                │
  │  5. Return session data (includes JWT in response)                  │
  └─────────────────────────────────────────────────────────────────────┘
         │
         │ 3. Session Response (includes JWT token)
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                        Client State                                  │
  │                                                                       │
  │  {                                                                    │
  │    user: { id, email, name },                                         │
  │    session: { token: "eyJ..." },  ← JWT TOKEN HERE                    │
  │    ...                                                                │
  │  }                                                                    │
  └─────────────────────────────────────────────────────────────────────┘
         │
         │ 4. Server Action: Get JWT Token
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                  Server Action (app/actions/tasks.ts)                │
  │                                                                       │
  │  async function createTask(title: string) {                         │
  │    // Get session (contains JWT)                                    │
  │    const session = await authClient.api.getSession()                │
  │    const jwtToken = session.data?.token                             │
  │                                                                       │
  │    // Call backend API with JWT                                      │
  │    const response = await fetch(`${API_URL}/api/${userId}/tasks`,  │
  │      {                                                               │
  │        headers: {                                                    │
  │          'Authorization': `Bearer ${jwtToken}`  ← JWT ATTACHED       │
  │        }                                                             │
  │      }                                                               │
  │    )                                                                 │
  │  }                                                                   │
  └─────────────────────────────────────────────────────────────────────┘
         │
         │ 5. API Request with JWT Header
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                       FastAPI Backend                                │
  │                      (localhost:8000)                                 │
  ├─────────────────────────────────────────────────────────────────────┤
  │                                                                     │
  │  ┌──────────────────────────────────────────────────────────────┐ │
  │  │                   JWT Middleware                               │ │
  │  │                   (jwt_middleware.py)                         │ │
  │  │                                                              │ │
  │  │  async def verify_jwt_token(credentials):                    │ │
  │  │      token = credentials.credentials                          │ │
  │  │      secret = os.getenv("BETTER_AUTH_SECRET")                │ │
  │  │      payload = jwt.decode(token, secret, algorithms=["HS256"])│ │
  │  │      return payload  # { userId, iat, exp }                   │ │
  │  │                                                              │ │
  │  └──────────────────────────────────────────────────────────────┘ │
  │                              │                                       │
  │                              ▼                                       │
  │  ┌──────────────────────────────────────────────────────────────┐ │
  │  │                      Route Handler                            │ │
  │  │                   (routes/tasks.py)                           │ │
  │  │                                                              │ │
  │  │  @app.get("/api/{user_id}/tasks")                            │ │
  │  │  async def get_tasks(                                        │ │
  │  │      user_id: str,                                           │ │
  │  │      token_payload: dict = Depends(verify_jwt_token)         │ │
  │  │  ):                                                           │ │
  │  │      # Verify user_id matches token                           │ │
  │  │      if token_payload["userId"] != user_id:                  │ │
  │  │          raise HTTPException(403)                             │ │
  │  │                                                              │ │
  │  │      # Query database with user filter                        │ │
  │  │      tasks = session.exec(select(Task).where(Task.user_id == user_id))│ │
  │  │      return tasks                                             │ │
  │  └──────────────────────────────────────────────────────────────┘ │
  │                              │                                       │
  │                              ▼                                       │
  │  ┌──────────────────────────────────────────────────────────────┐ │
  │  │                    NeonDB Database                            │ │
  │  │                  (Shared PostgreSQL)                         │ │
  │  │                                                              │ │
  │  │  Tables:                                                     │ │
  │  │  - user (managed by Better Auth)                            │ │
  │  │  - session (managed by Better Auth)                          │ │
  │  │  - task (managed by FastAPI/SQLModel)                        │ │
  │  └──────────────────────────────────────────────────────────────┘ │
  └─────────────────────────────────────────────────────────────────────┘
         │
         │ 6. Response with User's Data
         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                      UI Update                                       │
  │                                                                       │
  │  Tasks rendered in dashboard, user can CRUD operations              │
  └─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════

                         SHARED SECRET CONFIGURATION

  ┌────────────────────────────────┐    ┌────────────────────────────────┐
  │   frontend/.env.local          │    │   backend/.env                  │
  ├────────────────────────────────┤    ├────────────────────────────────┤
  │ DATABASE_URL=postgresql://...   │    │ DATABASE_URL=postgresql://...   │
  │ BETTER_AUTH_SECRET=abc123...     │◀──▶│ BETTER_AUTH_SECRET=abc123...     │
  │ BETTER_AUTH_URL=http://...       │    │ CORS_ORIGINS=http://localhost:3000│
  │ NEXT_PUBLIC_API_URL=http://...   │    │                                │
  └────────────────────────────────┘    └────────────────────────────────┘

        CRITICAL: Same BETTER_AUTH_SECRET in both files!
```

## Key Points

1. **JWT is included in Better Auth session response** - not a separate endpoint
2. **Both services share the same database** - NeonDB for users, sessions, tasks
3. **Both services share the same secret** - `BETTER_AUTH_SECRET` must match exactly
4. **JWT is passed in Authorization header** - Format: `Bearer <token>`
5. **Backend verifies JWT on every request** - Using PyJWT with shared secret
6. **User isolation is enforced** - `user_id` must match JWT userId
