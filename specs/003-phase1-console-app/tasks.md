# Tasks: Phase 1 - In-Memory Python Console Todo App

**Input**: Design documents from `/specs/003-phase1-console-app/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/cli-interface.md ✓

**Tests**: Test tasks are NOT included (not explicitly requested in specification). Tests can be added via `/sp.tasks --with-tests` if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure - single project layout:

```
src/
├── todo/
│   ├── __init__.py
│   ├── domain/           # Task, Priority, Exceptions
│   ├── services/         # TaskService
│   ├── repository/       # TaskRepository (abstract), InMemoryTaskRepository
│   └── cli/              # app.py, handlers.py, display.py, validators.py
└── main.py
tests/
├── unit/
└── integration/
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and package structure

- [x] T001 Initialize Python 3.13+ project with UV in repository root with pyproject.toml
- [x] T002 Create package structure: src/todo/ with __init__.py (version="1.0.0")
- [x] T003 [P] Create src/todo/domain/__init__.py
- [x] T004 [P] Create src/todo/services/__init__.py
- [x] T005 [P] Create src/todo/repository/__init__.py
- [x] T006 [P] Create src/todo/cli/__init__.py
- [x] T007 Create src/main.py entry point (placeholder)
- [x] T008 [P] Add pytest as dev dependency and create tests/ structure

---

## Phase 2: Foundational (Domain Layer - Blocking Prerequisites)

**Purpose**: Core domain entities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create Priority IntEnum (LOW=1, MEDIUM=2, HIGH=3) with display property in src/todo/domain/task.py
- [x] T010 Create Task dataclass (id, title, description, priority, tags, completed, created_at) in src/todo/domain/task.py
- [x] T011 [P] Create TodoError base exception in src/todo/domain/exceptions.py
- [x] T012 [P] Create TaskNotFoundError(TodoError) with task_id attribute in src/todo/domain/exceptions.py
- [x] T013 [P] Create ValidationError(TodoError) with field and message attributes in src/todo/domain/exceptions.py
- [x] T014 Create abstract TaskRepository ABC (add, get, get_all, update, delete, count) in src/todo/repository/base.py
- [x] T015 Implement InMemoryTaskRepository with dict[int, Task] storage in src/todo/repository/memory.py
- [x] T016 Export domain entities from src/todo/domain/__init__.py
- [x] T017 Export repository classes from src/todo/repository/__init__.py

**Checkpoint**: Domain layer complete - service layer can now be implemented

---

## Phase 3: User Story 6 - Navigate Menu System (Priority: P1)

**Goal**: Provide clear, intuitive menu system for all features

**Independent Test**: Launch application and navigate through all menu options

### Implementation for User Story 6

- [x] T018 [US6] Create display utilities (print_header, print_error, print_success, clear_screen) in src/todo/cli/display.py
- [x] T019 [US6] Create input validators (get_integer_input, get_yes_no_input, get_choice_input) in src/todo/cli/validators.py
- [x] T020 [US6] Create main menu display function with 9-option layout in src/todo/cli/app.py
- [x] T021 [US6] Implement TodoCLI class with handler dictionary dispatch in src/todo/cli/app.py
- [x] T022 [US6] Implement main application loop with KeyboardInterrupt handling in src/todo/cli/app.py
- [x] T023 [US6] Implement exit_handler with graceful goodbye message in src/todo/cli/handlers.py
- [x] T024 [US6] Wire up main.py entry point to instantiate and run TodoCLI

**Checkpoint**: Application launches with menu, can navigate options 1-9, exits gracefully

---

## Phase 4: User Story 1 - View All Tasks (Priority: P1) 🎯 MVP

**Goal**: Display all tasks with ID, title, status, priority, tags, and statistics

**Independent Test**: Launch app, add sample tasks manually via code, select "View Tasks" to see formatted display

### Implementation for User Story 1

