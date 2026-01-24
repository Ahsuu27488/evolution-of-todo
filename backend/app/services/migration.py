"""
Background Migration Service for Legacy User Names

[T042-T046] Service for migrating legacy single name field to first_name/last_name schema.

This module provides:
- Background migration job to copy legacy names to first_name
- Progress monitoring for migration tracking
- Zero-downtime migration support
- Rollback-safe operations

[From]: data-model.md §Migration Rollback Strategy
[From]: research.md §Research Area 2: Database Schema Migration Strategy
"""

import asyncio
import logging
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User

logger = logging.getLogger(__name__)


class MigrationService:
    """Service for handling user name migrations."""

    def __init__(self, batch_size: int = 100):
        """
        Initialize migration service.

        Args:
            batch_size: Number of users to migrate per batch (default: 100)
        """
        self.batch_size = batch_size

    async def get_migration_progress(
        self, session: AsyncSession
    ) -> dict[str, int | float]:
        """
        [T047] Get migration progress statistics.

        Args:
            session: Async database session

        Returns:
            Dictionary with total_users, migrated_users, and progress_percentage
        """
        # Count total users
        total_result = await session.execute(select(func.count(User.id)))
        total_users = total_result.scalar() or 0

        # Count migrated users (those with first_name populated)
        migrated_result = await session.execute(
            select(func.count(User.id)).where(User.first_name.is_not(None))
        )
        migrated_users = migrated_result.scalar() or 0

        # Calculate progress percentage
        progress_percentage = (
            (migrated_users / total_users * 100) if total_users > 0 else 0
        )

        return {
            "total_users": total_users,
            "migrated_users": migrated_users,
            "progress_percentage": round(progress_percentage, 2),
        }

    async def migrate_user_names(
        self,
        session: AsyncSession,
        dry_run: bool = False,
    ) -> dict[str, int | str]:
        """
        [T043-T046] Migrate legacy user names to first_name/last_name schema.

        Migration strategy:
        - Legacy 'name' value becomes 'first_name'
        - 'last_name' is set to NULL (per spec clarification)
        - Operates in batches to avoid long-running transactions
        - Resumable if interrupted

        Args:
            session: Async database session
            dry_run: If True, report changes without committing (default: False)

        Returns:
            Dictionary with migration results: migrated_count, remaining_count, status
        """
        # Query for users who haven't been migrated yet
        # (first_name is NULL but name has a value)
        statement = (
            select(User)
            .where(User.first_name.is_(None))
            .where(User.name.is_not(None))
            .limit(self.batch_size)
        )

        result = await session.execute(statement)
        users_to_migrate = result.scalars().all()

        if not users_to_migrate:
            logger.info("No users remaining to migrate")
            return {
                "migrated_count": 0,
                "remaining_count": 0,
                "status": "complete",
            }

        # Migrate each user
        migrated_count = 0
        for user in users_to_migrate:
            # [T046] Legacy name becomes first_name, last_name is NULL
            # This supports mononyms and follows spec clarification
            user.first_name = user.name
            user.last_name = None
            migrated_count += 1

            logger.info(f"Migrated user: {user.email} -> {user.first_name}")

        if not dry_run:
            # Commit the batch
            await session.commit()
            logger.info(f"Committed batch of {migrated_count} users")
        else:
            # Roll back for dry run
            await session.rollback()
            logger.info(f"Dry run: Would migrate {migrated_count} users")

        # Check remaining users
        remaining_result = await session.execute(
            select(func.count(User.id))
            .where(User.first_name.is_(None))
            .where(User.name.is_not(None))
        )
        remaining_count = remaining_result.scalar() or 0

        return {
            "migrated_count": migrated_count,
            "remaining_count": remaining_count,
            "status": "in_progress" if remaining_count > 0 else "complete",
        }

    async def verify_migration_integrity(
        self, session: AsyncSession
    ) -> dict[str, int | bool]:
        """
        [T048] Verify migration integrity and data consistency.

        Checks:
        - All users have either first_name or legacy name
        - No orphaned users (users without any name)
        - Migration progress is 100% complete

        Args:
            session: Async database session

        Returns:
            Dictionary with verification results
        """
        # Count users with first_name
        with_first_name_result = await session.execute(
            select(func.count(User.id)).where(User.first_name.is_not(None))
        )
        users_with_first_name = with_first_name_result.scalar() or 0

        # Count users with only legacy name (not migrated)
        with_legacy_only_result = await session.execute(
            select(func.count(User.id))
            .where(User.first_name.is_(None))
            .where(User.name.is_not(None))
        )
        users_with_legacy_only = with_legacy_only_result.scalar() or 0

        # Count total users
        total_result = await session.execute(select(func.count(User.id)))
        total_users = total_result.scalar() or 0

        # Count users without any name (data integrity issue)
        without_any_name_result = await session.execute(
            select(func.count(User.id))
            .where(User.first_name.is_(None))
            .where(User.name.is_(None))
        )
        users_without_any_name = without_any_name_result.scalar() or 0

        # Migration is complete if no users have legacy-only names
        is_complete = users_with_legacy_only == 0

        return {
            "total_users": total_users,
            "users_with_first_name": users_with_first_name,
            "users_with_legacy_only": users_with_legacy_only,
            "users_without_any_name": users_without_any_name,
            "migration_complete": is_complete,
            "data_integrity_ok": users_without_any_name == 0,
        }


# Singleton instance
migration_service = MigrationService()


async def run_migration_job(
    session: AsyncSession,
    dry_run: bool = False,
) -> dict[str, int | str]:
    """
    [T046] Execute background migration job.

    This function can be called:
    - Via CLI script for manual migration
    - Via scheduled task for gradual migration
    - Via admin endpoint for on-demand migration

    Args:
        session: Async database session
        dry_run: If True, report changes without committing

    Returns:
        Migration results dictionary

    Example:
        ```python
        # In a CLI script
        result = await run_migration_job(session, dry_run=False)
        print(f"Migrated {result['migrated_count']} users")
        ```
    """
    return await migration_service.migrate_user_names(session, dry_run)
