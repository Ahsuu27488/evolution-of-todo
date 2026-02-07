# Tasks: AI Chat UI Redesign

**Input**: Design documents from `/specs/013-ai-chat-ui-redesign/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are OPTIONAL - not explicitly requested in feature specification. Tasks focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/components/`, `frontend/lib/`, `frontend/app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

> **NOTE**: This is a frontend-only feature modifying an existing project. Setup tasks are minimal since the project structure already exists.

- [ ] T001 Verify frontend dependencies are installed in frontend/package.json
- [ ] T002 [P] Verify TanStack Query v5 is installed in frontend/
- [ ] T003 [P] Verify Framer Motion is installed in frontend/
- [ ] T004 [P] Verify Sonner (toast library) is installed in frontend/
- [ ] T005 [P] Verify Zustand is installed in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core state management infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 [P] Create responsive breakpoint utility in frontend/lib/utils/responsive.ts (exports useResponsive hook, Breakpoint type)
- [ ] T007 [P] Create TaskEventStore Zustand store in frontend/lib/stores/task-events.ts (exports TaskMutation interface, TaskEventStore with lastMutation, setTaskMutation, clearMutation)
- [ ] T008 Extend SSE parser with tool result event types in frontend/lib/utils/sse.ts (add ToolResultEvent, ToolCallEvent interfaces, parseToolResult helper)
- [ ] T009 Add triggerTaskUpdate action to chat store in frontend/lib/stores/chat-store.ts (adds cache update coordination between Context and Zustand)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-Time Task State Synchronization (Priority: P1) 🎯 MVP

**Goal**: AI actions (create, complete, update tasks) update dashboard immediately via SSE cache updates without page refresh

**Independent Test**: Open chat panel, ask Chronos to complete a task, verify task shows as completed in dashboard without refresh

### Implementation for User Story 1

- [ ] T010 [US1] Add tool result event handler in frontend/lib/api/chat.ts (parses tool_result events, extracts task data, calls cache update)
- [ ] T011 [US1] Implement TanStack Query cache update in frontend/lib/api/chat.ts (calls queryClient.setQueryData for immediate update, queryClient.invalidateQueries for background refresh)
- [ ] T012 [US1] Wire task event store to SSE handler in frontend/lib/api/chat.ts (calls setTaskMutation on each tool_result event)
- [ ] T013 [US1] Add celebration animation trigger in frontend/components/dashboard/task-card.tsx (triggers when task.completed changes to true via AI action)
- [ ] T014 [US1] Integrate SSE cache updates with toast notifications in frontend/lib/api/chat.ts (calls themedToast on successful AI actions)

**Checkpoint**: At this point, User Story 1 should be fully functional - AI actions update dashboard in real-time

---

## Phase 4: User Story 2 - FAB Location Control (Priority: P1)

**Goal**: AI assistant FAB only visible on dashboard page

**Independent Test**: Navigate to different pages, verify FAB only appears on /dashboard

### Implementation for User Story 2

- [ ] T015 [P] [US2] Create ConditionalChatPanel component in frontend/components/chat/conditional-chat-panel.tsx (uses usePathname hook, renders ChatPanel only when pathname === '/dashboard')
- [ ] T016 [US2] Remove global ChatPanel from providers in frontend/app/providers.tsx (replaces global ChatPanel with ConditionalChatPanel)
- [ ] T017 [US2] Add chat panel close on navigation in frontend/components/chat/chat-panel.tsx (listens to pathname changes, closes panel when navigating away from /dashboard)
- [ ] T018 [US2] Preserve chat state in frontend/lib/stores/chat-store.ts (maintains messages, conversationId when navigating back to dashboard)

**Checkpoint**: At this point, User Story 2 should be fully functional - FAB only visible on dashboard

---

## Phase 5: User Story 3 - Mobile-First Responsive Design (Priority: P1)

**Goal**: Chat panel adapts to screen size - full-screen mobile, centered modal tablet, floating panel desktop - with glassmorphism theme

**Independent Test**: Resize browser from 320px to 1920px, verify chat panel layout adapts smoothly

### Implementation for User Story 3

- [ ] T019 [P] [US3] Define breakpoint variants in frontend/components/chat/chat-panel.tsx (mobile: full-screen, tablet: centered modal, desktop: floating panel)
- [ ] T020 [US3] Add AnimatePresence wrapper in frontend/components/chat/chat-panel.tsx (enables smooth layout transitions during resize)
- [ ] T021 [US3] Implement responsive layout logic in frontend/components/chat/chat-panel.tsx (uses useResponsive hook, applies variants based on breakpoint)
- [ ] T022 [P] [US3] Apply glassmorphism theme to chat panel in frontend/components/chat/chat-panel.tsx (backdrop-blur, OKLCH colors, neon borders matching dashboard)
- [ ] T023 [US3] Verify touch targets meet 44px minimum in frontend/components/chat/chat-panel.tsx (all interactive elements have min-height: 44px)
- [ ] T024 [US3] Add resize debouncing in frontend/lib/utils/responsive.ts (prevents animation jank during rapid resize)

**Checkpoint**: At this point, User Story 3 should be fully functional - chat panel responsive across all screen sizes

---

## Phase 6: User Story 4 - Enhanced Voice Recording Experience (Priority: P2)

**Goal**: Streamlined voice recording - no confirmation prompts, direct send to agent, stop button for cancellation

**Independent Test**: Record voice message, verify it sends directly without confirmation dialog

### Implementation for User Story 4

- [ ] T025 [P] [US4] Add recording duration display in frontend/components/chat/voice-recorder.tsx (shows MM:SS format, updates every second)
- [ ] T026 [P] [US4] Add pulsing animation during recording in frontend/components/chat/voice-recorder.tsx (visual feedback that recording is active)
- [ ] T027 [P] [US4] Add stop/cancel button in frontend/components/chat/voice-recorder.tsx (allows user to cancel recording and retry)
- [ ] T028 [US4] Remove confirmation dialog in frontend/components/chat/voice-recorder.tsx (transcription sends directly to agent via onTranscriptionComplete)
- [ ] T029 [US4] Display voice message indicator in frontend/components/chat/chat-message.tsx (shows mic icon for voice messages, not transcribed text)
- [ ] T030 [US4] Add transcription error handling with retry in frontend/components/chat/voice-recorder.tsx (shows inline error message with retry button on failure)

**Checkpoint**: At this point, User Story 4 should be fully functional - voice recording streamlined

---

## Phase 7: User Story 5 - Loading Skeleton States (Priority: P2)

**Goal**: Skeleton loading animations when conversation history loads - YouTube-style shimmer effect

**Independent Test**: Open existing conversation, verify skeleton placeholders appear before messages

### Implementation for User Story 5

- [ ] T031 [P] [US5] Create ChatSkeleton component in frontend/components/chat/chat-skeleton.tsx (accepts count and variant props, matches message bubble design)
- [ ] T032 [P] [US5] Implement shimmer animation in frontend/components/chat/chat-skeleton.tsx (uses CSS keyframes, matches dashboard loading pattern)
- [ ] T033 [US5] Add skeleton fade-out transition in frontend/components/chat/chat-skeleton.tsx (smoothly fades out when content loads)
- [ ] T034 [US5] Integrate skeletons with conversation loading in frontend/components/chat/chat-panel.tsx (shows ChatSkeleton while messages are loading)
- [ ] T035 [US5] Add timeout fallback for slow connections in frontend/components/chat/chat-panel.tsx (after 15 seconds, shows retry option)

**Checkpoint**: At this point, User Story 5 should be fully functional - loading skeletons display correctly

---

## Phase 8: User Story 6 - Agent Introduction Screen (Priority: P2)

**Goal**: Welcome screen for first-time users showing Chronos's name, personality, capabilities, and example prompts

**Independent Test**: Open fresh chat session (no messages), verify introduction screen appears

### Implementation for User Story 6

- [ ] T036 [P] [US6] Create AgentIntro component in frontend/components/chat/agent-intro.tsx (displays Chronos name, personality, key capabilities)
- [ ] T037 [P] [US6] Add example prompt buttons in frontend/components/chat/agent-intro.tsx (clickable prompts like "Create a task", "What can you do?")
- [ ] T038 [P] [US6] Apply glassmorphism theme in frontend/components/chat/agent-intro.tsx (backdrop-blur, OKLCH colors matching dashboard)
- [ ] T039 [US6] Integrate intro screen with chat panel in frontend/components/chat/chat-panel.tsx (shows when messages.length === 0, hides on first message)
- [ ] T040 [US6] Add example prompt click handler in frontend/components/chat/agent-intro.tsx (calls sendMessage with clicked prompt text)

**Checkpoint**: At this point, User Story 6 should be fully functional - introduction screen displays for new users

---

## Phase 9: User Story 7 - Themed Toast Notifications (Priority: P2)

**Goal**: Glassmorphism toast notifications matching app theme, appearing for both user and AI actions

**Independent Test**: Trigger AI action, verify themed toast appears with glassmorphism styling

### Implementation for User Story 7

- [ ] T041 [P] [US7] Create ThemedToast component in frontend/components/chat/themed-toast.tsx (glassmorphism styling with backdrop-blur, neon borders)
- [ ] T042 [P] [US7] Add themed toast helper in frontend/lib/utils/toast.ts (themedToast function with success, error, info methods)
- [ ] T043 [US7] Implement toast queue management in frontend/lib/utils/toast.ts (max 3 visible at once, intelligent stacking)
- [ ] T044 [US7] Add responsive positioning in frontend/components/ui/sonner.tsx (positioned appropriately on mobile, doesn't interfere with chat input)
- [ ] T045 [US7] Integrate themed toasts with SSE events in frontend/lib/api/chat.ts (calls themedToast.success on AI task actions)

**Checkpoint**: At this point, User Story 7 should be fully functional - themed toasts display for AI actions

---

## Phase 10: User Story 8 - Redesigned Message Components (Priority: P3)

**Goal**: Chat messages and input areas redesigned with glassmorphism theme matching dashboard visual quality

**Independent Test**: Compare chat message design with dashboard task cards, verify consistent styling

### Implementation for User Story 8

- [ ] T046 [P] [US8] Apply glassmorphism to chat messages in frontend/components/chat/chat-message.tsx (backdrop-blur, subtle borders, OKLCH colors)
- [ ] T047 [P] [US8] Design voice message indicator in frontend/components/chat/chat-message.tsx (mic icon styling matching app icon theme)
- [ ] T048 [P] [US8] Apply consistent input styling in frontend/components/chat/chat-input.tsx (matches dashboard input fields, glassmorphism, focus states)
- [ ] T049 [US8] Add spring physics animations in frontend/components/chat/chat-message.tsx (hover/tap animations match dashboard components)
- [ ] T050 [US8] Verify color consistency in frontend/components/chat/chat-panel.tsx (cyan primary, purple secondary consistent with dashboard)

**Checkpoint**: At this point, User Story 8 should be fully functional - chat components match dashboard theme

---

## Phase 11: User Story 9 - Conversation History Loading States (Priority: P3)

**Goal**: Loading feedback when switching conversations or loading older messages - skeleton placeholders and error states

**Independent Test**: Switch between conversations, verify skeletons appear; scroll to load older messages, verify loading indicator

### Implementation for User Story 9

- [ ] T051 [P] [US9] Add conversation switch loading state in frontend/components/chat/chat-panel.tsx (shows ChatSkeleton when switching conversations)
- [ ] T052 [US9] Implement older messages loading indicator in frontend/components/chat/chat-panel.tsx (shows loading indicator at top when scrolling up for pagination)
- [ ] T053 [US9] Add loading error state with retry in frontend/components/chat/chat-panel.tsx (displays error message with retry button on load failure)
- [ ] T054 [US9] Implement request cancellation on rapid switch in frontend/lib/api/chat.ts (cancels pending request when user switches conversations rapidly)

**Checkpoint**: At this point, User Story 9 should be fully functional - conversation loading states work correctly

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T055 [P] Update frontend/CLAUDE.md with dual state management pattern documentation
- [ ] T056 [P] Run quickstart.md validation in frontend/ (verify all testing procedures pass)
- [ ] T057 [P] Test responsive behavior across all breakpoints (mobile 320px-480px, tablet 640px-1024px, desktop 1024px+)
- [ ] T058 [P] Verify glassmorphism theme consistency across all chat components in frontend/components/chat/
- [ ] T059 [P] Test real-time task synchronization end-to-end (AI creates task, verify dashboard updates)
- [ ] T060 [P] Verify voice recording works without confirmation (record, send, verify no dialog appears)
- [ ] T061 [P] Test FAB location control across all routes (navigate to /, /profile, /settings, verify FAB hidden)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-11)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 7 (P2)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 8 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 9 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T005) marked [P] can run in parallel
- All Foundational tasks (T006-T009) marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all foundational tasks together:
Task: "Create responsive breakpoint utility in frontend/lib/utils/responsive.ts"
Task: "Create TaskEventStore Zustand store in frontend/lib/stores/task-events.ts"
Task: "Extend SSE parser with tool result event types in frontend/lib/utils/sse.ts"
Task: "Add triggerTaskUpdate action to chat store in frontend/lib/stores/chat-store.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Real-Time Sync) 🎯
4. Complete Phase 4: User Story 2 (FAB Location)
5. Complete Phase 5: User Story 3 (Responsive Design)
6. **STOP and VALIDATE**: Test P1 stories independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (P1) → Test independently → Deploy/Demo (Core value!)
3. Add User Story 2 (P1) → Test independently → Deploy/Demo
4. Add User Story 3 (P1) → Test independently → Deploy/Demo
5. Add User Story 4 (P2) → Test independently → Deploy/Demo
6. Add User Story 5 (P2) → Test independently → Deploy/Demo
7. Add User Story 6 (P2) → Test independently → Deploy/Demo
8. Add User Story 7 (P2) → Test independently → Deploy/Demo
9. Add User Story 8 (P3) → Test independently → Deploy/Demo
10. Add User Story 9 (P3) → Test independently → Deploy/Demo
11. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Stories 1, 2, 3 (P1 features)
   - Developer B: User Stories 4, 5, 6 (P2 features)
   - Developer C: User Stories 7, 8, 9 (P2/P3 features)
3. Stories complete and integrate independently

---

## Summary

- **Total Tasks**: 61
- **Task Count by User Story**:
  - Setup: 5 tasks
  - Foundational: 4 tasks
  - US1 (P1): 5 tasks
  - US2 (P1): 4 tasks
  - US3 (P1): 6 tasks
  - US4 (P2): 6 tasks
  - US5 (P2): 5 tasks
  - US6 (P2): 5 tasks
  - US7 (P2): 5 tasks
  - US8 (P3): 5 tasks
  - US9 (P3): 4 tasks
  - Polish: 7 tasks
- **Parallel Opportunities Identified**: 37 tasks marked [P] can run in parallel within their phases
- **Independent Test Criteria**: Each user story has clear independent test criteria
- **Suggested MVP Scope**: User Stories 1-3 (all P1 features) for core value delivery

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All paths are frontend/ (this is a frontend-only feature)
