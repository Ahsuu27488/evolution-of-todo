---
name: fastapi-guide
description: Fetch FastAPI documentation and apply web API best practices. Use when building REST APIs, endpoints, or backend services (Phase II+).
version: 2.0.0
---

# FastAPI Mastery Skill

## Theoretical Foundation

FastAPI is a modern Python web framework for building APIs with:
- **High Performance**: Based on Starlette and Pydantic
- **Type Hints**: Automatic data validation and serialization
- **OpenAPI**: Auto-generated interactive documentation
- **Async Support**: Native `async/await` for I/O operations

### Request-Response Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI REQUEST LIFECYCLE                             │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Client                                                                       │
│    │                                                                          │
│    │ HTTP POST /api/tasks                                                    │
│    │ { "title": "Buy milk" }                                                 │
│    ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                         FastAPI Application                          │     │
│  │  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐  │     │
│  │  │ Middleware  │───▶│ Path         │───▶│ Dependency Injection    │  │     │
│  │  │ (CORS,      │    │ Operation    │    │ (get_session, auth)     │  │     │
│  │  │  Auth)      │    │ @app.post()  │    │                         │  │     │
│  │  └─────────────┘    └──────┬───────┘    └───────────┬─────────────┘  │     │
│  │                            │                        │                 │     │
│  │                            ▼                        ▼                 │     │
│  │                    ┌───────────────┐      ┌───────────────┐          │     │
│  │                    │ Pydantic      │      │ Business      │          │     │
│  │                    │ Validation    │      │ Logic         │          │     │
│  │                    │ (auto         │      │ (create task) │          │     │
│  │                    │  deserialize) │      └───────┬───────┘          │     │
│  │                    └───────┬───────┘              │                 │     │
│  │                            │                      │                 │     │
│  │                            ▼                      ▼                 │     │
│  │                    ┌───────────────┐      ┌───────────────┐          │     │
│  │                    │ SQLModel      │      │ Response      │          │     │
│  │                    │ Database      │      │ Serialization │          │     │
│  │                    └───────────────┘      └───────┬───────┘          │     │
│  │                                                   │                 │     │
│  └───────────────────────────────────────────────────┼─────────────────┘     │
│                                                      │                       │
│    ▼                                                 │                       │
│  HTTP 201 Created                                    │                       │
│  { "id": 1, "title": "Buy milk", ... }               │                       │
│    │                                                 │                       │
│    └─────────────────────────────────────────────────┘                       │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Path Operations**: `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()`, `@app.patch()`
2. **Pydantic Models**: Request/response validation with automatic JSON serialization
3. **Dependency Injection**: `Depends()` for shared logic (auth, DB sessions)
4. **Status Codes**: HTTP status codes (200, 201, 204, 400, 404, 422, 500)
5. **Async Handlers**: `async def` for non-blocking I/O operations

## When to Use This Skill

Activation triggers:
- Creating REST API endpoints
- Implementing CRUD operations
- Setting up authentication/authorization
- Configuring middleware (CORS, auth)
- Defining Pydantic models for validation

## Context7 Research Results

**Library ID**: `/websites/fastapi_tiangolo`
**Source**: https://fastapi.tiangolo.com
**Reputation**: High
**Code Snippets**: 12,067+
**Benchmark Score**: 94.6

### Core CRUD Pattern (from Context7)

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Models
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class HeroCreate(HeroBase):
    pass

class HeroPublic(HeroBase):
    id: int

class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None

# Database setup
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep) -> Hero:
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

## Implementation Guidelines

### 1. API Router Structure

```python
# routers/tasks.py
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated

from ..models import Task, TaskCreate, TaskUpdate, TaskPublic
from ..database import get_session

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    session: SessionDep,
    current_user: dict = Depends(get_current_user),
) -> Task:
    """Create a new task for the authenticated user."""
    db_task = Task.model_validate(task)
    db_task.user_id = current_user["sub"]
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("", response_model=list[TaskPublic])
async def list_tasks(
    session: SessionDep,
    current_user: dict = Depends(get_current_user),
    status: str | None = None,
    priority: str | None = None,
) -> list[Task]:
    """List all tasks for the authenticated user with optional filters."""
    statement = select(Task).where(Task.user_id == current_user["sub"])

    if status:
        statement = statement.where(Task.completed == (status == "completed"))
    if priority:
        statement = statement.where(Task.priority == priority)

    return session.exec(statement).all()
```

