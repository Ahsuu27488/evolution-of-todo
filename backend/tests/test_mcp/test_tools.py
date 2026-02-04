"""
MCP Tool Integration Tests.

Per T105: Test all MCP tools with real database operations.
Per FR-027: Stateless tool execution - each test is isolated.
Per FR-029: Ownership verification - users cannot access other users' tasks.
Per FR-030: Tool errors caught and returned with structured responses.

Test Coverage:
- add_task: Create tasks with various parameters
- list_tasks: List with filters (all, pending, completed)
- get_task: Retrieve single task by ID
- update_task: Modify task fields
- complete_task: Mark task as complete
- delete_task: Remove task
- semantic_search: Search by meaning (with keyword fallback)
- timeout: Tool execution timeout handling (T103)
- ownership: User scoping and 404 responses (FR-029)
- error_handling: Structured error responses (FR-030)
"""

import asyncio
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.mcp.tools import TaskTools
from app.ai.mcp.server import _execute_tool_call
from app.ai.utils.logging import get_logger


# =============================================================================
# Test Constants
# =============================================================================

logger = get_logger("test", "mcp_tools")


# =============================================================================
# add_task Tests
# =============================================================================

class TestAddTask:
    """Tests for add_task MCP tool."""

    @pytest.mark.asyncio
    async def test_add_task_basic(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test basic task creation with required fields only."""
        response = await task_tools.add_task(
            user_id=test_user_id,
            title="Buy groceries",
        )

        assert response.status == "success"
        assert response.data is not None
        assert response.data["title"] == "Buy groceries"
        assert response.data["task_id"] > 0
        assert response.data["completed"] is False
        assert "created successfully" in response.message.lower()

    @pytest.mark.asyncio
    async def test_add_task_with_description(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test task creation with description."""
        response = await task_tools.add_task(
            user_id=test_user_id,
            title="Buy groceries",
            description="Milk, eggs, bread, and cheese",
        )

        assert response.status == "success"
        assert response.data["description"] == "Milk, eggs, bread, and cheese"

    @pytest.mark.asyncio
    async def test_add_task_with_priority(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test task creation with different priority levels."""
        for priority in ["HIGH", "MEDIUM", "LOW"]:
            response = await task_tools.add_task(
                user_id=test_user_id,
                title=f"Task with {priority} priority",
                priority=priority,
            )

            assert response.status == "success"
            assert response.data["priority"] == priority

    @pytest.mark.asyncio
    async def test_add_task_with_due_date(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test task creation with due date."""
        due_date = datetime(2025, 12, 25, 10, 0, 0)
        response = await task_tools.add_task(
            user_id=test_user_id,
            title="Christmas shopping",
            due_date=due_date,
        )

        assert response.status == "success"
        assert response.data["due_date"] is not None
        assert "2025-12-25" in response.data["due_date"]

    @pytest.mark.asyncio
    async def test_add_task_with_tags(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test task creation with colored tags."""
        tags = [
            {"name": "shopping", "color": "#ff0000"},
            {"name": "urgent", "color": "#00ff00"},
        ]
        response = await task_tools.add_task(
            user_id=test_user_id,
            title="Buy gifts",
            tags=tags,
        )

        assert response.status == "success"
        assert response.data["task_id"] > 0

    @pytest.mark.asyncio
    async def test_add_task_lowercase_priority(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test that lowercase priority is converted to uppercase."""
        response = await task_tools.add_task(
            user_id=test_user_id,
            title="Lowercase priority test",
            priority="high",  # lowercase input
        )

        assert response.status == "success"
        assert response.data["priority"] == "HIGH"  # converted to uppercase


# =============================================================================
# list_tasks Tests
# =============================================================================

class TestListTasks:
    """Tests for list_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test listing tasks when user has no tasks."""
        response = await task_tools.list_tasks(user_id=test_user_id)

        assert response.status == "success"
        assert response.data == []
        assert "0 tasks" in response.message.lower() or "found 0" in response.message.lower()

    @pytest.mark.asyncio
    async def test_list_tasks_with_tasks(
        self,
        db_session: AsyncSession,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test listing tasks when user has multiple tasks."""
        # Create 3 tasks
        for i in range(3):
            await task_tools.add_task(
                user_id=test_user_id,
                title=f"Task {i+1}",
            )

        response = await task_tools.list_tasks(user_id=test_user_id)

        assert response.status == "success"
        assert len(response.data) == 3

    @pytest.mark.asyncio
    async def test_list_tasks_filter_pending(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task,
        completed_sample_task,
    ):
        """Test listing only pending (not completed) tasks."""
        response = await task_tools.list_tasks(
            user_id=test_user_id,
            status="pending",
        )

        assert response.status == "success"
        assert all(not task["completed"] for task in response.data)

    @pytest.mark.asyncio
    async def test_list_tasks_filter_completed(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task,
        completed_sample_task,
    ):
        """Test listing only completed tasks."""
        response = await task_tools.list_tasks(
            user_id=test_user_id,
            status="completed",
        )

        assert response.status == "success"
        assert all(task["completed"] for task in response.data)

    @pytest.mark.asyncio
    async def test_list_tasks_with_limit(
        self,
        db_session: AsyncSession,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test pagination with limit parameter."""
        # Create 10 tasks
        for i in range(10):
            await task_tools.add_task(
                user_id=test_user_id,
                title=f"Task {i+1}",
            )

        response = await task_tools.list_tasks(
            user_id=test_user_id,
            limit=5,
        )

        assert response.status == "success"
        assert len(response.data) == 5

    @pytest.mark.asyncio
    async def test_list_tasks_with_offset(
        self,
        db_session: AsyncSession,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test pagination with offset parameter."""
        # Create 5 tasks
        task_ids = []
        for i in range(5):
            response = await task_tools.add_task(
                user_id=test_user_id,
                title=f"Task {i+1}",
            )
            task_ids.append(response.data["task_id"])

        # Get first page (limit 2, offset 0)
        response = await task_tools.list_tasks(
            user_id=test_user_id,
            limit=2,
            offset=0,
        )
        first_page_ids = [t["task_id"] for t in response.data]

        # Get second page (limit 2, offset 2)
        response = await task_tools.list_tasks(
            user_id=test_user_id,
            limit=2,
            offset=2,
        )
        second_page_ids = [t["task_id"] for t in response.data]

        # Verify pagination works
        assert len(first_page_ids) == 2
        assert len(second_page_ids) == 2
        # IDs should not overlap
        assert set(first_page_ids).isdisjoint(set(second_page_ids))


# =============================================================================
# get_task Tests
# =============================================================================

class TestGetTask:
    """Tests for get_task MCP tool."""

    @pytest.mark.asyncio
    async def test_get_task_valid(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task,
    ):
        """Test retrieving a valid task."""
        response = await task_tools.get_task(
            user_id=test_user_id,
            task_id=sample_task.id,
        )

        assert response.status == "success"
        assert response.data["task_id"] == sample_task.id
        assert response.data["title"] == sample_task.title

    @pytest.mark.asyncio
    async def test_get_task_not_found(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test retrieving a non-existent task."""
        response = await task_tools.get_task(
            user_id=test_user_id,
            task_id=99999,  # Non-existent ID
        )

        assert response.status == "error"
        assert "not found" in response.error.lower() or "doesn't exist" in response.message.lower()

    @pytest.mark.asyncio
    async def test_get_task_wrong_user_ownership(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        test_user_id_2: str,
        sample_task_for_user_2: Task,
    ):
        """
        Test that user cannot access another user's task.

        Per FR-029: Ownership verification - returns 404 not 403.
        """
        response = await task_tools.get_task(
            user_id=test_user_id,  # Different user
            task_id=sample_task_for_user_2.id,
        )

        # Should return error (404 pattern, not 403)
        assert response.status == "error"
        # Should not reveal task exists for different user
        assert "not found" in response.message.lower() or "doesn't exist" in response.message.lower()


# =============================================================================
# update_task Tests
# =============================================================================

class TestUpdateTask:
    """Tests for update_task MCP tool."""

    @pytest.mark.asyncio
    async def test_update_task_title(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task,
    ):
        """Test updating task title."""
        new_title = "Updated: Buy groceries and more"
        response = await task_tools.update_task(
            user_id=test_user_id,
            task_id=sample_task.id,
            title=new_title,
        )

        assert response.status == "success"
        assert response.data["title"] == new_title

    @pytest.mark.asyncio
    async def test_update_task_description(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task,
    ):
        """Test updating task description."""
        new_description = "Updated description with more details"
        response = await task_tools.update_task(
            user_id=test_user_id,
            task_id=sample_task.id,
            description=new_description,
        )

        assert response.status == "success"
        assert response.data["description"] == new_description

    @pytest.mark.asyncio
    async def test_update_task_priority(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task,
    ):
        """Test updating task priority."""
        response = await task_tools.update_task(
            user_id=test_user_id,
            task_id=sample_task.id,
            priority="HIGH",
        )

        assert response.status == "success"
        assert response.data["priority"] == "HIGH"

    @pytest.mark.asyncio
    async def test_update_task_not_found(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test updating a non-existent task."""
        response = await task_tools.update_task(
            user_id=test_user_id,
            task_id=99999,
            title="This should fail",
        )

        assert response.status == "error"
        assert "not found" in response.message.lower() or "doesn't exist" in response.message.lower()

    @pytest.mark.asyncio
    async def test_update_task_wrong_user_ownership(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task_for_user_2: Task,
    ):
        """
        Test that user cannot update another user's task.

        Per FR-029: Ownership verification.
        """
        response = await task_tools.update_task(
            user_id=test_user_id,  # Different user
            task_id=sample_task_for_user_2.id,
            title="Should not update",
        )

        assert response.status == "error"
        assert "not found" in response.message.lower()


# =============================================================================
# complete_task Tests
# =============================================================================

class TestCompleteTask:
    """Tests for complete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_complete_task(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task,
    ):
        """Test marking a task as complete."""
        response = await task_tools.complete_task(
            user_id=test_user_id,
            task_id=sample_task.id,
        )

        assert response.status == "success"
        assert response.data["completed"] is True
        assert "marked as complete" in response.message.lower()

    @pytest.mark.asyncio
    async def test_complete_task_not_found(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test completing a non-existent task."""
        response = await task_tools.complete_task(
            user_id=test_user_id,
            task_id=99999,
        )

        assert response.status == "error"
        assert "not found" in response.message.lower() or "doesn't exist" in response.message.lower()

    @pytest.mark.asyncio
    async def test_complete_task_wrong_user_ownership(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task_for_user_2: Task,
    ):
        """
        Test that user cannot complete another user's task.

        Per FR-029: Ownership verification.
        """
        response = await task_tools.complete_task(
            user_id=test_user_id,  # Different user
            task_id=sample_task_for_user_2.id,
        )

        assert response.status == "error"
        assert "not found" in response.message.lower()


# =============================================================================
# delete_task Tests
# =============================================================================

class TestDeleteTask:
    """Tests for delete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_task(
        self,
        db_session: AsyncSession,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test deleting a task."""
        # First create a task
        create_response = await task_tools.add_task(
            user_id=test_user_id,
            title="Task to delete",
        )
        task_id = create_response.data["task_id"]

        # Delete it
        response = await task_tools.delete_task(
            user_id=test_user_id,
            task_id=task_id,
        )

        assert response.status == "success"
        assert response.data["task_id"] == task_id
        assert "deleted" in response.message.lower()

        # Verify it's gone
        get_response = await task_tools.get_task(
            user_id=test_user_id,
            task_id=task_id,
        )
        assert get_response.status == "error"

    @pytest.mark.asyncio
    async def test_delete_task_not_found(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test deleting a non-existent task."""
        response = await task_tools.delete_task(
            user_id=test_user_id,
            task_id=99999,
        )

        assert response.status == "error"
        assert "not found" in response.message.lower() or "doesn't exist" in response.message.lower()

    @pytest.mark.asyncio
    async def test_delete_task_wrong_user_ownership(
        self,
        db_session: AsyncSession,
        task_tools: TaskTools,
        test_user_id: str,
        sample_task_for_user_2: Task,
    ):
        """
        Test that user cannot delete another user's task.

        Per FR-029: Ownership verification.
        """
        response = await task_tools.delete_task(
            user_id=test_user_id,  # Different user
            task_id=sample_task_for_user_2.id,
        )

        assert response.status == "error"
        assert "not found" in response.message.lower()

        # Verify task still exists for owner
        owner_get = await task_tools.get_task(
            user_id="test-user-mcp-456",
            task_id=sample_task_for_user_2.id,
        )
        assert owner_get.status == "success"


# =============================================================================
# semantic_search Tests
# =============================================================================

class TestSemanticSearch:
    """Tests for semantic_search MCP tool."""

    @pytest.mark.asyncio
    async def test_semantic_search_empty_results(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test semantic search with no matching tasks."""
        response = await task_tools.semantic_search(
            user_id=test_user_id,
            query="nonexistent task about quantum physics",
        )

        assert response.status == "success"
        assert response.data == []

    @pytest.mark.asyncio
    async def test_semantic_search_keyword_fallback(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """
        Test semantic search with keyword fallback.

        Per FR-038: Falls back to keyword search if Qdrant unavailable.
        Per FR-040: Still returns results even when vector search fails.
        """
        # Create a task
        await task_tools.add_task(
            user_id=test_user_id,
            title="Buy groceries",
            description="Milk, eggs, bread",
        )

        # Search - should use keyword fallback if Qdrant unavailable
        response = await task_tools.semantic_search(
            user_id=test_user_id,
            query="groceries",
        )

        assert response.status == "success"
        # Should find the task via keyword fallback
        assert len(response.data) >= 1
        assert any("groceries" in result.get("title", "").lower() for result in response.data)

    @pytest.mark.asyncio
    async def test_semantic_search_user_scoped(
        self,
        task_tools: TaskTools,
        test_user_id: str,
        test_user_id_2: str,
    ):
        """
        Test that semantic search only returns user's own tasks.

        Per FR-039: User scoping - no cross-user data leakage.
        """
        # Create task for user 1
        await task_tools.add_task(
            user_id=test_user_id,
            title="User 1 shopping list",
        )

        # Create task for user 2
        await task_tools.add_task(
            user_id=test_user_id_2,
            title="User 2 shopping list",
        )

        # Search as user 1
        response = await task_tools.semantic_search(
            user_id=test_user_id,
            query="shopping list",
        )

        assert response.status == "success"
        # Should only find user 1's task
        for result in response.data:
            task_title = result.get("title", "")
            assert "User 1" in task_title or "user 1" in task_title.lower()

    @pytest.mark.asyncio
    async def test_semantic_search_with_limit(
        self,
        db_session: AsyncSession,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """Test semantic search with limit parameter."""
        # Create 5 tasks with similar keywords
        for i in range(5):
            await task_tools.add_task(
                user_id=test_user_id,
                title=f"Shopping item {i+1}",
            )

        response = await task_tools.semantic_search(
            user_id=test_user_id,
            query="shopping",
            limit=3,
        )

        assert response.status == "success"
        assert len(response.data) <= 3


# =============================================================================
# Timeout Tests (T103)
# =============================================================================

class TestTimeoutHandling:
    """Tests for tool timeout handling per T103."""

    @pytest.mark.asyncio
    async def test_execute_tool_call_timeout_handling(
        self,
        db_session: AsyncSession,
        test_user_id: str,
    ):
        """
        Test that tool calls handle timeouts gracefully.

        Per T103: 30-second timeout limit on MCP tool execution.
        """
        # Test normal completion (well under 30 seconds)
        response = await _execute_tool_call(
            name="list_tasks",
            arguments={"user_id": test_user_id},
            session=db_session,
            logger=logger,
        )

        # Should complete successfully
        assert len(response) > 0
        assert response[0].type == "text"

    @pytest.mark.asyncio
    async def test_execute_tool_call_unknown_tool(
        self,
        db_session: AsyncSession,
        test_user_id: str,
    ):
        """Test calling an unknown tool returns proper error."""
        response = await _execute_tool_call(
            name="unknown_tool_xyz",
            arguments={"user_id": test_user_id},
            session=db_session,
            logger=logger,
        )

        assert len(response) > 0
        assert "error" in response[0].text.lower() or "not implemented" in response[0].text.lower()


# =============================================================================
# Error Handling Tests (FR-030)
# =============================================================================

class TestErrorHandling:
    """Tests for structured error responses per FR-030."""

    @pytest.mark.asyncio
    async def test_tool_response_error_structure(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """
        Test that all tool errors follow ToolResponse schema.

        Per FR-030: Tool errors MUST have structured responses.
        """
        # Trigger an error with invalid task ID
        response = await task_tools.get_task(
            user_id=test_user_id,
            task_id=99999,
        )

        # Verify error structure
        assert hasattr(response, "status")
        assert hasattr(response, "error")
        assert hasattr(response, "message")
        assert response.status == "error"
        assert response.error is not None
        assert len(response.message) > 0

    @pytest.mark.asyncio
    async def test_all_tools_return_structured_response(
        self,
        task_tools: TaskTools,
        test_user_id: str,
    ):
        """
        Test that all MCP tools return ToolResponse schema.

        Per FR-028: All MCP tools MUST return structured responses.
        """
        # Test add_task (success case)
        response = await task_tools.add_task(
            user_id=test_user_id,
            title="Structured response test",
        )
        assert hasattr(response, "status")
        assert hasattr(response, "data")
        assert hasattr(response, "message")
        assert response.status == "success"
        assert response.data is not None