- [x] T025 [US1] Create TaskService with constructor accepting TaskRepository in src/todo/services/task_service.py
- [x] T026 [US1] Implement TaskService.list_tasks(status, priority, tag, search, sort_by) method
- [x] T027 [US1] Implement TaskService.get_stats() returning {total, pending, completed}
- [x] T028 [US1] Create format_task_row() function for single task display in src/todo/cli/display.py
- [x] T029 [US1] Create format_task_table() function for full task list with headers in src/todo/cli/display.py
- [x] T030 [US1] Implement view_tasks_handler showing stats, filter/sort indicators, and task table in src/todo/cli/handlers.py
- [x] T031 [US1] Handle empty task list with friendly "No tasks yet" message
- [x] T032 [US1] Export TaskService from src/todo/services/__init__.py

**Checkpoint**: User can view all tasks with complete information display

---

## Phase 5: User Story 2 - Add New Task (Priority: P1)

**Goal**: Create new tasks with title, description, priority, and tags

**Independent Test**: Select "Add Task", enter details, verify task appears in "View Tasks"

### Implementation for User Story 2

- [x] T033 [US2] Implement TaskService.create_task(title, description, priority, tags) with validation
- [x] T034 [US2] Add title validation (required, 1-200 chars, trimmed) in TaskService
- [x] T035 [US2] Add description validation (optional, max 1000 chars) in TaskService
- [x] T036 [US2] Implement _normalize_tags() helper (lowercase, trim, dedupe, max 10, max 30 chars each) in TaskService
- [x] T037 [US2] Create get_priority_input() validator for high/medium/low in src/todo/cli/validators.py
- [x] T038 [US2] Create get_tags_input() validator parsing comma-separated tags in src/todo/cli/validators.py
- [x] T039 [US2] Implement add_task_handler with prompts for all fields in src/todo/cli/handlers.py
- [x] T040 [US2] Display confirmation with task ID, title, priority, and tags after creation

**Checkpoint**: User can add tasks with all fields, validation works correctly

---

## Phase 6: User Story 3 - Mark Complete/Incomplete (Priority: P2)

**Goal**: Toggle task completion status by ID

**Independent Test**: Add a task, mark it complete, verify status change, toggle back

### Implementation for User Story 3

- [x] T041 [US3] Implement TaskService.get_task(task_id) returning Task or raising TaskNotFoundError
- [x] T042 [US3] Implement TaskService.toggle_complete(task_id) returning updated Task
- [x] T043 [US3] Implement toggle_complete_handler prompting for task ID in src/todo/cli/handlers.py
- [x] T044 [US3] Display confirmation with task title and new status (completed/pending)
- [x] T045 [US3] Handle TaskNotFoundError with user-friendly message

**Checkpoint**: User can toggle task completion, status displays correctly

---

## Phase 7: User Story 4 - Update Existing Task (Priority: P2)

**Goal**: Modify any field of an existing task by ID

**Independent Test**: Add a task, update various fields, verify changes in task list

### Implementation for User Story 4

- [x] T046 [US4] Implement TaskService.update_task(task_id, title, description, priority, tags) with partial updates
- [x] T047 [US4] Add validation in update_task (same rules as create: title 1-200, description max 1000)
- [x] T048 [US4] Create show_update_submenu() for field selection (title/description/priority/tags/cancel) in src/todo/cli/display.py
- [x] T049 [US4] Implement update_task_handler with current task display and field selection in src/todo/cli/handlers.py
- [x] T050 [US4] Display confirmation with field name and new value after update
- [x] T051 [US4] Handle empty title update with error message

**Checkpoint**: User can update any task field, original data preserved for unchanged fields

---

## Phase 8: User Story 5 - Delete Task (Priority: P2)

**Goal**: Permanently remove tasks with confirmation prompt

**Independent Test**: Add a task, delete it, verify it no longer appears in task list

### Implementation for User Story 5

- [x] T052 [US5] Implement TaskService.delete_task(task_id) returning success boolean
- [x] T053 [US5] Implement delete_task_handler with task preview and confirmation in src/todo/cli/handlers.py
- [x] T054 [US5] Display task details (ID, title, priority) before confirmation prompt
- [x] T055 [US5] Handle cancellation with "Operation cancelled" message
- [x] T056 [US5] Display success confirmation with task ID after deletion

