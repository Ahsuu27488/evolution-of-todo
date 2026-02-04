"""Add deleted_at column to conversations for soft delete (T120).

Revision ID: add_conversation_deleted_at
Revises: d7efc9f1d315
Create Date: 2025-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_conversation_deleted_at'
down_revision = 'd7efc9f1d315'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add deleted_at column to conversations table for 90-day archive."""
    # Add deleted_at column with index for efficient querying
    op.add_column(
        'conversations',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index(
        'ix_conversations_deleted_at',
        'conversations',
        ['deleted_at']
    )


def downgrade() -> None:
    """Remove deleted_at column from conversations table."""
    op.drop_index('ix_conversations_deleted_at', table_name='conversations')
    op.drop_column('conversations', 'deleted_at')
