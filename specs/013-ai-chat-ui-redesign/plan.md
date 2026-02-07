# Implementation Plan: AI Chat UI Redesign

**Branch**: `013-ai-chat-ui-redesign` | **Date**: 2025-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-ai-chat-ui-redesign/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature delivers comprehensive UI/UX improvements for the Phase III AI Chatbot ("Chronos"). The primary goal is to achieve visual consistency with the dashboard's glassmorphism theme while enabling real-time task state synchronization when the AI performs actions.

Key improvements include:
1. **Real-Time Task Sync** - AI actions (create, complete, update tasks) update dashboard immediately via SSE cache updates
2. **FAB Location Control** - AI assistant FAB only visible on dashboard page
3. **Mobile-First Responsive Design** - Full-screen on mobile, modal on tablet, floating panel on desktop
4. **Streamlined Voice Recording** - No confirmation prompts, direct send to agent with stop button
5. **Loading Skeleton States** - YouTube-style shimmer skeletons for conversation loading
6. **Agent Introduction Screen** - Welcome screen with Chronos capabilities and example prompts
7. **Themed Toast Notifications** - Glassmorphism toasts for AI-triggered actions

**Technical Approach**: Pure frontend changes using existing TanStack Query, React Context, and SSE infrastructure. No backend modifications required.

## Technical Context

**Language/Version**: TypeScript (Next.js 15.2+ with App Router)
**Primary Dependencies**: React 19, TanStack Query v5, Framer Motion, Sonner (toasts), Next.js 15
**Storage**: N/A (frontend-only feature, uses existing backend SSE)
**Testing**: Vitest, React Testing Library
**Target Platform**: Web browsers supporting ES2020+, CSS backdrop-filter
**Project Type**: web (frontend modification to existing full-stack app)
**Performance Goals**:
- Task state changes visible within 500ms (SC-001)
- Layout adaptation within 100ms of resize (SC-002)
- Skeletons appear within 200ms of fetch initiation (SC-006)
- Toasts appear within 300ms of backend completion (SC-007)
**Constraints**:
- Minimum viewport width: 320px (iPhone SE)
- Touch targets: minimum 44px for mobile
- No backend changes allowed (reuse existing SSE infrastructure)
- Must maintain existing dashboard component patterns
**Scale/Scope**:
- ~9 chat components to modify/redesign
- 3 new components (skeletons, intro screen, themed toasts)
- FAB location change affects routing (providers.tsx)
- Responsive breakpoints: 640px, 1024px for layout changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Compliance Check

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Phase Scope (§IV.1)** | ✅ PASS | Feature is within Phase III scope (AI Chatbot UI improvements). No Phase IV/V features leak. |
| **No Future Phase Features** | ✅ PASS | Spec explicitly states "No new data entities" and "no backend API changes." |
| **Spec-Driven (§I.1)** | ✅ PASS | All work references spec.md user stories and functional requirements. |
| **Python 3.13+ (§V.1.1)** | N/A | Frontend-only feature (TypeScript/Next.js). No Python code changes. |

### Code Quality Standards (§VI)

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Clean Architecture** | ✅ PASS | Separation maintained: UI components, state management (React Context), API client layer. |
| **Stateless Services** | ✅ PASS | Frontend is stateless by design; state managed via React Context + TanStack Query cache. |
| **Smallest Viable Diff** | ✅ PASS | Only modifies chat UI components; no unrelated changes to other features. |
| **TypeScript Strict Mode** | ✅ PASS | All new/modified components use TypeScript strict mode. |
| **No Hardcoded Secrets** | ✅ PASS | No secrets added; uses existing auth token infrastructure. |

### Security Standards (§VI.3)

