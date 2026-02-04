"""Database connection module for Neon PostgreSQL with asyncpg.

This module provides async database connectivity using SQLModel with asyncpg driver.
It includes connection pooling, table creation, and session management.
"""

import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlmodel import SQLModel

# Import all models to ensure they're registered with SQLModel.metadata
# [Task]: T017 - Import notification models
import app.models  # noqa: F401
import app.models.notification  # noqa: F401
import app.models.push_subscription  # noqa: F401
import app.models.email_delivery_log  # noqa: F401

load_dotenv()

# Get database URL and convert to async format
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Convert postgresql:// to postgresql+asyncpg:// for async driver
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgres+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# STRIP SSL parameters from URL to prevent SQLAlchemy from passing channel_binding
# We'll configure SSL via code instead (connect_args)
ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.split("?")[0]

# Create async engine with connection pooling for serverless Neon
# Settings per research.md for optimal serverless performance
# SSL is configured via connect_args using "require" to avoid start_tls issues
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",  # SQL logging in dev
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,  # Recycle connections after 5 min (serverless friendly)
    pool_size=5,  # Min pool size per quickstart.md
    max_overflow=15,  # Max pool size: 5 + 15 = 20 per quickstart.md
    connect_args={"ssl": "require"},  # Direct SSL requirement, avoids start_tls error
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables() -> None:
    """Create all SQLModel tables asynchronously.

    Called on application startup via lifespan handler.
    This creates all tables defined in models.py if they don't exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions.

    Yields:
        AsyncSession: SQLAlchemy async session for database operations

    Example:
        @app.get("/tasks")
        async def list_tasks(session: AsyncSession = Depends(get_session)):
            result = await session.exec(select(Task))
            return result.all()
    """
    async with async_session_maker() as session:
        yield session
