# Tasks: Fix Phase II Integration Issues

**Input**: Design documents from `/specs/001-fix-phase2-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification. The focus is on fixing existing integration issues to enable the Phase II application to function.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` at repository root (Next.js 16+ App Router)
- **Backend**: `backend/` at repository root (FastAPI + SQLModel)
- **Phase I**: `/src/` console app (unchanged, do not modify)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify and configure environment for both frontend and backend services

- [x] T001 Generate secure 32-character BETTER_AUTH_SECRET and document in both `.env` files
- [x] T002 Verify DATABASE_URL includes `?sslmode=require` parameter in backend/.env
- [x] T003 [P] Install all Python dependencies in backend/.venv (FastAPI, SQLModel, PyJWT, psycopg2)
- [x] T004 [P] Install all npm dependencies in frontend/ (Next.js, Better Auth, shadcn/ui components)
- [x] T005 [P] Create backend/.env with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS
- [x] T006 [P] Create frontend/.env.local with DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, NEXT_PUBLIC_API_URL

**Checkpoint**: ✅ Environment configured. Both services can access dependencies and environment variables.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Verify Better Auth JWT plugin is enabled in frontend/lib/auth.ts
- [x] T008 Implement PyJWT verification middleware in backend/app/jwt_middleware.py with shared secret
- [x] T009 Configure NeonDB SSL connection in backend/app/db.py with pool settings (pool_pre_ping, pool_recycle, sslmode)
- [x] T010 Configure CORS in backend/app/main.py with specific origins and allow_credentials=True
- [x] T011 Create Task SQLModel in backend/app/models.py with user_id foreign key and indexes
- [x] T012 Initialize database tables (user, session, task) on backend startup in backend/app/main.py

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Can Sign Up and Access Their Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable new user signup flow with automatic login and immediate task creation capability

**Independent Test**: Create a new account, add a task, verify task appears and persists across page refresh

### Implementation for User Story 1

- [x] T013 [P] [US1] Configure Better Auth with JWT plugin in frontend/lib/auth.ts (expirationTime: "7d")
- [x] T014 [P] [US1] Enable httpOnly cookies for JWT storage in frontend/lib/auth.ts session configuration
- [x] T015 [P] [US1] Implement getSession() helper in frontend/lib/auth-client.ts to retrieve JWT from session response
- [x] T016 [P] [US1] Create POST /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py with JWT verification dependency
- [x] T017 [P] [US1] Implement GET /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py with user filtering
- [x] T018 [US1] Integrate JWT token in Authorization header for API calls in frontend/lib/api.ts
- [x] T019 [US1] Wire signup form to Better Auth signUp.email() in frontend/components/auth/signup-form.tsx
- [ ] T020 [US1] Test end-to-end signup → task creation → persistence flow

**Checkpoint**: ✅ Backend and frontend code complete - pending end-to-end integration testing

---

## Phase 4: User Story 2 - Application Connects to Database Successfully (Priority: P1)

**Goal**: Establish secure SSL-encrypted NeonDB connection with proper connection pooling

**Independent Test**: Start backend server, verify logs show successful database connection with zero SSL/certificate errors

### Implementation for User Story 2

- [x] T021 [P] [US2] Update DATABASE_URL in backend/.env to include `?sslmode=require` parameter
- [x] T022 [P] [US2] Configure SQLModel engine with sslmode=require in backend/app/db.py connect_args
- [x] T023 [P] [US2] Set pool_pre_ping=True in backend/app/db.py to verify connections before use
- [x] T024 [P] [US2] Set pool_recycle=300 in backend/app/db.py for serverless-friendly connection recycling
- [x] T025 [US2] Create database connection test script backend/neondb_test.py to verify SSL connection
- [x] T026 [US2] Test backend startup with `uvicorn app.main:app` and verify no SSL errors in logs

**Checkpoint**: ✅ Database connectivity is verified - backend connects successfully with SSL

---

## Phase 5: User Story 3 - Frontend Successfully Communicates with Backend API (Priority: P1)

**Goal**: Enable authenticated API communication between Next.js frontend and FastAPI backend without CORS or authentication errors

**Independent Test**: Open browser console, perform task operations - verify zero CORS errors and all API calls return 200 OK

### Implementation for User Story 3

