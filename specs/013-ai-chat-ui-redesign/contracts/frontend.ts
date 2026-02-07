# Frontend Component Contracts

**Feature**: 013-ai-chat-ui-redesign
**Type**: TypeScript/React Interface Definitions

---

## New Components

### ChatSkeleton

```typescript
// components/chat/chat-skeleton.tsx
interface ChatSkeletonProps {
  /** Number of skeleton items to render */
  count?: number

  /** Message type variant (affects skeleton height) */
  variant?: 'user' | 'assistant'

  /** Optional custom className */
  className?: string
}

// Example usage:
<ChatSkeleton count={3} variant="assistant" />
```

### AgentIntro

```typescript
// components/chat/agent-intro.tsx
interface AgentIntroProps {
  /** Callback when user clicks an example prompt */
  onExampleClick: (prompt: string) => void

  /** Callback when user sends first message (dismisses intro) */
  onStartChat: () => void

  /** Optional custom className */
  className?: string
}

// Example usage:
<AgentIntro
  onExampleClick={(prompt) => sendMessage(prompt)}
  onStartChat={() => setShowIntro(false)}
/>
```

### ThemedToast

```typescript
// components/chat/themed-toast.tsx
interface ThemedToastProps {
  /** Toast message content */
  message: string

  /** Toast type determines styling */
  type: 'success' | 'error' | 'info'

  /** Callback when toast is dismissed */
  onClose: () => void

  /** Optional duration in ms (default: 3000) */
  duration?: number

  /** Optional custom className */
  className?: string
}

// Example usage:
<ThemedToast
  message="Task created successfully"
  type="success"
  onClose={() => toast.dismiss(id)}
/>
```

---

## Modified Components

### ChatPanel

```typescript
// components/chat/chat-panel.tsx (MODIFIED)
interface ChatPanelProps {
  /** Panel open/closed state */
  isOpen?: boolean

  /** Callback when panel is toggled */
  onToggle?: () => void

  /** Current conversation ID */
  conversationId?: string | null

  /** Optional custom className */
  className?: string
}

// NEW: Responsive behavior
// - Mobile (< 640px): full-screen layout
// - Tablet (640px - 1024px): centered modal
// - Desktop (> 1024px): floating panel bottom-right

// NEW: Introduction screen integration
// - Shows when no messages in current conversation
// - Dismissed on first message sent
```

### VoiceRecorder

```typescript
// components/chat/voice-recorder.tsx (MODIFIED)
interface VoiceRecorderProps {
  /** Callback when transcription is ready */
  onTranscriptionComplete: (text: string) => void

  /** Callback when recording is cancelled */
  onCancel?: () => void

  /** Optional custom className */
  className?: string
}

// NEW: Stop button during recording
// - User can cancel/recording during active recording
// - Shows pulsing animation and duration counter

// REMOVED: Confirmation dialog
// - Transcription sends directly to agent
// - No "Retake or Send?" prompt
```

### ChatMessage

```typescript
// components/chat/chat-message.tsx (MODIFIED)
interface ChatMessageProps {
  /** Message role */
  role: 'user' | 'assistant' | 'system'

  /** Message content */
  content: string

  /** Timestamp of message */
  timestamp: Date

  /** Whether message is from voice input */
  isVoiceMessage?: boolean

  /** Optional tool calls for assistant messages */
  toolCalls?: ToolCall[]

  /** Optional custom className */
  className?: string
}

// NEW: Glassmorphism styling
// - backdrop-filter: blur(12px)
// - border: 1px solid var(--color-primary)
// - box-shadow: 0 4px 24px rgba(0, 245, 255, 0.1)

// NEW: Voice indicator for user messages
// - Shows mic icon instead of transcribed text
// - Alt text reveals transcription
```

### ChatInput

