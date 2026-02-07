"""Update default timezone to Asia/Karachi

Revision ID: update_default_timezone_to_pkt
Revises: add_user_timezone
Create Date: 2026-02-07

This migration updates the default timezone for all users from UTC to
Asia/Karachi (PKT, UTC+5) for the Pakistan user base.

[Fix]: Default timezone changed to Asia/Karachi for all users
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'update_default_timezone_to_pkt'
down_revision: Union[str, Sequence[str], None] = 'add_user_timezone'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update default timezone to Asia/Karachi."""
    # Update all existing users to Asia/Karachi timezone
    op.execute("""
        UPDATE users
        SET timezone = 'Asia/Karachi'
        WHERE timezone = 'UTC'
    """)

    # Update the server default for new users
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN timezone
        SET DEFAULT 'Asia/Karachi'
    """)


def downgrade() -> None:
    """Revert default timezone to UTC."""
    # Revert all users back to UTC
    op.execute("""
        UPDATE users
        SET timezone = 'UTC'
        WHERE timezone = 'Asia/Karachi'
    """)

    # Revert the server default
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN timezone
        SET DEFAULT 'UTC'
    """)