- [x] T027 [P] [US3] Configure CORS_ORIGINS="http://localhost:3000" in backend/.env
- [x] T028 [P] [US3] Add CORSMiddleware to backend/app/main.py with allow_credentials=True
- [x] T029 [P] [US3] Set allow_origins from CORS_ORIGINS env var (not wildcard) in backend/app/main.py
- [x] T030 [P] [US3] Create apiClient helper in frontend/lib/api.ts with Authorization header injection
- [x] T031 [P] [US3] Implement JWT extraction from session in frontend/lib/api.ts getAuthToken() function
- [ ] T032 [US3] Test API call from frontend dashboard - verify CORS headers and JWT passing
- [ ] T033 [US3] Verify all task CRUD endpoints return proper responses without CORS errors

**Checkpoint**: ✅ Code implementation complete - pending end-to-end integration testing

---

## Phase 6: User Story 4 - User Can Log In with Existing Credentials (Priority: P2)

**Goal**: Enable returning users to log in with email/password and receive valid JWT token

**Independent Test**: Log out, then log back in with same credentials - verify redirected to dashboard with access to tasks

### Implementation for User Story 4

- [x] T034 [P] [US4] Wire login form to Better Auth signIn.email() in frontend/components/auth/login-form.tsx
- [x] T035 [P] [US4] Add JWT token retrieval after successful login in frontend/lib/auth-client.ts
- [x] T036 [P] [US4] Store JWT in httpOnly cookie via Better Auth session in frontend/lib/auth.ts
- [x] T037 [US4] Implement error handling for invalid credentials in frontend/components/auth/login-form.tsx
- [ ] T038 [US4] Test login with invalid credentials - verify clear error message
- [ ] T039 [US4] Test login with valid credentials - verify JWT token and redirect to dashboard

**Checkpoint**: ✅ Code implementation complete - pending end-to-end integration testing

---

## Phase 7: User Story 5 - All CRUD Operations Work End-to-End (Priority: P2)

**Goal**: Enable complete task management: Create, Read, Update, Delete, and Toggle completion

**Independent Test**: Test each operation - add task, view tasks, edit task, mark complete, delete task - verify all persist

### Implementation for User Story 5

- [x] T040 [P] [US5] Implement GET /api/{user_id}/tasks/{id} in backend/app/routes/tasks.py with ownership check
- [x] T041 [P] [US5] Implement PUT /api/{user_id}/tasks/{id} in backend/app/routes/tasks.py with validation
- [x] T042 [P] [US5] Implement DELETE /api/{user_id}/tasks/{id} in backend/app/routes/tasks.py with 403 on unauthorized
- [x] T043 [P] [US5] Implement PATCH /api/{user_id}/tasks/{id}/complete in backend/app/routes/tasks.py
- [x] T044 [P] [US5] Create task update form component in frontend/components/tasks/task-form.tsx
- [x] T045 [P] [US5] Implement delete task handler in frontend/components/tasks/task-actions.tsx
- [x] T046 [P] [US5] Implement toggle complete handler in frontend/components/tasks/task-card.tsx
- [x] T047 [US5] Add frontend validation for empty task title with "Title is required" message in frontend/components/tasks/task-form.tsx
- [x] T048 [US5] Add backend validation for empty task title with consistent "Title is required" message in backend/app/routes/tasks.py
- [ ] T049 [US5] Test all five CRUD operations end-to-end with data persistence verification

**Checkpoint**: ✅ Code implementation complete - pending end-to-end integration testing

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Edge case handling, error UX improvements, and security hardening from clarifications

- [x] T050 [P] Implement JWT expiry handler in frontend/lib/api.ts - redirect to login with "Session expired" message
- [x] T051 [P] Return 403 Forbidden (not 404) when user attempts to access another user's task in backend/app/routes/tasks.py
- [x] T052 [P] Add network timeout detection in frontend/lib/api.ts with error toast display
- [ ] T053 Implement retry button in frontend/lib/api.ts error toast for one-click retry on timeout
- [x] T054 [P] Verify httpOnly cookie flag is set on session cookies in frontend/lib/auth.ts
- [ ] T055 Run full integration test: signup → create → update → complete → delete → logout → login
- [ ] T056 Validate all environment variables are documented in backend/.env.example and frontend/.env.example.local
- [ ] T057 Run quickstart.md validation checklist to confirm all setup steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (need env vars to configure JWT, DB, CORS) - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Sign Up)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1 - Database)**: Can start after Foundational - Independent of other stories
- **User Story 3 (P1 - API Communication)**: Can start after Foundational - Independent of other stories
- **User Story 4 (P2 - Login)**: Can start after Foundational - Builds on US1 auth foundation but independently testable
- **User Story 5 (P2 - Full CRUD)**: Depends on US1 and US3 - Requires working auth and API communication

