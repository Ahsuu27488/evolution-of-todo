---
name: sqlmodel-guide
description: Fetch SQLModel documentation and apply database best practices. Use when creating models, queries, or database operations (Phase II+).
version: 2.0.0
---

# SQLModel Database Mastery Skill

## Theoretical Foundation

SQLModel combines **Pydantic** and **SQLAlchemy** into a single library:
- **Pydantic Models**: Data validation and serialization
- **SQLAlchemy Core**: Database operations and session management
- **Type Hints**: Full IDE support with Python 3.10+
- **FastAPI Integration**: Seamless API endpoint creation

### Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      SQLMODEL DUAL NATURE                                     │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        SQLModel Class                                   │ │
│  │  ┌─────────────────────┐  ┌─────────────────────────────────────────┐  │ │
│  │  │   Pydantic Model    │  │      SQLAlchemy Table                   │  │ │
│  │  │   (validation)      │  │      (persistence)                      │  │ │
│  │  │                     │  │                                         │  │ │
│  │  │  - Field() types    │  │  - table=True                           │  │ │
│  │  │  - validate()       │  │  - primary_key                          │  │ │
│  │  │  - model_dump()     │  │  - foreign_key                          │  │ │
│  │  │  - model_json_schema│  │  - index                                │  │ │
│  │  └─────────────────────┘  └─────────────────────────────────────────┘  │ │
│  │                                   │                                   │  │ │
│  │            One class definition serves BOTH purposes                   │  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                   │                                           │
│                                   ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                      Usage Patterns                                      │ │
│  │                                                                          │ │
│  │  FastAPI Request                                                        │ │
│  │       │                                                                 │ │
│  │       ▼                                                                 │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │  HeroCreate (Pydantic) ──▶ validates input                       │  │ │
│  │  │  Hero (table=True)       ◀─▶ persists to database                │  │ │
│  │  │  HeroPublic (Pydantic)  ──▶ serializes output                    │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Base Model**: Shared fields for multiple related models
2. **Table Model**: Inherits base, adds `table=True` and primary key
3. **Create/Update Models**: Separate schemas for input validation
4. **Public Models**: Response schemas (may exclude sensitive fields)
5. **Session Management**: Context manager for database operations

## When to Use This Skill

Activation triggers:
- Defining database models with SQLModel
- Creating CRUD operations with FastAPI
- Setting up relationships between tables
- Writing queries with filters and joins
- Managing database sessions

## Context7 Research Results

**Library ID**: `/websites/sqlmodel_tiangolo`
**Source**: https://sqlmodel.tiangolo.com
**Reputation**: High
**Code Snippets**: 2464+

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
```

## Implementation Guidelines

### 1. Model Definition Pattern

```python
# models/task.py
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

class TaskBase(SQLModel):
    """Shared fields across all Task models."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: str = Field(default="MEDIUM")  # HIGH, MEDIUM, LOW
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    """Database table model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    """Input schema for creating tasks."""
    pass

