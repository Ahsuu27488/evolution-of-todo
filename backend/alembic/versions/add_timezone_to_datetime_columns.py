"""Add timezone support to datetime columns

Revision ID: add_timezone_to_datetime_columns
Revises: add_user_timezone
Create Date: 2026-02-01 00:00:00.000000

This migration alters datetime columns to use TIMESTAMP WITH TIME ZONE
to support proper timezone-aware comparisons in the scheduler.

Changes:
- tasks.due_date: TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
- tasks.created_at: TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
- task_logs.created_at: TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
- notifications.created_at: TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
- notifications.deleted_at: TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
- push_subscriptions.created_at: TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
- push_subscriptions.last_used_at: TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
- email_delivery_logs sent_at/delivered_at/opened_at/clicked_at: → TIMESTAMP WITH TIME ZONE

[Fix]: Resolves "can't subtract offset-naive and offset-aware datetimes" error
in daily digest scheduler when comparing timezone-aware datetimes with naive DB columns.

From: backend.log line 281-465
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_timezone_to_datetime_columns'
down_revision: Union[str, Sequence[str], None] = 'populate_notif_prefs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert datetime columns to TIMESTAMP WITH TIME ZONE."""

    # Tasks table
    op.alter_column(
        'tasks',
        'due_date',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=True,
    )

    op.alter_column(
        'tasks',
        'created_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    # Task logs table
    op.alter_column(
        'task_logs',
        'created_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    # Notifications table
    op.alter_column(
        'notifications',
        'created_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.alter_column(
        'notifications',
        'deleted_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=True,
    )

    # Push subscriptions table
    op.alter_column(
        'push_subscriptions',
        'created_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.alter_column(
        'push_subscriptions',
        'last_used_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    # Notification preferences table (created_at only)
    op.alter_column(
        'notification_preferences',
        'created_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    # Email delivery logs table
    op.alter_column(
        'email_delivery_logs',
        'sent_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.alter_column(
        'email_delivery_logs',
        'delivered_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=True,
    )

    op.alter_column(
        'email_delivery_logs',
        'opened_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=True,
    )

    op.alter_column(
        'email_delivery_logs',
        'clicked_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        nullable=True,
    )


def downgrade() -> None:
    """Revert to TIMESTAMP WITHOUT TIME ZONE."""

    # Tasks table
    op.alter_column(
        'tasks',
        'due_date',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=True,
    )

    op.alter_column(
        'tasks',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=False,
    )

    # Task logs table
    op.alter_column(
        'task_logs',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=False,
    )

    # Notifications table
    op.alter_column(
        'notifications',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=False,
    )

    op.alter_column(
        'notifications',
        'deleted_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=True,
    )

    # Push subscriptions table
    op.alter_column(
        'push_subscriptions',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=False,
    )

    op.alter_column(
        'push_subscriptions',
        'last_used_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=False,
    )

    # Notification preferences table
    op.alter_column(
        'notification_preferences',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=False,
    )

    # Email delivery logs table
    op.alter_column(
        'email_delivery_logs',
        'sent_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=False,
    )

    op.alter_column(
        'email_delivery_logs',
        'delivered_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=True,
    )

    op.alter_column(
        'email_delivery_logs',
        'opened_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=True,
    )

    op.alter_column(
        'email_delivery_logs',
        'clicked_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        nullable=True,
    )
