# Implementation Plan: Advanced Dashboard UI Overhaul

**Branch**: `008-dashboard-ui-overhaul` | **Date**: 2026-01-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-dashboard-ui-overhaul/spec.md`

## Summary

Transform the dashboard UI from basic functionality to a high-fidelity "Deep Space" glassmorphism interface matching the landing page aesthetic. Implement missing UI controls for advanced features: due dates, tags, recurrence patterns, search, filtering, and sorting.

**Primary Requirement**: Update `TaskForm`, create `DashboardToolbar`, enhance `TaskCard` to display all advanced task attributes with glassmorphism styling.

**Technical Approach**: Leverage existing backend capabilities (API already supports all features), use existing Zustand store for filter state, implement Framer Motion animations for staggered list entry, and reuse existing glassmorphism CSS utilities.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.13+ (backend - existing)
**Primary Dependencies**: Next.js 15.2.8, React 19.2.3, Framer Motion 12.24.7, TanStack Query 5.90.16, Zustand 5.0.9, Tailwind CSS 4.x
**Storage**: Neon Serverless PostgreSQL (existing, no changes)
**Testing**: Playwright 1.57.0 (existing), React Testing Library (if needed)
**Target Platform**: Web (Next.js App Router)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- Search updates within 500ms (debounced)
- Task list animations complete within 600ms
- Task creation in under 30 seconds
**Constraints**:
- Must use existing `ui-store.ts` for filter state
- Must use existing `api-client.ts` methods (no new API fetchers)
- Must match "Deep Space" glassmorphism aesthetic from hero page
- Must remain fully responsive (mobile/desktop)
**Scale/Scope**:
- ~5 new/modified components
- No backend changes required
- Single-user focus (Phase II)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate Status: ✅ PASSED

| Principle | Status | Notes |
|-----------|--------|-------|
| SDD Pipeline | ✅ PASS | Spec exists, no code written yet |
| Phase Isolation | ✅ PASS | Phase II feature, no Phase III+ features |
| Python 3.13+ | ✅ PASS | Backend uses Python 3.13+ (existing) |
| Context7 Mandate | ✅ PASS | Used for Next.js, Framer Motion, shadcn/ui docs |
| No Manual Coding | ✅ PASS | All code via Claude Code |
| Task References | ✅ PASS | Will add `[Task]: T-XXX` in implementation |

### Constitution Compliance Details

- **Spec-Driven Development**: Following `spec.md → plan.md → tasks.md → implementation` pipeline
- **Phase II Scope**: Only implementing UI for existing backend features. No Phase III AI features, no Phase IV K8s, no Phase V Dapr
- **Technology Stack**: Using constitution-approved stack (Next.js, FastAPI, SQLModel, Neon DB, Better Auth)
- **Reusability**: Creating reusable `TagInput` and `DueDatePicker` components

## Project Structure

### Documentation (this feature)

```text
specs/008-dashboard-ui-overhaul/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - Complete
├── data-model.md        # Phase 1 output - Complete
├── quickstart.md        # Phase 1 output - Complete
├── contracts/           # Phase 1 output - Complete
│   └── components.ts    # Component contracts
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
# Option 2: Web application (frontend + backend)
backend/
├── src/
│   ├── models/          # SQLModel models (existing, no changes)
│   ├── services/        # Business logic (existing, no changes)
│   └── api/             # FastAPI endpoints (existing, no changes)
└── tests/

frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx     # Dashboard page (existing, minor changes)
│   └── globals.css      # Glassmorphism utilities (existing, no changes)
├── components/
│   ├── dashboard/
│   │   ├── dashboard-content.tsx  [MODIFY] - Main layout
│   │   ├── dashboard-toolbar.tsx  [CREATE] - Search/filter/sort
│   │   └── sort-dropdown.tsx      [CREATE] - Sort selector
│   ├── tasks/
│   │   ├── task-form.tsx          [MODIFY] - Add fields
│   │   └── task-card.tsx          [MODIFY] - Display attributes
│   └── tags/
│       └── tag-input.tsx          [CREATE] - Tag management
├── lib/
│   ├── hooks/
│   │   ├── use-debounce.ts        [CREATE] - Search debounce
│   │   └── use-task-filters.ts    [CREATE] - Filter logic
│   ├── stores/
│   │   └── ui-store.ts            (existing, no changes)
│   ├── validations/
│   │   └── task.ts                [UPDATE] - Add field validations
│   └── utils/
│       └── tag-utils.ts           [CREATE] - Tag utilities
└── types/
    └── task.ts                    (existing, no changes)
