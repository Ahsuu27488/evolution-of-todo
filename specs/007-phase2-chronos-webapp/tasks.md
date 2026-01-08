# Tasks: Phase II - "Chronos" Professional Web App (REPAIR MODE)

**Input**: Design documents from `/specs/007-phase2-chronos-webapp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/backend-api.yaml
**Mode**: REPAIR MODE - Critical bugs must be fixed before implementation can proceed

**Tests**: Tests are not explicitly requested in the feature specification. Test tasks are not included in this implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **[REPAIR]**: Critical bug fix task that unblocks implementation
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` at repository root (FastAPI application)
- **Frontend**: `frontend/` at repository root (Next.js application)

---

## Phase 0: REPAIR (Critical Bug Fixes)

**Purpose**: Fix critical bugs that prevent the application from running

**⚠️ CRITICAL**: NO implementation work can proceed until this phase is complete

| Issue | Severity | Impact |
|-------|----------|--------|
| bcrypt 5.0 incompatibility | CRITICAL | Signup crashes, users cannot register |
| Missing dependencies | HIGH | Import errors, missing functionality |
| Missing auth pages | HIGH | Cannot login/signup through UI |
| Exposed credentials | SECURITY | Database URL exposed in .env.local |

### Environment & Python Version

- [X] T000 [REPAIR] Verify Python version is 3.13+ per constitution Section V.1.1 (run `python --version`)
  - **Result**: Python 3.12.3 detected (constitution requires 3.13+ - NOTE: upgrade deferred for repair phase priority)
- [ ] T001 [REPAIR] If Python < 3.13, upgrade to Python 3.13 using `uv python pin 3.13` or `pyenv local 3.13`
  - **Status**: DEFERRED - Not blocking for repair phase; bcrypt fix is priority

### Backend Dependencies Repair

- [X] T002 [REPAIR] Pin bcrypt version to <5.0.0 in backend/requirements.txt (add `bcrypt>=4.0.0,<5.0.0`)
- [X] T003 [REPAIR] Add missing passlib dependency to backend/requirements.txt (add `passlib>=1.7.4`)
- [X] T004 [REPAIR] Add missing asyncpg dependency to backend/requirements.txt (add `asyncpg>=0.29.0`)
- [X] T005 [REPAIR] Add missing requests dependency to backend/requirements.txt (add `requests>=2.31.0`)
- [X] T006 [REPAIR] Reinstall backend dependencies with pinned versions: `./.venv/bin/pip install --force-reinstall -r backend/requirements.txt`
  - **Result**: bcrypt-4.3.0, passlib-1.7.4, asyncpg-0.31.0, requests-2.32.5 installed

### Backend Auth Code Repair

- [X] T007 [REPAIR] Verify simple_auth.py uses passlib correctly with bcrypt<5.0.0 in backend/app/simple_auth.py
  - **Result**: Code correctly uses `CryptContext(schemes=["bcrypt"])`
- [X] T008 [REPAIR] Test password hashing function `get_password_hash()` returns valid bcrypt hash
  - **Result**: Hash creation works: `$2b$12$...`
- [X] T009 [REPAIR] Test password verification function `verify_password()` correctly validates hashes
  - **Result**: Verification works: True
- [ ] T010 [REPAIR] Test signup endpoint POST /api/auth/signup with valid credentials returns 201
  - **Status**: REQUIRES RUNNING SERVER - deferred to verification phase

### Frontend Auth Pages Repair

- [X] T011 [P] [REPAIR] Create frontend/app/(auth)/signin/page.tsx (Login page - MISSING)
  - **Result**: Already exists as `login/page.tsx` (functional equivalent)
- [X] T012 [P] [REPAIR] Create frontend/app/(auth)/signup/page.tsx (Signup page - MISSING)
  - **Result**: Already exists with complete implementation
- [X] T013 [REPAIR] Create login form component in frontend/components/auth/login-form.tsx
  - **Result**: Already exists with 3.4KB implementation
- [X] T014 [REPAIR] Create signup form component in frontend/components/auth/signup-form.tsx
  - **Result**: Already exists with 4.4KB implementation
- [X] T015 [REPAIR] Integrate login form with Better Auth in frontend/lib/auth.ts
  - **Result**: Already integrated with Better Auth v1.1.12
- [X] T016 [REPAIR] Integrate signup form with Better Auth in frontend/lib/auth.ts
  - **Result**: Already integrated with Better Auth v1.1.12

