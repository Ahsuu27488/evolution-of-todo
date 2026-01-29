"""Task CRUD endpoints for Chronos Todo API.

All endpoints:
- Require bearer token authentication
- Verify the user owns the requested resource
- Support filtering, sorting, and searching
- Return standardized error responses

Per contracts/backend-api.yaml specification.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, desc, asc, case as sql_case, String, cast, func

from app.db import get_session
from app.models import (
    Action,
    Priority,
    RecurrencePattern,
    Tag,
    Task,
    TaskCreate,
    TaskList,
    TaskLog,
    TaskLogPublic,
    TaskPublic,
    TaskUpdate,
)
from app.simple_auth import get_current_user_id
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Query Parameters
# =============================================================================

class TaskStatus(str, Enum):
    """Task status filter values."""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class SortField(str, Enum):
    """Available sort fields."""
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    TITLE = "title"


class SortOrder(str, Enum):
    """Sort order direction."""
    ASC = "asc"
    DESC = "desc"


# =============================================================================
# Helper Functions
# =============================================================================

async def get_task_or_404(
    task_id: int,
    user_id: str,
    session: AsyncSession,
) -> Task:
    """Get a task by ID, ensuring it belongs to the user.

    Args:
        task_id: Task ID to retrieve
        user_id: User ID for ownership verification
        session: Database session

    Returns:
        Task if found and owned by user

    Raises:
        HTTPException: If task not found (404, not 403 for security)
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found",
        )

    return task


async def create_task_log(
    session: AsyncSession,
    task_id: int,
    user_id: str,
    action: Action,
    changed_fields: dict = None,
) -> None:
    """Create an audit log entry for a task action.

    Args:
        session: Database session
        task_id: Related task ID
        user_id: User performing the action
        action: Type of action performed
        changed_fields: Dictionary of changed values
    """
    log = TaskLog(
        task_id=task_id,
        user_id=user_id,
        action=action,
        changed_fields=changed_fields or {},
    )
    session.add(log)


# =============================================================================
# Task Endpoints
# =============================================================================

@router.get("", response_model=TaskList)
async def list_tasks(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    status: TaskStatus = TaskStatus.ALL,
    priority: Optional[Priority] = None,
    tag: Optional[str] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    sort_by: SortField = SortField.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
) -> TaskList:
    """List all tasks for the authenticated user with filtering and sorting.

    Supports:
    - Status filter (all/pending/completed)
    - Priority filter
    - Tag filter
    - Due date range filter
    - Sorting by created_at, due_date, priority, title
    - Pagination
    """
    logger.info(
        f"List tasks: user={current_user_id}, status={status}, "
        f"priority={priority}, tag={tag}, sort={sort_by} {sort_order}"
    )

    # Build base query
    statement = select(Task).where(Task.user_id == current_user_id)

    # Apply status filter
    if status == TaskStatus.PENDING:
        statement = statement.where(Task.completed == False)
    elif status == TaskStatus.COMPLETED:
        statement = statement.where(Task.completed == True)

    # Apply priority filter
    if priority:
        statement = statement.where(Task.priority == priority)

    # Apply tag filter (JSONB array contains)
    if tag:
        # For JSONB array contains: tags @> '[{"name": "tag_name"}]'
        statement = statement.where(Task.tags.contains([{"name": tag}]))

    # Apply due date filters
    if due_before:
        statement = statement.where(Task.due_date <= due_before)
    if due_after:
        statement = statement.where(Task.due_date >= due_after)

    # Get total count before pagination (use func.count for efficiency)
    total = await session.scalar(select(func.count()).select_from(statement.subquery()))

    # Apply sorting
    sort_column = {
        SortField.CREATED_AT: Task.created_at,
        SortField.DUE_DATE: Task.due_date,
        SortField.TITLE: Task.title,
    }.get(sort_by, Task.created_at)

    # Calculate pagination offset before applying sort/pagination
    offset = (page - 1) * per_page

    if sort_by == SortField.PRIORITY:
        # Use SQL CASE for database-level priority sorting
        # HIGH=1, MEDIUM=2, LOW=3 for ascending order
        # Cast to VARCHAR to avoid enum type issues with prepared statements
        priority_order = sql_case(
            (cast(Task.priority, String) == "HIGH", 1),
            (cast(Task.priority, String) == "MEDIUM", 2),
            (cast(Task.priority, String) == "LOW", 3),
            else_=4
        )
        order_func = desc if sort_order == SortOrder.DESC else asc
        statement = statement.order_by(order_func(priority_order))
    else:
        statement = statement.order_by(
            desc(sort_column) if sort_order == SortOrder.DESC else asc(sort_column)
        )

    # Apply pagination (now consistent for all sort types)
    statement = statement.offset(offset).limit(per_page)

    tasks_result = await session.execute(statement)
    tasks = tasks_result.scalars().all()

    logger.debug(f"Found {len(tasks)} tasks for user {current_user_id} (total: {total})")

    return TaskList(
        tasks=[TaskPublic.model_validate(t) for t in tasks],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=TaskPublic, status_code=201)
