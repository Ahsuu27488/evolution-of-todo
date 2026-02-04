"""
Test configuration and fixtures for MCP tool integration tests.

Per T105: MCP tool integration tests for User Story 7.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.ai.mcp.tools import TaskTools
from app.models import Task, Base
from app.simple_auth import get_password_hash


# =============================================================================
# Test Database Configuration
# =============================================================================

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_todo"
)

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an instance of the default event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    Per FR-027: Stateless tool execution - each test gets isolated state.
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session
        # Rollback after test
        await session.rollback()


@pytest.fixture
def test_user_id() -> str:
    """Provide a test user ID for MCP tool calls."""
    return "test-user-mcp-123"


@pytest.fixture
def test_user_id_2() -> str:
    """Provide a second test user ID for ownership verification tests."""
    return "test-user-mcp-456"


@pytest.fixture
def task_tools(db_session: AsyncSession) -> TaskTools:
    """
    Provide TaskTools instance with test database session.

    Per FR-027: Stateless - fresh tools instance per test.
    """
    return TaskTools(db_session)


@pytest.fixture
async def sample_task(
    db_session: AsyncSession,
    test_user_id: str,
) -> Task:
    """
    Create a sample task in the database for testing.

    Returns:
        Task object with test data
    """
    task = Task(
        user_id=test_user_id,
        title="Test Task for MCP Integration",
        description="This is a test task created by pytest fixture",
        priority="MEDIUM",
        completed=False,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def sample_task_for_user_2(
    db_session: AsyncSession,
    test_user_id_2: str,
) -> Task:
    """
    Create a sample task for user 2 in the database for ownership testing.

    Per FR-029: Ownership verification tests.
    """
    task = Task(
        user_id=test_user_id_2,
        title="User 2 Task - Should Not Be Accessible",
        description="This task belongs to user 2 only",
        priority="HIGH",
        completed=False,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def completed_sample_task(
    db_session: AsyncSession,
    test_user_id: str,
) -> Task:
    """
    Create a completed sample task for status filter testing.
    """
    task = Task(
        user_id=test_user_id,
        title="Completed Test Task",
        description="This task is already completed",
        priority="LOW",
        completed=True,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task
