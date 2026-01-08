# Implementation Plan: Advanced Level Features

**Branch**: `004-advanced-features` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-advanced-features/spec.md`

---

## Summary

Extend the Phase 1 Console App from **Intermediate Level (9 features)** to **Advanced Level (11 features)** by adding:

1. **Due Dates & Time Reminders** - Optional deadline dates with color-coded visual indicators (overdue=red, due soon=yellow, future=gray)
2. **Recurring Tasks** - Automatic rescheduling via daily/weekly/monthly patterns when tasks are completed

Technical approach: Extend existing `Task` dataclass with two new optional fields, add `Recurrence` enum, and modify `toggle_complete()` to create new occurrences for recurring tasks.

---

## Technical Context

**Language/Version**: Python 3.10+ (standard library only)
**Primary Dependencies**: None (stdlib: datetime, dataclasses, enum)
**Storage**: In-memory (existing InMemoryTaskRepository)
**Testing**: Manual integration testing via CLI
**Target Platform**: Console/Terminal (Linux/macOS/Windows)
**Project Type**: Single Python package (CLI application)
**Performance Goals**: Instant response (<100ms for any operation)
**Constraints**: No external dependencies (Phase I constitution constraint)
**Scale/Scope**: Single user, in-memory session

---

## Constitution Check

*GATE: Must pass before implementation. Verified against `.specify/memory/constitution.md`*

| Gate | Status | Notes |
|------|--------|-------|
| Phase I scope (no DB, web, auth) | PASS | Only in-memory operations |
| No external dependencies | PASS | Uses only Python stdlib |
| SDD workflow (spec → plan → tasks → implement) | PASS | Following prescribed flow |
| Task references to spec sections | PENDING | Tasks will include `[From]: spec.md §X.X` |
| Clean Architecture (domain/service/repository/cli) | PASS | Extending existing layers |
| Type hints required | PASS | All new functions will be typed |
| Context7 for external docs | N/A | No external libraries used |

**Gate Result**: PASS - Ready for implementation

---

## Project Structure

### Documentation (this feature)

```text
specs/004-advanced-features/
├── spec.md              # Requirements specification (COMPLETE)
├── plan.md              # This file (COMPLETE)
├── research.md          # Phase 0 research output (COMPLETE)
├── data-model.md        # Entity definitions (COMPLETE)
├── quickstart.md        # Implementation guide (COMPLETE)
├── contracts/           # API contracts (COMPLETE)
│   └── service-api.md   # Service method signatures
├── checklists/          # Quality checklists
│   └── requirements.md  # Spec validation checklist
└── tasks.md             # Implementation tasks (NEXT: /sp.tasks)
```

### Source Code (repository root)

```text
src/
├── todo/
│   ├── domain/
│   │   ├── task.py          # MODIFY: Add Recurrence enum, extend Task
│   │   └── exceptions.py    # No changes
│   ├── services/
│   │   └── task_service.py  # MODIFY: Extend methods, add recurrence logic
│   ├── repository/
│   │   ├── base.py          # No changes
│   │   └── memory.py        # No changes (stores full Task objects)
│   └── cli/
│       ├── app.py           # MODIFY: Add due_date to FilterState
│       ├── handlers.py      # MODIFY: Extend handlers for due date/recurrence
│       ├── display.py       # MODIFY: Add due date formatting, update table
│       └── validators.py    # MODIFY: Add date/recurrence input validators
└── main.py                  # MODIFY: Update demo data with due dates

tests/
├── unit/                    # Future: unit tests
└── integration/             # Future: integration tests
```

**Structure Decision**: Single Python package (existing structure), no new directories needed.

---

## Component Design

### 1. Domain Layer Changes

**File**: `src/todo/domain/task.py`

```python
# NEW: Recurrence enum
class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# EXTENDED: Task dataclass
@dataclass
class Task:
    # ... existing fields ...
    due_date: date | None = None           # NEW
    recurrence: Recurrence = Recurrence.NONE  # NEW
