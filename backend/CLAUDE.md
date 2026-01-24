# backend/ — Chronos Todo API

**Claude Code Context** for the FastAPI backend (Phase II Chronos WebApp).

## Project Purpose

FastAPI REST API serving the Chronos Todo frontend with:
- Task CRUD operations with filtering, sorting, search
- JWT authentication compatible with Better Auth
- Async PostgreSQL database operations
- Audit trail for all task modifications

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  CORS Mdw    │  │ Request ID   │  │ Error Handlers   │  │
│  └──────────────┘  │  Middleware  │  │                  │  │
│        └───────────┴──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        API Routes                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  /api/auth   │  │  /api/tasks  │  │  /api/health     │  │
│  │  - signup    │  │  - CRUD      │  │  - status check  │  │
│  │  - signin    │  │  - search    │  │                  │  │
│  │  - me        │  │  - filter    │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Authentication                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         HTTPBearer (JWT Token)                      │  │
│  │                    │                                 │  │
│  │                    ▼                                 │  │
│  │         get_current_user_id                         │  │
│  │         (extracts 'sub' claim)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Access                            │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │   get_session()  │────────▶│  AsyncSession (SQLAlchemy)│ │
│  │   FastAPI Dep    │         │  + Async Engine          │ │
│  └──────────────────┘         │  + Connection Pool        │ │
│                              └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (Neon)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   tasks      │  │  task_logs   │  │ (users in-memory)│  │
│  │   (JSONB)    │  │  (audit)     │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Key File Locations

| File | Purpose | Key Details |
|------|---------|-------------|
| `main.py` | FastAPI app | Lifespan, CORS, middleware, route registration |
| `db.py` | Database config | Async engine, session factory, table creation |
| `models.py` | Data models | Task, TaskLog, Tag, Pydantic schemas |
| `errors.py` | Error handling | Custom exceptions, error middleware |
| `simple_auth.py` | JWT auth | Token verification, password hashing, dependencies |
| `routes/tasks.py` | Task endpoints | CRUD, search, filtering, audit logs |
| `routes/auth.py` | Auth endpoints | Signup, signin, signout, /me |
| `.env.example` | Config template | Required env vars |

## Architecture Patterns

### Dependency Injection for Auth

All protected endpoints use `get_current_user_id` dependency:

```python
@router.get("/api/tasks")
async def list_tasks(
    user_id: str = Depends(get_current_user_id),  # ← Injects user_id from JWT
    session: AsyncSession = Depends(get_session),  # ← Injects DB session
) -> TaskList:
    # user_id is guaranteed to be valid here
    statement = select(Task).where(Task.user_id == user_id)
```

### Async Database Sessions

Database operations use SQLAlchemy async:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Usage in endpoint
@router.post("/api/tasks")
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
):
    task = Task(**task_data.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
```

### Error Handling Hierarchy

```
Exception (base)
    │
    ├── HTTPException (FastAPI)
    │     └── Handled by http_exception_handler → 4xx/5xx response
    │
    └── AppException (custom)
            ├── AuthenticationError → 401
            ├── AuthorizationError → 403
            ├── NotFoundError → 404
            ├── ValidationError → 422
            └── DatabaseError → 500
```

All errors return `ErrorResponse` format:

```json
{
  "detail": "Error message",
  "code": "NOT_FOUND",
  "request_id": "req_abc123",
  "timestamp": "2025-01-10T12:00:00Z",
  "path": "/api/tasks/123"
}
```

## Coding Conventions

### Type Hints

All functions use full type hints with return types:

```python
async def get_task_or_404(
    task_id: int,
    user_id: str,
    session: AsyncSession,
) -> Task:
    ...
```

### Request/Response Models

Separate Pydantic models for input/output:

| Model | Purpose |
|-------|---------|
| `TaskCreate` | POST request (partial fields) |
| `TaskUpdate` | PUT request (all optional) |
| `TaskPublic` | GET response (user-facing) |
| `TaskLogPublic` | Audit log response |

### Ownership Verification

Every task access verifies ownership (404 not 403 for security):

```python
async def get_task_or_404(task_id: int, user_id: str, session: AsyncSession) -> Task:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await session.execute(statement)).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404)  # Not 403 — prevents enumeration
    return task
