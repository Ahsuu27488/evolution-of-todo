# Implementation Plan: Fix Phase II Integration Issues

**Branch**: `001-fix-phase2-integration` | **Date**: 2026-01-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-fix-phase2-integration/spec.md`

## Summary

**Primary Requirement**: Fix Phase II full-stack integration issues preventing the Todo web application from functioning. The UI is complete but authentication, database connectivity, and API communication between Next.js frontend and FastAPI backend are failing.

**Technical Approach**:
1. Fix Better Auth JWT plugin configuration for token generation
2. Verify NeonDB SSL connection with proper pool settings
3. Ensure CORS allows frontend (port 3000) to backend (port 8000) communication
4. Fix missing or broken UI components
5. Validate end-to-end authentication flow

## Technical Context

**Language/Version**: Python 3.13+, TypeScript 5+, Next.js 16+
**Primary Dependencies**: FastAPI, SQLModel, Better Auth, PyJWT, Neon PostgreSQL
**Storage**: Neon Serverless PostgreSQL (shared between frontend and backend)
**Testing**: pytest (backend), existing component tests (frontend)
**Target Platform**: Local development (Linux/Mac/WSL2)
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**: <200ms API response p95, support 10 concurrent users
**Constraints**: Local development first, single developer testing, no cloud deployment yet
**Scale/Scope**: Single-tenant todo application, ~5 tasks per user initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Isolation Verification

| Requirement | Status | Notes |
|-------------|--------|-------|
| Phase II features only | ✅ PASS | No Phase III+ features (chatbot, K8s, Kafka) included |
| Phase I preserved | ✅ PASS | Console app in `/src` remains untouched |
| Spec-driven implementation | ✅ PASS | All changes trace to spec.md requirements |

### Architecture Standards

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture | ✅ PASS | Backend has models/services/routes separation |
| Stateless Services | ✅ PASS | JWT tokens, no in-memory session state |
| Smallest Viable Diff | ✅ PASS | Only fix broken integration, no refactor |

### Code Standards

| Standard | Status | Notes |
|----------|--------|-------|
| Explicit error handling | ✅ PASS | Custom exceptions and error middleware exist |
| No hardcoded secrets | ✅ PASS | `.env` files properly configured |
| Type hints required | ✅ PASS | Python type hints and TypeScript strict mode |
| JWT validation required | ✅ PASS | PyJWT with httpOnly cookies per clarification |
| Error messages | ✅ PASS | Network timeout retry button per clarification |

### Security Standards

| Standard | Status | Notes |
|----------|--------|-------|
| User data isolation | ✅ PASS | 403 Forbidden on unauthorized access (per clarification) |
| JWT validation on protected endpoints | ✅ PASS | PyJWT with shared secret, httpOnly cookies |
| JWT expiry handling | ✅ PASS | Redirect to login with "Session expired" message |
| Secrets in environment variables | ✅ PASS | BETTER_AUTH_SECRET configured |
| XSS protection | ✅ PASS | httpOnly cookies for JWT storage |
| Input validation | ✅ PASS | Both frontend and backend validate (per clarification) |

**GATE RESULT**: ✅ **PASS** - All security standards addressed through clarifications.

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-phase2-integration/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0: Official docs findings
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Development setup
└── contracts/           # Phase 1: API contracts
    ├── backend-api.yaml # OpenAPI spec
    └── auth-flow.md     # JWT authentication flow
```

### Source Code (repository root)

```text
# Existing structure (being fixed, not changed)
frontend/                    # Next.js 16+ App Router
├── app/
│   ├── (auth)/             # Auth routes (login/signup)
│   ├── dashboard/          # Protected task dashboard
│   ├── actions/            # Server Actions
│   └── api/auth/           # Better Auth API routes
├── components/
│   ├── auth/               # Login/signup forms
│   ├── tasks/              # Task UI components
│   └── layout/             # Header, navigation
└── lib/
    ├── auth.ts             # Better Auth server config
    ├── auth-client.ts      # Client auth helpers
    └── api.ts              # Backend API client

backend/                     # FastAPI server
├── app/
│   ├── main.py             # FastAPI app initialization
│   ├── models.py           # SQLModel database models
│   ├── db.py               # Database connection
│   ├── jwt_middleware.py   # JWT verification
│   └── routes/
│       └── tasks.py        # Task CRUD endpoints
└── tests/
    └── test_jwt_middleware.py

src/                         # Phase I console app (unchanged)
```

