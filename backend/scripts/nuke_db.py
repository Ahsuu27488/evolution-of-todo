#!/usr/bin/env python3
"""
Database Reset Script - Phase 0 REPAIR

Drops and recreates the public schema to clear all Better Auth tables.
This is necessary when BETTER_AUTH_SECRET is rotated, as the old
JWKS and session data become undecryptable.

WARNING: This will DELETE ALL DATA in the database.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)


async def reset_database():
    """Drop and recreate the public schema."""

    # Import asyncpg here after dotenv is loaded
    import asyncpg

    print("=" * 50)
    print("  🔥 DATABASE RESET - Phase 0 REPAIR")
    print("=" * 50)
    print(f"📍 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}")
    print()
    print("⚠️  WARNING: This will DELETE ALL DATA!")
    print()

    # Convert postgresql:// to postgres:// for asyncpg if needed
    conn_str = DATABASE_URL.replace("postgresql://", "postgres://")
    # Strip any SSL parameters for the connection
    conn_str = conn_str.split("?")[0]

    try:
        # Connect to the 'postgres' database first (we can't drop the DB we're connected to)
        # Instead, we'll drop and recreate the 'public' schema
        conn = await asyncpg.connect(conn_str)

        print("✅ Connected to database")

        # Drop all tables in the public schema by dropping and recreating it
        print("\n🗑️  Dropping public schema...")
        await conn.execute("DROP SCHEMA public CASCADE")
        print("   ✓ Public schema dropped")

        print("\n🆕 Recreating public schema...")
        await conn.execute("CREATE SCHEMA public")
        print("   ✓ Public schema created")

        # Grant necessary permissions
        print("\n🔐 Granting permissions...")
        await conn.execute("GRANT ALL ON SCHEMA public TO public")
        await conn.execute("GRANT ALL ON SCHEMA public TO current_user")
        print("   ✓ Permissions granted")

        # Close connection
        await conn.close()

        print("\n" + "=" * 50)
        print("  ✅ DATABASE RESET COMPLETE")
        print("=" * 50)
        print("\n💡 Next steps:")
        print("   1. Restart the backend server")
        print("   2. Better Auth will auto-create tables on first request")
        print("   3. Run the verification script")
        print()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(reset_database())
