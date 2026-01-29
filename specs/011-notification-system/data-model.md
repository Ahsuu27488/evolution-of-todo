# Data Model: Notification System

**Feature**: 011-notification-system
**Date**: 2026-01-27
**Source**: spec.md §Key Entities

## Entity Relationship Diagram

```
┌─────────────────────┐         ┌──────────────────────┐
│   notifications      │         │ notification_prefs  │
├─────────────────────┤         ├──────────────────────┤
│ id (PK)             │◄────────┤ id (PK)              │
│ user_id (FK)        │         │ user_id (FK)         │
│ type                │         │ notification_type   │
│ title               │         │ in_app_enabled      │
│ message             │         │ push_enabled        │
│ data (JSONB)        │         │ email_enabled       │
│ read_status         │         │ frequency           │
│ created_at          │         │ dnd_start           │
│ sent_channels       │         │ dnd_end             │
│ related_task_id (FK)│         └──────────────────────┘
└─────────────────────┘
           │
           │
           ▼
┌─────────────────────┐         ┌──────────────────────┐
│ push_subscriptions  │         │ email_delivery_logs  │
├─────────────────────┤         ├──────────────────────┤
│ id (PK)             │         │ id (PK)              │
│ user_id (FK)        │         │ notification_id (FK) │
│ subscription (JSONB)│         │ email               │
│ device_info (JSONB) │         │ status              │
│ created_at          │         │ sent_at             │
│ last_used_at        │         │ delivered_at        │
└─────────────────────┘         │ opened_at           │
                                  │ clicked_at          │
                                  └──────────────────────┘
```

---

## Entity Definitions

### 1. Notification

**Purpose**: Store all notification events for users with delivery tracking.

**From**: spec.md FR-004, FR-009, FR-035

```python
# [Task]: T-XXX
# [From]: spec.md §Key Entities, plan.md §Data Model
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification types per FR-004"""
    TASK_DUE = "task_due"
    TASK_OVERDUE = "task_overdue"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_REMINDER = "task_reminder"
    SYSTEM_UPDATE = "system_update"


class Notification(SQLModel, table=True):
    """Core notification entity with read status and delivery tracking."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)

    # Notification content
    type: NotificationType = Field(index=True)
    title: str
    message: str
    data: dict = Field(sa_type=JSON, default={})

    # Related entity (e.g., task that triggered notification)
    related_task_id: Optional[int] = Field(foreign_key="task.id", index=True)

    # State tracking
    read_status: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_channels: list[str] = Field(sa_type=JSON, default=[])  # ["in_app", "push", "email"]

    # Soft delete support (per spec edge case)
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="notifications")
    related_task: Optional["Task"] = Relationship(back_populates="notifications")

    class Config:
        indexes = [
            ("user_id", "created_at", "deleted_at"),  # For active notifications query
            ("read_status", "created_at"),             # For unread count
        ]
```

**Validation Rules**:
- `type` must be one of `NotificationType` enum values
- `read_status` defaults to `False`
- `sent_channels` tracks which channels the notification was delivered to

**State Transitions**:
```
created (read=False) → read (read=True) → archived (deleted_at set)
```

---

### 2. NotificationPreference

**Purpose**: Store user notification preferences per channel and type.

**From**: spec.md FR-032, FR-036, Assumptions & Decisions

```python
class NotificationPreference(SQLModel, table=True):
    """Per-user notification settings with channel and frequency controls."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")

    # Notification type this preference applies to
    notification_type: NotificationType

    # Channel enablement
    in_app_enabled: bool = Field(default=True)
    push_enabled: bool = Field(default=False)   # Opt-in required
    email_enabled: bool = Field(default=False)  # Opt-in required

    # Frequency for email (immediate, daily, weekly per FR-022)
    frequency: str = Field(default="immediate")  # "immediate" | "daily" | "weekly"

    # Do Not Disturb hours (per FR-036)
    dnd_start: Optional[str] = Field(default=None)   # HH:MM format
    dnd_end: Optional[str] = Field(default=None)     # HH:MM format

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="notification_preferences")

    class Config:
        unique_constraints = [("user_id", "notification_type")]
```

**Validation Rules**:
- `dnd_start` < `dnd_end` when both set (e.g., 22:00 < 08:00 for overnight)
- `frequency` must be `"immediate"`, `"daily"`, or `"weekly"`
- If `push_enabled=False`, push notifications are not sent (respect permission status)

**Defaults**:
- `in_app_enabled=True` (always on, cannot be disabled)
- `push_enabled=False` (requires opt-in per FR-012)
- `email_enabled=False` (requires opt-in per FR-026)

