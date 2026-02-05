"""
Qdrant vector database client service for Phase III.

Provides:
- Vector storage for task embeddings
- Semantic search functionality
- Collection management
- Connection recovery and circuit breaker

Per spec.md FR-031 through FR-040, LOG-041, FR-103.
"""

import asyncio
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    PointStruct,
    UpdateCollection,
    VectorParams,
    CreateCollection,
)

from app.ai.utils.logging import get_logger


# =============================================================================
# Configuration
# =============================================================================

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Collection names
TASKS_COLLECTION = "tasks"

# Embedding dimension for text-embedding-3-small
EMBEDDING_DIMENSION = 1536


class ConnectionState(str, Enum):
    """Qdrant connection state per FR-103."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"


@dataclass
class SearchResult:
    """Semantic search result."""

    task_id: int
    score: float
    payload: dict[str, Any]


@dataclass
class SearchResponse:
    """Response from semantic search."""

    results: list[SearchResult]
    total: int
    duration_ms: float


# =============================================================================
# Circuit Breaker
# =============================================================================

class QdrantCircuitBreaker:
    """
    Circuit breaker for Qdrant failures.

    Per FR-103, FR-099:
    - Open circuit after 3 consecutive failures
    - Attempt reconnection every 30 seconds
    - Fallback to keyword search when open
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_seconds: int = 30,
    ) -> None:
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = ConnectionState.CONNECTED
        self.logger = get_logger("ai", "QdrantCircuitBreaker")

    def is_open(self) -> bool:
        """Check if circuit is open (Qdrant unavailable)."""
        if self.state == ConnectionState.DISCONNECTED:
            # Check if timeout passed
            if time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = ConnectionState.RECONNECTING
                self.logger.info("Circuit breaker entering RECONNECTING state")
                return False
            return True
        return False

    def record_success(self) -> None:
        """Record successful operation."""
        if self.state != ConnectionState.CONNECTED:
            old_state = self.state
            self.state = ConnectionState.CONNECTED
            self.logger.info(f"Circuit breaker reset to CONNECTED (was {old_state})")
        self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            old_state = self.state
            self.state = ConnectionState.DISCONNECTED
            if old_state != ConnectionState.DISCONNECTED:
                self.logger.warning(
                    "Qdrant circuit breaker opened",
                    failure_count=self.failure_count,
                    threshold=self.failure_threshold,
                )


# =============================================================================
# Service
# =============================================================================

