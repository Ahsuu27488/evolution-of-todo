"""
MCP (Model Context Protocol) server for Phase III.

In-process MCP server that exposes task management tools to the AI agent.
Per spec.md FR-021 through FR-030.

Architecture:
- All tools are stateless (accept user_id, perform operation, return result)
- Tools return structured responses with status, data/error, message
- Tool errors are caught by AI agent and explained to user
- All operations scoped to authenticated user_id

This is an in-process server using streamable-http transport,
simpler deployment while maintaining MCP protocol benefits.
"""

from .server import mcp_server
from .tools import TaskTools

__all__ = ["mcp_server", "TaskTools"]
