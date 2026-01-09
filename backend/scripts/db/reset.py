#!/usr/bin/env python3
"""Database reset script.

Drops and recreates the public schema to clear all data.
WARNING: This will DELETE ALL DATA in the database.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import asyncpg

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    sys.exit(1)


async def reset_database():
    """Drop and recreate the public schema."""
    conn_str = DATABASE_URL.replace("postgresql://", "postgres://").split("?")[0]

    print("=" * 50)
    print("  🔥 DATABASE RESET")
    print("=" * 50)
    print("⚠️  WARNING: This will DELETE ALL DATA!")
    print()

    try:
        conn = await asyncpg.connect(conn_str)
        print("✅ Connected to database")

        await conn.execute("DROP SCHEMA public CASCADE")
        print("🗑️  Public schema dropped")

        await conn.execute("CREATE SCHEMA public")
        await conn.execute("GRANT ALL ON SCHEMA public TO public")
        await conn.execute("GRANT ALL ON SCHEMA public TO current_user")
        print("🆕 Public schema recreated")

        await conn.close()

        print("\n✅ DATABASE RESET COMPLETE")
        print("\n💡 Next: Restart the backend to recreate tables")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(reset_database())
