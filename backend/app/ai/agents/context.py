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
import time
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
    response_language: str | None = None  # Actual language to respond in (overrides detection)
    timezone: str = "UTC"

    # Current date for agent awareness (fixes "tomorrow" parsing to model's birth date)
    current_date: date | None = None

    # User profile information for personalized responses
    user_email: str | None = None
    user_first_name: str | None = None
    user_last_name: str | None = None
    user_display_name: str | None = None  # Computed display name

    # Runtime state (not persisted)
    session: Any = None  # Database session for MCP tools
    tool_results: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Valid task IDs from recent list_tasks call (for validation)
    # Prevents agent from hallucinating non-existent task IDs
    valid_task_ids: list[int] = field(default_factory=list)
    last_list_tasks_time: float | None = None  # When list_tasks was last called (epoch time)

    # Task ID cache TTL in seconds - after this, IDs are considered stale
    TASK_ID_CACHE_TTL: int = 300  # 5 minutes

    @property
    def user_name(self) -> str:
        """
        Get the user's name for personalized responses.

        Returns display_name if available, otherwise first_name,
        otherwise "there" as a neutral fallback.

        Examples:
            >>> ctx.user_name
            "Ahsan"
            >>> ctx.user_name  # When no name is set
            "there"
        """
        if self.user_display_name:
            return self.user_display_name
        if self.user_first_name:
            return self.user_first_name
        return "there"

    @property
    def user_greeting(self) -> str:
        """
        Get a culturally appropriate greeting for the user.

        Returns a greeting based on the user's name and language preference.

        Examples:
            >>> ctx.user_greeting
            "Hello Ahsan!"
            >>> ctx.user_greeting  # When Urdu preference
            "السلام علیکم Ahsan!"
        """
        name = self.user_name
        if self.language_preference == "ur" or self.response_language == "ur":
            return f"السلام علیکم {name}!"  # Assalam-o-Alaikum
        return f"Hello {name}!"

    def is_task_id_valid(self, task_id: int) -> bool:
        """
        Check if a task ID is valid (exists in the user's tasks).

        Uses the cached valid_task_ids list from recent list_tasks call.
        If cache is stale (> TASK_ID_CACHE_TTL seconds), returns True (bypass validation).

        Args:
            task_id: Task ID to validate

        Returns:
            True if task ID is valid or cache is stale, False otherwise
        """
        # If cache is empty or stale, bypass validation (trust the agent)
        if not self.valid_task_ids:
            return True

        if self.last_list_tasks_time is None:
            return True

        # Check if cache is stale
        cache_age = time.time() - self.last_list_tasks_time
        if cache_age > self.TASK_ID_CACHE_TTL:
            return True

        # Validate against cached IDs (list instead of set for pickle compatibility)
        return task_id in self.valid_task_ids

    def update_valid_task_ids(self, task_ids: list[int] | set[int]) -> None:
        """
        Update the cache of valid task IDs from a list_tasks call.

        Args:
            task_ids: List of valid task IDs from list_tasks result
        """
        # Convert to list and deduplicate for storage
        if isinstance(task_ids, set):
            self.valid_task_ids = list(task_ids)
        else:
            # Remove duplicates while preserving order
            seen = set()
            unique_ids = []
            for tid in task_ids:
                if tid not in seen:
                    seen.add(tid)
                    unique_ids.append(tid)
            self.valid_task_ids = unique_ids
        self.last_list_tasks_time = time.time()

    def get_invalid_task_ids(self, task_ids: list[int]) -> list[int]:
        """
        Filter out invalid task IDs from a list.

        Args:
            task_ids: List of task IDs to validate

        Returns:
            List of invalid task IDs (empty if all valid or cache is stale)
        """
        if not self.valid_task_ids or self.last_list_tasks_time is None:
            return []  # Cache not populated, can't validate

        # Check if cache is stale
        cache_age = time.time() - self.last_list_tasks_time
        if cache_age > self.TASK_ID_CACHE_TTL:
            return []  # Cache stale, bypass validation

        # Return IDs that are NOT in the valid list
        valid_set = set(self.valid_task_ids)
        return [tid for tid in task_ids if tid not in valid_set]

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for logging."""
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "correlation_id": self.correlation_id,
            "language_preference": self.language_preference,
            "response_language": self.response_language,
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
            # User profile fields
            user_email=data.get("user_email"),
            user_first_name=data.get("user_first_name"),
            user_last_name=data.get("user_last_name"),
            user_display_name=data.get("user_display_name"),
        )


# =============================================================================
# User Profile Fetching
# =============================================================================

async def fetch_user_profile(
    user_id: str,
    session: Any,
) -> dict[str, Any] | None:
    """
    Fetch user profile information from the database.

    This function retrieves the user's profile data including name,
    email, and timezone for use in agent context.

    Args:
        user_id: User ID from JWT 'sub' claim
        session: Database session

    Returns:
        Dictionary with user profile fields or None if user not found

    Example:
        >>> profile = await fetch_user_profile("user123", session)
        >>> profile["user_first_name"]
        "Ahsan"
    """
    try:
        from sqlalchemy import select
        from app.models import User

        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        if user:
            return {
                "user_email": user.email,
                "user_first_name": getattr(user, "first_name", None),
                "user_last_name": getattr(user, "last_name", None),
                "user_display_name": getattr(user, "display_name", None),
                "timezone": getattr(user, "timezone", "UTC"),
            }

        return None

    except Exception as e:
        # Log error but don't fail - agent can work without user profile
        import logging
        logging.warning(
            "Failed to fetch user profile for agent context",
            user_id=user_id,
            error=str(e),
        )
        return None


async def create_context_with_user_profile(
    user_id: str,
    conversation_id: str,
    correlation_id: str,
    session: Any,
    language_preference: str = "auto",
    timezone: str = "UTC",
    current_date: date | None = None,
) -> TodoContext:
    """
    Create a TodoContext with user profile information.

    This function creates a context and populates it with user profile
    data from the database for personalized agent responses.

    Args:
        user_id: User ID from JWT 'sub' claim
        conversation_id: Conversation ID
        correlation_id: Request correlation ID
        session: Database session
        language_preference: Language preference (auto, en, ur)
        timezone: User's timezone
        current_date: Current date for agent awareness

    Returns:
        TodoContext with user profile populated

    Example:
        >>> ctx = await create_context_with_user_profile(
        ...     "user123",
        ...     "conv456",
        ...     "corr789",
        ...     session,
        ...     language_preference="auto"
        ... )
        >>> ctx.user_name
        "Ahsan"
    """
    # Fetch user profile from database
    user_profile = await fetch_user_profile(user_id, session)

    # Create context with or without user profile
    context_data = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "correlation_id": correlation_id,
        "language_preference": language_preference,
        "timezone": timezone,
        "current_date": current_date,
    }

    if user_profile:
        context_data.update(user_profile)

    return TodoContext.from_dict(context_data)
