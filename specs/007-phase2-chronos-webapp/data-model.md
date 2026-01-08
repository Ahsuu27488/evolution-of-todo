# Data Model: Phase II - "Chronos" Web App

**Feature**: 007-phase2-chronos-webapp
**Date**: 2026-01-06
**Status**: Complete

## Overview

This document defines the database schema for Phase II "Chronos" Professional Web App. The schema is designed to:
1. Support all Phase I features (Basic + Intermediate + Advanced)
2. Enable multi-user data isolation
3. Include AI-ready fields for Phase III continuity

---

## Database: Neon PostgreSQL

**Technology**: PostgreSQL 16+ (Neon Serverless)
**Driver**: asyncpg (via SQLModel)
**Connection String Environment Variable**: `DATABASE_URL`

---

## Tables

### users (Managed by Better Auth)

Better Auth manages the `users` table. This table is created and maintained by the authentication library.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | text | PRIMARY KEY | User identifier (UUID) |
| email | text | UNIQUE, NOT NULL | User email address |
| name | text | nullable | User display name |
| emailVerified | boolean | DEFAULT false | Email verification status |
| image | text | nullable | Profile image URL |
| createdAt | timestamp | DEFAULT NOW() | Account creation timestamp |
| updatedAt | timestamp | DEFAULT NOW() | Last update timestamp |

**Notes**:
- Better Auth creates this table automatically
- Do not manually modify this table structure
- Use Better Auth APIs for user CRUD operations

---

### tasks

Core task entity with full Phase I feature parity plus AI-ready fields.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing task identifier |
| user_id | text | NOT NULL, FOREIGN KEY → users.id | Task owner |
| title | varchar(200) | NOT NULL | Task title |
| description | text | nullable | Task description (max 1000 chars) |
| priority | varchar(10) | NOT NULL, DEFAULT 'MEDIUM' | Priority: HIGH, MEDIUM, LOW |
| completed | boolean | NOT NULL, DEFAULT false | Completion status |
| tags | jsonb | DEFAULT '[]' | Array of {name, color} objects |
| due_date | timestamp | nullable | Task deadline |
| recurrence_pattern | varchar(10) | nullable | DAILY, WEEKLY, MONTHLY |
| transcription_text | text | nullable | **AI-ready**: Voice command log |
| ai_summary | text | nullable | **AI-ready**: LLM-generated summary |
| embedding_id | text | nullable | **AI-ready**: Vector search ID |
| created_at | timestamp | DEFAULT NOW() | Creation timestamp |
| updated_at | timestamp | DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `idx_tasks_user_id` ON tasks(user_id) -- For user filtering
- `idx_tasks_completed` ON tasks(completed) -- For status filtering
- `idx_tasks_due_date` ON tasks(due_date) -- For deadline sorting
- `idx_tasks_priority` ON tasks(priority) -- For priority filtering
- `idx_tasks_created_at` ON tasks(created_at DESC) -- For recent tasks

**Foreign Key**:
- `fk_tasks_user` FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

**Constraints**:
- `chk_priority` CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW'))
- `chk_recurrence` CHECK (recurrence_pattern IN ('DAILY', 'WEEKLY', 'MONTHLY'))
- `chk_title_length` CHECK (char_length(title) >= 1 AND char_length(title) <= 200)

**AI-Ready Fields**:
- `transcription_text`: Stores raw voice command text from Phase III
- `ai_summary`: LLM-generated task context/summary
- `embedding_id`: Vector ID for semantic search (Phase III+)

---

### task_logs

Audit trail for all task modifications.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing log identifier |
| task_id | integer | NOT NULL, FOREIGN KEY → tasks.id | Related task |
| user_id | text | NOT NULL, FOREIGN KEY → users.id | User who made change |
| action | varchar(20) | NOT NULL | Action type |
| changed_fields | jsonb | DEFAULT '{}' | Before/after values |
| created_at | timestamp | DEFAULT NOW() | When action occurred |

**Indexes**:
- `idx_task_logs_task_id` ON task_logs(task_id) -- For task history lookup
- `idx_task_logs_user_id` ON task_logs(user_id) -- For user activity
- `idx_task_logs_created_at` ON task_logs(created_at DESC) -- For recent activity

**Foreign Keys**:
- `fk_task_logs_task` FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
- `fk_task_logs_user` FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

**Constraints**:
- `chk_action` CHECK (action IN ('created', 'updated', 'deleted', 'completed', 'uncompleted', 'recurred'))

**Action Types**:
- `created`: New task created
- `updated`: Task fields modified
- `deleted`: Task deleted
- `completed`: Task marked complete
- `uncompleted`: Task marked incomplete
- `recurred`: New recurring task created

---

## Entity Relationships

