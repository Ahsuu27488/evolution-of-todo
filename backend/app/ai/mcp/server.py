"""
MCP server instance for Phase III.

This module creates the in-process MCP server that exposes
task management tools to the AI agent.

Per spec.md FR-021 through FR-030.
Per T103: Tool timeout handling with 30-second limit.

The server uses streamable-http transport for integration with
the FastAPI application.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.utils.logging import get_logger
from app.ai.mcp.tools import TaskTools


# =============================================================================
# MCP Server Configuration
# =============================================================================

mcp_server = Server("todo-task-manager")


# =============================================================================
# Tool Definitions
# =============================================================================

TOOLS: list[Tool] = [
    Tool(
        name="add_task",
        description="Create a new task. IMPORTANT: Extract meaningful tags from user input including locations (Karachi, Lahore, etc.), categories (work, shopping, travel, personal, study), activities (meeting, class, appointment), and action items (buy, call, email). Tags help organize and find tasks later.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID from JWT",
                },
                "title": {
                    "type": "string",
                    "description": "Task title",
                },
                "description": {
                    "type": "string",
                    "description": "Optional task description",
                },
                "priority": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW"],
                    "description": "Task priority (default: MEDIUM)",
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in ISO format (optional)",
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Tag name (e.g., 'karachi', 'work', 'shopping')"},
                            "color": {"type": "string", "description": "Hex color code (e.g., '#00f5ff' for cyan, '#a855f7' for purple)"},
                        },
                        "required": ["name", "color"],
                    },
                    "description": "Extracted tags from user input. Include locations, categories, and activities. Use these colors: #00f5ff (cyan), #a855f7 (purple), #f59e0b (amber), #10b981 (green), #ef4444 (red).",
                },
            },
            "required": ["user_id", "title"],
        },
    ),
    Tool(
        name="list_tasks",
        description="List tasks for the user with optional filters",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID from JWT",
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by completion status",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results to return (default: 50)",
                },
                "offset": {
                    "type": "integer",
                    "description": "Pagination offset (default: 0)",
                },
            },
            "required": ["user_id"],
        },
    ),
    Tool(
        name="complete_task",
        description="Mark a task as complete",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID from JWT",
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to mark complete",
                },
            },
            "required": ["user_id", "task_id"],
        },
    ),
    Tool(
        name="delete_task",
        description="Delete a task",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID from JWT",
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to delete",
                },
            },
            "required": ["user_id", "task_id"],
        },
    ),
    Tool(
        name="update_task",
        description="Update an existing task",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID from JWT",
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to update",
                },
                "title": {
                    "type": "string",
                    "description": "New task title",
                },
                "description": {
                    "type": "string",
                    "description": "New task description",
                },
                "priority": {
                    "type": "string",
                    "enum": ["HIGH", "MEDIUM", "LOW"],
                    "description": "New task priority",
                },
                "due_date": {
                    "type": "string",
                    "description": "New due date in ISO format",
                },
            },
            "required": ["user_id", "task_id"],
        },
    ),
    Tool(
        name="get_task",
        description="Get a single task by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID from JWT",
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to retrieve",
                },
            },
            "required": ["user_id", "task_id"],
        },
    ),
    Tool(
        name="semantic_search",
        description="Search tasks by semantic meaning using vector embeddings. Use this when the user asks to find tasks by meaning, topic, or intent (not just exact keyword matches). For example: 'tasks about groceries', 'things I need to buy', 'work-related items', 'urgent tasks'. Falls back to keyword search if vector search is unavailable.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User ID from JWT",
                },
                "query": {
                    "type": "string",
                    "description": "Natural language search query - describe what you're looking for in plain English",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results to return (default: 10)",
                },
            },
            "required": ["user_id", "query"],
        },
    ),
]


# =============================================================================
# Tool Handlers
# =============================================================================

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return TOOLS


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle MCP tool calls from the AI agent.

    This function is called by the OpenAI Agents SDK when the agent
    needs to invoke a tool.

    Per FR-030: Tool errors MUST be caught by AI agent and explained to user.

    Args:
        name: Tool name to invoke
        arguments: Tool parameters

    Returns:
        Tool response as TextContent

    Example:
        result = await call_tool("add_task", {"user_id": "123", "title": "Buy groceries"})
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    logger = get_logger("mcp", "server")

    logger.info(
        "MCP tool call received",
        tool_name=name,
        arguments_keys=list(arguments.keys()),
    )

    # Get database session from context if available
    # The chat route handler sets this in the request state
    session: AsyncSession | None = arguments.pop("_session", None)

    if not session:
        # Create a temporary session for this tool call
        from app.db import get_session

        async with get_session() as temp_session:
            return await _execute_tool_call(name, arguments, temp_session, logger)

    return await _execute_tool_call(name, arguments, session, logger)


async def _execute_tool_call(
    name: str,
    arguments: dict,
    session: AsyncSession,
    logger,
) -> list[TextContent]:
    """
    Execute the actual tool call with a valid session.

    Per T103: Tool timeout handling with 30-second limit.
    """

    tools = TaskTools(session)
    TOOL_TIMEOUT = 30.0  # seconds per spec.md T103

    # Route to appropriate tool method with timeout
    try:
        match name:
            case "add_task":
                response = await asyncio.wait_for(
                    tools.add_task(**arguments),
                    timeout=TOOL_TIMEOUT,
                )
            case "list_tasks":
                response = await asyncio.wait_for(
                    tools.list_tasks(**arguments),
                    timeout=TOOL_TIMEOUT,
                )
            case "complete_task":
                response = await asyncio.wait_for(
                    tools.complete_task(**arguments),
                    timeout=TOOL_TIMEOUT,
                )
            case "delete_task":
                response = await asyncio.wait_for(
                    tools.delete_task(**arguments),
                    timeout=TOOL_TIMEOUT,
                )
            case "update_task":
                response = await asyncio.wait_for(
                    tools.update_task(**arguments),
                    timeout=TOOL_TIMEOUT,
                )
            case "get_task":
                response = await asyncio.wait_for(
                    tools.get_task(**arguments),
                    timeout=TOOL_TIMEOUT,
                )
            case "semantic_search":
                response = await asyncio.wait_for(
                    tools.semantic_search(**arguments),
                    timeout=TOOL_TIMEOUT,
                )
            case _:
                logger.warning(
                    "Unknown MCP tool called",
                    tool_name=name,
                )
                response = ToolResponse(
                    status="error",
                    error=f"Unknown tool: {name}",
                    message="This tool is not implemented",
                )
    except asyncio.TimeoutError:
        logger.error(
            "MCP tool timeout",
            tool_name=name,
            timeout_seconds=TOOL_TIMEOUT,
        )
        response = ToolResponse(
            status="error",
            error="timeout",
            message=f"Tool '{name}' timed out after {TOOL_TIMEOUT} seconds. Please try again.",
        )
    except Exception as e:
        logger.error(
            "MCP tool execution error",
            tool_name=name,
            error_type=type(e).__name__,
            error_message=str(e),
        )
        response = ToolResponse(
            status="error",
            error=type(e).__name__,
            message=f"Tool execution failed: {str(e)}",
        )

    # Format response for MCP
    if response.status == "success":
        return [
            TextContent(
                type="text",
                text=response.message or "Operation completed",
            )
        ]
    else:
        # Return error details for AI agent to explain
        return [
            TextContent(
                type="text",
                text=f"Error: {response.error or response.message}",
            )
        ]


# =============================================================================
# Initialization
# =============================================================================

def get_mcp_tools() -> list[Tool]:
    """Get list of available MCP tools."""
    return TOOLS


def get_tool_names() -> list[str]:
    """Get list of available MCP tool names."""
    return [tool.name for tool in TOOLS]
