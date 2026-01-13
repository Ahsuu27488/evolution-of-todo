# Tasks: Light Mode Theme

**Input**: Design documents from `/specs/009-light-mode-theme/`
**Prerequisites**: plan.md, spec.md (3 user stories P1-P3), research.md, data-model.md, contracts/css-variables.md, quickstart.md

**Tests**: Visual testing only - no automated test tasks included (spec defines visual criteria)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/app/`, `frontend/components/`
- **Single file modification**: `frontend/app/globals.css` only

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify prerequisites and understand existing structure

- [X] T001 Verify next-themes v0.4.6 is installed in frontend/package.json
- [X] T002 Verify ThemeProvider is configured with `attribute="class"` in frontend/app/providers.tsx
- [X] T003 Verify theme toggle UI exists in frontend/components/layout/theme-toggle.tsx

**Checkpoint**: Prerequisites verified - ready to implement light mode CSS ✅

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core CSS infrastructure that MUST be in place before any visual testing

**⚠️ CRITICAL**: No visual testing can begin until this phase is complete

- [X] T004 Read current globals.css structure to understand dark mode implementation in frontend/app/globals.css
- [X] T005 Identify exact line numbers for `.dark` selector insertion point in frontend/app/globals.css

**Checkpoint**: CSS structure understood - ready to add `.light` selector ✅

---

## Phase 3: User Story 1 - Theme Selection (Priority: P1) 🎯 MVP

**Goal**: Enable users to switch between Light, Dark, and System themes with functional light mode CSS variables

**Independent Test**: Click Sun icon → verify UI switches to light mode with all colors inverted appropriately. Reload page → verify light mode persists. Click Monitor icon → verify system theme detection works.

### Implementation for User Story 1

- [X] T006 [US1] Add `.light` selector with base color variables (background, foreground) in frontend/app/globals.css after `.dark` block (lines ~168-195)
- [X] T007 [P] [US1] Add `.light` selector with surface color variables (card, popover, muted) in frontend/app/globals.css
- [X] T008 [P] [US1] Add `.light` selector with accent color variables (primary, secondary, accent, destructive) in frontend/app/globals.css
- [X] T009 [P] [US1] Add `.light` selector with border/input variables (border, input, ring) in frontend/app/globals.css
- [X] T010 [P] [US1] Add `.light` selector with chart color variables (chart-1 through chart-5) in frontend/app/globals.css
- [X] T011 [P] [US1] Add `.light` selector with sidebar color variables (sidebar-*) in frontend/app/globals.css
- [X] T012 [US1] Add `.light body` background gradient with reduced opacity orbs in frontend/app/globals.css @layer base section

**Checkpoint**: At this point, User Story 1 should be fully functional - clicking Sun icon switches to light mode with proper CSS variables ✅

---

## Phase 4: User Story 2 - Light Mode Visual Consistency (Priority: P2)

**Goal**: Ensure all UI elements maintain visual hierarchy with WCAG AA contrast ratios and brand-consistent accent colors

**Independent Test**: Activate light mode and verify task cards have white backgrounds with dark text, primary buttons show cyan (unchanged), all text is readable with proper contrast

### Implementation for User Story 2

> **NOTE**: All components automatically adapt via CSS variables. This phase validates the CSS variable definitions from US1 are correct and complete.

- [X] T013 [P] [US2] Validate base color contrast ratios (background/foreground) meet WCAG AA 4.5:1 in contracts/css-variables.md
- [X] T014 [P] [US2] Validate accent colors (cyan, purple) remain unchanged between themes in contracts/css-variables.md
- [X] T015 [P] [US2] Validate destructive color (red) has sufficient contrast in light mode in contracts/css-variables.md
- [X] T016 [US2] Visual test: Verify button components render correctly in light mode with proper contrast
- [X] T017 [US2] Visual test: Verify card components display with white backgrounds and dark text in light mode
- [X] T018 [US2] Visual test: Verify input components show appropriate border visibility in light mode

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - light mode is functional and visually consistent ✅

---

## Phase 5: User Story 3 - Component-Specific Light Mode Adaptations (Priority: P3)

**Goal**: Adapt glassmorphism effects and glow effects for light mode with appropriate shadows and borders

**Independent Test**: Examine modal dialogs and verify glass effect uses light semi-transparent background with darker border. Verify glow effects use darker shadows for visibility against light backgrounds.

### Implementation for User Story 3

- [X] T019 [US3] Add `.light .glass` utility with white semi-transparent background in frontend/app/globals.css @layer utilities section
- [X] T020 [P] [US3] Add `.light .glass-strong` utility with stronger white opacity in frontend/app/globals.css @layer utilities section
- [X] T021 [P] [US3] Add `.light .glass-modal` utility with near-solid white background in frontend/app/globals.css @layer utilities section
- [X] T022 [P] [US3] Add `.light .glow-cyan` utility with reduced opacity for visibility in frontend/app/globals.css @layer utilities section
- [X] T023 [P] [US3] Add `.light .glow-purple` utility with reduced opacity for visibility in frontend/app/globals.css @layer utilities section
- [X] T024 [US3] Visual test: Verify modal dialogs show proper glassmorphism in light mode
- [X] T025 [US3] Visual test: Verify glow effects are visible but subtle in light mode
- [X] T026 [US3] Visual test: Verify hero section gradient orbs appear subtle against light background

**Checkpoint**: All user stories should now be independently functional - complete light mode theme with glassmorphism and glow adaptations ✅

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [X] T027 [P] Verify no hydration flash occurs on page load (test with devtools network throttling)
- [X] T028 [P] Verify theme switching completes in under 1 second (no page reload)
- [X] T029 [P] Verify all 40+ CSS variables have `.light` mode values defined per contracts/css-variables.md
- [X] T030 [P] Run quickstart.md testing checklist (14 verification points)
- [X] T031 Update this feature's spec.md status from "Draft" to "Complete"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification tasks can run immediately
- **Foundational (Phase 2)**: Depends on Setup - structure understanding required before CSS modifications
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): MUST complete first - defines core CSS variables
  - User Story 2 (P2): Depends on US1 - validates US1's CSS definitions
  - User Story 3 (P3): Depends on US1 - adds utility class variants to US1's foundation
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    Light Mode Tasks                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Setup (T001-T003)                                         │
│        │                                                    │
│        ▼                                                    │
│   Foundational (T004-T005)                                  │
│        │                                                    │
│        ▼                                                    │
│   ┌─────────────────────────────────────────────┐          │
│   │   US1: Theme Selection (T006-T012)         │          │
│   │   - Core CSS variables                      │          │
│   │   - Body background gradient                │          │
│   └─────────────┬───────────────────────────────┘          │
│                 │                                           │
│      ┌──────────┴──────────┐                               │
│      ▼                     ▼                               │
│ ┌─────────────┐      ┌──────────────┐                      │
│ │ US2: Visual │      │  US3: Glass  │                      │
│ │ Consistency │      │  & Glow      │                      │
│ │ (T013-T018) │      │  (T019-T026) │                      │
│ └─────────────┘      └──────────────┘                      │
│      │                     │                               │
│      └──────────┬──────────┘                               │
│                 ▼                                           │
│   Polish (T027-T031)                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Within Each User Story

- **US1**: Tasks T007-T011 can run in parallel (different variable groups)
- **US2**: Tasks T013-T015 can run in parallel (different validation aspects)
- **US3**: Tasks T020-T023 can run in parallel (different utility classes)

### Parallel Opportunities

- Setup phase: All tasks are independent verification - can conceptually run in parallel
- US1 variable definitions: T007-T011 add different variable categories to same file - can be done simultaneously if coordinated
- US2 validations: T013-T015 validate different aspects - can run in parallel
- US3 utilities: T020-T023 add different utility classes - can run in parallel

---

## Parallel Example: User Story 1

```bash
# Tasks T007-T011 add different variable categories to the same selector block.
# They can be executed together by a single agent making all changes at once:

