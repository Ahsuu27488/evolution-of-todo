# Phase II Data Model

**Feature**: 006-phase2-fullstack-webapp
**Date**: 2025-12-29
**Database**: Neon Serverless PostgreSQL

---

## Entity Relationship Diagram

```
┌──────────────────────────────────────┐
│                USER                   │
│  (Managed by Better Auth)            │
├──────────────────────────────────────┤
│  id: string (PK)                     │
│  email: string (unique)              │
│  name: string (nullable)             │
│  emailVerified: boolean              │
│  image: string (nullable)            │
│  createdAt: datetime                 │
│  updatedAt: datetime                 │
└──────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌──────────────────────────────────────┐
│                TASK                   │
│  (Managed by FastAPI/SQLModel)       │
├──────────────────────────────────────┤
│  id: integer (PK, auto-increment)    │
│  user_id: string (FK → user.id)      │ ─── Index: idx_task_user_id
│  title: string (1-200 chars)         │
│  description: string (nullable, max  │
│               1000 chars)            │
│  completed: boolean (default: false) │ ─── Index: idx_task_completed
│  created_at: datetime (auto)         │
│  updated_at: datetime (auto)         │
└──────────────────────────────────────┘
```

---

## SQLModel Definitions

### Task Model (backend/app/models.py)

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    """Base task fields shared across all task models."""
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional task description"
    )

class TaskCreate(TaskBase):
    """Request model for creating a task."""
    pass

class TaskUpdate(SQLModel):
    """Request model for updating a task (all fields optional)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

class Task(TaskBase, table=True):
    """Database model for tasks."""
    __tablename__ = "task"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, description="Owner user ID from Better Auth")
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskPublic(TaskBase):
    """Response model for task data (excludes internal fields)."""
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime

class TaskList(SQLModel):
    """Response model for list of tasks."""
    tasks: list[TaskPublic]
    total: int
```

---

## Validation Rules

### Title Field
| Rule | Constraint | Error Message |
|------|------------|---------------|
| Required | `min_length=1` | "Title is required" |
| Max Length | `max_length=200` | "Title must be 200 characters or less" |
| Trimmed | Strip whitespace | N/A (handled in service) |

### Description Field
| Rule | Constraint | Error Message |
|------|------------|---------------|
| Optional | `default=None` | N/A |
| Max Length | `max_length=1000` | "Description must be 1000 characters or less" |

### Completed Field
| Rule | Constraint | Error Message |
|------|------------|---------------|
| Default | `default=False` | N/A |
| Boolean | `bool` type | "Must be true or false" |

### User ID Field
| Rule | Constraint | Error Message |
|------|------------|---------------|
| Required | No default | "User ID required" |
| Foreign Key | References Better Auth users | "Invalid user" |
| Immutable | Cannot change after creation | "Cannot change task owner" |

---

## Database Indexes

```sql
-- Primary key (automatic)
CREATE INDEX idx_task_pkey ON task (id);

-- User lookup (for filtering user's tasks)
CREATE INDEX idx_task_user_id ON task (user_id);

-- Status filtering (for completed/pending filters)
CREATE INDEX idx_task_completed ON task (completed);

-- Compound index for common query pattern
CREATE INDEX idx_task_user_status ON task (user_id, completed);
```

---

## State Transitions

```
┌─────────────┐
│   CREATE    │ ──→ Task(completed=false)
└─────────────┘
       │
       ▼
┌─────────────┐      TOGGLE       ┌─────────────┐
│  INCOMPLETE │ ◄──────────────▶ │  COMPLETED   │
│ completed=  │                   │ completed=   │
│   false     │                   │   true       │
└─────────────┘                   └─────────────┘
       │                                 │
       │          DELETE                 │
       └───────────────┬─────────────────┘
                       ▼
               ┌─────────────┐
               │   DELETED   │ (removed from DB)
               └─────────────┘
```

---

## TypeScript Types (Frontend)

```typescript
// types/task.ts

export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string  // ISO 8601
  updated_at: string  // ISO 8601
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
}

export interface TaskList {
  tasks: Task[]
  total: number
}
```

---

## Zod Schemas (Frontend Validation)

```typescript
// lib/validations/task.ts
import { z } from 'zod'

export const taskCreateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less")
    .transform(val => val.trim()),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional()
    .transform(val => val?.trim() || undefined),
})

export const taskUpdateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less")
    .transform(val => val.trim())
    .optional(),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .transform(val => val?.trim() || undefined)
    .optional(),
})

export type TaskCreateInput = z.infer<typeof taskCreateSchema>
export type TaskUpdateInput = z.infer<typeof taskUpdateSchema>
```

---

## Better Auth User Schema

Better Auth manages the user table automatically. Key fields:

```typescript
// Managed by Better Auth - DO NOT modify directly
interface User {
  id: string           // UUID or similar
  email: string        // Unique
  name: string | null
  emailVerified: boolean
  image: string | null
  createdAt: Date
  updatedAt: Date
}

interface Session {
  id: string
  userId: string
  expiresAt: Date
  token: string        // JWT token
}
```

---

## Migration Strategy

### Initial Setup
```python
# backend/app/db.py
from sqlmodel import SQLModel

def create_db_and_tables():
    """Create all tables. Run on startup."""
    SQLModel.metadata.create_all(engine)
```

### FastAPI Lifespan
```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(lifespan=lifespan)
```

---

## Query Patterns

### List User's Tasks
```python
tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
).all()
```

### Get Task by ID (with ownership check)
```python
task = session.exec(
    select(Task)
    .where(Task.id == task_id)
    .where(Task.user_id == user_id)
).first()

if not task:
    raise HTTPException(404, "Task not found")
```

### Toggle Completion
```python
task.completed = not task.completed
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
session.refresh(task)
```

### Count by Status
```python
completed = session.exec(
    select(func.count(Task.id))
    .where(Task.user_id == user_id)
    .where(Task.completed == True)
).one()

pending = session.exec(
    select(func.count(Task.id))
    .where(Task.user_id == user_id)
    .where(Task.completed == False)
).one()
```