```typescript
// components/chat/chat-input.tsx (MODIFIED)
interface ChatInputProps {
  /** Callback when message is sent */
  onSend: (message: string) => void

  /** Whether currently streaming */
  isStreaming?: boolean

  /** Optional placeholder text */
  placeholder?: string

  /** Optional custom className */
  className?: string
}

// NEW: Consistent styling with dashboard inputs
// - Uses same .glass class
// - Same focus states (cyan glow)
// - Same border radius and padding

// UNCHANGED: Auto-expanding textarea behavior
```

---

## State Management Contracts

### TaskEventStore (NEW - Zustand)

```typescript
// lib/stores/task-events.ts
interface TaskEventStore {
  // State
  lastMutation: TaskMutation | null

  // Actions
  setTaskMutation: (mutation: TaskMutation) => void
  clearMutation: () => void
}

interface TaskMutation {
  type: 'create' | 'complete' | 'update' | 'delete'
  taskId: number
  timestamp: number
  data?: Partial<Task>
}

// Example usage:
import { useTaskEventStore } from '@/lib/stores/task-events'

const { lastMutation, setTaskMutation } = useTaskEventStore()

// When SSE tool_result event received:
setTaskMutation({
  type: 'complete',
  taskId: 123,
  timestamp: Date.now(),
  data: { completed: true }
})
```

### ChatStore (MODIFIED - React Context)

```typescript
// lib/stores/chat-store.ts
interface ChatUIState {
  // Existing (unchanged)
  isOpen: boolean
  messages: Message[]
  isStreaming: boolean
  currentConversationId: string | null

  // NEW: Task cache coordination
  triggerTaskUpdate: (taskId: number, mutation: TaskMutation) => void
  onTaskMutated: (mutation: TaskMutation) => void

  // Existing actions (unchanged)
  openChat: () => void
  closeChat: () => void
  sendMessage: (content: string, isVoice?: boolean) => Promise<void>
  setCurrentConversation: (id: string | null) => void
}

// Example usage:
import { useChatStore } from '@/lib/stores/chat-store'

const { triggerTaskUpdate } = useChatStore()

// When AI completes a task:
triggerTaskUpdate(123, { type: 'complete', taskId: 123, timestamp: Date.now() })
```

---

## API Contracts

### SSE Event Extensions

```typescript
// lib/utils/sse.ts (MODIFIED)
interface SSEEventHandlers {
  // Existing (unchanged)
  onToken?: (data: { content: string }) => void
  onToolCall?: (data: { tool: string; arguments: unknown }) => void
  onAgentHandoff?: (data: { from_agent: string; to_agent: string }) => void

  // NEW: Tool result handler for task mutations
  onToolResult?: (data: ToolResultEvent) => void
}

interface ToolResultEvent {
  tool: 'add_task' | 'complete_task' | 'update_task' | 'delete_task'
  output: {
    success: boolean
    data?: Task
    error?: string
  }
}
```

---

## Utility Contracts

### Toast Notification Helper

```typescript
// lib/utils/toast.ts (NEW)
interface ThemedToastOptions {
  message: string
  type: 'success' | 'error' | 'info'
  duration?: number
}

interface ThemedToastAPI {
  success: (message: string) => void
  error: (message: string) => void
  info: (message: string) => void
}

// Example usage:
import { themedToast } from '@/lib/utils/toast'

// When AI creates a task:
themedToast.success('Task created: Buy groceries')

// When AI completes a task:
themedToast.success('Task completed!')

// On error:
themedToast.error('Failed to create task')
```

### Responsive Breakpoint Helper

```typescript
// lib/utils/responsive.ts (NEW)
type Breakpoint = 'mobile' | 'tablet' | 'desktop'

interface UseResponsiveReturn {
  breakpoint: Breakpoint
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
}

// Example usage:
import { useResponsive } from '@/lib/utils/responsive'

const { breakpoint, isMobile } = useResponsive()
// breakpoint: 'mobile' | 'tablet' | 'desktop'
// isMobile: breakpoint === 'mobile'
```
