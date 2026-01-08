# Feature Specification: Phase 1 - In-Memory Python Console Todo App

**Feature Branch**: `003-phase1-console-app`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "Phase 1: In-Memory Python Console Todo App with Basic + Intermediate Level Features - Building an extraordinary foundation for the Evolution of Todo hackathon"

## Overview

This specification defines the foundation phase of the "Evolution of Todo" hackathon project. The goal is to build a command-line todo application that stores tasks in memory, implementing all 5 Basic Level features **PLUS** all 4 Intermediate Level features, establishing clean architecture patterns that will scale across subsequent phases.

### Vision Statement

Create an intuitive, reliable, and well-structured console-based task management application that **exceeds hackathon requirements** by delivering both Basic and Intermediate functionality. This demonstrates mastery of spec-driven development principles while serving as the architectural foundation for the full cloud-native AI chatbot evolution.

### Scope

**In Scope:**
- Command-line interface for task management
- In-memory task storage (data persists only during application runtime)
- **All 5 Basic Level features** (Add, Delete, Update, View, Mark Complete)
- **All 4 Intermediate Level features** (Priorities, Tags/Categories, Search & Filter, Sort)
- Clean, modular code architecture ready for future expansion
- Comprehensive user feedback and error handling
- Interactive menu-driven interface

**Out of Scope:**
- Persistent storage (database, file-based) - deferred to Phase II
- Multi-user support - deferred to Phase II
- Web interface - deferred to Phase II
- AI/chatbot features - deferred to Phase III
- Authentication/authorization - deferred to Phase II
- Advanced Level features (Recurring Tasks, Due Dates & Reminders) - deferred to Phase V

---

## User Scenarios & Testing *(mandatory)*

### BASIC LEVEL FEATURES

---

### User Story 1 - View All Tasks (Priority: P1)

As a user, I want to see all my tasks at a glance so I can understand what needs to be done and track my progress.

**Why this priority**: Viewing tasks is the most fundamental operation - without it, users cannot understand the state of their todo list. Every other operation depends on being able to see results.

**Independent Test**: Can be fully tested by launching the application and selecting "View Tasks" from the menu.

**Acceptance Scenarios**:

