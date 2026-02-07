# Quickstart: AI Chat UI Redesign

**Feature**: 013-ai-chat-ui-redesign
**Branch**: `013-ai-chat-ui-redesign`

---

## Development Setup

### Prerequisites

- Node.js 20+ (for Next.js frontend)
- Python 3.13+ (for FastAPI backend - unchanged)
- Existing Phase III AI Chatbot implementation

### Installation

```bash
# Frontend dependencies (already installed, but verify)
cd frontend
npm install

# Key dependencies for this feature:
# - framer-motion: ^11.0.0  (responsive animations)
# - @tanstack/react-query: ^5.0.0  (cache updates)
# - sonner: ^1.5.0  (toast notifications)
# - zustand: ^4.5.0  (task event store)
```

### Running the Application

```bash
# Terminal 1: Start backend (required for SSE)
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Open browser to http://localhost:3000/dashboard
```

---

## Feature Overview

### What Changed

| Component | Change | Impact |
|-----------|--------|--------|
| `chat-panel.tsx` | Responsive layouts (mobile/tablet/desktop) | FAB only on dashboard |
| `chat-skeleton.tsx` | NEW | Loading skeletons for conversations |
| `agent-intro.tsx` | NEW | Welcome screen for first-time users |
| `themed-toast.tsx` | NEW | Glassmorphism toast notifications |
| `voice-recorder.tsx` | Removed confirmation, added stop button | Streamlined voice UX |
| `chat-message.tsx` | Glassmorphism styling | Visual consistency |
| `chat-input.tsx` | Consistent styling | Visual consistency |
| `lib/api/chat.ts` | SSE tool call parsing | Real-time updates |
| `lib/stores/task-events.ts` | NEW (Zustand) | Task mutation events |
| `app/providers.tsx` | Route-aware ChatPanel | FAB location control |

---

## Testing the Features

### 1. FAB Location Control

```bash
# Test: FAB only visible on dashboard
1. Navigate to http://localhost:3000/dashboard
2. Verify: AI assistant FAB (bottom-right) is visible
3. Navigate to http://localhost:3000/
4. Verify: FAB is NOT visible
5. Navigate to http://localhost:3000/dashboard
6. Verify: FAB reappears
```

### 2. Real-Time Task Updates

```bash
# Test: AI actions update dashboard immediately
1. Open dashboard: http://localhost:3000/dashboard
2. Open browser DevTools > Network tab
3. Click AI FAB to open chat
4. Send: "Create a task called 'Test real-time update'"
5. Verify: Task appears in dashboard WITHOUT refresh
6. Send: "Mark the 'Test real-time update' task as complete"
7. Verify: Task shows as completed WITHOUT refresh
8. Verify: Celebration animation plays
```

### 3. Responsive Chat Panel

```bash
# Test: Chat panel adapts to screen size
1. Open dashboard on desktop (>1024px)
2. Click AI FAB
3. Verify: Chat panel is floating in bottom-right (400x600px)
4. Resize browser to 800px width (tablet)
5. Verify: Chat panel becomes centered modal (600x80vh)
6. Resize browser to 400px width (mobile)
7. Verify: Chat panel becomes full-screen with padding
```

### 4. Voice Recording (No Confirmation)

```bash
# Test: Voice sends directly without confirmation
1. Open chat panel
2. Click microphone button
3. Speak a task: "Remind me to buy groceries"
4. Click stop button
5. Verify: Transcription sends DIRECTLY to agent (no confirmation dialog)
6. Verify: Chat shows voice indicator (mic icon) for your message
```

### 5. Loading Skeletons

```bash
# Test: Skeletons appear during conversation loading
1. Open chat panel
2. Click on a conversation in history (if available)
3. Verify: Skeleton placeholders appear before messages load
4. Verify: Skeletons use shimmer effect matching dashboard
5. Verify: Skeletons fade out when content arrives
```

### 6. Agent Introduction Screen

```bash
# Test: Introduction shows for new conversations
1. Clear browser local storage (to simulate new user)
2. Open chat panel
3. Verify: Welcome screen with Chronos name appears
4. Verify: Example prompts are clickable
5. Click an example prompt
6. Verify: Introduction screen replaced by conversation
```

### 7. Themed Toast Notifications

```bash
# Test: Toast notifications match app theme
1. Have AI create a task
2. Verify: Toast appears with glassmorphism theme (backdrop blur, neon border)
3. Verify: Toast displays on mobile without blocking chat input
4. Trigger multiple actions rapidly
5. Verify: Maximum 3 toasts visible at once
```

---

## Development Workflow

### Component Development Order

1. **Phase 1a**: `chat-skeleton.tsx` - Foundation for loading states
2. **Phase 1b**: `agent-intro.tsx` - Welcome screen
3. **Phase 1c**: `themed-toast.tsx` - Custom toasts
4. **Phase 1d**: `voice-recorder.tsx` - Streamlined recording
5. **Phase 1e**: `chat-panel.tsx` - Responsive variants + intro integration
6. **Phase 1f**: `chat-message.tsx` - Glassmorphism styling
7. **Phase 1g**: `chat-input.tsx` - Consistent input styling
8. **Phase 1h**: `lib/api/chat.ts` - SSE tool call parsing
9. **Phase 1i**: `lib/stores/task-events.ts` - Task event store
10. **Phase 1j**: `app/providers.tsx` - Route-aware rendering

### Testing Each Component

```bash
# After completing each component:
1. Run frontend: npm run dev
2. Open relevant page
3. Test component behavior
4. Check responsive behavior (resize browser)
5. Verify dark/light mode consistency
6. Test accessibility (keyboard navigation, screen reader)
```

---

## Troubleshooting

### Issue: FAB not appearing on dashboard

**Solution**: Check `app/providers.tsx` - verify `ConditionalChatPanel` is being rendered

### Issue: Tasks not updating in real-time

**Solution**: Check DevTools Console for SSE events. Verify `tool_result` events are being parsed.

### Issue: Chat panel not responsive

**Solution**: Check browser width. Breakpoints are: 640px (mobile/tablet), 1024px (tablet/desktop)

### Issue: Toasts not themed

**Solution**: Verify `ThemedToast` component is being used, not default `toast()`

### Issue: Voice confirmation still showing

**Solution**: Check `voice-recorder.tsx` - verify `onTranscriptionComplete` sends directly without confirmation dialog

---

## Success Criteria Verification

| Criterion | How to Verify |
|-----------|---------------|
| SC-001: Task updates within 500ms | Use DevTools Performance tab during AI action |
| SC-002: Layout adapts within 100ms | Resize browser rapidly, observe smooth transition |
| SC-003: Voice transcription 95% accurate | Test voice input with clear speech |
| SC-004: Visual feedback for AI actions | Observe toasts and celebrations |
| SC-005: Mobile interactions work | Test on mobile device or DevTools mobile emulation |
| SC-006: Skeletons within 200ms | Open conversation, observe loading state |
| SC-007: Toasts within 300ms | Trigger AI action, observe toast appearance |
| SC-008: 95% visual consistency | Compare chat components with dashboard |
| SC-009: Introduction screen clear | Ask new user to identify 3 capabilities |
| SC-010: FAB respects page boundaries | Navigate all routes, verify FAB visibility |

---

## Next Steps

After completing this feature:

1. Run full test suite: `npm test`
2. Build production bundle: `npm run build`
3. Test production build locally: `npm run start`
4. Create pull request with `/sp.git.commit-pr`