**Checkpoint**: User can delete tasks with safety confirmation

---

## Phase 9: User Story 8 - Set Task Priority (Priority: P2)

**Goal**: Assign priority levels (high/medium/low) with visual indicators

**Independent Test**: Add tasks with different priorities, verify display with [HIGH], [MEDIUM], [LOW] indicators

### Implementation for User Story 8

- [x] T057 [US8] Add priority display property returning "[HIGH]", "[MEDIUM]", "[LOW]" in Priority enum
- [x] T058 [US8] Update format_task_row() to show priority indicator with task in src/todo/cli/display.py
- [x] T059 [US8] Ensure add_task_handler defaults to medium priority when skipped
- [x] T060 [US8] Ensure update_task_handler allows priority modification

**Checkpoint**: Priority displays correctly, defaults work, updates function

---

## Phase 10: User Story 9 - Assign Tags/Categories (Priority: P2)

**Goal**: Support multiple tags per task displayed as hashtags

**Independent Test**: Add tasks with various tags, verify #hashtag display format

### Implementation for User Story 9

- [x] T061 [US9] Create format_tags() function returning "#tag1 #tag2" or "(no tags)" in src/todo/cli/display.py
- [x] T062 [US9] Update format_task_row() to include formatted tags in src/todo/cli/display.py
- [x] T063 [US9] Ensure tag normalization (lowercase, trim, dedupe) in _normalize_tags()
- [x] T064 [US9] Verify tag update replaces rather than appends in update_task

**Checkpoint**: Tags display as hashtags, normalization and limits enforced

---

## Phase 11: User Story 10 - Search Tasks (Priority: P2)

**Goal**: Search tasks by keyword in title and description (case-insensitive)

**Independent Test**: Add multiple tasks, search for keywords, verify matching results

### Implementation for User Story 10

- [x] T065 [US10] Implement search logic in TaskService.list_tasks(search=keyword)
- [x] T066 [US10] Ensure case-insensitive matching in title and description
- [x] T067 [US10] Implement search_tasks_handler prompting for search term in src/todo/cli/handlers.py
- [x] T068 [US10] Display "Found X tasks matching 'term'" with results
- [x] T069 [US10] Handle empty results with "No tasks found matching 'term'" message
- [x] T070 [US10] Handle empty search term by showing all tasks

**Checkpoint**: Search finds tasks by keyword, displays clear results

---

## Phase 12: User Story 11 - Filter Tasks (Priority: P2)

**Goal**: Filter tasks by status, priority, or tag

**Independent Test**: Add tasks with varied properties, apply filters, verify correct subsets shown

### Implementation for User Story 11

- [x] T071 [US11] Implement status filter in TaskService.list_tasks(status="pending"|"completed")
- [x] T072 [US11] Implement priority filter in TaskService.list_tasks(priority=Priority)
- [x] T073 [US11] Implement tag filter in TaskService.list_tasks(tag="tagname")
- [x] T074 [US11] Create FilterState dataclass (status, priority, tag) in src/todo/cli/app.py
- [x] T075 [US11] Add current_filter attribute to TodoCLI class
- [x] T076 [US11] Create filter submenu (by status/priority/tag/clear all) in src/todo/cli/handlers.py
- [x] T077 [US11] Implement filter_tasks_handler with submenu navigation
- [x] T078 [US11] Display active filter indicator in view_tasks_handler ("Showing: pending only")
- [x] T079 [US11] Handle "No tasks match filter" message

**Checkpoint**: All filter types work, active filter indicated, clear filter resets view

---

## Phase 13: User Story 12 - Sort Tasks (Priority: P3)

**Goal**: Sort tasks by priority, title, creation date, or status

**Independent Test**: Add multiple tasks, apply different sorts, verify correct ordering

### Implementation for User Story 12

