"""
Message model for AI chatbot conversations.

Represents individual messages in a conversation with
support for tool calls and correlation tracking.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field as PydanticField, model_validator
from sqlalchemy import Column, DateTime, Enum as SQLEnum, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Role of the message sender.

    Per OpenAI API format:
    - user: Message from the user
    - assistant: Message from the AI
    - system: System instruction
    - tool: Tool result (for maintaining conversation context after tool calls)
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"  # FR-005: Tool results for conversation context


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
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


# =============================================================================
# Pydantic Schemas
# =============================================================================

class ToolCallSchema(BaseModel):
    """Schema for tool call data.

    Database stores tools as {tool, arguments} but API uses {name, parameters}.
    Field serializer handles conversion during serialization.
    """

    name: str
    parameters: dict[str, Any]
    result: Any | None = None
    error: str | None = None
    duration_ms: float | None = None

    @classmethod
    def from_db_format(cls, data: dict[str, Any]) -> "ToolCallSchema":
        """Convert database format {tool, arguments} to API format {name, parameters}."""
        return cls(
            name=data.get("tool", data.get("name", "")),
            parameters=data.get("arguments", data.get("parameters", {})),
            result=data.get("result"),
            error=data.get("error"),
            duration_ms=data.get("duration_ms"),
        )


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
    """Schema for message API responses.

    Uses camelCase aliases for JSON serialization to match frontend expectations.
    Python attributes remain snake_case per PEP 8.

    Handles conversion from database format {tool, arguments} to API format {name, parameters}.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    conversation_id: UUID = PydanticField(alias="conversationId")
    correlation_id: str | None = PydanticField(alias="correlationId")
    tool_calls: list[ToolCallSchema] = PydanticField(alias="toolCalls", default_factory=list)
    created_at: datetime = PydanticField(alias="createdAt")

    @model_validator(mode="before")
    @classmethod
    def convert_tool_calls_format(cls, data: Any) -> Any:
        """Convert tool_calls from database format to API format before validation.

        Database stores: [{tool: str, arguments: dict}] or None
        API expects: [{name: str, parameters: dict}] or []

        This validator runs BEFORE Pydantic validation, so it can handle None values
        and format mismatches that would otherwise cause validation errors.

        Handles edge case where arguments/parameters is stored as JSON string instead of dict.
        """
        if not isinstance(data, dict):
            return data

        # Handle tool_calls conversion
        tool_calls_raw = data.get("tool_calls")
        if tool_calls_raw is None:
            data["tool_calls"] = []
        elif isinstance(tool_calls_raw, list):
            # Convert each tool call from {tool, arguments} to {name, parameters}
            converted_calls = []
            for item in tool_calls_raw:
                if isinstance(item, dict):
                    # Already has correct format
                    if "name" in item and "parameters" in item:
                        converted_calls.append(item)
                    # Has database format {tool, arguments}
                    elif "tool" in item or "arguments" in item:
                        # Get arguments value - may be dict or JSON string
                        arguments_value = item.get("arguments", item.get("parameters", {}))

                        # Parse JSON string if needed (fixes double-serialization bug)
                        if isinstance(arguments_value, str):
                            try:
                                arguments_value = json.loads(arguments_value)
                            except json.JSONDecodeError:
                                # If parsing fails, keep as-is and let Pydantic handle validation error
                                pass

                        converted_calls.append({
                            "name": item.get("tool", ""),
                            "parameters": arguments_value,
                            "result": item.get("result"),
                            "error": item.get("error"),
                            "duration_ms": item.get("duration_ms"),
                        })
                    else:
                        converted_calls.append(item)
                else:
                    converted_calls.append(item)
            data["tool_calls"] = converted_calls

        return data


class MessageList(BaseModel):
    """Schema for list of messages."""

    messages: list[MessagePublic]
    total: int
