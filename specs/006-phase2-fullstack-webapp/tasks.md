# Tasks: Phase II Full-Stack Todo Web Application

**Input**: Design documents from `/specs/006-phase2-fullstack-webapp/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/openapi.yaml ✓, quickstart.md ✓

**Tests**: Not explicitly requested in spec - tests are EXCLUDED per task generation rules.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in all descriptions

## Path Conventions

- **Backend**: `backend/app/` for FastAPI source
- **Frontend**: `frontend/app/`, `frontend/components/`, `frontend/lib/`
- Per plan.md monorepo structure

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create monorepo structure, initialize both frontend and backend projects

- [X] T001 Create monorepo directory structure with `frontend/` and `backend/` directories
- [X] T002 [P] Initialize backend Python project with `backend/pyproject.toml` and `backend/requirements.txt`
- [X] T003 [P] Initialize frontend Next.js 16+ project in `frontend/` with TypeScript and Tailwind
- [X] T004 [P] Create backend environment template `backend/.env.example` with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS
- [X] T005 [P] Create frontend environment template `frontend/.env.example` with DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL
- [X] T006 [P] Create `backend/CLAUDE.md` with backend-specific guidelines (FastAPI, SQLModel patterns)
- [X] T007 [P] Create `frontend/CLAUDE.md` with frontend-specific guidelines (Next.js App Router, shadcn/ui patterns)
- [X] T008 Install and configure shadcn/ui in frontend with required components (button, card, checkbox, dialog, alert-dialog, form, input, label, textarea, dropdown-menu, sonner, skeleton)

**Checkpoint**: Monorepo structure ready - can install dependencies and run dev servers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can begin

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [X] T009 Create database connection module in `backend/app/db.py` with SQLModel engine, session dependency, and create_db_and_tables function
- [X] T010 Create Task SQLModel models in `backend/app/models.py` (TaskBase, TaskCreate, TaskUpdate, Task, TaskPublic, TaskList)
- [X] T011 Create JWT verification middleware in `backend/app/auth.py` with verify_jwt and get_current_user_id functions using PyJWT
- [X] T012 Create FastAPI app entry point in `backend/app/main.py` with lifespan handler, CORS middleware, and health endpoint
- [X] T013 [P] Create `backend/app/routes/__init__.py` for route module initialization
- [X] T014 Create task routes scaffold in `backend/app/routes/tasks.py` with APIRouter registration

### Frontend Foundation

- [X] T015 Create cn() utility helper in `frontend/lib/utils.ts` for Tailwind class merging
- [X] T016 Create Better Auth server configuration in `frontend/lib/auth.ts` with Neon pool, email/password, and JWT plugin
- [X] T017 Create Better Auth client helpers in `frontend/lib/auth-client.ts` for client-side auth operations
- [X] T018 Create TypeScript task types in `frontend/types/task.ts` (Task, TaskCreate, TaskUpdate, TaskList interfaces)
- [X] T019 Create Zod validation schemas in `frontend/lib/validations/task.ts` (taskCreateSchema, taskUpdateSchema)
- [X] T020 Create API client in `frontend/lib/api.ts` with base fetch wrapper and auth header injection
- [X] T021 Create root layout in `frontend/app/layout.tsx` with html/body structure and metadata
- [X] T022 Create client-side providers in `frontend/app/providers.tsx` with Toaster from sonner
- [X] T023 Create Better Auth API route handler in `frontend/app/api/auth/[...all]/route.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Registration (Priority: P1) 🎯 MVP

**Goal**: Allow new visitors to create an account and be redirected to their empty dashboard

**Independent Test**: Visit `/signup`, enter valid email/password, verify account creation redirects to dashboard

### Implementation for User Story 1

- [X] T024 [P] [US1] Create signup page route in `frontend/app/(auth)/signup/page.tsx` with form container
- [X] T025 [P] [US1] Create signup form component in `frontend/components/auth/signup-form.tsx` with email, password, confirm password fields
- [X] T026 [US1] Implement signup form validation with Zod schema in `frontend/lib/validations/auth.ts`
- [X] T027 [US1] Connect signup form to Better Auth signUp action with error handling
- [X] T028 [US1] Add signup success redirect to `/dashboard` with toast notification
- [X] T029 [US1] Add email already exists error handling with user-friendly message

**Checkpoint**: New users can register accounts - User Story 1 complete

---

## Phase 4: User Story 2 - User Authentication (Priority: P1) 🎯 MVP

**Goal**: Allow registered users to login, access protected routes, and logout securely

**Independent Test**: Login with valid credentials, verify dashboard access, logout and verify session ends

### Implementation for User Story 2

