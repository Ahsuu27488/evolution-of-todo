"""add_tool_role_to_messages

Revision ID: c4e4fac56184
Revises: add_conversation_deleted_at
Create Date: 2026-02-04 21:53:09.396774

Adds 'tool' role to messagerole enum for storing tool call results.
This enables the AI agent to maintain conversation context across requests
by remembering what happened with previous tool calls.

Per FR-005: Tool results for conversation context.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4e4fac56184'
down_revision: Union[str, Sequence[str], None] = 'add_conversation_deleted_at'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add 'tool' value to messagerole enum."""

    # Add 'tool' as a new value to the existing messagerole enum
    op.execute("ALTER TYPE messagerole ADD VALUE 'tool' AFTER 'system'")


def downgrade() -> None:
    """Downgrade schema - remove 'tool' value from messagerole enum.

    Note: PostgreSQL doesn't support removing enum values directly.
    We need to recreate the enum without the 'tool' value.
    """

    # Get the current database name to use the correct enum syntax
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT current_database()"))
    db_name = result.scalar()

    # 1. Create a new enum type without 'tool' value
    op.execute("""
        CREATE TYPE messagerole_old AS ENUM (
            'user',
            'assistant',
            'system'
        )
    """)

    # 2. Alter the column to use the old enum type
    op.execute("""
        ALTER TABLE messages
        ALTER COLUMN role TYPE messagerole_old
        USING role::text::messagerole_old
    """)

    # 3. Drop the old enum type
    op.execute("DROP TYPE messagerole")

    # 4. Rename the new enum back to the original name
    op.execute("ALTER TYPE messagerole_old RENAME TO messagerole")
