# Research: Advanced Level Features

**Feature**: 004-advanced-features
**Date**: 2025-12-27
**Purpose**: Resolve technical unknowns and document design decisions

---

## 1. Date Handling in Python

### Decision
Use Python's built-in `datetime.date` type for due dates.

### Rationale
- Part of Python standard library (no external dependencies for Phase I)
- Clean separation of date-only vs datetime values
- Natural comparison operators for due date filtering
- `timedelta` for recurrence calculations
- Easy conversion to string format (YYYY-MM-DD)

### Alternatives Considered
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| `datetime.date` | Standard library, simple | Limited timezone support | **CHOSEN** |
| `datetime.datetime` | More precise | Unnecessary for date-only | Rejected |
| `pendulum` | Rich features, timezones | External dependency | Rejected (Phase I constraint) |
| `arrow` | Nice API | External dependency | Rejected (Phase I constraint) |

---

## 2. Recurrence Pattern Representation

### Decision
Create a new `Recurrence` enum similar to existing `Priority` enum.

### Rationale
- Consistent with existing codebase pattern (`Priority` as IntEnum)
- Type-safe representation
- Easy serialization/display
- Simple next-date calculation via enum value mapping

### Pattern Design
```python
class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
```

### Next Date Calculation Strategy
| Pattern | Calculation | Edge Case Handling |
|---------|-------------|-------------------|
| DAILY | `due_date + timedelta(days=1)` | None needed |
| WEEKLY | `due_date + timedelta(days=7)` | None needed |
| MONTHLY | Same day next month | Clamp to month's last day if overflow |

### Monthly Edge Case Solution
```python
def next_month_date(date: date) -> date:
    """Calculate same day next month, adjusting for shorter months."""
    next_month = date.month % 12 + 1
    year = date.year + (1 if next_month == 1 else 0)
    last_day = calendar.monthrange(year, next_month)[1]
    day = min(date.day, last_day)  # Clamp to last valid day
    return date.replace(year=year, month=next_month, day=day)
```

---

## 3. Task Entity Extension

### Decision
Add two new optional fields to the existing `Task` dataclass.

### Rationale
- Minimal change to existing entity
- Optional fields maintain backward compatibility
- Dataclass defaults make fields transparent to existing code

### New Fields
| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `due_date` | `date \| None` | `None` | Deadline for task |
| `recurrence` | `Recurrence` | `Recurrence.NONE` | Repeat pattern |

### Backward Compatibility
- Existing code doesn't pass these fields → defaults apply
- Existing display code continues working (new columns opt-in)
- Repository `update()` unchanged (full object replacement)

---

## 4. Due Date Status Calculation

### Decision
Create utility function for due date status that returns visual indicator.

### Rationale
- Centralized logic for consistent display
- Pure function (no state, easy to test)
- Called at display time, not stored

### Status Categories
| Status | Condition | Color | Symbol |
|--------|-----------|-------|--------|
| OVERDUE | `due_date < today` | Red | Overdue text |
| DUE_SOON | `due_date == today OR due_date == tomorrow` | Yellow | Due soon text |
| FUTURE | `due_date > tomorrow` | Gray | Date string |
| NO_DEADLINE | `due_date is None` | Gray | "(no deadline)" |

### Implementation
```python
def get_due_date_status(due_date: date | None) -> tuple[str, str]:
    """Return (display_text, color_code) for due date."""
    if due_date is None:
        return "(no deadline)", "gray"

    today = date.today()
    if due_date < today:
        days_overdue = (today - due_date).days
        return f"Overdue by {days_overdue}d", "red"
    elif due_date == today:
        return "Due today!", "yellow"
    elif due_date == today + timedelta(days=1):
        return "Due tomorrow", "yellow"
    else:
        days_until = (due_date - today).days
        return f"In {days_until}d ({due_date})", "gray"
```

---

## 5. Recurring Task Completion Flow