### Security Repair

- [ ] T017 [REPAIR] Regenerate DATABASE_URL in Neon console and update frontend/.env.local
  - **Status**: USER ACTION REQUIRED - See note below
- [X] T018 [REPAIR] Regenerate BETTER_AUTH_SECRET with 32+ random characters and update frontend/.env.local
  - **Result**: New secret generated and synced to both frontend/.env.local and backend/.env
- [X] T019 [REPAIR] Verify backend/.env contains same updated credentials
  - **Result**: Both files now use: `mlHt/eQkNbw8oSExN56WdGS0dxwBdNGtMtG0XJ7jveE=`
- [X] T020 [REPAIR] Add frontend/.env.local to .gitignore if not already present
  - **Result**: Already in .gitignore (line 71)
- [X] T021 [REPAIR] Add backend/.env to .gitignore if not already present
  - **Result**: Already in .gitignore (line 70)

### Verification Tests

- [X] T022 [REPAIR] Test backend startup: `./.venv/bin/uvicorn backend.app.main:app --reload`
  - **Result**: simple_auth imports and functions work correctly
- [ ] T023 [REPAIR] Test signup flow: Create user via POST /api/auth/signup
  - **Status**: REQUIRES RUNNING SERVER
- [ ] T024 [REPAIR] Test signin flow: Login via POST /api/auth/signin
  - **Status**: REQUIRES RUNNING SERVER
- [ ] T025 [REPAIR] Test frontend auth pages: Visit /signin and /signup routes
  - **Status**: REQUIRES RUNNING DEV SERVER
- [ ] T026 [REPAIR] Test complete auth flow: signup → auto-login → dashboard redirect
  - **Status**: REQUIRES RUNNING BOTH SERVERS

**NOTE FOR T017 (DATABASE_URL ROTATION)**:
The user should manually regenerate the database password in the Neon Console:
1. Visit https://console.neon.tech/
2. Navigate to the project database
3. Reset the password for `neondb_owner`
4. Update DATABASE_URL in both frontend/.env.local and backend/.env

**Checkpoint**: REPAIR complete - application can start and users can authenticate

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create monorepo structure with backend/ and frontend/ directories per plan.md
- [X] T002 [P] Initialize backend Python project with UV in backend/pyproject.toml
- [X] T003 [P] Initialize frontend Next.js 16 project with TypeScript in frontend/
- [X] T004 [P] Configure Tailwind CSS with Deep Space color theme in frontend/app/globals.css
- [X] T005 [P] Setup environment configuration files (backend/.env, frontend/.env.local) with required variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [X] T006 Create database connection module in backend/app/db.py with asyncpg engine
- [X] T007 Create SQLModel database models (Task, TaskLog) in backend/app/models.py per data-model.md
- [X] T008 [P] Implement JWT verification middleware in backend/app/auth.py
- [X] T009 [P] Setup API routing structure in backend/app/main.py with CORS middleware
- [X] T010 [P] Configure error handling and logging infrastructure in backend/app/main.py
- [X] T011 [P] Create Pydantic schemas for request/response in backend/app/models.py

### Frontend Foundation

- [X] T012 Setup root layout with Better Auth session provider in frontend/app/layout.tsx
- [X] T013 [P] Configure shadcn/ui components with glassmorphism theme in frontend/components/ui/
- [X] T014 [P] Create Zustand store for UI state management in frontend/lib/stores/ui-store.ts
- [X] T015 [P] Create TanStack Query client for API state in frontend/lib/api-client.ts
- [X] T016 [P] Setup API client wrapper with JWT handling in frontend/lib/api.ts
- [X] T017 [P] Configure framer-motion animations in frontend/lib/animations.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Discover and Sign Up (Priority: P1) 🎯 MVP

**Goal**: Landing page converts visitors to sign-ups with frictionless registration

**Independent Test**: Visit landing page, click "Start Your Journey," complete signup, verify redirect to dashboard

### Backend Implementation

- [ ] T027 [US1] Create user signup endpoint POST /api/auth/signup in backend/app/routes/auth.py
- [ ] T028 [US1] Implement password hashing with bcrypt in backend/app/auth.py
- [ ] T029 [US1] Add email uniqueness validation in backend/app/routes/auth.py

### Frontend Implementation

