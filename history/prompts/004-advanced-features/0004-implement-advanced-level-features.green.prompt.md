---
id: 0004
title: Implement Advanced Level Features
stage: green
date: 2025-12-28
surface: agent
model: claude-opus-4-5
feature: 004-advanced-features
branch: 004-advanced-features
user: ahsan
command: sp.implement
labels: ["implementation", "advanced-features", "due-dates", "recurring-tasks"]
links:
  spec: specs/004-advanced-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/todo/domain/task.py
  - src/todo/services/task_service.py
  - src/todo/cli/validators.py
  - src/todo/cli/display.py
  - src/todo/cli/handlers.py
  - src/todo/cli/app.py
  - src/main.py
  - test_implementation.py
tests:
  - test_implementation.py (all 8 tests passed)
---

## Prompt

Implement all 31 tasks for the 004-advanced-features feature following the Spec-Driven Development workflow. The feature adds Advanced Level functionality to the Phase I Todo Console App:

1. **Due Dates & Time Reminders** - Optional deadline dates with color-coded visual indicators (overdue=red, due soon=yellow, future=gray)
2. **Recurring Tasks** - Automatic rescheduling via daily/weekly/monthly patterns when tasks are completed

Implementation must follow the task breakdown in tasks.md across 6 phases:
- Phase 1: Setup (Domain Foundation) - T001-T004
- Phase 2: User Story 1 - Set Due Date on Task (P1) - T005-T012
- Phase 3: User Story 2 - Create Recurring Task (P2) - T013-T019
- Phase 4: User Story 3 - Filter and Sort by Due Date (P3) - T020-T025
- Phase 5: User Story 4 - Manage Recurring Settings (P3) - T026-T028
- Phase 6: Polish & Demo Data - T029-T031

## Response snapshot

Successfully implemented all 31 tasks across 6 phases:

**Phase 1: Setup (T001-T004)** - Domain layer foundation
- Added `Recurrence` enum (NONE, DAILY, WEEKLY, MONTHLY) with display properties
- Extended `Task` dataclass with `due_date: date | None` and `recurrence: Recurrence` fields
- Implemented `get_due_date_input()` and `get_recurrence_input()` validators

**Phase 2: User Story 1 (T005-T012)** - Due date functionality
- Created `format_due_date_display()` with color-coded status (overdue/today/future)
- Updated task table display to include Due column with visual indicators
- Extended `create_task()` and `update_task()` service methods with due_date parameter
- Added due date prompts and update options to CLI handlers
- Implemented sentinel pattern (`_REMOVE_DUE_DATE`) for distinguishing "remove" vs "don't change"

**Phase 3: User Story 2 (T013-T019)** - Recurring tasks
- Implemented `_calculate_next_due_date()` with monthly edge case handling (Jan 31 → Feb 28)
- Modified `toggle_complete()` to return tuple and auto-create recurring occurrences
- Updated CLI to show "Next occurrence scheduled for {date}" message
- Added recurrence indicators to task display (Daily), (Weekly), (Monthly)

**Phase 4: User Story 3 (T020-T025)** - Filter and sort
- Extended `list_tasks()` with `due_date_filter` parameter (overdue/today/this_week/no_deadline)
- Added due date sorting with nulls-last strategy using tuple sort key
- Updated `FilterState` dataclass and filter handler with option 5 for due date filters
- Added sort option 7 for "By Due Date (earliest first)"

**Phase 5: User Story 4 (T026-T028)** - Manage recurrence
- Extended update_task() with recurrence parameter
- Added recurrence option (6) to update handler submenu
- Updated show_update_submenu() to display current recurrence pattern

**Phase 6: Polish (T029-T031)** - Demo data and validation
- Updated demo data with 9 diverse tasks including overdue, due today, recurring (daily/weekly/monthly)
- Created comprehensive test script (test_implementation.py) - all 8 tests passed
- Verified all 11 features accessible from main menu with no regressions

## Outcome

- ✅ Impact: All 31 tasks completed. Advanced Level features (Due Dates + Recurring Tasks) fully functional with color-coded display, filter/sort, and update capabilities.
- 🧪 Tests: test_implementation.py validates 8 key scenarios including monthly edge case (Jan 31), all passing
- 📁 Files: Modified 7 core files across domain/service/CLI layers. Created 1 test file.
- 🔁 Next prompts: Ready for Phase II (Full-Stack Web App) or integration testing
- 🧠 Reflection: Clean architecture allowed additive changes with zero breaking modifications. Sentinel pattern for due_date removal was elegant. Monthly recurrence edge case handling was critical.

## Evaluation notes (flywheel)

- Failure modes observed: None. Initial approach with incremental phases worked correctly.
- Graders run and results (PASS/FAIL): Manual testing PASS. Automated test suite PASS (8/8 tests).
- Prompt variant (if applicable): Standard SDD workflow (specify → plan → tasks → implement)
- Next experiment (smallest change to try): Could explore alternative recurrence patterns (bi-weekly, quarterly) or relative due dates ("in 3 days")
