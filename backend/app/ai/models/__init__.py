"""
AI Chatbot Database Models for Phase III.

This module defines:
- Conversation: Chat sessions with metadata
- Message: Individual messages in conversations
- AgentHandoff: Records of agent transfers for audit trail
- ConversationPreference: User chat settings

Per data-model.md and spec.md requirements.
"""

from .conversation import (
    Conversation,
    ConversationPublic,
    ConversationCreate,
    LanguagePreference,
)
from .message import (
    Message,
    MessagePublic,
    MessageRole,
    MessageType,
    ToolCall,
)
from .agent_handoff import (
    AgentHandoff,
    AgentHandoffPublic,
)
from .conversation_preference import (
    ConversationPreference,
    ConversationPreferencePublic,
    ConversationPreferenceUpdate,
)

__all__ = [
    # Conversation
    "Conversation",
    "ConversationPublic",
    "ConversationCreate",
    "LanguagePreference",
    # Message
    "Message",
    "MessagePublic",
    "MessageRole",
    "MessageType",
    "ToolCall",
    # AgentHandoff
    "AgentHandoff",
    "AgentHandoffPublic",
    # ConversationPreference
    "ConversationPreference",
    "ConversationPreferencePublic",
    "ConversationPreferenceUpdate",
]
