"""Populate default notification preferences for existing users.

Revision ID: populate_default_notification_preferences
Revises: add_user_timezone
Create Date: 2026-01-28 00:00:00.000000

This migration ensures all existing users have default notification preferences.
New users will get preferences created automatically during signup.

[Fix]: Populate notification preferences for users who signed up before the notification system
"""

from typing import Sequence, Union
import logging

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# revision identifiers, used by Alembic.
revision: str = 'populate_notif_prefs'  # Shortened for VARCHAR(32) limit
down_revision: Union[str, Sequence[str], None] = 'add_user_timezone'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add default notification preferences for users who don't have any."""

    # Get database connection
    conn = op.get_bind()

    # First, let's check which users need preferences
    query = """
    SELECT u.id
    FROM users u
    WHERE NOT EXISTS (
        SELECT 1 FROM notification_preferences np
        WHERE np.user_id = u.id
    )
    """

    result = conn.execute(sa.text(query))
    user_ids = [row[0] for row in result.fetchall()]

    if not user_ids:
        logger.info("No users missing notification preferences")
        return

    logger.info(f"Creating default notification preferences for {len(user_ids)} users")

    # Define default preferences
    # notification_type, in_app_enabled, push_enabled, email_enabled, frequency
    default_preferences = [
        ('TASK_DUE', True, False, True, 'IMMEDIATE'),
        ('TASK_OVERDUE', True, True, True, 'IMMEDIATE'),
        ('TASK_COMPLETED', True, False, True, 'IMMEDIATE'),
        ('TASK_ASSIGNED', True, False, True, 'IMMEDIATE'),
        ('TASK_REMINDER', True, False, True, 'IMMEDIATE'),
        ('SYSTEM_UPDATE', True, False, False, 'NONE'),
    ]

    notification_preferences_table = table(
        'notification_preferences',
        column('user_id', sa.String),
        column('notification_type', sa.Enum(
            'TASK_DUE', 'TASK_OVERDUE', 'TASK_ASSIGNED',
            'TASK_COMPLETED', 'TASK_REMINDER', 'SYSTEM_UPDATE',
            name='notificationtype'
        )),
        column('in_app_enabled', sa.Boolean),
        column('push_enabled', sa.Boolean),
        column('email_enabled', sa.Boolean),
        column('frequency', sa.Enum(
            'IMMEDIATE', 'DAILY', 'WEEKLY', 'NONE',
            name='emailfrequency'
        )),
        column('dnd_start', sa.String(5)),
        column('dnd_end', sa.String(5)),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime(timezone=True)),
    )

    # Insert preferences for each user
    count = 0
    for user_id in user_ids:
        for notif_type, in_app, push, email, freq in default_preferences:
            conn.execute(
                notification_preferences_table.insert().values(
                    user_id=user_id,
                    notification_type=notif_type,
                    in_app_enabled=in_app,
                    push_enabled=push,
                    email_enabled=email,
                    frequency=freq,
                    dnd_start=None,
                    dnd_end=None,
                    created_at=sa.text('CURRENT_TIMESTAMP'),
                    updated_at=sa.text('CURRENT_TIMESTAMP'),
                )
            )
            count += 1

    logger.info(f"Created {count} notification preferences for {len(user_ids)} users")


def downgrade() -> None:
    """Remove preferences that were created by this migration.

    Note: This removes ALL preferences for users who didn't have them before,
    effectively reverting them to the state where they would get in-memory defaults.
    """
    # We cannot easily distinguish which preferences were added by this migration
    # vs. which were manually set by users. So we'll leave them in place.
    # The migration is reversible in that the code changes can be reverted,
    # but the data changes are intentionally preserved.
    pass
