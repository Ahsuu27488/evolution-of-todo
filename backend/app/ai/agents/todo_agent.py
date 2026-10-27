"""
Todo agents using OpenAI Agents SDK.

Defines the main TodoAgent and specialized agents for:
- Planning: Weekly planning and task prioritization
- Query: Complex task searches and semantic filtering

Per spec.md FR-001 through FR-020, FR-106 through FR-113.
Per T100-T105: MCP Tool Integration with OpenAI Agents SDK.
"""

import os
from datetime import datetime
from typing import Any, Callable

# Import from openai-agents package
try:
    from agents import Agent, function_tool, handoff
    AGENT_AVAILABLE = True
except ImportError:
    # Fallback for development without the SDK installed
    Agent = object  # type: ignore

    # Create a no-op decorator that works like @function_tool
    def identity_decorator(f: Callable) -> Callable:
        """Fallback decorator that returns the function unchanged."""
        return f

    function_tool = identity_decorator  # type: ignore
    handoff = lambda *args, **kwargs: None  # type: ignore
    AGENT_AVAILABLE = False

from app.ai.utils.logging import get_logger
from app.ai.agents.prompts import (
    KAIROS_INSTRUCTIONS,
    PLANNING_INSTRUCTIONS,
    SEARCH_INSTRUCTIONS,
    localize_due_date,
)


# =============================================================================
# Logging
# =============================================================================

logger = get_logger("ai", "TodoAgents")


# =============================================================================
# MCP Tool Functions (OpenAI Agents SDK Compatible)
# =============================================================================
# Per T100-T105: Register MCP tools as @function_tool decorated functions
# These tools wrap the TaskTools class methods for agent use.
# =============================================================================


def _user_timezone() -> str | None:
    """The signed-in user's IANA time zone from the request context (users.timezone)."""
    from app.ai.agents.context import get_current_context

    context = get_current_context()
    return getattr(context, "timezone", None) if context else None


def _get_user_id_and_session(ctx: Any) -> tuple[str, Any]:
    """
    Extract user_id and session from execution context.

    Args:
        ctx: TodoContext, dict with user_id/session, or similar execution context

    Returns:
        Tuple of (user_id, session)

    Raises:
        ValueError: If context is missing required fields

    Note:
        Uses contextvars (get_current_context) because the OpenAI Agents SDK
        doesn't automatically inject context into @function_tool decorated functions.

        Handles both object format (ctx.user_id) and dict format (ctx['user_id'])
        since the agent may pass either.
    """
    from app.ai.agents.context import get_current_context

    # Method 1: Try context variable first (primary method, most reliable)
    context = get_current_context()
    logger.debug(f"[DEBUG] get_current_context() returned: {context}, user_id={context.user_id if context else None}")
    if context and context.user_id and context.session:
        logger.debug(f"[DEBUG] Using context variable: user_id={context.user_id}")
        return context.user_id, context.session

    # Method 2: Handle dict format from agent (e.g., {'user_id': 'xxx', 'session': xxx})
    if ctx and isinstance(ctx, dict):
        user_id = ctx.get("user_id")
        session = ctx.get("session")
        if user_id and user_id != "default" and session:
            return user_id, session
        # If dict has default values, continue to other methods
        if user_id == "default":
            # Agent hallucinated default values - ignore and try other methods
            pass

    # Method 3: Handle object format with attributes (backward compatibility)
    if ctx and hasattr(ctx, "user_id"):
        user_id = getattr(ctx, "user_id", None)
        session = getattr(ctx, "session", None)
        if user_id and user_id != "default" and session:
            return user_id, session

    # Method 4: Last resort - try accessing ctx as dict-like with get()
    if ctx and hasattr(ctx, "get"):
        try:
            user_id = ctx.get("user_id")
            session = ctx.get("session")
            if user_id and user_id != "default" and session:
                return user_id, session
        except (AttributeError, TypeError):
            pass

    # All methods failed - provide helpful error message
    raise ValueError(
        "Tool execution requires user_id and session in context. "
        "Ensure the TodoContext is properly set via set_context() before calling tools."
    )


