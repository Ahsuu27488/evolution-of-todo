# Feature Specification: Advanced Level Features - Recurring Tasks & Due Dates

**Feature Branch**: `004-advanced-features`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "Take Our Phase 1 to Advanced level, since we are currently at intermediate level. Read Hackathon2_doc.md"

## Overview

This specification extends the Phase 1 Console App from Intermediate Level (5 Basic + 4 Intermediate = 9 features) to **Advanced Level** by adding two intelligent time-based features:

1. **Due Dates & Time Reminders** - Set deadlines with visual indicators for overdue/upcoming tasks
2. **Recurring Tasks** - Auto-reschedule repeating tasks (daily, weekly, monthly)

These features add **time-based intelligence** to the todo app, preparing for Phase V's Kafka event-driven reminder system.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Due Date on Task (Priority: P1)

A user wants to set a deadline for a task so they can track when it needs to be completed. When viewing tasks, they should immediately see which tasks are overdue, due soon, or have time remaining.

**Why this priority**: Due dates are the foundation for time-based task management. Without this, recurring tasks cannot function. This is the most critical feature for advancing to Advanced Level.

**Independent Test**: Can be fully tested by creating a task with a due date, waiting for time to pass, and observing visual indicators change from "upcoming" to "due soon" to "overdue".

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they are prompted for optional fields, **Then** they can enter a due date in format YYYY-MM-DD
2. **Given** a task has a due date set, **When** the user views tasks, **Then** the due date is displayed with color-coded status (red=overdue, yellow=due within 24 hours, gray=future)
3. **Given** a task has no due date, **When** the user views tasks, **Then** the task displays "(no deadline)" in the due date column
4. **Given** a user is updating a task, **When** they select "Due Date" from the update menu, **Then** they can set, change, or remove the due date

---

### User Story 2 - Create Recurring Task (Priority: P2)

A user has regular tasks that repeat on a schedule (daily standup, weekly review, monthly report). They want to create a task once with a recurrence pattern, and have the system automatically create the next occurrence when they complete the current one.

**Why this priority**: Recurring tasks build on due dates and provide significant automation value. This is the second Advanced Level feature required by the hackathon.

**Independent Test**: Can be fully tested by creating a recurring task, marking it complete, and verifying a new task is automatically created with the next due date.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they set a due date, **Then** they are prompted to optionally set a recurrence pattern (none, daily, weekly, monthly)
2. **Given** a recurring task exists, **When** the user marks it as complete, **Then** the system automatically creates a new task with the same title, description, priority, and tags, with the due date advanced according to the recurrence pattern
3. **Given** a recurring task is marked complete, **When** the new occurrence is created, **Then** the user sees a message confirming the next occurrence (e.g., "Task completed! Next occurrence scheduled for 2025-01-22")
4. **Given** a user is viewing tasks, **When** a task has recurrence, **Then** a recurrence indicator is displayed (e.g., "Daily", "Weekly", "Monthly")

---

### User Story 3 - Filter and Sort by Due Date (Priority: P3)

A user wants to focus on tasks that are due soon or overdue. They should be able to filter to see only tasks with upcoming deadlines and sort tasks by due date.

**Why this priority**: Enhances usability of due dates but is not strictly required for Advanced Level. Builds on existing filter/sort infrastructure.

**Independent Test**: Can be tested by creating tasks with various due dates and filtering to "due today" or "overdue", verifying only matching tasks appear.

**Acceptance Scenarios**:

1. **Given** tasks exist with various due dates, **When** the user selects "Filter by Due Date", **Then** they can choose from: "Overdue", "Due Today", "Due This Week", "No Deadline", "All"
2. **Given** a filter is applied, **When** tasks are displayed, **Then** only tasks matching the due date criteria appear
3. **Given** the user selects "Sort by Due Date", **When** tasks are displayed, **Then** tasks are ordered by due date (earliest first, tasks without due dates appear last)

---

### User Story 4 - Manage Recurring Task Settings (Priority: P3)

A user wants to modify or remove the recurrence pattern on an existing task without recreating it.

**Why this priority**: Quality-of-life improvement for recurring tasks but not essential for the core feature.

**Independent Test**: Can be tested by creating a recurring task, updating its recurrence pattern, and verifying the change takes effect on next completion.

**Acceptance Scenarios**:

1. **Given** a task exists (recurring or not), **When** the user selects "Update Task" and chooses "Recurrence", **Then** they can set, change, or remove the recurrence pattern
2. **Given** a recurring task has its pattern removed, **When** the task is completed, **Then** no new occurrence is created

---

### Edge Cases

