#!/usr/bin/env python3
"""
Resync all task embeddings to Qdrant.

This script fixes stale embedding data by regenerating all embeddings
from the current database state. Run this after updating the embedding sync logic.

Usage:
    python scripts/resync_qdrant_embeddings.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models import Task
from app.ai.services.openai_client import OpenAIService
from app.ai.services.qdrant_client import QdrantService
from app.ai.utils.logging import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = get_logger("scripts", "ResyncEmbeddings")

# Validate required environment variables
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment variable is required")
    print("ERROR: OPENAI_API_KEY not set. Please check your .env file.")
    sys.exit(1)


async def resync_all_embeddings():
    """Regenerate and store embeddings for all tasks."""

    # Explicitly load from .env file (in backend directory)
    # Use override=True to ensure values are loaded even if they exist as None
    script_dir = Path(__file__).parent
    dotenv_path = script_dir.parent / ".env"
    load_dotenv(dotenv_path, override=True)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        return

    # Convert to async URL for SQLAlchemy async engine
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgres+asyncpg://", 1)

    # Strip SSL parameters
    database_url = database_url.split("?")[0]

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # Initialize Qdrant service with explicit config
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url:
        logger.error("QDRANT_URL not found in environment")
        await engine.dispose()
        return

    qdrant_service = QdrantService(url=qdrant_url, api_key=qdrant_api_key)
    await qdrant_service.initialize()

    if not qdrant_service.is_available():
        logger.error("Qdrant service not available after initialization")
        await engine.dispose()
        return

    # Get API key for OpenAI service
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment")
        await engine.dispose()
        return

    openai_service = OpenAIService(api_key=api_key)

    # Query all tasks using proper session
    async with async_session_maker() as session:
        result = await session.execute(select(Task).order_by(Task.id))
        tasks = result.scalars().all()

    logger.info(f"Found {len(tasks)} tasks to resync")

    success_count = 0
    error_count = 0

    for task in tasks:
        try:
            # Generate embedding
            text_to_embed = f"{task.title}. {task.description or ''}"
            embedding_response = await openai_service.generate_embedding(text_to_embed)

            # Prepare tags list
            tags_list = []
            if task.tags:
                if isinstance(task.tags, list):
                    tags_list = [
                        tag.get("name", "") if isinstance(tag, dict) else str(tag)
                        for tag in task.tags
                    ]

            # Update in Qdrant with CURRENT database state
            success = await qdrant_service.upsert_task_embedding(
                task_id=task.id,
                user_id=task.user_id,
                embedding=embedding_response.embedding,
                payload={
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,  # Current value from DB
                    "priority": task.priority.value,
                    "tags": tags_list,
                },
            )

            if success:
                success_count += 1
                logger.info(
                    f"Resynced task {task.id}: {task.title[:40]}... "
                    f"completed={task.completed}, priority={task.priority.value}"
                )
            else:
                error_count += 1
                logger.warning(f"Failed to resync task {task.id}")

        except Exception as e:
            error_count += 1
            logger.error(f"Error resyncing task {task}: {e}")

    logger.info(f"Resync complete: {success_count} succeeded, {error_count} failed")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(resync_all_embeddings())
