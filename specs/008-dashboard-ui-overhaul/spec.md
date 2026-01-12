# Feature Specification: Advanced Dashboard UI Overhaul

**Feature Branch**: `008-dashboard-ui-overhaul`
**Created**: 2026-01-10
**Status**: Draft
**Input**: User description provided via `/sp.specify` command

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Advanced Task Creation (Priority: P1)

As a user managing tasks, I want to create tasks with rich attributes (due dates, tags, recurrence patterns) so that I can better organize and track my responsibilities beyond simple title and priority.

**Why this priority**: This is the foundational capability that enables all advanced task management features. Without the ability to create tasks with full attributes, filtering and sorting have limited value.

**Independent Test**: A user can create a task with a due date, multiple colored tags, and a weekly recurrence pattern. The task appears in the list with all attributes visibly displayed.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the dashboard, **When** they click the "Add Task" button, **Then** a glassmorphism modal opens with form fields for title, description, priority, due date picker, tag management, and recurrence selector
2. **Given** a user creating a task, **When** they select a due date using the datetime picker, **Then** the selected date is formatted and saved with the task
3. **Given** a user creating a task, **When** they add tags by typing and pressing Enter, **Then** colored tag chips appear and can be removed by clicking their × icon
4. **Given** a user creating a task, **When** they select a recurrence pattern (DAILY, WEEKLY, MONTHLY), **Then** a recurrence icon appears on the saved task card
5. **Given** a user with form validation errors, **When** they attempt to submit without a title, **Then** appropriate error messages display inline

---

### User Story 2 - Task Filtering and Search (Priority: P1)

As a user with many tasks, I want to filter and search through my tasks so that I can quickly find specific tasks without manually scanning the entire list.

**Why this priority**: Filter and search capabilities transform a long list into a manageable view. This is essential for productivity as the number of tasks grows.

**Independent Test**: A user can type in the search bar to see matching tasks in real-time, toggle status tabs to show only pending tasks, and select a priority filter to see only high-priority items.

**Acceptance Scenarios**:

1. **Given** an authenticated user with multiple tasks, **When** they type in the search bar, **Then** the task list updates in real-time (debounced) to show only matching tasks
2. **Given** a user viewing all tasks, **When** they click the "Pending" tab, **Then** only incomplete tasks are displayed
3. **Given** a user viewing filtered tasks, **When** they select "High" from the priority dropdown, **Then** only high-priority tasks matching the current status filter are shown
4. **Given** a user with active filters, **When** they clear the search or click "All" status, **Then** all tasks are displayed again

---

### User Story 3 - Task Sorting (Priority: P2)

As a user wanting to prioritize my work, I want to sort tasks by various criteria so that I can see the most urgent or relevant tasks at the top of my list.

**Why this priority**: Sorting enhances the utility of the task list but depends on having tasks to sort. Users can function without it, but it significantly improves the experience.

**Independent Test**: A user can select "Due Date" from the sort dropdown and toggle ascending/descending to see overdue tasks first or future tasks first.

**Acceptance Scenarios**:

1. **Given** an authenticated user with tasks, **When** they select "Due Date" from the sort dropdown, **Then** tasks reorder with those having due dates at the top
2. **Given** a user with tasks sorted by due date, **When** they click the sort direction toggle, **Then** the sort order reverses (ascending vs descending)
3. **Given** a user sorting by priority, **When** they select "Priority" from the dropdown, **Then** high-priority tasks appear at the top (with descending order)
4. **Given** a user sorting by title, **When** they select "Title", **Then** tasks sort alphabetically

---

### User Story 4 - Glassmorphism Visual Redesign (Priority: P2)

As a user, I want the dashboard to have the same stunning "Deep Space" glassmorphism aesthetic as the landing page so that my experience feels cohesive and modern throughout the application.

**Why this priority**: Visual consistency creates trust and delight. While functionally the app works without it, the aesthetic transformation is a key part of the "Advanced" experience promised in Phase II.

**Independent Test**: A user navigating from the landing page to the dashboard sees a seamless visual transition with matching colors, blur effects, gradient text, and smooth animations.

**Acceptance Scenarios**:

1. **Given** a user viewing the dashboard, **When** the page loads, **Then** task cards animate in with staggered timing matching the landing page style
2. **Given** a user viewing task cards, **When** they hover over a card, **Then** subtle glow and scale effects occur matching the glassmorphism design
3. **Given** a user viewing the toolbar, **When** they see search and filter controls, **Then** inputs use the glass effect with backdrop blur matching the hero section
4. **Given** a user viewing a task with a due date, **When** the task is overdue, **Then** red highlighting appears, and when due soon, orange highlighting appears

---

### Edge Cases