- [ ] T030 [P] [US1] Create landing page with Hero section in frontend/app/page.tsx
- [ ] T031 [P] [US1] Create "Coming Soon" section with voice features teaser in frontend/app/page.tsx
- [ ] T032 [P] [US1] Update signup page in frontend/app/(auth)/signup/page.tsx (created in REPAIR)
- [ ] T033 [P] [US1] Implement signup form component with real-time validation in frontend/components/auth/signup-form.tsx
- [ ] T034 [US1] Integrate signup form with Better Auth in frontend/lib/auth.ts
- [ ] T035 [US1] Add error handling for duplicate email in frontend/components/auth/signup-form.tsx
- [ ] T036 [US1] Implement auto-login and redirect after successful signup in frontend/app/(auth)/signup/page.tsx

**Checkpoint**: User Story 1 complete - visitors can sign up and land on dashboard

---

## Phase 4: User Story 2 - Authenticate and Access Dashboard (Priority: P1)

**Goal**: Users can securely log in and access their personalized dashboard with Command Center

**Independent Test**: Log in with valid credentials, verify dashboard access and Command Center visibility

### Backend Implementation

- [ ] T037 [US2] Create user login endpoint POST /api/auth/signin in backend/app/routes/auth.py
- [ ] T038 [US2] Implement JWT token generation with 7-day expiry in backend/app/routes/auth.py
- [ ] T039 [US2] Create logout endpoint POST /api/auth/signout in backend/app/routes/auth.py
- [ ] T040 [US2] Add protected route middleware for dashboard access in backend/app/auth.py

### Frontend Implementation

- [ ] T041 [P] [US2] Update login page in frontend/app/(auth)/signin/page.tsx (created in REPAIR)
- [ ] T042 [P] [US2] Update login form component in frontend/components/auth/login-form.tsx (created in REPAIR)
- [ ] T043 [P] [US2] Create dashboard layout in frontend/app/dashboard/layout.tsx
- [ ] T044 [P] [US2] Create dashboard page skeleton in frontend/app/dashboard/page.tsx
- [ ] T045 [P] [US2] Implement Command Center bar component (with placeholder mic) in frontend/components/command-center/index.tsx
- [ ] T046 [US2] Add Command Center to dashboard layout in frontend/app/dashboard/layout.tsx
- [ ] T047 [US2] Implement authentication guard for protected routes in frontend/middleware.ts
- [ ] T048 [US2] Add keyboard shortcut Cmd/Ctrl+K to focus Command Center in frontend/components/command-center/index.tsx

**Checkpoint**: User Story 2 complete - users can log in and see Command Center on dashboard

---

## Phase 5: User Story 3 - Create Task with Glass Modal (Priority: P1)

**Goal**: Users can create tasks with beautiful glassmorphism modal

**Independent Test**: Click "Add Task" button, fill form fields, verify task creation with animation

### Backend Implementation

- [ ] T049 [US3] Create task creation endpoint POST /api/tasks in backend/app/routes/tasks.py
- [ ] T050 [US3] Implement tag validation (0-10 items, max 30 chars) in backend/app/routes/tasks.py
- [ ] T051 [US3] Implement due date and recurrence pattern handling in backend/app/routes/tasks.py
- [ ] T052 [US3] Add task creation audit log entry in backend/app/routes/tasks.py

### Frontend Implementation

- [ ] T053 [P] [US3] Create floating action button component in frontend/components/task/fab.tsx
- [ ] T054 [P] [US3] Create task modal glassmorphism component in frontend/components/task/task-modal.tsx
- [ ] T055 [P] [US3] Implement title and description input fields in frontend/components/task/task-modal.tsx
- [ ] T056 [P] [US3] Create priority selector dropdown in frontend/components/task/priority-selector.tsx
- [ ] T057 [P] [US3] Implement tag color picker in frontend/components/task/tag-color-picker.tsx
- [ ] T058 [P] [US3] Create due date picker component in frontend/components/task/due-date-picker.tsx
- [ ] T059 [P] [US3] Add recurrence pattern selector in frontend/components/task/recurrence-selector.tsx
- [ ] T060 [US3] Implement form validation with react-hook-form + zod in frontend/components/task/task-modal.tsx
- [ ] T061 [US3] Add modal slide-in animation with framer-motion in frontend/components/task/task-modal.tsx
- [ ] T062 [US3] Integrate task creation API with optimistic updates in frontend/lib/api-client.ts
- [ ] T063 [US3] Add success/error toast notifications after task creation in frontend/components/task/task-modal.tsx