**Structure Decision**: Monorepo with existing frontend/backend directories. Phase I console app preserved in `/src`. No new directories created—only fixing existing code.

## Complexity Tracking

> No constitution violations requiring justification. This is a bug-fix feature to complete Phase II.

## Phase 0: Research & Documentation

### Research Tasks

| Task | Context7 Source | Output |
|------|-----------------|--------|
| Better Auth JWT plugin | /better-auth/better-auth | JWT token generation configuration |
| FastAPI JWT verification | /fastapi/fastapi | Depends() pattern for auth |
| SQLModel Neon SSL | /websites/sqlmodel_tiangolo | Connection string SSL params |
| FastAPI CORS | /fastapi/fastapi | CORSMiddleware configuration |

### Official Documentation Sources

Using Context7 MCP as per constitution §3.1:

1. **Better Auth JWT Plugin** → `mcp__context7__resolve-library-id` + `query-docs`
2. **FastAPI Dependencies** → `mcp__context7__resolve-library-id` + `query-docs`
3. **SQLModel + Neon** → `mcp__context7__resolve-library-id` + `query-docs`

---

★ Insight ─────────────────────────────────────
**Research Phase Strategy**: Instead of assuming from training data, we fetch official docs for:
1. Better Auth's JWT plugin endpoint paths (/api/auth/token vs alternatives)
2. FastAPI's latest CORS middleware configuration (patterns change)
3. SQLModel's SSL connection parameters for Neon (critical for serverless)

This ensures we use current, correct patterns rather than outdated assumptions.
─────────────────────────────────────────────────

## Phase 1: Design

### Data Model (data-model.md)

Based on spec entities and SQLModel patterns:

```python
# Task Model (backend/app/models.py)
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)  # From Better Auth
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationship**: Task → User (many-to-one) via `user_id` foreign key

### API Contracts (contracts/)

#### Backend REST API (OpenAPI format)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/{user_id}/tasks` | JWT | List user's tasks |
| POST | `/api/{user_id}/tasks` | JWT | Create new task |
| GET | `/api/{user_id}/tasks/{id}` | JWT | Get single task |
| PUT | `/api/{user_id}/tasks/{id}` | JWT | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | JWT | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | JWT | Toggle completion |

#### Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Next.js   │     │ Better Auth │     │   FastAPI       │
│  Frontend   │────▶│   Server    │────▶│   Backend       │
│             │     │  (issues    │     │  (verifies      │
│             │     │   JWT)      │     │   JWT)          │
└─────────────┘     └─────────────┘     └─────────────────┘
```

**Flow**:
1. User logs in via Better Auth → Session created + JWT token generated
2. Server Action fetches session via `authClient.api.getSession()` - JWT included in response
3. JWT included in `Authorization: Bearer <token>` header
4. JWT stored in httpOnly cookies (XSS protection)
5. FastAPI middleware verifies signature using `BETTER_AUTH_SECRET`
6. User ID extracted from token payload (`userId` claim)
7. Request proceeds if user_id matches resource owner

### Quickstart (quickstart.md)

```bash
# 1. Install dependencies
cd backend && source .venv/bin/activate && pip install -r requirements.txt
cd frontend && npm install

# 2. Configure environment
# backend/.env and frontend/.env.local must have matching:
DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=32-character-secret-key-here-change-me
NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Start services
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev  # Runs on port 3000