- [x] T080 [US12] Implement _sort_tasks(tasks, sort_by) helper in TaskService
- [x] T081 [US12] Add sort by priority (HIGH→MEDIUM→LOW) using Priority IntEnum value
- [x] T082 [US12] Add sort by title (A→Z, case-insensitive)
- [x] T083 [US12] Add sort by created date (newest first and oldest first)
- [x] T084 [US12] Add sort by status (pending first)
- [x] T085 [US12] Create SortState dataclass (field, reverse) in src/todo/cli/app.py
- [x] T086 [US12] Add current_sort attribute to TodoCLI class
- [x] T087 [US12] Create sort submenu (priority/title/created/status/default) in src/todo/cli/handlers.py
- [x] T088 [US12] Implement sort_tasks_handler with submenu navigation
- [x] T089 [US12] Display current sort order in view_tasks_handler ("Sorted by: priority")

**Checkpoint**: All sort options work correctly, sort indicator displayed

---

## Phase 14: User Story 7 - Graceful Error Handling (Priority: P3)

**Goal**: Helpful error messages for all invalid inputs, never crash

**Independent Test**: Intentionally provide invalid inputs at various prompts, verify helpful messages

### Implementation for User Story 7

- [x] T090 [US7] Add try-except wrapper in main application loop for unexpected exceptions
- [x] T091 [US7] Create format_error() function for consistent error message styling in src/todo/cli/display.py
- [x] T092 [US7] Ensure all ValidationError messages include field name and specific guidance
- [x] T093 [US7] Ensure all TaskNotFoundError messages include the attempted task ID
- [x] T094 [US7] Add catch-all handler returning to main menu with "An error occurred. Please try again."
- [x] T095 [US7] Verify KeyboardInterrupt displays "Goodbye!" and exits cleanly

**Checkpoint**: No crashes possible, all errors show helpful messages

---

## Phase 15: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements affecting multiple user stories

- [x] T096 [P] Add ANSI color support with fallback for priority/status/errors in src/todo/cli/display.py
- [x] T097 [P] Verify all handlers export from src/todo/cli/handlers.py
- [x] T098 [P] Ensure all __init__.py files properly export public API
- [x] T099 Run quickstart.md validation - verify application runs with documented commands
- [x] T100 Verify 9-feature integration: all menu options 1-9 functional end-to-end
- [x] T101 Performance check: verify <100ms response for operations with 100 sample tasks

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ─────────────────────────────────────────────┐
                                                            │
Phase 2: Foundational (Domain Layer) ─────────────────────────┼─── BLOCKS ALL USER STORIES
                                                            │
┌───────────────────────────────────────────────────────────┘
│
├─► Phase 3: US6 Menu System (P1) ──────────────────────────► Required for all other stories
│
├─► Phase 4: US1 View Tasks (P1) 🎯 MVP
│
├─► Phase 5: US2 Add Task (P1)
│
├─► Phase 6: US3 Mark Complete (P2)
│
├─► Phase 7: US4 Update Task (P2)
│
├─► Phase 8: US5 Delete Task (P2)
│
├─► Phase 9: US8 Set Priority (P2) ─────────────────────────► Can parallel with US9-US11
│
├─► Phase 10: US9 Assign Tags (P2) ─────────────────────────► Can parallel with US8, US10-US11
│
├─► Phase 11: US10 Search Tasks (P2) ───────────────────────► Can parallel with US8-US9, US11
│
├─► Phase 12: US11 Filter Tasks (P2) ───────────────────────► Can parallel with US8-US10
│
├─► Phase 13: US12 Sort Tasks (P3)
│
├─► Phase 14: US7 Error Handling (P3)
│
└─► Phase 15: Polish
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US6 (Menu) | Foundational | None - required first |
| US1 (View) | US6 | None - needed for verification |
| US2 (Add) | US1 | None |
| US3 (Complete) | US1, US2 | US4, US5 |
| US4 (Update) | US1, US2 | US3, US5 |
| US5 (Delete) | US1, US2 | US3, US4 |
| US8 (Priority) | US2 | US9, US10, US11 |
| US9 (Tags) | US2 | US8, US10, US11 |
| US10 (Search) | US1 | US8, US9, US11 |
| US11 (Filter) | US1 | US8, US9, US10 |
| US12 (Sort) | US1 | US7 |
| US7 (Errors) | All above | US12 |

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:
- **Setup**: T003-T006, T008 (package __init__.py files)
- **Foundational**: T011-T013 (exception classes)
- **Polish**: T096-T098 (independent enhancements)