| Requirement | Status | Notes |
|-------------|--------|-------|
| **OWASP Top 10 Awareness** | ✅ PASS | No new XSS/injection vectors; uses existing React XSS protection. |
| **JWT Validation** | ✅ PASS | Uses existing getAuthToken() from lib/auth/token. |
| **User Data Isolation** | ✅ PASS | SSE stream already filtered by user_id; cache updates respect ownership. |

### Context7 Compliance (§III.1)

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Context7 for External Libraries** | ✅ PASS | Will query Context7 for: Next.js 15, Framer Motion, TanStack Query v5, Sonner API. |

**CONCLUSION**: All gates PASSED. Proceed to Phase 0 research.

---

## Project Structure

### Documentation (this feature)

```text
specs/013-ai-chat-ui-redesign/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Frontend structure (existing - will be modified)
frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx              # MODIFIED: Add ChatPanel (FAB only on dashboard)
│   ├── providers.tsx             # MODIFIED: Remove global ChatPanel
│   └── layout.tsx                # No changes needed
├── components/
│   ├── chat/
│   │   ├── chat-panel.tsx         # MODIFIED: Responsive layouts, intro screen
│   │   ├── chat-message.tsx      # MODIFIED: Glassmorphism styling
│   │   ├── chat-input.tsx         # MODIFIED: Consistent styling
│   │   ├── voice-recorder.tsx     # MODIFIED: Remove confirmation, add stop button
│   │   ├── task-card.tsx          # MODIFIED: Glassmorphism styling
│   │   ├── chat-skeleton.tsx      # NEW: Message loading skeletons
│   │   ├── agent-intro.tsx        # NEW: Welcome screen for Chronos
│   │   └── themed-toast.tsx       # NEW: Custom glassmorphism toasts
│   └── ui/
│       └── sonner.tsx             # MODIFIED: Custom toast styling
├── lib/
│   ├── api/
│   │   └── chat.ts                # MODIFIED: Add SSE tool call parsing
│   ├── stores/
│   │   └── chat-store.ts          # MODIFIED: Add cache update actions
│   └── utils/
│       └── sse.ts                 # MODIFIED: Add tool call event parser
└── hooks/
      └── use-chat.ts             # MODIFIED: Add tool call handler
```

**Structure Decision**: Option 2 (Web application) is selected. This is a frontend-only modification to the existing Phase III full-stack application. All changes occur within the `frontend/` directory, specifically targeting chat components and related state management.

---

## Phase 0: Research & Best Practices

### Research Tasks

1. **TanStack Query v5 Cache Updates from SSE**
   - **Question**: How to optimistically update TanStack Query cache from SSE events?
   - **Approach**: Query Context7 for `@tanstack/react-query` cache mutation patterns
   - **Deliverable**: Cache update strategy for task mutations from SSE tool_call events

2. **Framer Motion Responsive Layouts**
   - **Question**: How to implement smooth layout transitions between breakpoints?
   - **Approach**: Query Context7 for `framer-motion` layout animation patterns
   - **Deliverable**: Responsive panel layout variants (mobile/tablet/desktop)

3. **Sonner Custom Toast Styling**
   - **Question**: How to apply glassmorphism theme to Sonner toasts?
   - **Approach**: Query Context7 for `sonner` toast styling API
   - **Deliverable**: Custom toast component with glassmorphism theme

4. **Next.js 15 Client Components in App Router**
   - **Question**: How to conditionally render ChatPanel only on dashboard route?
   - **Approach**: Query Context7 for Next.js 15 App Router client component patterns
   - **Deliverable**: Route-aware ChatPanel rendering strategy

5. **React Context vs Zustand for Chat State**
   - **Question**: Should chat state remain in React Context or migrate to Zustand?
   - **Approach**: Evaluate existing `chat-store.ts` implementation and migration cost
   - **Deliverable**: Decision on state management approach (keep Context is likely)

---

## Research Output

### Research: TanStack Query Cache Updates from SSE

**Decision**: Use `queryClient.setQueryData()` for optimistic updates from SSE events.

