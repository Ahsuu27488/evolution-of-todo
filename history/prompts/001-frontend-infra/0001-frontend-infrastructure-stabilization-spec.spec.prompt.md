---
id: "0001"
title: "Frontend Infrastructure Stabilization Spec"
stage: "spec"
date: "2026-01-09"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "001-frontend-infra"
branch: "001-frontend-infra"
user: "ahsan"
command: "/sp.specify"
labels: ["frontend", "infrastructure", "api-client", "authentication"]
links:
  spec: "specs/001-frontend-infra/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-frontend-infra/spec.md
  - specs/001-frontend-infra/checklists/requirements.md
tests:
  - N/A (spec phase - no tests written yet)
---

## Prompt

Frontend Infrastructure Stabilization and Backend Integration

Refactor the frontend codebase to align with backend services and remove architectural inconsistencies.

Core Requirements:
1. **Consolidate API Clients**: Merge lib/api.ts and lib/api-client.ts into a single, robust lib/api-client.ts. Remove the duplicate file. Ensure the unified client uses the Result type pattern and ApiError classes.
2. **Fix Authentication Integration**:
   - Implement the missing /api/auth/token route OR adapt the client to retrieve the session JWT correctly from Better Auth.
   - Verify and fix middleware cookie names to match lib/auth.ts config.
   - Ensure the signout flow works (add endpoint or fix client method).
3. **Backend Synchronization**:
   - Update the Health Check path from /health to /api/health.
   - Remove unused userId parameters from API methods (the backend infers user from token).
4. **Cleanup**:
   - Remove console.log statements in production paths.
   - Move inline keyframe styles (CSS-in-JS) to globals.css.

Technical Constraints:
- Do NOT change backend code (Backend is the source of truth).
- Must pass strict TypeScript checks.
- API Client must auto-inject Auth headers.

## Response snapshot

Created feature specification for Frontend Infrastructure Stabilization (feature 001-frontend-infra). The specification includes:

1. **User Stories** (prioritized P1-P3):
   - P1: Reliable Task Synchronization - core value proposition
   - P2: Seamless Authentication Flow - gateway to all features
   - P3: Clear Error Communication - user trust and supportability

2. **Functional Requirements** (17 total):
   - API Client Consolidation (FR-001 to FR-005)
   - Authentication Integration (FR-006 to FR-010)
   - Backend Synchronization (FR-011 to FR-014)
   - Code Quality (FR-015 to FR-017)

3. **Success Criteria** (6 measurable outcomes):
   - Task operations complete within 3 seconds
   - Authentication flow 100% success rate
   - Zero TypeScript errors in strict mode
   - Zero console.log statements in production
   - E2E tests pass at 100%
   - No duplicate API clients

4. **Quality Validation**: All checklist items passed - spec is ready for planning phase.

## Outcome

- ✅ Impact: New feature branch and specification created
- 🧪 Tests: N/A (spec phase)
- 📁 Files: 2 files created (spec.md, requirements checklist)
- 🔁 Next prompts: Ready for `/sp.clarify` or `/sp.plan`
- 🧠 Reflection: Specification successfully framed technical infrastructure work in terms of user value (reliable task sync, seamless auth, clear errors) rather than implementation details. All requirements are testable and measurable.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All quality criteria met
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