### Within Each User Story

- Tasks marked [P] within a story can run in parallel (different files)
- Implementation tasks typically follow order: config → backend → frontend → integration → test

### Parallel Opportunities

**Phase 1 (Setup)** - All can run in parallel:
- T003, T004, T005, T006 (dependency installation and env file creation)

**Phase 2 (Foundational)** - Partial parallelization:
- T007, T008, T009, T010 (different files: auth.ts, jwt_middleware.py, db.py, main.py)
- T011, T012 (models then main.py initialization)

**Phase 3 (US1 - Sign Up)** - Parallel groups:
- Group 1: T013, T014, T015 (frontend auth configuration)
- Group 2: T016, T017 (backend endpoints)
- Then: T018, T019, T020 (integration and testing)

**Phase 4 (US2 - Database)** - Mostly parallel:
- T021, T022, T023, T024 (all db.py configuration)
- Then: T025, T026 (testing)

**Phase 5 (US3 - API Communication)** - Parallel groups:
- Group 1: T027, T028, T029 (backend CORS)
- Group 2: T030, T031 (frontend API client)
- Then: T032, T033 (integration testing)

**Phase 6 (US4 - Login)** - Partial parallelization:
- T034, T035, T036 (frontend login components)
- Then: T037, T038, T039 (error handling and testing)

**Phase 7 (US5 - CRUD)** - Highly parallel:
- Group 1: T040, T041, T042, T043 (all backend endpoints)
- Group 2: T044, T045, T046 (frontend components)
- Group 3: T047, T048 (validation on both sides)
- Then: T049 (integration testing)

**Phase 8 (Polish)** - All can run in parallel:
- T050, T051, T052, T053, T054 (all independent fixes)
- Then: T055, T056, T057 (validation)

---

## Parallel Example: User Story 1 (Sign Up Flow)

```bash
# Launch all frontend auth configuration together:
Task T013: "Configure Better Auth with JWT plugin in frontend/lib/auth.ts"
Task T014: "Enable httpOnly cookies for JWT storage in frontend/lib/auth.ts"
Task T015: "Implement getSession() helper in frontend/lib/auth-client.ts"

# Launch all backend endpoints together:
Task T016: "Create POST /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py"
Task T017: "Implement GET /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only - All P1)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T012) - CRITICAL
3. Complete Phase 3: User Story 1 (T013-T020) - Sign up + task creation
4. Complete Phase 4: User Story 2 (T021-T026) - Database connectivity
5. Complete Phase 5: User Story 3 (T027-T033) - API communication
6. **STOP and VALIDATE**: Test signup → task creation → persistence independently
7. Deploy/demo if ready

This delivers a working MVP where users can sign up, create tasks, and see them persist.

### Incremental Delivery (Full Scope)

1. Complete Setup + Foundational → Foundation ready
2. Add User Stories 1, 2, 3 (all P1) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 4 (P2 - Login) → Test independently → Deploy/Demo
4. Add User Story 5 (P2 - Full CRUD) → Test independently → Deploy/Demo
5. Add Polish (Phase 8) → Final validation
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Sign Up)
   - Developer B: User Story 2 (Database)
   - Developer C: User Story 3 (API Communication)
3. After P1 stories complete:
   - Developer A: User Story 4 (Login)
   - Developer B: User Story 5 (CRUD)
4. Stories complete and integrate independently

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 57 |
| **Setup Tasks** | 6 |
| **Foundational Tasks** | 6 |
| **US1 (Sign Up) Tasks** | 8 |
| **US2 (Database) Tasks** | 6 |
| **US3 (API Comm) Tasks** | 7 |
| **US4 (Login) Tasks** | 6 |
| **US5 (CRUD) Tasks** | 10 |
| **Polish Tasks** | 8 |
| **Parallelizable** | 45+ (marked with [P]) |
| **MVP Scope (P1 stories)** | 33 tasks (Phases 1-5) |

**Recommended MVP**: Complete Phases 1-5 (User Stories 1-3, all P1) for a working sign-up → task creation → persistence flow.

**Format Validation**: ✅ ALL tasks follow checkbox format with ID, file paths, and story labels where applicable.