```
┌─────────────────┐
│     users       │
│  (Better Auth)  │
└────────┬────────┘
         │ 1
         │
         │ N
┌─────────────────────┐         ┌─────────────────┐
│      tasks          │         │   task_logs     │
│ ┌─────────────────┐ │         │ ┌──────────────┐ │
│ │ id: SERIAL PK  │ │         │ │ id: SERIAL PK│ │
│ │ user_id: FK    │◄┼─────────┤ │ task_id: FK  │ │
│ │ ...fields      │ │         │ │ user_id: FK  │ │
│ └─────────────────┘ │         │ └──────────────┘ │
└─────────────────────┘         └─────────────────┘
```

**Relationships**:
- users → tasks: One-to-Many (one user has many tasks)
- users → task_logs: One-to-Many (one user makes many log entries)
- tasks → task_logs: One-to-Many (one task has many log entries)

---

## SQLModel Definitions (Python)

```python
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON, DateTime, func
from sqlalchemy.dialects.postgresql import ENUM

# Enums
PriorityEnum = ENUM("HIGH", "MEDIUM", "LOW", name="priority")
RecurrenceEnum = ENUM("DAILY", "WEEKLY", "MONTHLY", name="recurrence")
ActionEnum = ENUM("created", "updated", "deleted", "completed", "uncompleted", "recurred", name="action")

# Tag model (embedded in tasks as JSON)
class Tag(SQLModel):
    name: str
    color: str

# Base models
class TaskBase(SQLModel):
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: str = Field(default="MEDIUM")
    completed: bool = Field(default=False)
    tags: List[Tag] = Field(default_factory=list, sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(default=None)
    recurrence_pattern: Optional[str] = Field(default=None)

class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    transcription_text: Optional[str] = Field(default=None)  # AI-ready
    ai_summary: Optional[str] = Field(default=None)           # AI-ready
    embedding_id: Optional[str] = Field(default=None)        # AI-ready
    created_at: datetime = Field(default_factory=func.now())
    updated_at: datetime = Field(default_factory=func.now())

    # Relationships
    logs: List["TaskLog"] = Relationship(back_populates="task")

class TaskLogBase(SQLModel):
    action: str
    changed_fields: dict = Field(default_factory=dict)

class TaskLog(TaskLogBase, table=True):
    __tablename__ = "task_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id")
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=func.now())

    # Relationships
    task: Task = Relationship(back_populates="logs")
```

---

## Migration Strategy

1. **Initial Migration**: Create all tables with indexes
2. **Better Auth Setup**: Run Better Auth migrations first (creates users table)
3. **Tasks Migration**: Create tasks table with AI-ready fields
4. **Task Logs Migration**: Create task_logs table
5. **Seed Data**: None required (starts empty)

**Migration Tool**: Alembic (recommended) or raw SQL scripts

---

## Data Integrity Rules

### User Isolation
- All queries MUST filter by `user_id`
- API MUST verify JWT token matches `user_id` on operations
- 404 Not Found for accessing other users' tasks (not 403, to prevent ID enumeration)

### Cascading Deletes
- When user is deleted: All tasks and task_logs deleted (CASCADE)
- When task is deleted: All task_logs deleted (CASCADE)

### Timestamps
- `created_at`: Set on creation, never modified
- `updated_at`: Updated on every modify operation

### JSON Field: tags
- Stored as JSONB for efficient querying
- Format: `[{"name": "work", "color": "#00f5ff"}, {"name": "urgent", "color": "#ef4444"}]`
- Max 10 tags per task (enforced at application level)

---

## Phase III Continuity

The following fields are reserved for Phase III AI features:

| Field | Purpose | Phase II Value |
|-------|---------|----------------|
| `transcription_text` | Store raw voice command text | NULL |
| `ai_summary` | LLM-generated task context/summary | NULL |
| `embedding_id` | Vector search identifier | NULL |

**Migration Notes**:
- Fields are nullable in Phase II
- No migration needed in Phase III (fields already exist)
- Application logic in Phase III will populate these fields

---

## Performance Considerations

### Index Strategy
- Index on `user_id` for all user queries (most common access pattern)
- Index on `completed` for filtering
- Index on `due_date` for deadline sorting
- Composite index on `(user_id, completed)` for common filtered queries

### Query Patterns
- **List tasks**: `WHERE user_id = ? ORDER BY created_at DESC LIMIT 50`
- **Filter pending**: `WHERE user_id = ? AND completed = false`
- **Filter priority**: `WHERE user_id = ? AND priority = 'HIGH'`
- **Search**: `WHERE user_id = ? AND (title ILIKE ? OR description ILIKE ?)`

### Connection Pooling
- Use Neon's connection pooling (pgbouncer)
- Min pool size: 5, Max pool size: 20
