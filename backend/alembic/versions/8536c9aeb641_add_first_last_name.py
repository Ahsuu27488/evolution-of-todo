"""add_first_last_name

[T008] Alembic migration to add first_name and last_name columns to users table.
Migration Rollback Strategy per data-model.md §Migration Rollback Strategy

Revision ID: 8536c9aeb641
Revises:
Create Date: 2026-01-24 23:19:45.633213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8536c9aeb641'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add first_name and last_name columns.

    Strategy:
    - Add nullable columns (backward compatible)
    - Legacy 'name' column remains for existing code
    - Future migration will populate first_name from legacy name
    """
    # Add first_name column (nullable for backward compatibility)
    op.add_column(
        'users',
        sa.Column('first_name', sa.String(length=50), nullable=True)
    )

    # Add last_name column (nullable for backward compatibility)
    op.add_column(
        'users',
        sa.Column('last_name', sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema: Remove first_name and last_name columns.

    Rollback strategy:
    - Safe to remove new columns if migration hasn't run yet
    - If migration has run, data will be lost (acceptable rollback)
    """
    # Remove last_name column
    op.drop_column('users', 'last_name')

    # Remove first_name column
    op.drop_column('users', 'first_name')