**Rationale**:
- TanStack Query v5 provides `setQueryData()` for immediate cache updates
- SSE tool_call events contain task data that can be applied directly
- Avoids refetch delay while maintaining cache consistency
- Pattern: `queryClient.setQueryData(taskKeys.detail(taskId), (old) => ({ ...old, completed: true }))`

**Alternatives Considered**:
- **queryClient.invalidateQueries()**: Would trigger refetch, adds latency
- **queryClient.refetchQueries()**: Same as above, worse UX
- **Wait for next poll**: Not real-time enough (SC-001 requires 500ms)

**Implementation Pattern**:
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

---

### Research: Framer Motion Responsive Layouts

**Decision**: Use `useResponsive()` hook with breakpoint-specific variants.

**Rationale**:
- Framer Motion's `AnimatePresence` handles layout transitions smoothly
- Breakpoint-specific variants allow different layouts per screen size
- `layout="position"` prop enables smooth position animations
- Pattern: `variants={{ mobile: { ... }, tablet: { ... }, desktop: { ... } }}`

**Alternatives Considered**:
- **CSS media queries + conditional rendering**: Flicker during resize
- **Single responsive variant**: Complex nested ternaries in styles
- **Separate components**: Code duplication

**Implementation Pattern**:
```typescript
const variants = {
  mobile: { width: '100vw', height: '100vh', borderRadius: 0 },
  tablet: { width: '600px', height: '80vh', x: '-50%', left: '50%' },
  desktop: { width: '400px', height: '600px', bottom: 24, right: 24 }
}
```

---

### Research: Sonner Custom Toast Styling

**Decision**: Create custom toast component with glassmorphism theme passed to `toast()`.

**Rationale**:
- Sonner supports custom components via `toast.custom()` API
- Glassmorphism can be applied via backdrop-filter and CSS custom properties
- Allows themed icons, animations, and responsive positioning
- Pattern: `toast.custom((props) => <ThemedToast {...props} />)`

**Alternatives Considered**:
- **Global CSS overrides**: Conflicts with default Sonner styling
- **React-Toastify**: Additional dependency, larger bundle
- **Custom toast library**: Reinventing the wheel

**Implementation Pattern**:
```typescript
const themedToast = (message: string, type: 'success' | 'error') => {
  toast.custom((t) => (
    <ThemedToast t={t} message={message} type={type} />
  ), { duration: 3000 })
}
```

---

### Research: Next.js 15 Route-Aware Component Rendering

**Decision**: Use `usePathname()` hook to conditionally render ChatPanel.

**Rationale**:
- `usePathname()` returns current route in client components
- Providers layer can check pathname before rendering ChatPanel
- Alternative: Create separate dashboard layout with ChatPanel included
- Chosen approach: Less file changes, leverages existing providers structure

**Alternatives Considered**:
- **Separate dashboard layout**: More files to maintain
- **Middleware-based**: Overkill for component visibility
- **URL parameter**: Adds clutter to URLs

**Implementation Pattern**:
```typescript
'use client'
import { usePathname } from 'next/navigation'
import { ChatPanel } from '@/components/chat/chat-panel'

export function ConditionalChatPanel() {
  const pathname = usePathname()
  const showChat = pathname === '/dashboard'
  return showChat ? <ChatPanel /> : null
}
```

---

### Research: State Management Approach

**Decision**: Keep React Context for chat UI state, add Zustand for task cache updates.

**Rationale**:
- Existing `chat-store.ts` uses React Context (prevents SSR issues)
- Task cache updates are cross-cutting concern (affects dashboard)
- Zustand persists state across component unmounts
- Split: Context for chat UI, Zustand for task mutation events

**Alternatives Considered**:
- **Migrate all to Zustand**: Risk of SSR hydration issues returning
- **Keep all in Context**: Complex prop drilling for task updates
- **Jotai**: Additional dependency, team less familiar

