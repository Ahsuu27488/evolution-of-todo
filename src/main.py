#!/usr/bin/env python3
"""Entry point for Todo Console Application."""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add src directory to path for direct execution (allows running from anywhere)
_src_dir = Path(__file__).parent.resolve()
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from todo.cli.app import TodoCLI
from todo.services.task_service import TaskService
from todo.repository.memory import InMemoryTaskRepository
from todo.domain.task import Priority, Recurrence


def load_demo_data(service: TaskService) -> None:
    """Load mock data for testing and demonstration.

    Creates a variety of tasks with different priorities, tags,
    completion states, due dates, and recurrence patterns to showcase
    all Advanced Level features.
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    # High priority tasks with due dates
    service.create_task(
        title="Prepare hackathon presentation",
        description="Create slides and demo video for Phase 1 submission",
        priority=Priority.HIGH,
        tags={"hackathon", "urgent", "presentation"},
        due_date=tomorrow,  # Due tomorrow
    )
    service.create_task(
        title="Fix critical bug in login",
        description="Users cannot login with special characters in password",
        priority=Priority.HIGH,
        tags={"bug", "critical", "auth"},
        due_date=yesterday,  # Overdue (demonstrates red color)
    )

    # Medium priority tasks with recurring patterns
    service.create_task(
        title="Daily standup meeting",
        description="Team sync at 9 AM",
        priority=Priority.MEDIUM,
        tags={"work", "meeting"},
        due_date=today,  # Due today
        recurrence=Recurrence.DAILY,  # Recurring daily
    )
    service.create_task(
        title="Weekly team retrospective",
        description="Review sprint progress and improvements",
        priority=Priority.MEDIUM,
        tags={"work", "meeting"},
        due_date=next_week,
        recurrence=Recurrence.WEEKLY,  # Recurring weekly
    )
    service.create_task(
        title="Call mom",
        description="Weekly catch-up call",
        priority=Priority.MEDIUM,
        tags={"personal", "family"},
        due_date=today,
        recurrence=Recurrence.WEEKLY,
    )

    # Low priority tasks (some with no deadline)
    service.create_task(
        title="Organize desktop files",
        description="Sort downloads folder and delete old screenshots",
        priority=Priority.LOW,
        tags={"personal", "cleanup"},
        # No due date - demonstrates "(no deadline)" display
    )
    service.create_task(
        title="Research new Python libraries",
        description="Look into FastAPI, SQLModel for Phase 2",
        priority=Priority.LOW,
        tags={"learning", "research"},
        # No due date
    )
    service.create_task(
        title="Buy groceries",
        description="Milk, bread, eggs, cheese, vegetables",
        priority=Priority.LOW,
        tags={"shopping", "personal"},
        due_date=today + timedelta(days=2),
    )

    # Medium priority monthly recurring task
    service.create_task(
        title="Pay rent",
        description="Monthly rent payment",
        priority=Priority.MEDIUM,
        tags={"financial", "important"},
        due_date=date(today.year, today.month, 1) + timedelta(days=32),  # 1st of next month
        recurrence=Recurrence.MONTHLY,
    )

    # Mark some tasks as completed
    # Note: Completing recurring tasks will create new occurrences
    service.toggle_complete(7)  # Research libraries - completed (no recurrence)

    print(f"\n✓ Demo mode: Loaded 9 sample tasks with due dates and recurring patterns")
    print(f"  - Overdue: 1 | Due today: 2 | Upcoming: 3 | No deadline: 2")
    print(f"  - Recurring: 4 (Daily, Weekly x2, Monthly)")
    print(f"  - Completed: 1 | Pending: 8\n")


def main() -> None:
    """Initialize and run the Todo CLI application.

    Usage:
        python3 src/main.py          # Start with empty task list
        python3 src/main.py --demo   # Start with sample data for testing
    """
    repository = InMemoryTaskRepository()
    service = TaskService(repository)

    # Check for --demo flag
    if "--demo" in sys.argv or "-d" in sys.argv:
        load_demo_data(service)

    cli = TodoCLI(service)
    cli.run()


if __name__ == "__main__":
    main()