```

**Structure Decision**: Web application (Option 2). The project has separate `frontend/` and `backend/` directories. This feature only modifies frontend components; backend remains unchanged.

## Complexity Tracking

> **No violations to justify.** All requirements align with Clean Architecture principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Research Complete ✅

**Output**: [research.md](research.md)

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| Framer Motion staggerChildren | Already in project, matches hero animations |
| Custom debounce hook | No additional dependencies, full control |
| Native datetime-local input | Browser support, zero dependencies |
| Existing ui-store for filters | Already implemented with persistence |
| Existing api-client methods | All endpoints exist, zero backend changes |

## Phase 1: Design Complete ✅

### Data Model

**Output**: [data-model.md](data-model.md)

**Entities**:
- `Task`: Core todo entity with advanced attributes
- `Tag`: Category labels with colors
- `FilterState`: UI filter/sort configuration

### Component Contracts

**Output**: [contracts/components.ts](contracts/components.ts)

**New Components**:
1. `DashboardToolbar` - Search, filter, sort controls
2. `TagInput` - Add/remove colored tags
3. `DueDatePicker` - Styled datetime input
4. `SortDropdown` - Sort criterion selector

**Modified Components**:
1. `TaskForm` - Add due_date, tags, recurrence_pattern fields
2. `TaskCard` - Display new attributes with styling
3. `DashboardContent` - Integrate new toolbar

### Quickstart Guide

**Output**: [quickstart.md](quickstart.md)

**Development Commands**:
```bash
cd frontend && npm run dev
# Access at http://localhost:3000/dashboard
```

## Phase 2: Implementation (Next - via /sp.tasks)

The following components will be created/modified in implementation phase:

### New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `DashboardToolbar` | `components/dashboard/` | Search, status tabs, priority filter, sort controls |
| `TagInput` | `components/tags/` | Add/remove colored tag chips |
| `DueDatePicker` | `components/tasks/` | Styled datetime-local input |
| `SortDropdown` | `components/dashboard/` | Sort criterion with direction toggle |

### Modified Components

| Component | Changes |
|-----------|---------|
| `TaskForm` | Add due_date, tags, recurrence_pattern fields |
| `TaskCard` | Display due date, tags, recurrence icon with proper styling |
| `DashboardContent` | Replace header with `DashboardToolbar` |

### New Hooks

| Hook | Purpose |
|------|---------|
| `useDebounce` | Debounce search input (300ms delay) |
| `useTaskFilters` | Compose filter/sort logic with API calls |

### New Utilities

| Utility | Purpose |
|---------|---------|
| `tag-utils.ts` | Color generation, tag validation |

## Constitution Check (Post-Design)

**Status**: ✅ STILL PASSED

No violations introduced during design phase. All decisions align with:
- Clean Architecture (clear separation, existing patterns)
- Stateless Services (no in-memory state between requests)
- Cloud-Native Readiness (design scales horizontally)
- Smallest Viable Diff (only changing what's necessary)

## Dependencies

### Internal

| Dependency | Type | Description |
|------------|------|-------------|
| `lib/stores/ui-store.ts` | Store | Filter/sort state management |
| `lib/api-client.ts` | API | All task CRUD and search methods |
| `types/task.ts` | Types | TypeScript interfaces |
| `lib/animations.ts` | Animation | Framer Motion variants |
| `app/globals.css` | Styles | Glassmorphism utilities |

### External (Verified Versions)

| Package | Version | Purpose |
|---------|---------|---------|
| next | 15.2.8 | React framework |
| framer-motion | 12.24.7 | Animations |
| @tanstack/react-query | 5.90.16 | Server state |
| zustand | 5.0.9 | Client state |
| react-hook-form | 7.69.0 | Form handling |
| zod | 4.2.1 | Validation |

## Success Criteria Mapping

| Spec SC | Implementation |
|---------|----------------|
| SC-001: Create task in <30s | Optimistic form with pre-filled defaults |
| SC-002: Search updates in <500ms | 300ms debounce + TanStack Query cache |
| SC-003: Visual match to hero | Reuse glass classes, variants, animations |
| SC-004: Attributes visible at glance | Task card shows all fields without expansion |
| SC-005: Filter/sort in <5s | One-click controls with immediate feedback |
| SC-006: Animations in <600ms | Stagger variants with optimized timing |
| SC-007: Mobile responsive | Tailwind responsive classes, stacked layout |
| SC-008: Overdue visually distinct | Red glow + "Overdue:" prefix |
| SC-009: Inline validation | react-hook-form + zod error display |
| SC-010: Filter persistence | Zustand persist middleware (existing) |

## Out of Scope (Explicitly Excluded)

1. Backend API changes - all endpoints exist
2. Authentication flow changes
3. Phase III AI features (voice input, ai_summary, embedding_id)
4. Task edit modal changes (beyond supporting new fields)
5. Bulk operations (multi-select, bulk delete)
6. Calendar view for tasks
7. Task sharing or collaboration
8. Advanced recurrence (beyond DAILY/WEEKLY/MONTHLY)

---

**Next Command**: `/sp.tasks` to generate implementation tasks.
