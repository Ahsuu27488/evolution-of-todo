# Implementation Plan: Loading States & User Profile Enhancement

**Branch**: `010-loading-states-user-profile` | **Date**: 2025-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-loading-states-user-profile/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature enhances the Phase II full-stack todo application with two primary improvements:
1. **Creative Loading States (P1)**: Implement a dual-ring spinner animation using neon cyan/purple colors for dashboard task loading and status tab switches
2. **User Profile Expansion (P2)**: Separate first and last name fields in the user model with inclusive validation (first name required, last name optional)
3. **Zero-Downtime Migration (P3)**: Multi-phase database migration preserving existing user data without service interruption

**Technical Approach**:
- Frontend: Create reusable `DualRingSpinner` component with CSS animations, integrate with TanStack Query loading states
- Backend: Extend User model with `first_name` and `last_name` columns, implement multi-phase migration strategy
- Migration: 4-phase approach (add columns → deploy backward-compatible code → background data migration → enforce constraints)

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**:
  - Backend: FastAPI 0.115+, SQLModel 0.014+, asyncpg 0.29+, alembic 1.13+
  - Frontend: Next.js 16+ (App Router), React 19+, Framer Motion 12+, Tailwind CSS v4, TanStack Query v5+
  - Auth: Better Auth (JWT), bcrypt 4.2+
**Storage**: Neon Serverless PostgreSQL (PostgreSQL 16+)
**Testing**:
  - Backend: pytest 8+, pytest-asyncio 0.23+, httpx 0.27+
  - Frontend: Vitest 2+, React Testing Library 14+, Playwright 1.45+
**Target Platform**: Linux server (backend), Modern browsers (Chrome 120+, Firefox 120+, Safari 17+, Edge 120+)
**Project Type**: Web application (full-stack monorepo)
**Performance Goals**:
  - Loading animation visible within 100ms of data fetch
  - Animation fade-out within 300ms of data arrival
  - Minimum 400ms display duration to prevent flash
  - Zero service interruption during migration
**Constraints**:
  - Must maintain backward compatibility with existing `name` field
  - Must support Unicode characters for international names
  - Must prevent XSS attacks in user input
  - Cannot use training data for external libraries - must use Context7 (Constitution §III.1)
**Scale/Scope**:
  - ~1000 existing users (legacy data migration)
  - 2 new database columns (first_name, last_name)
  - 1 new frontend component (DualRingSpinner)
  - 3 modified frontend components (signup form, header, dashboard content)
  - 5 modified backend endpoints (signup, signin, user profile, token, migration script)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Evaluation

**Phase Compliance** (Constitution §IV.2):
- ✅ Feature scoped to Phase II (Full-Stack Web) - No chatbot, Kubernetes, or cloud deployment concepts
- ✅ Uses approved Phase II stack: Next.js, FastAPI, SQLModel, Neon DB, Better Auth
- ✅ No Phase III+ features leaking (AI agents, MCP, Kafka, Dapr)

**SDD Workflow** (Constitution §I.1):
- ✅ Spec approved and clarified via `/sp.specify` and `/sp.clarify`
- ✅ All 21 functional requirements defined with acceptance criteria
- ✅ No code will be written without this plan and subsequent tasks

**Agent Behavior Rules** (Constitution §II.1):
- ✅ No manual coding - All code via Claude Code
- ✅ No feature invention - Only implementing what spec defines
- ✅ Context7 will be used as PRIMARY source for all library documentation (§III.1)
- ✅ Task IDs will be referenced in code comments

**Quality Principles** (Constitution §VI):
- ✅ Clean Architecture - Frontend/backend separation maintained
- ✅ Stateless Services - Backend remains stateless
- ✅ Security Standards - XSS prevention, JWT validation, user data isolation
- ✅ Error Handling - Explicit loading and error states defined

**Technology Constraints** (Constitution §V):
- ✅ Python 3.13+ will be used (backend already validated)
- ✅ UV package manager for backend dependencies
- ✅ Approved Phase II stack (FastAPI, Next.js, SQLModel, Neon, Better Auth)

**Gate Status**: ✅ **PASS** - All constitution requirements satisfied, no violations requiring justification

### Post-Design Re-Evaluation

*After Phase 1 design completion:*

**Architecture Decisions**:
- ✅ Dual-ring spinner uses pure CSS animations (no JS libraries) - minimal complexity
- ✅ Multi-phase migration uses alembic for schema versioning - industry best practice
- ✅ Name display computed in backend (display_name property) - maintains single source of truth
- ✅ Loading states integrated with existing TanStack Query - leverages current patterns

**Gate Status**: ✅ **PASS** - Design choices align with Clean Architecture and Smallest Viable Diff principles

## Project Structure

### Documentation (this feature)

```text
specs/010-loading-states-user-profile/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - Technical research and decisions
├── data-model.md        # Phase 1 output - Entity definitions and relationships
├── quickstart.md        # Phase 1 output - Setup and development instructions
├── contracts/           # Phase 1 output - API contracts and schemas
│   ├── openapi.yaml     # OpenAPI 3.1 spec for backend endpoints
│   └── user-schema.ts   # TypeScript interfaces for User entity
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
backend/                     # FastAPI backend (Phase II)
├── alembic/                 # Database migration scripts
│   ├── versions/
│   │   └── 010_add_first_last_name.py  # Multi-phase migration
│   └── env.py
├── src/
│   ├── models/
│   │   └── user.py          # Updated User model with first/last name
│   ├── routes/
│   │   ├── auth.py          # Updated signup/signin endpoints
│   │   └── users.py         # Updated profile endpoints
│   └── services/
│       └── migration.py     # Background migration service
└── tests/
    ├── integration/
    │   └── test_auth_flow.py  # Updated auth flow tests
    └── unit/
        └── test_user_model.py  # User model tests

frontend/                    # Next.js frontend (Phase II)
├── src/
│   ├── app/
│   │   ├── signup/
│   │   │   └── page.tsx     # Updated signup page with name fields
│   │   └── dashboard/
│   │       └── page.tsx     # Updated dashboard with loading states
│   ├── components/
│   │   ├── ui/
│   │   │   └── dual-ring-spinner.tsx  # NEW: Loading spinner component
│   │   ├── auth/
│   │   │   └── signup-form.tsx  # Updated with first/last name fields
│   │   ├── layout/
│   │   │   └── user-nav.tsx  # Updated to display first + last name
│   │   └── dashboard/
│   │       └── dashboard-content.tsx  # Updated with dual-ring spinner
│   └── lib/
│       └── types/
│           └── user.ts      # Updated User type with first/last name
└── tests/
    ├── integration/
    │   └── signup-flow.test.tsx  # Signup flow tests
    └── unit/
        └── dual-ring-spinner.test.tsx  # Spinner component tests
```

**Structure Decision**: Web application structure (Option 2) - This is a Phase II feature with existing frontend and backend directories. The structure maintains the established monorepo layout with clear separation between client and server code.

## Complexity Tracking

> **No violations requiring justification** - All changes align with existing architecture patterns

| N/A | N/A | N/A |
|-----|-----|-----|
