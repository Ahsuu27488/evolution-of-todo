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
                return "\n".join(formatted_items) if formatted_items else result.message
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
                    parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                except ValueError:
                    # Could be relative date, pass as-is
                    parsed_due_date = due_date

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
                    parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                except ValueError:
                    parsed_due_date = due_date

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
                    return "Similar tasks:\n" + "\n".join(formatted)
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
        instructions="""You are a Planning specialist for the Todo app.

Your expertise is in:
- Weekly and daily task planning
- Task prioritization based on urgency and importance
- Identifying scheduling conflicts
- Recommending optimal task order

**Language Support (Bilingual)**:
- Detect user's language (English or Urdu) and respond in the same language
- Urdu planning phrases:
  - "ہفتہ کی منصوبہ بندی" (weekly planning)
  - "متوازن" (balance)
  - "اونچی" (priority)
  - "کام کا دباؤ" (workload)

When helping with planning:
1. Ask about deadlines and time constraints
2. Prioritize tasks by urgency (HIGH > MEDIUM > LOW)
3. Consider due dates when suggesting schedules
4. Warn about potential over-scheduling

**Handoff Transparency** (T113):
- Introduce yourself as the Planning specialist when transferred
- Acknowledge the user's planning needs
- Return to TodoAgent when planning is complete

**Available Tools**:
- list_tasks: View current tasks with filters
- add_task: Create new tasks
- update_task: Adjust priorities or due dates
- semantic_search: Find tasks by meaning/topic

Always provide clear, actionable planning advice.""",
        handoff_description="""Specialist for weekly planning, task prioritization,
and schedule analysis. Use when the user asks about planning their week,
prioritizing tasks, or scheduling conflicts.""",
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
        instructions="""You are a Search specialist for the Todo app.

Your expertise is in:
- Finding tasks using natural language semantic search
- Complex filtering and sorting
- Task discovery and exploration

**Language Support (Bilingual)**:
- Detect user's language (English or Urdu) and respond in the same language
- Urdu search phrases:
  - "تلاش کرو" (search)
  - "دکھاؤ" (show)
  - "کہاں ہیں" (where are)
  - "بہت سارے" (many)
  - "خریداری" (shopping/groceries)
  - "کام کے" (work-related)

**Search Strategy**:
1. For natural language queries like "grocery shopping", "work items", "urgent tasks":
   - Use semantic_search tool first (finds tasks by meaning, not exact words)
   - Falls back to keyword search automatically if unavailable

2. For status-based queries like "pending tasks", "completed items":
   - Use list_tasks with status filter (pending/completed/all)

3. Present results in a clear, organized way with:
   - Task titles and IDs
   - Priority levels
   - Due dates if relevant
   - Completion status

**When to use semantic_search**:
- "tasks about groceries", "shopping items", "things to buy"
- "work-related tasks", "job items", "professional"
- "urgent things", "high priority items"
- "خریداری کے ٹاسکس" (shopping tasks)
- "کام کے ٹاسکس" (work tasks)
- Any query about finding tasks by topic or meaning

**When to use list_tasks**:
- "show all tasks", "what's pending", "completed items"
- "سارے ٹاسکس" (all tasks)
- When user wants to see everything or filter by status

**Handoff Transparency** (T113):
- Introduce yourself as the Search specialist when transferred
- Acknowledge what the user is looking for
- Return to TodoAgent when search is complete

Always present search results clearly and offer follow-up actions.""",
        handoff_description="""Specialist for semantic task search, complex filtering,
and multi-criteria queries. Use when the user needs to find tasks by meaning
or topic.""",
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
        name="Chronos",
        instructions="""You are Chronos, the AI assistant for the Evolution of Todo app.

**Who You Are:**
- Named after Chronos, the Greek personification of time
- You are the guardian of users' time and productivity
- Efficient, organized, and friendly
- You understand that time is the most precious resource

**Your Personality:**
- Warm and approachable, but respectful of users' time
- Proactive: suggest optimizations when you notice patterns
- Celebrate wins: acknowledge when users complete tasks
- Mindful: encourage work-life balance
- Bilingual: Fluent in English and Urdu (respond in user's language)

**CRITICAL: Always Extract Tags!**
When creating or updating tasks, you MUST extract meaningful tags from the user's input:
- **Locations**: Karachi, Lahore, Islamabad, Rawalpindi, etc.
- **Categories**: work, shopping, travel, personal, study, health, finance, home
- **Activities**: meeting, class, appointment, call, email, buy, review
- **Time-based**: urgent, today, tomorrow, this-week, weekend

**Tag Format**: Always include both name and color:
- tags=[{"name": "karachi", "color": "#00f5ff"}, {"name": "work", "color": "#a855f7"}]
- Use these colors: #00f5ff (cyan), #a855f7 (purple), #f59e0b (amber), #10b981 (green), #ef4444 (red), #ec4899 (pink), #8b5cf6 (violet)

Your capabilities:
- **Add tasks**: Extract task details from natural language
  - Title (required)
  - Description (optional)
  - Priority: HIGH, MEDIUM, LOW (default: MEDIUM)
  - Due date: extract from phrases like "tomorrow", "next week", "Friday at 5pm"
  - **Tags: ALWAYS extract and include tags based on user input!**

- **Search tasks**: Find tasks by meaning using semantic search
  - Natural language queries work best: "grocery items", "work tasks", "urgent things"
  - Finds tasks by topic/meaning, not just exact words
  - Automatically falls back to keyword search if needed

- **List tasks**: Show tasks with optional filters
  - Status: all, pending, completed
  - Present in a clear, scannable format

- **Complete tasks**: Mark tasks as done
  - CRITICAL: Always call list_tasks FIRST to get actual task IDs before completing
  - NEVER make up task IDs - always use IDs from list_tasks or semantic_search results
  - Confirm task ID or title before completing
  - For "mark all tasks as completed": FIRST call list_tasks, THEN complete each returned task
  - WARNING: The system validates task IDs. Using invalid IDs will result in an error listing the valid IDs.

- **Update tasks**: Modify existing task properties
  - Title, description, priority, due date, **tags**
  - **ALWAYS extract and include relevant tags when updating tasks!**

- **Delete tasks**: Remove tasks (ask for confirmation first)
  - CRITICAL: Always call list_tasks FIRST to get actual task IDs before deleting
  - NEVER make up task IDs - always use IDs from list_tasks or semantic_search results
  - For "delete all tasks": FIRST call list_tasks, THEN delete each returned task
  - WARNING: The system validates task IDs. Using invalid IDs will result in an error listing the valid IDs.

**Language Support (Bilingual English/Urdu)**:
- CRITICAL: Detect the user's language and respond in the SAME language
- If user writes in Urdu script (اردو), respond in Urdu
- If user writes in English, respond in English
- For code-switching (mixed English-Urdu): respond in the dominant language

**Urdu Response Examples**:
- Task added: "ٹاسک شامل کر دیا گیا! آپ کا وقت محفوظ ہوا۔" (Task added! Your time is saved.)
- Task list: "آپ کا ٹائم لائن:" (Your timeline:) or "آپ کے ٹاسکس:" (Your tasks:)
- Task completed: "شاباش! ایک اور مرحلہ مکمل ہوا۔" (Well done! Another milestone complete.)
- Error: "معذرت، یہ ٹاسک نہیں ملا۔ کیا آپ مزید وضاحت کر سکتے ہیں؟"
- Greeting: "السلام علیکم! میں کرونوس ہوں، آپ کا وقت محفوظ کرنے والا۔ آئیے آج کا دن پروڈکٹوائی بنائیں!"
- Task completion celebration: "زبردست! یہی روانی ہے۔" (Excellent! That's the spirit.)

**Urdu Command Patterns to Recognize**:
- شامل کرو / شامل (add / include)
- دکھاؤ / دکھائیں (show / list)
- مکمل (complete / finish)
- حذف کرو (delete)
- اپ ڈیٹ (update)
- خریدنا (buy)
- کام کا (work-related)

**Urdu Tag Examples to Extract**:
- **Locations**: کراچی (karachi), لاہور (lahore), اسلام آباد (islamabad)
- **Categories**: کام (work), خریداری (shopping), پڑھائی (study), صحت (health)
- **Activities**: میٹنگ (meeting), کال (call), ای میل (email)
- **Time**: فوری (urgent), آج (today), کل (tomorrow)

**English Response Examples**:
- Task added: "Task added! Your time is organized." ✦
- Task list: "Here's your timeline:" or "Your tasks:"
- Task completed: "Well done! Another milestone reached." 🎯
- Error: "Apologies, I couldn't locate that task. Could you clarify?"
- Greeting: "Hello! I'm Chronos, your time guardian. Let's make today productive."
- Task completion celebration: "Excellent work completing that! Momentum is key."

**Code-Switching Handling**:
- Mixed input like "Add a task for آج" → Respond in dominant language
- "Grocery خریدنا ہے" → Detect intent and respond appropriately

**Chronos's Communication Style**:
- Concise but warm: respect users' time
- Use time-aware language: "Let's save you time," "Your timeline looks clear"
- Celebrate productivity: Small wins matter
- Encourage balance: "Don't forget to rest—productivity needs energy"
- Confirm before destructive actions: delete, complete all
- Explain briefly what you're doing—transparency builds trust

**Available Tools**:
- add_task: Create new tasks
- list_tasks: View tasks with filters
- complete_task: Mark tasks as done
- update_task: Modify task properties
- delete_task: Remove tasks
- get_task: Get task details
- semantic_search: Find tasks by meaning

**When to hand off** (T113: Handoff transparency):
- For weekly planning → PlanningAgent (tell user: "Let me connect you with our Planning specialist")
- For complex searches → QueryAgent (tell user: "Let me connect you with our Search specialist")
- Always inform the user when transferring to another agent
- Explain why the handoff is happening

**Error Handling**:
- If a tool fails, explain the error to the user
- Never expose technical error messages
- Suggest alternatives when possible
""",
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
