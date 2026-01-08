# Tasks: Advanced Level Features

**Input**: Design documents from `/specs/004-advanced-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/service-api.md

**Tests**: Manual testing via CLI (no automated tests required for Phase I)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## User Stories Summary

| ID | Story | Priority | Description |
|----|-------|----------|-------------|
| US1 | Set Due Date on Task | P1 | Create tasks with deadlines, visual indicators |
| US2 | Create Recurring Task | P2 | Auto-reschedule on completion |
| US3 | Filter and Sort by Due Date | P3 | Filter overdue/today/week, sort by due date |
| US4 | Manage Recurring Settings | P3 | Update/remove recurrence on existing tasks |

---

## Phase 1: Setup (Domain Foundation)

**Purpose**: Add new domain types that all user stories depend on

- [X] T001 [P] Add Recurrence enum to src/todo/domain/task.py
  - [From]: data-model.md §Enum: Recurrence
  - Values: NONE, DAILY, WEEKLY, MONTHLY
  - Include `__str__()` and `display` property

- [X] T002 Extend Task dataclass with due_date and recurrence fields in src/todo/domain/task.py
  - [From]: data-model.md §Entity: Task (Extended)
  - `due_date: date | None = None`
  - `recurrence: Recurrence = field(default=Recurrence.NONE)`
  - Requires: T001 (Recurrence enum)

- [X] T003 [P] Add get_due_date_input() validator in src/todo/cli/validators.py
  - [From]: contracts/service-api.md §get_due_date_input()
  - Parse YYYY-MM-DD format, return date or None
  - Handle invalid format with helpful error message

- [X] T004 [P] Add get_recurrence_input() validator in src/todo/cli/validators.py
  - [From]: contracts/service-api.md §get_recurrence_input()
  - Parse none/daily/weekly/monthly, return Recurrence enum
  - Default to NONE on empty input

**Checkpoint**: Domain types ready - user story implementation can begin

---

## Phase 2: User Story 1 - Set Due Date on Task (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with optional due dates and see color-coded visual indicators showing overdue (red), due soon (yellow), or future (gray) status.

**Independent Test**: Create a task with a due date, view the task list, verify the due date displays with appropriate color based on status (overdue/today/future).

**Acceptance Criteria**:
- [From]: spec.md §User Story 1
- AC1: User can enter due date in YYYY-MM-DD format when creating task
- AC2: Task displays with color-coded due date status
- AC3: Tasks without due date show "(no deadline)"
- AC4: User can update or remove due date via update menu

### Implementation for User Story 1

- [X] T005 [US1] Add format_due_date_display() function in src/todo/cli/display.py
  - [From]: contracts/service-api.md §format_due_date_display()
  - Return color-coded string based on date status
  - Overdue: red, Due today/tomorrow: yellow, Future: gray
  - No due date: "(no deadline)" in gray

- [X] T006 [US1] Update format_task_row() to include due date column in src/todo/cli/display.py
  - [From]: plan.md §CLI Layer Changes
  - Add Due column between Title and Tags
  - Call format_due_date_display() for each task

- [X] T007 [US1] Update format_task_table() header to include Due column in src/todo/cli/display.py
  - [From]: plan.md §CLI Layer Changes
  - Add "Due" header with appropriate width (~15 chars)

- [X] T008 [US1] Extend create_task() service method with due_date parameter in src/todo/services/task_service.py
  - [From]: contracts/service-api.md §create_task() - Extended
  - Add `due_date: date | None = None` parameter
  - Pass to Task constructor

- [X] T009 [US1] Update add_task_handler() to prompt for due date in src/todo/cli/handlers.py
  - [From]: spec.md §User Story 1 AC1
  - After tags prompt, call get_due_date_input()
  - Pass due_date to service.create_task()

- [X] T010 [US1] Extend update_task() service method with due_date parameter in src/todo/services/task_service.py
  - [From]: contracts/service-api.md §update_task() - Extended
  - Add `due_date: date | None = None` parameter
  - Support setting, changing, or removing due date

- [X] T011 [US1] Add due date option to update_task_handler() submenu in src/todo/cli/handlers.py
  - [From]: spec.md §User Story 1 AC4
  - Add option 5: "Due Date" (renumber Cancel to 6)
  - Call get_due_date_input() and update_task()

- [X] T012 [US1] Update show_update_submenu() to display current due date in src/todo/cli/display.py
  - [From]: plan.md §CLI Layer Changes
  - Show current due date value in task details
  - Add option 5 to menu list

**Checkpoint**: User Story 1 complete - tasks can be created with due dates and displayed with visual indicators

---

## Phase 3: User Story 2 - Create Recurring Task (Priority: P2)

**Goal**: Users can set recurrence patterns on tasks with due dates. When a recurring task is marked complete, the system automatically creates a new task occurrence with the next due date.

**Independent Test**: Create a daily recurring task, mark it complete, verify a new task is created with due date +1 day.

**Acceptance Criteria**:
- [From]: spec.md §User Story 2
- AC1: User can set recurrence when creating task with due date
- AC2: Completing recurring task creates new occurrence
- AC3: User sees confirmation message with next due date
- AC4: Recurrence indicator displays on recurring tasks

### Implementation for User Story 2

- [X] T013 [US2] Add _calculate_next_due_date() helper method in src/todo/services/task_service.py
  - [From]: research.md §Next Date Calculation Strategy
  - Daily: +1 day, Weekly: +7 days, Monthly: same day next month
  - Handle monthly edge case (31st → 28/29/30)
  - Ensure result is always in future (skip past dates)

- [X] T014 [US2] Extend create_task() service with recurrence parameter in src/todo/services/task_service.py
  - [From]: contracts/service-api.md §create_task() - Extended
  - Add `recurrence: Recurrence = Recurrence.NONE` parameter
  - Pass to Task constructor

- [X] T015 [US2] Update add_task_handler() to prompt for recurrence after due date in src/todo/cli/handlers.py
  - [From]: spec.md §User Story 2 AC1
  - Only prompt if due_date is set
  - Call get_recurrence_input() and pass to create_task()

- [X] T016 [US2] Modify toggle_complete() to return tuple and create recurring occurrences in src/todo/services/task_service.py
  - [From]: contracts/service-api.md §toggle_complete() - Extended
  - Change return type to `tuple[Task, Task | None]`
  - When marking complete: check recurrence != NONE and due_date != None
  - Create new task with calculated next due date
  - Copy title, description, priority, tags, recurrence

- [X] T017 [US2] Update toggle_complete_handler() to handle tuple return and show message in src/todo/cli/handlers.py
  - [From]: spec.md §User Story 2 AC3
  - Unpack tuple: `task, new_occurrence = service.toggle_complete(id)`
  - If new_occurrence: print "Next occurrence scheduled for {date}"

- [X] T018 [US2] Update format_due_date_display() to include recurrence indicator in src/todo/cli/display.py
  - [From]: spec.md §User Story 2 AC4
  - If recurrence != NONE: append "(Daily)", "(Weekly)", or "(Monthly)"
  - Requires recurrence parameter added to function signature

- [X] T019 [US2] Update format_task_row() to pass recurrence to format_due_date_display() in src/todo/cli/display.py
  - [From]: plan.md §CLI Layer Changes
  - Pass task.recurrence to display function

**Checkpoint**: User Story 2 complete - recurring tasks auto-create next occurrence on completion

---

## Phase 4: User Story 3 - Filter and Sort by Due Date (Priority: P3)

**Goal**: Users can filter tasks by due date status (overdue, today, this week, no deadline) and sort tasks by due date.

**Independent Test**: Create tasks with various due dates, apply "overdue" filter, verify only overdue tasks appear. Sort by due date, verify earliest dates first.

**Acceptance Criteria**:
- [From]: spec.md §User Story 3
- AC1: Filter options include Overdue, Due Today, Due This Week, No Deadline
- AC2: Filtered list shows only matching tasks
- AC3: Sort by due date orders earliest first, no-deadline last

### Implementation for User Story 3

- [X] T020 [US3] Extend list_tasks() with due_date_filter parameter in src/todo/services/task_service.py
  - [From]: contracts/service-api.md §list_tasks() - Extended
  - Add `due_date_filter: str | None = None` parameter
  - Implement filter logic for: "overdue", "today", "this_week", "no_deadline"

- [X] T021 [US3] Add due date sorting logic to _sort_tasks() in src/todo/services/task_service.py
  - [From]: spec.md §FR-006
  - Add case for `sort_by == "due_date"`
  - Sort ascending, None values (no deadline) at end

- [X] T022 [US3] Add DueDateFilter to FilterState in src/todo/cli/app.py
  - [From]: plan.md §CLI Layer Changes
  - Add `due_date_filter: str | None = None` to FilterState dataclass

- [X] T023 [US3] Add due date filter option (5) to filter_tasks_handler() in src/todo/cli/handlers.py
  - [From]: spec.md §User Story 3 AC1
  - Add option 5: "By Due Date"
  - Submenu: Overdue, Due Today, Due This Week, No Deadline, All
  - Set cli.current_filter.due_date_filter

- [X] T024 [US3] Update view_tasks_handler() to pass due_date_filter to service in src/todo/cli/handlers.py
  - [From]: plan.md §CLI Layer Changes
  - Pass cli.current_filter.due_date_filter to list_tasks()

- [X] T025 [US3] Add due date sort option (7) to sort_tasks_handler() in src/todo/cli/handlers.py
  - [From]: spec.md §FR-006
  - Add option 7: "By Due Date (earliest first)"
  - Set cli.current_sort.field = "due_date"

**Checkpoint**: User Story 3 complete - users can filter and sort by due date

---

## Phase 5: User Story 4 - Manage Recurring Task Settings (Priority: P3)

**Goal**: Users can modify or remove recurrence patterns on existing tasks without recreating them.

**Independent Test**: Create a recurring task, update recurrence to "none", mark complete, verify no new occurrence is created.

**Acceptance Criteria**:
- [From]: spec.md §User Story 4
- AC1: User can update recurrence via update menu
- AC2: Removing recurrence stops auto-creation on completion

### Implementation for User Story 4

- [X] T026 [US4] Extend update_task() service with recurrence parameter in src/todo/services/task_service.py
  - [From]: contracts/service-api.md §update_task() - Extended
  - Add `recurrence: Recurrence | None = None` parameter
  - Update task.recurrence if provided

- [X] T027 [US4] Add recurrence option (6) to update_task_handler() submenu in src/todo/cli/handlers.py
  - [From]: spec.md §User Story 4 AC1
  - Add option 6: "Recurrence" (renumber Cancel to 7)
  - Call get_recurrence_input() and update_task()

- [X] T028 [US4] Update show_update_submenu() to display current recurrence in src/todo/cli/display.py
  - [From]: plan.md §CLI Layer Changes
  - Show current recurrence pattern in task details
  - Add option 6 to menu list

**Checkpoint**: User Story 4 complete - recurrence settings can be managed on existing tasks

---

## Phase 6: Polish & Demo Data

**Purpose**: Final touches and demo preparation

- [X] T029 [P] Update demo data in src/main.py with due dates and recurring tasks
  - [From]: quickstart.md §Demo Script
  - Add tasks with various due dates (past, today, future)
  - Add daily and weekly recurring tasks
  - Mix completed and pending for demo variety

- [X] T030 Verify all 11 features accessible from main menu in src/todo/cli/app.py
  - [From]: spec.md §SC-006
  - Run through each menu option
  - Verify no regressions in existing 9 features

- [X] T031 Run quickstart.md validation checklist
  - [From]: quickstart.md §Testing Checklist
  - Test all due date scenarios
  - Test all recurring task scenarios
  - Test filter and sort options

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (US1) → Phase 3 (US2) → Phase 4 (US3) → Phase 5 (US4) → Phase 6 (Polish)
```

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 1 (domain types)
- **US2 (P2)**: Depends on US1 (due dates must exist for recurrence to work)
- **US3 (P3)**: Depends on US1 (needs due dates to filter/sort)
- **US4 (P3)**: Depends on US2 (needs recurrence to manage)

