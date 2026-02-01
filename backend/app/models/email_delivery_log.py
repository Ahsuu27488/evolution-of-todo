"""EmailDeliveryLog model for tracking email delivery status.

[Task]: T009
[From]: spec.md FR-025, FR-034, research.md Resend webhook section
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Literal

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field as SQLField


class EmailDeliveryStatus(str, Enum):
    """Email delivery status enum.

    [From]: data-model.md §Entity Definitions - EmailDeliveryLog
    """

    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"


class EmailDeliveryLog(SQLModel, table=True):
    """Email delivery tracking for bounce handling and analytics.

    [Task]: T009
    [From]: spec.md FR-025, FR-034, research.md Resend webhook section
    [From]: data-model.md §Entity Definitions - EmailDeliveryLog

    Tracks the delivery status of emails sent through Resend.
    Used for bounce detection (per FR-025) and analytics.

    Attributes:
        id: Primary key
        notification_id: FK to notifications table
        email: Recipient email address
        status: Current delivery status
        sent_at: When email was sent
        delivered_at: When email was delivered
        opened_at: When email was opened
        clicked_at: When link in email was clicked
        error_message: Error details for bounced emails
        error_code: Error code for bounced emails
    """

    __tablename__ = "email_delivery_logs"

    id: Optional[int] = SQLField(default=None, primary_key=True)
    notification_id: int = SQLField(
        foreign_key="notifications.id",
        index=True,
        description="Related notification ID",
    )

    # Resend email ID for webhook matching
    resend_email_id: Optional[str] = SQLField(
        default=None,
        index=True,
        max_length=255,
        description="Resend API email ID for webhook matching",
    )

    # Recipient
    email: str = SQLField(
        index=True,
        description="Recipient email address",
    )

    # Delivery status (from Resend webhook)
    status: EmailDeliveryStatus = SQLField(
        default=EmailDeliveryStatus.SENT,
        index=True,
        description="Current delivery status",
    )

    # Tracking timestamps (all timezone-aware)
    sent_at: datetime = SQLField(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
        description="When email was sent (timezone-aware)",
    )
    delivered_at: Optional[datetime] = SQLField(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="When email was delivered (timezone-aware)",
    )
    opened_at: Optional[datetime] = SQLField(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="When email was opened (timezone-aware)",
    )
    clicked_at: Optional[datetime] = SQLField(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="When link in email was clicked (timezone-aware)",
    )

    # Error details (for bounced emails)
    error_message: Optional[str] = SQLField(
        default=None,
        max_length=500,
        description="Error message for bounced emails",
    )
    error_code: Optional[str] = SQLField(
        default=None,
        max_length=50,
        description="Error code for bounced emails",
    )