Task: "Add .light selector with base, surface, accent, border/input, chart, and sidebar color variables in frontend/app/globals.css"

# This consolidates 6 parallel tasks into one coordinated change.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup - Verify prerequisites (5 minutes)
2. Complete Phase 2: Foundational - Understand CSS structure (5 minutes)
3. Complete Phase 3: User Story 1 - Add core `.light` CSS variables (15 minutes)
4. **STOP and VALIDATE**: Test theme toggle, verify light mode works
5. **MVP COMPLETE**: Light mode is functional

### Incremental Delivery

1. MVP (US1): Core light mode CSS variables → Test independently → Feature complete for basic use
2. Add US2: Validate contrast ratios and brand consistency → Production-ready
3. Add US3: Glassmorphism and glow adaptations → Polish complete

### Single-File Implementation Strategy

This feature is unique in that **only one file** needs modification:

```
┌─────────────────────────────────────────────────────────────┐
│              Single File: frontend/app/globals.css          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Line ~132-166:  .dark selector (EXISTS - reference only)   │
│  Line ~168-220:  .light selector (ADD - US1 tasks)          │
│  Line ~172-185:  @layer base body (MODIFY - add .light body)│
│  Line ~194-290:  @layer utilities (ADD - US3 tasks)         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight**: Because all components use CSS variables, adding the `.light` selector automatically enables light mode across the entire application - zero component code changes required.

---

## Notes

- [P] tasks = different variable categories, no dependencies within the task group
- [Story] label maps task to specific user story for traceability
- US1 is the **only required implementation phase** - US2/US3 are validation and polish
- All changes are additive - no existing dark mode code is modified
- The `.dark` selector serves as a reference - `.light` mirrors its structure with inverted brightness values
- Brand colors (cyan, purple) remain **identical** between themes for brand consistency
- Tests are visual/manual - no automated tests defined for this UI-focused feature

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 31 |
| **Setup Phase** | 3 tasks (T001-T003) |
| **Foundational Phase** | 2 tasks (T004-T005) |
| **User Story 1 (P1)** | 7 tasks (T006-T012) |
| **User Story 2 (P2)** | 6 tasks (T013-T018) |
| **User Story 3 (P3)** | 8 tasks (T019-T026) |
| **Polish Phase** | 5 tasks (T027-T031) |
| **Parallel Opportunities** | 5 task groups |
| **Files Modified** | 1 file (frontend/app/globals.css) |
| **Suggested MVP** | US1 only (tasks T001-T012) |

**Format Validation**: ✅ ALL tasks follow the checklist format with checkbox, Task ID, Story labels where applicable, and file paths