- [X] T030 [P] [US2] Create login page route in `frontend/app/(auth)/login/page.tsx` with form container
- [X] T031 [P] [US2] Create login form component in `frontend/components/auth/login-form.tsx` with email, password fields
- [X] T032 [US2] Implement login form validation with Zod schema (extend `frontend/lib/validations/auth.ts`)
- [X] T033 [US2] Connect login form to Better Auth signIn action with error handling
- [X] T034 [US2] Add login success redirect to `/dashboard`
- [X] T035 [US2] Add invalid credentials error handling with generic "Invalid email or password" message
- [X] T036 [US2] Create auth layout in `frontend/app/(auth)/layout.tsx` for consistent auth page styling
- [X] T037 [US2] Create header component in `frontend/components/layout/header.tsx` with logo and conditional user nav
- [X] T038 [US2] Create user-nav component in `frontend/components/layout/user-nav.tsx` with avatar and logout button
- [X] T039 [US2] Implement logout functionality in user-nav using Better Auth signOut
- [X] T040 [US2] Create middleware for route protection in `frontend/middleware.ts` (redirect unauthenticated to login)
- [X] T041 [US2] Create landing page in `frontend/app/page.tsx` that redirects authenticated users to dashboard, others to login

**Checkpoint**: Users can login/logout and protected routes work - User Story 2 complete

---

## Phase 5: User Story 3 - Create New Task (Priority: P1) 🎯 MVP

**Goal**: Allow authenticated users to add new tasks with title and optional description

**Independent Test**: Click "Add Task", enter title, verify new task appears in list immediately

### Backend Implementation for User Story 3

- [X] T042 [US3] Implement POST `/api/{user_id}/tasks` endpoint in `backend/app/routes/tasks.py` with JWT validation and user_id match check
- [X] T043 [US3] Add request body validation for TaskCreate in POST endpoint
- [X] T044 [US3] Add database insert logic with user_id assignment and return TaskPublic

### Frontend Implementation for User Story 3

- [X] T045 [P] [US3] Create task form dialog component in `frontend/components/tasks/task-form.tsx` with title, description fields
- [X] T046 [US3] Create server action for task creation in `frontend/app/actions/tasks.ts` with JWT header and revalidatePath
- [X] T047 [US3] Connect task form to createTask server action with optimistic UI update
- [X] T048 [US3] Add form validation with taskCreateSchema before submission
- [X] T049 [US3] Add success toast "Task created" on successful creation
- [X] T050 [US3] Add error handling with user-friendly error toast

**Checkpoint**: Users can create tasks - User Story 3 complete

---

## Phase 6: User Story 4 - View Task List (Priority: P1) 🎯 MVP

**Goal**: Display all user's tasks with status indicators and empty state

**Independent Test**: Login and verify all tasks displayed with correct status, verify empty state for new users

### Backend Implementation for User Story 4

- [X] T051 [US4] Implement GET `/api/{user_id}/tasks` endpoint in `backend/app/routes/tasks.py` with user filtering and JWT validation
- [X] T052 [US4] Add ordering by created_at descending in list endpoint
- [X] T053 [US4] Return TaskList response with tasks array and total count

### Frontend Implementation for User Story 4

- [X] T054 [US4] Create dashboard page in `frontend/app/dashboard/page.tsx` as Server Component fetching tasks
- [X] T055 [US4] Create task-list component in `frontend/components/tasks/task-list.tsx` to render task cards
- [X] T056 [P] [US4] Create task-card component in `frontend/components/tasks/task-card.tsx` with title, description, checkbox, actions
- [X] T057 [P] [US4] Create empty-state component in `frontend/components/tasks/empty-state.tsx` with friendly message and add task CTA
- [X] T058 [US4] Create loading skeleton in `frontend/app/dashboard/loading.tsx` for dashboard loading state
- [X] T059 [US4] Add API client method getTasks in `frontend/lib/api.ts`
- [X] T060 [US4] Integrate task-list with Add Task button in dashboard page

**Checkpoint**: Users can view all their tasks - User Story 4 complete

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P1) 🎯 MVP

**Goal**: Allow users to toggle task completion with immediate visual feedback

**Independent Test**: Click task checkbox, verify visual change, refresh and verify persistence

### Backend Implementation for User Story 5

- [X] T061 [US5] Implement PATCH `/api/{user_id}/tasks/{task_id}/complete` endpoint in `backend/app/routes/tasks.py`
- [X] T062 [US5] Add toggle logic (completed = not completed) with updated_at timestamp
- [X] T063 [US5] Add ownership validation (user_id match) before toggle

### Frontend Implementation for User Story 5

- [X] T064 [US5] Create server action toggleTaskComplete in `frontend/app/actions/tasks.ts`
- [X] T065 [US5] Add checkbox click handler in task-card component calling toggleTaskComplete
- [X] T066 [US5] Add visual styling for completed tasks (strike-through, muted colors) in task-card
- [X] T067 [US5] Add optimistic update for checkbox toggle with rollback on error
- [X] T068 [US5] Add subtle success feedback (animation or toast) on completion toggle

