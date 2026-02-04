"""
Message model for AI chatbot conversations.

Represents individual messages in a conversation with
support for tool calls and correlation tracking.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, DateTime, Enum as SQLEnum, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ToolCall:
    """
    Represents a tool call made by the AI agent.

    Per MCP specification FR-021 through FR-030.

    Attributes:
        name: MCP tool name (e.g., "add_task", "list_tasks")
        parameters: Tool input parameters
        result: Tool execution result (if completed)
        error: Error message if tool failed
        duration_ms: Tool execution time
    """

    name: str
    parameters: dict[str, Any]
    result: Any | None = None
    error: str | None = None
    duration_ms: float | None = None


# =============================================================================
# Database Model
# =============================================================================

class Message(SQLModel, table=True):
    """
    Message database model.

    Represents a single message in a conversation.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Parent conversation ID
        correlation_id: Distributed tracing ID for observability
        role: Message role (user/assistant/system)
        content: Message text content
        tool_calls: JSON array of tools invoked by assistant
        created_at: Message creation timestamp

    Per spec.md FR-005, LOG-015.
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PGUUID(as_uuid=True), primary_key=True),
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,  # For loading conversation history
        description="Parent conversation ID",
    )
    correlation_id: str | None = Field(
        default=None,
        index=True,  # For distributed tracing queries
        description="Correlation ID for request tracing",
    )
    role: MessageRole = Field(
        sa_column=Column(
            SQLEnum(MessageRole, values_callable=lambda x: [e.value for e in x]),
            nullable=False
        ),
        description="Role of message sender",
    )
    content: str = Field(
        max_length=10000,
        sa_column=Column(Text, nullable=False),
        description="Message text content",
    )
    tool_calls: list[dict[str, Any]] = Field(
        default=[],
        sa_column=Column(JSON, nullable=False, server_default="[]"),
        description="Tools invoked by assistant (for role=assistant)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


# =============================================================================
# Pydantic Schemas
# =============================================================================

class ToolCallSchema(BaseModel):
    """Schema for tool call data."""

    name: str
    parameters: dict[str, Any]
    result: Any | None = None
    error: str | None = None
    duration_ms: float | None = None


class MessageBase(BaseModel):
    """Base message schema."""

    role: MessageRole
    content: str


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    conversation_id: UUID
    correlation_id: str | None = None
    tool_calls: list[ToolCallSchema] = []


class MessagePublic(MessageBase):
    """Schema for message API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    correlation_id: str | None
    tool_calls: list[ToolCallSchema]
    created_at: datetime


class MessageList(BaseModel):
    """Schema for list of messages."""

    messages: list[MessagePublic]
    total: int
