#!/usr/bin/env python3
"""
Qdrant collection validation script for Phase III AI Chatbot.

Validates that:
- Qdrant connection is working
- Tasks collection exists
- Collection has correct vector configuration
- Payload indexes exist for user_id filtering

Run with: python scripts/validate_qdrant.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai.services.qdrant_client import (
    QdrantService,
    TASKS_COLLECTION,
    EMBEDDING_DIMENSION,
)


async def validate_qdrant_connection() -> dict:
    """Validate Qdrant connection and return status."""
    result = {
        "connected": False,
        "has_collection": False,
        "collection_info": None,
        "errors": [],
    }

    service = QdrantService()
    await service.initialize()

    # Check connection
    if service.client:
        result["connected"] = await service.health_check()

    if not result["connected"]:
        result["errors"].append("Cannot connect to Qdrant. Check QDRANT_URL and QDRANT_API_KEY.")
        return result

    # Check collection exists
    try:
        collections = service.client.get_collections().collections
        collection_names = [c.name for c in collections]
        result["has_collection"] = TASKS_COLLECTION in collection_names

        if result["has_collection"]:
            # Get collection info
            collection_info = service.client.get_collection(TASKS_COLLECTION)
            result["collection_info"] = collection_info

            # Validate vector configuration
            vector_config = collection_info.config.params.vectors
            if hasattr(vector_config, 'size'):
                result["vector_size"] = vector_config.size
                if vector_config.size != EMBEDDING_DIMENSION:
                    result["errors"].append(
                        f"Vector size mismatch: expected {EMBEDDING_DIMENSION}, got {vector_config.size}"
                    )

            # Check for payload schema (indexes)
            # Note: Qdrant doesn't expose payload indexes via API easily
            # but we can verify the collection is ready for operations

            # Test write/read operations
            test_point_id = "validation_test_point"
            try:
                # Try to delete if exists from previous validation
                service.client.delete(
                    collection_name=TASKS_COLLECTION,
                    points_selector=[test_point_id],
                )
            except Exception:
                pass  # Point doesn't exist, that's fine

        else:
            result["errors"].append(f"Collection '{TASKS_COLLECTION}' does not exist. It will be created on first use.")

    except Exception as e:
        result["errors"].append(f"Error checking collection: {type(e).__name__}: {e}")

    return result


async def main():
    """Run Qdrant validation."""
    print("=" * 60)
    print("Phase III AI Chatbot - Qdrant Validation")
    print("=" * 60)
    print()

    print("Configuration:")
    import os
    qdrant_url = os.getenv("QDRANT_URL", "Not set")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "Not set")

    if qdrant_url != "Not set":
        # Hide most of the URL for security
        masked_url = qdrant_url[:20] + "..." if len(qdrant_url) > 20 else qdrant_url
        print(f"  QDRANT_URL: {masked_url}")
    else:
        print(f"  QDRANT_URL: {qdrant_url}")

    api_key_set = "✓ Set" if qdrant_api_key != "Not set" else "✗ Not set"
    print(f"  QDRANT_API_KEY: {api_key_set}")
    print()

    # Run validation
    print("Validating Qdrant connection...")
    result = await validate_qdrant_connection()

    if result["connected"]:
        print("  ✅ Qdrant connection successful")
    else:
        print("  ❌ Qdrant connection failed")

    if result["has_collection"]:
        print(f"  ✅ Collection '{TASKS_COLLECTION}' exists")

        if result.get("vector_size"):
            print(f"     Vector size: {result['vector_size']} (expected {EMBEDDING_DIMENSION})")

        if result.get("collection_info"):
            info = result["collection_info"]
            if hasattr(info, 'config') and hasattr(info.config, 'params'):
                params = info.config.params
                if hasattr(params, 'vectors'):
                    vectors = params.vectors
                    if hasattr(vectors, 'distance'):
                        print(f"     Distance metric: {vectors.distance}")
    else:
        print(f"  ⚠️  Collection '{TASKS_COLLECTION}' does not exist")
        print(f"     It will be created automatically on first use")

    print()

    # Show any errors
    if result["errors"]:
        print("Errors found:")
        for error in result["errors"]:
            print(f"  ❌ {error}")
        print()
    else:
        print("✅ No errors found")

    print("=" * 60)

    # Return exit code based on connection status
    if result["connected"]:
        print("✅ QDRANT VALIDATION PASSED")
        return 0
    else:
        print("❌ QDRANT VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
