"""Custom exceptions for the todo application."""


class TodoError(Exception):
    """Base exception for all todo application errors.

    All domain-specific exceptions inherit from this class,
    enabling catch-all handling at the CLI layer.
    """
    pass


class TaskNotFoundError(TodoError):
    """Raised when a task with the given ID does not exist.

    Attributes:
        task_id: The ID that was not found
    """
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class ValidationError(TodoError):
    """Raised when input validation fails.

    Attributes:
        field: The field that failed validation
        message: Description of the validation failure
    """
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")
