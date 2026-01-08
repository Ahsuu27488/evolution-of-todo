# Phase II Research: Technical Decisions

**Feature**: 006-phase2-fullstack-webapp
**Date**: 2025-12-29
**Status**: Complete

---

## 1. Neon PostgreSQL Connection

### Decision
Use Neon Serverless PostgreSQL with SQLModel via environment variable `DATABASE_URL`.

### Connection String Format
```
postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}?sslmode=require
```

### How to Get Your Connection String

1. **Log in to Neon Console**: https://console.neon.tech
2. **Select your project** (or create one if needed)
3. **Go to Dashboard** → **Connection Details**
4. **Copy the connection string** - It looks like:
   ```
   postgresql://ahsan:************@ep-xxxxx-xxxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
5. **Store in `.env` file** (backend):
   ```env
   DATABASE_URL=postgresql://ahsan:YOUR_PASSWORD@ep-xxxxx-xxxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### SQLModel Connection Setup
```python
# backend/app/db.py
import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling for serverless
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging in development
    pool_pre_ping=True,  # Handle dropped connections
)

def create_db_and_tables():
    """Create all SQLModel tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

### Rationale
- Neon is specified in hackathon requirements
- Serverless architecture = no infrastructure management
- Free tier sufficient for hackathon scale
- PostgreSQL compatibility with SQLModel/SQLAlchemy

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Supabase | Not in hackathon requirements |
| Local PostgreSQL | Requires Docker setup, not serverless |
| SQLite | Not production-ready, single-file |

---

## 2. Better Auth + FastAPI JWT Integration

### Decision
Use Better Auth in Next.js with JWT plugin, verify tokens in FastAPI using PyJWT with shared secret.

### Architecture Flow
```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js   │     │   Better Auth   │     │    FastAPI      │
│  Frontend   │────▶│   (JWT Issue)   │     │   (JWT Verify)  │
└─────────────┘     └────────┬────────┘     └────────┬────────┘
                             │                       │
                             ▼                       ▼
                    ┌─────────────────────────────────────────┐
                    │     BETTER_AUTH_SECRET (shared)         │
                    │     Both services use same secret       │
                    └─────────────────────────────────────────┘