---

## Parallel Example: Setup Phase

```bash
# Can run these simultaneously:
Task: "Create src/todo/domain/__init__.py" [T003]
Task: "Create src/todo/services/__init__.py" [T004]
Task: "Create src/todo/repository/__init__.py" [T005]
Task: "Create src/todo/cli/__init__.py" [T006]
```

## Parallel Example: Intermediate Features

```bash
# After Basic Level complete, these can run in parallel:
Task: "Implement search logic in TaskService" [T065] - US10
Task: "Implement status filter in TaskService" [T071] - US11
Task: "Implement _sort_tasks helper in TaskService" [T080] - US12
```

---

## Implementation Strategy

### MVP First (Basic Level - User Stories 1-6)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US6 Menu System
4. Complete Phase 4: US1 View Tasks
5. Complete Phase 5: US2 Add Task
6. **STOP and VALIDATE**: Test View + Add independently
7. Complete Phases 6-8: US3, US4, US5 (Complete, Update, Delete)
8. **CHECKPOINT**: All 5 Basic Level features functional

### Intermediate Enhancement (User Stories 8-12)

9. Complete Phases 9-10: US8 Priority + US9 Tags (can parallel)
10. Complete Phases 11-12: US10 Search + US11 Filter (can parallel)
11. Complete Phase 13: US12 Sort
12. Complete Phase 14: US7 Error Handling
13. Complete Phase 15: Polish

### Final Delivery

- **Total: 101 tasks** organized across 15 phases
- **9 features**: 5 Basic + 4 Intermediate (exceeds hackathon requirements)
- **Architecture**: 4-layer Clean Architecture ready for Phase II evolution

---

## Task Summary

| Phase | Description | Task Count | Parallelizable |
|-------|-------------|------------|----------------|
| 1 | Setup | 8 | 5 |
| 2 | Foundational | 9 | 3 |
| 3 | US6 Menu | 7 | 0 |
| 4 | US1 View | 8 | 0 |
| 5 | US2 Add | 8 | 0 |
| 6 | US3 Complete | 5 | 0 |
| 7 | US4 Update | 6 | 0 |
| 8 | US5 Delete | 5 | 0 |
| 9 | US8 Priority | 4 | 0 |
| 10 | US9 Tags | 4 | 0 |
| 11 | US10 Search | 6 | 0 |
| 12 | US11 Filter | 9 | 0 |
| 13 | US12 Sort | 10 | 0 |
| 14 | US7 Errors | 6 | 0 |
| 15 | Polish | 6 | 3 |
| **Total** | | **101** | **11** |

### Tasks per User Story

| User Story | Priority | Task Count | Description |
|------------|----------|------------|-------------|
| US1 | P1 | 8 | View All Tasks |
| US2 | P1 | 8 | Add New Task |
| US6 | P1 | 7 | Navigate Menu System |
| US3 | P2 | 5 | Mark Complete/Incomplete |
| US4 | P2 | 6 | Update Existing Task |
| US5 | P2 | 5 | Delete Task |
| US8 | P2 | 4 | Set Task Priority |
| US9 | P2 | 4 | Assign Tags/Categories |
| US10 | P2 | 6 | Search Tasks |
| US11 | P2 | 9 | Filter Tasks |
| US12 | P3 | 10 | Sort Tasks |
| US7 | P3 | 6 | Graceful Error Handling |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label (e.g., [US1]) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

*Tasks version: 1.0*
*Generated from: spec.md v1.0, plan.md v1.0, data-model.md v1.0*
*Ready for: `/sp.implement`*
