# Data Model: AI Chat UI Redesign

**Feature**: 013-ai-chat-ui-redesign
**Status**: No new data entities (frontend-only feature)

## Overview

This feature focuses purely on UI/UX improvements and does not introduce any new data entities or modify existing backend data models. All changes are frontend state management and component styling.

---

## No New Data Entities

### Backend (No Changes)

The existing backend models remain unchanged:

```python
# Existing models (NOT modified by this feature)
class Task(SQLModel, table=True):
    id: int
    user_id: str
    title: str
    description: str | None
    priority: Priority
    tags: list[Tag]
    completed: bool
    created_at: datetime
    due_date: datetime | None
    recurrence_pattern: RecurrencePattern | None

# Chat models (NOT modified)
class Conversation(SQLModel, table=True):
    id: int
    user_id: str
    title: str | None
    created_at: datetime
    updated_at: datetime

class Message(SQLModel, table=True):
    id: int
    conversation_id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
```

---

## Frontend State Models (TypeScript)

### New: Task Event Store (Zustand)

```typescript
// lib/stores/task-events.ts (NEW)
interface TaskMutation {
  type: 'create' | 'complete' | 'update' | 'delete'
  taskId: number
  timestamp: number
  data?: Partial<Task>
}

interface TaskEventStore {
  // State
  lastMutation: TaskMutation | null

  // Actions
  setTaskMutation: (mutation: TaskMutation) => void
  clearMutation: () => void
}
```

### Modified: Chat Store (React Context)

```typescript
// lib/stores/chat-store.ts (MODIFIED)
interface ChatUIState {
  // Existing fields (unchanged)
  isOpen: boolean
  messages: Message[]
  isStreaming: boolean
  currentConversationId: string | null

  // NEW: Task cache coordination
  triggerTaskUpdate: (taskId: number, mutation: TaskMutation) => void
  onTaskMutated: (mutation: TaskMutation) => void
}
```

### New: Component Props

```typescript
// components/chat/chat-skeleton.tsx (NEW)
interface ChatSkeletonProps {
  count?: number
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

### New: SSE Event Types

```typescript
// lib/utils/sse.ts (MODIFIED - extended types)
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

interface ToolCallEvent {
  eventType: 'tool_call'
  data: {
    tool: string
    arguments: Record<string, unknown>
  }
}
```

---

## State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     SSE Stream (Backend)                         │
│  - tool_call events (AI invoked action)                          │
│  - tool_result events (Action completed)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend SSE Parser (lib/api/chat.ts)              │
│  - Parse tool_result events                                      │
│  - Extract task mutation data                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Chat Store (React Context) + Task Events (Zustand)       │
│  - triggerTaskUpdate() action                                    │
│  - setTaskMutation() action                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              TanStack Query Cache Update                         │
│  - queryClient.setQueryData(['tasks', id], updatedTask)         │
│  - queryClient.invalidateQueries(['tasks']) // Background       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Dashboard Components                          │
│  - Task lists auto-re-render with updated data                   │
│  - Celebration animation plays on task completion                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Validation Rules

### Task Mutation Validation

```typescript
// Validate task mutation before cache update
function validateTaskMutation(mutation: TaskMutation): boolean {
  // Must have type
  if (!mutation.type) return false

  // Must have taskId (except for create which generates it)
  if (mutation.type !== 'create' && !mutation.taskId) return false

  // Must have timestamp
  if (!mutation.timestamp) return false

  // Create must have data
  if (mutation.type === 'create' && !mutation.data) return false

  return true
}
```

### Voice Recording Validation

```typescript
// Validate voice recording state
interface VoiceRecordingState {
  isRecording: boolean
  duration: number  // Maximum 30 seconds
  blob?: Blob
  error?: string
}

// Validation rules
const MAX_RECORDING_DURATION = 30 * 1000 // 30 seconds in ms

function validateRecording(state: VoiceRecordingState): boolean {
  if (state.duration > MAX_RECORDING_DURATION) return false
  if (state.isRecording && !state.blob) return true  // Valid: recording in progress
  if (!state.isRecording && state.blob) return true   // Valid: recording complete
  return false
}
```

---

## Summary

- **Backend**: No changes to data models or API
- **Frontend State**: New TaskEventStore (Zustand), extended ChatUIState (React Context)
- **Component Props**: 3 new component interfaces
- **SSE Events**: Extended event types for tool call/result parsing
