"""
AI Chatbot package for Phase III.

This package provides:
- Agents: OpenAI Agents SDK agent definitions
- MCP: Model Context Protocol server and tools
- Models: Database models for conversations, messages, handoffs
- Services: OpenAI client, Qdrant client, chat orchestration
- Utils: Structured logging, language detection
- Middleware: Correlation ID, rate limiting

Per spec.md Phase III requirements.
"""

from .utils import (
    get_logger,
    bind_correlation_id,
    generate_correlation_id,
    get_correlation_id,
    detect_language,
    LanguageCode,
)
from .models import (
    Conversation,
    ConversationPublic,
    ConversationCreate,
    Message,
    MessagePublic,
    MessageRole,
    AgentHandoff,
    AgentHandoffPublic,
    ConversationPreference,
    ConversationPreferencePublic,
)
from .services import (
    OpenAIService,
    QdrantService,
    initialize_qdrant,
)
from .middleware import CorrelationMiddleware, UserIdMiddleware
from .rate_limit import RateLimitMiddleware, check_rate_limit

__all__ = [
    # Utils
    "get_logger",
    "bind_correlation_id",
    "generate_correlation_id",
    "get_correlation_id",
    "detect_language",
    "LanguageCode",
    # Models
    "Conversation",
    "ConversationPublic",
    "ConversationCreate",
    "Message",
    "MessagePublic",
    "MessageRole",
    "AgentHandoff",
    "AgentHandoffPublic",
    "ConversationPreference",
    "ConversationPreferencePublic",
    # Services
    "OpenAIService",
    "QdrantService",
    "initialize_qdrant",
    # Middleware
    "CorrelationMiddleware",
    "UserIdMiddleware",
    "RateLimitMiddleware",
    "check_rate_limit",
]
