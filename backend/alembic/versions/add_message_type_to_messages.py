"""Add message_type column to messages for voice/text distinction

Revision ID: add_message_type
Revises: c4e4fac56184
Create Date: 2026-02-07

This migration adds a message_type column to the messages table to distinguish
between voice messages (transcribed from audio) and regular text messages.
This enables the frontend to display voice messages with a mic icon instead
of showing the transcribed text.

Per FR-061: Voice input with visual indicator.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_message_type_to_messages'
down_revision: Union[str, Sequence[str], None] = 'c4e4fac56184'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add message_type column to messages table."""

    # Create the messagetype enum
    op.execute("""
        CREATE TYPE messagetype AS ENUM (
            'text',
            'voice'
        )
    """)

    # Add the message_type column with a default value
    # Using nullable=False with server_default='text' ensures existing rows get 'text'
    op.add_column(
        'messages',
        sa.Column(
            'message_type',
            sa.Enum('text', 'voice', name='messagetype', create_type=False),
            nullable=False,
            server_default='text'
        )
    )


def downgrade() -> None:
    """Remove message_type column from messages table."""

    # Drop the message_type column
    op.drop_column('messages', 'message_type')

    # Drop the messagetype enum
    op.execute("DROP TYPE messagetype")