**Checkpoint**: Users can mark tasks complete/incomplete - User Story 5 complete

---

## Phase 8: User Story 6 - Update Task Details (Priority: P2)

**Goal**: Allow users to edit task title and description with save/cancel options

**Independent Test**: Click edit, modify text, save, verify changes persist after refresh

### Backend Implementation for User Story 6

- [X] T069 [US6] Implement PUT `/api/{user_id}/tasks/{task_id}` endpoint in `backend/app/routes/tasks.py`
- [X] T070 [US6] Add request body validation for TaskUpdate (partial update support)
- [X] T071 [US6] Add ownership validation and 404 handling for non-existent tasks
- [X] T072 [US6] Update only provided fields with updated_at timestamp

### Frontend Implementation for User Story 6

- [X] T073 [US6] Create task-actions dropdown component in `frontend/components/tasks/task-actions.tsx` with Edit, Delete options
- [X] T074 [US6] Add edit dialog/modal state management in task-card or task-form component
- [X] T075 [US6] Create server action updateTask in `frontend/app/actions/tasks.ts`
- [X] T076 [US6] Pre-populate edit form with existing task data
- [X] T077 [US6] Add cancel button that discards changes without saving
- [X] T078 [US6] Add success toast "Task updated" on successful update
- [X] T079 [US6] Add validation feedback for edit form (same rules as create)

**Checkpoint**: Users can edit task details - User Story 6 complete

---

## Phase 9: User Story 7 - Delete Task (Priority: P2)

**Goal**: Allow users to permanently remove tasks with confirmation

**Independent Test**: Click delete, confirm, verify task removed from list

### Backend Implementation for User Story 7

- [X] T080 [US7] Implement DELETE `/api/{user_id}/tasks/{task_id}` endpoint in `backend/app/routes/tasks.py`
- [X] T081 [US7] Add ownership validation before delete
- [X] T082 [US7] Return success response with ok: true, message: "Task deleted"

### Frontend Implementation for User Story 7

- [X] T083 [US7] Add delete option to task-actions dropdown in `frontend/components/tasks/task-actions.tsx`
- [X] T084 [US7] Create delete confirmation dialog using alert-dialog component
- [X] T085 [US7] Create server action deleteTask in `frontend/app/actions/tasks.ts`
- [X] T086 [US7] Connect delete confirmation to deleteTask action
- [X] T087 [US7] Add success toast "Task deleted" on successful deletion
- [X] T088 [US7] Add cancel button in confirmation that closes dialog without action

**Checkpoint**: Users can delete tasks - User Story 7 complete

---

## Phase 10: User Story 8 - Responsive Mobile Experience (Priority: P2)

**Goal**: Ensure all UI components work well on mobile, tablet, and desktop viewports

**Independent Test**: Access app on mobile viewport, verify all features accessible and usable

### Implementation for User Story 8

- [X] T089 [P] [US8] Add responsive styles to auth pages (login/signup) in their respective components
- [X] T090 [P] [US8] Add responsive styles to dashboard layout (header, task list)
- [X] T091 [P] [US8] Ensure task-card component adapts to mobile width with proper spacing
- [X] T092 [P] [US8] Ensure task-form dialog is mobile-friendly with full-width on small screens
- [X] T093 [US8] Verify touch targets are at least 44x44 pixels for buttons and checkboxes
- [X] T094 [US8] Add viewport meta tag in root layout if not present
- [X] T095 [US8] Test and adjust header/user-nav for mobile (hamburger menu if needed)

**Checkpoint**: App is fully responsive across devices - User Story 8 complete

---

## Phase 11: User Story 9 - Data Isolation Between Users (Priority: P3)

**Goal**: Ensure complete privacy - users only see their own tasks

**Independent Test**: Create tasks as User A, login as User B, verify User A's tasks not visible

### Backend Implementation for User Story 9

- [X] T096 [US9] Verify all task endpoints filter by user_id from JWT in `backend/app/routes/tasks.py`
- [X] T097 [US9] Implement GET `/api/{user_id}/tasks/{task_id}` endpoint with ownership check
- [X] T098 [US9] Add 403 Forbidden response when URL user_id doesn't match JWT user_id
- [X] T099 [US9] Add 404 Not Found response when task doesn't exist or doesn't belong to user
- [X] T100 [US9] Review all endpoints for consistent authorization checks

