"""
Qdrant initialization and embedding migration script.

Run this script to:
1. Initialize the Qdrant collection
2. Generate embeddings for all existing tasks

Usage:
    python -m app.ai.scripts.init_qdrant
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

from app.ai.services import OpenAIService, QdrantService
from app.ai.utils.logging import get_logger
from app.db import async_session_maker
from sqlmodel import select

from app.models import Task

load_dotenv()

logger = get_logger("scripts", "InitQdrant")

# Global service instance to share across functions
_qdrant_service: QdrantService | None = None
_openai_service: OpenAIService | None = None


def get_qdrant_service() -> QdrantService:
    """Get or create global Qdrant service instance."""
    global _qdrant_service
    if _qdrant_service is None:
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        _qdrant_service = QdrantService(url=qdrant_url, api_key=qdrant_api_key)
    return _qdrant_service


def get_openai_service() -> OpenAIService:
    """Get or create global OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        openai_key = os.getenv("OPENAI_API_KEY")
        _openai_service = OpenAIService(api_key=openai_key)
    return _openai_service


async def init_qdrant_collection() -> bool:
    """Initialize the Qdrant collection."""
    logger.info("Starting Qdrant collection initialization...")

    # Explicitly pass environment variables to avoid loading issues
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url:
        logger.error("QDRANT_URL environment variable is not set")
        return False

    logger.info(f"Connecting to Qdrant at: {qdrant_url[:50]}...")

    qdrant_service = get_qdrant_service()

    try:
        await qdrant_service.initialize()

        # Create payload index on user_id for filtering (required for semantic search)
        from qdrant_client import QdrantClient
        from qdrant_client.models import PayloadSchemaType

        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

        # Check if collection exists and has user_id index
        try:
            collection_info = client.get_collection(qdrant_service.collection_name)
            has_user_id_index = collection_info.payload_schema and "user_id" in collection_info.payload_schema

            if not has_user_id_index:
                logger.info("Creating payload index on user_id field")
                client.create_payload_index(
                    collection_name=qdrant_service.collection_name,
                    field_name="user_id",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                logger.info("✓ Payload index created on user_id")
        except Exception as idx_err:
            logger.warning(f"Could not create payload index: {idx_err}")

        # Verify collection exists
        exists = await qdrant_service.collection_exists()
        if exists:
            logger.info("✓ Qdrant collection created/verified")
            return True
        else:
            logger.error("✗ Qdrant collection does not exist after initialization")
            return False
    except Exception as e:
        logger.error(f"✗ Failed to initialize Qdrant: {e}")
        return False


async def generate_embeddings_for_existing_tasks() -> int:
    """Generate embeddings for all existing tasks that don't have one."""
    logger.info("Starting embedding generation for existing tasks...")

    qdrant_service = get_qdrant_service()
    openai_service = get_openai_service()

    # Skip availability check - we'll handle errors directly
    logger.info(f"Qdrant service state: {qdrant_service.circuit_breaker.state}")

    count = 0
    failed = 0

    async with async_session_maker() as session:
        # Get all tasks
        statement = select(Task)
        result = await session.execute(statement)
        tasks = result.scalars().all()

        logger.info(f"Found {len(tasks)} total tasks")

        # Process each task
        for task in tasks:
            try:
                # Skip if embedding_id is already set (though we found all are NULL)
                if task.embedding_id:
                    logger.debug(f"Skipping task {task.id} - already has embedding")
                    continue

                # Generate embedding
                text_to_embed = f"{task.title}. {task.description or ''}"
                embedding_response = await openai_service.generate_embedding(text_to_embed)

                # Store in Qdrant (with detailed error logging)
                try:
                    success = await qdrant_service.upsert_task_embedding(
                        task_id=task.id,
                        user_id=task.user_id,
                        embedding=embedding_response.embedding,
                        payload={
                            "title": task.title,
                            "description": task.description or "",
                            "completed": task.completed,
                        },
                    )

                    if success:
                        # Update task with embedding_id
                        task.embedding_id = str(task.id)
                        count += 1

                        # Log progress every 10 tasks
                        if count % 10 == 0:
                            logger.info(f"Generated {count} embeddings so far...")
                    else:
                        failed += 1
                        logger.warning(f"Failed to upsert embedding for task {task.id} (upsert returned False)")
                except Exception as upsert_err:
                    failed += 1
                    logger.error(
                        f"Failed to upsert embedding for task {task.id}",
                        error_type=type(upsert_err).__name__,
                        error_message=str(upsert_err),
                    )

            except Exception as e:
                failed += 1
                logger.error(f"Failed to generate embedding for task {task.id}: {e}")

        # Commit all changes
        await session.commit()

    logger.info(f"✓ Generated {count} embeddings successfully")
    if failed > 0:
        logger.warning(f"✗ Failed to generate {failed} embeddings")

    return count


async def verify_qdrant_status() -> dict:
    """Verify Qdrant status and return info."""
    logger.info("Verifying Qdrant status...")

    qdrant_service = get_qdrant_service()

    if not qdrant_service.is_available():
        return {
            "available": False,
            "collection_exists": False,
            "message": "Qdrant service is not available"
        }

    try:
        exists = await qdrant_service.collection_exists()
        return {
            "available": True,
            "collection_exists": exists,
            "message": "Qdrant is available" + (" and collection exists" if exists else " but collection does not exist")
        }
    except Exception as e:
        return {
            "available": False,
            "collection_exists": False,
            "message": f"Error checking Qdrant: {e}"
        }


async def main():
    """Main function to run all initialization steps."""
    print("=" * 60)
    print("Qdrant Initialization and Embedding Migration Script")
    print("=" * 60)

    # Check environment variables
    if not os.getenv("QDRANT_URL"):
        print("✗ QDRANT_URL environment variable is not set")
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("✗ OPENAI_API_KEY environment variable is not set")
        return

    print(f"QDRANT_URL: {os.getenv('QDRANT_URL')}")
    print(f"OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
    print("-" * 60)

    # Step 1: Verify current status
    print("\n1. Checking current Qdrant status...")
    status = await verify_qdrant_status()
    print(f"   Status: {status['message']}")

    # Step 2: Initialize collection if needed
    if not status.get("collection_exists"):
        print("\n2. Initializing Qdrant collection...")
        success = await init_qdrant_collection()
        if success:
            print("   ✓ Collection initialized successfully")
        else:
            print("   ✗ Failed to initialize collection")
            return
    else:
        print("\n2. Collection already exists, skipping initialization")

    # Step 3: Generate embeddings for existing tasks
    print("\n3. Generating embeddings for existing tasks...")
    count = await generate_embeddings_for_existing_tasks()

    # Step 4: Final verification
    print("\n4. Final verification...")
    final_status = await verify_qdrant_status()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Qdrant Status: {final_status['message']}")
    print(f"Embeddings Generated: {count}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
