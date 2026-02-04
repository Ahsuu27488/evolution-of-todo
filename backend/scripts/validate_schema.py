#!/usr/bin/env python3
"""
Database schema validation script for Phase III AI Chatbot.

Validates that all required tables, columns, and indexes exist.
Run with: python scripts/validate_schema.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import async_session_maker


# Required tables for Phase III
REQUIRED_TABLES = [
    # Phase II tables
    "users",
    "tasks",
    "tags",
    "task_logs",
    "notifications",
    "email_delivery_logs",
    "notification_preferences",
    # Phase III tables
    "conversations",
    "messages",
    "agent_handoffs",
    "conversation_preferences",
]


# Required columns for Phase III tables
REQUIRED_COLUMNS = {
    "conversations": [
        "id",
        "user_id",
        "title",
        "language_preference",
        "message_count",
        "created_at",
        "updated_at",
        "deleted_at",  # T120: Soft delete column
    ],
    "messages": [
        "id",
        "conversation_id",
        "correlation_id",
        "role",
        "content",
        "tool_calls",
        "created_at",
    ],
    "agent_handoffs": [
        "id",
        "conversation_id",
        "from_agent",
        "to_agent",
        "reason",
        "context_snapshot",
        "timestamp",
        "success",
        "error_message",
    ],
}


# Required indexes for Phase III tables
REQUIRED_INDEXES = [
    "ix_conversations_user_id",
    "ix_conversations_updated_at",
    "ix_conversations_deleted_at",  # T120
    "ix_messages_conversation_id",
    "ix_messages_correlation_id",
    "ix_agent_handoffs_conversation_id",
]


async def validate_tables() -> list[str]:
    """Check that all required tables exist."""
    errors = []

    async with async_session_maker() as session:
        result = await session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        existing_tables = {row[0] for row in result}

        for table in REQUIRED_TABLES:
            if table not in existing_tables:
                errors.append(f"Missing table: {table}")

    return errors


async def validate_columns() -> list[str]:
    """Check that all required columns exist."""
    errors = []

    async with async_session_maker() as session:
        for table, columns in REQUIRED_COLUMNS.items():
            result = await session.execute(text(
                f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = '{table}'
                """
            ))
            existing_columns = {row[0] for row in result}

            for column in columns:
                if column not in existing_columns:
                    errors.append(f"Missing column: {table}.{column}")

    return errors


async def validate_indexes() -> list[str]:
    """Check that all required indexes exist."""
    errors = []

    async with async_session_maker() as session:
        result = await session.execute(text(
            "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
        ))
        existing_indexes = {row[0] for row in result}

        for index in REQUIRED_INDEXES:
            if index not in existing_indexes:
                errors.append(f"Missing index: {index}")

    return errors


async def main():
    """Run all validations."""
    print("=" * 60)
    print("Phase III AI Chatbot - Database Schema Validation")
    print("=" * 60)
    print()

    all_errors = []

    # Validate tables
    print("Validating tables...")
    table_errors = await validate_tables()
    all_errors.extend(table_errors)
    if table_errors:
        print(f"  ❌ {len(table_errors)} issues found")
        for error in table_errors:
            print(f"     - {error}")
    else:
        print(f"  ✅ All {len(REQUIRED_TABLES)} required tables present")

    print()

    # Validate columns
    print("Validating columns...")
    column_errors = await validate_columns()
    all_errors.extend(column_errors)
    if column_errors:
        print(f"  ❌ {len(column_errors)} issues found")
        for error in column_errors:
            print(f"     - {error}")
    else:
        total_columns = sum(len(cols) for cols in REQUIRED_COLUMNS.values())
        print(f"  ✅ All {total_columns} required columns present")

    print()

    # Validate indexes
    print("Validating indexes...")
    index_errors = await validate_indexes()
    all_errors.extend(index_errors)
    if index_errors:
        print(f"  ❌ {len(index_errors)} issues found")
        for error in index_errors:
            print(f"     - {error}")
    else:
        print(f"  ✅ All {len(REQUIRED_INDEXES)} required indexes present")

    print()
    print("=" * 60)

    if all_errors:
        print(f"❌ VALIDATION FAILED: {len(all_errors)} total issues")
        print()
        print("To fix schema issues, run:")
        print("  cd backend")
        print("  python -m alembic upgrade head")
        return 1
    else:
        print("✅ VALIDATION PASSED: Database schema is correct!")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