1. **Given** an empty task list, **When** user selects "View Tasks", **Then** system displays a friendly message indicating no tasks exist with guidance on how to add one
2. **Given** a list with 3 tasks (2 pending, 1 completed), **When** user selects "View Tasks", **Then** system displays all tasks with ID, title, description preview, priority, tags, status indicator (pending/completed), and creation order
3. **Given** a task with a long description, **When** viewing the task list, **Then** description is truncated to 50 characters with "..." indicator
4. **Given** tasks exist, **When** user views tasks, **Then** completed tasks are visually distinguished from pending tasks (e.g., strikethrough styling or clear status marker)
5. **Given** tasks with different priorities, **When** viewing tasks, **Then** priority is displayed with visual indicator (e.g., [HIGH], [MEDIUM], [LOW])
6. **Given** tasks with tags, **When** viewing tasks, **Then** tags are displayed in a compact format (e.g., #work #urgent)

---

### User Story 2 - Add New Task (Priority: P1)

As a user, I want to add new tasks with a title, optional description, priority, and tags so I can capture things I need to do with full context.

**Why this priority**: Adding tasks is the entry point for all functionality - users must be able to create tasks before they can view, update, delete, or complete them.

**Independent Test**: Can be fully tested by launching the application, selecting "Add Task", entering task details, and confirming the task was created by viewing the task list.

**Acceptance Scenarios**:

1. **Given** the main menu, **When** user selects "Add Task" and enters a valid title "Buy groceries", **Then** system creates the task with default priority (medium), no tags, assigns a unique ID, sets status to pending, and confirms creation
2. **Given** user is adding a task, **When** user provides title, description, priority "high", and tags "shopping, errands", **Then** system stores all fields and confirms successful creation
3. **Given** user is adding a task, **When** user provides only a title (skipping optional fields), **Then** system creates task with defaults (medium priority, no tags, empty description)
4. **Given** user attempts to add a task, **When** title is empty or whitespace only, **Then** system displays error "Title is required" and prompts user to enter a valid title
5. **Given** user is setting priority, **When** user enters invalid priority, **Then** system displays valid options (high/medium/low) and prompts again
6. **Given** user is adding tags, **When** user enters "work, home, urgent", **Then** system parses and stores as separate tags ["work", "home", "urgent"]

---

### User Story 3 - Mark Task as Complete/Incomplete (Priority: P2)

As a user, I want to mark tasks as complete when I finish them, and toggle them back to pending if needed, so I can track my progress.

**Why this priority**: Completion tracking is the core value proposition of a todo app.

**Independent Test**: Can be tested by adding a task, marking it complete, verifying the status change, and toggling it back.

**Acceptance Scenarios**:

1. **Given** a pending task with ID 1, **When** user selects "Mark Complete" and enters ID 1, **Then** task status changes to completed and system confirms "Task 1 marked as completed"
2. **Given** a completed task with ID 2, **When** user selects "Mark Complete" and enters ID 2, **Then** task status toggles back to pending and system confirms "Task 2 marked as pending"
3. **Given** no task exists with ID 99, **When** user attempts to mark task 99 as complete, **Then** system displays error "Task with ID 99 not found"
4. **Given** user is prompted for task ID, **When** user enters non-numeric input "abc", **Then** system displays error "Please enter a valid task ID (number)"

---

### User Story 4 - Update Existing Task (Priority: P2)

As a user, I want to update any field of an existing task (title, description, priority, tags) so I can correct mistakes or change task properties.

**Why this priority**: Tasks often need refinement after creation.

**Independent Test**: Can be tested by adding a task, updating various fields, and verifying changes in the task list.

**Acceptance Scenarios**:

1. **Given** task ID 1 with title "Buy groceries", **When** user selects "Update Task", enters ID 1, and provides new title "Buy groceries and vegetables", **Then** title is updated and system confirms the change
2. **Given** task ID 1 with priority "medium", **When** user updates priority to "high", **Then** priority is updated and system confirms the change
3. **Given** task ID 1 with tags ["work"], **When** user updates tags to "work, urgent", **Then** tags are replaced with ["work", "urgent"]
4. **Given** task ID 1, **When** user chooses to update only one field (leaving others unchanged), **Then** only selected field is updated, others remain unchanged
5. **Given** no task exists with ID 50, **When** user attempts to update task 50, **Then** system displays error "Task with ID 50 not found"
6. **Given** user is updating a task, **When** user provides empty title, **Then** system displays error "Title cannot be empty" and retains original title

---

### User Story 5 - Delete Task (Priority: P2)

As a user, I want to permanently remove tasks I no longer need so I can keep my task list clean and focused.

**Why this priority**: Cleanup capability prevents list clutter.

**Independent Test**: Can be tested by adding a task, deleting it, and verifying it no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** task ID 3 exists, **When** user selects "Delete Task" and enters ID 3, **Then** task is permanently removed and system confirms "Task 3 deleted successfully"
2. **Given** no task exists with ID 100, **When** user attempts to delete task 100, **Then** system displays error "Task with ID 100 not found"
3. **Given** user selects delete, **When** system prompts for confirmation (showing task title), **Then** user must confirm before deletion proceeds
4. **Given** user is at confirmation prompt, **When** user declines deletion, **Then** task is not deleted and user returns to main menu

---

### INTERMEDIATE LEVEL FEATURES

---

### User Story 8 - Set Task Priority (Priority: P2)

As a user, I want to assign priority levels (high/medium/low) to tasks so I can focus on what's most important.

**Why this priority**: Priority helps users triage work and focus on high-impact tasks first.

**Independent Test**: Can be tested by adding tasks with different priorities and verifying they display correctly with visual distinction.

**Acceptance Scenarios**:

1. **Given** user is adding a task, **When** user sets priority to "high", **Then** task is created with high priority and displays with [HIGH] indicator
2. **Given** user is adding a task, **When** user sets priority to "medium", **Then** task is created with medium priority and displays with [MEDIUM] indicator
3. **Given** user is adding a task, **When** user sets priority to "low", **Then** task is created with low priority and displays with [LOW] indicator
4. **Given** user is adding a task, **When** user skips priority selection, **Then** task defaults to medium priority
5. **Given** user is updating a task, **When** user changes priority from "low" to "high", **Then** priority is updated and confirmed
6. **Given** high priority tasks exist, **When** viewing task list, **Then** high priority tasks are visually emphasized (e.g., color or symbol)

---

### User Story 9 - Assign Tags/Categories (Priority: P2)

As a user, I want to assign multiple tags (categories) to tasks so I can organize and group related tasks.

**Why this priority**: Tags enable flexible organization that adapts to different workflows (work/home, projects, contexts).

**Independent Test**: Can be tested by adding tasks with various tags and filtering by those tags.

**Acceptance Scenarios**:

1. **Given** user is adding a task, **When** user enters tags "work, meeting", **Then** task is created with tags ["work", "meeting"]
2. **Given** user is adding a task, **When** user enters single tag "personal", **Then** task is created with tags ["personal"]
3. **Given** user is adding a task, **When** user skips tag entry, **Then** task is created with no tags (empty list)
4. **Given** task has tags, **When** viewing task, **Then** tags display as hashtags (e.g., #work #meeting)
5. **Given** user is updating a task, **When** user modifies tags, **Then** tags are completely replaced (not appended)
6. **Given** user enters tags with extra spaces "work , home, urgent ", **Then** system trims whitespace and stores clean tags
7. **Given** user enters duplicate tags "work, work, home", **Then** system stores unique tags only ["work", "home"]

---

### User Story 10 - Search Tasks (Priority: P2)

As a user, I want to search for tasks by keyword so I can quickly find specific tasks without scrolling through the entire list.

**Why this priority**: Search becomes essential as task lists grow, enabling quick access to specific items.

**Independent Test**: Can be tested by adding multiple tasks and searching for specific keywords to verify matching results.

**Acceptance Scenarios**:

1. **Given** tasks exist with titles containing "groceries", **When** user searches for "groceries", **Then** system displays only tasks with "groceries" in title or description
2. **Given** task has description "Buy milk from store", **When** user searches for "milk", **Then** task appears in search results
3. **Given** no tasks match search term "xyz123", **When** user searches for "xyz123", **Then** system displays "No tasks found matching 'xyz123'"
4. **Given** search term "Work", **When** user searches, **Then** search is case-insensitive and matches "work", "WORK", "Work"
5. **Given** user enters empty search term, **When** search executes, **Then** system displays all tasks (no filter applied)
6. **Given** search results found, **When** displaying results, **Then** matching keywords are highlighted or search term is shown

---

### User Story 11 - Filter Tasks (Priority: P2)

As a user, I want to filter tasks by status, priority, or tag so I can focus on specific subsets of my task list.

**Why this priority**: Filtering enables focused work by hiding irrelevant tasks temporarily.

**Independent Test**: Can be tested by adding tasks with various properties and applying different filters to verify correct subsets are shown.

**Acceptance Scenarios**:

1. **Given** tasks with mixed statuses, **When** user filters by "pending", **Then** only pending tasks are displayed
2. **Given** tasks with mixed statuses, **When** user filters by "completed", **Then** only completed tasks are displayed
3. **Given** tasks with mixed priorities, **When** user filters by priority "high", **Then** only high-priority tasks are displayed
4. **Given** tasks with various tags, **When** user filters by tag "work", **Then** only tasks tagged with "work" are displayed
5. **Given** user applies filter, **When** no tasks match filter, **Then** system displays "No tasks match the current filter"
6. **Given** filter is active, **When** viewing tasks, **Then** system indicates active filter (e.g., "Showing: pending tasks only")
7. **Given** filter is active, **When** user selects "clear filter" or "show all", **Then** all tasks are displayed again

---

### User Story 12 - Sort Tasks (Priority: P3)

As a user, I want to sort tasks by different criteria (priority, title, creation date, status) so I can view my tasks in the most useful order.

**Why this priority**: Sorting helps users organize their view based on current needs - urgency, alphabetical lookup, or chronological review.

**Independent Test**: Can be tested by adding multiple tasks and applying different sort orders to verify correct ordering.

**Acceptance Scenarios**:

1. **Given** tasks with different priorities, **When** user sorts by priority, **Then** tasks display in order: high, medium, low
2. **Given** tasks with various titles, **When** user sorts by title, **Then** tasks display in alphabetical order (A-Z)
3. **Given** tasks created at different times, **When** user sorts by creation date (newest first), **Then** most recently created tasks appear first
4. **Given** tasks created at different times, **When** user sorts by creation date (oldest first), **Then** oldest tasks appear first
5. **Given** tasks with mixed statuses, **When** user sorts by status, **Then** pending tasks appear before completed tasks (or vice versa based on preference)
6. **Given** sort is applied, **When** viewing tasks, **Then** system indicates current sort order (e.g., "Sorted by: priority")
7. **Given** user has not selected sort, **When** viewing tasks, **Then** default sort is by creation order (ID ascending)

---

### SYSTEM FEATURES

---

### User Story 6 - Navigate Menu System (Priority: P1)

As a user, I want a clear, intuitive menu system so I can easily access all features without confusion.

**Why this priority**: The menu is the primary interface - poor navigation undermines all other features.

**Independent Test**: Can be tested by launching the application and navigating through all menu options.

**Acceptance Scenarios**:

1. **Given** application starts, **When** main menu displays, **Then** all options are clearly visible:
   - (1) View Tasks
   - (2) Add Task
   - (3) Update Task
   - (4) Delete Task
   - (5) Mark Complete/Incomplete
   - (6) Search Tasks
   - (7) Filter Tasks
   - (8) Sort Tasks
   - (9) Exit
2. **Given** main menu is displayed, **When** user enters a valid option number, **Then** system navigates to the corresponding feature
3. **Given** main menu is displayed, **When** user enters invalid input, **Then** system displays error "Invalid option" and re-displays menu
4. **Given** user completes any operation, **When** operation finishes, **Then** system returns to main menu automatically
5. **Given** user selects Exit, **When** confirmed, **Then** application terminates gracefully with farewell message

---

### User Story 7 - Graceful Error Handling (Priority: P3)

As a user, I want helpful error messages when I make mistakes so I can understand what went wrong and correct my input.

**Why this priority**: Good error handling improves user experience and reduces frustration.

**Independent Test**: Can be tested by intentionally providing invalid inputs at various prompts.

**Acceptance Scenarios**:

1. **Given** any input prompt, **When** user enters unexpected input type, **Then** system provides specific guidance on expected format
2. **Given** an operation fails, **When** error occurs, **Then** system never crashes - always displays error and returns to stable state (main menu)
3. **Given** user interrupts with Ctrl+C, **When** interrupt signal received, **Then** application exits gracefully with message "Goodbye!"

---

### Edge Cases

**Basic Operations:**
- Empty task list operations: Delete, Update, Mark Complete on empty list should display "No tasks available"
- ID uniqueness: Task IDs must remain unique even after deletion (IDs should not be reused)
- Input length limits: Titles max 200 characters; descriptions max 1000 characters

**Intermediate Operations:**
- Invalid priority: Entering "critical" instead of "high/medium/low" prompts re-entry
- Tag limits: Maximum 10 tags per task; tags max 30 characters each
- Empty search: Returns all tasks
- Combined filters: System handles multiple active filters gracefully
- Sort stability: Tasks with equal sort values maintain relative order

**General:**
- Whitespace handling: Leading/trailing whitespace trimmed from all inputs
- Special characters: Titles, descriptions, and tags may contain special characters, emojis, unicode
- Memory constraints: System should handle up to 1000 tasks without performance degradation

---

## Requirements *(mandatory)*

### Functional Requirements - Basic Level

- **FR-001**: System MUST provide an interactive command-line menu with numbered options for all features
- **FR-002**: System MUST support adding tasks with required title (1-200 characters) and optional description (0-1000 characters)
- **FR-003**: System MUST assign unique sequential integer IDs to each task starting from 1
- **FR-004**: System MUST store all tasks in memory during application runtime
- **FR-005**: System MUST display all tasks with ID, title, description preview, priority, tags, and completion status
- **FR-006**: System MUST allow updating task title, description, priority, and tags by task ID
- **FR-007**: System MUST allow deleting tasks by task ID with confirmation
- **FR-008**: System MUST allow toggling task completion status (complete/incomplete) by task ID
- **FR-009**: System MUST validate all user inputs and display helpful error messages for invalid input
- **FR-010**: System MUST handle graceful exit via menu option and Ctrl+C interrupt
- **FR-011**: System MUST distinguish completed tasks visually from pending tasks in the task list display
- **FR-012**: System MUST display task counts (total, pending, completed) when viewing task list
- **FR-013**: System MUST trim leading/trailing whitespace from user inputs
- **FR-014**: System MUST reject empty or whitespace-only titles
- **FR-015**: System MUST return to main menu after completing any operation

### Functional Requirements - Intermediate Level

- **FR-016**: System MUST support task priority levels: high, medium (default), low
- **FR-017**: System MUST visually distinguish priority levels in task display (e.g., [HIGH], [MEDIUM], [LOW])
- **FR-018**: System MUST support multiple tags per task (0-10 tags, each max 30 characters)
- **FR-019**: System MUST display tags in hashtag format (e.g., #work #urgent)
- **FR-020**: System MUST remove duplicate tags automatically
- **FR-021**: System MUST support keyword search across task titles and descriptions (case-insensitive)
- **FR-022**: System MUST support filtering by status (all/pending/completed)
- **FR-023**: System MUST support filtering by priority (high/medium/low)
- **FR-024**: System MUST support filtering by tag
- **FR-025**: System MUST indicate when a filter is active
- **FR-026**: System MUST support sorting by priority (high to low)
- **FR-027**: System MUST support sorting by title (alphabetical A-Z)
- **FR-028**: System MUST support sorting by creation date (newest/oldest first)
- **FR-029**: System MUST support sorting by status (pending first or completed first)
- **FR-030**: System MUST indicate current sort order when displaying tasks

### Key Entities

- **Task**: Represents a single todo item
  - Unique identifier (integer, auto-assigned, sequential)
  - Title (required, 1-200 characters, trimmed)
  - Description (optional, 0-1000 characters, trimmed)
  - Priority (enum: high/medium/low, default: medium)
  - Tags (list of strings, 0-10 items, each max 30 characters, unique, trimmed)
  - Completion status (boolean: pending or completed, default: pending)
  - Creation timestamp (for sorting by date)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Basic Level:**
- **SC-001**: Users can add a new task in under 30 seconds from application start
- **SC-002**: Users can view all tasks and understand their status in under 5 seconds
- **SC-003**: Users can complete any single operation (add/update/delete/complete) in under 3 menu selections
- **SC-004**: System handles 100 consecutive operations without error or crash
- **SC-005**: 100% of invalid inputs result in helpful error messages (never crashes or hangs)
- **SC-006**: All 5 Basic Level features (Add, Delete, Update, View, Mark Complete) are fully functional

**Intermediate Level:**
- **SC-007**: Users can set priority on a task during creation in under 10 seconds
- **SC-008**: Users can add tags to a task during creation in under 15 seconds
- **SC-009**: Users can find a specific task via search in under 10 seconds (from 50+ tasks)
- **SC-010**: Users can filter to see only high-priority pending tasks in under 3 menu selections
- **SC-011**: Users can sort tasks by priority in under 2 menu selections
- **SC-012**: All 4 Intermediate Level features (Priorities, Tags, Search/Filter, Sort) are fully functional

**System:**
- **SC-013**: Application starts and displays menu in under 2 seconds
- **SC-014**: Task list displays correctly with up to 100 tasks without truncation or formatting issues

---

## Assumptions

- Users are familiar with command-line interfaces and can enter text and numbers
- Terminal supports basic text display (no graphical elements required)
- Application runs in a single session - data loss on exit is expected (in-memory storage)
- Python 3.13+ runtime environment is available
- UV package manager is available for dependency management
- Single user operates the application at any time (no concurrency requirements)

## Dependencies

- Python 3.13+ runtime
- UV package manager for project setup
- Standard library only (no external dependencies for core functionality)

## Constraints

- In-memory storage only - no file or database persistence
- Command-line interface only - no graphical user interface
- Single-user, single-session operation
- Must follow clean code principles and proper Python project structure
- Must use spec-driven development workflow (Spec -> Plan -> Tasks -> Implement)

## Future Considerations

This Phase 1 implementation establishes architectural patterns that will be extended in subsequent phases:

- **Phase II**: Task model extends to include user association; storage migrates to PostgreSQL; all features become REST API endpoints
- **Phase III**: Operations become MCP tools callable by AI agents; natural language interface
- **Phase IV-V**: Application containerizes and deploys to Kubernetes; Advanced Level features added (Recurring Tasks, Due Dates & Reminders)

The clean separation of concerns established here (presentation, business logic, data) will enable smooth evolution.
