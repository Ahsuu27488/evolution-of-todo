"""All models for Chronos Todo App.

[Task]: T005-T011
[From]: spec.md §Key Entities, plan.md §Data Model, data-model.md

This package exports all database models:
- Core models: Task, TaskLog, User, Tag (from app/models.py)
- Notification models: Notification, NotificationPreference, etc.
"""

# Import and re-export core models from models.py file
# We use importlib to import the file directly, avoiding the package shadow
import importlib.util
import sys
from pathlib import Path

# Get the path to models.py (sibling to this models/ package directory)
# models.py is at app/models.py, this file is at app/models/__init__.py
models_path = Path(__file__).parent.parent / "models.py"

# Load models.py as a module
spec = importlib.util.spec_from_file_location("app_models_core", models_path)
if spec and spec.loader:
    core_models = importlib.util.module_from_spec(spec)
    sys.modules["app_models_core"] = core_models
    spec.loader.exec_module(core_models)

    # Re-export all core models
    Task = core_models.Task
    TaskLog = core_models.TaskLog
    User = core_models.User
    Tag = core_models.Tag
    Priority = core_models.Priority
    RecurrencePattern = core_models.RecurrencePattern
    Action = core_models.Action

    # Request/Response models
    TaskCreate = core_models.TaskCreate
    TaskUpdate = core_models.TaskUpdate
    TaskPublic = core_models.TaskPublic
    TaskList = core_models.TaskList
    TaskLogPublic = core_models.TaskLogPublic
    UserPublic = core_models.UserPublic
    UserCreate = core_models.UserCreate
    UserLogin = core_models.UserLogin
    UserUpdate = core_models.UserUpdate
    LoginResponse = core_models.LoginResponse
else:
    raise ImportError(f"Could not load core models from {models_path}")

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
    # Core models from models.py
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