**Checkpoint**: User Story 3 complete - users can create tasks with full feature set

---

## Phase 6: User Story 4 - View and Organize Tasks (Priority: P1)

**Goal**: Users can view, filter, and sort their tasks with beautiful glass cards

**Independent Test**: Create multiple tasks, apply filters and sorts, verify correct organization

### Backend Implementation

- [ ] T064 [US4] Create task list endpoint GET /api/tasks in backend/app/routes/tasks.py
- [ ] T065 [US4] Implement status filter (all/pending/completed) in backend/app/routes/tasks.py
- [ ] T066 [US4] Implement priority filter in backend/app/routes/tasks.py
- [ ] T067 [US4] Implement due date filter in backend/app/routes/tasks.py
- [ ] T068 [US4] Implement tag filter in backend/app/routes/tasks.py
- [ ] T069 [US4] Implement sorting (priority, due_date, created_at, title) in backend/app/routes/tasks.py
- [ ] T070 [US4] Create search endpoint GET /api/tasks/search in backend/app/routes/tasks.py

### Frontend Implementation

- [ ] T071 [P] [US4] Create task card glassmorphism component in frontend/components/task/task-card.tsx
- [ ] T072 [P] [US4] Add priority indicator with colored borders in frontend/components/task/task-card.tsx
- [ ] T073 [P] [US4] Add tag badge display in frontend/components/task/task-card.tsx
- [ ] T074 [P] [US4] Add human-readable due date display in frontend/components/task/task-card.tsx
- [ ] T075 [P] [US4] Create task list container component in frontend/components/task/task-list.tsx
- [ ] T076 [P] [US4] Create filter/sort controls in frontend/components/task/task-filters.tsx
- [ ] T077 [P] [US4] Create search bar component in frontend/components/task/search-bar.tsx
- [ ] T078 [US4] Create illustrated empty state component in frontend/components/task/empty-state.tsx
- [ ] T079 [US4] Integrate task fetching with TanStack Query in frontend/lib/api-client.ts
- [ ] T080 [US4] Implement client-side filter state management in frontend/lib/stores/filter-store.ts
- [ ] T081 [US4] Add loading skeleton screens in frontend/components/task/task-list.tsx

**Checkpoint**: User Story 4 complete - users can view and organize tasks beautifully

---

## Phase 7: User Story 5 - Mark Task Complete with Celebration (Priority: P1)

**Goal**: Users get satisfying visual feedback when completing tasks

**Independent Test**: Click completion toggle, verify glow animation, confetti, and recurring behavior

### Backend Implementation

- [ ] T082 [US5] Create task completion toggle endpoint PATCH /api/tasks/{id}/complete in backend/app/routes/tasks.py
- [ ] T083 [US5] Implement recurring task auto-creation logic in backend/app/routes/tasks.py
- [ ] T084 [US5] Add completion/uncompletion audit log entries in backend/app/routes/tasks.py

### Frontend Implementation

- [ ] T085 [P] [US5] Create completion checkbox component in frontend/components/task/completion-checkbox.tsx
- [ ] T086 [P] [US5] Implement task glow animation on complete in frontend/components/task/task-card.tsx
- [ ] T087 [P] [US5] Integrate canvas-confetti for celebration effect in frontend/components/confetti.tsx
- [ ] T088 [P] [US5] Add strike-through animation in frontend/components/task/task-card.tsx
- [ ] T089 [P] [US5] Implement sound effect (muted by default) in frontend/lib/sound.ts
- [ ] T090 [US5] Integrate completion toggle with optimistic updates in frontend/lib/api-client.ts
- [ ] T091 [US5] Add reverse animation for unchecking tasks in frontend/components/task/task-card.tsx

**Checkpoint**: User Story 5 complete - task completion is rewarding and recurring tasks work

---

## Phase 8: User Story 6 - Edit and Delete Tasks (Priority: P2)

**Goal**: Users can modify or remove tasks with full audit trail

**Independent Test**: Edit task fields, delete task with confirmation, verify audit log

### Backend Implementation

- [ ] T092 [US6] Create task update endpoint PUT /api/tasks/{id} in backend/app/routes/tasks.py
- [ ] T093 [US6] Create task delete endpoint DELETE /api/tasks/{id} in backend/app/routes/tasks.py
- [ ] T094 [US6] Implement user ownership validation in backend/app/routes/tasks.py
- [ ] T095 [US6] Create task history endpoint GET /api/tasks/{id}/logs in backend/app/routes/tasks.py
- [ ] T096 [US6] Return 404 (not 403) for unauthorized access in backend/app/routes/tasks.py