```

### 2. Service Layer Changes

**File**: `src/todo/services/task_service.py`

| Method | Change | Impact |
|--------|--------|--------|
| `create_task()` | Add `due_date`, `recurrence` params | Low |
| `update_task()` | Add `due_date`, `recurrence` params | Low |
| `toggle_complete()` | Return tuple, create recurring occurrence | Medium |
| `list_tasks()` | Add `due_date_filter`, `sort_by="due_date"` | Low |
| `_calculate_next_due_date()` | NEW helper method | New |

### 3. CLI Layer Changes

**File**: `src/todo/cli/validators.py`

| Function | Purpose |
|----------|---------|
| `get_due_date_input()` | Parse YYYY-MM-DD date from user |
| `get_recurrence_input()` | Parse recurrence pattern from user |

**File**: `src/todo/cli/display.py`

| Function | Purpose |
|----------|---------|
| `format_due_date_display()` | Format due date with colors and status |
| `format_task_row()` | EXTEND: Add due date column |
| `format_task_table()` | EXTEND: Add due date header |

**File**: `src/todo/cli/handlers.py`

| Handler | Change |
|---------|--------|
| `add_task_handler()` | Add due date and recurrence prompts |
| `update_task_handler()` | Add due date and recurrence options (6, 7) |
| `toggle_complete_handler()` | Handle tuple return, show new occurrence |
| `filter_tasks_handler()` | Add due date filter option (5) |
| `sort_tasks_handler()` | Add due date sort option (7) |

---

## Implementation Phases

### Phase A: Due Dates Foundation (P1 - Critical)

**Goal**: Users can create tasks with due dates and see visual indicators.

1. Add `Recurrence` enum to domain
2. Extend `Task` with `due_date` and `recurrence` fields
3. Add `get_due_date_input()` validator
4. Extend `create_task()` service and handler
5. Add `format_due_date_display()` utility
6. Update task table display with due date column
7. Extend `update_task_handler()` with due date option

**Acceptance**: User can create task with due date, see it in table with color status.

### Phase B: Recurring Tasks (P2 - Required)

**Goal**: Recurring tasks automatically create next occurrence on completion.

8. Add `get_recurrence_input()` validator
9. Extend create flow to prompt for recurrence
10. Implement `_calculate_next_due_date()` helper
11. Modify `toggle_complete()` to create new occurrences
12. Update `toggle_complete_handler()` to show new occurrence
13. Add recurrence indicator to task display

**Acceptance**: Completing a recurring task creates new task with next due date.

### Phase C: Filter and Sort (P3 - Enhancement)

**Goal**: Users can filter and sort by due date.

14. Add `due_date_filter` parameter to `list_tasks()`
15. Implement due date filter logic (overdue, today, this_week, no_deadline)
16. Add due date sort option (`sort_by="due_date"`)
17. Extend filter handler with due date options
18. Extend sort handler with due date option

**Acceptance**: Filter shows only matching tasks, sort orders by due date.

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Monthly edge case bugs (31st) | Medium | Low | Explicit test cases in quickstart |
| Toggle return type breaks callers | Low | Medium | Single caller (handler) - controlled change |
| Date display column width issues | Low | Low | Fixed 15-char width, truncate if needed |
| Recurrence without due_date confusion | Low | Low | Only prompt for recurrence if due_date set |

---

## Dependencies

### Internal Dependencies

```
Recurrence enum ← Task dataclass ← TaskService ← CLI handlers
                                              ↖ CLI display
```

### Build Order

1. `Recurrence` enum (no dependencies)
2. `Task` extension (depends on Recurrence)
3. Service methods (depends on Task)
4. CLI validators (no dependencies)
5. CLI display (depends on Recurrence)
6. CLI handlers (depends on all above)

---

## Testing Strategy

### Manual Testing

Following the quickstart.md checklist:

- Due date creation, display, update, removal
- Overdue/today/tomorrow/future status colors
- Recurring task creation and completion
- Monthly edge cases (31st → 28/29/30)
- Filter and sort verification

### Automated Testing (Future)

Structure prepared in `tests/` for:
- Unit tests for date calculations
- Integration tests for recurring flow

---

## Success Criteria Mapping

| Success Criteria | Implementation |
|-----------------|----------------|
| SC-001: Task with due date in <30s | Streamlined input flow |
| SC-002: Identify overdue in <1s | Color-coded display |
| SC-003: Verify rescheduling in <2min | Clear feedback message |
| SC-004: 100% correct rescheduling | Comprehensive test cases |
| SC-005: Filter accuracy | Exact date comparisons |
| SC-006: All 11 features accessible | Menu unchanged (existing options) |
| SC-007: Zero data loss on toggle | Atomic service operations |

---

## Complexity Tracking

No constitution violations requiring justification. Implementation uses:
- Existing 4-layer architecture
- No new external dependencies
- Standard Python patterns
- Minimal API surface changes

---

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Execute tasks in order (Phase A → B → C)
3. Verify against quickstart.md checklist
4. Update demo data in `main.py`
5. Create demo video showing new features

---

**Plan Status**: COMPLETE
**Ready for**: `/sp.tasks`
