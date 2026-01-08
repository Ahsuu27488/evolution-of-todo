# ADR-001: Command Center Foundation Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-06
- **Feature:** 007-phase2-chronos-webapp
- **Context:** Phase II "Chronos" Professional Web App - Designing the Command Center UI component as a foundation for Phase III voice integration

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines the UI foundation for voice input in Phase III
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Text-only, Modal-only, or Separate page options considered
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects routing, state management, API design, and Phase III continuity
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Implement a **Command Center** as a persistent UI component in the dashboard that provides:

1. **Phase II (Current)**: Text-based natural language command input with basic NLP parsing for task creation
2. **Phase III (Future)**: Extensible foundation for voice input via Web Speech API without UI restructuring

**Component Architecture**:
- **Location**: Fixed at bottom of dashboard page (above mobile navigation, below task list)
- **Components**:
  - `command-center/index.tsx` - Main bar component with glassmorphism styling
  - `command-center/command-parser.ts` - Basic NLP parser for Phase II (regex-based pattern matching)
  - `placeholder-mic-button.tsx` - Disabled microphone icon (visual only, activated in Phase III)
- **API Endpoint**: `POST /api/command` - Processes natural language commands and returns structured responses
- **State Management**: Zustand store for command history and input state
- **Keyboard Shortcut**: `Cmd+K` / `Ctrl+K` to focus Command Center

**Phase II Command Patterns** (supported via regex parsing):
- "Add task [title]" → Creates task with title
- "Add [title] due [date]" → Creates task with due date
- "Add [title] high priority" → Creates task with priority
- "Complete task [id]" → Marks task complete
- "Show [pending|completed|all] tasks" → Filters task list

**Phase III Extension Points** (reserved, not implemented):
- `placeholder-mic-button.tsx` → Replace with `voice-input-button.tsx` (Web Speech API)
- `command-parser.ts` → Extend or replace with OpenAI Agents SDK integration
- `/api/command` endpoint → Route to MCP tools for agent execution

## Consequences

### Positive

1. **Phase III Continuity**: UI foundation exists for voice input—no major restructuring needed when adding Web Speech API
2. **User Experience**: Natural language commands provide power-user alternative to form-based task creation
3. **Keyboard Accessibility**: `Cmd+K` shortcut aligns with modern app patterns (Linear, Slack, Raycast)
4. **Single Endpoint**: `/api/command` provides unified interface for both text and future voice commands
5. **Visual Consistency**: Command Center matches Deep Space Glassmorphism theme, maintains design cohesion
6. **Progressive Enhancement**: Phase II users get basic NLP; Phase III adds voice without breaking existing functionality

### Negative

1. **Complexity**: Adds NLP parsing logic that increases frontend bundle size and maintenance burden
2. **Ambiguity Handling**: Regex-based parsing has limited understanding—users may encounter "command not understood" errors
3. **Testing Surface**: Command parsing requires comprehensive test coverage for edge cases (typos, ambiguous phrasing)
4. **API Duplication**: `/api/command` endpoint duplicates some CRUD functionality (create, update, complete)
5. **Mobile Considerations**: Fixed position at bottom requires responsive design care to avoid obscuring content on small screens
6. **Placeholder UI**: Disabled microphone button may confuse users who expect voice functionality

## Alternatives Considered

### Alternative A: Text-Only Dashboard (No Command Center)
**Description**: Skip natural language input entirely; use only form-based task creation modal.

**Why Rejected**:
- Loses Phase III continuity—would need significant UI changes to add voice input later
- Poor power-user experience; forms feel slow for frequent task creation
- Misses opportunity to demonstrate "AI-ready" architecture to judges

### Alternative B: Modal Command Palette (Cmd+K Triggered Only)
**Description**: Command Center appears only as a modal overlay when keyboard shortcut is pressed (similar to Cmd+K in VS Code).

**Why Rejected**:
- Less discoverability—users may not know the feature exists
- Modal interrupts workflow; persistent bar is always visible and inviting
- Harder to extend for voice input in Phase III (modal vs. inline recording)

### Alternative C: Separate Command Page
**Description**: Dedicated page (`/command`) for natural language task management, separate from dashboard.

**Why Rejected**:
- Breaks workflow—users must navigate away from task list to use commands
- Voice recording in Phase III would be awkward on a separate page
- Doesn't align with modern app patterns (command palette should be context-aware)

### Alternative D: External AI Service Integration (Phase II)
**Description**: Call OpenAI API directly from Command Center for GPT-powered parsing in Phase II.

**Why Rejected**:
- Violates Phase II constraints (OpenAI Agents SDK is Phase III feature per constitution)
- Adds API cost and latency for basic command parsing
- Over-engineering for "add task" commands that regex can handle

### Alternative E: No Placeholder, Build Voice in Phase III
**Description**: Don't include Command Center at all in Phase II; build entire feature (text + voice) in Phase III.

**Why Rejected**:
- Loses opportunity to showcase architectural foresight (AI-ready design)
- Phase III already has significant scope (MCP, Agents SDK)—adding UI foundation increases risk
- User Story 9 ("Command Center with keyboard shortcuts") is a Phase II requirement per spec

## References

- Feature Spec: `/specs/007-phase2-chronos-webapp/spec.md` (User Story 9: FR-47 to FR-52)
- Implementation Plan: `/specs/007-phase2-chronos-webapp/plan.md` (Section: Phase 2.6 - Command Center)
- Research Notes: `/specs/007-phase2-chronos-webapp/research.md` (Form Handling: react-hook-form + zod)
- Data Model: `/specs/007-phase2-chronos-webapp/data-model.md` (AI-ready fields for Phase III continuity)
- API Contract: `/specs/007-phase2-chronos-webapp/contracts/backend-api.yaml` (POST /api/command endpoint)
- Evaluator Evidence: `/history/prompts/007-phase2-chronos-webapp/0002-phase-ii-chronos-planning.plan.prompt.md`

## Implementation Checklist

- [ ] Create `components/command-center/index.tsx` with glassmorphism styling
- [ ] Create `components/command-center/command-parser.ts` with regex-based NLP
- [ ] Create `components/command-center/placeholder-mic-button.tsx` (disabled, visual only)
- [ ] Add `Cmd+K` / `Ctrl+K` keyboard shortcut listener
- [ ] Implement Zustand store for command state
- [ ] Create `POST /api/command` endpoint in FastAPI backend
- [ ] Add command history UI (dropdown with recent commands)
- [ ] Write unit tests for command parser patterns
- [ ] Add E2E test for command-based task creation
- [ ] Document Phase III extension points in code comments
