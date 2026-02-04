"""
AI services package for Phase III.

Provides:
- OpenAI client: Chat, embeddings, transcription
- Qdrant client: Vector storage and semantic search
- Runner service: Agent orchestration with streaming
- MCP server: Model Context Protocol tools

Per spec.md FR-002 through FR-040.
"""

from .openai_client import (
    OpenAIService,
    TokenUsage,
    OpenAIResponse,
    EmbeddingResponse,
    TranscriptionResponse,
    get_openai_circuit_breaker,
    CircuitBreaker,
)
from .qdrant_client import (
    QdrantService,
    SearchResult,
    SearchResponse,
    get_qdrant_service,
    set_qdrant_service,
    initialize_qdrant,
)
from .runner_service import (
    RunnerService,
    RunnerResult,
    StreamEvent,
    StreamEventType,
    convert_to_sse_format,
    stream_with_correlation,
)

__all__ = [
    # OpenAI
    "OpenAIService",
    "TokenUsage",
    "OpenAIResponse",
    "EmbeddingResponse",
    "TranscriptionResponse",
    "get_openai_circuit_breaker",
    "CircuitBreaker",
    # Qdrant
    "QdrantService",
    "SearchResult",
    "SearchResponse",
    "get_qdrant_service",
    "set_qdrant_service",
    "initialize_qdrant",
    # Runner
    "RunnerService",
    "RunnerResult",
    "StreamEvent",
    "StreamEventType",
    "convert_to_sse_format",
    "stream_with_correlation",
]
