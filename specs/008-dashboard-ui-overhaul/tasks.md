# Tasks: Advanced Dashboard UI Overhaul

**Feature Branch**: `008-dashboard-ui-overhaul`
**Input**: Design documents from `/specs/008-dashboard-ui-overhaul/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/components.ts, quickstart.md

**Tests**: Playwright tests exist in the project. Test tasks are NOT included in this implementation - manual testing per quickstart.md is sufficient.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with separate frontend and backend:
- Frontend: `frontend/components/`, `frontend/lib/`, `frontend/app/`
- Backend: No changes required for this feature

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify environment and prepare for implementation

- [X] T001 Verify branch `008-dashboard-ui-overhaul` is checked out and up to date
- [X] T002 Verify frontend dependencies are installed (Framer Motion, TanStack Query, Zustand, shadcn/ui)
- [X] T003 Verify backend is running on http://localhost:8000 with all task endpoints functional
- [X] T004 Verify ui-store at `frontend/lib/stores/ui-store.ts` has FilterState infrastructure
- [X] T005 Verify api-client at `frontend/lib/api-client.ts` has all required methods (getTasks, searchTasks, createTask, updateTask)

**Checkpoint**: Environment verified - ready to begin implementation ✅

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and hooks that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 [P] Create `useDebounce` hook in `frontend/lib/hooks/use-debounce.ts` for 300ms debounced search
- [X] T007 [P] Create `tag-utils.ts` in `frontend/lib/utils/tag-utils.ts` with getRandomColor() function using Deep Space color palette
- [X] T008 [P] Create `useTaskFilters` hook in `frontend/lib/hooks/use-task-filters.ts` that composes FilterState from ui-store with filter/sort logic
- [X] T009 Update task validation schema in `frontend/lib/validations/task.ts` to include due_date, tags, recurrence_pattern with Zod rules

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - Advanced Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks with due dates, colored tags, and recurrence patterns via an enhanced TaskForm.

**Independent Test**: A user can click "Add Task", fill in the due date picker, add multiple colored tags by typing and pressing Enter, select a recurrence pattern, and submit. The task appears in the list with all attributes visible.

### Implementation for User Story 1

- [X] T010 [P] [US1] Create `TagInput` component in `frontend/components/tags/tag-input.tsx` with add/remove functionality and color generation
- [X] T011 [P] [US1] Create `DueDatePicker` component in `frontend/components/tasks/due-date-picker.tsx` with styled datetime-local input and ISO 8601 formatting
- [X] T012 [US1] Update `TaskForm` in `frontend/components/tasks/task-form.tsx` to integrate DueDatePicker, TagInput, and recurrence pattern select dropdown
- [X] T013 [US1] Update `TaskCard` in `frontend/components/tasks/task-card.tsx` to display due date with overdue/due-soon color coding, tags as colored pills, and recurrence icon

**Checkpoint**: At this point, users can create tasks with all advanced attributes and see them displayed properly ✅

---

## Phase 4: User Story 2 - Task Filtering and Search (Priority: P1) 🎯 MVP

**Goal**: Enable users to filter tasks by status and priority, and search through tasks in real-time.

**Independent Test**: A user can type in the search bar and see matching tasks update within 500ms, toggle between All/Pending/Completed tabs, and select a priority filter to see only matching tasks.

### Implementation for User Story 2

- [X] T014 [P] [US2] Create status tab component (within DashboardToolbar) with All/Pending/Completed tabs and active state styling
- [X] T015 [P] [US2] Create priority filter dropdown (within DashboardToolbar) using shadcn Select with All/High/Medium/Low options
- [X] T016 [P] [US2] Create search input (within DashboardToolbar) with glassmorphism styling, debounced via useDebounce hook, and clear button
- [X] T017 [US2] Create `DashboardToolbar` in `frontend/components/dashboard/dashboard-toolbar.tsx` integrating search input, status tabs, and priority dropdown with proper callbacks
- [X] T018 [US2] Wire DashboardToolbar filter/sort state to ui-store in `frontend/components/dashboard/dashboard-content.tsx` for persistence

**Checkpoint**: At this point, users can search and filter tasks with real-time updates and state persistence ✅

---

## Phase 5: User Story 3 - Task Sorting (Priority: P2)

**Goal**: Enable users to sort tasks by created date, due date, priority, or title with ascending/descending toggle.

**Independent Test**: A user can select "Due Date" from the sort dropdown and toggle the direction to see overdue tasks first or future tasks first.

### Implementation for User Story 3

- [X] T019 [P] [US3] Create `SortDropdown` component in `frontend/components/dashboard/sort-dropdown.tsx` with sort criterion options and direction toggle button
- [X] T020 [US3] Integrate SortDropdown into DashboardToolbar in `frontend/components/dashboard/dashboard-toolbar.tsx` with sort change callbacks
- [X] T021 [US3] Implement sort logic in `useTaskFilters` hook at `frontend/lib/hooks/use-task-filters.ts` to apply sorting to filtered task list

**Checkpoint**: At this point, users can sort tasks by any criterion with bidirectional control ✅

---

## Phase 6: User Story 4 - Glassmorphism Visual Redesign (Priority: P2)

**Goal**: Transform the dashboard UI to match the "Deep Space" glassmorphism aesthetic from the landing page with staggered animations and cohesive styling.

**Independent Test**: A user navigating from landing page to dashboard sees seamless visual transition with matching colors, blur effects, gradient text, and smooth staggered card animations.

### Implementation for User Story 4

- [X] T022 [P] [US4] Add staggered list animation variants to `lib/animations.ts` or create task-specific variants (container with staggerChildren: 0.05, item with fade/scale)
- [X] T023 [P] [US4] Update `DashboardContent` in `frontend/components/dashboard/dashboard-content.tsx` to replace basic header with DashboardToolbar integration
- [X] T024 [P] [US4] Apply glassmorphism classes (.glass, .glass-strong) to DashboardToolbar inputs and dropdowns in `frontend/components/dashboard/dashboard-toolbar.tsx`
- [X] T025 [P] [US4] Add hover effects (glow, scale) to TaskCard in `frontend/components/tasks/task-card.tsx` matching glassmorphism design
- [X] T026 [US4] Wrap task list in motion.ul with staggered variants in `frontend/components/dashboard/dashboard-content.tsx` for smooth entry animation
- [X] T027 [US4] Add responsive breakpoint handling to DashboardToolbar for mobile stacking (< 640px) in `frontend/components/dashboard/dashboard-toolbar.tsx`

**Checkpoint**: At this point, dashboard fully matches landing page aesthetic with smooth animations ✅

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, validation, and edge case handling

- [X] T028 [P] Add empty state component in `frontend/components/dashboard/empty-state.tsx` with glassmorphism styling and call-to-action
- [X] T029 [P] Add "no results" state in `frontend/components/dashboard/dashboard-content.tsx` when search returns no matches
- [X] T030 Implement tag color persistence using localStorage in `frontend/lib/utils/tag-utils.ts` so same tag name gets same color across sessions
- [X] T031 Add overdue task highlighting (red glow + "Overdue:" prefix) in `frontend/components/tasks/task-card.tsx`
- [X] T032 Add inline validation error messages to TaskForm in `frontend/components/tasks/task-form.tsx` using react-hook-form error state
- [X] T033 Verify mobile responsiveness of all components at 375px breakpoint
- [X] T034 Run quickstart.md testing checklist to verify all acceptance scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 (MVP priority)
  - US3 and US4 are P2 (enhancement priority)
  - User stories can proceed in parallel after Foundational phase
- **Polish (Phase 7)**: Depends on US1-US4 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can build toolbar before TaskCard shows all fields)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Integrates with DashboardToolbar from US2 but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Visual polish that applies to all components, independently verifiable

### Within Each User Story

- Utility/hook tasks marked [P] can run in parallel
- Component creation before integration
- Core implementation before visual polish

### Parallel Opportunities

**Phase 2 (Foundational)** - All can run in parallel:
```bash
T006: useDebounce hook
T007: tag-utils.ts
T008: useTaskFilters hook
T009: task validation update
```

**Phase 3 (US1)** - T010 and T011 can run in parallel:
```bash
T010: TagInput component
T011: DueDatePicker component
```

**Phase 4 (US2)** - T014, T015, T016 can run in parallel:
```bash
T014: Status tabs
T015: Priority dropdown
T016: Search input
```

**Phase 5 (US3)**:
- T019: SortDropdown component (independent)

**Phase 6 (US4)** - T022, T024, T025 can run in parallel:
```bash
T022: Animation variants
T024: Toolbar glassmorphism
T025: TaskCard hover effects
```

---

## Parallel Example: User Story 1 (MVP)

```bash
# Launch all parallel tasks for User Story 1:
Task: "Create TagInput component in frontend/components/tags/tag-input.tsx"
Task: "Create DueDatePicker component in frontend/components/tasks/due-date-picker.tsx"

