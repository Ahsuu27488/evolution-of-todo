"""Business logic for task operations."""

import calendar
from datetime import date, timedelta

from todo.domain.task import Task, Priority, Recurrence
from todo.domain.exceptions import TaskNotFoundError, ValidationError
from todo.repository.base import TaskRepository


class TaskService:
    """Task management business logic.

    Handles validation, CRUD operations, and query operations.
    Designed for reuse in Phase II FastAPI backend.

    Attributes:
        _repository: The task repository for data access
    """

    def __init__(self, repository: TaskRepository) -> None:
        """Initialize service with a repository.

        Args:
            repository: Task repository implementation
        """
        self._repository = repository

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: set[str] | None = None,
        due_date: date | None = None,
        recurrence: Recurrence = Recurrence.NONE,
    ) -> Task:
        """Create a new task with validation.

        Args:
            title: Task title (required, 1-200 chars)
            description: Optional description (max 1000 chars)
            priority: Priority level (default: MEDIUM)
            tags: Optional set of tags
            due_date: Optional deadline date
            recurrence: Repeat pattern (default: NONE)

        Returns:
            The created task with assigned ID

        Raises:
            ValidationError: If validation fails
        """
        # Validate title
        title = title.strip()
        if not title:
            raise ValidationError("title", "Title is required")
        if len(title) > 200:
            raise ValidationError("title", "Title must be 200 characters or less")

        # Validate description
        description = description.strip()
        if len(description) > 1000:
            raise ValidationError("description", "Description must be 1000 characters or less")

        # Normalize tags
        normalized_tags = self._normalize_tags(tags or set())

        task = Task(
            id=0,  # Will be assigned by repository
            title=title,
            description=description,
            priority=priority,
            tags=normalized_tags,
            due_date=due_date,
            recurrence=recurrence,
        )
        return self._repository.add(task)

    def get_task(self, task_id: int) -> Task:
        """Get a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            The task

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    # Sentinel value to indicate "remove due date" vs "don't change"
    _REMOVE_DUE_DATE = object()

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | None = None,
        tags: set[str] | None = None,
        due_date: date | None | object = None,
        recurrence: Recurrence | None = None,
    ) -> Task:
        """Update an existing task (partial update).

        Only provided fields are updated; others remain unchanged.

        Args:
            task_id: The task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            tags: New tags - replaces existing (optional)
            due_date: New due date, None to skip, _REMOVE_DUE_DATE to clear (optional)
            recurrence: New recurrence pattern (optional)

        Returns:
            The updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            ValidationError: If validation fails
        """
        task = self.get_task(task_id)

        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationError("title", "Title cannot be empty")
            if len(title) > 200:
                raise ValidationError("title", "Title must be 200 characters or less")
            task.title = title

        if description is not None:
            description = description.strip()
            if len(description) > 1000:
                raise ValidationError("description", "Description must be 1000 characters or less")
            task.description = description

        if priority is not None:
            task.priority = priority

        if tags is not None:
            task.tags = self._normalize_tags(tags)

        # Handle due_date: None means "don't change", _REMOVE_DUE_DATE means "clear it"
        if due_date is self._REMOVE_DUE_DATE:
            task.due_date = None
        elif due_date is not None:
            task.due_date = due_date  # type: ignore[assignment]

        if recurrence is not None:
            task.recurrence = recurrence

        return self._repository.update(task)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task to delete

        Returns:
            True if deleted, False if not found
        """
        return self._repository.delete(task_id)

    def toggle_complete(self, task_id: int) -> tuple[Task, Task | None]:
        """Toggle a task's completion status.

        For recurring tasks being completed:
        - Current task is marked complete
        - New task occurrence is created with next due date

        Args:
            task_id: The task to toggle

        Returns:
            Tuple of (updated_task, new_occurrence_or_None)
            - new_occurrence is None if task is not recurring or being uncompleted

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = self.get_task(task_id)
        was_completed = task.completed
        task.completed = not task.completed
        self._repository.update(task)

        new_occurrence = None

        # Create new occurrence for recurring tasks being marked complete
        if (not was_completed and task.completed and
            task.recurrence != Recurrence.NONE and
            task.due_date is not None):

            next_due_date = self._calculate_next_due_date(task.due_date, task.recurrence)

            if next_due_date is not None:
                # Create new task with same properties but new due date
                new_occurrence = self.create_task(
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    tags=task.tags.copy(),
                    due_date=next_due_date,
                    recurrence=task.recurrence,
                )

        return task, new_occurrence

    def list_tasks(
        self,
        status: str | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        due_date_filter: str | None = None,
    ) -> list[Task]:
        """List tasks with optional filtering and sorting.

        Args:
            status: Filter by "pending" or "completed"
            priority: Filter by priority level
            tag: Filter by tag (case-insensitive)
            search: Search keyword in title/description
            sort_by: Sort field: "id", "priority", "title", "created", "status", "due_date"
            due_date_filter: Filter by due date: "overdue", "today", "this_week", "no_deadline"

        Returns:
            List of matching tasks (may be empty)
        """
        tasks = self._repository.get_all()

        # Apply status filter
        if status == "pending":
            tasks = [t for t in tasks if not t.completed]
        elif status == "completed":
            tasks = [t for t in tasks if t.completed]

        # Apply priority filter
        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]

        # Apply tag filter
        if tag:
            tag_lower = tag.lower()
            tasks = [t for t in tasks if tag_lower in t.tags]

        # Apply search filter
        if search:
            search_lower = search.lower()
            tasks = [
                t for t in tasks
                if search_lower in t.title.lower() or search_lower in t.description.lower()
            ]

        # Apply due date filter
        if due_date_filter:
            today = date.today()
            if due_date_filter == "overdue":
                tasks = [t for t in tasks if t.due_date is not None and t.due_date < today]
            elif due_date_filter == "today":
                tasks = [t for t in tasks if t.due_date == today]
            elif due_date_filter == "this_week":
                week_end = today + timedelta(days=7)
                tasks = [t for t in tasks if t.due_date is not None and today <= t.due_date <= week_end]
            elif due_date_filter == "no_deadline":
                tasks = [t for t in tasks if t.due_date is None]

        # Apply sorting
        if sort_by:
            tasks = self._sort_tasks(tasks, sort_by)

        return tasks

    def get_stats(self) -> dict[str, int]:
        """Get task statistics.

        Returns:
            Dictionary with total, pending, and completed counts
        """
        all_tasks = self._repository.get_all()
        pending = sum(1 for t in all_tasks if not t.completed)
        return {
            "total": len(all_tasks),
            "pending": pending,
            "completed": len(all_tasks) - pending,
        }

    def _normalize_tags(self, tags: set[str]) -> set[str]:
        """Normalize tags: lowercase, trim, dedupe, enforce limits.

        Args:
            tags: Raw tag set

        Returns:
            Normalized tag set (max 10 tags, each max 30 chars)
        """
        normalized = set()
        for tag in tags:
            tag = tag.strip().lower()
            if tag and len(tag) <= 30:
                normalized.add(tag)

        # Enforce max 10 tags
        if len(normalized) > 10:
            normalized = set(list(normalized)[:10])

        return normalized

    def _calculate_next_due_date(self, current_date: date, recurrence: Recurrence) -> date | None:
        """Calculate the next occurrence date based on recurrence pattern.

        Args:
            current_date: The current due date
            recurrence: The recurrence pattern

        Returns:
            Next due date, or None if recurrence is NONE

        Notes:
            - Always returns a date >= today (skips past dates)
            - Monthly handles day overflow (Jan 31 -> Feb 28)
        """
        if recurrence == Recurrence.NONE:
            return None

        today = date.today()

        if recurrence == Recurrence.DAILY:
            next_date = current_date + timedelta(days=1)
        elif recurrence == Recurrence.WEEKLY:
            next_date = current_date + timedelta(days=7)
        elif recurrence == Recurrence.MONTHLY:
            # Calculate same day next month, handling day overflow
            next_month = current_date.month % 12 + 1
            next_year = current_date.year + (1 if next_month == 1 else 0)
            # Get last day of target month to handle overflow (e.g., Jan 31 -> Feb 28)
            last_day_of_month = calendar.monthrange(next_year, next_month)[1]
            day = min(current_date.day, last_day_of_month)
            next_date = date(next_year, next_month, day)
        else:
            return None

        # Ensure result is in the future (skip past dates if completing late)
        while next_date < today:
            if recurrence == Recurrence.DAILY:
                next_date += timedelta(days=1)
            elif recurrence == Recurrence.WEEKLY:
                next_date += timedelta(days=7)
            elif recurrence == Recurrence.MONTHLY:
                next_month = next_date.month % 12 + 1
                next_year = next_date.year + (1 if next_month == 1 else 0)
                last_day_of_month = calendar.monthrange(next_year, next_month)[1]
                day = min(next_date.day, last_day_of_month)
                next_date = date(next_year, next_month, day)

        return next_date

    def _sort_tasks(self, tasks: list[Task], sort_by: str) -> list[Task]:
        """Sort tasks by specified criteria.

        Args:
            tasks: List of tasks to sort
            sort_by: Sort field

        Returns:
            Sorted list of tasks
        """
        if sort_by == "priority":
            # High priority first (higher IntEnum value = higher priority)
            return sorted(tasks, key=lambda t: t.priority, reverse=True)
        elif sort_by == "title":
            return sorted(tasks, key=lambda t: t.title.lower())
        elif sort_by == "created":
            # Newest first by default
            return sorted(tasks, key=lambda t: t.created_at, reverse=True)
        elif sort_by == "status":
            # Pending first (False < True, so not completed first)
            return sorted(tasks, key=lambda t: t.completed)
        elif sort_by == "due_date":
            # Sort by due date ascending, with None (no deadline) at the end
            return sorted(tasks, key=lambda t: (t.due_date is None, t.due_date or date.max))
        elif sort_by == "id":
            return sorted(tasks, key=lambda t: t.id)
        return tasks
