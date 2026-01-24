# Tasks: Loading States & User Profile Enhancement

**Input**: Design documents from `/specs/010-loading-states-user-profile/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Tests**: Tests are NOT included in this specification per feature requirements. Focus on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/alembic/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Review plan, spec, and design documents to understand implementation requirements

- [ ] T001 Review implementation plan at specs/010-loading-states-user-profile/plan.md
- [ ] T002 Review data model documentation at specs/010-loading-states-user-profile/data-model.md
- [ ] T003 Review research findings at specs/010-loading-states-user-profile/research.md
- [ ] T004 Review API contracts at specs/010-loading-states-user-profile/contracts/openapi.yaml
- [ ] T005 Verify Python 3.13+ is installed (backend requirement)
- [ ] T006 Verify Node.js 20+ and TypeScript 5+ are installed (frontend requirement)
- [ ] T007 Verify PostgreSQL database access (Neon Serverless)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create alembic migration for adding first_name and last_name columns in backend/alembic/versions/010_add_first_last_name.py
- [ ] T009 [P] Update User model with first_name and last_name fields in backend/src/models/user.py
- [ ] T010 [P] Add display_name computed property to User model in backend/src/models/user.py
- [ ] T011 [P] Update UserCreate schema to accept first_name (required) and last_name (optional) in backend/src/models/user.py
- [ ] T012 [P] Update UserPublic response schema to include first_name, last_name, and display_name in backend/src/models/user.py
- [ ] T013 [P] Create background migration service for legacy user names in backend/src/services/migration.py
- [ ] T014 [P] Update signup endpoint to handle first_name and last_name in backend/src/routes/auth.py
- [ ] T015 [P] Update GET /api/auth/me endpoint to return new name fields in backend/src/routes/auth.py
- [ ] T016 [P] Update GET /api/auth/token endpoint to return new name fields in backend/src/routes/auth.py

**Checkpoint**: Foundation ready - database schema, models, and endpoints updated. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Enhanced Loading Feedback (Priority: P1) 🎯 MVP

**Goal**: Implement dual-ring spinner animation for dashboard loading and tab switches

**Independent Test**: Navigate to dashboard and observe dual-ring spinner during initial load and tab switches. Verify spinner fades out smoothly and error card appears on failures.

### Frontend Implementation for US1

- [ ] T017 [P] [US1] Create DualRingSpinner component in frontend/src/components/ui/dual-ring-spinner.tsx
- [ ] T018 [P] [US1] Add CSS keyframe animations for dual-ring spinner in frontend/app/globals.css (rotate-cw and rotate-ccw)
- [ ] T019 [US1] Implement minimum display duration logic to prevent flash in frontend/src/components/ui/dual-ring-spinner.tsx
- [ ] T020 [P] [US1] Create LoadingErrorCard component with retry button in frontend/src/components/dashboard/loading-error-card.tsx
- [ ] T021 [US1] Integrate DualRingSpinner with dashboard content loading state in frontend/src/components/dashboard/dashboard-content.tsx
- [ ] T022 [US1] Integrate DualRingSpinner with status tab switches (Pending/Done) in frontend/src/components/dashboard/dashboard-content.tsx
- [ ] T023 [US1] Implement debounce logic for rapid tab switches in frontend/src/components/dashboard/dashboard-content.tsx
- [ ] T024 [US1] Add 15-second timeout with error state in frontend/src/components/dashboard/dashboard-content.tsx
- [ ] T025 [US1] Test spinner visibility within 100ms target in frontend/src/components/dashboard/dashboard-content.tsx
- [ ] T026 [US1] Test fade-out transition within 300ms target in frontend/src/components/dashboard/dashboard-content.tsx

**Checkpoint**: User Story 1 complete - Dual-ring spinner displays on dashboard load and tab switches, error card with retry appears on failures. Visual feedback provides clear indication of system activity.

---

## Phase 4: User Story 2 - Personalized User Profile (Priority: P2)

**Goal**: Separate first and last name fields in signup form and display throughout UI

**Independent Test**: Complete signup flow with first/last name (or first name only for mononyms). Verify name displays correctly in header dropdown and all profile sections.

### Frontend Implementation for US2

- [ ] T027 [P] [US2] Update User type definition to include firstName, lastName, displayName in frontend/src/lib/types/user.ts
- [ ] T028 [P] [US2] Add getDisplayName helper function in frontend/src/lib/types/user.ts
- [ ] T029 [P] [US2] Create Zod validation schema for signup form with first_name (required) and last_name (optional) in frontend/components/auth/signup-form.tsx
- [ ] T030 [US2] Add first_name and last_name input fields to signup form in frontend/components/auth/signup-form.tsx
- [ ] T031 [US2] Mark first_name field as required and last_name as optional in frontend/components/auth/signup-form.tsx
- [ ] T032 [US2] Implement validation error display for missing first name in frontend/components/auth/signup-form.tsx
- [ ] T033 [US2] Add 50-character limit per name field with validation in frontend/components/auth/signup-form.tsx
- [ ] T034 [US2] Implement XSS prevention (strip HTML tags) in frontend/components/auth/signup-form.tsx
- [ ] T035 [US2] Update signup form submission to send firstName and lastName to backend API in frontend/components/auth/signup-form.tsx

### Frontend Integration for US2

- [ ] T036 [US2] Update user-nav dropdown to display displayName (first + last or first only) in frontend/src/components/layout/user-nav.tsx
- [ ] T037 [US2] Add displayName fallback logic for legacy data in frontend/src/components/layout/user-nav.tsx
- [ ] T038 [US2] Update header to show displayName in all profile references in frontend/src/components/layout/header.tsx
- [ ] T039 [US2] Test signup with both first and last name (displays "John Doe") in frontend/tests/integration/signup-flow.test.tsx
- [ ] T040 [US2] Test signup with only first name (mononym support, displays "Madonna") in frontend/tests/integration/signup-flow.test.tsx
- [ ] T041 [US2] Test validation rejects empty first name in frontend/tests/integration/signup-flow.test.tsx

**Checkpoint**: User Story 2 complete - Signup form collects first/last name, validation works correctly, displayName appears in header and profile sections. Supports both full names and mononyms inclusively.

---

## Phase 5: User Story 3 - Data Migration for Existing Users (Priority: P3)

**Goal**: Zero-downtime migration of legacy user names to new first_name/last_name schema

**Independent Test**: Sign in with legacy user account (single name field) and verify name displays correctly with no service interruption during migration.

### Backend Migration Implementation for US3

- [ ] T042 [P] [US3] Run alembic migration to add nullable columns in production database
- [ ] T043 [US3] Verify migration script rollback plan in backend/alembic/versions/010_add_first_last_name.py
- [ ] T044 [P] [US3] Test backward compatibility - old code still reads from 'name' column in backend/tests/integration/test_auth_flow.py
- [ ] T045 [US3] Test display_name property returns legacy 'name' when first_name is NULL in backend/tests/unit/test_user_model.py
- [ ] T046 [US3] Execute background migration job to copy legacy names to first_name field
- [ ] T047 [US3] Monitor migration progress (total users vs migrated users) in backend/src/services/migration.py
- [ ] T048 [US3] Verify zero service interruption during migration (monitor response times < 200ms P95)
- [ ] T049 [US3] Test legacy user sign-in after migration (name displays from first_name field) in backend/tests/integration/test_auth_flow.py

**Checkpoint**: User Story 3 complete - Legacy user names migrated to first_name field, zero downtime achieved, all existing users can sign in without disruption. Backward compatibility maintained throughout migration phases.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and validation across all user stories

- [ ] T050 [P] Update API documentation with new name fields in backend/README.md or API docs
- [ ] T051 [P] Update frontend component documentation with spinner and form changes in frontend/README.md
- [ ] T052 [P] Add comments to all code referencing Task IDs: `[TXXX]` and spec sections: `[From]: spec.md §X.X, plan.md §X.X`
- [ ] T053 Run manual testing checklist from quickstart.md (Loading States section)
- [ ] T054 Run manual testing checklist from quickstart.md (User Profile section)
- [ ] T055 Run manual testing checklist from quickstart.md (Migration section)
- [ ] T056 Verify all 8 success criteria from spec.md are met
- [ ] T057 Verify constitution compliance (Context7 used as primary source for all libraries)
- [ ] T058 Code cleanup - remove any TODO comments or debug statements
- [ ] T059 Final validation - run all backend tests: `pytest` in backend directory
- [ ] T060 Final validation - run all frontend tests: `npm test` in frontend directory

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on US2 or US3
  - User Story 2 (P2): Can start after Foundational - No dependencies on US1 or US3
  - User Story 3 (P3): Can start after Foundational - Should be tested after US2 for complete flow
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1 or US3
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Should complete after US2 for full signup/migration flow testing

### Within Each User Story

- Foundation tasks before user story tasks
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks in Phase 1 can run in parallel
- All Foundational tasks marked [P] in Phase 2 can run in parallel
- Once Foundational phase completes, US1, US2, and US3 can all start in parallel (if team capacity allows)
- Within US1: T017-T020 marked [P] can run in parallel
- Within US2: T027-T028 marked [P] can run in parallel
- Within US3: T042, T043, T044 marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 component creation tasks together:
Task: "Create DualRingSpinner component in frontend/src/components/ui/dual-ring-spinner.tsx"
Task: "Add CSS keyframe animations for dual-ring spinner in frontend/app/globals.css"
Task: "Create LoadingErrorCard component with retry button in frontend/src/components/dashboard/loading-error-card.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Loading States)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP delivers**: Dashboard loading states with dual-ring spinner animation, error handling with retry button, smooth fade transitions. Provides clear visual feedback for all data fetch operations.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Loading States) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (User Profile) → Test independently → Deploy/Demo
4. Add User Story 3 (Migration) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Loading States) - Frontend focused
   - Developer B: User Story 2 (User Profile) - Full stack
   - Developer C: User Story 3 (Migration) - Backend focused
3. Stories complete and integrate independently

---

## Notes

- **Task ID Format**: Sequential T001-T060 for easy tracking
- **[P] Marker**: Indicates task can run in parallel with others marked [P] in same phase
- **[Story] Label**: Maps task to User Story (US1, US2, US3) for traceability back to spec.md
- **Checkpoint Validation**: Each story has checkpoint where it should be independently testable
- **Spec References**: All tasks map back to functional requirements FR-001 through FR-021
- **Context7 Requirement**: Per Constitution §III.1, all library usage must reference Context7 documentation
- **No Tests**: Tests not included per feature specification - implementation focused
- **Code Comments**: Every code change must reference Task ID and spec section
- **File Paths**: All tasks include exact file paths from plan.md structure

## Success Criteria Verification

Per spec.md, the following success criteria must be met:

- **SC-001**: Loading animation visible within 100ms → Verified in T025
- **SC-002**: Animation fades within 300ms → Verified in T026
- **SC-003**: Signup completes in under 90 seconds → Verified in T039-T040
- **SC-004**: 100% of signups include first name → Verified in T041
- **SC-005**: Zero downtime during migration → Verified in T048
- **SC-006**: Loading state provides clear feedback (95% user understanding) → Manual test in T053
- **SC-007**: Name display correct in all UI locations → Verified in T036-T038
- **SC-008**: Form validation prevents missing first name → Verified in T032, T041
