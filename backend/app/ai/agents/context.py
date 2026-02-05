"""
Context for agent execution.

Provides the TodoContext class that carries user-specific
state through agent handoffs.

Uses contextvars for async-safe context propagation to tool functions.
Per openai-agents-guide: The SDK doesn't automatically inject context
into @function_tool decorated functions, so we use context variables.
"""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from datetime import date
from typing import Any

# =============================================================================
# Context Variable for Tool Access
# =============================================================================
# Per T100-T105: MCP Tool Integration
# The OpenAI Agents SDK passes context to Runner.run() but doesn't
# automatically inject it into @function_tool decorated functions.
# We use contextvars to provide async-safe implicit context access.
# =============================================================================

_todo_context: contextvars.ContextVar["TodoContext"] = contextvars.ContextVar(
    "todo_context",
    default=None,
)


def get_current_context() -> TodoContext | None:
    """
    Get the current TodoContext from context variable.

    Tool functions should use this instead of relying on ctx parameter,
    as the SDK doesn't automatically inject context into @function_tool.

    Returns:
        TodoContext if set, None otherwise

    Example:
        ctx = get_current_context()
        if not ctx or not ctx.user_id:
            raise ValueError("No active user context")
    """
    return _todo_context.get(None)


def set_context(context: TodoContext) -> Any:
    """
    Set the TodoContext for the current async context.

    Called by RunnerService before executing agent.

    Args:
        context: TodoContext to store

    Returns:
        Context token that can be used to reset the context
    """
    return _todo_context.set(context)


def reset_context(token: Any) -> None:
    """
    Reset the TodoContext to previous value.

    Args:
        token: Token returned by set_context()
    """
    _todo_context.reset(token)


@dataclass
class TodoContext:
    """
    Execution context for Todo agents.

    Carries user-specific state through the agent lifecycle
    including handoffs between specialized agents.

    Per spec.md FR-018: Context must persist across handoffs.
    """

    user_id: str
    conversation_id: str
    correlation_id: str

    # Optional preferences
    language_preference: str = "auto"  # auto, en, ur
    timezone: str = "UTC"

    # Current date for agent awareness (fixes "tomorrow" parsing to model's birth date)
    current_date: date | None = None

    # Runtime state (not persisted)
    session: Any = None  # Database session for MCP tools
    tool_results: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for logging."""
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "correlation_id": self.correlation_id,
            "language_preference": self.language_preference,
            "timezone": self.timezone,
            "current_date": str(self.current_date) if self.current_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TodoContext":
        """Create context from dictionary."""
        return cls(
            user_id=data["user_id"],
            conversation_id=data["conversation_id"],
            correlation_id=data["correlation_id"],
            language_preference=data.get("language_preference", "auto"),
            timezone=data.get("timezone", "UTC"),
            current_date=data.get("current_date"),
        )
