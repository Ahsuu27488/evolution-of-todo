"""SQLModel database models for Chronos Todo App.

This module defines:
- Task model with all Phase I features (Basic + Intermediate + Advanced)
- TaskLog model for audit trail
- AI-ready fields for Phase III continuity
- Pydantic schemas for request/response validation

Per data-model.md specification.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_serializer, field_validator
from sqlalchemy import Column, DateTime, func, JSON
from sqlmodel import SQLModel, Field as SQLField, Relationship


# =============================================================================
# Enums
# =============================================================================

class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecurrencePattern(str, Enum):
    """Recurring task patterns."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class Action(str, Enum):
    """Audit log action types."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    COMPLETED = "completed"
    UNCOMPLETED = "uncompleted"
    RECURRED = "recurred"


# =============================================================================
# Tag Model (embedded in tasks as JSON)
# =============================================================================

class Tag(BaseModel):
    """Tag with name and color.

    Stored as JSONB in tasks table.
    Max 10 tags per task, max 30 chars per tag name.
    """
    name: str = Field(min_length=1, max_length=30)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")  # Hex color

    def to_dict(self) -> dict[str, Any]:
        """Convert Tag to dict for JSON storage."""
        return {"name": self.name, "color": self.color}


# =============================================================================
# Task Models
# =============================================================================

class TaskBase(SQLModel):
    """Base task fields shared across create/update models."""
    title: str = SQLField(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = SQLField(
        default=None,
        max_length=1000,
        description="Optional task description",
    )
    priority: Priority = SQLField(
        default=Priority.MEDIUM,
        description="Task priority level",
    )
    tags: list[Tag] = SQLField(
        default_factory=list,
        sa_column=Column(JSON),
        description="Task tags with colors (JSONB)",
    )
    due_date: Optional[datetime] = SQLField(
        default=None,
        description="Task due date/time",
    )
    recurrence_pattern: Optional[RecurrencePattern] = SQLField(
        default=None,
        description="Recurring task pattern (DAILY, WEEKLY, MONTHLY)",
    )


class Task(TaskBase, table=True):
    """Database model for tasks.

    Includes all Phase I features plus AI-ready fields for Phase III.
    Per data-model.md specification.
    """
    __tablename__ = "tasks"

    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: str = SQLField(
        index=True,
        description="Owner user ID from Better Auth",
    )
    completed: bool = SQLField(
        default=False,
        index=True,
        description="Task completion status",
    )

    # AI-ready fields for Phase III (nullable in Phase II)
    transcription_text: Optional[str] = SQLField(
        default=None,
        description="AI-ready: Raw voice command text from Phase III",
    )
    ai_summary: Optional[str] = SQLField(
        default=None,
        description="AI-ready: LLM-generated task summary",
    )
    embedding_id: Optional[str] = SQLField(
        default=None,
        description="AI-ready: Vector search ID for semantic search",
    )

    created_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
        description="Last update timestamp",
    )

    # Relationships
    logs: list["TaskLog"] = Relationship(back_populates="task")


# =============================================================================
# Task Log Models (Audit Trail)
# =============================================================================

class TaskLogBase(SQLModel):
    """Base fields for task log entries."""
    action: Action = SQLField(description="Action performed on task")
    changed_fields: dict[str, Any] = SQLField(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Before/after values of changed fields",
    )


class TaskLog(TaskLogBase, table=True):
    """Database model for task audit trail.

    Tracks all task modifications for history and debugging.
    Per data-model.md specification.
    """
    __tablename__ = "task_logs"

    id: Optional[int] = SQLField(default=None, primary_key=True)
    task_id: int = SQLField(
        foreign_key="tasks.id",
        index=True,
        description="Related task ID",
    )
    user_id: str = SQLField(
        index=True,
        description="User who performed the action",
    )
    created_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        index=True,
        description="When the action occurred",
    )

    # Relationships
    task: Task = Relationship(back_populates="logs")


# =============================================================================
# Request/Response Models (Pydantic Schemas)
# =============================================================================

class TaskCreate(TaskBase):
    """Request model for creating a task.

    All fields optional except title (min 1, max 200 chars).
    """
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "priority": "MEDIUM",
                    "tags": [{"name": "shopping", "color": "#00f5ff"}],
                    "due_date": "2026-01-10T12:00:00Z",
                }
            ]
        }
    }

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[Tag]) -> list[Tag]:
        """Validate tag constraints (max 10 tags)."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed per task")
        return v

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class TaskUpdate(SQLModel):
    """Request model for updating a task.

    All fields optional - only provided fields are updated.
    """
    title: Optional[str] = SQLField(default=None, min_length=1, max_length=200)
    description: Optional[str] = SQLField(default=None, max_length=1000)
    priority: Optional[Priority] = None
    tags: Optional[list[Tag]] = None
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    completed: Optional[bool] = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[Tag]]) -> Optional[list[Tag]]:
        """Validate tag constraints (max 10 tags)."""
        if v is not None and len(v) > 10:
            raise ValueError("Maximum 10 tags allowed per task")
        return v

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip() if v else None


class TaskPublic(TaskBase):
    """Response model for task data (excludes internal/audit fields).

    Includes all user-facing fields plus ID, timestamps, completion status.
    """
    id: int
    user_id: str
    completed: bool
    transcription_text: Optional[str] = None
    ai_summary: Optional[str] = None
    embedding_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TaskList(SQLModel):
    """Response model for paginated task list."""
    tasks: list[TaskPublic]
    total: int
    page: int = 1
    per_page: int = 50


class TaskLogPublic(SQLModel):
    """Response model for task log entries."""
    id: int
    task_id: int
    user_id: str
    action: Action
    changed_fields: dict[str, Any]
    created_at: datetime


# =============================================================================
# User Models (for Better Auth integration)
# =============================================================================

class UserPublic(SQLModel):
    """Public user information returned by auth endpoints."""
    id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None


class UserCreate(SQLModel):
    """Request model for user registration."""
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=1, max_length=100)


class UserLogin(SQLModel):
    """Request model for user login."""
    email: str
    password: str


class LoginResponse(SQLModel):
    """Response model for successful login."""
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
