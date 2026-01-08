"""Display utilities for CLI output formatting."""

import os
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from todo.domain.task import Task, Recurrence

# ANSI color codes with fallback
COLORS_ENABLED = os.environ.get("NO_COLOR") is None and os.environ.get("TERM") != "dumb"


class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[91m" if COLORS_ENABLED else ""
    GREEN = "\033[92m" if COLORS_ENABLED else ""
    YELLOW = "\033[93m" if COLORS_ENABLED else ""
    GRAY = "\033[90m" if COLORS_ENABLED else ""
    BOLD = "\033[1m" if COLORS_ENABLED else ""
    RESET = "\033[0m" if COLORS_ENABLED else ""


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{Colors.BOLD}═══ {title.upper()} ═══{Colors.RESET}\n")


def print_error(message: str) -> None:
    """Print an error message in red."""
    print(f"{Colors.RED}✗ Error: {message}{Colors.RESET}")


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"  {message}")


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def format_error(message: str) -> str:
    """Format an error message consistently."""
    return f"{Colors.RED}✗ Error: {message}{Colors.RESET}"


def format_tags(tags: set[str]) -> str:
    """Format tags as hashtags or placeholder."""
    if not tags:
        return f"{Colors.GRAY}(no tags){Colors.RESET}"
    return " ".join(f"#{tag}" for tag in sorted(tags))


def format_status(completed: bool) -> str:
    """Format completion status with visual indicator."""
    if completed:
        return f"{Colors.GREEN}[✓]{Colors.RESET}"
    return "[ ]"


def format_priority_display(priority: "Priority") -> str:
    """Format priority with color coding."""
    from todo.domain.task import Priority

    color_map = {
        Priority.HIGH: Colors.RED,
        Priority.MEDIUM: Colors.YELLOW,
        Priority.LOW: Colors.GRAY,
    }
    color = color_map.get(priority, "")
    return f"{color}{priority.display}{Colors.RESET}"


def format_due_date_display(due_date: date | None, recurrence: "Recurrence | None" = None) -> str:
    """Format due date for display with color codes and recurrence indicator.

    Displays due date status with appropriate color coding:
    - Overdue: red text showing days overdue
    - Due today/tomorrow: yellow text with warning
    - Future: gray text showing days until due
    - No deadline: gray "(no deadline)" placeholder

    Args:
        due_date: The due date or None if no deadline
        recurrence: Optional recurrence pattern for indicator display

    Returns:
        Formatted string with ANSI color codes

    Examples:
        "(no deadline)"              [gray]
        "Overdue by 2d"              [red]
        "Due today! (Daily)"         [yellow]
        "In 5d (2025-01-05) (Weekly)" [gray]
    """
    from todo.domain.task import Recurrence

    # Handle no deadline case
    if due_date is None:
        return f"{Colors.GRAY}(no deadline){Colors.RESET}"

    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Build recurrence suffix if applicable
    recur_suffix = ""
    if recurrence is not None and recurrence != Recurrence.NONE:
        recur_suffix = f" {recurrence.display}"

    # Determine status and format
    if due_date < today:
        days_overdue = (today - due_date).days
        return f"{Colors.RED}Overdue {days_overdue}d{recur_suffix}{Colors.RESET}"
    elif due_date == today:
        return f"{Colors.YELLOW}Due today!{recur_suffix}{Colors.RESET}"
    elif due_date == tomorrow:
        return f"{Colors.YELLOW}Due tomorrow{recur_suffix}{Colors.RESET}"
    else:
        days_until = (due_date - today).days
        return f"{Colors.GRAY}In {days_until}d ({due_date}){recur_suffix}{Colors.RESET}"


def format_task_row(task: "Task") -> str:
    """Format a single task for display in a list.

    Includes ID, status, priority, title, due date (with recurrence), and tags.
    """
    status = format_status(task.completed)
    priority = format_priority_display(task.priority)
    due = format_due_date_display(task.due_date, task.recurrence)
    tags = format_tags(task.tags)

    # Truncate title if too long
    title = task.title[:25] + "..." if len(task.title) > 25 else task.title

    return f"| {task.id:3d} | {status} | {priority:18s} | {title:28s} | {due:22s} | {tags}"


