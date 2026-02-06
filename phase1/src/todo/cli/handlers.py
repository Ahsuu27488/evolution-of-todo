"""Menu option handlers for CLI application."""

from typing import TYPE_CHECKING

from todo.domain.task import Priority
from todo.domain.exceptions import TaskNotFoundError, ValidationError
from todo.cli.display import (
    print_header,
    print_error,
    print_success,
    print_info,
    format_task_table,
    format_empty_task_list,
    format_tags,
    format_priority_display,
    format_due_date_display,
    show_update_submenu,
    show_task_picker,
    wait_for_enter,
)
from todo.cli.validators import (
    get_task_id_input,
    get_title_input,
    get_description_input,
    get_priority_input,
    get_tags_input,
    get_yes_no_input,
    get_choice_input,
    get_input,
    get_due_date_input,
    get_recurrence_input,
)

if TYPE_CHECKING:
    from todo.cli.app import TodoCLI


def view_tasks_handler(cli: "TodoCLI") -> None:
    """Handle viewing all tasks with current filter/sort.

    Args:
        cli: The CLI application instance
    """
    print_header("View Tasks")

    # Build filter/sort labels for display
    filter_label = "All"
    if cli.current_filter:
        if cli.current_filter.status:
            filter_label = f"Status: {cli.current_filter.status}"
        elif cli.current_filter.priority:
            filter_label = f"Priority: {cli.current_filter.priority.name}"
        elif cli.current_filter.tag:
            filter_label = f"Tag: #{cli.current_filter.tag}"
        elif cli.current_filter.due_date_filter:
            filter_label = f"Due: {cli.current_filter.due_date_filter.replace('_', ' ').title()}"

    sort_label = cli.current_sort.field.title().replace("_", " ")
    if cli.current_sort.reverse:
        sort_label += " (desc)"

    # Get filtered/sorted tasks
    tasks = cli.service.list_tasks(
        status=cli.current_filter.status if cli.current_filter else None,
        priority=cli.current_filter.priority if cli.current_filter else None,
        tag=cli.current_filter.tag if cli.current_filter else None,
        due_date_filter=cli.current_filter.due_date_filter if cli.current_filter else None,
        sort_by=cli.current_sort.field,
    )

    if not tasks:
        if cli.current_filter and (cli.current_filter.status or cli.current_filter.priority or
                                   cli.current_filter.tag or cli.current_filter.due_date_filter):
            print_info("No tasks match the current filter.")
        else:
            print(format_empty_task_list())
    else:
        print(format_task_table(tasks, filter_label, sort_label))

    wait_for_enter()


def add_task_handler(cli: "TodoCLI") -> None:
    """Handle adding a new task.

    Args:
        cli: The CLI application instance
    """
    from todo.domain.task import Recurrence

    print_header("Add New Task")

    # Get title (required)
    title = None
    while title is None:
        title = get_title_input()

    # Get optional fields
    description = get_description_input()
    priority = get_priority_input()
    tags = get_tags_input()

    # Get due date (optional)
    due_date = get_due_date_input()

    # Only prompt for recurrence if due date is set
    recurrence = Recurrence.NONE
    if due_date is not None:
        recurrence = get_recurrence_input()

    try:
        task = cli.service.create_task(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurrence=recurrence,
        )

        print_success("Task created successfully!")
        print_info(f"ID: {task.id}")
        print_info(f"Title: {task.title}")
        print_info(f"Priority: {format_priority_display(task.priority)}")
        print_info(f"Due: {format_due_date_display(task.due_date, task.recurrence)}")
        print_info(f"Tags: {format_tags(task.tags)}")

    except ValidationError as e:
        print_error(str(e))

    wait_for_enter()


