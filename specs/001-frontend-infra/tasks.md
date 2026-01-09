# Tasks: Frontend Infrastructure Stabilization

**Input**: Design documents from `/specs/001-frontend-infra/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api.yaml, quickstart.md

**Tests**: This feature focuses on fixing existing inconsistencies. Tests are already in place via `./scripts/verify-e2e.sh` and `./backend/scripts/test_all.py`. No new test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a Phase II full-stack web application with monorepo structure:
- Frontend: `frontend/`
- Backend: `backend/` (READ-ONLY for this feature)

---

## Phase 1: Setup (Verification & Preparation)

**Purpose**: Verify environment is ready and understand current state

- [X] T001 Verify backend is running on http://localhost:8000 with `curl http://localhost:8000/api/health`
- [X] T002 Verify frontend dependencies are installed in `frontend/node_modules`
- [X] T003 Check environment variables configured: `frontend/.env` exists with `NEXT_PUBLIC_API_URL`, `BETTER_AUTH_SECRET`, `DATABASE_URL`
- [X] T004 Run existing type check baseline: `cd frontend && npx tsc --noEmit --strict` (note existing errors)

**Checkpoint**: Environment verified; baseline type errors documented

---

## Phase 2: Foundational (Authentication Token Endpoint)

**Purpose**: Create the missing `/api/auth/token` endpoint that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create JWT token endpoint at `frontend/app/api/auth/token/route.ts` using `auth.api.getSession({ headers })` pattern
- [X] T006 Test JWT endpoint manually: `curl -H "Cookie: better-auth.session_token=<valid>" http://localhost:3000/api/auth/token` returns `{ "token": "..." }`

**Checkpoint**: `/api/auth/token` endpoint returns valid JWT for authenticated sessions

---

## Phase 3: User Story 1 - Reliable Task Synchronization (Priority: P1) 🎯 MVP

**Goal**: Users can create, update, complete, and delete tasks that persist correctly to the backend.

**Independent Test**: A signed-in user can create a task, mark it complete, refresh the page, and see the completed state persists.

**Acceptance**: All task CRUD operations work end-to-end; no data loss on refresh.

### Implementation for User Story 1

- [X] T007 [P] [US1] Add `getAuthToken()` private method to `frontend/lib/api-client.ts` that calls `/api/auth/token`
- [X] T008 [P] [US1] Remove `userId` parameter from `getTasks()` method signature in `frontend/lib/api-client.ts`
- [X] T009 [P] [US1] Remove `userId` parameter from `getTask()` method signature in `frontend/lib/api-client.ts`
- [X] T010 [P] [US1] Remove `userId` parameter from `createTask()` method signature in `frontend/lib/api-client.ts`
- [X] T011 [P] [US1] Remove `userId` parameter from `updateTask()` method signature in `frontend/lib/api-client.ts`
- [X] T012 [P] [US1] Remove `userId` parameter from `deleteTask()` method signature in `frontend/lib/api-client.ts`
- [X] T013 [P] [US1] Remove `userId` parameter from `toggleTaskComplete()` method signature in `frontend/lib/api-client.ts`
- [X] T014 [US1] Update `healthCheck()` method in `frontend/lib/api-client.ts` to use `/api/health` instead of `/health`
- [X] T015 [US1] Update all `request()` method calls in `frontend/lib/api-client.ts` to pass token from `getAuthToken()` instead of parameter

**Checkpoint**: API client methods no longer require `userId`; all calls use JWT for authentication

---

## Phase 4: User Story 2 - Seamless Authentication Flow (Priority: P2)

**Goal**: Users can sign in, navigate protected routes, and sign out without errors or unexpected redirects.

**Independent Test**: A user can sign in with valid credentials, access the dashboard, and sign out cleanly. Each action completes without error.

**Acceptance**: Sign in → dashboard → sign out flow works; middleware correctly checks session cookie.

### Implementation for User Story 2

- [X] T016 [P] [US2] Remove fallback to `session` cookie in `frontend/middleware.ts` (only check `better-auth.session_token`)
- [X] T017 [US2] Remove all `console.log()` debug statements from `frontend/middleware.ts`
- [X] T018 [US2] Remove `console.log()` and `console.error()` debug statements from `frontend/app/actions/tasks.ts` (keep error logging for production)
- [X] T019 [US2] Remove `console.debug()` and `console.error()` debug statements from `frontend/lib/api-client.ts` (keep error logging via `logError()`)

**Checkpoint**: Production code has no debug logging; middleware uses correct cookie name

---

## Phase 5: User Story 3 - Clear Error Communication (Priority: P3)

**Goal**: Users receive actionable error messages when operations fail (network issues, invalid input, auth problems).

**Independent Test**: Trigger various error conditions (invalid input, network disconnection, expired session) and see appropriate user-facing messages.

**Acceptance**: All API errors surface as human-readable messages; Result pattern is used consistently.

### Implementation for User Story 3

- [X] T020 [P] [US3] Verify `frontend/lib/errors.ts` exports `Result<T>`, `ok()`, `err()`, and `ApiError` (no changes needed if correct)
- [X] T021 [US3] Ensure `handleJwtExpiry()` function in `frontend/lib/api-client.ts` redirects with "Session expired" message
- [X] T022 [US3] Verify `getSessionMessage()` function exists in `frontend/lib/api-client.ts` for login page context display

**Checkpoint**: Error communication paths are verified; JWT expiry handled correctly

