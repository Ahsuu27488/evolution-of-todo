"""Notification and NotificationPreference models.

[Task]: T006-T007
[From]: spec.md §Key Entities, data-model.md §Entity Definitions
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field as SQLField, Relationship


# =============================================================================
# Enums
# =============================================================================


class NotificationType(str, Enum):
    """Notification types per FR-004.

    [From]: spec.md FR-004
    """

    TASK_DUE = "task_due"
    TASK_OVERDUE = "task_overdue"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_REMINDER = "task_reminder"
    SYSTEM_UPDATE = "system_update"


class NotificationChannel(str, Enum):
    """Delivery channels for notifications."""

    IN_APP = "in_app"
    PUSH = "push"
    EMAIL = "email"


class EmailFrequency(str, Enum):
    """Email frequency options per FR-022.

    [From]: spec.md FR-022
    """

    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    NONE = "none"


# =============================================================================
# Database Models
# =============================================================================


class Notification(SQLModel, table=True):
    """Core notification entity with read status and delivery tracking.

    [Task]: T006
    [From]: spec.md FR-001, FR-004, FR-009, FR-035
    [From]: data-model.md §Entity Definitions - Notification

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        type: Notification type enum
        title: Notification title
        message: Notification message body
        data: Additional JSON data (task_id, etc.)
        related_task_id: Optional FK to tasks table
        read_status: Whether user has read the notification
        created_at: Timestamp when notification was created
        sent_channels: List of channels this was sent to
        deleted_at: Soft delete timestamp (30-day archive per FR-035)
    """

    __tablename__ = "notifications"

    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: str = SQLField(
        foreign_key="users.id",
        index=True,
        description="Owner user ID from Better Auth",
    )

    # Notification content
    type: NotificationType = SQLField(index=True, description="Notification type")
    title: str = SQLField(max_length=200, description="Notification title")
    message: str = SQLField(max_length=1000, description="Notification message")
    data: dict[str, Any] = SQLField(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="Additional data (task_id, due_date, etc.)",
    )

    # Related entity (e.g., task that triggered notification)
    related_task_id: Optional[int] = SQLField(
        default=None,
        foreign_key="tasks.id",
        index=True,
        description="Related task ID if applicable",
    )

    # State tracking
    read_status: bool = SQLField(
        default=False,
        index=True,
        description="Whether user has read this notification",
    )
    created_at: datetime = SQLField(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
        index=True,
        description="When notification was created (timezone-aware)",
    )
    sent_channels: list[str] = SQLField(
        default_factory=list,
        sa_column=Column(JSONB),
        description="Channels notification was sent to",
    )

    # Soft delete support (30-day archive per spec)
    deleted_at: Optional[datetime] = SQLField(
        default=None,
        index=True,
        description="Soft delete timestamp for 30-day archive",
    )

    # Relationships
    # Note: Task relationship defined in main models.py to avoid circular import
    # related_task: Optional["Task"] = Relationship(back_populates="notifications")


class NotificationPreference(SQLModel, table=True):
    """Per-user notification settings with channel and frequency controls.

    [Task]: T007
    [From]: spec.md FR-032, FR-036, data-model.md §Entity Definitions - NotificationPreference

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        notification_type: Type this preference applies to
        in_app_enabled: Whether in-app notifications are enabled
        push_enabled: Whether push notifications are enabled (opt-in)
        email_enabled: Whether email notifications are enabled (opt-in)
        frequency: Email frequency (immediate, daily, weekly)
        dnd_start: Do Not Disturb start time (HH:MM format)
        dnd_end: Do Not Disturb end time (HH:MM format)
        created_at: When preference was created
        updated_at: When preference was last updated
    """

    __tablename__ = "notification_preferences"

    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: str = SQLField(
        foreign_key="users.id",
        description="Owner user ID from Better Auth",
    )

    # Notification type this preference applies to
    notification_type: NotificationType = SQLField(
        description="Notification type for this preference",
    )

    # Channel enablement
    in_app_enabled: bool = SQLField(
        default=True,
        description="Whether in-app notifications are enabled",
    )
    push_enabled: bool = SQLField(
        default=False,
        description="Whether push notifications are enabled (opt-in)",
    )
    email_enabled: bool = SQLField(
        default=False,
        description="Whether email notifications are enabled (opt-in)",
    )

    # Frequency for email (per FR-022)
    frequency: EmailFrequency = SQLField(
        default=EmailFrequency.IMMEDIATE,
        description="Email frequency: immediate, daily, weekly, or none",
    )

    # Do Not Disturb hours (per FR-036)
    dnd_start: Optional[str] = SQLField(
        default=None,
        max_length=5,
        description="Do Not Disturb start time (HH:MM format)",
    )
    dnd_end: Optional[str] = SQLField(
        default=None,
        max_length=5,
        description="Do Not Disturb end time (HH:MM format)",
    )

    created_at: datetime = SQLField(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
        description="When preference was created (timezone-aware)",
    )
    updated_at: datetime = SQLField(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=func.now()),
        description="When preference was last updated (timezone-aware)",
    )


# =============================================================================
# Pydantic Schemas for Request/Response
# =============================================================================


class NotificationPublic(SQLModel):
    """Response model for notification data.

    Excludes internal fields while providing user-facing data.
    """

    id: int
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: dict[str, Any]
    related_task_id: Optional[int] = None
    read_status: bool
    created_at: datetime
    sent_channels: list[str]


class NotificationList(SQLModel):
    """Response model for paginated notification list.

    [From]: spec.md FR-009, contracts/api.yaml §1.1 List Notifications
    """

    items: list[NotificationPublic]
    total: int
    unread_count: int
    limit: int = 10
    offset: int = 0


class NotificationPreferenceCreate(SQLModel):
    """Request model for creating/updating notification preferences.

    All fields optional - only provided fields are updated.
    """

    in_app_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    frequency: Optional[EmailFrequency] = None
    dnd_start: Optional[str] = None
    dnd_end: Optional[str] = None


class NotificationPreferenceUpdate(SQLModel):
    """Request model for updating notification preferences.

    All fields optional - only provided fields are updated.
    """

    in_app_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    frequency: Optional[EmailFrequency] = None
    dnd_start: Optional[str] = None
    dnd_end: Optional[str] = None


class NotificationPreferencePublic(SQLModel):
    """Response model for notification preference data.

    [From]: spec.md FR-033, contracts/api.yaml §4.1 Get Notification Settings
    """

    notification_type: NotificationType
    in_app_enabled: bool
    push_enabled: bool
    email_enabled: bool
    frequency: EmailFrequency
    dnd_start: Optional[str] = None
    dnd_end: Optional[str] = None