def update_task_handler(cli: "TodoCLI") -> None:
    """Handle updating an existing task.

    Args:
        cli: The CLI application instance
    """
    from todo.services.task_service import TaskService

    print_header("Update Task")

    # Show available tasks first
    tasks = cli.service.list_tasks()
    if not tasks:
        print_info("No tasks available to update.")
        wait_for_enter()
        return

    show_task_picker(tasks, "update")

    # Get task ID
    task_id = get_task_id_input()
    if task_id is None:
        wait_for_enter()
        return

    try:
        task = cli.service.get_task(task_id)
    except TaskNotFoundError as e:
        print_error(str(e))
        wait_for_enter()
        return

    # Show current task and update options
    show_update_submenu(task)

    choice = get_choice_input("Enter choice (1-7): ", ["1", "2", "3", "4", "5", "6", "7"])
    if choice is None or choice == "7":
        print_info("Update cancelled.")
        wait_for_enter()
        return

    try:
        if choice == "1":  # Title
            new_title = get_title_input("Enter new title: ")
            if new_title:
                cli.service.update_task(task_id, title=new_title)
                print_success(f"Title updated to: {new_title}")

        elif choice == "2":  # Description
            new_desc = get_description_input("Enter new description: ")
            cli.service.update_task(task_id, description=new_desc)
            print_success("Description updated.")

        elif choice == "3":  # Priority
            new_priority = get_priority_input()
            cli.service.update_task(task_id, priority=new_priority)
            print_success(f"Priority updated to: {format_priority_display(new_priority)}")

        elif choice == "4":  # Tags
            new_tags = get_tags_input("Enter new tags (replaces existing): ")
            cli.service.update_task(task_id, tags=new_tags)
            print_success(f"Tags updated to: {format_tags(new_tags)}")

        elif choice == "5":  # Due Date
            print_info("Enter new due date (leave empty to remove deadline):")
            new_due_date = get_due_date_input("New due date (YYYY-MM-DD): ")
            if new_due_date is None:
                # User pressed Enter - remove the due date
                cli.service.update_task(task_id, due_date=TaskService._REMOVE_DUE_DATE)
                print_success("Due date removed.")
            else:
                cli.service.update_task(task_id, due_date=new_due_date)
                print_success(f"Due date updated to: {new_due_date}")

        elif choice == "6":  # Recurrence
            new_recurrence = get_recurrence_input()
            cli.service.update_task(task_id, recurrence=new_recurrence)
            print_success(f"Recurrence updated to: {new_recurrence.value}")

    except ValidationError as e:
        print_error(str(e))
    except TaskNotFoundError as e:
        print_error(str(e))

    wait_for_enter()


def delete_task_handler(cli: "TodoCLI") -> None:
    """Handle deleting a task with confirmation.

    Args:
        cli: The CLI application instance
    """
    print_header("Delete Task")

    # Show available tasks first
    tasks = cli.service.list_tasks()
    if not tasks:
        print_info("No tasks available to delete.")
        wait_for_enter()
        return

    show_task_picker(tasks, "delete")

    # Get task ID
    task_id = get_task_id_input()
    if task_id is None:
        wait_for_enter()
        return

    try:
        task = cli.service.get_task(task_id)
    except TaskNotFoundError as e:
        print_error(str(e))
        wait_for_enter()
        return

    # Show task details before confirmation
    print(f"\nTask to delete:")
    print_info(f"ID: {task.id}")
    print_info(f"Title: {task.title}")
    print_info(f"Priority: {format_priority_display(task.priority)}")

    # Confirm deletion
    confirm = None
    while confirm is None:
        confirm = get_yes_no_input("\n⚠ Are you sure you want to delete this task? (y/n): ")

    if confirm:
        if cli.service.delete_task(task_id):
            print_success(f"Task {task_id} deleted successfully.")
        else:
            print_error(f"Failed to delete task {task_id}.")
    else:
        print_info("Operation cancelled. Task was not deleted.")

    wait_for_enter()


def toggle_complete_handler(cli: "TodoCLI") -> None:
    """Handle marking a task as complete/incomplete.

    For recurring tasks, creates next occurrence when completed.

    Args:
        cli: The CLI application instance
    """
    print_header("Mark Complete/Incomplete")

    # Show available tasks first
    tasks = cli.service.list_tasks()
    if not tasks:
        print_info("No tasks available.")
        wait_for_enter()
        return

    show_task_picker(tasks, "toggle")

    # Get task ID
    task_id = get_task_id_input()
    if task_id is None:
        wait_for_enter()
        return

    try:
        task, new_occurrence = cli.service.toggle_complete(task_id)
        status = "completed" if task.completed else "pending"
        print_success(f"Task {task_id} marked as {status}.")
        print_info(f"Title: {task.title}")

        # Show recurring task notification
        if new_occurrence is not None:
            print_success(f"Next occurrence scheduled for {new_occurrence.due_date}")
            print_info(f"New task ID: {new_occurrence.id}")

    except TaskNotFoundError as e:
        print_error(str(e))

    wait_for_enter()


def search_tasks_handler(cli: "TodoCLI") -> None:
    """Handle searching tasks by keyword.

    Args:
        cli: The CLI application instance
    """
    print_header("Search Tasks")

    search_term = get_input("Enter search term (searches title and description): ")

    tasks = cli.service.list_tasks(search=search_term if search_term else None)

    if not tasks:
        if search_term:
            print_info(f"No tasks found matching '{search_term}'.")
        else:
            print(format_empty_task_list())
    else:
        if search_term:
            print_success(f"Found {len(tasks)} task(s) matching '{search_term}':")
        print(format_task_table(tasks, f"Search: '{search_term}'" if search_term else "All", "ID"))

    wait_for_enter()