### 2. Dependency Injection for Authentication

```python
# dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, PyJWTError
from os import getenv

security = HTTPBearer()

async def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict:
    """Verify JWT and return user payload."""
    try:
        payload = decode(
            credentials.credentials,
            getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"],
            audience=getenv("API_URL"),
        )
        return payload
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

# Type alias for cleaner code
CurrentUserDep = Annotated[dict, Depends(verify_token)]
```

### 3. Pydantic Models with Validation

```python
# models/task.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: Optional[datetime] = None

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

class TaskPublic(TaskBase):
    id: int
    completed: bool
    created_at: datetime
```

### 4. Error Handling

```python
# exceptions.py
from fastapi import HTTPException, status
from typing import Any, Dict

class AppException(HTTPException):
    """Base exception with structured error response."""

    def __init__(
        self,
        detail: str,
        code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "detail": self.detail,
            "status": self.status_code,
        }

# Usage
@app.post("/tasks")
async def create_task(task: TaskCreate):
    if len(task.title) == 0:
        raise AppException(
            detail="Title cannot be empty",
            code="INVALID_TITLE",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
```

### 5. CORS Configuration

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Todo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Code Standards

### Path Operation Rules

| Rule | Description |
|------|-------------|
| **Naming** | Use kebab-case for URL paths: `/api/tasks/{task_id}` |
| **Status Codes** | 201 for create, 200 for read, 204 for delete |
| **Response Models** | Always specify `response_model` for serialization |
| **Async First** | Use `async def` for I/O operations |
| **Type Hints** | Full type hints on all parameters and returns |

### Pydantic Model Standards

```python
# ✅ GOOD - Separate models for each operation
class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)

class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)

class TaskPublic(SQLModel):
    id: int
    title: str

# ❌ BAD - Single model for everything
class Task(SQLModel):
    id: int | None = None  # Confusing for create
    title: str
```

### Dependency Injection Standards

```python
# ✅ GOOD - Type alias for dependencies
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUserDep = Annotated[dict, Depends(verify_token)]

@router.get("/tasks")
def get_tasks(
    session: SessionDep,
    user: CurrentUserDep,
):
    pass

# ❌ BAD - Repeated Depends()
@router.get("/tasks")
def get_tasks(
    session: Session = Depends(get_session),
    user: dict = Depends(verify_token),
):
    pass
```

## Common Pitfalls

### 1. Missing `response_model`
**Symptom**: Internal fields (passwords, secrets) exposed
**Fix**: Always specify `response_model` for public schema

### 2. Not Using Async
**Symptom**: Blocking operations block entire application
**Fix**: Use `async def` and `await` for I/O

### 3. Forgetting `Annotated`
**Symptom**: Verbose dependency injection
**Fix**: Use `SessionDep = Annotated[Session, Depends(get_session)]`

### 4. Incorrect Status Codes
**Symptom**: 200 returned for create/delete
**Fix**: Use `status_code` parameter: `@app.post(..., status_code=201)`

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| CRUD operations | "CRUD SQLModel FastAPI create read update delete" |
| Dependency injection | "Depends Annotated dependency injection pattern" |
| Authentication | "JWT OAuth2 Bearer token security HTTPBearer" |
| Pydantic models | "Pydantic BaseModel validation Field constraints" |
| Error handling | "HTTPException status codes custom exceptions" |
| Middleware | "CORS middleware authentication request preprocessing" |

## OpenAPI Documentation

FastAPI auto-generates docs at `/docs` (Swagger UI) and `/redoc`.

Enable detailed docs:

```python
app = FastAPI(
    title="Todo API",
    description="Full-stack task management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.post(
    "/tasks",
    response_model=TaskPublic,
    status_code=201,
    summary="Create a new task",
    description="Creates a task for the authenticated user with the provided title, description, and priority.",
    responses={
        201: {"description": "Task created successfully"},
        401: {"description": "Unauthorized - invalid token"},
        422: {"description": "Validation error"},
    },
)
async def create_task(task: TaskCreate, user: CurrentUserDep):
    ...
```

## References

- **Documentation**: https://fastapi.tiangolo.com
- **Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **Context7 ID**: `/websites/fastapi_tiangolo`
