# Evolution of Todo — Project Architecture

**Claude Code Context** for the Evolution of Todo Hackathon II project.

## Project Overview

This is a **5-phase evolution** demonstrating Spec-Driven Development:
- **Phase I** (Complete): In-memory Python console app
- **Phase II** (Complete): Full-stack web app (Next.js + FastAPI + Neon DB)
- **Phase III** (Pending): AI chatbot with OpenAI Agents SDK + MCP
- **Phase IV** (Pending): Local K8s deployment with Minikube/Helm
- **Phase V** (Pending): Cloud deployment with Kafka/Dapr

## Directory-Level Context

| Directory | Purpose | Context File |
|-----------|---------|--------------|
| `src/` | Phase I console app | [`src/CLAUDE.md`](src/CLAUDE.md) |
| `backend/` | Phase II FastAPI backend | [`backend/CLAUDE.md`](backend/CLAUDE.md) |
| `frontend/` | Phase II Next.js frontend | [`frontend/CLAUDE.md`](frontend/CLAUDE.md) |

## Cross-Phase Architectural Rules

### 1. Authentication Flow

The project uses a **shared JWT secret** architecture:

```
┌─────────────┐     Sign In/Up      ┌──────────────┐
│   Frontend  │─────────────────────▶│  Better Auth│
│  (Next.js)  │                     │  (Frontend)  │
└─────────────┘                     └──────────────┘
      │                                     │
      │  Generates JWT with BETTER_AUTH_SECRET
      │                                     │
      ▼                                     │
┌─────────────┐                             │
│ API Client  │◀────────────────────────────┘
│             │  Fetches JWT from /api/auth/token
└─────────────┘
      │
      │  Sends: Authorization: Bearer <JWT>
      ▼
┌──────────────┐
│  FastAPI     │  Verifies JWT with same BETTER_AUTH_SECRET
│  Backend     │  Extracts user_id from 'sub' claim
└──────────────┘
```

### 2. Shared Secret Requirement

`BETTER_AUTH_SECRET` MUST be identical in:
1. `frontend/.env.local` — Better Auth signing
2. `backend/.env` — FastAPI verification

Length: ≥32 characters
Algorithm: HS256 (symmetric)

### 3. Task Data Model Evolution

The Task model is consistent across phases:

```python
# Phase I (src/todo/domain/task.py)
@dataclass
class Task:
    id: int
    title: str
    description: str
    priority: Priority  # HIGH, MEDIUM, LOW
    tags: set[str]
    completed: bool
    created_at: datetime
    due_date: date | None
    recurrence: Recurrence  # NONE, DAILY, WEEKLY, MONTHLY
```

```python
# Phase II (backend/app/models.py)
class Task(SQLModel, table=True):
    id: int
    user_id: str  # Added for multi-user
    title: str
    description: str | None
    priority: Priority
    tags: list[Tag]  # Now JSONB with colors
    completed: bool
    created_at: datetime
    due_date: datetime | None
    recurrence_pattern: RecurrencePattern | None

    # Phase III AI-ready fields (pre-provisioned)
    transcription_text: str | None
    ai_summary: str | None
    embedding_id: str | None
```

### 4. Repository Pattern

Both Phase I and Phase II use the Repository pattern:

```python
# Abstract interface
class TaskRepository(ABC):
    def add(self, task: Task) -> Task: ...
    def get(self, task_id: int) -> Task | None: ...
    def list(self) -> list[Task]: ...
    def update(self, task: Task) -> Task: ...
    def delete(self, task_id: int) -> bool: ...

# Phase I: In-memory implementation
class InMemoryTaskRepository(TaskRepository): ...

# Phase II: SQLModel implementation (planned)
class SQLModelTaskRepository(TaskRepository): ...
```

### 5. Error Handling Strategy

#### Backend (FastAPI)

```python
# Returns 404 (not 403) for ownership verification
# to prevent ID enumeration attacks

if task.user_id != current_user_id:
    raise HTTPException(status_code=404)
```

#### Frontend (Next.js)

```typescript
// Result type for error handling
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError }

// Usage
const result = await api.createTask(data)
if (result.success) {
  // Handle success
} else {
  // Handle error
  toast.error(result.error.message)
}
```

## Workflow Preferences

### When Working on Backend

1. **Always read existing models first** — Check `backend/app/models.py`
2. **Use async/await throughout** — All database operations are async
3. **Return TaskPublic from endpoints** — Never expose internal fields
4. **Create audit logs** — Use `create_task_log()` for modifications
5. **Test with Swagger UI** — Available at http://localhost:8000/docs

### When Working on Frontend

1. **Server Components by default** — Only use `"use client"` when necessary
2. **Use TanStack Query for server state** — Never duplicate in Zustand
3. **Use Zustand for client UI state** — Filters, modals, toasts
4. **All API calls go through api-client** — Don't use fetch directly
5. **Form validation with Zod** — Match backend validation rules

### When Adding Features

1. **Update Phase I first** — Prove the concept in the console app
2. **Add to backend models** — Include AI-ready fields for Phase III
3. **Create backend endpoints** — With proper error handling
4. **Add to frontend API client** — Auto-fetches JWT
5. **Build UI components** — Use shadcn/ui patterns

## Important Constraints

### Security

- **Never hardcode secrets** — Use `.env` files
- **404 not 403 for ownership checks** — Prevents enumeration
- **JWT in httpOnly cookies** — Never localStorage
- **SQL injection protection** — Use parameterized queries

### Performance

- **Connection pooling** — Backend uses asyncpg pool
- **Pagination** — Default 50 items per page
- **Request timeout** — 15 seconds for API calls
- **Automatic retry** — For transient network failures

### Phase Isolation

When working on a phase, **do not modify** other phases' code unless:
1. Fixing a bug that affects all phases
2. Updating shared documentation
3. Explicitly evolving to the next phase

## Extension Points

### Phase III: AI Integration

The following are pre-provisioned:

```python
# Backend (app/models.py)
task.transcription_text  # Voice input storage
task.ai_summary         # LLM-generated summary
task.embedding_id       # Vector search ID
```

```typescript
// Frontend (types/task.ts)
export interface Task {
  transcription_text: string | null
  ai_summary: string | null
  embedding_id: string | null
}
```

### Phase IV: Kubernetes

Helm chart structure (planned):
```
helm/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
```

### Phase V: Dapr Integration

Dapr sidecar patterns (planned):
- Pub/sub via Kafka
- State store for caching
- Service discovery for microservices

## Recent Changes
- 010-loading-states-user-profile: Added Python 3.13+ (backend), TypeScript 5+ (frontend)
- 009-light-mode-theme: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
- 008-dashboard-ui-overhaul: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

## Active Technologies
- Python 3.13+ (backend), TypeScript 5+ (frontend) (010-loading-states-user-profile)
- Neon Serverless PostgreSQL (PostgreSQL 16+) (010-loading-states-user-profile)