**Checkpoint**: Data isolation enforced - User Story 9 complete

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [X] T101 [P] Add API client method getTask (single task) in `frontend/lib/api.ts` for future use
- [X] T102 [P] Add error boundary component for graceful error handling in `frontend/components/error-boundary.tsx`
- [X] T103 [P] Add session expiry handling - redirect to login with friendly message
- [X] T104 [P] Add network error handling with retry option in API client
- [X] T105 Update `README.md` with setup instructions for both frontend and backend
- [X] T106 Create `.gitignore` entries for .env files, node_modules, __pycache__, .venv
- [X] T107 Run final validation per quickstart.md - verify both services start and communicate
- [X] T108 Verify all acceptance criteria from spec.md are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-11 (User Stories)**: All depend on Phase 2 completion
- **Phase 12 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Priority | Can Start After | Dependencies on Other Stories |
|-------|----------|-----------------|------------------------------|
| US1 (Registration) | P1 | Phase 2 | None |
| US2 (Login/Logout) | P1 | Phase 2 | None (but logically after US1) |
| US3 (Create Task) | P1 | Phase 2 | US2 (needs auth) |
| US4 (View Tasks) | P1 | Phase 2 | US2 (needs auth) |
| US5 (Toggle Complete) | P1 | Phase 2 | US3, US4 (needs tasks to exist) |
| US6 (Update Task) | P2 | Phase 2 | US3, US4 (needs tasks to exist) |
| US7 (Delete Task) | P2 | Phase 2 | US3, US4 (needs tasks to exist) |
| US8 (Responsive) | P2 | Any time | Can be done in parallel with any story |
| US9 (Data Isolation) | P3 | Phase 2 | US3, US4 (needs tasks to test) |

### MVP Path (Recommended)

1. Phase 1: Setup ✓
2. Phase 2: Foundational ✓
3. Phase 3: US1 (Registration) → Test independently
4. Phase 4: US2 (Login/Logout) → Test independently
5. Phase 5: US3 (Create Task) → Test independently
6. Phase 6: US4 (View Tasks) → Test independently
7. Phase 7: US5 (Toggle Complete) → Test independently
8. **MVP COMPLETE** - Can demo core functionality

### Parallel Opportunities

**Within Phase 1 (Setup):**
```bash
# These can all run in parallel:
T002: Initialize backend Python project
T003: Initialize frontend Next.js project
T004: Create backend .env.example
T005: Create frontend .env.example
T006: Create backend CLAUDE.md
T007: Create frontend CLAUDE.md
```

**Within Phase 2 (Foundational):**
```bash
# Backend foundation can run in parallel with frontend foundation
# Within backend: T009 → T010 → T011 → T012 → T013, T014
# Within frontend: T015-T023 mostly parallel
```

**User Stories (US3-US7):**
```bash
# Backend and frontend for same story can partially parallelize
# Example for US3:
# 1. Backend: T042-T044 (API implementation)
# 2. Frontend: T045 (form component) can start in parallel
# 3. Frontend: T046-T050 (server action, integration) after backend ready
```

**Responsive (US8):**
```bash
# All T089-T094 can run in parallel as they affect different components
T089: Auth pages responsive
T090: Dashboard responsive
T091: Task-card responsive
T092: Task-form responsive
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (~15 min)
2. Complete Phase 2: Foundational (~45 min)
3. Complete US1-US5 in order (~2-3 hours)
4. **STOP and VALIDATE**: Full CRUD + Auth working
5. Deploy to Vercel + Railway
6. Submit for Phase II checkpoint

### Full Implementation

1. MVP path above
2. Add US6 (Update Task) - ~30 min
3. Add US7 (Delete Task) - ~30 min
4. Add US8 (Responsive) - ~30 min
5. Add US9 (Data Isolation verification) - ~15 min
6. Complete Phase 12 (Polish) - ~30 min

### Total Estimated Tasks: 108

| Phase | Task Count | Parallel Opportunities |
|-------|------------|----------------------|
| Phase 1 (Setup) | 8 | 6 tasks parallel |
| Phase 2 (Foundational) | 15 | ~8 tasks parallel |
| Phase 3 (US1) | 6 | 2 tasks parallel |
| Phase 4 (US2) | 12 | 2 tasks parallel |
| Phase 5 (US3) | 9 | 2 tasks parallel |
| Phase 6 (US4) | 10 | 3 tasks parallel |
| Phase 7 (US5) | 8 | 0 tasks parallel |
| Phase 8 (US6) | 11 | 0 tasks parallel |
| Phase 9 (US7) | 9 | 0 tasks parallel |
| Phase 10 (US8) | 7 | 5 tasks parallel |
| Phase 11 (US9) | 5 | 0 tasks parallel |
| Phase 12 (Polish) | 8 | 4 tasks parallel |

---

## Notes

- [P] tasks = different files, no dependencies on other tasks in same phase
- [US#] label maps task to specific user story from spec.md
- Each user story checkpoint enables independent testing
- Commit after each task or logical group
- Backend and frontend for same story can have some parallel work
- All endpoints require JWT - verify auth works before testing API
- Use same BETTER_AUTH_SECRET in both .env files!