class QdrantService:
    """
    Qdrant vector database client service.

    Provides:
    - Collection creation and management
    - Point insertion for task embeddings
    - Semantic search with filtering
    - Connection recovery

    Per FR-031 through FR-040.

    Example:
        service = QdrantService()
        await service.initialize()

        # Upsert task embedding
        await service.upsert_task_embedding(
            task_id=1,
            user_id="user123",
            embedding=[0.1, 0.2, ...],
            payload={"title": "Buy groceries", "description": "..."},
        )

        # Semantic search
        results = await service.semantic_search(
            user_id="user123",
            query_embedding=[0.1, 0.2, ...],
            limit=10,
        )
    """

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_name: str = TASKS_COLLECTION,
        embedding_dimension: int = EMBEDDING_DIMENSION,
    ) -> None:
        """
        Initialize Qdrant service.

        Args:
            url: Qdrant cluster URL
            api_key: Qdrant API key (if using cloud)
            collection_name: Name of the tasks collection
            embedding_dimension: Dimension of embedding vectors
        """
        self.url = url or QDRANT_URL
        self.api_key = api_key or QDRANT_API_KEY
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self.circuit_breaker = QdrantCircuitBreaker()
        self.logger = get_logger("ai", "QdrantService")

        if not self.url:
            self.logger.warning("QDRANT_URL not set, semantic search will be disabled")

        # Client initialized in initialize()
        self.client: QdrantClient | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize Qdrant client and collection.

        Creates collection if it doesn't exist.
        """
        if not self.url:
            self.logger.warning("Qdrant URL not configured, skipping initialization")
            return

        try:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
            )

            # Check if collection exists, create if not
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE,
                    ),
                )

            self._initialized = True
            self.circuit_breaker.record_success()
            self.logger.info("Qdrant service initialized successfully")

        except Exception as e:
            self.logger.error(
                "Failed to initialize Qdrant",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            self.circuit_breaker.record_failure()

    async def health_check(self) -> bool:
        """
        Check Qdrant connection health.

        Per FR-103: Ping Qdrant before each search operation.

        Returns:
            True if connected, False otherwise
        """
        if not self.client or not self._initialized:
            return False

        try:
            # Simple collection list as health check
            self.client.get_collections()
            self.circuit_breaker.record_success()
            return True
        except Exception:
            self.circuit_breaker.record_failure()
            return False

    async def upsert_task_embedding(
        self,
        task_id: int,
        user_id: str,
        embedding: list[float],
        payload: dict[str, Any] | None = None,
    ) -> bool:
        """
        Upsert task embedding to Qdrant.

        Per FR-034: Create task embedding on task creation and update.

        Args:
            task_id: Task ID (used as point ID)
            user_id: User ID for scoping
            embedding: Vector embedding
            payload: Optional task metadata for filtering

        Returns:
            True if successful, False otherwise
        """
        if self.circuit_breaker.is_open():
            return False

        try:
            # Health check before operation (FR-103)
            if not await self.health_check():
                return False

            # Use task_id as integer (not string) for Qdrant point ID
            # Qdrant expects: unsigned integer OR valid UUID string
            point = PointStruct(
                id=task_id,
                vector=embedding,
                payload={
                    "user_id": user_id,
                    **(payload or {}),
                },
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )

            self.circuit_breaker.record_success()

            self.logger.debug(
                "Task embedding upserted",
                task_id=task_id,
                user_id=user_id,
            )
            return True

        except Exception as e:
            self.logger.error(
                "Failed to upsert task embedding",
                task_id=task_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            self.circuit_breaker.record_failure()
            return False

    async def delete_task_embedding(self, task_id: int) -> bool:
        """
        Delete task embedding from Qdrant.

        Args:
            task_id: Task ID to delete

        Returns:
            True if successful, False otherwise
        """
        if self.circuit_breaker.is_open():
            return False

        try:
            if not await self.health_check():
                return False

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[task_id],  # Use integer, not string
            )

            self.circuit_breaker.record_success()

            self.logger.debug(
                "Task embedding deleted",
                task_id=task_id,
            )
            return True

        except Exception as e:
            self.logger.error(
                "Failed to delete task embedding",
                task_id=task_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            self.circuit_breaker.record_failure()
            return False

    async def semantic_search(
        self,
        user_id: str,
        query_embedding: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> SearchResponse:
        """
        Perform semantic search for tasks.

        Per FR-036, FR-037, FR-039:
        - Return semantically similar tasks ranked by cosine similarity
        - Scope to user_id (no cross-user search)
        - Return results ranked by relevance

        Args:
            user_id: User ID to scope search
            query_embedding: Query vector embedding
            limit: Maximum results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            SearchResponse with results and timing

        Raises:
            Exception: If search fails and circuit breaker is open
        """
        start_time = time.time()

        # Log request (LOG-041)
        self.logger.info(
            "Qdrant search request",
            event_type="qdrant_search",
            collection_name=self.collection_name,
            user_id=user_id,
            limit=limit,
        )

        if self.circuit_breaker.is_open():
            self.logger.warning("Qdrant circuit breaker open, returning empty results")
            return SearchResponse(results=[], total=0, duration_ms=0)

        try:
            if not await self.health_check():
                return SearchResponse(results=[], total=0, duration_ms=0)

            # Search with user_id filter (FR-039)
            # Note: Qdrant client v1.16+ uses query_points instead of search
            from qdrant_client.models import Filter

            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,  # Dense vector for nearest search
                query_filter=Filter(
                    must=[
                        {"key": "user_id", "match": {"value": user_id}},
                    ]
                ),
                limit=limit,
                score_threshold=score_threshold,
            )

            duration_ms = (time.time() - start_time) * 1000

            # Convert to search results
            # QueryResponse has a .points attribute containing ScoredPoint list
            results = []
            for point in response.points:
                results.append(SearchResult(
                    task_id=int(point.id),
                    score=point.score,
                    payload=point.payload or {},
                ))

            # Log response (LOG-041)
            self.logger.info(
                "Qdrant search response",
                event_type="qdrant_response",
                collection_name=self.collection_name,
                duration_ms=round(duration_ms, 2),
                result_count=len(results),
                success=True,
            )

            self.circuit_breaker.record_success()

            return SearchResponse(
                results=results,
                total=len(results),
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                "Qdrant search failed",
                event_type="qdrant_error",
                collection_name=self.collection_name,
                user_id=user_id,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration_ms, 2),
            )
            self.circuit_breaker.record_failure()

            # Return empty results for fallback to keyword search (FR-038)
            return SearchResponse(results=[], total=0, duration_ms=duration_ms)

    async def batch_upsert(
        self,
        embeddings: list[tuple[int, str, list[float], dict[str, Any]]],
    ) -> int:
        """
        Batch upsert multiple task embeddings.

        Args:
            embeddings: List of (task_id, user_id, embedding, payload) tuples

        Returns:
            Number of successfully upserted embeddings
        """
        if self.circuit_breaker.is_open():
            return 0

        try:
            if not await self.health_check():
                return 0

            points = [
                PointStruct(
                    id=task_id,  # Use integer, not string
                    vector=emb,
                    payload={
                        "user_id": user_id,
                        **payload,
                    },
                )
                for task_id, user_id, emb, payload in embeddings
            ]

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            self.circuit_breaker.record_success()

            self.logger.info(
                "Batch embeddings upserted",
                count=len(points),
            )
            return len(points)

        except Exception as e:
            self.logger.error(
                "Failed to batch upsert embeddings",
                error_type=type(e).__name__,
                error_message=str(e),
            )
            self.circuit_breaker.record_failure()
            return 0

    def is_available(self) -> bool:
        """
        Check if Qdrant service is available.

        Returns:
            True if connected, False if disconnected or reconnecting
        """
        return self.circuit_breaker.state == ConnectionState.CONNECTED

    async def collection_exists(self) -> bool:
        """
        Check if the tasks collection exists in Qdrant.

        Returns:
            True if collection exists, False otherwise
        """
        if not self.client or not self._initialized:
            return False

        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            return self.collection_name in collection_names
        except Exception:
            return False


# =============================================================================
# Global Service Instance
# =============================================================================

_qdrant_service: QdrantService | None = None


def get_qdrant_service() -> QdrantService | None:
    """Get the global Qdrant service instance."""
    return _qdrant_service


def set_qdrant_service(service: QdrantService) -> None:
    """Set the global Qdrant service instance."""
    global _qdrant_service
    _qdrant_service = service


async def initialize_qdrant() -> QdrantService | None:
    """
    Initialize the global Qdrant service.

    Should be called during application startup.

    Returns:
        Initialized QdrantService or None if not configured
    """
    global _qdrant_service

    if _qdrant_service is None:
        _qdrant_service = QdrantService()
        await _qdrant_service.initialize()

    return _qdrant_service