def _extract_task_ids_from_result(result: Any) -> list[int]:
    """
    Extract task IDs from a tool result.

    This helper function extracts all task IDs from list_tasks or semantic_search
    results, making them available for the agent to use in subsequent operations.

    Args:
        result: ToolResponse from MCP tool

    Returns:
        List of task IDs (empty list if none found)

    Example:
        >>> result = ToolResponse(status="success", data=[{"task_id": 123}, ...])
        >>> _extract_task_ids_from_result(result)
        [123]
    """
    from app.ai.mcp.tools import ToolResponse

    task_ids = []

    if isinstance(result, ToolResponse) and result.status == "success":
        if isinstance(result.data, list):
            for item in result.data:
                if isinstance(item, dict):
                    # Try both task_id and id fields
                    task_id = item.get("task_id") or item.get("id")
                    if isinstance(task_id, int):
                        task_ids.append(task_id)
                    elif isinstance(task_id, str) and task_id.isdigit():
                        task_ids.append(int(task_id))

    return task_ids


def _format_tool_result(result: Any, tool_name: str) -> str:
    """
    Format ToolResponse for agent consumption.

    Args:
        result: ToolResponse from MCP tool
        tool_name: Name of the tool that was called

    Returns:
        Formatted string message for the agent
    """
    from app.ai.mcp.tools import ToolResponse

    if not isinstance(result, ToolResponse):
        return str(result)

    if result.status == "success":
        logger.info(
            "MCP tool success",
            tool_name=tool_name,
        )
        if isinstance(result.data, list):
            items = result.data
            if items:
                # Format task list for agent
                # IMPORTANT: Do NOT truncate - agent needs to see ALL tasks for "delete all" operations
                # The agent instructions say "For 'delete all tasks': FIRST call list_tasks, THEN delete each returned task"
                # If we truncate, the agent will only delete the visible tasks, not all tasks!
                formatted_items = []
                for item in items:  # Show ALL items - no truncation
                    if isinstance(item, dict):
                        title = item.get("title", "")
                        task_id = item.get("task_id", item.get("id", ""))
                        completed = item.get("completed", False)
                        status = "✓" if completed else "○"
                        formatted_items.append(f"{status} [{task_id}] {title}")
                output = "\n".join(formatted_items) if formatted_items else result.message

                # Add explicit task ID summary for LLM parsing
                # This helps the agent extract IDs more reliably
                task_ids = _extract_task_ids_from_result(result)
                if task_ids and len(task_ids) > 1:
                    output += f"\n\nTASK_IDS: {','.join(map(str, task_ids))}"
                    output += f"\nUse these exact IDs for complete_task/delete_task: {', '.join(map(str, task_ids))}"

                return output
            return f"Found {len(items)} items. {result.message}"
        return result.message or f"Operation completed: {tool_name}"
    else:
        logger.warning(
            "MCP tool error",
            tool_name=tool_name,
            error=result.error,
        )
        return f"Error: {result.error or result.message}"