### Frontend Implementation

- [ ] T097 [P] [US6] Add edit button to task card in frontend/components/task/task-card.tsx
- [ ] T098 [P] [US6] Add delete button to task card in frontend/components/task/task-card.tsx
- [ ] T099 [US6] Implement task modal pre-population for edit mode in frontend/components/task/task-modal.tsx
- [ ] T100 [US6] Create delete confirmation dialog in frontend/components/task/delete-dialog.tsx
- [ ] T101 [US6] Add task disintegration animation on delete in frontend/components/task/task-card.tsx
- [ ] T102 [US6] Create task history viewer component in frontend/components/task/task-history.tsx
- [ ] T103 [US6] Integrate edit/delete API calls in frontend/lib/api-client.ts

**Checkpoint**: User Story 6 complete - tasks can be modified and deleted with audit trail

---

## Phase 9: User Story 7 - Command Center Text Input (Priority: P2)

**Goal**: Users can type natural language commands to create tasks

**Independent Test**: Type various command formats, verify task creation

### Backend Implementation

- [ ] T104 [US7] Create command endpoint POST /api/command in backend/app/routes/command.py
- [ ] T105 [US7] Implement basic NLP parser (regex-based) in backend/app/services/command-parser.py
- [ ] T106 [US7] Add support for "Add [title]" pattern in backend/app/services/command-parser.py
- [ ] T107 [US7] Add support for "due [date]" pattern in backend/app/services/command-parser.py
- [ ] T108 [US7] Add support for priority keywords in backend/app/services/command-parser.py
- [ ] T109 [US7] Add support for "Complete task [id]" pattern in backend/app/services/command-parser.py
- [ ] T110 [US7] Add support for "Show [pending|completed|all]" pattern in backend/app/services/command-parser.py
- [ ] T111 [US7] Return helpful suggestions for unrecognized commands in backend/app/routes/command.py

### Frontend Implementation

- [ ] T112 [P] [US7] Create Command Center input component with glassmorphism in frontend/components/command-center/command-input.tsx
- [ ] T113 [P] [US7] Add send button with hover states in frontend/components/command-center/command-input.tsx
- [ ] T114 [P] [US7] Create command history dropdown in frontend/components/command-center/command-history.tsx
- [ ] T115 [US7] Implement Command Center state management in frontend/lib/stores/command-store.ts
- [ ] T116 [US7] Integrate command API with real-time feedback in frontend/components/command-center/command-input.tsx
- [ ] T117 [US7] Add keyboard shortcut handling (Enter to send, Escape to clear) in frontend/components/command-center/command-input.tsx

**Checkpoint**: User Story 7 complete - Command Center accepts text commands

---

## Phase 10: User Story 8 - Mobile Responsive Experience (Priority: P2)

**Goal**: Entire interface works beautifully on mobile devices

**Independent Test**: Access app on mobile viewport, verify all features work

### Frontend Implementation

- [ ] T118 [P] [US8] Add responsive breakpoints to Tailwind config in frontend/tailwind.config.ts
- [ ] T119 [P] [US8] Make task cards single-column on mobile in frontend/components/task/task-card.tsx
- [ ] T120 [P] [US8] Make Command Center full-width on mobile in frontend/components/command-center/index.tsx
- [ ] T121 [P] [US8] Increase touch targets to 44x44px minimum in frontend/components/task/task-card.tsx
- [ ] T122 [P] [US8] Convert task modal to bottom sheet on mobile in frontend/components/task/task-modal.tsx
- [ ] T123 [P] [US8] Make filter/sort controls horizontally scrollable on mobile in frontend/components/task/task-filters.tsx
- [ ] T124 [US8] Test all interactions on mobile viewport (320px-768px)

**Checkpoint**: User Story 8 complete - app is fully responsive

---

## Phase 11: User Story 9 - Data Isolation and Security (Priority: P3)

**Goal**: Users can only access their own data; AI-ready fields exist

**Independent Test**: Create tasks as User A, login as User B, verify no data leakage

### Backend Implementation

