"""
Agent Handoff model for multi-agent architecture.

Records agent transfer events for audit trail and debugging.
Per FR-073 through FR-078 in spec.md.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, DateTime, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class AgentType(str, Enum):
    """Agent types in the system."""

    TODO_ASSISTANT = "TodoAssistant"
    PLANNING_AGENT = "PlanningAgent"
    TASK_QUERY_AGENT = "TaskQueryAgent"
    # Future agents per FR-078:
    NOTIFICATION_AGENT = "NotificationAgent"
    CALENDAR_AGENT = "CalendarAgent"
    ANALYTICS_AGENT = "AnalyticsAgent"


# =============================================================================
# Database Model
# =============================================================================

class AgentHandoff(SQLModel, table=True):
    """
    Agent handoff database model.

    Records when a conversation is transferred between agents
    for audit trail and debugging.

    Per spec.md FR-073, LOG-030 through LOG-034.

    Attributes:
        id: Unique handoff identifier
        conversation_id: Associated conversation
        from_agent: Source agent name
        to_agent: Destination agent name
        reason: Why the handoff occurred
        context_snapshot: Conversation state at handoff time
        timestamp: When the handoff occurred
        success: Whether handoff completed successfully
        error_message: Error details if handoff failed
    """

    __tablename__ = "agent_handoffs"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PGUUID(as_uuid=True), primary_key=True),
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,  # For debugging by conversation
        description="Associated conversation ID",
    )
    from_agent: str = Field(
        max_length=100,
        description="Source agent name",
    )
    to_agent: str = Field(
        max_length=100,
        description="Destination agent name",
    )
    reason: str | None = Field(
        default=None,
        max_length=500,
        sa_column=Column(Text),
        description="Why the handoff occurred",
    )
    context_snapshot: dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON, nullable=False, server_default="{}"),
        description="Conversation state at handoff time",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    success: bool = Field(
        default=True,
        description="Whether handoff completed successfully",
    )
    error_message: str | None = Field(
        default=None,
        max_length=1000,
        description="Error details if handoff failed",
    )


# =============================================================================
# Pydantic Schemas
# =============================================================================

class AgentHandoffBase(BaseModel):
    """Base handoff schema."""

    from_agent: str
    to_agent: str
    reason: str | None = None


class AgentHandoffCreate(AgentHandoffBase):
    """Schema for creating a handoff record."""

    conversation_id: UUID
    context_snapshot: dict[str, Any] = {}


class AgentHandoffPublic(AgentHandoffBase):
    """Schema for handoff API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    context_snapshot: dict[str, Any]
    timestamp: datetime
    success: bool
    error_message: str | None
