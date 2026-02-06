"""fix_task_logs_cascade_delete

Revision ID: fix_task_logs_cascade_delete
Revises: c4e4fac56184
Create Date: 2026-02-06 16:30:00.000000

Fixes task_logs foreign key constraint to use ON DELETE CASCADE.
This prevents SQLAlchemy from trying to NULL out task_id before
deleting tasks, which was causing "null value in column task_id violates
not-null constraint" errors.

The issue occurred when:
1. Agent deleted tasks (via MCP tools)
2. Conversation save failed later
3. Transaction rollback attempted to restore state
4. SQLAlchemy tried to set task_logs.task_id = NULL
5. Database rejected it (NOT NULL constraint)

Root cause: SQLAlchemy's default cascade behavior tries to update
foreign keys to NULL before deleting the parent row.

Fix: Add ON DELETE CASCADE at database level so PostgreSQL
automatically deletes task_logs when tasks are deleted.

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_task_logs_cascade_delete'
down_revision: Union[str, Sequence[str], None] = 'c4e4fac56184'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - fix task_logs foreign key with CASCADE."""

    # Get the current foreign key constraint name
    # PostgreSQL typically names it: task_logs_task_id_fkey
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT conname
        FROM pg_constraint
        WHERE conrelid = 'task_logs'::regclass
        AND confrelid = 'tasks'::regclass
        AND contype = 'f'
    """))
    fk_name = result.scalar()

    if fk_name:
        # Drop the existing foreign key constraint
        op.execute(f"ALTER TABLE task_logs DROP CONSTRAINT {fk_name}")

        # Re-create with ON DELETE CASCADE
        op.execute("""
            ALTER TABLE task_logs
            ADD CONSTRAINT task_logs_task_id_fkey
            FOREIGN KEY (task_id) REFERENCES tasks(id)
            ON DELETE CASCADE
        """)


def downgrade() -> None:
    """Downgrade schema - restore original foreign key without CASCADE."""

    # Drop the CASCADE foreign key
    op.execute("ALTER TABLE task_logs DROP CONSTRAINT task_logs_task_id_fkey")

    # Re-create without ON DELETE CASCADE (default behavior)
    op.execute("""
        ALTER TABLE task_logs
        ADD CONSTRAINT task_logs_task_id_fkey
        FOREIGN KEY (task_id) REFERENCES tasks(id)
    """)