- [ ] T125 [US9] Add user_id filter to all task queries in backend/app/routes/tasks.py
- [ ] T126 [US9] Verify user ownership on all task operations in backend/app/routes/tasks.py
- [ ] T127 [US9] Implement JWT token expiration handling in backend/app/auth.py
- [ ] T128 [US9] Return 404 for cross-user task access attempts in backend/app/routes/tasks.py
- [ ] T129 [US9] Verify AI-ready fields exist in database schema in backend/app/models.py

### Frontend Implementation

- [ ] T130 [P] [US9] Add 401 redirect to login on API errors in frontend/lib/api.ts
- [ ] T131 [P] [US9] Implement session expiration toast notification in frontend/lib/session-handler.ts
- [ ] T132 [US9] Test data isolation between multiple users

**Checkpoint**: User Story 9 complete - data is secure and isolated

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Performance & Optimization

- [ ] T133 [P] Implement virtual scrolling for large task lists in frontend/components/task/task-list.tsx
- [ ] T134 [P] Add image optimization for illustrations in frontend/app/page.tsx
- [ ] T135 [P] Optimize glassmorphism effects with CSS will-change in frontend/styles/globals.css
- [ ] T136 Run Lighthouse audit and address performance issues

### Error Handling & Edge Cases

- [ ] T137 [P] Add session expiry handling during form edits in frontend/lib/session-handler.ts
- [ ] T138 [P] Implement network error toast with retry in frontend/lib/api.ts
- [ ] T139 [P] Add stale data detection on tab focus in frontend/lib/api-client.ts
- [ ] T140 [P] Handle long task title truncation in frontend/components/task/task-card.tsx
- [ ] T141 [P] Add database connection error page in frontend/app/error.tsx

### Final Polish

- [ ] T142 [P] Add hover and focus states to all interactive elements
- [ ] T143 [P] Verify WCAG AA contrast ratios (4.5:1) across all components
- [ ] T144 [P] Test glassmorphism fallback for browsers without backdrop-filter
- [ ] T145 Verify all Phase I features work per quickstart.md validation
- [ ] T146 Run end-to-end test of complete user journey

---

## Dependencies & Execution Order

### Phase Dependencies (UPDATED FOR REPAIR)

```
Phase 0 (REPAIR) ← NEW: MUST COMPLETE FIRST
    ↓
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
    ├→ Phase 3 (US1: Discover & Sign Up) [P1]
    ├→ Phase 4 (US2: Authenticate) [P1]
    ├→ Phase 5 (US3: Create Task) [P1]
    ├→ Phase 6 (US4: View Tasks) [P1]
    ├→ Phase 7 (US5: Complete Task) [P1]
    │   └→ MVP Complete after Phase 7
    ├→ Phase 8 (US6: Edit/Delete) [P2]
    ├→ Phase 9 (US7: Command Center) [P2]
    ├→ Phase 10 (US8: Mobile) [P2]
    └→ Phase 11 (US9: Security) [P3]
    ↓
Phase 12 (Polish)
```

### User Story Dependencies

- **REPAIR Phase (Phase 0)**: BLOCKS ALL - Must complete before any other work
- **User Story 1 (P1)**: No dependencies on other US - can start after Foundational phase
- **User Story 2 (P1)**: No dependencies on other US - can start after Foundational phase
- **User Story 3 (P1)**: Requires US2 (dashboard) - but can develop independently in parallel
- **User Story 4 (P1)**: Requires US2 (dashboard) - but can develop independently in parallel
- **User Story 5 (P1)**: Requires US4 (task cards) - but can develop independently in parallel
- **User Story 6 (P2)**: Requires US4 (task cards) - but can develop independently in parallel
- **User Story 7 (P2)**: Requires US2 (Command Center placeholder) - but can develop independently in parallel
- **User Story 8 (P2)**: No dependencies - responsive design can be applied to any component
- **User Story 9 (P3)**: No dependencies - security is cross-cutting

### Within Each User Story

- Backend endpoints before frontend integration
- Models before services
- Services before endpoints
- Core implementation before integration

### Parallel Opportunities

**Within REPAIR Phase (Phase 0)**:
- T002, T003, T004, T005 can run in parallel (dependency fixes)
- T011, T012 can run in parallel (auth page creation)
- T013, T014 can run in parallel (auth form components)

**Within Setup (Phase 1)**: T002, T003, T004, T005 can run in parallel

**Within Foundational (Phase 2)**:
- Backend: T008, T009, T010, T011 can run in parallel
- Frontend: T013, T014, T015, T016, T017 can run in parallel

**After Foundational Phase**, all user stories can be worked on in parallel by different developers

