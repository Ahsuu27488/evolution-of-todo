"""All models for Chronos Todo App.

[Task]: T005-T011
[From]: spec.md §Key Entities, plan.md §Data Model, data-model.md

This package exports all database models:
- Core models: Task, TaskLog, User, Tag (from app/models/core.py)
- Notification models: Notification, NotificationPreference, etc.
"""

# Core models live in app/models/core.py (formerly app/models.py, which this
# package used to shadow and load through importlib).
from app.models.core import (
    Task,
    TaskLog,
    User,
    Tag,
    Priority,
    RecurrencePattern,
    Action,
    # Request/Response models
    TaskCreate,
    TaskUpdate,
    TaskPublic,
    TaskList,
    TaskLogPublic,
    UserPublic,
    UserCreate,
    UserLogin,
    UserUpdate,
    LoginResponse,
)

# Export all notification models from package modules
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationPreference,
    NotificationPublic,
    NotificationList,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationPreferencePublic,
)
from app.models.push_subscription import (
    PushSubscription,
    PushSubscriptionCreate,
)
from app.models.email_delivery_log import (
    EmailDeliveryLog,
    EmailDeliveryStatus,
)

__all__ = [
    # Core models from core.py
    "Task",
    "TaskLog",
    "User",
    "Tag",
    "Priority",
    "RecurrencePattern",
    "Action",
    "TaskCreate",
    "TaskUpdate",
    "TaskPublic",
    "TaskList",
    "TaskLogPublic",
    "UserPublic",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "LoginResponse",
    # Notification models
    "Notification",
    "NotificationType",
    "NotificationPreference",
    "NotificationPublic",
    "NotificationList",
    "NotificationPreferenceCreate",
    "NotificationPreferenceUpdate",
    "NotificationPreferencePublic",
    # Push subscription models
    "PushSubscription",
    "PushSubscriptionCreate",
    # Email delivery models
    "EmailDeliveryLog",
    "EmailDeliveryStatus",
]