```

### Frontend: Better Auth Setup
```typescript
// frontend/lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { Pool } from "@neondatabase/serverless"

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL
  }),
  emailAndPassword: {
    enabled: true,
  },
  plugins: [jwt()],  // Enable JWT token issuance
})
```

### Backend: JWT Verification
```python
# backend/app/auth.py
import os
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET not set")

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token and return payload."""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(payload: dict = Security(verify_jwt)) -> str:
    """Extract user ID from verified JWT payload."""
    user_id = payload.get("sub") or payload.get("userId")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id
```

### Environment Variables
```env
# Both frontend and backend must share this secret
BETTER_AUTH_SECRET=your-super-secret-key-at-least-32-chars

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://...@neon.tech/...

# Backend (.env)
DATABASE_URL=postgresql://...@neon.tech/...
CORS_ORIGINS=http://localhost:3000
```

### Rationale
- Better Auth is specified in hackathon requirements
- JWT allows stateless authentication between services
- Shared secret enables cross-stack verification without network calls

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Session-based auth | Requires shared session store |
| NextAuth.js | Not specified in requirements |
| Firebase Auth | External dependency not in stack |

---

## 3. Frontend State Management

### Decision
Use React Server Components + React Context for minimal client-side state. No Redux needed.

### Architecture
```
Server Components (default)
├── Data fetching
├── Initial render
└── SEO optimization

Client Components ('use client')
├── Interactive forms
├── Optimistic updates
└── Real-time UI state
```

### Pattern: Server Action for Mutations
```typescript
// app/actions/tasks.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createTask(formData: FormData) {
  const token = cookies().get('auth-token')?.value

  const response = await fetch(`${API_URL}/api/${userId}/tasks`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: formData.get('title'),
      description: formData.get('description'),
    }),
  })

  if (!response.ok) throw new Error('Failed to create task')

  revalidatePath('/dashboard')
  return response.json()
}
```

### Rationale
- Next.js App Router optimizes for Server Components
- Redux adds complexity without benefit for this scale
- Server Actions handle mutations naturally
- Less JavaScript = faster load times

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Redux Toolkit | Overkill for todo app scope |
| Zustand | Unnecessary with Server Components |
| TanStack Query | Server Actions handle data fetching |

---

## 4. API Design: User ID in URL vs Token

### Decision
Use URL pattern `/api/{user_id}/tasks` with JWT validation that user_id matches token.

### Security Implementation
```python
# backend/app/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user_id

router = APIRouter()

@router.get("/api/{user_id}/tasks")
def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    # Security check: URL user_id must match token user
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return {"tasks": tasks, "total": len(tasks)}
```

### Rationale
- Matches hackathon API specification exactly
- URL user_id enables caching strategies
- Double validation (URL + token) prevents tampering
- Clear audit trail in logs

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Token-only (no URL user_id) | Doesn't match hackathon spec |
| Query parameter | Less RESTful, harder to cache |

---

## 5. UI Component Strategy

### Decision
Use shadcn/ui with React Hook Form + Zod for forms, Sonner for toasts.

### Component Installation
```bash
# Core components for Phase II
npx shadcn@latest add button card checkbox dialog \
  alert-dialog form input label textarea \
  dropdown-menu sonner skeleton
```

### Form Validation Schema
```typescript
// lib/validations/task.ts
import { z } from 'zod'

export const taskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less"),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional(),
})

export type TaskInput = z.infer<typeof taskSchema>
```

### Rationale
- shadcn/ui is accessible and customizable
- React Hook Form is performant for forms
- Zod provides runtime validation matching backend
- Sonner integrates seamlessly with shadcn

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Material UI | Heavier bundle, different aesthetic |
| Chakra UI | Not as customizable |
| Custom components | Time-intensive, accessibility concerns |

---

## 6. Project Structure

### Decision
Monorepo with frontend/ and backend/ directories at root.

### Final Structure
```
evolution-of-todo/
├── frontend/                    # Next.js 16+ App Router
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── dashboard/
│   │   │   ├── page.tsx        # Task list (Server Component)
│   │   │   └── loading.tsx     # Skeleton loader
│   │   ├── actions/            # Server Actions
│   │   │   └── tasks.ts
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Landing → redirect
│   │   └── providers.tsx       # Client providers
│   ├── components/
│   │   ├── ui/                 # shadcn components
│   │   ├── task-card.tsx
│   │   ├── task-form.tsx
│   │   ├── task-list.tsx
│   │   └── empty-state.tsx
│   ├── lib/
│   │   ├── auth.ts             # Better Auth config
│   │   ├── api.ts              # API client
│   │   └── utils.ts            # cn() helper
│   ├── .env.local
│   └── package.json
│
├── backend/                     # FastAPI + SQLModel
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app
│   │   ├── models.py           # SQLModel models
│   │   ├── db.py               # Database connection
│   │   ├── auth.py             # JWT verification
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py        # Task CRUD endpoints
│   ├── tests/
│   │   └── test_tasks.py
│   ├── .env
│   ├── requirements.txt
│   └── pyproject.toml
│
├── specs/                       # Spec-Kit specs
├── .specify/                    # Spec-Kit config
├── .claude/                     # Skills and agents
├── CLAUDE.md
└── README.md
```

### Rationale
- Matches hackathon monorepo recommendation
- Clear separation of concerns
- Each directory has own CLAUDE.md for context
- Specs folder for Spec-Driven Development

---

## 7. Deployment Strategy

### Decision
Vercel for frontend, Railway for backend (both free tier).

### Frontend (Vercel)
- Automatic Next.js deployment
- Edge functions for auth routes
- Environment variables in Vercel dashboard

### Backend (Railway)
- Free tier: $5 credit/month (sufficient for hackathon)
- Automatic Python detection
- Connect via GitHub for auto-deploy

### Environment Setup
```
# Vercel Environment Variables
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Railway Environment Variables
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Rationale
- Both have generous free tiers
- Simple GitHub-based deployment
- Production-ready with SSL

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| AWS/GCP | More complex, requires credit card |
| Render | Slower cold starts on free tier |
| Fly.io | Requires credit card |

---

## Summary: Key Technical Decisions

| Area | Decision | Confidence |
|------|----------|------------|
| Database | Neon PostgreSQL via `DATABASE_URL` | High |
| Auth | Better Auth + JWT shared secret | High |
| State | Server Components + Context | High |
| API | `/api/{user_id}/tasks` with JWT check | High |
| UI | shadcn/ui + React Hook Form + Zod | High |
| Structure | Monorepo (frontend/ + backend/) | High |
| Deployment | Vercel + Railway | High |

All technical decisions align with hackathon requirements and constitution.
