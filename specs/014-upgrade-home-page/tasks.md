---

description: "Task list for Home Page Upgrade with Latest Features implementation"
---

# Tasks: Home Page Upgrade with Latest Features

**Input**: Design documents from `/specs/014-upgrade-home-page/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Visual testing only - no automated tests requested for this content update feature.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/components/`, `frontend/app/`, `frontend/lib/`
- Paths below reflect the actual project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Review and preparation for content updates

- [ ] T001 Verify development environment is running for frontend in `frontend/`
- [ ] T002 Review existing hero section component at `frontend/components/landing/hero-section.tsx`
- [ ] T003 [P] Review design decisions from `specs/014-upgrade-home-page/research.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prepare for content updates - NO code changes in this phase

- [ ] T004 Confirm branch `014-upgrade-home-page` is checked out and up to date
- [ ] T005 Verify no uncommitted changes exist in working directory

**Checkpoint**: Ready to implement user story updates

---

## Phase 3: User Story 1 - Discover AI-Powered Productivity Features (Priority: P1) 🎯 MVP

**Goal**: First-time visitors see accurate information about all production-ready features (AI chatbot, voice input, semantic search, bilingual support, multi-channel notifications)

**Independent Test**: View home page while logged out. Verify badge shows "✨ AI-Powered Productivity Assistant", description mentions Chronos AI capabilities, and 6 feature cards are visible with accurate information about completed features.

### Implementation for User Story 1

- [X] T006 [P] [US1] Update badge text to "✨ AI-Powered Productivity Assistant" in `frontend/components/landing/hero-section.tsx` (line ~121)
- [X] T007 [US1] Update hero description to "Meet Chronos — Your AI-powered time guardian. Manage tasks with natural language, voice commands, and semantic search in English and Urdu." in `frontend/components/landing/hero-section.tsx` (line ~141)
- [X] T008 [P] [US1] Add `Bot` icon import from lucide-react for AI Chatbot card in `frontend/components/landing/hero-section.tsx`
- [X] T009 [P] [US1] Add `Search` icon import from lucide-react for Semantic Search card in `frontend/components/landing/hero-section.tsx`
- [X] T010 [P] [US1] Add `Languages` icon import from lucide-react for Bilingual Support card in `frontend/components/landing/hero-section.tsx`
- [X] T011 [US1] Replace existing 3 feature cards with 6 new feature cards in `frontend/components/landing/hero-section.tsx` (lines ~199-246)
- [X] T012 [US1] Update tagline to remove hackathon reference in `frontend/components/landing/hero-section.tsx` (line ~254)
- [X] T013 [US1] Adjust grid layout from `grid-cols-1 lg:grid-cols-3` to `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` in `frontend/components/landing/hero-section.tsx` (line ~197)

**Checkpoint**: At this point, User Story 1 should be fully functional. First-time visitors see accurate production-ready feature information.

---

## Phase 4: User Story 2 - Existing User Returns to Updated Homepage (Priority: P2)

**Goal**: Logged-in users see updated content that reflects current capabilities

**Independent Test**: Log in and view home page. Verify personalized welcome message displays correctly and "Go to Dashboard" button works.

### Implementation for User Story 2

- [ ] T014 [US2] Verify logged-in user greeting logic works correctly in `frontend/components/landing/hero-section.tsx` (lines ~139-141)
- [ ] T015 [US2] Test "Go to Dashboard" button navigation for logged-in users in `frontend/components/landing/hero-section.tsx` (lines ~155-164)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. New and existing users both see accurate content.

---

## Phase 5: User Story 3 - Mobile User Experiences Responsive Feature Showcase (Priority: P3)

**Goal**: Mobile users experience fully responsive feature showcase with proper readability

**Independent Test**: View page on mobile viewport (320px - 768px). Verify all 6 feature cards stack vertically, are fully readable, and animations are smooth.

### Implementation for User Story 3

- [ ] T016 [P] [US3] Verify responsive grid classes work correctly for mobile in `frontend/components/landing/hero-section.tsx` (line ~197)
- [ ] T017 [P] [US3] Verify badge is readable on mobile with existing `text-xs sm:text-sm` classes in `frontend/components/landing/hero-section.tsx` (line ~120)
- [ ] T018 [P] [US3] Verify feature cards are readable on mobile with existing padding classes in `frontend/components/landing/hero-section.tsx` (line ~202)

**Checkpoint**: All user stories should now be independently functional. Mobile responsiveness maintained across all updates.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and quality checks

- [X] T019 [P] Verify dark mode works correctly for all new feature cards in `frontend/components/landing/hero-section.tsx`
- [X] T020 [P] Verify light mode works correctly for all new feature cards in `frontend/components/landing/hero-section.tsx`
- [X] T021 [P] Verify all hover effects (`group-hover:scale-110`) work on new feature cards in `frontend/components/landing/hero-section.tsx`
- [X] T022 [P] Verify animations are smooth with 6 cards using `staggerContainer` variant in `frontend/components/landing/hero-section.tsx`
- [X] T023 [P] Run verification checklist from `specs/014-upgrade-home-page/research.md` (lines ~215-223)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1) is the MVP - should be completed first
  - User Story 2 (P2) can be tested independently after US1
  - User Story 3 (P3) validates responsive design after content updates
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories. This is the MVP.
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses same component as US1, tests logged-in state independently
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Validates responsive design of US1 changes

### Within Each User Story

**User Story 1**:
- T006, T007, T008, T009, T010 can run in parallel (different sections of the file)
- T011 must complete after T008, T009, T010 (depends on icon imports)
- T012, T013 can run in parallel with other tasks

**User Story 2**:
- T014, T015 are independent verification tasks

**User Story 3**:
- T016, T017, T018 are independent verification tasks

### Parallel Opportunities

- All Setup tasks marked [P] in Phase 1 can run in parallel
- All icon imports (T008, T009, T010) can run in parallel
- All verification tasks in Polish phase marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch icon imports together:
Task T008: "Add Bot icon import from lucide-react for AI Chatbot card"
Task T009: "Add Search icon import from lucide-react for Semantic Search card"
Task T010: "Add Languages icon import from lucide-react for Bilingual Support card"

# After icons are imported, update the feature cards:
Task T011: "Replace existing 3 feature cards with 6 new feature cards"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently by viewing home page logged out
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- This is a content-only update - no new components, APIs, or data structures
- All changes are in `frontend/components/landing/hero-section.tsx`
- Existing animations and styling are preserved
- Tests are visual/manual - no automated tests for this feature
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
