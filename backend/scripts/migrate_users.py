#!/usr/bin/env python3
"""
User Name Migration CLI Script

[T046] Command-line interface for running legacy user name migrations.

Usage:
    python backend/scripts/migrate_users.py           # Run migration
    python backend/scripts/migrate_users.py --dry-run  # Preview changes
    python backend/scripts/migrate_users.py --status   # Check progress

[From]: quickstart.md §Phase 4: Background Migration
"""

import argparse
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.db import async_session_maker
from app.services.migration import migration_service


async def run_migration(dry_run: bool = False) -> None:
    """
    Execute the migration process.

    Args:
        dry_run: If True, preview changes without committing
    """
    async with async_session_maker() as session:
        print("=" * 60)
        print("User Name Migration")
        print("=" * 60)

        # Get initial progress
        print("\n📊 Initial Migration Progress:")
        initial_progress = await migration_service.get_migration_progress(session)
        print(f"  Total users:      {initial_progress['total_users']}")
        print(f"  Migrated users:   {initial_progress['migrated_users']}")
        print(f"  Progress:         {initial_progress['progress_percentage']}%")

        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be committed")

        # Run migration
        print("\n🚀 Starting migration...")
        result = await migration_service.migrate_user_names(
            session, dry_run=dry_run
        )

        print(f"\n✅ Batch complete:")
        print(f"  Migrated:    {result['migrated_count']} users")
        print(f"  Remaining:   {result['remaining_count']} users")
        print(f"  Status:      {result['status']}")

        # Get final progress
        print("\n📊 Final Migration Progress:")
        final_progress = await migration_service.get_migration_progress(session)
        print(f"  Total users:      {final_progress['total_users']}")
        print(f"  Migrated users:   {final_progress['migrated_users']}")
        print(f"  Progress:         {final_progress['progress_percentage']}%")

        # Verify integrity
        print("\n🔍 Data Integrity Check:")
        verification = await migration_service.verify_migration_integrity(session)
        print(f"  Migration complete:  {verification['migration_complete']}")
        print(f"  Data integrity OK:   {verification['data_integrity_ok']}")
        print(f"  Users without name: {verification['users_without_any_name']}")

        if verification['users_without_any_name'] > 0:
            print("\n⚠️  WARNING: Some users have no name field populated!")

        print("\n" + "=" * 60)
        if dry_run:
            print("Dry run complete. No changes were committed.")
        else:
            print("Migration complete!")
        print("=" * 60)


async def show_status() -> None:
    """Show current migration status without running migration."""
    async with async_session_maker() as session:
        progress = await migration_service.get_migration_progress(session)
        verification = await migration_service.verify_migration_integrity(session)

        print("📊 Migration Status:")
        print(f"  Total users:      {progress['total_users']}")
        print(f"  Migrated users:   {progress['migrated_users']}")
        print(f"  Remaining:        {progress['total_users'] - progress['migrated_users']}")
        print(f"  Progress:         {progress['progress_percentage']}%")
        print(f"\n  Migration complete:  {verification['migration_complete']}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Migrate legacy user names to first_name/last_name schema"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without committing to database",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show migration status without running migration",
    )

    args = parser.parse_args()

    try:
        if args.status:
            asyncio.run(show_status())
        else:
            asyncio.run(run_migration(dry_run=args.dry_run))
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