if AGENT_AVAILABLE:

    @function_tool(strict_mode=False)
    async def add_task(
        ctx: Any,
        title: str,
        description: str | None = None,
        priority: str = "MEDIUM",
        due_date: str | None = None,
        tags: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Add a new task for the user.

        Args:
            ctx: Execution context with user_id and session
            title: Task title (required)
            description: Optional task description
            priority: Task priority - HIGH, MEDIUM, or LOW (default: MEDIUM)
            due_date: Optional due date in ISO format or relative terms
            tags: Optional list of tags with name and color

        Returns:
            Success message with task ID or error message

        Examples:
            add_task(ctx, "Buy groceries")
            add_task(ctx, "Meeting", priority="HIGH", due_date="2025-01-15")
        """
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                try:
                    # No offset in the value means the user's local time, not UTC
                    parsed_due_date = localize_due_date(due_date, _user_timezone())
                except ValueError:
                    return (
                        f"Error: due_date '{due_date}' is not ISO 8601. Resolve it against the current "
                        "time and send e.g. 2026-10-30T10:00:00+05:00."
                    )

            # Use default autocommit=False to allow parallel tool calls
            # The HTTP route handler commits the session after all tools complete
            tools = TaskTools(session)
            result = await tools.add_task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
                tags=tags,
            )

            return _format_tool_result(result, "add_task")

        except Exception as e:
            logger.error("add_task exception", error=str(e))
            return f"Error adding task: {str(e)}"


    @function_tool(strict_mode=False)
    async def list_tasks(
        ctx: Any,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """
        List tasks with optional filters.

        Args:
            ctx: Execution context with user_id and session
            status: Filter by status - 'pending', 'completed', or 'all' (default: all)
            limit: Maximum number of tasks to return (default: 50)
            offset: Number of tasks to skip for pagination (default: 0)

        Returns:
            Formatted list of tasks or error message

        Examples:
            list_tasks(ctx)  # All tasks
            list_tasks(ctx, status="pending")  # Only pending tasks

        IMPORTANT: The task IDs returned here are the ONLY valid IDs for complete_task
        and delete_task. Always use the exact IDs shown in brackets.
        """
        from app.ai.agents.context import get_current_context
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

            tools = TaskTools(session)
            result = await tools.list_tasks(
                user_id=user_id,
                status=status,
                limit=limit,
                offset=offset,
            )

            # Cache valid task IDs in context for validation by complete_task/delete_task
            # This prevents the agent from hallucinating non-existent task IDs
            if result.status == "success" and isinstance(result.data, list):
                task_ids = [item.get("task_id") for item in result.data if item.get("task_id")]
                if task_ids:
                    context = get_current_context()
                    if context:
                        context.update_valid_task_ids(task_ids)
                        logger.debug(
                            "Cached valid task IDs",
                            task_count=len(task_ids),
                            task_ids=task_ids[:10],  # Log first 10
                        )

            return _format_tool_result(result, "list_tasks")

        except Exception as e:
            logger.error("list_tasks exception", error=str(e))
            return f"Error listing tasks: {str(e)}"


    @function_tool(strict_mode=False)
    async def complete_task(
        ctx: Any,
        task_id: int,
    ) -> str:
        """
        Mark a task as complete.

        CRITICAL: Before calling this tool, you MUST obtain valid task_id from
        list_tasks or semantic_search. NEVER make up or guess task IDs.

        Args:
            ctx: Execution context with user_id and session
            task_id: ID of the task to mark complete (must be from list_tasks result)

        Returns:
            Success message or error message

        Examples:
            complete_task(ctx, 123)  # where 123 came from list_tasks result
        """
        from app.ai.agents.context import get_current_context
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

            # Validate task ID against cached list_tasks results
            # This prevents the agent from hallucinating non-existent task IDs
            context = get_current_context()
            if context and not context.is_task_id_valid(task_id):
                # Task ID is not in the valid list - provide helpful error
                if context.valid_task_ids:
                    valid_ids = sorted(list(context.valid_task_ids))
                    logger.warning(
                        "Agent attempted to use invalid task ID - validation caught it",
                        attempted_id=task_id,
                        valid_ids=valid_ids,
                        user_id=user_id,
                    )
                    return (
                        f"Error: Task ID {task_id} is not valid. "
                        f"Please use one of these valid task IDs from list_tasks: {valid_ids}. "
                        f"ALWAYS call list_tasks FIRST to get the current valid task IDs before completing tasks."
                    )
                # Cache is stale or empty, proceed with validation at database level
                logger.warning(
                    "Task ID validation skipped - cache stale or empty",
                    task_id=task_id,
                    cache_size=len(context.valid_task_ids) if context else 0,
                )

            # Use default autocommit=False to allow parallel tool calls
            # The HTTP route handler commits the session after all tools complete
            tools = TaskTools(session)
            result = await tools.complete_task(
                user_id=user_id,
                task_id=task_id,
            )

            return _format_tool_result(result, "complete_task")

        except Exception as e:
            logger.error("complete_task exception", error=str(e))
            return f"Error completing task: {str(e)}"


    @function_tool(strict_mode=False)
    async def delete_task(
        ctx: Any,
        task_id: int,
    ) -> str:
        """
        Delete a task permanently.

        CRITICAL: Before calling this tool, you MUST obtain valid task_id from
        list_tasks or semantic_search. NEVER make up or guess task IDs.

        Args:
            ctx: Execution context with user_id and session
            task_id: ID of the task to delete (must be from list_tasks result)

        Returns:
            Success message or error message

        Examples:
            delete_task(ctx, 123)  # where 123 came from list_tasks result
        """
        from app.ai.agents.context import get_current_context
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

            # Validate task ID against cached list_tasks results
            # This prevents the agent from hallucinating non-existent task IDs
            context = get_current_context()
            if context and not context.is_task_id_valid(task_id):
                # Task ID is not in the valid list - provide helpful error
                if context.valid_task_ids:
                    valid_ids = sorted(list(context.valid_task_ids))
                    logger.warning(
                        "Agent attempted to use invalid task ID - validation caught it",
                        attempted_id=task_id,
                        valid_ids=valid_ids,
                        user_id=user_id,
                    )
                    return (
                        f"Error: Task ID {task_id} is not valid. "
                        f"Please use one of these valid task IDs from list_tasks: {valid_ids}. "
                        f"ALWAYS call list_tasks FIRST to get the current valid task IDs before deleting tasks."
                    )
                # Cache is stale or empty, proceed with validation at database level
                logger.warning(
                    "Task ID validation skipped - cache stale or empty",
                    task_id=task_id,
                    cache_size=len(context.valid_task_ids) if context else 0,
                )

            # Use default autocommit=False to allow parallel tool calls
            # The HTTP route handler commits the session after all tools complete
            tools = TaskTools(session)
            result = await tools.delete_task(
                user_id=user_id,
                task_id=task_id,
            )

            return _format_tool_result(result, "delete_task")

        except Exception as e:
            logger.error("delete_task exception", error=str(e))
            return f"Error deleting task: {str(e)}"


    @function_tool(strict_mode=False)
    async def update_task(
        ctx: Any,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        tags: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Update an existing task's properties.

        Args:
            ctx: Execution context with user_id and session
            task_id: ID of the task to update
            title: New title for the task
            description: New description for the task
            priority: New priority - HIGH, MEDIUM, or LOW
            due_date: New due date in ISO format
            tags: List of tags with name and color - IMPORTANT: Extract tags from user input!

        Returns:
            Success message with updated task or error message

        Examples:
            update_task(ctx, 123, priority="HIGH")
            update_task(ctx, 123, title="New title", description="New description")
            update_task(ctx, 123, tags=[{"name": "urgent", "color": "#ef4444"}])
        """
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

            # Parse due_date if provided
            parsed_due_date = None
            if due_date:
                try:
                    # No offset in the value means the user's local time, not UTC
                    parsed_due_date = localize_due_date(due_date, _user_timezone())
                except ValueError:
                    return (
                        f"Error: due_date '{due_date}' is not ISO 8601. Resolve it against the current "
                        "time and send e.g. 2026-10-30T10:00:00+05:00."
                    )

            # Use default autocommit=False to allow parallel tool calls
            # The HTTP route handler commits the session after all tools complete
            tools = TaskTools(session)
            result = await tools.update_task(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
                tags=tags,
            )

            return _format_tool_result(result, "update_task")

        except Exception as e:
            logger.error("update_task exception", error=str(e))
            return f"Error updating task: {str(e)}"


    @function_tool(strict_mode=False)
    async def get_task(
        ctx: Any,
        task_id: int,
    ) -> str:
        """
        Get details of a specific task.

        Args:
            ctx: Execution context with user_id and session
            task_id: ID of the task to retrieve

        Returns:
            Formatted task details or error message

        Examples:
            get_task(ctx, 123)
        """
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

            tools = TaskTools(session)
            result = await tools.get_task(
                user_id=user_id,
                task_id=task_id,
            )

            if result.status == "success" and result.data:
                task = result.data
                return (
                    f"Task {task['task_id']}: {task['title']}\n"
                    f"Description: {task.get('description', 'None')}\n"
                    f"Priority: {task['priority']}\n"
                    f"Status: {'Completed' if task['completed'] else 'Pending'}\n"
                    f"Due: {task.get('due_date', 'Not set')}"
                )
            return _format_tool_result(result, "get_task")

        except Exception as e:
            logger.error("get_task exception", error=str(e))
            return f"Error getting task: {str(e)}"


    @function_tool(strict_mode=False)
    async def semantic_search(
        ctx: Any,
        query: str,
        limit: int = 10,
    ) -> str:
        """
        Search tasks by meaning using vector embeddings.

        This tool finds tasks that are semantically similar to the query,
        not just matching exact words. Use it for natural language searches
        like "grocery items", "work tasks", "urgent things".

        Args:
            ctx: Execution context with user_id and session
            query: Natural language search query
            limit: Maximum number of results (default: 10)

        Returns:
            Formatted search results or error message

        Examples:
            semantic_search(ctx, "grocery shopping")
            semantic_search(ctx, "urgent work tasks")
            semantic_search(ctx, "خریداری")  # Urdu for shopping

        IMPORTANT: The task IDs returned here are valid for complete_task
        and delete_task. Always use the exact IDs shown in brackets.
        """
        from app.ai.agents.context import get_current_context
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

            tools = TaskTools(session)
            result = await tools.semantic_search(
                user_id=user_id,
                query=query,
                limit=limit,
            )

            if result.status == "success" and result.data:
                items = result.data
                if items:
                    formatted = []
                    task_ids = []
                    for item in items:  # Show ALL results, not just first 10
                        score = item.get("score", 0)
                        title = item.get("title", "")
                        task_id = item.get("task_id", item.get("id", ""))
                        formatted.append(f"[{task_id}] (relevance: {score:.2f}) {title}")
                        task_ids.append(task_id)
                    # Cache found task IDs for validation
                    context = get_current_context()
                    if context and task_ids:
                        context.update_valid_task_ids(task_ids)
                        logger.debug(
                            "Cached valid task IDs from semantic_search",
                            task_count=len(task_ids),
                            query=query[:50],
                        )
                    output = "Similar tasks:\n" + "\n".join(formatted)

                    # Add explicit task ID summary for LLM parsing
                    if len(task_ids) > 1:
                        output += f"\n\nTASK_IDS: {','.join(map(str, task_ids))}"
                        output += f"\nUse these exact IDs for complete_task/delete_task: {', '.join(map(str, task_ids))}"

                    return output
                return "No similar tasks found."
            return _format_tool_result(result, "semantic_search")

        except Exception as e:
            logger.error("semantic_search exception", error=str(e))
            return f"Error searching tasks: {str(e)}"


    # =============================================================================
    # Tools List for Agent Registration
    # =============================================================================

    MCP_TOOLS = [
        add_task,
        list_tasks,
        complete_task,
        delete_task,
        update_task,
        get_task,
        semantic_search,
    ]

else:
    # Fallback when SDK is not installed
    MCP_TOOLS = []
    add_task = None
    list_tasks = None
    complete_task = None
    delete_task = None
    update_task = None
    get_task = None
    semantic_search = None


# =============================================================================
# Specialized Agents
# =============================================================================

def create_planning_agent() -> Agent:
    """
    Create the Planning agent for weekly planning and task prioritization.

    Per FR-108: PlanningAgent specializes in weekly planning.
    Per T100-T105: Agent has access to MCP tools for task operations.

    This agent handles:
    - Weekly task planning and scheduling
    - Task prioritization by urgency and importance
    - Identifying scheduling conflicts
    - Recommending optimal task order

    Returns:
        Configured Planning Agent with MCP tools
    """
    if Agent is None:
        logger.warning("OpenAI Agents SDK not installed, returning None")
        return None

    return Agent(
        name="PlanningAgent",
        instructions=PLANNING_INSTRUCTIONS,
        handoff_description=(
            "Planning mode: weekly or daily plans, what to do first, overloaded days. "
            "Internal; the user only ever talks to Kairos."
        ),
        tools=MCP_TOOLS if MCP_TOOLS else [],
    )


def create_query_agent() -> Agent:
    """
    Create the Query agent for complex task searches and filtering.

    Per FR-109: QueryAgent specializes in complex searches.
    Per T066: Use semantic_search for natural language queries.
    Per T100-T105: Agent has access to MCP tools for task operations.

    This agent handles:
    - Semantic task search using vector embeddings
    - Complex filtering queries
    - Multi-criteria task searches
    - Task discovery and exploration

    Returns:
        Configured Query Agent with MCP tools
    """
    if Agent is None:
        logger.warning("OpenAI Agents SDK not installed, returning None")
        return None

    return Agent(
        name="QueryAgent",
        instructions=SEARCH_INSTRUCTIONS,
        handoff_description=(
            "Search mode: find tasks by topic, meaning or several criteria. "
            "Internal; the user only ever talks to Kairos."
        ),
        tools=MCP_TOOLS if MCP_TOOLS else [],
    )


# =============================================================================
# Main Todo Agent
# =============================================================================

def create_todo_agent(
    planning_agent: Agent = None,
    query_agent: Agent = None,
) -> Agent:
    """
    Create the main TodoAgent with handoffs to specialists.

    Per FR-001 through FR-010: Main agent for natural language task management.
    Per T100-T105: Agent has access to MCP tools for task operations.

    This agent handles:
    - Natural language task creation
    - Task status updates (complete/uncomplete)
    - Task modifications
    - Basic task listing
    - Handoffs to PlanningAgent and QueryAgent

    Args:
        planning_agent: Optional pre-configured Planning agent
        query_agent: Optional pre-configured Query agent

    Returns:
        Configured Todo Agent with handoffs and MCP tools
    """
    if Agent is None:
        logger.warning("OpenAI Agents SDK not installed, returning None")
        return None

    # Create specialists if not provided
    if planning_agent is None:
        planning_agent = create_planning_agent()
    if query_agent is None:
        query_agent = create_query_agent()

    return Agent(
        name="Kairos",
        instructions=KAIROS_INSTRUCTIONS,
        handoffs=[planning_agent, query_agent],
        tools=MCP_TOOLS if MCP_TOOLS else [],
    )


# =============================================================================
# Global Agent Instances (Lazy)
# =============================================================================

_planning_agent: "Agent | None" = None
_query_agent: "Agent | None" = None
_todo_agent: "Agent | None" = None


def get_planning_agent() -> "Agent | None":
    """Get or create the global Planning agent instance."""
    global _planning_agent
    if _planning_agent is None:
        _planning_agent = create_planning_agent()
    return _planning_agent


def get_query_agent() -> "Agent | None":
    """Get or create the global Query agent instance."""
    global _query_agent
    if _query_agent is None:
        _query_agent = create_query_agent()
    return _query_agent


def get_todo_agent() -> "Agent | None":
    """Get or create the global Todo agent instance."""
    global _todo_agent
    if _todo_agent is None:
        _todo_agent = create_todo_agent(
            planning_agent=get_planning_agent(),
            query_agent=get_query_agent(),
        )
    return _todo_agent


def reset_todo_agent() -> "Agent | None":
    """
    Force recreate the Todo agent instance.

    Use this after updating agent instructions to ensure the new
    instructions are used. This is primarily useful during development
    when using StatReload, as the global _todo_agent cache would
    otherwise hold the old agent with old instructions.

    Returns:
        Newly created Todo Agent
    """
    global _todo_agent
    _todo_agent = None  # Clear cache
    return get_todo_agent()  # Create fresh with new instructions


# Export for convenience
planning_agent = get_planning_agent
query_agent = get_query_agent
todo_agent = get_todo_agent

# Export MCP tools for direct access if needed
__all__ = [
    "get_todo_agent",
    "get_planning_agent",
    "get_query_agent",
    "create_todo_agent",
    "create_planning_agent",
    "create_query_agent",
    "MCP_TOOLS",
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
    "get_task",
    "semantic_search",
]