- What happens when a user enters an invalid date format? → System shows error and re-prompts with format examples
- What happens when a due date is set in the past? → System accepts it but immediately shows as "overdue"
- What happens when a recurring task's next occurrence would fall on a date in the past (e.g., task completed very late)? → System calculates next valid future date
- What happens when a user deletes a recurring task? → Only that occurrence is deleted; no new occurrence is created
- What happens when a task has both recurrence and is marked incomplete after being completed? → Toggle behavior: if task becomes incomplete, no new occurrence should be created until it's completed again
- What happens with monthly recurrence on the 31st? → Adjusts to last day of shorter months (Feb 28/29, Apr/Jun/Sep/Nov 30)

---

## Requirements *(mandatory)*

### Functional Requirements

#### Due Dates

- **FR-001**: System MUST allow users to set an optional due date when creating a task
- **FR-002**: System MUST accept due dates in format "YYYY-MM-DD" and display them in a user-friendly format
- **FR-003**: System MUST display due date status with visual indicators:
  - Red for overdue tasks (past due date)
  - Yellow for tasks due within 24 hours
  - Gray/normal for future tasks
- **FR-004**: System MUST allow users to update or remove a task's due date
- **FR-005**: System MUST display "(no deadline)" for tasks without a due date
- **FR-006**: System MUST add "Due Date" as a sort option (earliest due dates first, no-deadline tasks last)
- **FR-007**: System MUST add "Due Date" as a filter option with choices: Overdue, Due Today, Due This Week, No Deadline, All

#### Recurring Tasks

- **FR-008**: System MUST allow users to set an optional recurrence pattern when a task has a due date
- **FR-009**: System MUST support recurrence patterns: None, Daily, Weekly, Monthly
- **FR-010**: System MUST automatically create a new task occurrence when a recurring task is marked complete
- **FR-011**: New occurrences MUST copy title, description, priority, tags, and recurrence pattern from the completed task
- **FR-012**: New occurrences MUST have their due date calculated based on the recurrence pattern:
  - Daily: +1 day from original due date
  - Weekly: +7 days from original due date
  - Monthly: Same day next month (adjusted for shorter months)
- **FR-013**: System MUST display recurrence indicator on tasks (e.g., icon or text showing "Daily", "Weekly", "Monthly")
- **FR-014**: System MUST allow users to update or remove recurrence pattern on existing tasks
- **FR-015**: System MUST NOT create new occurrences when a non-recurring task is completed
- **FR-016**: System MUST NOT create new occurrences when a recurring task is deleted
- **FR-017**: System MUST ensure new occurrence due dates are always in the future (skip past dates if task completed late)

### Key Entities

- **Task** (extended):
  - `due_date`: Optional date when task should be completed
  - `recurrence`: Optional pattern (none, daily, weekly, monthly)

- **RecurrencePattern** (new):
  - Represents the repeat schedule
  - Types: NONE, DAILY, WEEKLY, MONTHLY
  - Used to calculate next occurrence date

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with a due date in under 30 seconds (adding ~5 seconds to current task creation flow)
- **SC-002**: Users can identify overdue tasks within 1 second of viewing the task list (via clear visual indicators)
- **SC-003**: Users can create a recurring task and verify automatic rescheduling in under 2 minutes (create → complete → observe new task)
- **SC-004**: 100% of recurring task completions result in correctly scheduled new occurrences
- **SC-005**: Due date filters correctly show only matching tasks (0 false positives or negatives)
- **SC-006**: All 11 features (5 Basic + 4 Intermediate + 2 Advanced) are accessible from the main menu
- **SC-007**: Zero data loss when toggling completion status on recurring tasks

---

## Assumptions

1. **Date input format**: Users will enter dates in "YYYY-MM-DD" format. Natural language parsing ("tomorrow", "next week") is out of scope for Phase 1.
2. **Time precision**: Due dates are date-only (no time component). A task due on 2025-01-15 becomes overdue at midnight on 2025-01-16.
3. **Console notifications**: Since this is a console app, "reminders" are passive visual indicators, not active notifications. Active notifications will be implemented in Phase V with Kafka.
4. **Recurrence base date**: New occurrence dates are calculated from the original due date, not the completion date. This prevents "drift" if tasks are completed late.
5. **Single occurrence**: Only one occurrence of a recurring task exists at a time. The next occurrence is created only when the current one is completed.

---

## Out of Scope

- Active push notifications or alarms (Phase V feature with Kafka)
- Natural language date parsing ("tomorrow", "in 3 days")
- Custom recurrence intervals (e.g., "every 3 days", "every 2 weeks")
- End date for recurring tasks (e.g., "repeat weekly until March")
- Snooze or postpone functionality
- Calendar integration

---

## Dependencies

- Existing Phase 1 Console App with 9 features (Basic + Intermediate)
- Task domain model (`todo/domain/task.py`)
- Task service (`todo/services/task_service.py`)
- In-memory repository (`todo/repository/memory.py`)
- CLI handlers and display utilities
