"""PushSubscription model for browser push notifications.

[Task]: T008
[From]: spec.md FR-018, research.md Web Push section, data-model.md §Entity Definitions - PushSubscription
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field as SQLField


class PushSubscription(SQLModel, table=True):
    """Browser push subscription with VAPID authentication details.

    [Task]: T008
    [From]: spec.md FR-018, research.md Web Push section
    [From]: data-model.md §Entity Definitions - PushSubscription

    Stores the PushSubscription JSON from the browser's PushManager
    along with device metadata for multi-device support.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        subscription: Full subscription JSON (endpoint + keys)
        device_info: Device metadata (user agent, platform, last active)
        created_at: When subscription was created
        last_used_at: When subscription was last used for push
        is_valid: Whether subscription is still valid (410/404 = invalid)
    """

    __tablename__ = "push_subscriptions"

    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: str = SQLField(
        foreign_key="users.id",
        index=True,
        description="Owner user ID from Better Auth",
    )

    # Full subscription object from Push API (endpoint + keys)
    # Schema per Web Push API:
    # {
    #   "endpoint": "https://fcm.googleapis.com/fcm/send/...",
    #   "keys": {
    #     "p256dh": "Base64-encoded public key",
    #     "auth": "Base64-encoded auth secret"
    #   }
    # }
    subscription: dict[str, Any] = SQLField(
        sa_column=Column(JSONB, nullable=False),
        description="Full PushSubscription JSON from browser",
    )

    # Device metadata for management
    device_info: dict[str, Any] = SQLField(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="User agent, platform, last active timestamp",
    )

    # Lifecycle tracking
    created_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="When subscription was created",
    )
    last_used_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        description="When subscription was last used successfully",
    )
    is_valid: bool = SQLField(
        default=True,
        index=True,
        description="Whether subscription is still valid (false on 410/404)",
    )


# =============================================================================
# Pydantic Schemas for Request/Response
# =============================================================================


class PushSubscriptionCreate(BaseModel):
    """Request model for creating a push subscription.

    [From]: contracts/api.yaml §2.1 Subscribe to Push

    This receives the PushSubscription JSON from the browser's
    PushManager.subscribe() call.
    """

    subscription: dict[str, Any] = Field(
        ...,
        description="PushSubscription JSON from browser",
    )
    device_info: dict[str, Any] = Field(
        default_factory=dict,
        description="Device metadata (user agent, platform)",
    )

    @field_validator("subscription")
    @classmethod
    def validate_subscription(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate subscription has required fields.

        Per Web Push API spec, subscription must have:
        - endpoint: URL string
        - keys: object with p256dh and auth
        """
        if "endpoint" not in v:
            raise ValueError("Subscription must include 'endpoint'")
        if not isinstance(v.get("keys"), dict):
            raise ValueError("Subscription must include 'keys' object")
        keys = v["keys"]
        if "p256dh" not in keys or "auth" not in keys:
            raise ValueError("Subscription keys must include 'p256dh' and 'auth'")
        return v


class PushSubscriptionPublic(SQLModel):
    """Response model for push subscription data."""

    id: int
    user_id: str
    device_info: dict[str, Any]
    created_at: datetime
    last_used_at: datetime
    is_valid: bool