class TaskUpdate(SQLModel):
    """Input schema for updating tasks (all fields optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None

class TaskPublic(TaskBase):
    """Output schema (excludes internal fields)."""
    id: int
    created_at: datetime
```

### 2. Database Session Dependency

```python
# database.py
from sqlmodel import Session, create_engine
from typing import Annotated, Generator

DATABASE_URL = "postgresql://..."

engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, None, None]:
    """Dependency for database session with automatic cleanup."""
    with Session(engine) as session:
        yield session

# Type alias for cleaner dependency injection
SessionDep = Annotated[Session, Depends(get_session)]

# Usage in FastAPI
@app.get("/tasks")
def list_tasks(session: SessionDep):
    tasks = session.exec(select(Task)).all()
    return tasks
```

### 3. CRUD Operations with FastAPI

```python
# routers/tasks.py
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

from ..models import Task, TaskCreate, TaskUpdate, TaskPublic
from ..database import SessionDep

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, session: SessionDep, user_id: str) -> Task:
    """Create a new task."""
    db_task = Task.model_validate(task)
    db_task.user_id = user_id
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("", response_model=list[TaskPublic])
def list_tasks(
    session: SessionDep,
    user_id: str,
    offset: int = 0,
    limit: int = 100,
) -> list[Task]:
    """List all tasks for user with pagination."""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(statement).all()

@router.get("/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: SessionDep, user_id: str) -> Task:
    """Get a specific task by ID."""
    task = session.exec(
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: SessionDep,
    user_id: str,
) -> Task:
    """Update a task."""
    db_task = session.exec(
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_update.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, session: SessionDep, user_id: str):
    """Delete a task."""
    task = session.exec(
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
```

### 4. Advanced Query Patterns

```python
from sqlmodel import Session, select, col, or_, and_

# Filter by multiple conditions
def search_tasks(session: Session, user_id: str, query: str):
    statement = select(Task).where(
        Task.user_id == user_id,
        or_(
            col(Task.title).ilike(f"%{query}%"),
            col(Task.description).ilike(f"%{query}%")
        )
    )
    return session.exec(statement).all()

# Sort with multiple columns
def list_tasks_sorted(session: Session, user_id: str):
    statement = select(Task).where(
        Task.user_id == user_id
    ).order_by(col(Task.completed).asc(), col(Task.created_at).desc())
    return session.exec(statement).all()

# Count with filters
def count_pending(session: Session, user_id: str):
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False
    )
    return len(session.exec(statement).all())
```

### 5. Relationships

```python
# models/user.py
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .task import Task

class User(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")

# models/task.py
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    title: str

    # Relationships
    user: User = Relationship(back_populates="tasks")

# Usage: eager loading
def get_tasks_with_user(session: Session):
    from sqlmodel import selectinload
    statement = select(Task).options(selectinload(Task.user))
    return session.exec(statement).all()
```

## Code Standards

| Rule | Description |
|------|-------------|
| **Separate Models** | Use Create/Update/Public models for each operation |
| **Field Constraints** | Add `min_length`, `max_length`, `index` to fields |
| **Type Aliases** | Use `SessionDep = Annotated[Session, Depends(get_session)]` |
| **Nullable Types** | Use `Optional[T]` or `T | None` for nullable fields |
| **Relationships** | Use `Relationship()` with `back_populates` |

## Field Types Reference

| Python Type | SQL Type | Notes |
|-------------|----------|-------|
| `str` | VARCHAR | Use `Field(max_length=N)` for limit |
| `int` | INTEGER | Auto-increment with `primary_key=True` |
| `float` | FLOAT | For decimal values |
| `bool` | BOOLEAN | Default: `Field(default=False)` |
| `datetime` | TIMESTAMP | Use `default_factory=datetime.utcnow` |
| `bytes` | BYTEA | For binary data |
| `JSON` | JSON/JSONB | Postgres JSON type |

## Common Pitfalls

### 1. Not Using `model_dump(exclude_unset=True)`
**Symptom**: All fields updated even if not provided
**Fix**: Use `task_data = task_update.model_dump(exclude_unset=True)`

### 2. Forgetting `session.refresh()`
**Symptom**: ID not returned after insert
**Fix**: Call `session.refresh(db_obj)` after commit

### 3. Missing `table=True`
**Symptom**: Model not created in database
**Fix**: Add `table=True` to database models

### 4. Not Using Indexes
**Symptom**: Slow queries on large datasets
**Fix**: Add `index=True` to frequently queried fields

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| CRUD | "CRUD create read update delete FastAPI" |
| Relationships | "Relationship foreign_key back_populates" |
| Select queries | "select where order_by limit offset filtering" |
| Sessions | "Session dependency injection context manager" |
| Field types | "Field String Integer DateTime constraints" |

## References

- **Documentation**: https://sqlmodel.tiangolo.com
- **Tutorial**: https://sqlmodel.tiangolo.com/tutorial/
- **FastAPI Integration**: https://sqlmodel.tiangolo.com/tutorial/fastapi/
- **Context7 ID**: `/websites/sqlmodel_tiangolo`