- What happens when a user has no tasks? The dashboard displays an empty state with a call-to-action to create the first task, using the glassmorphism style.
- What happens when search returns no results? A "No tasks found" message displays with a suggestion to adjust filters or create new tasks.
- What happens when a due date is in the past? The task card displays "Overdue" in red with enhanced glow effect.
- What happens when a user creates a task with an invalid date? Form validation prevents submission and shows an appropriate error message.
- What happens when the browser doesn't support backdrop-filter? The glassmorphism falls back to solid semi-transparent backgrounds (already implemented in globals.css).
- What happens when a user adds too many tags? Tags wrap to multiple lines and the card expands to accommodate them.
- What happens when recurrence is set on a completed task? This is allowed (task will recur based on backend logic).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow users to create tasks with a due date via a datetime-local input
- **FR-002**: The system MUST allow users to add and remove tags from tasks, with each tag having a name and color
- **FR-003**: The system MUST allow users to select a recurrence pattern (NONE, DAILY, WEEKLY, MONTHLY) when creating or editing a task
- **FR-004**: The system MUST provide a search bar that filters tasks in real-time as the user types (with debouncing)
- **FR-005**: The system MUST provide status filter tabs (All, Pending, Completed) that filter the displayed tasks
- **FR-006**: The system MUST provide a priority dropdown filter (All, High, Medium, Low) that filters the displayed tasks
- **FR-007**: The system MUST provide a sort dropdown with options: Created Date, Due Date, Priority, Title
- **FR-008**: The system MUST provide a sort direction toggle (ascending/descending) that reverses the current sort order
- **FR-009**: The system MUST display due dates on task cards with red highlighting for overdue tasks
- **FR-010**: The system MUST display tags on task cards as colored pills/badges with their assigned colors
- **FR-011**: The system MUST display a recurrence icon on task cards that have a recurrence pattern set
- **FR-012**: The dashboard MUST use the existing ui-store for managing filter and sort state
- **FR-013**: All API interactions MUST use the existing api-client methods (getTasks, searchTasks, etc.)
- **FR-014**: The dashboard MUST use the "Deep Space" glassmorphism aesthetic matching the landing page
- **FR-015**: Task cards MUST animate in with staggered timing on load and when the list changes
- **FR-016**: The dashboard MUST remain fully responsive on mobile and desktop devices

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's todo item with attributes: id, title, description, priority (HIGH/MEDIUM/LOW), tags (array of {name, color}), due_date (ISO datetime), recurrence_pattern (NONE/DAILY/WEEKLY/MONTHLY), completed (boolean), created_at, updated_at
- **Tag**: Represents a category label with name (string) and color (hex string)
- **FilterState**: Represents the current dashboard view filters: status (all/pending/completed), priority (all/HIGH/MEDIUM/LOW), sortBy (created_at/due_date/priority/title), sortOrder (asc/desc), tag (optional string)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with due date, tags, and recurrence in under 30 seconds from clicking the "Add Task" button
- **SC-002**: Search results update within 500ms after the user stops typing (debounced)
- **SC-003**: The dashboard visually matches the landing page's glassmorphism aesthetic (verified by design review)
- **SC-004**: All advanced task attributes (due date, tags, recurrence) are visible at a glance without expanding or clicking on task cards
- **SC-005**: Users can switch between any combination of filters and sort options in under 5 seconds
- **SC-006**: Task list animations complete within 600ms for smooth perceived performance
- **SC-007**: The dashboard toolbar reflows appropriately on mobile (screen width < 640px) with stacked controls
- **SC-008**: Overdue tasks are visually distinguishable from urgent but not overdue tasks (different colors)
- **SC-009**: All form inputs provide validation feedback before submission (inline error messages)
- **SC-010**: Filter state persists across page refreshes (via ui-store persistence)

## Assumptions

1. The backend API already supports creating tasks with due_date, tags, and recurrence_pattern fields (confirmed from backend models and types)
2. The backend API already supports filtering by status and priority, and sorting (confirmed from api-client.ts getTasks method)
3. The backend API already supports search functionality (confirmed from api-client.ts searchTasks method)
4. The ui-store already has filter state management infrastructure (confirmed from ui-store.ts)
5. Design tokens (colors, glassmorphism utilities) are already defined in globals.css
6. Framer Motion is already available in the project for animations
7. The Task type already includes all necessary fields (tags, due_date, recurrence_pattern) confirmed from types/task.ts
8. Users are authenticated before accessing the dashboard (per existing auth flow)

## Out of Scope

The following items are explicitly out of scope for this feature:

1. Backend API changes - all necessary endpoints already exist
2. Authentication flow changes - the existing auth system is used as-is
3. Phase III AI features (voice input, ai_summary, embedding_id fields) - these are pre-provisioned but not implemented
4. Task edit functionality - existing edit flow is preserved but form must support new fields
5. Bulk operations (select multiple tasks, delete all filtered) - not included in this scope
6. Calendar view for tasks - list view only
7. Task sharing or collaboration features - single-user focus
8. Advanced recurrence patterns (complex schedules like "every Monday and Wednesday") - only simple DAILY/WEEKLY/MONTHLY
