"""Abstract base repository for task persistence."""

from abc import ABC, abstractmethod

from todo.domain.task import Task


class TaskRepository(ABC):
    """Abstract base class for task storage.

    Defines the contract that all task repositories must implement.
    This abstraction enables swapping storage backends (in-memory → PostgreSQL)
    without changing service layer code.
    """

    @abstractmethod
    def add(self, task: Task) -> Task:
        """Add a new task and assign its ID.

        Args:
            task: Task to add (id will be assigned by repository)

        Returns:
            The task with its assigned ID
        """
        ...

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            The task if found, None otherwise
        """
        ...

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Retrieve all tasks.

        Returns:
            List of all tasks (may be empty)
        """
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update an existing task.

        Args:
            task: Task with updated fields (id must exist)

        Returns:
            The updated task

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist
        """
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The unique task identifier

        Returns:
            True if task was deleted, False if not found
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Count total number of tasks.

        Returns:
            Total task count
        """
        ...