# 4. Test
# Open http://localhost:3000
# Signup → Create task → Verify persistence
```

### Configuration Matrix

| Variable | Frontend | Backend | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | ✅ | ✅ | Neon PostgreSQL (same DB) |
| `BETTER_AUTH_SECRET` | ✅ | ✅ | JWT signing (MUST match) |
| `BETTER_AUTH_URL` | ✅ | ❌ | Frontend URL for JWKS |
| `NEXT_PUBLIC_API_URL` | ✅ | ❌ | Backend API base URL |
| `CORS_ORIGINS` | ❌ | ✅ | Allowed frontend origins |

## Phase 2: Implementation Tasks

### P1 Tasks (Critical Path)

| Task ID | Description | File(s) | Clarification |
|---------|-------------|---------|--------------|
| T-001 | Verify Better Auth JWT plugin enabled and session includes JWT | `frontend/lib/auth.ts` | JWT in session, not `/api/auth/token` |
| T-002 | Implement JWT verification with PyJWT (not JWKS) | `backend/app/jwt_middleware.py` | Use shared secret, no JWKS |
| T-003 | Verify NeonDB SSL connection with `sslmode=require` | `backend/app/db.py` | SSL required for serverless |
| T-004 | Validate CORS configuration with credentials enabled | `backend/app/main.py` | Specific origins, not wildcard |
| T-005 | Test end-to-end signup → task creation flow | Integration test | Full auth flow |

### P2 Tasks (Important)

| Task ID | Description | File(s) | Clarification |
|---------|-------------|---------|--------------|
| T-006 | Implement httpOnly cookie storage for JWT | `frontend/lib/auth.ts` | XSS protection |
| T-007 | Handle JWT expiry with redirect to login | `frontend/lib/auth-client.ts` | "Session expired" message |
| T-008 | Return 403 Forbidden on unauthorized access | `backend/app/routes/tasks.py` | Not 404 |
| T-009 | Add frontend+backend validation for empty titles | `frontend/components/`, `backend/app/routes/tasks.py` | Consistent messages |
| T-010 | Implement network timeout retry button | `frontend/lib/api.ts` | One-click retry |

### File-Specific Fixes

Based on exploration analysis + recent clarifications:

1. **`frontend/lib/auth.ts`**: Enable JWT plugin, ensure tokens stored in httpOnly cookies
2. **`frontend/lib/auth-client.ts`**: Use `getSession()` to retrieve JWT (not `/api/auth/token`)
3. **`backend/app/jwt_middleware.py`**: Use PyJWT with shared secret (not JWKS)
4. **`backend/app/db.py`**: Add `sslmode=require` with serverless-optimized pool settings
5. **`backend/app/main.py`**: Configure CORS with `allow_credentials=True`
6. **`frontend/components/tasks/*.tsx`**: Fix any import/prop errors
7. **`frontend/lib/api.ts`**: Add network timeout handling with retry button

### Session 2026-01-06 Clarifications Integrated

| Clarification | Implementation Impact |
|---------------|----------------------|
| JWT stored in httpOnly cookies | Frontend: Set httpOnly on session cookies |
| JWT expiry → redirect to login | Frontend: Handle 401, redirect with message |
| Unauthorized access → 403 Forbidden | Backend: Return 403, not 404 |
| Empty title → both sides validate | Frontend + Backend: Consistent error messages |
| Network timeout → retry button | Frontend: Add retry button to error toast |

## Success Verification

### Pre-Implementation Baseline

```bash
# Backend startup check
cd backend && python -c "from app.main import app; print('✅ Backend imports OK')"

# Frontend build check
cd frontend && npm run build  # Should complete without errors

# Database connection check
cd backend && python neondb_test.py  # Should connect with SSL
```

### Post-Implementation Validation

| Scenario | Command | Expected |
|----------|---------|----------|
| Backend starts | `uvicorn app.main:app` | No import/SSL errors |
| Frontend builds | `npm run build` | Zero TypeScript errors |
| Signup flow | UI test | Account created, redirected |
| Task creation | UI test | Task persists, visible |
| JWT verification | API test with invalid token | 401 Unauthorized |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Better Auth JWT plugin API changed | Medium | Use Context7 for current docs |
| Neon SSL certificate issues | High | Test with `sslmode=require` first |
| JWKS endpoint not accessible | Medium | Fallback to shared secret verification |
| Component cascade failures | Low | Fix imports/components incrementally |

## Dependencies

### External Documentation
- Better Auth: https://www.better-auth.com/docs
- FastAPI: Official docs via Context7
- SQLModel: Official docs via Context7
- Neon DB: https://neon.tech/docs

### Internal Artifacts
- Phase I console app: `/src/` (reference for domain models)
- Constitution: `.specify/memory/constitution.md`
- Hackathon docs: `Hackathon-docs/Hackathon2_doc.md`