# After those complete, sequential integration:
Task: "Update TaskForm to integrate DueDatePicker, TagInput, recurrence select"
Task: "Update TaskCard to display new attributes"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Advanced Task Creation)
4. Complete Phase 4: User Story 2 (Filtering and Search)
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready (users can create rich tasks and find them easily)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 + US2 → Test independently → Deploy/Demo (MVP!)
3. Add US3 → Test independently → Deploy/Demo (Sorting)
4. Add US4 → Test independently → Deploy/Demo (Full visual polish)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (TaskForm + TaskCard enhancements)
   - Developer B: User Story 2 (DashboardToolbar + filters)
3. After US1 + US2 complete:
   - Developer A: User Story 3 (SortDropdown)
   - Developer B: User Story 4 (Visual polish + animations)
4. Merge and integrate, final polish

---

## Task Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 1: Setup | 5 tasks (T001-T005) | Environment verification |
| Phase 2: Foundational | 4 tasks (T006-T009) | Shared hooks and utilities |
| Phase 3: US1 - Task Creation | 4 tasks (T010-T013) | Form fields and display |
| Phase 4: US2 - Filtering | 5 tasks (T014-T018) | Toolbar and filters |
| Phase 5: US3 - Sorting | 3 tasks (T019-T021) | Sort controls |
| Phase 6: US4 - Visuals | 6 tasks (T022-T027) | Glassmorphism and animations |
| Phase 7: Polish | 7 tasks (T028-T034) | Edge cases and validation |
| **Total** | **34 tasks** | Full feature implementation |

**Parallelizable Tasks**: 15 tasks marked [P] can run in parallel within their phases

---

## Notes

- [P] tasks = different files, no dependencies within the same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No backend changes required - all endpoints already exist
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow quickstart.md testing checklist for verification
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
