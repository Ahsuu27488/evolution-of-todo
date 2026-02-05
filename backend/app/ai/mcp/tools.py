"""
MCP tool implementations for task management.

Per spec.md FR-021 through FR-030:
- add_task: Create a new task
- list_tasks: List tasks with optional filters
- complete_task: Mark a task as complete
- delete_task: Delete a task
- update_task: Update task fields
- semantic_search: Search tasks by meaning

All tools are stateless and scoped to user_id.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.ai.utils.logging import get_logger
from app.ai.services import get_qdrant_service, OpenAIService
from app.models import Task, Priority, Tag


# =============================================================================
# Tool Response Schema
# =============================================================================

@dataclass
class ToolResponse:
    """
    Standardized MCP tool response.

    Per FR-028: All MCP tools MUST return structured responses.
    """

    status: str  # "success" or "error"
    data: Any | None = None
    error: str | None = None
    message: str = ""


# =============================================================================
# MCP Tools Implementation
# =============================================================================

class TaskTools:
    """
    Task management tools for MCP server.

    All methods are stateless per FR-027:
    - Accept user_id as parameter
    - Perform database operation
    - Return structured response

    Per FR-029: Validate user owns task before operations (404 if not).
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize task tools.

        Args:
            session: Database session for operations
        """
        self.session = session
        self.logger = get_logger("mcp", "TaskTools")

    async def add_task(
        self,
        user_id: str,
        title: str,
        description: str | None = None,
        priority: str = "MEDIUM",
        due_date: datetime | None = None,
        tags: list[dict[str, str]] | None = None,
        transcription_text: str | None = None,  # T083: Voice transcription
    ) -> ToolResponse:
        """
        Add a new task for the user.

        Per FR-022: add_task tool parameters.
        Per FR-034: Generate embedding on task creation.

        Args:
            user_id: User ID from JWT 'sub' claim
            title: Task title
            description: Optional task description
            priority: Task priority (HIGH, MEDIUM, LOW)
            due_date: Optional due date
            tags: Optional tags with colors

        Returns:
            ToolResponse with created task data

        Example:
            response = await tools.add_task(
                user_id="user123",
                title="Buy groceries",
                priority="HIGH",
            )
        """
        try:
            # Log tool call (LOG-020, LOG-021)
            self.logger.info(
                "MCP tool called: add_task",
                tool_name="add_task",
                user_id=user_id,
                title=title,
            )

            # Create task
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=Priority(priority.upper()),
                due_date=due_date,
                tags=[Tag(**t) for t in (tags or [])],
                completed=False,
                transcription_text=transcription_text,  # T083: Store voice transcription
            )

            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)

            # Generate AI summary if description is long (T094, T096-T098)
            if description and len(description) > 100:
                task.ai_summary = await self._generate_task_summary(
                    title=title,
                    description=description,
                    priority=priority,
                    tags=tags,
                )
                await self.session.commit()

            # Generate embedding for semantic search (T062, FR-034)
            await self._generate_and_store_embedding(task, user_id)

            # Update embedding_id in task
            if task.embedding_id or task.ai_summary:
                await self.session.commit()

            # Log success (LOG-021)
            self.logger.info(
                "MCP tool completed: add_task",
                tool_name="add_task",
                user_id=user_id,
                task_id=task.id,
                result_status="success",
            )

            return ToolResponse(
                status="success",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                },
                message=f"Task '{title}' created successfully",
            )

        except Exception as e:
            self.logger.error(
                "MCP tool failed: add_task",
                tool_name="add_task",
                user_id=user_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return ToolResponse(
                status="error",
                error=str(e),
                message="Failed to create task",
            )

    async def _generate_and_store_embedding(
        self,
        task: Task,
        user_id: str,
    ) -> None:
        """
        Generate and store task embedding for semantic search.

        Per FR-032, FR-034:
        - Uses OpenAI text-embedding-3-small model
        - Stores in Qdrant with user_id scoping
        - Handles Qdrant failures gracefully

        Args:
            task: Task object to embed
            user_id: User ID for scoping
        """
        from app.ai.services import get_qdrant_service, OpenAIService

        qdrant_service = get_qdrant_service()
        if not qdrant_service or not qdrant_service.is_available():
            self.logger.warning(
                "Qdrant unavailable, skipping embedding generation",
                task_id=task.id,
            )
            return

        try:
            # Generate embedding
            openai_service = OpenAIService()
            text_to_embed = f"{task.title}. {task.description or ''}"
            embedding_response = await openai_service.generate_embedding(text_to_embed)

            # Store in Qdrant
            success = await qdrant_service.upsert_task_embedding(
                task_id=task.id,
                user_id=user_id,
                embedding=embedding_response.embedding,
                payload={
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,
                },
            )

            if success:
                # Store embedding_id in task
                task.embedding_id = str(task.id)
                self.logger.debug(
                    "Task embedding generated and stored",
                    task_id=task.id,
                    embedding_id=task.embedding_id,
                )
            else:
                self.logger.warning(
                    "Failed to store task embedding in Qdrant",
                    task_id=task.id,
                )

        except Exception as e:
            # Non-fatal: task creation succeeds even if embedding fails
            self.logger.error(
                "Failed to generate task embedding",
                task_id=task.id,
                error_type=type(e).__name__,
                error_message=str(e),
            )

    async def _delete_task_embedding(self, task_id: int) -> None:
        """
        Delete task embedding from Qdrant.

        Per FR-034: Delete embedding when task is deleted.

        Args:
            task_id: Task ID whose embedding should be deleted
        """
        from app.ai.services import get_qdrant_service

        qdrant_service = get_qdrant_service()
        if not qdrant_service or not qdrant_service.is_available():
            self.logger.warning(
                "Qdrant unavailable, skipping embedding deletion",
                task_id=task_id,
            )
            return

        try:
            success = await qdrant_service.delete_task_embedding(task_id)
            if success:
                self.logger.debug(
                    "Task embedding deleted",
                    task_id=task_id,
                )
            else:
                self.logger.warning(
                    "Failed to delete task embedding from Qdrant",
                    task_id=task_id,
                )
        except Exception as e:
            # Non-fatal: task deletion succeeds even if embedding deletion fails
            self.logger.error(
                "Failed to delete task embedding",
                task_id=task_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )

    async def _generate_task_summary(
        self,
        title: str,
        description: str | None,
        priority: str,
        tags: list[dict[str, str]] | None,
    ) -> str | None:
        """
        Generate AI summary for a task.

        Per T093-T099: AI-powered task summarization for quick scanning.
        Uses OpenAIService.generate_task_summary() with fallback handling.

        Args:
            title: Task title
            description: Task description
            priority: Task priority level
            tags: Optional task tags

        Returns:
            Generated summary (max 500 chars) or None on failure
        """
        try:
            openai_service = OpenAIService()
            summary = await openai_service.generate_task_summary(
                title=title,
                description=description,
                tags=[t.get("name", "") for t in (tags or [])],
                priority=priority,
                max_length=500,  # T099: Max 500 characters
            )
            self.logger.debug(
                "AI summary generated",
                title=title,
                summary_length=len(summary),
            )
            return summary
        except Exception as e:
            # Non-fatal: task creation succeeds even if summary generation fails
            self.logger.warning(
                "Failed to generate AI summary, task will be created without summary",
                title=title,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return None

    async def list_tasks(
        self,
        user_id: str,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ToolResponse:
        """
        List tasks for the user.

        Per FR-023: list_tasks tool parameters.

        Args:
            user_id: User ID from JWT 'sub' claim
            status: Filter by status (all/pending/completed)
            limit: Max results to return
            offset: Pagination offset

        Returns:
            ToolResponse with list of tasks

        Example:
            response = await tools.list_tasks(
                user_id="user123",
                status="pending",
                limit=10,
            )
        """
        try:
            self.logger.info(
                "MCP tool called: list_tasks",
                tool_name="list_tasks",
                user_id=user_id,
                status=status,
            )

            # Build query
            statement = select(Task).where(Task.user_id == user_id)

            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)

            statement = statement.order_by(Task.created_at.desc())
            statement = statement.offset(offset).limit(limit)

            result = await self.session.execute(statement)
            tasks = result.scalars().all()

            self.logger.info(
                "MCP tool completed: list_tasks",
                tool_name="list_tasks",
                user_id=user_id,
                result_count=len(tasks),
            )

            return ToolResponse(
                status="success",
                data=[
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority.value,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "completed": task.completed,
                    }
                    for task in tasks
                ],
                message=f"Found {len(tasks)} tasks",
            )

        except Exception as e:
            self.logger.error(
                "MCP tool failed: list_tasks",
                tool_name="list_tasks",
                user_id=user_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return ToolResponse(
                status="error",
                error=str(e),
                message="Failed to list tasks",
            )

    async def complete_task(
        self,
        user_id: str,
        task_id: int,
    ) -> ToolResponse:
        """
        Mark a task as complete.

        Per FR-024: complete_task tool parameters.

        Args:
            user_id: User ID from JWT 'sub' claim
            task_id: Task to mark complete

        Returns:
            ToolResponse with updated task data

        Example:
            response = await tools.complete_task(
                user_id="user123",
                task_id=42,
            )
        """
        try:
            self.logger.info(
                "MCP tool called: complete_task",
                tool_name="complete_task",
                user_id=user_id,
                task_id=task_id,
            )

            # Get task (scoped to user)
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
            )
            result = await self.session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                # Return 404, not 403 (per FR-029)
                return ToolResponse(
                    status="error",
                    error="Task not found",
                    message=f"Task {task_id} doesn't exist or was deleted",
                )

            # Mark complete
            task.completed = True
            await self.session.commit()

            self.logger.info(
                "MCP tool completed: complete_task",
                tool_name="complete_task",
                user_id=user_id,
                task_id=task_id,
            )

            return ToolResponse(
                status="success",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "completed": True,
                },
                message=f"Task '{task.title}' marked as complete",
            )

        except Exception as e:
            self.logger.error(
                "MCP tool failed: complete_task",
                tool_name="complete_task",
                user_id=user_id,
                task_id=task_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return ToolResponse(
                status="error",
                error=str(e),
                message="Failed to complete task",
            )

    async def delete_task(
        self,
        user_id: str,
        task_id: int,
    ) -> ToolResponse:
        """
        Delete a task.

        Per FR-025: delete_task tool parameters.

        Args:
            user_id: User ID from JWT 'sub' claim
            task_id: Task to delete

        Returns:
            ToolResponse confirming deletion

        Example:
            response = await tools.delete_task(
                user_id="user123",
                task_id=42,
            )
        """
        try:
            self.logger.info(
                "MCP tool called: delete_task",
                tool_name="delete_task",
                user_id=user_id,
                task_id=task_id,
            )

            # Get task (scoped to user)
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
            )
            result = await self.session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return ToolResponse(
                    status="error",
                    error="Task not found",
                    message=f"Task {task_id} doesn't exist or was deleted",
                )

            # Delete task embedding from Qdrant first (FR-034)
            await self._delete_task_embedding(task_id)

            # Delete task
            await self.session.delete(task)
            await self.session.commit()

            self.logger.info(
                "MCP tool completed: delete_task",
                tool_name="delete_task",
                user_id=user_id,
                task_id=task_id,
            )

            return ToolResponse(
                status="success",
                data={"task_id": task_id},
                message=f"Task '{task.title}' deleted",
            )

        except Exception as e:
            self.logger.error(
                "MCP tool failed: delete_task",
                tool_name="delete_task",
                user_id=user_id,
                task_id=task_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return ToolResponse(
                status="error",
                error=str(e),
                message="Failed to delete task",
            )

    async def update_task(
        self,
        user_id: str,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        due_date: datetime | None = None,
    ) -> ToolResponse:
        """
        Update a task.

        Per FR-026: update_task tool parameters.
        Per FR-034: Regenerate embedding when title/description changes (T064).
        Per T095: Regenerate AI summary when description changes.

        Args:
            user_id: User ID from JWT 'sub' claim
            task_id: Task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            due_date: New due date (optional)

        Returns:
            ToolResponse with updated task data

        Example:
            response = await tools.update_task(
                user_id="user123",
                task_id=42,
                title="Updated title",
            )
        """
        try:
            self.logger.info(
                "MCP tool called: update_task",
                tool_name="update_task",
                user_id=user_id,
                task_id=task_id,
            )

            # Get task (scoped to user)
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
            )
            result = await self.session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return ToolResponse(
                    status="error",
                    error="Task not found",
                    message=f"Task {task_id} doesn't exist or was deleted",
                )

            # Track if title or description changed (for embedding/summary regeneration)
            text_changed = False
            description_changed = False
            if title is not None and title != task.title:
                task.title = title
                text_changed = True
            if description is not None and description != task.description:
                task.description = description
                text_changed = True
                description_changed = True
            if priority is not None:
                task.priority = Priority(priority.upper())
            if due_date is not None:
                task.due_date = due_date

            await self.session.commit()

            # Regenerate AI summary if description changed (T095)
            if description_changed and task.description and len(task.description) > 100:
                task.ai_summary = await self._generate_task_summary(
                    title=task.title,
                    description=task.description,
                    priority=task.priority.value,
                    tags=[t.model_dump() for t in task.tags],
                )
                await self.session.commit()

            # Regenerate embedding if text changed (T064, FR-034)
            if text_changed:
                await self._generate_and_store_embedding(task, user_id)
                if task.embedding_id or task.ai_summary:
                    await self.session.commit()

            self.logger.info(
                "MCP tool completed: update_task",
                tool_name="update_task",
                user_id=user_id,
                task_id=task_id,
            )

            return ToolResponse(
                status="success",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                },
                message=f"Task '{task.title}' updated",
            )

        except Exception as e:
            self.logger.error(
                "MCP tool failed: update_task",
                tool_name="update_task",
                user_id=user_id,
                task_id=task_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return ToolResponse(
                status="error",
                error=str(e),
                message="Failed to update task",
            )

    async def get_task(
        self,
        user_id: str,
        task_id: int,
    ) -> ToolResponse:
        """
        Get a single task by ID.

        Args:
            user_id: User ID from JWT 'sub' claim
            task_id: Task to retrieve

        Returns:
            ToolResponse with task data

        Example:
            response = await tools.get_task(
                user_id="user123",
                task_id=42,
            )
        """
        try:
            self.logger.info(
                "MCP tool called: get_task",
                tool_name="get_task",
                user_id=user_id,
                task_id=task_id,
            )

            # Get task (scoped to user)
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
            )
            result = await self.session.execute(statement)
            task = result.scalar_one_or_none()

            if not task:
                return ToolResponse(
                    status="error",
                    error="Task not found",
                    message=f"Task {task_id} doesn't exist or was deleted",
                )

            return ToolResponse(
                status="success",
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed": task.completed,
                    "tags": [t.model_dump() for t in task.tags],
                },
                message=f"Task '{task.title}' retrieved",
            )

        except Exception as e:
            self.logger.error(
                "MCP tool failed: get_task",
                tool_name="get_task",
                user_id=user_id,
                task_id=task_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return ToolResponse(
                status="error",
                error=str(e),
                message="Failed to get task",
            )

    async def semantic_search(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
    ) -> ToolResponse:
        """
        Search tasks by semantic meaning (not keywords).

        Per FR-036, FR-037, FR-038, FR-039, FR-040:
        - Uses Qdrant vector search for semantic similarity
        - Falls back to keyword search if Qdrant unavailable
        - Results scoped to user_id (no cross-user search)

        Args:
            user_id: User ID from JWT 'sub' claim
            query: Natural language search query
            limit: Maximum results to return

        Returns:
            ToolResponse with semantically similar tasks

        Example:
            response = await tools.semantic_search(
                user_id="user123",
                query="things I need to buy at the store",
                limit=10,
            )
        """
        try:
            self.logger.info(
                "MCP tool called: semantic_search",
                tool_name="semantic_search",
                user_id=user_id,
                query=query[:100],  # Truncate for logging
                limit=limit,
            )

            # Get Qdrant service
            qdrant_service = get_qdrant_service()
            openai_service = None

            if qdrant_service and qdrant_service.is_available():
                # Generate query embedding
                try:
                    if openai_service is None:
                        openai_service = OpenAIService()

                    embedding_response = await openai_service.generate_embedding(query)
                    query_embedding = embedding_response.embedding

                    # Search Qdrant
                    search_response = await qdrant_service.semantic_search(
                        user_id=user_id,
                        query_embedding=query_embedding,
                        limit=limit,
                        # Lower threshold for better recall (0.3 instead of 0.5)
                        # This captures semantically related tasks even with lower similarity
                        score_threshold=0.3,
                    )

                    if search_response.results:
                        self.logger.info(
                            "MCP tool completed: semantic_search (Qdrant)",
                            tool_name="semantic_search",
                            user_id=user_id,
                            result_count=len(search_response.results),
                            mode="semantic",
                            scores=[round(r.score, 3) for r in search_response.results],
                        )

                        return ToolResponse(
                            status="success",
                            data=[
                                {
                                    "task_id": r.task_id,
                                    "score": round(r.score, 3),
                                    "title": r.payload.get("title", ""),
                                }
                                for r in search_response.results
                            ],
                            message=f"Found {len(search_response.results)} semantically similar tasks",
                        )
                    else:
                        # Log when Qdrant returns no results (helps debug threshold issues)
                        self.logger.info(
                            "Qdrant semantic search returned no results (check score_threshold)",
                            tool_name="semantic_search",
                            user_id=user_id,
                            query=query[:100],
                            score_threshold=0.3,
                        )

                except Exception as e:
                    self.logger.warning(
                        "Qdrant search failed, falling back to keyword",
                        tool_name="semantic_search",
                        error=str(e),
                    )

            # Fallback: keyword search (FR-038)
            self.logger.info(
                "MCP tool: semantic_search using keyword fallback",
                tool_name="semantic_search",
                user_id=user_id,
                mode="keyword",
            )

            # Build keyword search query
            statement = select(Task).where(Task.user_id == user_id)

            # Search in title and description
            search_pattern = f"%{query}%"
            statement = statement.where(
                (Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern))
            )

            statement = statement.order_by(Task.created_at.desc())
            statement = statement.limit(limit)

            result = await self.session.execute(statement)
            tasks = result.scalars().all()

            self.logger.info(
                "MCP tool completed: semantic_search (keyword fallback)",
                tool_name="semantic_search",
                user_id=user_id,
                result_count=len(tasks),
                mode="keyword",
            )

            return ToolResponse(
                status="success",
                data=[
                    {
                        "task_id": task.id,
                        "score": 1.0,  # Perfect match for keyword search
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority.value,
                        "completed": task.completed,
                    }
                    for task in tasks
                ],
                message=f"Found {len(tasks)} matching tasks (keyword search)",
            )

        except Exception as e:
            self.logger.error(
                "MCP tool failed: semantic_search",
                tool_name="semantic_search",
                user_id=user_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            return ToolResponse(
                status="error",
                error=str(e),
                message="Failed to search tasks",
            )
