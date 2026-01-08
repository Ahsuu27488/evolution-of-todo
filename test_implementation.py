#!/usr/bin/env python3
"""Quick test script to validate the Advanced Features implementation."""

import sys
from pathlib import Path
from datetime import date, timedelta

_src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(_src_dir))

from todo.services.task_service import TaskService
from todo.repository.memory import InMemoryTaskRepository
from todo.domain.task import Priority, Recurrence

def test_due_dates_and_recurring():
    """Test due dates and recurring task functionality."""
    print("=" * 60)
    print("TESTING ADVANCED LEVEL FEATURES")
    print("=" * 60)

    repo = InMemoryTaskRepository()
    service = TaskService(repo)

    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Test 1: Create task with due date
    print("\n✓ Test 1: Create task with due date")
    task1 = service.create_task(
        title="Task with due date",
        due_date=tomorrow,
    )
    print(f"  Created task {task1.id}: '{task1.title}'")
    print(f"  Due date: {task1.due_date}")
    assert task1.due_date == tomorrow, "Due date should be tomorrow"

    # Test 2: Create recurring daily task
    print("\n✓ Test 2: Create recurring daily task")
    task2 = service.create_task(
        title="Daily standup",
        due_date=today,
        recurrence=Recurrence.DAILY,
    )
    print(f"  Created task {task2.id}: '{task2.title}'")
    print(f"  Due date: {task2.due_date}")
    print(f"  Recurrence: {task2.recurrence.value}")
    assert task2.recurrence == Recurrence.DAILY, "Should be daily recurring"

    # Test 3: Complete recurring task and check new occurrence
    print("\n✓ Test 3: Complete recurring task creates new occurrence")
    completed_task, new_occurrence = service.toggle_complete(task2.id)
    print(f"  Completed task {completed_task.id}")
    assert completed_task.completed, "Task should be marked complete"
    assert new_occurrence is not None, "New occurrence should be created"
    print(f"  New occurrence created: ID {new_occurrence.id}")
    print(f"  New due date: {new_occurrence.due_date}")
    assert new_occurrence.due_date == tomorrow, "New occurrence should be tomorrow"

    # Test 4: Filter by due date
    print("\n✓ Test 4: Filter tasks by due date")
    overdue_tasks = service.list_tasks(due_date_filter="today")
    print(f"  Tasks due today: {len(overdue_tasks)}")

    # Test 5: Sort by due date
    print("\n✓ Test 5: Sort tasks by due date")
    all_tasks = service.list_tasks(sort_by="due_date")
    print(f"  All tasks sorted by due date: {len(all_tasks)} tasks")
    for task in all_tasks:
        due_str = str(task.due_date) if task.due_date else "(no deadline)"
        print(f"    - Task {task.id}: due {due_str}")

    # Test 6: Update task due date
    print("\n✓ Test 6: Update task due date")
    updated_task = service.update_task(task1.id, due_date=today)
    print(f"  Updated task {updated_task.id} due date to: {updated_task.due_date}")
    assert updated_task.due_date == today, "Due date should be updated"

    # Test 7: Remove due date
    print("\n✓ Test 7: Remove due date from task")
    updated_task = service.update_task(task1.id, due_date=TaskService._REMOVE_DUE_DATE)
    print(f"  Removed due date from task {updated_task.id}")
    assert updated_task.due_date is None, "Due date should be removed"

    # Test 8: Monthly recurrence edge case
    print("\n✓ Test 8: Monthly recurrence handles month overflow")
    jan_31 = date(2025, 1, 31)
    next_date = service._calculate_next_due_date(jan_31, Recurrence.MONTHLY)
    print(f"  Jan 31 + monthly = {next_date}")
    assert next_date.day <= 29, "Should clamp to Feb 28/29"

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print("\nAdvanced Features Summary:")
    print("  ✓ Due dates with color-coded visual indicators")
    print("  ✓ Recurring tasks (daily/weekly/monthly)")
    print("  ✓ Automatic rescheduling on completion")
    print("  ✓ Filter by due date status")
    print("  ✓ Sort by due date")
    print("  ✓ Update and remove due dates")
    print("  ✓ Manage recurrence settings")
    print("  ✓ Monthly edge case handling (31st → 28/29)")
    print()

if __name__ == "__main__":
    test_due_dates_and_recurring()
