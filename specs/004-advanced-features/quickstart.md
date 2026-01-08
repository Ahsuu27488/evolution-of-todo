# Quickstart: Advanced Level Features

**Feature**: 004-advanced-features
**Date**: 2025-12-27

---

## Overview

This guide helps developers quickly understand and implement the Advanced Level features for the Phase 1 Console App.

---

## Prerequisites

- Existing Phase 1 Console App with 9 features working
- Python 3.10+
- Understanding of existing codebase:
  - `src/todo/domain/task.py` - Task entity
  - `src/todo/services/task_service.py` - Business logic
  - `src/todo/cli/handlers.py` - CLI handlers
  - `src/todo/cli/display.py` - Display utilities
  - `src/todo/cli/validators.py` - Input validation

---

## Implementation Order

Follow this order to implement features incrementally:

### Phase A: Due Dates (P1 - Required)

1. **Add Recurrence enum** to `domain/task.py`
2. **Extend Task dataclass** with `due_date` and `recurrence` fields
3. **Add date validation** to `cli/validators.py`
4. **Extend create_task()** in service and CLI
5. **Add due date display** to task table
6. **Extend update handler** with due date option
7. **Add due date filter/sort** options

### Phase B: Recurring Tasks (P2 - Required)

8. **Add recurrence input** to CLI validators
9. **Extend create flow** to ask for recurrence after due date
10. **Modify toggle_complete()** to create new occurrences
11. **Update CLI handler** to show new occurrence message
12. **Add recurrence indicator** to task display

### Phase C: Enhanced Filter/Sort (P3 - Optional)

13. **Add due date filter options** to filter handler
14. **Add due date sort option** to sort handler

---

## Key Code Changes

### 1. New Enum (task.py)

```python
from enum import Enum

class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
```

### 2. Extended Task (task.py)

```python
from datetime import date

@dataclass
class Task:
    # ... existing fields ...
    due_date: date | None = None
    recurrence: Recurrence = field(default=Recurrence.NONE)
```

### 3. Date Input (validators.py)

```python
from datetime import date

def get_due_date_input(prompt: str = "Due date (YYYY-MM-DD): ") -> date | None:
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            return None
        try:
            return date.fromisoformat(user_input)
        except ValueError:
            print("Invalid format. Use YYYY-MM-DD (e.g., 2025-01-15)")
```

### 4. Due Date Display (display.py)

```python
def format_due_date(due_date: date | None, recurrence: Recurrence) -> str:
    if due_date is None:
        return f"{Colors.GRAY}(no deadline){Colors.RESET}"

    today = date.today()
    recur_suffix = recurrence.display if recurrence != Recurrence.NONE else ""

    if due_date < today:
        days = (today - due_date).days
        return f"{Colors.RED}Overdue {days}d{recur_suffix}{Colors.RESET}"
    elif due_date == today:
        return f"{Colors.YELLOW}Due today!{recur_suffix}{Colors.RESET}"
    else:
        days = (due_date - today).days
        return f"In {days}d{recur_suffix}"
```

### 5. Toggle Complete (task_service.py)

```python
def toggle_complete(self, task_id: int) -> tuple[Task, Task | None]:
    task = self.get_task(task_id)
    was_completed = task.completed
    task.completed = not task.completed
    self._repository.update(task)

    new_occurrence = None
    if (not was_completed and task.completed and
        task.recurrence != Recurrence.NONE and
        task.due_date is not None):
        new_occurrence = self._create_next_occurrence(task)

    return task, new_occurrence
```

---

## Testing Checklist

### Due Dates

- [ ] Create task with due date → shows in table
- [ ] Create task without due date → shows "(no deadline)"
- [ ] Task with past due date → shows "Overdue by Nd" in red
- [ ] Task due today → shows "Due today!" in yellow
- [ ] Task due tomorrow → shows "Due tomorrow" in yellow
- [ ] Task due in future → shows "In Nd" in gray
- [ ] Update task's due date → changes reflected
- [ ] Remove task's due date → shows "(no deadline)"
- [ ] Filter by "overdue" → only overdue tasks shown
- [ ] Sort by due date → ordered correctly, no-deadline last

### Recurring Tasks

- [ ] Create daily recurring task → shows "(Daily)" indicator
- [ ] Create weekly recurring task → shows "(Weekly)" indicator
- [ ] Create monthly recurring task → shows "(Monthly)" indicator
- [ ] Complete daily task → new task created with +1 day
- [ ] Complete weekly task → new task created with +7 days
- [ ] Complete monthly task (Jan 15) → new task Feb 15
- [ ] Complete monthly task (Jan 31) → new task Feb 28/29
- [ ] Complete non-recurring task → no new task created
- [ ] Delete recurring task → no new task created
- [ ] Update recurrence pattern → reflected on next completion
- [ ] Remove recurrence → no new task on completion

---

## Demo Script

Quick demo to show all Advanced features:

```bash
# Start app with demo data
python3 src/main.py --demo

# 1. Add task with due date and recurrence
# Select: 2 (Add Task)
# Title: Daily standup
# Due date: [tomorrow's date in YYYY-MM-DD]
# Recurrence: daily

# 2. View tasks to see due date column
# Select: 1 (View Tasks)

# 3. Mark the recurring task complete
# Select: 5 (Mark Complete)
# Enter ID of the recurring task
# Observe: "Task completed! Next occurrence: [date]"

# 4. View tasks again to see new occurrence
# Select: 1 (View Tasks)
# Notice: New task with advanced due date

# 5. Filter by due date
# Select: 7 (Filter Tasks)
# Select: 5 (By Due Date)
# Select: 2 (Due Today)

# 6. Sort by due date
# Select: 8 (Sort Tasks)
# Select: 7 (By Due Date)
```

---

## Common Pitfalls

1. **Monthly overflow**: Don't forget to handle Jan 31 → Feb 28 case
2. **Toggle direction**: Only create new occurrence when completing, not when un-completing
3. **Future dates**: Ensure new occurrence is always in future even if completing late
4. **Null handling**: `due_date` can be `None` - always check before calculations
5. **Service return type**: `toggle_complete()` now returns tuple - update all callers

---

## Files to Modify

| File | Changes |
|------|---------|
| `todo/domain/task.py` | Add `Recurrence` enum, extend `Task` dataclass |
| `todo/services/task_service.py` | Extend methods, add recurrence logic |
| `todo/cli/validators.py` | Add `get_due_date_input()`, `get_recurrence_input()` |
| `todo/cli/display.py` | Add `format_due_date()`, update table format |
| `todo/cli/handlers.py` | Extend add/update handlers, handle toggle return |
| `src/main.py` | Update demo data with due dates |

---

## Success Metrics

Feature is complete when:

- [x] All 17 functional requirements pass
- [x] Demo script runs successfully
- [x] All testing checklist items verified
- [x] No regression in existing 9 features
