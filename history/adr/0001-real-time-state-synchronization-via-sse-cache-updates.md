# ADR-0001: Real-Time State Synchronization via SSE Cache Updates

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-02-07
- **Feature:** 013-ai-chat-ui-redesign
- **Context:** Phase III AI Chatbot needs real-time task state synchronization when AI performs actions (create, complete, update tasks) without page refresh

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines state synchronization pattern for all AI-triggered actions
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Polling, SSE with refetch, dedicated sync endpoint evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects chat UI, dashboard components, cache layer, and SSE parsing
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **TanStack Query's `setQueryData()` for optimistic cache updates** triggered by SSE `tool_result` events. When the AI completes a tool call (add_task, complete_task, update_task, delete_task), the frontend parses the SSE event and immediately updates the TanStack Query cache, followed by a background `invalidateQueries()` to ensure consistency.

**Components of this decision cluster:**
- **SSE Event Parsing**: Extend existing SSE parser to handle `tool_result` events
- **Cache Update Strategy**: Use `queryClient.setQueryData()` for immediate updates (500ms requirement)
- **Background Refresh**: Use `queryClient.invalidateQueries()` after optimistic update
- **State Coordination**: New Zustand store (`task-events.ts`) for cross-component communication

**Implementation Pattern:**
```typescript
// In SSE event handler for tool_result
if (tool === 'complete_task' && output.success) {
  const taskId = output.data.id
  queryClient.setQueryData(['tasks', taskId], (old) => ({
    ...old,
    completed: true,
  }))
  queryClient.invalidateQueries(['tasks']) // Background refresh
}
```

## Consequences

### Positive

1. **No Backend Changes**: Leverages existing SSE infrastructure; no new API endpoints required
2. **Real-Time UX**: Task updates appear instantly (<500ms per SC-001) without page refresh
3. **Optimistic UI**: Users see immediate feedback even before backend confirmation
4. **Cache Consistency**: Background invalidateQueries ensures eventual consistency
5. **Scalable Pattern**: Same approach works for all AI tool calls (create, complete, update, delete)
6. **Celebration Triggers**: Direct cache updates enable celebration animation triggering on task completion

### Negative

1. **Cache Complexity**: Requires careful cache key management to avoid stale data
2. **Conflict Resolution**: Concurrent user/AI edits resolved by "last write wins" (backend timestamp)
3. **Debugging Difficulty**: Cache updates invisible in Network tab; requires React Query DevTools
4. **Memory Overhead**: Keeping task data in multiple cache locations (detail + list queries)
5. **Rollback Risk**: If optimistic update fails, need manual cache rollback mechanism
6. **Testing Complexity**: SSE event mocking required for unit/integration tests

## Alternatives Considered

### Alternative A: Dedicated Task Sync SSE Endpoint
**Description:** Create new SSE endpoint (`/api/tasks/stream`) that broadcasts all task changes, not just AI-triggered ones.

**Why Rejected:**
- Duplicates existing functionality (SSE chat stream already contains tool results)
- Adds backend complexity (new endpoint, event broadcasting logic)
- Over-engineering for current requirement (only AI actions need real-time sync)

### Alternative B: Polling-Based Cache Invalidation
**Description:** Frontend polls task list every 2-5 seconds to check for changes.

**Why Rejected:**
- Fails SC-001 (500ms requirement) - polling interval too long for "instant" feel
- Unnecessary server load from repeated requests
- Battery drain on mobile devices
- Poor UX during network latency

### Alternative C: `invalidateQueries()` Only (No Optimistic Updates)
**Description:** Skip `setQueryData()` and only call `invalidateQueries()` on SSE events, triggering refetch.

**Why Rejected:**
- Adds network latency (refetch delay before UI updates)
- Slower than 500ms target on poor connections
- Flickering loading states during refetch
- Worse perceived performance than optimistic updates

### Alternative D: WebSocket-Based Real-Time Sync
**Description:** Replace SSE with WebSocket for bidirectional real-time communication.

**Why Rejected:**
- Over-engineering for unidirectional updates (server → client sufficient)
- WebSocket connection management adds complexity (reconnection, heartbeat)
- SSE already established in Phase III; switching would be significant work
- WebSocket stateful nature complicates serverless deployment

### Alternative E: Browser BroadcastChannel for Cross-Tab Sync
**Description:** Use BroadcastChannel API to sync task changes across browser tabs only.

**Why Rejected:**
- Doesn't solve single-tab real-time updates (AI action → dashboard)
- Limited to same-browser sync (no cross-device capability)
- Edge Case 7 already documents storage events for cross-tab sync
- Insufficient for primary use case

## References

- Feature Spec: `/specs/013-ai-chat-ui-redesign/spec.md` (User Story 1: Real-Time Task State Synchronization)
- Implementation Plan: `/specs/013-ai-chat-ui-redesign/plan.md` (Research: TanStack Query Cache Updates)
- Data Model: `/specs/013-ai-chat-ui-redesign/data-model.md` (State Management Contracts)
- Contracts: `/specs/013-ai-chat-ui-redesign/contracts/frontend.ts` (SSE Event Extensions)
- Clarification Session: `/specs/013-ai-chat-ui-redesign/spec.md` (Session 2025-02-07)
- Evaluator Evidence: `/history/prompts/013-ai-chat-ui-redesign/0002-sse-stream-cache-update.spec.prompt.md`

## Implementation Checklist

- [ ] Extend SSE parser to handle `tool_result` events in `lib/utils/sse.ts`
- [ ] Create `lib/stores/task-events.ts` Zustand store for task mutation events
- [ ] Implement `queryClient.setQueryData()` calls in SSE event handler
- [ ] Add background `invalidateQueries()` after optimistic updates
- [ ] Integrate celebration animation trigger for task completion
- [ ] Add themed toast notifications for AI-triggered actions
- [ ] Write unit tests for SSE event parsing
- [ ] Write integration tests for cache updates
- [ ] Document cache key patterns for task queries
