# Tasks: Fix Authentication Integration

**Input**: Design documents from `/specs/001-fix-auth-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Not requested - focusing on implementation only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Backend Dependencies)

**Purpose**: Install required Python dependencies for JWT verification

- [ ] T001 Install python-jose[cryptography] library for JWT verification in backend/requirements.txt
- [ ] T002 Install python-dotenv for environment variable loading in backend/requirements.txt

---

## Phase 2: Foundational (JWT Verification Infrastructure)

**Purpose**: Core authentication infrastructure that MUST be complete before any user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 [P] Create JWT verification middleware in backend/app/jwt_middleware.py
- [ ] T004 [P] Update backend/app/auth.py to use new JWT verification
- [ ] T005 [P] Update backend/app/routes/tasks.py with detailed logging and error handling

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1) MVP

**Goal**: Enable Better Auth JWT plugin configuration so users can register and login successfully

**Independent Test**: Deploy both frontend and backend. Run signup flow locally. Verify:
- Better Auth creates user record in Neon PostgreSQL
- Session cookie is set in browser
- Dashboard page loads with user session
- JWT token is retrievable via getSession

### Implementation for User Story 1

- [ ] T006 [P] [US1] Update frontend/lib/auth.ts to add jwt() plugin configuration
- [ ] T007 [P] [US1] Update frontend/lib/auth-client.ts to include jwtClient plugin
- [ ] T008 [US1] Update frontend/app/actions/tasks.ts to use getSession for JWT token retrieval
- [ ] T009 [US1] Update frontend/lib/api.ts with comprehensive error handling

**Checkpoint**: User Story 1 should be fully functional - test signup and login flows

---

## Phase 4: User Story 2 - Task Management Dashboard Access (Priority: P1)

**Goal**: Enable authenticated users to access dashboard and manage their tasks via JWT-authenticated API

**Independent Test**: Login with test account. Access dashboard. Verify:
- All user tasks load correctly from backend
- User can create new task via API
- User can toggle task completion via API
- User can delete task via API
- User isolation verified (cannot see other users' tasks)

### Implementation for User Story 2

- [ ] T010 [P] [US2] Verify backend/app/routes/tasks.py has proper JWT auth dependencies
- [ ] T011 [P] [US2] Verify frontend/app/dashboard/page.tsx loads tasks correctly
- [ ] T012 [P] [US2] Verify frontend/components/tasks/task-form.tsx creates tasks via API
- [ ] T013 [P] [US2] Verify frontend/components/tasks/task-card.tsx toggles completion via API
- [ ] T014 [US2] Verify frontend/components/tasks/task-actions.tsx deletes tasks via API

**Checkpoint**: User Story 2 should work - test complete task CRUD flow

---

## Phase 5: User Story 3 - Session Management and Logout (Priority: P2)

**Goal**: Enable users to securely log out and end their session

**Independent Test**: Login, click logout button. Verify:
- Session cookie is removed from browser
- User is redirected to login page
- Attempting to access /dashboard redirects to login
- Login again creates new valid session

### Implementation for User Story 3

- [ ] T015 [P] [US3] Verify frontend/lib/auth-client.ts has signOut method available
- [ ] T016 [P] [US3] Verify frontend/components/layout/user-nav.tsx has logout button
- [ ] T017 [US3] Verify frontend/middleware.ts redirects to login after logout

**Checkpoint**: All user stories should be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation and final testing

- [ ] T018 [P] Create backend/tests/test_jwt_middleware.py with unit tests for JWT verification
- [ ] T019 Run end-to-end test: signup → login → create task → view tasks → logout
- [ ] T020 Verify environment variables are properly documented in .env.example files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staff capacity allows)
  - Or sequentially in priority order (US1 → US2 → US3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Depends on US1 for JWT plugin to be enabled
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for auth configuration

### Within Each User Story

- Models/Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- All tasks within a user story marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tasks for User Story 1 together:
Task: "Update frontend/lib/auth.ts to add jwt() plugin configuration"
Task: "Update frontend/lib/auth-client.ts to include jwtClient plugin"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004, T005)
3. Complete Phase 3: User Story 1 (T006, T007, T008, T009)
4. STOP and VALIDATE: Test signup/login flow
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (frontend JWT plugin)
   - Developer B: User Story 2 (task API integration)
   - Developer C: User Story 3 (logout flow)
3. Stories complete and integrate independently

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 20 |
| Setup Tasks | 2 |
| Foundational Tasks | 3 |
| User Story 1 Tasks | 4 |
| User Story 2 Tasks | 5 |
| User Story 3 Tasks | 3 |
| Polish Tasks | 3 |
| Parallelizable Tasks | 14 (70%) |

### Suggested MVP Scope

**User Story 1 (P1)** is the MVP. Complete:
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: User Story 1

Test: Signup → Login → Dashboard loads

### Next Steps

1. Run `/sp.implement` to execute tasks sequentially
2. Or manually complete tasks in dependency order
3. Test each user story independently before moving to next