def format_task_table(
    tasks: list["Task"],
    filter_label: str = "All",
    sort_label: str = "ID"
) -> str:
    """Format a list of tasks as a table.

    Displays tasks with ID, status, priority, title, due date, and tags columns.
    """
    lines = []

    # Simple header
    lines.append("")
    lines.append(f"{Colors.BOLD}                              YOUR TASKS{Colors.RESET}")
    lines.append(f"+{'-'*100}+")

    # Stats
    total = len(tasks)
    pending = sum(1 for t in tasks if not t.completed)
    completed = total - pending
    lines.append(f"| Total: {total} | Pending: {pending} | Completed: {completed}")
    lines.append(f"| Filter: {filter_label} | Sort: {sort_label}")
    lines.append(f"+{'-'*100}+")

    # Column headers (added Due column)
    lines.append(f"| {'ID':>3} | Status | {'Priority':^18} | {'Title':^28} | {'Due':^22} | Tags")
    lines.append(f"+{'-'*5}+{'-'*8}+{'-'*20}+{'-'*30}+{'-'*24}+{'-'*15}")

    # Task rows
    for task in tasks:
        lines.append(format_task_row(task))

    lines.append(f"+{'-'*100}+")
    lines.append("")

    return "\n".join(lines)


def format_empty_task_list() -> str:
    """Format message for empty task list."""
    lines = [
        "",
        f"{Colors.BOLD}                         YOUR TASKS{Colors.RESET}",
        f"+{'-'*50}+",
        f"|                                                  |",
        f"|  {Colors.GRAY}No tasks yet! Use option 2 to add your first task.{Colors.RESET}",
        f"|                                                  |",
        f"+{'-'*50}+",
        "",
    ]
    return "\n".join(lines)


def show_main_menu() -> None:
    """Display the main application menu."""
    menu = f"""
{Colors.BOLD}+---------------------------------------+
|       TODO CONSOLE APP                |
+---------------------------------------+
|  1. View Tasks                        |
|  2. Add Task                          |
|  3. Update Task                       |
|  4. Delete Task                       |
|  5. Mark Complete/Incomplete          |
|  6. Search Tasks                      |
|  7. Filter Tasks                      |
|  8. Sort Tasks                        |
|  9. Exit                              |
+---------------------------------------+{Colors.RESET}"""
    print(menu)


def show_update_submenu(task: "Task") -> None:
    """Display the update task submenu with current values and options."""
    print(f"\nCurrent task:")
    print(f"  Title: {task.title}")
    print(f"  Description: {task.description or '(none)'}")
    print(f"  Priority: {task.priority.display}")
    print(f"  Tags: {format_tags(task.tags)}")
    print(f"  Due: {format_due_date_display(task.due_date, task.recurrence)}")
    print(f"  Status: {'Completed' if task.completed else 'Pending'}")
    print(f"\nWhat would you like to update?")
    print(f"  1. Title")
    print(f"  2. Description")
    print(f"  3. Priority")
    print(f"  4. Tags")
    print(f"  5. Due Date")
    print(f"  6. Recurrence")
    print(f"  7. Cancel")


def wait_for_enter() -> None:
    """Prompt user to press Enter to continue."""
    input("\nPress Enter to continue...")


def show_task_picker(tasks: list["Task"], action: str = "select") -> None:
    """Display a compact task list for ID selection.

    Shows tasks in a simple format to help users pick an ID.

    Args:
        tasks: List of tasks to display
        action: The action being performed (e.g., "update", "delete")
    """
    if not tasks:
        print(f"{Colors.GRAY}  No tasks available.{Colors.RESET}")
        return

    print(f"{Colors.BOLD}Available tasks:{Colors.RESET}")
    print(f"  {'ID':<4} {'Status':<6} {'Priority':<10} Title")
    print(f"  {'-'*4} {'-'*6} {'-'*10} {'-'*40}")

    for task in tasks:
        status = "✓" if task.completed else " "
        priority = task.priority.name[:3]  # HIGH->HIG, MEDIUM->MED, LOW->LOW
        title = task.title[:40] + "..." if len(task.title) > 40 else task.title
        print(f"  {task.id:<4} [{status}]    {priority:<10} {title}")

    print()
