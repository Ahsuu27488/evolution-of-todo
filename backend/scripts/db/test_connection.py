#!/usr/bin/env python3
"""Database connection test script.

Verifies Neon PostgreSQL connection and table setup.
"""

import os
import sys
from sqlalchemy import text
from sqlmodel import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable is not set")
    sys.exit(1)

print("Testing database connection...")

try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"},
    )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print(f"✅ Database connection successful!")

    with engine.connect() as conn:
        tables = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)).fetchall()
        print(f"✅ Found {len(tables)} tables: {[t[0] for t in tables]}")

    print("\n✅ All database tests passed!")

except Exception as e:
    print(f"\n❌ Database connection failed: {e}")
    sys.exit(1)
