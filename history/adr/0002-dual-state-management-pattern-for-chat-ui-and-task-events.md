# ADR-0002: Dual State Management Pattern for Chat UI and Task Events

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-02-07
- **Feature:** 013-ai-chat-ui-redesign
- **Context:** Phase III AI Chatbot requires state management for both chat UI (panel open/close, messages) AND task mutation events (AI actions updating dashboard)

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Establishes state management pattern for all AI-triggered actions across components
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - All Zustand, all Context, Jotai, signals evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects chat components, dashboard, and cache coordination layer
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **React Context for chat UI state** and **Zustand for task mutation events**, creating a dual state management pattern that separates concerns while enabling cross-component communication.

**Components of this decision cluster:**
- **Chat UI State (React Context)**: Panel open/close, messages list, streaming status, conversation ID
- **Task Events (Zustand)**: Last AI-triggered task mutation, timestamp, task data snapshot
- **Coordination Layer**: Chat Context triggers Zustand updates on SSE tool_result events
- **Persistence Strategy**: Context state is ephemeral (clears on close), Zustand persists across unmounts

**State Split Rationale:**
```typescript
// React Context (chat-store.ts) - UI state only
interface ChatUIState {
  isOpen: boolean
  messages: Message[]
  isStreaming: boolean
  currentConversationId: string | null
  triggerTaskUpdate: (taskId: number, mutation: TaskMutation) => void
}

// Zustand (task-events.ts) - Cross-cutting events
interface TaskEventStore {
  lastMutation: TaskMutation | null
  setTaskMutation: (mutation: TaskMutation) => void
  clearMutation: () => void
}
```

## Consequences

### Positive

1. **SSR Hydration Safety**: React Context prevents SSR hydration issues that plagued earlier Zustand usage
2. **Separation of Concerns**: UI state (ephemeral) separated from domain events (persistent)
3. **Cross-Component Communication**: Zustand enables dashboard to listen for task events without prop drilling
4. **Backward Compatibility**: Existing chat Context remains unchanged; new Zustand store is additive
5. **Testability**: Each store can be tested independently; no complex setup for cross-store tests
6. **Performance**: Zustand's selector-based reactivity prevents unnecessary re-renders in dashboard components

### Negative

1. **Two State Libraries**: Adds dependency footprint (Zustand ~1KB gzipped)
2. **Learning Curve**: Developers must understand when to use Context vs Zustand
3. **State Coordination Complexity**: Need manual trigger calls from Context to Zustand
4. **Debugging Overhead**: Two DevTools panels needed for full state visibility
5. **Potential Duplication**: Risk of storing similar data in both stores if not careful
6. **Migration Path**: If pattern proves problematic, migration to single library requires significant refactoring

## Alternatives Considered

### Alternative A: Zustand for All State
**Description:** Migrate chat UI state from React Context to Zustand, unifying all state in one library.

**Why Rejected:**
- **High Risk**: Previous Zustand usage caused SSR hydration issues (documented in CLAUDE.md)
- **Migration Cost**: Requires rewriting existing chat-store.ts and all consuming components
- **Limited Benefit**: Chat UI state doesn't need cross-component persistence (panel-only)

### Alternative B: React Context for All State
**Description:** Add task events to existing React Context instead of introducing Zustand.

**Why Rejected:**
- **Prop Drilling**: Dashboard components would need to consume entire Chat Context to access task events
- **Unnecessary Re-renders**: Context changes trigger all consumers to re-render, including non-chat components
- **Tight Coupling**: Dashboard becomes coupled to chat-specific state structure

### Alternative C: Jotai for Atomic State Management
**Description:** Use Jotai atoms for both chat UI and task events, leveraging atomic state pattern.

**Why Rejected:**
- **Additional Dependency**: Team has no experience with Jotai; learning curve
- **Overkill**: Atomic state pattern provides benefits not needed for current use case
- **Bundle Size**: Jotai similar size to Zustand but with unfamiliar API

### Alternative D: TanStack Query for Task Events
**Description:** Store task mutation events as TanStack Query data (e.g., `/api/task-events` endpoint).

**Why Rejected:**
- **Fake API**: No real backend endpoint; would be mocking API for state management
- **Cache Pollution**: Task events are transient, not meant to be cached like API data
- **Complexity**: Requires query key management and invalidation for ephemeral state

### Alternative E: Event Bus Pattern (Custom EventEmitter)
**Description:** Implement custom event bus for task mutations, using browser events or custom emitter.

**Why Rejected:**
- **Reinventing Wheel**: Zustand provides same functionality with better DX
- **Type Safety**: Custom event bus requires careful TypeScript typing
- **Debugging**: Event buses harder to debug than state store DevTools

## References

- Feature Spec: `/specs/013-ai-chat-ui-redesign/spec.md` (User Story 1: Real-Time Task State Synchronization)
- Implementation Plan: `/specs/013-ai-chat-ui-redesign/plan.md` (Research: State Management Approach)
- Data Model: `/specs/013-ai-chat-ui-redesign/data-model.md` (State Management Contracts)
- Frontend Context: `/frontend/CLAUDE.md` (React Context over Zustand rationale)
- Related ADRs: ADR-0001 (Real-Time State Synchronization via SSE Cache Updates)
- Evaluator Evidence: `/history/prompts/013-ai-chat-ui-redesign/0003-ui-redesign-implementation-plan.plan.prompt.md`

## Implementation Checklist

- [ ] Create `lib/stores/task-events.ts` Zustand store with TaskMutation interface
- [ ] Add `triggerTaskUpdate()` action to `lib/stores/chat-store.ts` Context
- [ ] Implement Zustand → Context coordination in SSE event handler
- [ ] Create dashboard hook `useTaskEvents()` to listen for mutations
- [ ] Add celebration animation trigger based on task event type
- [ ] Write tests for task event store mutations
- [ ] Write tests for Context → Zustand coordination
- [ ] Update CLAUDE.md to document dual pattern rationale