**Implementation Pattern**:
```typescript
// New: lib/stores/task-events.ts (Zustand)
interface TaskEventStore {
  lastEvent: { type: string; taskId: number; timestamp: number } | null
  setTaskEvent: (event: TaskEvent) => void
}

// Existing: chat-store.ts (React Context)
// Add action: invalidateTask: (taskId: number) => void
```

---

## Phase 1: Design & Contracts

### Data Model

**No new data entities.** This feature modifies UI state only. Existing Task model remains unchanged.

### State Management Contracts

```typescript
// lib/stores/task-events.ts (NEW - Zustand)
interface TaskEventStore {
  // Recent task mutation from AI (for dashboard sync)
  lastMutation: {
    type: 'create' | 'complete' | 'update' | 'delete'
    taskId: number
    timestamp: number
    data?: Partial<Task>
  } | null

  // Actions
  setTaskMutation: (mutation: TaskMutation) => void
  clearMutation: () => void
}

// lib/stores/chat-store.ts (MODIFIED)
interface ChatUIState {
  // ... existing fields ...

  // NEW: Cache update trigger for AI actions
  triggerTaskUpdate: (taskId: number, mutation: TaskMutation) => void
}
```

### Component Contracts

```typescript
// components/chat/chat-skeleton.tsx (NEW)
interface ChatSkeletonProps {
  count?: number  // Number of skeleton items
  variant?: 'user' | 'assistant'
}

// components/chat/agent-intro.tsx (NEW)
interface AgentIntroProps {
  onExampleClick: (prompt: string) => void
  onStartChat: () => void
}

// components/chat/themed-toast.tsx (NEW)
interface ThemedToastProps {
  message: string
  type: 'success' | 'error' | 'info'
  onClose: () => void
}
```

### SSE Event Contracts

```typescript
// Extended SSE event types for tool result parsing
interface ToolResultEvent {
  eventType: 'tool_result'
  data: {
    tool: 'add_task' | 'complete_task' | 'update_task' | 'delete_task'
    output: {
      success: boolean
      data?: Task
      error?: string
    }
  }
}
```

---

## Quickstart

### Development Setup

```bash
# Ensure frontend dependencies are installed
cd frontend
npm install

# Start development server
npm run dev

# Open dashboard
# Navigate to http://localhost:3000/dashboard
# AI assistant FAB should be visible only on this page
```

### Testing Real-Time Updates

```bash
# 1. Start backend (required for SSE)
cd ../backend
uv run uvicorn app.main:app --reload

# 2. Start frontend
cd frontend
npm run dev

# 3. Open browser to http://localhost:3000/dashboard
# 4. Open DevTools Console
# 5. Click AI FAB and send: "Create a task called 'Test real-time update'"
# 6. Watch Console for SSE events and cache updates
# 7. Verify task appears in dashboard without refresh
```

### Component Development Order

1. **Phase 1a**: Create `chat-skeleton.tsx` - Foundation for loading states
2. **Phase 1b**: Create `agent-intro.tsx` - Welcome screen for new users
3. **Phase 1c**: Create `themed-toast.tsx` - Glassmorphism toast component
4. **Phase 1d**: Modify `voice-recorder.tsx` - Remove confirmation, add stop button
5. **Phase 1e**: Modify `chat-panel.tsx` - Add responsive variants and intro screen
6. **Phase 1f**: Modify `chat-message.tsx` - Apply glassmorphism styling
7. **Phase 1g**: Modify `chat-input.tsx` - Consistent styling
8. **Phase 1h**: Modify `lib/api/chat.ts` - Add tool call event parsing
9. **Phase 1i**: Modify `lib/stores/chat-store.ts` - Add cache update actions
10. **Phase 1j**: Modify `app/providers.tsx` - Route-aware ChatPanel rendering

---

## Complexity Tracking

> **No constitution violations require justification.** All gates passed in Constitution Check section above.