### Within Each Phase

1. Domain/model tasks first
2. Service layer tasks second
3. CLI display tasks (can parallel with service)
4. CLI handler tasks last (depends on service + display)

### Parallel Opportunities

**Phase 1** (all can run in parallel after T001):
```bash
# After T001 (Recurrence enum):
Task T002: Extend Task dataclass
Task T003: Add get_due_date_input() validator
Task T004: Add get_recurrence_input() validator
```

**Phase 2** (display tasks can parallel):
```bash
# After T005:
Task T006: Update format_task_row()
Task T007: Update format_task_table() header
Task T012: Update show_update_submenu()
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: User Story 1 (T005-T012)
3. **STOP and VALIDATE**: Test due dates independently
4. Demo if ready - this delivers the core P1 feature

### Full Implementation

1. Phase 1 → Phase 2 (US1) → **Validate MVP**
2. Phase 3 (US2) → **Validate recurring tasks**
3. Phase 4 (US3) → **Validate filter/sort**
4. Phase 5 (US4) → **Validate recurrence management**
5. Phase 6 (Polish) → **Full demo validation**

### Task Count Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| Phase 1 | Setup | 4 | 3 |
| Phase 2 | US1 | 8 | 3 |
| Phase 3 | US2 | 7 | 0 |
| Phase 4 | US3 | 6 | 0 |
| Phase 5 | US4 | 3 | 0 |
| Phase 6 | Polish | 3 | 1 |
| **Total** | - | **31** | **7** |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to spec.md user story
- T016 (toggle_complete return type change) is the highest-risk task - single caller makes it safe
- Monthly edge case (31st) handled in T013 - test explicitly
- All existing 9 features must continue working (T030 verification)