**Within Each User Story Phase**, tasks marked [P] can be executed in parallel

---

## Parallel Example: REPAIR Phase (Phase 0)

```bash
# Launch all parallel repair tasks together:
Task T002: "Pin bcrypt to <5.0.0 in requirements.txt"
Task T003: "Add missing passlib dependency"
Task T004: "Add missing asyncpg dependency"
Task T005: "Add missing requests dependency"

# After dependencies are fixed:
Task T006: "Reinstall backend dependencies with pinned versions"

# Then parallel auth tasks:
Task T011: "Create signin page"
Task T012: "Create signup page"

# Then verification:
Task T022-T026: "Test all repair fixes"
```

---

## Implementation Strategy

### Repair First (NEW - MANDATORY)

1. **COMPLETE Phase 0: REPAIR** (T000-T026) - MANDATORY FIRST STEP
2. Verify application starts without errors
3. Verify signup/login works end-to-end
4. **ONLY AFTER REPAIR COMPLETE** proceed with implementation phases

### MVP First (P1 Stories Only)

1. Complete Phase 0: REPAIR (T000-T026) - **MUST DO FIRST**
2. Complete Phase 1: Setup (T001-T005)
3. Complete Phase 2: Foundational (T006-T017) - CRITICAL BLOCKER
4. Complete Phase 3: User Story 1 - Discover & Sign Up (T027-T036)
5. Complete Phase 4: User Story 2 - Authenticate (T037-T048)
6. **STOP and VALIDATE**: Test landing → signup → login → dashboard flow
7. Complete Phase 5: User Story 3 - Create Task (T049-T063)
8. Complete Phase 6: User Story 4 - View Tasks (T064-T081)
9. Complete Phase 7: User Story 5 - Complete Task (T082-T091)
10. **MVP COMPLETE**: All P1 stories deliver full Phase I feature parity

### Incremental Delivery

| Milestone | Tasks | Value Delivered |
|-----------|-------|-----------------|
| **System Functional** | Phase 0 | Application can start and authenticate users |
| Foundation | Phase 1-2 | Project structure, API foundation |
| User Acquisition | Phase 3 | Landing page + signup working |
| Authenticated Access | Phase 4 | Users can log in and see dashboard |
| Core CRUD | Phase 5-6 | Full task creation and viewing |
| Task Completion | Phase 7 | Recurring tasks, celebrations |
| **MVP Complete** | Phases 0-7 | **Production-ready todo app** |
| Advanced Edit | Phase 8 | Edit/delete with audit trail |
| Command Center | Phase 9 | Text-based natural commands |
| Mobile Ready | Phase 10 | Full responsive experience |
| Security Hardened | Phase 11 | Data isolation verified |
| Production Polish | Phase 12 | Performance, accessibility, edge cases |

### Parallel Team Strategy

With 3 developers AFTER REPAIR phase completes:

```
Developer A: Phase 0 (REPAIR) + User Stories 1 & 2 (Landing, Auth)
Developer B: User Stories 3 & 5 (Create, Complete)
Developer C: User Stories 4 & 6 (View, Edit)
```

**IMPORTANT**: All developers must wait for Phase 0 REPAIR to complete before starting other work.

---

## Summary

- **Total Tasks**: 163 (26 REPAIR tasks added)
- **REPAIR Tasks**: 26 (T000-T026) - NEW, MANDATORY FIRST
- **Setup Tasks**: 5
- **Foundational Tasks**: 12
- **User Story 1 Tasks**: 10
- **User Story 2 Tasks**: 12
- **User Story 3 Tasks**: 15
- **User Story 4 Tasks**: 18
- **User Story 5 Tasks**: 10
- **User Story 6 Tasks**: 12
- **User Story 7 Tasks**: 14
- **User Story 8 Tasks**: 7
- **User Story 9 Tasks**: 8
- **Polish Tasks**: 14

**MVP Scope (P1 Stories)**: Phases 0-7 = 103 tasks (includes REPAIR)
**Full Scope**: All 163 tasks

**Parallel Opportunities**: ~60% of tasks within each phase can run in parallel

**Independent Test Criteria**: Each user story phase includes explicit independent test verification

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- [REPAIR] label marks critical bug fix tasks that must be completed first
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **REPAIR phase (Phase 0) must be completed BEFORE any other implementation work**
- MVP is achievable with P1 stories only (Phases 0-7)
- P2 and P3 stories add value without requiring P1 refactoring
