"""NeonDB SSL connection test script.

Tests SSL connection to Neon PostgreSQL serverless database.
This script verifies:
1. DATABASE_URL is set with sslmode=require
2. SSL connection can be established
3. Basic database operations work
"""

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import create_engine

load_dotenv()

# =============================================================================
# Test Configuration
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable is not set")
    sys.exit(1)

# Check for sslmode parameter
if "sslmode" not in DATABASE_URL:
    print("⚠️  Warning: DATABASE_URL does not contain sslmode parameter")
    print("   Expected format: ...neondb?sslmode=require")
else:
    if "sslmode=require" in DATABASE_URL:
        print("✅ DATABASE_URL contains sslmode=require")
    else:
        sslmode = DATABASE_URL.split("sslmode=")[1].split("&")[0] if "sslmode=" in DATABASE_URL else "not set"
        print(f"⚠️  DATABASE_URL has sslmode={sslmode}")

# =============================================================================
# Test Connection
# =============================================================================

print("\nTesting database connection...")

try:
    # Create engine with SSL settings (matching db.py)
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "sslmode": "require",
        },
    )

    # Test basic connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print(f"✅ Database connection successful!")
        print(f"   Query result: {result}")

    # Test table check
    with engine.connect() as conn:
        tables = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('user', 'session', 'task', 'account')
        """)).fetchall()

        print(f"\n✅ Found {len(tables)} tables: {[t[0] for t in tables]}")

    print("\n✅ All database tests passed!")
    print("\nYou can now start the backend with:")
    print("  uvicorn app.main:app --reload --port 8000")

except Exception as e:
    print(f"\n❌ Database connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
