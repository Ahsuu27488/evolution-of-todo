"""add_ai_chatbot_tables

Revision ID: d7efc9f1d315
Revises: add_timezone_to_datetime_columns
Create Date: 2026-02-02 20:57:00.811938

Phase III AI Chatbot Tables:
- conversations: Chat sessions with message history
- messages: Individual messages with tool calls and correlation tracking
- agent_handoffs: Agent transfer audit trail
- conversation_preferences: User chat settings

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd7efc9f1d315'
down_revision: Union[str, Sequence[str], None] = 'add_timezone_to_datetime_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add AI chatbot tables."""

    # =========================================================================
    # conversations table
    # =========================================================================
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False, server_default='New Chat'),
        sa.Column('language_preference', sa.Enum('en', 'ur', 'auto', name='languagepreference'), nullable=False, server_default='auto'),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    # Create index for user conversation lookups
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])

    # =========================================================================
    # messages table
    # =========================================================================
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('correlation_id', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    )
    # Create indexes for conversation history and tracing
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_correlation_id', 'messages', ['correlation_id'])

    # =========================================================================
    # agent_handoffs table
    # =========================================================================
    op.create_table(
        'agent_handoffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_agent', sa.String(100), nullable=False),
        sa.Column('to_agent', sa.String(100), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('context_snapshot', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.String(1000), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    )
    # Create index for debugging by conversation
    op.create_index('ix_agent_handoffs_conversation_id', 'agent_handoffs', ['conversation_id'])

    # =========================================================================
    # conversation_preferences table
    # =========================================================================
    op.create_table(
        'conversation_preferences',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False, unique=True),
        sa.Column('language', sa.Enum('en', 'ur', 'auto', name='languagepreference'), nullable=False, server_default='auto'),
        sa.Column('voice_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('response_format', sa.String(20), nullable=False, server_default='text'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
    )
    # Create index for user preference lookups
    op.create_index('ix_conversation_preferences_user_id', 'conversation_preferences', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema - remove AI chatbot tables."""

    # Drop in reverse order of creation (foreign keys first)
    op.drop_index('ix_conversation_preferences_user_id', table_name='conversation_preferences')
    op.drop_table('conversation_preferences')

    op.drop_index('ix_agent_handoffs_conversation_id', table_name='agent_handoffs')
    op.drop_table('agent_handoffs')

    op.drop_index('ix_messages_correlation_id', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    op.drop_index('ix_conversations_updated_at', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS languagepreference')
    op.execute('DROP TYPE IF EXISTS messagerole')