async def create_task(
    request: Request,
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskPublic:
    """Create a new task for the authenticated user.

    Validates:
    - Title is 1-200 characters
    - Description max 1000 characters
    - Priority is valid enum value
    - Tags max 10 items, max 30 chars each
    - Due date is valid datetime
    - Recurrence pattern is valid enum value
    """
    logger.info(
        f"Create task: user={current_user_id}, title={task_data.title!r}, "
        f"priority={task_data.priority}, due_date={task_data.due_date}"
    )

    # Convert Tag models to dicts for JSON storage
    tags_as_dicts = [tag.to_dict() if hasattr(tag, 'to_dict') else tag for tag in (task_data.tags or [])]

    # Create task
    task = Task(
        user_id=current_user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority or Priority.MEDIUM,
        tags=tags_as_dicts,
        due_date=task_data.due_date,
        recurrence_pattern=task_data.recurrence_pattern,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Create audit log
    await create_task_log(
        session=session,
        task_id=task.id,
        user_id=current_user_id,
        action=Action.CREATED,
        changed_fields={"title": task.title, "priority": task.priority.value},
    )
    await session.commit()

    # [Task]: T051 - Create notification for new task with due date
    # Send notification if task has a due date
    if task.due_date:
        await NotificationService.dispatch(
            session=session,
            user_id=current_user_id,
            type=NotificationType.TASK_DUE,
            title=f"New Task: {task.title}",
            message=f"You've created a new task due on {task.due_date.strftime('%Y-%m-%d')}",
            data={
                "task_id": task.id,
                "task_title": task.title,
                "due_date": task.due_date.isoformat() if task.due_date else None,
            },
            related_task_id=task.id,
        )

    logger.info(f"Task created: id={task.id}, user={current_user_id}")

    return TaskPublic.model_validate(task)


@router.get("/search", response_model=TaskList)
async def search_tasks(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
) -> TaskList:
    """Search tasks by keyword in title or description.

    Uses case-insensitive ILIKE for partial matching.
    """
    logger.info(f"Search tasks: user={current_user_id}, query={q!r}")

    # Build search query
    statement = select(Task).where(
        and_(
            Task.user_id == current_user_id,
            or_(
                Task.title.ilike(f"%{q}%"),
                Task.description.ilike(f"%{q}%"),
            )
        )
    ).order_by(Task.created_at.desc())

    # Get total count (use func.count for efficiency)
    total = await session.scalar(select(func.count()).select_from(statement.subquery()))

    # Apply pagination
    offset = (page - 1) * per_page
    statement = statement.offset(offset).limit(per_page)

    tasks_result = await session.execute(statement)
    tasks = tasks_result.scalars().all()

    logger.debug(f"Search found {len(tasks)} tasks for user {current_user_id}")

    return TaskList(
        tasks=[TaskPublic.model_validate(t) for t in tasks],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{task_id}", response_model=TaskPublic)
async def get_task(
    request: Request,
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskPublic:
    """Get a specific task by ID.

    Returns 404 (not 403) if task not found or doesn't belong to user
    to prevent ID enumeration attacks.
    """
    logger.debug(f"Get task: task_id={task_id}, user={current_user_id}")

    task = await get_task_or_404(task_id, current_user_id, session)
    return TaskPublic.model_validate(task)


@router.put("/{task_id}", response_model=TaskPublic)
async def update_task(
    request: Request,
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskPublic:
    """Update an existing task.

    Only updates fields that are provided in the request.
    Returns 404 if task doesn't exist or belong to user.
    """
    logger.info(f"Update task: task_id={task_id}, user={current_user_id}")

    task = await get_task_or_404(task_id, current_user_id, session)

    # Track changed fields for audit log
    changed_fields = {}

    # Update only provided fields
    if task_data.title is not None:
        changed_fields["title"] = {"old": task.title, "new": task_data.title}
        task.title = task_data.title

    if task_data.description is not None:
        changed_fields["description"] = {"old": task.description, "new": task_data.description}
        task.description = task_data.description

    if task_data.priority is not None:
        changed_fields["priority"] = {"old": task.priority.value, "new": task_data.priority.value}
        task.priority = task_data.priority

    if task_data.tags is not None:
        changed_fields["tags"] = {"old": task.tags, "new": task_data.tags}
        # Convert Tag models to dicts for JSON storage
        tags_as_dicts = [tag.to_dict() if hasattr(tag, 'to_dict') else tag for tag in task_data.tags]
        task.tags = tags_as_dicts

    if task_data.due_date is not None:
        changed_fields["due_date"] = {"old": task.due_date, "new": task_data.due_date}
        task.due_date = task_data.due_date

    if task_data.recurrence_pattern is not None:
        changed_fields["recurrence_pattern"] = {"old": task.recurrence_pattern, "new": task_data.recurrence_pattern}
        task.recurrence_pattern = task_data.recurrence_pattern

    if task_data.completed is not None:
        changed_fields["completed"] = {"old": task.completed, "new": task_data.completed}
        task.completed = task_data.completed

    task.updated_at = datetime.utcnow()
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Create audit log
    await create_task_log(
        session=session,
        task_id=task.id,
        user_id=current_user_id,
        action=Action.UPDATED,
        changed_fields=changed_fields,
    )
    await session.commit()

    logger.info(f"Task updated: id={task.id}")

    return TaskPublic.model_validate(task)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> dict:
    """Delete a task permanently.

    Returns 404 if task doesn't exist or belong to user.
    """
    logger.info(f"Delete task: task_id={task_id}, user={current_user_id}")

    # Verify task exists and belongs to user
    task = await get_task_or_404(task_id, current_user_id, session)

    # Delete audit logs first (foreign key constraint)
    from sqlalchemy import delete as sql_delete
    from app.models import TaskLog

    await session.execute(
        sql_delete(TaskLog).where(TaskLog.task_id == task_id)
    )

    # Now delete the task
    await session.delete(task)
    await session.commit()

    logger.info(f"Task deleted: id={task_id}, title={task.title!r}")

    return {"id": task_id, "message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=TaskPublic)
async def toggle_task_complete(
    request: Request,
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TaskPublic:
    """Toggle task completion status.

    Handles recurring tasks: if a recurring task is completed,
    automatically creates the next occurrence.
    """
    logger.info(f"Toggle complete: task_id={task_id}, user={current_user_id}")

    task = await get_task_or_404(task_id, current_user_id, session)

    # Toggle completion
    old_completed = task.completed
    new_completed = not old_completed
    task.completed = new_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Create audit log
    action = Action.COMPLETED if new_completed else Action.UNCOMPLETED
    await create_task_log(
        session=session,
        task_id=task.id,
        user_id=current_user_id,
        action=action,
        changed_fields={"completed": {"old": old_completed, "new": new_completed}},
    )
    await session.commit()

    # [Task]: T052 - Create notification for task completion
    # Send notification when task is marked complete
    if new_completed:
        await NotificationService.dispatch(
            session=session,
            user_id=current_user_id,
            type=NotificationType.TASK_COMPLETED,
            title=f"Task Completed: {task.title}",
            message=f"Great job! You completed: {task.title}",
            data={
                "task_id": task.id,
                "task_title": task.title,
            },
            related_task_id=task.id,
        )

    # Handle recurring task auto-creation
    if new_completed and task.recurrence_pattern:
        logger.info(f"Creating recurring task from: task_id={task_id}")

        # Calculate next due date based on recurrence pattern
        from datetime import timedelta

        base_date = task.due_date or datetime.utcnow()
        if task.recurrence_pattern == RecurrencePattern.DAILY:
            next_due = base_date + timedelta(days=1)
        elif task.recurrence_pattern == RecurrencePattern.WEEKLY:
            next_due = base_date + timedelta(weeks=1)
        elif task.recurrence_pattern == RecurrencePattern.MONTHLY:
            # Add approximately 30 days
            next_due = base_date + timedelta(days=30)
        else:
            next_due = None

        # Create new recurring task
        recurring_task = Task(
            user_id=current_user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            due_date=next_due,
            recurrence_pattern=task.recurrence_pattern,
        )

        session.add(recurring_task)
        await session.commit()
        await session.refresh(recurring_task)

        # Log the recurrence
        await create_task_log(
            session=session,
            task_id=recurring_task.id,
            user_id=current_user_id,
            action=Action.RECURRED,
            changed_fields={"parent_task_id": task.id, "next_due": next_due.isoformat() if next_due else None},
        )
        await session.commit()

        logger.info(f"Recurring task created: id={recurring_task.id}, due={next_due}")

    logger.info(f"Task completion toggled: id={task.id}, completed={new_completed}")

    return TaskPublic.model_validate(task)


@router.get("/{task_id}/logs", response_model=list[TaskLogPublic])
async def get_task_logs(
    request: Request,
    task_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> list[TaskLogPublic]:
    """Get audit log history for a task.

    Returns all modifications made to the task.
    Returns 404 if task doesn't exist or belong to user.
    """
    logger.debug(f"Get task logs: task_id={task_id}, user={current_user_id}")

    # Verify task exists and belongs to user
    await get_task_or_404(task_id, current_user_id, session)

    # Get logs
    statement = select(TaskLog).where(
        TaskLog.task_id == task_id
    ).order_by(TaskLog.created_at.desc())

    result = await session.execute(statement)
    logs = result.scalars().all()

    return [TaskLogPublic.model_validate(log) for log in logs]
