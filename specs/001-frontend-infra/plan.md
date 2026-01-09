# Implementation Plan: Frontend Infrastructure Stabilization

**Branch**: `001-frontend-infra` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)

## Summary

Consolidate duplicate API clients (`lib/api.ts` and `lib/api-client.ts`) into a single unified client using the Result pattern from `lib/errors.ts`. Implement the missing `/api/auth/token` endpoint to retrieve JWT tokens from Better Auth sessions. Align health check paths to match backend contracts and remove unnecessary `userId` parameters from API methods.

**Primary Technical Approach**:
1. Merge `lib/api.ts` (TanStack Query-based) into `lib/api-client.ts` (Result-based) or vice versa
2. Create `/api/auth/token/route.ts` to expose JWT from Better Auth session
3. Update middleware cookie names to match Better Auth config
4. Fix health check endpoint path from `/health` to `/api/health`

## Technical Context

**Language/Version**: TypeScript 5+, Next.js 16+
**Primary Dependencies**: Better Auth (JWT plugin), TanStack Query, FastAPI (backend)
**Storage**: Neon Serverless PostgreSQL (backend only)
**Testing**: Existing `./backend/scripts/test_all.py` and `./scripts/verify-e2e.sh`
**Target Platform**: Web (browser + server-side Next.js)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: API responses < 3 seconds per SC-001
**Constraints**: Backend code cannot be modified; TypeScript strict mode required
**Scale/Scope**: Single application, ~50 frontend source files affected

### Current State Analysis