---

## Phase 6: Cleanup & Cross-Cutting Concerns

**Purpose**: Remove duplicate code, verify type safety, and validate all changes

- [X] T023 [P] Delete duplicate API client at `frontend/lib/api.ts` (functionality moved to `api-client.ts`)
- [X] T024 [P] Search codebase for any remaining imports of `lib/api.ts` and update to use `lib/api-client.ts`
- [X] T025 Run full type check: `cd frontend && npx tsc --noEmit --strict` (expected: 0 errors)
- [X] T026 Run E2E verification: `./scripts/verify-e2e.sh` (expected: all 13 tests pass)
- [X] T027 Verify no console.log in production paths: `grep -r "console\.log" frontend/app --exclude-dir=node_modules` (expected: 0 matches)
- [X] T028 Verify only one API client exists: `grep -l "export.*api" frontend/lib/*.ts` (expected: only `api-client.ts`)

**Checkpoint**: All cleanup complete; tests pass; zero type errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup verification - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (JWT endpoint)
- **User Story 2 (Phase 4)**: Depends on Foundational (JWT endpoint) - can run parallel to US1
- **User Story 3 (Phase 5)**: Depends on Foundational (JWT endpoint) - can run parallel to US1/US2
- **Cleanup (Phase 6)**: Depends on US1, US2, US3 completion - final phase

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2

### Within Each User Story

- User Story 1: T007-T013 are parallel refactor (different methods); T014-T015 depend on T007
- User Story 2: T016-T019 are all parallel (different files)
- User Story 3: T020 is verification; T021-T022 depend on T020

### Parallel Opportunities

- **Phase 2**: Single task (T005), must complete before user stories
- **Phase 3 (US1)**: T007-T013 can all run in parallel (different method signatures)
- **Phase 4 (US2)**: T016, T017, T018, T019 can all run in parallel (different files)
- **Phase 5 (US3)**: T020, T021 can run in parallel; T022 depends on T021
- **Phase 6**: T023, T024, T027, T028 can run in parallel (different verification tasks)
- **Cross-phase**: After Phase 2 completes, US1, US2, and US3 can proceed in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all method signature updates together (after T007 completes):
Task: "Remove userId parameter from getTasks() method signature in frontend/lib/api-client.ts"
Task: "Remove userId parameter from getTask() method signature in frontend/lib/api-client.ts"
Task: "Remove userId parameter from createTask() method signature in frontend/lib/api-client.ts"
Task: "Remove userId parameter from updateTask() method signature in frontend/lib/api-client.ts"
Task: "Remove userId parameter from deleteTask() method signature in frontend/lib/api-client.ts"
Task: "Remove userId parameter from toggleTaskComplete() method signature in frontend/lib/api-client.ts"
```

---

## Parallel Example: User Story 2

```bash
# Launch all file cleanup tasks together:
Task: "Remove fallback to session cookie in frontend/middleware.ts"
Task: "Remove all console.log() debug statements from frontend/middleware.ts"
Task: "Remove console.log() and console.error() debug statements from frontend/app/actions/tasks.ts"
Task: "Remove console.debug() and console.error() debug statements from frontend/lib/api-client.ts"
```

---

## Parallel Example: Cleanup Phase

```bash
# Launch all verification tasks together:
Task: "Delete duplicate API client at frontend/lib/api.ts"
Task: "Search codebase for any remaining imports of lib/api.ts"
Task: "Verify no console.log in production paths"
Task: "Verify only one API client exists"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify environment)
2. Complete Phase 2: Foundational (create `/api/auth/token` endpoint) - **CRITICAL**
3. Complete Phase 3: User Story 1 (API client refactor)
4. **STOP and VALIDATE**: Test task operations independently - create task, refresh, verify persistence
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → JWT endpoint ready
2. Add User Story 1 → Test task operations independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test auth flow independently → Deploy/Demo
4. Add User Story 3 → Test error handling → Deploy/Demo
5. Cleanup → Final validation
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (API client refactor)
   - Developer B: User Story 2 (Middleware and logging cleanup)
   - Developer C: User Story 3 (Error communication verification)
3. Stories complete and integrate independently
4. Team completes Cleanup phase together

---

## File Change Summary

| File | Action | Reason |
|------|--------|--------|
| `frontend/app/api/auth/token/route.ts` | CREATE | Missing JWT endpoint for API authentication |
| `frontend/lib/api-client.ts` | REFACTOR | Remove `userId` params, add `getAuthToken()`, fix health path |
| `frontend/lib/api.ts` | DELETE | Duplicate of api-client.ts functionality |
| `frontend/middleware.ts` | UPDATE | Remove `session` cookie fallback, remove console.log |
| `frontend/app/actions/tasks.ts` | UPDATE | Remove debug console statements |
| `frontend/lib/errors.ts` | KEEP | Already well-designed, no changes needed |
| `frontend/lib/auth.ts` | KEEP | Better Auth config, no changes needed |

---

## Notes

- [P] tasks = different files or methods, no dependencies within the phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- The `/api/auth/token` endpoint is CRITICAL - blocks all user story implementation
- Better Auth uses `better-auth.session_token` as the default cookie name
- Backend infers user identity from JWT - `userId` parameters are unnecessary
- Health check path is `/api/health` (confirmed via `backend/app/main.py`)
- All changes are frontend-only per constraint FR-013
- Stop at any checkpoint to validate story independently
