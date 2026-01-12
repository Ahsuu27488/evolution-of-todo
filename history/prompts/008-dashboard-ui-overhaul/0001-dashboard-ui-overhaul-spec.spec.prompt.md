---
id: "0001"
title: "dashboard-ui-overhaul-spec"
stage: "spec"
date: "2026-01-10T00:00:00Z"
surface: cli
model: "claude-opus-4-5-20251101"
feature: "008-dashboard-ui-overhaul"
branch: "008-dashboard-ui-overhaul"
user: "ahsan"
command: "/sp.specify"
labels: [spec, dashboard, ui, glassmorphism]
links:
  spec: ../specs/008-dashboard-ui-overhaul/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
- specs/008-dashboard-ui-overhaul/spec.md
- specs/008-dashboard-ui-overhaul/checklists/requirements.md
tests: []
---

## Prompt

# Feature: Advanced Dashboard UI Overhaul & Feature Completion

## 1. Context & Objective
The backend (FastAPI) and Frontend logic (API Client, Zustand Store) currently support Advanced features (Recurring Tasks, Due Dates, Tags) and Intermediate features (Sort, Search, Filter). However, the current Dashboard UI (`dashboard-content.tsx`) is functionally incomplete and visually "basic."

**Objective:** Transform the Dashboard into a high-fidelity, "Glassmorphism" aesthetic that matches the **Hero/Landing Page** design, while implementing the missing UI controls for all Advanced features.

## 2. Design System & Aesthetics (Source of Truth)
**Reference File:** `app/page.tsx` (Hero Page) & `app/layout.tsx`
The agent must analyze the Hero page to extract the design tokens. The Dashboard must use:
* **Theme:** "Deep Space" Glassmorphism.
* **Backgrounds:** Rich gradients, blur effects (`backdrop-blur-md`), and semi-transparent card backgrounds (e.g., `bg-white/10` or `bg-black/20`).
* **Typography:** Match the Hero page font weights, tracking, and gradient text styles.
* **Animations:** Use Framer Motion (or existing animation utils) for staggered list entry and smooth state transitions (like the Hero page elements).

## 3. Functional Requirements

### A. Advanced Task Creation (Update `TaskForm`)
The current form only allows Title, Description, and Priority. It must be updated to include:
1.  **Due Date Picker:** A datetime-local input (styled) to save to `due_date`.
2.  **Tag Management:** A UI to add/remove tags (visual chips with colors) mapped to the `tags` array.
3.  **Recurrence Selector:** A dropdown/select menu for `recurrence_pattern` (Options: NONE, DAILY, WEEKLY, MONTHLY).

### B. Dashboard Toolbar (New Component)
Replace the basic header with a cohesive Toolbar containing:
1.  **Search Bar:** Real-time text input (debounced) connected to `api.searchTasks`.
2.  **Filter Controls:** * **Status Tabs:** (All / Pending / Completed).
    * **Priority Dropdown:** Filter by High/Medium/Low.
3.  **Sort Controls:** * Dropdown for Criteria: (Created Date, Due Date, Priority, Title).
    * Toggle Button: Ascending / Descending.

### C. Task Card Redesign (`TaskCard`)
Update the card component to:
* Match the Glassmorphism aesthetic (remove basic borders, use subtle shadows/glows).
* Display the **Due Date** (highlight red if overdue, orange if due soon).
* Render **Tags** as colored pills/badges.
* Show a **Recurrence Icon** if the task is repeating.

## 4. Technical Constraints
* **State Management:** Must use the existing `stores/ui-store.ts` for managing filter/sort state.
* **API Interactions:** Must use existing methods in `lib/api-client.ts`. Do not write new API fetchers; connect the UI to the existing ones.
* **Responsiveness:** The dashboard must remain fully responsive (Mobile/Desktop).

## 5. Acceptance Criteria
1.  The Dashboard looks visually identical in quality and theme to the Hero page.
2.  A user can create a task with a specific Due Date, Tags, and Weekly Recurrence.
3.  A user can sort the list by "Due Date" (Ascending) to see urgent tasks first.
4.  A user can filter to see only "High Priority" tasks.

## Response snapshot

Successfully created specification for Feature 008: Advanced Dashboard UI Overhaul.

**Created Files:**
1. `/specs/008-dashboard-ui-overhaul/spec.md` - Complete feature specification
2. `/specs/008-dashboard-ui-overhaul/checklists/requirements.md` - Quality validation checklist

**Specification Summary:**
- 4 User Stories with priorities (P1: Task Creation, Filtering | P2: Sorting, Visual Redesign)
- 16 Functional Requirements covering all UI components and behaviors
- 10 Measurable Success Criteria with specific metrics
- Comprehensive edge cases and assumptions documented

**Quality Validation:** All checklist items passed. No [NEEDS CLARIFICATION] markers required. Specification is ready for `/sp.plan` or `/sp.clarify`.

## Outcome

- ✅ Impact: Created comprehensive specification for dashboard UI overhaul, enabling implementation of advanced task management features with glassmorphism aesthetic
- 🧪 Tests: N/A (spec phase)
- 📁 Files: spec.md, checklists/requirements.md created
- 🔁 Next prompts: `/sp.plan` to generate implementation plan
- 🧠 Reflection: Successfully analyzed existing codebase (api-client.ts, ui-store.ts, globals.css, hero-section.tsx, task types) to verify all backend capabilities and design tokens are already in place

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All validation checks PASSED
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