| File | Current Purpose | Issue |
|------|----------------|-------|
| `lib/api.ts` | TanStack Query client with types | Has auth methods, uses `/api/auth/token` (doesn't exist) |
| `lib/api-client.ts` | Result-based API client with retries | Has `userId` parameters (unnecessary), wrong health path |
| `lib/errors.ts` | Result type, ApiError classes | Well-designed, should be kept |
| `lib/auth.ts` | Better Auth configuration | Cookie name: `better-auth.session_token` |
| `middleware.ts` | Route protection | Checks `better-auth.session_token` or `session` |
| `app/api/auth/[...all]/route.ts` | Better Auth handler | No `/token` endpoint for JWT retrieval |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Section I: Spec-Driven Development

| Requirement | Status | Notes |
|-------------|--------|-------|
| No code without approved specs | ✅ PASS | Spec exists at `specs/001-frontend-infra/spec.md` |
| Follow pipeline: Spec → Plan → Tasks → Implement | ✅ PASS | This is Plan phase; Tasks to follow |
| Refinement at spec level only | ✅ PASS | All clarifications captured in spec |
| Reference Task IDs in code comments | ⚠️ TODO | Will be enforced in Tasks phase |
| Link code to spec sections | ⚠️ TODO | Will be enforced in Tasks phase |

### Section II: Agent Behavior Rules

| Requirement | Status | Notes |
|-------------|--------|-------|
| No manual coding by humans | ✅ PASS | AI-generated code only |
| No feature invention | ✅ PASS | Scope limited to spec requirements |
| No deviation from specifications | ✅ PASS | Implementation follows spec exactly |
| Use Context7 MCP for docs | ✅ PASS | Used for Better Auth JWT documentation |
| Create PHR after interactions | ✅ PASS | PHR will be created after this plan |

### Section III: Knowledge & Documentation Protocol

| Requirement | Status | Notes |
|-------------|--------|-------|
| Context7 MCP Mandate | ✅ PASS | Better Auth docs retrieved via Context7 |
| Reusable Intelligence Assets | ✅ PASS | Better Auth guide skill exists at `.claude/skills/` |

### Section IV: Phase Governance

| Requirement | Status | Notes |
|-------------|--------|-------|
| Phase II scope | ✅ PASS | Frontend infrastructure aligns with Phase II (web app) |
| No future-phase leak | ✅ PASS | No Phase III+ features (chatbot, K8s, cloud) |
| Architecture evolution via spec | ✅ PASS | Changes tracked in spec/plan |

### Section V: Technology Constraints

| Requirement | Status | Notes |
|-------------|--------|-------|
| Python 3.13+ | N/A | Frontend-only work |
| TypeScript strict mode | ✅ PASS | Required per FR-017 |
| Better Auth (Phase II) | ✅ PASS | Already configured |
| FastAPI backend | ✅ PASS | Backend contracts followed |

### Section VI: Quality Principles

| Requirement | Status | Notes |
|-------------|--------|-------|
| Clean Architecture | ✅ PASS | Single API client, clear separation |
| Stateless Services | ✅ PASS | No in-memory auth state |
| Type hints required | ✅ PASS | TypeScript strict mode |
| OWASP Top 10 awareness | ✅ PASS | JWT in httpOnly cookies, no exposure |

**CONSTITUTION CHECK RESULT**: ✅ **PASS** - All gates satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-frontend-infra/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (below)
├── data-model.md        # Phase 1 output (below)
├── quickstart.md        # Phase 1 output (below)
├── contracts/           # Phase 1 output (below)
│   └── api.yaml         # Backend API contract
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── lib/
│   ├── api.ts            # TO BE REMOVED (merged into api-client.ts)
│   ├── api-client.ts     # TO BE REFACTORED (unified client)
│   ├── errors.ts         # KEEP (Result type, ApiError)
│   ├── auth.ts           # KEEP (Better Auth config)
│   └── auth-client.ts    # KEEP (Better Auth client)
├── app/
│   ├── api/
│   │   └── auth/
│   │       ├── [...all]/route.ts    # KEEP (Better Auth handler)
│   │       └── token/
│   │           └── route.ts         # TO CREATE (JWT endpoint)
│   └── actions/
│       └── tasks.ts       # UPDATE (use unified API client)
└── middleware.ts         # UPDATE (cookie names aligned)

backend/
├── app/
│   └── routes/
│       └── auth.py       # READ-ONLY (do not modify)
```

**Structure Decision**: Monorepo with `frontend/` and `backend/` directories. This is a Phase II full-stack web application per constitution.

## Complexity Tracking

> **No violations requiring justification.** All changes are within Phase II scope and align with constitutional requirements.

---

# Phase 0: Research & Decisions

## Research Questions

### RQ-001: Better Auth JWT Token Retrieval

**Question**: How to get JWT token from Better Auth session for use in API requests?

**Decision**: Create `/api/auth/token/route.ts` endpoint that uses `auth.api.getSession()` to retrieve session and extracts JWT.

**Rationale**: Better Auth provides `auth.api.getSession({ headers })` method that returns session with JWT when JWT plugin is enabled. The JWT is accessible via the session or through a dedicated token endpoint.

**Alternatives Considered**:
1. **Use `authClient.token()` from client**: Requires client-side Better Auth client, not suitable for server components
2. **Extract from `set-auth-jwt` header**: Only available in `onSuccess` callback, not reusable
3. **Custom server endpoint** ✅ **CHOSEN**: Works in server components and actions, single source of truth

**References**: Better Auth JWT plugin docs (via Context7)

### RQ-002: API Client Consolidation Strategy

**Question**: Which API client pattern to keep - `lib/api.ts` (TanStack Query) or `lib/api-client.ts` (Result-based)?

**Decision**: Keep and enhance `lib/api-client.ts` with Result pattern; integrate TanStack Query as the consumer layer.

**Rationale**:
- `lib/api-client.ts` has superior error handling with Result type and ApiError classes
- Retry logic, timeout handling, and request ID tracking already implemented
- TanStack Query can use this client as the data fetching layer
- Aligns with FR-001 (single unified API client) and FR-003 (consistent error handling)

**Alternatives Considered**:
1. **Keep `lib/api.ts` only**: Lacks retry logic and structured error handling
2. **Merge into new file**: Unnecessary code churn
3. **Enhance `lib/api-client.ts`** ✅ **CHOSEN**: Best foundation, needs auth integration

### RQ-003: Better Auth Cookie Name Alignment

**Question**: What is the actual cookie name used by Better Auth?

**Decision**: Use `better-auth.session_token` as the cookie name (Better Auth default).

**Rationale**: According to `lib/auth.ts`, Better Auth is configured with default settings. The `nextCookies()` plugin uses `better-auth.session_token` as the default cookie name.

**Implementation**: Update `middleware.ts` to only check `better-auth.session_token`, remove fallback to `session`.

### RQ-004: Health Check Endpoint Path

**Question**: What is the correct health check path on the backend?

**Decision**: Use `/api/health` as the health check endpoint.

**Rationale**: The backend serves health check at `/api/health` per `backend/app/main.py`. The current `lib/api-client.ts` uses `/health` (incorrect), while `lib/api.ts` uses `/api/health` (correct).

---

# Phase 1: Design & Contracts

## Data Model

### Entity: Unified API Client

```typescript
// Location: frontend/lib/api-client.ts

class ApiClient {
  // Configuration
  private baseUrl: string
  private readonly timeout: number
  private readonly maxRetries: number

  // Core method
  private request<T>(endpoint: string, options: RequestOptions): Promise<Result<T>>

  // Auth methods (removed userId parameters)
  getTasks(): Promise<Result<TaskList>>
  getTask(taskId: number): Promise<Result<Task>>
  createTask(data: TaskCreate): Promise<Result<Task>>
  updateTask(taskId: number, data: TaskUpdate): Promise<Result<Task>>
  deleteTask(taskId: number): Promise<Result<void>>
  toggleTaskComplete(taskId: number): Promise<Result<Task>>
  searchTasks(query: string): Promise<Result<TaskList>>
  getTaskLogs(taskId: number): Promise<Result<TaskLog[]>>

  // Auth client methods (use Better Auth)
  signup(data: SignupData): Promise<Result<User>>
  signin(data: SigninData): Promise<Result<LoginResponse>>
  signout(): Promise<Result<void>>
  getCurrentUser(): Promise<Result<User>>

  // Health check (fixed path)
  healthCheck(): Promise<Result<HealthStatus>>
}
```

### Type Definitions

```typescript
// Result type (from lib/errors.ts - KEEP)
type Result<T> = { success: true; data: T } | { success: false; error: ApiError }

// API Error (from lib/errors.ts - KEEP)
class ApiError extends AppError {
  code: ErrorCode
  statusCode: number
  endpoint: string
  method: string
  requestId: string
}
```

## API Contracts

### Backend API (External - Read Only)

```yaml
# specs/001-frontend-infra/contracts/api.yaml

openapi: 3.0.0
info:
  title: Chronos Todo API
  version: 2.0.0

servers:
  - url: http://localhost:8000
    description: Development server

paths:
  /api/health:
    get:
      summary: Health check endpoint
      responses:
        '200':
          description: Server is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  timestamp:
                    type: string
                  version:
                    type: string

  /api/auth/signup:
    post:
      summary: Register new user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 8
                name:
                  type: string
              required: [email, password, name]
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '409':
          description: Email already registered

  /api/auth/signin:
    post:
      summary: Sign in user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
              required: [email, password]
      responses:
        '200':
          description: Sign in successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  token_type:
                    type: string
                  user:
                    $ref: '#/components/schemas/User'

  /api/auth/me:
    get:
      summary: Get current user
      security:
        - BearerAuth: []
      responses:
        '200':
          description: User data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

  /api/tasks:
    get:
      summary: List tasks
      security:
        - BearerAuth: []
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [all, pending, completed]
        - name: priority
          in: query
          schema:
            type: string
            enum: [HIGH, MEDIUM, LOW]
      responses:
        '200':
          description: Task list
          content:
            application/json:
              schema:
                type: object
                properties:
                  tasks:
                    type: array
                    items:
                      $ref: '#/components/schemas/Task'
                  total:
                    type: integer
    post:
      summary: Create task
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskCreate'
      responses:
        '201':
          description: Task created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'

  /api/tasks/{taskId}:
    get:
      summary: Get task by ID
      security:
        - BearerAuth: []
      parameters:
        - name: taskId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Task data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
    put:
      summary: Update task
      security:
        - BearerAuth: []
      parameters:
        - name: taskId
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskUpdate'
      responses:
        '200':
          description: Updated task
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
    delete:
      summary: Delete task
      security:
        - BearerAuth: []
      parameters:
        - name: taskId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Task deleted

  /api/tasks/{taskId}/complete:
    patch:
      summary: Toggle task completion
      security:
        - BearerAuth: []
      parameters:
        - name: taskId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Task toggled
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'

  /api/tasks/search:
    get:
      summary: Search tasks
      security:
        - BearerAuth: []
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  tasks:
                    type: array
                    items:
                      $ref: '#/components/schemas/Task'

  /api/tasks/{taskId}/logs:
    get:
      summary: Get task audit logs
      security:
        - BearerAuth: []
      parameters:
        - name: taskId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Audit logs
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TaskLog'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
          format: email
        name:
          type: string
          nullable: true
        created_at:
          type: string
          format: date-time
          nullable: true

    Task:
      type: object
      properties:
        id:
          type: integer
        user_id:
          type: string
        title:
          type: string
        description:
          type: string
          nullable: true
        priority:
          type: string
          enum: [HIGH, MEDIUM, LOW]
        completed:
          type: boolean
        tags:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              color:
                type: string
        due_date:
          type: string
          format: date-time
          nullable: true
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    TaskCreate:
      type: object
      required: [title]
      properties:
        title:
          type: string
        description:
          type: string
        priority:
          type: string
          enum: [HIGH, MEDIUM, LOW]
        tags:
          type: array
          items:
            type: object
        due_date:
          type: string
          format: date-time

    TaskUpdate:
      type: object
      properties:
        title:
          type: string
        description:
          type: string
        priority:
          type: string
          enum: [HIGH, MEDIUM, LOW]
        completed:
          type: boolean

    TaskLog:
      type: object
      properties:
        id:
          type: integer
        task_id:
          type: integer
        user_id:
          type: string
        action:
          type: string
        changed_fields:
          type: object
        created_at:
          type: string
          format: date-time
```

### Frontend API Contract (New Endpoint)

```yaml
# specs/001-frontend-infra/contracts/frontend-auth-api.yaml

openapi: 3.0.0
info:
  title: Frontend Auth API
  version: 1.0.0

paths:
  /api/auth/token:
    get:
      summary: Get JWT token from Better Auth session
      description: |
        Returns a JWT token for the currently authenticated user.
        The token is extracted from the Better Auth session cookie.
        Requires an active Better Auth session.
      responses:
        '200':
          description: JWT token returned
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                    description: JWT token for API authentication
        '401':
          description: No active session
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: No active session

  /api/auth/signout:
    post:
      summary: Sign out user
      description: |
        Terminates the Better Auth session on both client and server.
        This endpoint calls Better Auth's signOut method.
      responses:
        '200':
          description: Sign out successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
```

## Quickstart

### Development Setup

```bash
# 1. Ensure backend is running
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --port 8000

# 2. Ensure frontend dependencies are installed
cd frontend
npm install

# 3. Set environment variables
cp .env.example .env
# Edit .env with DATABASE_URL and BETTER_AUTH_SECRET

# 4. Run development server
npm run dev
```

### Testing

```bash
# Run backend tests
./backend/scripts/test_all.py

# Run E2E verification
./scripts/verify-e2e.sh

# Type checking
cd frontend && npx tsc --noEmit
```

### Key Files After Implementation

| File | Purpose | Change |
|------|---------|--------|
| `lib/api-client.ts` | Unified API client | REFACTORED |
| `lib/api.ts` | Legacy TanStack Query client | DELETED |
| `lib/errors.ts` | Error handling types | UNCHANGED |
| `app/api/auth/token/route.ts` | JWT token endpoint | CREATED |
| `middleware.ts` | Route protection | UPDATED (cookie names) |

---

# Implementation Phases

## Phase 1.1: Create JWT Token Endpoint

**File**: `frontend/app/api/auth/token/route.ts` (NEW)

```typescript
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { NextResponse } from "next/server"

/**
 * GET /api/auth/token
 *
 * Returns the JWT token from the current Better Auth session.
 * Used by the API client to authenticate requests to the backend.
 */
export async function GET() {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    })

    if (!session) {
      return NextResponse.json(
        { error: "No active session" },
        { status: 401 }
      )
    }

    // The JWT token is available in the session when JWT plugin is enabled
    // Better Auth automatically includes the token in the session response
    const token = (session as unknown as { token?: string }).token

    if (!token) {
      return NextResponse.json(
        { error: "No token in session" },
        { status: 401 }
      )
    }

    return NextResponse.json({ token })
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to retrieve token" },
      { status: 500 }
    )
  }
}
```

## Phase 1.2: Unified API Client

**File**: `frontend/lib/api-client.ts` (REFACTORED)

Key changes:
1. Add `getAuthToken()` method that calls `/api/auth/token`
2. Remove all `userId` parameters from method signatures
3. Update `healthCheck()` to use `/api/health`
4. Keep Result pattern and error handling
5. Keep retry logic and timeouts

## Phase 1.3: Update Middleware

**File**: `frontend/middleware.ts` (REFACTORED)

Key changes:
1. Remove fallback to `session` cookie name
2. Only check `better-auth.session_token`
3. Remove `console.log` statements (FR-015)

## Phase 1.4: Update Server Actions

**File**: `frontend/app/actions/tasks.ts` (REFACTORED)

Key changes:
1. Import from `lib/api-client.ts` only
2. Remove `lib/api.ts` imports
3. Handle Result types appropriately

## Phase 1.5: Cleanup

1. Delete `lib/api.ts`
2. Run TypeScript type checking: `npx tsc --noEmit`
3. Run E2E tests: `./scripts/verify-e2e.sh`

---

# Verification

### Type Checking

```bash
cd frontend
npx tsc --noEmit --strict
# Expected: 0 errors (SC-003)
```

### E2E Testing

```bash
./scripts/verify-e2e.sh
# Expected: All tests pass (SC-005)
```

### Code Quality Checks

| Check | Command | Success Criteria |
|-------|---------|------------------|
| No console.log in production | `grep -r "console.log" frontend/app --exclude-dir=node_modules` | 0 matches (SC-004) |
| No duplicate API clients | `grep -l "export.*api" frontend/lib/*.ts` | Only api-client.ts (SC-006) |
| Health check path | `grep -r "/health" frontend/lib --exclude-dir=node_modules` | All use /api/health (FR-011) |
| No userId in API client | `grep "userId" frontend/lib/api-client.ts` | Only in auth methods (FR-012) |

---

# Post-Design Constitution Re-Check

**Status**: ✅ **PASS** - No constitutional violations introduced by the design.

The design maintains:
- Clean Architecture (single API client)
- TypeScript strict mode compliance
- Better Auth integration patterns
- No backend modifications (FR-013 constraint)
- Phase II scope only