---

### 3. PushSubscription

**Purpose**: Store browser push subscriptions for multi-device support.

**From**: spec.md FR-018, research.md Web Push section

```python
class PushSubscription(SQLModel, table=True):
    """Browser push subscription with VAPID authentication details."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)

    # Full subscription object from Push API (endpoint + keys)
    subscription: dict = Field(sa_type=JSON)

    # Device metadata for management
    device_info: dict = Field(
        sa_type=JSON,
        default={},
        description="User agent, platform, last active timestamp"
    )

    # Lifecycle tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)
    is_valid: bool = Field(default=True, index=True)

    # Relationships
    user: "User" = Relationship(back_populates="push_subscriptions")

    class Config:
        indexes = [
            ("user_id", "is_valid"),  # Get active subscriptions
        ]
```

**Schema** (from Web Push documentation):
```json
{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "Base64-encoded public key",
    "auth": "Base64-encoded auth secret"
  }
}
```

**State Transitions**:
```
created (is_valid=True) → invalidated (is_valid=False, 410/404 from push service)
```

---

### 4. EmailDeliveryLog

**Purpose**: Track email delivery status for bounce handling per FR-025.

**From**: spec.md FR-034, research.md Resend webhook section

```python
class EmailDeliveryStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"


class EmailDeliveryLog(SQLModel, table=True):
    """Email delivery tracking for bounce handling and analytics."""

    id: Optional[int] = Field(default=None, primary_key=True)
    notification_id: int = Field(foreign_key="notification.id", index=True)

    # Recipient
    email: str = Field(index=True)

    # Delivery status (from Resend webhook)
    status: EmailDeliveryStatus = Field(default=EmailDeliveryStatus.SENT, index=True)

    # Tracking timestamps
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = Field(default=None)
    opened_at: Optional[datetime] = Field(default=None)
    clicked_at: Optional[datetime] = Field(default=None)

    # Error details (for bounced emails)
    error_message: Optional[str] = Field(default=None)
    error_code: Optional[str] = Field(default=None)

    # Relationships
    notification: Notification = Relationship(back_populates="email_logs")

    class Config:
        indexes = [
            ("email", "status"),  # Find bounced emails per user
        ]
```

**Webhook Events** (from Resend documentation):
- `email.sent`: Initial send
- `email.delivered: Successfully delivered
- `email.bounced`: Bounced (disable email for user per FR-025)
- `email.opened`: User opened email
- `email.clicked`: User clicked link

---

## Existing Entity Extensions

### User Model Extension

```python
class User(SQLModel, table=True):
    # ... existing fields ...

    # New relationships for notifications
    notifications: list["Notification"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"order_by": "desc(Notification.created_at)"}
    )
    notification_preferences: list["NotificationPreference"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade_delete": True}
    )
    push_subscriptions: list["PushSubscription"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade_delete": True}
    )
```

### Task Model Extension

```python
class Task(SQLModel, table=True):
    # ... existing fields ...

    # New relationship for notifications
    notifications: list["Notification"] = Relationship(
        back_populates="related_task"
    )
```

---

## Database Indexes

| Table | Index | Purpose |
|-------|-------|---------|
| `notifications` | `(user_id, created_at DESC, deleted_at)` | Active notifications query (FR-009) |
| `notifications` | `(read_status, created_at)` | Unread count query (FR-001) |
| `notifications` | `(related_task_id)` | Task-based lookup |
| `notification_preferences` | `(user_id, notification_type)` UNIQUE | Per-type preferences |
| `push_subscriptions` | `(user_id, is_valid)` | Active subscriptions |
| `email_delivery_logs` | `(email, status)` | Bounce detection (FR-025) |

---

## Data Retention

**From**: spec.md FR-035, Assumptions & Decisions

| Policy | Duration | Action |
|--------|----------|--------|
| Active notifications | 30 days | Queryable in UI |
| Archived notifications | After 30 days | `deleted_at` set, excluded from queries |
| Email logs | 90 days | For analytics and debugging |
| Push subscriptions | Until invalidated | Clean up when `is_valid=False` |

---

## Migration Notes

1. **Existing tables**: `users`, `tasks` already exist in Phase II schema
2. **New tables**: 4 new tables for notification system
3. **Foreign keys**: All use existing `user.id` and `task.id` references
4. **JSONB columns**: Used for `data`, `subscription`, `sent_channels` (PostgreSQL)
5. **Cascade deletes**: Configured for relationships with multi-deletion risk
