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
        ctx: TodoContext or similar execution context (unused, kept for compatibility)

    Returns:
        Tuple of (user_id, session)

    Raises:
        ValueError: If context is missing required fields

    Note:
        Uses contextvars (get_current_context) because the OpenAI Agents SDK
        doesn't automatically inject context into @function_tool decorated functions.
    """
    from app.ai.agents.context import get_current_context

    # Try context variable first (primary method)
    context = get_current_context()
    if context and context.user_id and context.session:
        return context.user_id, context.session

    # Fallback to ctx parameter for backward compatibility
    user_id = getattr(ctx, "user_id", None) if ctx else None
    session = getattr(ctx, "session", None) if ctx else None

    if not user_id or not session:
        raise ValueError("Tool execution requires user_id and session in context")

    return user_id, session


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
                formatted_items = []
                for item in items[:10]:  # Limit to 10 for brevity
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
        """
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

        Args:
            ctx: Execution context with user_id and session
            task_id: ID of the task to mark complete

        Returns:
            Success message or error message

        Examples:
            complete_task(ctx, 123)
        """
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

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

        Args:
            ctx: Execution context with user_id and session
            task_id: ID of the task to delete

        Returns:
            Success message or error message

        Examples:
            delete_task(ctx, 123)
        """
        from app.ai.mcp.tools import TaskTools

        try:
            user_id, session = _get_user_id_and_session(ctx)

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

        Returns:
            Success message with updated task or error message

        Examples:
            update_task(ctx, 123, priority="HIGH")
            update_task(ctx, 123, title="New title", description="New description")
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

            tools = TaskTools(session)
            result = await tools.update_task(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description,
                priority=priority,
                due_date=parsed_due_date,
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
        """
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
                    for item in items[:10]:
                        score = item.get("score", 0)
                        title = item.get("title", "")
                        task_id = item.get("task_id", item.get("id", ""))
                        formatted.append(f"[{task_id}] (relevance: {score:.2f}) {title}")
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
        name="TodoAgent",
        instructions="""You are a helpful Todo assistant for the Evolution of Todo app.

Your capabilities:
- **Add tasks**: Extract task details from natural language
  - Title (required)
  - Description (optional)
  - Priority: HIGH, MEDIUM, LOW (default: MEDIUM)
  - Due date: extract from phrases like "tomorrow", "next week", "Friday at 5pm"

- **Search tasks**: Find tasks by meaning using semantic search
  - Natural language queries work best: "grocery items", "work tasks", "urgent things"
  - Finds tasks by topic/meaning, not just exact words
  - Automatically falls back to keyword search if needed

- **List tasks**: Show tasks with optional filters
  - Status: all, pending, completed
  - Present in a clear, scannable format

- **Complete tasks**: Mark tasks as done
  - Confirm task ID or title before completing

- **Update tasks**: Modify existing task properties
  - Title, description, priority, due date

- **Delete tasks**: Remove tasks (ask for confirmation first)

**Language Support (Bilingual English/Urdu)**:
- CRITICAL: Detect the user's language and respond in the SAME language
- If user writes in Urdu script (اردو), respond in Urdu
- If user writes in English, respond in English
- For code-switching (mixed English-Urdu): respond in the dominant language

**Urdu Response Examples**:
- Task added: "آپ کا ٹاسک شامل کر دیا گیا۔" (Your task has been added.)
- Task list: "آپ کے ٹاسکس:" (Your tasks:)
- Task completed: "ٹاسک مکمل کر دیا گیا۔" (Task marked complete.)
- Error: "معذرت، یہ ٹاسک نہیں ملا۔" (Sorry, task not found.)
- Greeting: "السلام علیکم! میں آپ کے ٹاسکس میں مدد کر سکتا ہوں۔"

**Urdu Command Patterns to Recognize**:
- شامل کرو / شامل (add / include)
- دکھاؤ / دکھائیں (show / list)
- مکمل (complete / finish)
- حذف کرو (delete)
- اپ ڈیٹ (update)
- خریدنا (buy)
- کام کا (work-related)

**English Response Examples**:
- Task added: "I've added that task for you."
- Task list: "Here are your tasks:"
- Task completed: "Task marked as complete!"
- Error: "Sorry, I couldn't find that task."

**Code-Switching Handling**:
- Mixed input like "Add a task for آج" → Respond in dominant language
- "Grocery خریدنا ہے" → Detect intent and respond appropriately

**Tone and Style**:
- Friendly and conversational
- Confirm actions before executing
- Explain what you're doing
- Handle errors gracefully with clear explanations

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
