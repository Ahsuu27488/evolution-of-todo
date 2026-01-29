"""Add resend_email_id to email_delivery_logs

Revision ID: add_resend_email_id
Revises: 84a9c58f10fa
Create Date: 2026-01-28 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_resend_email_id'
down_revision: Union[str, Sequence[str], None] = '84a9c58f10fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add resend_email_id column to email_delivery_logs table."""
    # Add the resend_email_id column
    op.add_column(
        'email_delivery_logs',
        sa.Column('resend_email_id', sa.String(length=255), nullable=True)
    )
    # Create index on resend_email_id for faster webhook matching
    op.create_index(
        'ix_email_delivery_logs_resend_email_id',
        'email_delivery_logs',
        ['resend_email_id']
    )


def downgrade() -> None:
    """Remove resend_email_id column from email_delivery_logs table."""
    op.drop_index('ix_email_delivery_logs_resend_email_id', table_name='email_delivery_logs')
    op.drop_column('email_delivery_logs', 'resend_email_id')
