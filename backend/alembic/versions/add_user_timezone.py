"""Add user timezone for scheduled notifications

Revision ID: add_user_timezone
Revises: 84a9c58f10fa
Create Date: 2026-01-28 00:00:00.000000

This migration adds a timezone field to the users table to support
user-specific scheduling for digest emails. The timezone field stores
IANA timezone identifiers (e.g., 'America/New_York', 'Europe/London').

[Fix]: Scheduled digests now respect user's local timezone
[From]: notification timing analysis - server timezone issue
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_user_timezone'
down_revision: Union[str, Sequence[str], None] = 'add_resend_email_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add timezone column to users table."""
    # Add timezone column with default UTC for existing users
    op.add_column(
        'users',
        sa.Column(
            'timezone',
            sa.String(50),
            nullable=True,
            server_default='UTC',
            comment='User timezone for scheduled notifications (IANA format)',
        )
    )

    # Update existing users to have UTC as default
    op.execute("""
        UPDATE users
        SET timezone = 'UTC'
        WHERE timezone IS NULL
    """)

    # Set the column to non-nullable with default
    op.alter_column(
        'users',
        'timezone',
        nullable=False,
        server_default='UTC'
    )


def downgrade() -> None:
    """Remove timezone column from users table."""
    op.drop_column('users', 'timezone')