### Decision
Create new occurrence in `toggle_complete()` when task has recurrence.

### Rationale
- Single method handles completion logic
- Automatic scheduling without user intervention
- Clear feedback via return value or service method

### Flow Diagram
```
User marks task complete
        ↓
toggle_complete(task_id)
        ↓
    Is task.completed becoming True?
        ↓
    ┌─No──→ Just toggle (incomplete → complete check)
    │
    └─Yes─→ Does task have recurrence (not NONE)?
              ↓
          ┌─No──→ Just toggle
          │
          └─Yes─→ 1. Mark current task complete
                  2. Calculate next due date
                  3. Create new task (copy attributes)
                  4. Return both current task and message about new one
```

### New Method Signature
```python
def toggle_complete(self, task_id: int) -> tuple[Task, Task | None]:
    """Toggle task completion. Returns (updated_task, new_occurrence_or_None)."""
```

Alternative: Keep existing signature, handle recurring creation internally, and use separate query to inform user.

**Decision**: Modify `toggle_complete` to return additional info about created recurring task.

---

## 6. Filter/Sort Extension

### Decision
Extend existing `list_tasks()` with `due_date_filter` and `sort_by="due_date"`.

### Rationale
- Consistent with existing filter/sort patterns
- Minimal API surface change
- Reuses existing infrastructure

### New Filter Options
| Filter | Description | Implementation |
|--------|-------------|----------------|
| `"overdue"` | Past due date | `t.due_date and t.due_date < today` |
| `"today"` | Due today | `t.due_date == today` |
| `"this_week"` | Due within 7 days | `today <= t.due_date <= today + 7d` |
| `"no_deadline"` | No due date set | `t.due_date is None` |

### Sort Behavior
- Sort by due date ascending (earliest first)
- Tasks without due date go to end
- `None` values handled: `key=lambda t: (t.due_date is None, t.due_date or date.max)`

---

## 7. CLI Input Validation for Dates

### Decision
Create new validator function `get_due_date_input()` in validators.py.

### Rationale
- Consistent with existing `get_title_input()`, `get_priority_input()` pattern
- Single responsibility for date parsing and validation
- User-friendly error messages

### Validation Rules
| Rule | Error Message |
|------|---------------|
| Empty input | Returns `None` (due date is optional) |
| Invalid format | "Please enter date in YYYY-MM-DD format (e.g., 2025-01-15)" |
| Invalid date (Feb 30) | "Invalid date. Please check month/day values." |

---

## 8. Display Table Extension

### Decision
Add "Due" column between "Title" and "Tags" columns.

### Rationale
- Logical grouping (time-related after description)
- Compact width (fits in 15-character column)
- Color-coded for quick scanning

### Table Layout
```
| ID  | Status | Priority   | Title                    | Due            | Tags
|-----|--------|------------|--------------------------|----------------|------
|   1 | [ ]    | [HIGH]     | Weekly standup           | Due today!     | #work
|   2 | [✓]    | [MEDIUM]   | Buy groceries            | (no deadline)  | #personal
|   3 | [ ]    | [LOW]      | Code review              | Overdue by 2d  | #work
```

### Recurrence Indicator
Show recurrence pattern after due date status for recurring tasks:
```
| Due today! (Weekly)
| In 5d (2025-01-05) (Daily)
```

---

## Summary

All technical unknowns have been resolved:

| Area | Decision | Confidence |
|------|----------|------------|
| Date handling | `datetime.date` | High |
| Recurrence enum | `Recurrence(Enum)` | High |
| Task extension | Two new optional fields | High |
| Status calculation | Pure utility function | High |
| Completion flow | Extended `toggle_complete` | High |
| Filter/Sort | Extend existing pattern | High |
| CLI validation | New `get_due_date_input()` | High |
| Display | New "Due" column with colors | High |

**Ready for Phase 1: Data Model and Contracts**