```

### Audit Logging

All modifications create TaskLog entries:

```python
await create_task_log(
    session=session,
    task_id=task.id,
    user_id=current_user_id,
    action=Action.UPDATED,
    changed_fields={"title": {"old": "old", "new": "new"}},
)
```

## JWT Authentication Flow

```
┌─────────────┐     Authorization: Bearer <token>      ┌──────────────┐
│   Frontend  │────────────────────────────────────────│   FastAPI    │
└─────────────┘                                        └──────────────┘
                                                            │
                                                            ▼
                                                     ┌──────────────┐
                                                     │ HTTPBearer   │
                                                     │ extractor    │
                                                     └──────────────┘
                                                            │
                                                            ▼
                                                     ┌──────────────┐
                                                     │ verify_token │
                                                     │ (python-jose)│
                                                     └──────────────┘
                                                            │
                                                    ┌───────────┴───────────┐
                                                    │                       │
                                                   FAIL                   SUCCESS
                                                    │                       │
                                                    ▼                       ▼
                                              ┌──────────┐         ┌──────────────┐
                                              │ 401      │         │ Extract sub  │
                                              │ response │         │ (user_id)    │
                                              └──────────┘         └──────────────┘
```

## JSONB Query Patterns

### Tag Filtering (JSONB contains)

```python
# Filter tasks by tag name
if tag:
    statement = statement.where(Task.tags.contains([{"name": tag}]))
```

### Priority Sorting

Priority uses special Python sorting (enums don't sort naturally):

```python
def priority_sort_value(priority: str) -> int:
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return order.get(priority, 1)

tasks.sort(key=lambda t: priority_sort_value(t.priority), reverse=True)
```

## Connection Pool Settings

Optimized for serverless Neon (per research.md):

| Setting | Value | Rationale |
|---------|-------|-----------|
| `pool_size` | 5 | Min connections per Neon quickstart |
| `max_overflow` | 15 | Max additional connections (total: 20) |
| `pool_recycle` | 300s | Recycle before Neon closes idle |
| `pool_pre_ping` | True | Verify connections before use |
| `echo` | DEBUG | SQL logging in development only |

## SSL Configuration

Neon requires SSL but URL-based SSL causes `channel_binding` errors. Solution:

```python
# Strip SSL from URL
ASYNC_DATABASE_URL = DATABASE_URL.split("?")[0]

# Configure SSL via code
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(ASYNC_DATABASE_URL, connect_args={"ssl": ssl_context})
```

## Recurring Task Logic

When a recurring task is marked complete:

1. Original task `completed = True`
2. Calculate next due date based on pattern
3. Create new task with same properties, new due date
4. Log `RECURRED` action with parent task ID

**Location**: `routes/tasks.py:453-537` (toggle_task_complete)

## Extension Points for Phase III

### AI Field Usage

Fields are pre-provisioned but unused in Phase II:

```python
# Phase III: Store voice transcription
task.transcription_text = transcribe_audio(audio_file)

# Phase III: Store LLM summary
task.ai_summary = generate_summary(task.title, task.description)

# Phase III: Store vector embedding
task.embedding_id = vector_store.embed(task.title + " " + task.description)
```

### Vector Search Integration

```python
# Phase III endpoint
@router.get("/api/tasks/semantic")
async def semantic_search(
    query: str,
    user_id: str = Depends(get_current_user_id),
):
    # Use embedding_id to query vector database
    similar_ids = vector_search(query, user_id)
    return await get_tasks_by_ids(similar_ids)
```

## Important Constraints

- **All endpoints return JSON** — No HTML responses
- **404 not 403** for ownership checks — Prevents ID enumeration
- **Token must include `sub` claim** — User ID extracted from JWT
- **Tags stored as JSONB** — Max 10 tags, validated in Pydantic
- **Audit logs cascade delete** — TaskLog deleted when Task deleted