def filter_tasks_handler(cli: "TodoCLI") -> None:
    """Handle filtering tasks by status/priority/tag/due date.

    Args:
        cli: The CLI application instance
    """
    from todo.cli.app import FilterState

    print_header("Filter Tasks")

    # Show current filter
    if cli.current_filter and (cli.current_filter.status or cli.current_filter.priority or
                               cli.current_filter.tag or cli.current_filter.due_date_filter):
        print_info("Current filter active")
    else:
        print_info("No filter active")

    print("\nSelect filter type:")
    print("  1. By Status (pending/completed/all)")
    print("  2. By Priority (high/medium/low)")
    print("  3. By Tag")
    print("  4. By Due Date")
    print("  5. Clear all filters")

    choice = get_choice_input("Enter choice (1-5): ", ["1", "2", "3", "4", "5"])
    if choice is None:
        wait_for_enter()
        return

    if choice == "1":  # Status filter
        print("\nSelect status:")
        print("  1. Pending only")
        print("  2. Completed only")
        print("  3. All tasks")

        status_choice = get_choice_input("Enter choice (1-3): ", ["1", "2", "3"])
        if status_choice == "1":
            cli.current_filter = FilterState(status="pending")
            print_success("Filter applied: Showing pending tasks only.")
        elif status_choice == "2":
            cli.current_filter = FilterState(status="completed")
            print_success("Filter applied: Showing completed tasks only.")
        else:
            cli.current_filter = None
            print_success("Filter cleared: Showing all tasks.")

    elif choice == "2":  # Priority filter
        print("\nSelect priority:")
        print("  1. High")
        print("  2. Medium")
        print("  3. Low")

        priority_choice = get_choice_input("Enter choice (1-3): ", ["1", "2", "3"])
        if priority_choice == "1":
            cli.current_filter = FilterState(priority=Priority.HIGH)
            print_success("Filter applied: Showing high priority tasks only.")
        elif priority_choice == "2":
            cli.current_filter = FilterState(priority=Priority.MEDIUM)
            print_success("Filter applied: Showing medium priority tasks only.")
        elif priority_choice == "3":
            cli.current_filter = FilterState(priority=Priority.LOW)
            print_success("Filter applied: Showing low priority tasks only.")

    elif choice == "3":  # Tag filter
        tag = get_input("Enter tag to filter by: ").lower()
        if tag:
            cli.current_filter = FilterState(tag=tag)
            print_success(f"Filter applied: Showing tasks tagged with #{tag}.")
        else:
            print_info("No tag entered. Filter not applied.")

    elif choice == "4":  # Due Date filter
        print("\nSelect due date filter:")
        print("  1. Overdue")
        print("  2. Due Today")
        print("  3. Due This Week")
        print("  4. No Deadline")
        print("  5. All tasks")

        due_choice = get_choice_input("Enter choice (1-5): ", ["1", "2", "3", "4", "5"])
        if due_choice == "1":
            cli.current_filter = FilterState(due_date_filter="overdue")
            print_success("Filter applied: Showing overdue tasks only.")
        elif due_choice == "2":
            cli.current_filter = FilterState(due_date_filter="today")
            print_success("Filter applied: Showing tasks due today.")
        elif due_choice == "3":
            cli.current_filter = FilterState(due_date_filter="this_week")
            print_success("Filter applied: Showing tasks due this week.")
        elif due_choice == "4":
            cli.current_filter = FilterState(due_date_filter="no_deadline")
            print_success("Filter applied: Showing tasks with no deadline.")
        else:
            cli.current_filter = None
            print_success("Filter cleared: Showing all tasks.")

    elif choice == "5":  # Clear filters
        cli.current_filter = None
        print_success("All filters cleared.")

    wait_for_enter()


def sort_tasks_handler(cli: "TodoCLI") -> None:
    """Handle sorting tasks by various criteria.

    Args:
        cli: The CLI application instance
    """
    from todo.cli.app import SortState

    print_header("Sort Tasks")

    print(f"Current sort: {cli.current_sort.field.title().replace('_', ' ')}")

    print("\nSelect sort criteria:")
    print("  1. By Priority (high → low)")
    print("  2. By Title (A → Z)")
    print("  3. By Created Date (newest first)")
    print("  4. By Created Date (oldest first)")
    print("  5. By Status (pending first)")
    print("  6. By Due Date (earliest first)")
    print("  7. Default (by ID)")

    choice = get_choice_input("Enter choice (1-7): ", ["1", "2", "3", "4", "5", "6", "7"])
    if choice is None:
        wait_for_enter()
        return

    sort_map = {
        "1": SortState(field="priority", reverse=True),
        "2": SortState(field="title", reverse=False),
        "3": SortState(field="created", reverse=True),
        "4": SortState(field="created", reverse=False),
        "5": SortState(field="status", reverse=False),
        "6": SortState(field="due_date", reverse=False),
        "7": SortState(field="id", reverse=False),
    }

    cli.current_sort = sort_map[choice]
    print_success(f"Tasks sorted by {cli.current_sort.field.replace('_', ' ')}.")

    wait_for_enter()


def exit_handler(cli: "TodoCLI") -> None:
    """Handle graceful application exit.

    Args:
        cli: The CLI application instance
    """
    print_header("Exit")
    print("Thank you for using Todo Console App!")
    print("Goodbye! 👋")
    cli.running = False
