"""In-memory implementation of TaskRepository."""

from todo.domain.task import Task
from todo.domain.exceptions import TaskNotFoundError
from todo.repository.base import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """In-memory task storage using dict with O(1) lookup.

    Tasks are stored in a dictionary keyed by task ID.
    IDs are sequential and never reused after deletion.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects
        _next_id: Next ID to assign (never decremented)
    """

    def __init__(self) -> None:
        """Initialize empty repository."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> Task:
        """Add a new task with auto-assigned ID.

        Args:
            task: Task to add (id field will be overwritten)

        Returns:
            Task with assigned ID
        """
        task.id = self._next_id
        self._next_id += 1
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            The task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Retrieve all tasks ordered by ID.

        Returns:
            List of all tasks sorted by ID (creation order)
        """
        return list(self._tasks.values())

    def update(self, task: Task) -> Task:
        """Update an existing task.

        Args:
            task: Task with updated fields

        Returns:
            The updated task

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        if task.id not in self._tasks:
            raise TaskNotFoundError(task.id)
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Note: The deleted ID will never be reused.

        Args:
            task_id: The unique task identifier

        Returns:
            True if task was deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def count(self) -> int:
        """Count total number of tasks.

        Returns:
            Total task count
        """
        return len(self._tasks)
