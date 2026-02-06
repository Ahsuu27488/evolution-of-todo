"""Main CLI application class and state management."""

from dataclasses import dataclass
from typing import Callable

from todo.domain.task import Priority
from todo.services.task_service import TaskService
from todo.cli.display import show_main_menu, print_error
from todo.cli.validators import get_choice_input


@dataclass
class FilterState:
    """Tracks current filter settings.

    Only one filter type can be active at a time.
    """
    status: str | None = None      # "pending" or "completed"
    priority: Priority | None = None
    tag: str | None = None
    due_date_filter: str | None = None  # "overdue", "today", "this_week", "no_deadline"


@dataclass
class SortState:
    """Tracks current sort settings."""
    field: str = "id"              # "id", "priority", "title", "created", "status"
    reverse: bool = False


class TodoCLI:
    """Main CLI application managing user interaction.

    Attributes:
        service: TaskService for business operations
        running: Flag controlling main loop
        current_filter: Active filter state (None = no filter)
        current_sort: Active sort state
    """

    def __init__(self, service: TaskService) -> None:
        """Initialize CLI with a TaskService.

        Args:
            service: The task service for business operations
        """
        self.service = service
        self.running = True
        self.current_filter: FilterState | None = None
        self.current_sort: SortState = SortState()
        self._handlers: dict[str, Callable[["TodoCLI"], None]] = self._setup_handlers()

    def _setup_handlers(self) -> dict[str, Callable[["TodoCLI"], None]]:
        """Set up menu option handlers.

        Returns:
            Dictionary mapping menu choices to handler functions
        """
        from todo.cli.handlers import (
            view_tasks_handler,
            add_task_handler,
            update_task_handler,
            delete_task_handler,
            toggle_complete_handler,
            search_tasks_handler,
            filter_tasks_handler,
            sort_tasks_handler,
            exit_handler,
        )

        return {
            "1": view_tasks_handler,
            "2": add_task_handler,
            "3": update_task_handler,
            "4": delete_task_handler,
            "5": toggle_complete_handler,
            "6": search_tasks_handler,
            "7": filter_tasks_handler,
            "8": sort_tasks_handler,
            "9": exit_handler,
        }

    def run(self) -> None:
        """Run the main application loop.

        Handles KeyboardInterrupt for graceful exit.
        Catches all other exceptions to prevent crashes.
        """
        try:
            while self.running:
                show_main_menu()
                choice = get_choice_input(
                    "Enter your choice (1-9): ",
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                )

                if choice is None:
                    continue

                handler = self._handlers.get(choice)
                if handler:
                    try:
                        handler(self)
                    except Exception as e:
                        print_error(f"An error occurred: {e}")
                        print_error("Please try again.")
                else:
                    print_error("Invalid option. Please select 1-9.")

        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
        except Exception as e:
            print_error(f"An unexpected error occurred: {e}")
            print_error("Application will now exit.")
