# Tasks: Notification System

**Input**: Design documents from `/specs/011-notification-system/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.yaml, quickstart.md

**Tests**: Tests are NOT included in this specification - focus on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` (FastAPI)
- **Frontend**: `frontend/` (Next.js 15)
- **Context7**: Use for all external library integration questions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure environment variables

- [X] T001 Generate VAPID keys for Web Push and add to backend/.env (VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY) using Context7: `/web-push-libs/web-push`
- [X] T002 Add Resend API credentials to backend/.env (RESEND_API_KEY, RESEND_WEBHOOK_SECRET) - sign up at resend.com
- [X] T003 [P] Install backend dependencies: `uv add web-push resend sse-starlette` in backend/
- [X] T004 [P] Verify frontend dependencies: Ensure `@radix-ui/react-dropdown-menu`, `framer-motion` are installed in frontend/

**Checkpoint**: Environment ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create backend/app/models/__init__.py for models package
- [X] T006 [P] [US1][US2][US3] Create Notification model in backend/app/models/notification.py with NotificationType enum, data JSONB, sent_channels array, read_status, deleted_at (use Context7: `/fastapi` for SQLModel patterns)
- [X] T007 [P] [US1][US2][US3] Create NotificationPreference model in backend/app/models/notification_preference.py with in_app_enabled, push_enabled, email_enabled, frequency, dnd_start, dnd_end
- [X] T008 [P] [US2] Create PushSubscription model in backend/app/models/push_subscription.py with subscription JSONB, device_info, is_valid
- [X] T009 [P] [US3] Create EmailDeliveryLog model in backend/app/models/email_delivery_log.py with status enum, sent_at, delivered_at, opened_at
- [X] T010 [US1][US2][US3] Create Alembic migration for all notification tables: `uv run alembic revision --autogenerate -m "Add notification system tables"` in backend/
- [X] T011 [US1][US2][US3] Apply migration: `uv run alembic upgrade head` in backend/

**Checkpoint**: Database schema ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - In-App Notification Center (Priority: P1) 🎯 MVP

**Goal**: Users see a bell icon in header with dropdown showing all notifications, unread indicators, timestamps, and quick actions

**Independent Test**: Create a test notification via API and verify it appears in bell dropdown with cyan glow, correct timestamp, and marks as read on click

### Backend for US1

- [X] T012 [P] [US1] Create NotificationService in backend/app/services/notification_service.py with create(), list_for_user(), mark_read(), mark_all_read(), delete() methods (use Context7: `/fastapi` for service patterns)
- [X] T013 [P] [US1] Create SSEService in backend/app/services/sse_service.py with EventSourceResponse and connection manager (use Context7: `/sysid/sse-starlette`)
- [X] T014 [US1] Create notification routes in backend/app/routes/notifications.py: GET /api/notifications (list with pagination), PUT /api/notifications/{id}/read, POST /api/notifications/mark-all-read, DELETE /api/notifications/{id}
- [X] T015 [US1] Add SSE streaming endpoint GET /api/notifications/stream in backend/app/routes/notifications.py (use Context7: `/sysid/sse-starlette` for EventSourceResponse pattern)
- [X] T016 [US1] Register notifications router in backend/app/main.py
- [X] T017 [US1] Add Notification and NotificationPreference relationships to User model in backend/app/models.py

### Frontend for US1

- [X] T018 [P] [US1] Create frontend/hooks/use-notifications.ts with TanStack Query for notifications CRUD (use Context7: `/tanstack-query-guide` for useQuery, useMutation patterns)
- [X] T019 [P] [US1] Create frontend/hooks/use-notification-stream.ts with SSE EventSource connection and auto-reconnect (use Context7: `/tanstack-query-guide` for SSE integration)
- [X] T020 [P] [US1] Create frontend/components/notifications/notification-item.tsx with glassmorphism card, cyan glow for unread, relative timestamp, disintegrate animation on dismiss
- [X] T021 [P] [US1] Create frontend/components/notifications/notification-bell.tsx with Bell icon, Badge count from @radix-ui/react-dropdown-menu, AnimatePresence for badge pulse
- [X] T022 [P] [US1] Create frontend/components/notifications/notification-dropdown.tsx with DropdownMenu.Content, glassmorphism styling, scrollable list with virtualization for 100+ items
- [X] T023 [US1] Create frontend/components/notifications/notification-empty-state.tsx with "No notifications" message and illustration
- [X] T024 [US1] Create frontend/components/notifications/notifications-client.tsx to wrap all notification components and manage SSE stream
- [X] T025 [US1] Add notification endpoints to frontend/lib/api-client.ts: getNotifications(), markAsRead(), markAllAsRead(), deleteNotification()
- [X] T026 [US1] Integrate notification bell into frontend/components/layout/header.tsx

**Checkpoint**: US1 Complete - Bell icon shows unread count, dropdown displays notifications with real-time SSE updates

---

## Phase 4: User Story 2 - Browser Push Notifications (Priority: P2)

**Goal**: Users receive notifications when browser is backgrounded via Web Push API

**Independent Test**: Grant push permission, create task with due date, background browser, verify styled push notification appears

### Backend for US2

- [ ] T027 [P] [US2] Create PushService in backend/app/services/push_service.py with send_push(), subscribe(), unsubscribe(), is_subscribed() methods (use Context7: `/web-push-libs/web-push` for VAPID setup and sendNotification)
- [ ] T028 [US2] Add push subscription endpoints to backend/app/routes/notifications.py: POST /api/notifications/push/subscribe, DELETE /api/notifications/push/unsubscribe, GET /api/notifications/push/status
- [ ] T029 [US2] Implement rate limiting in PushService: max 3 push/hour per user, exempt urgent (task_overdue, task_due within 1 hour)
- [ ] T030 [US2] Add subscription cleanup on 410/404 errors in PushService, mark is_valid=False

### Frontend for US2

- [ ] T031 [P] [US2] Create frontend/components/notifications/push-permission-modal.tsx with glassmorphism modal, clear permission request, "Allow" and "Deny" buttons
- [ ] T032 [P] [US2] Create frontend/hooks/use-push-subscription.ts with requestPermission(), subscribe(), unsubscribe(), getPermissionStatus() (use Context7: `/web-push-libs/web-push` for subscribe pattern)
- [ ] T033 [P] [US2] Create frontend/public/sw.js service worker with push event handler, notificationclick handler, showNotification with icon/badge (use Context7: `/web-push-libs/web-push` for service worker pattern)
- [ ] T034 [US2] Add service worker registration in frontend/app/layout.tsx with navigator.serviceWorker.register()
- [ ] T035 [US2] Add push endpoints to frontend/lib/api-client.ts: subscribePush(), unsubscribePush(), getPushStatus()
- [ ] T036 [US2] Integrate push permission modal into notification settings in frontend/components/notifications/notification-dropdown.tsx

**Checkpoint**: US2 Complete - Push permissions work, notifications arrive when browser backgrounded

---

## Phase 5: User Story 3 - Email Notifications (Priority: P3)

**Goal**: Users receive email summaries and urgent alerts with Deep Space styling

**Independent Test**: Configure email preferences, trigger notification, verify HTML email arrives with correct styling and unsubscribe link

### Backend for US3

- [ ] T037 [P] [US3] Create EmailService in backend/app/services/email_service.py with send_email(), send_batch(), get_preferences() (use Context7: `/resend/resend-node` for React template pattern)
- [ ] T038 [P] [US3] Create backend/app/emails/task-overdue.tsx React Email template with Deep Space dark theme, cyan accents, glassmorphism card
- [ ] T039 [P] [US3] Create backend/app/emails/daily-digest.tsx React Email template with task summary, due dates, action links
- [ ] T040 [P] [US3] Create backend/app/emails/weekly-summary.tsx React Email template with completion stats, upcoming tasks
- [ ] T041 [US3] Add email preference endpoints to backend/app/routes/notifications.py: GET /api/notifications/email/preferences, PUT /api/notifications/email/preferences
- [ ] T042 [US3] Create backend/app/webhooks/__init__.py for webhooks package
- [ ] T043 [US3] Create backend/app/webhooks/resend.py webhook handler for email.bounced events (use Context7: `/resend/resend-node` for webhook signature verification)
- [ ] T044 [US3] Add POST /api/notifications/webhooks/resend endpoint in backend/app/routes/notifications.py
- [ ] T045 [US3] Implement bounce handling: disable email for user on bounced, log to EmailDeliveryLog
- [ ] T046 [US3] Add unsubscribe endpoint GET /api/notifications/email/unsubscribe with token

### Frontend for US3

- [ ] T047 [P] [US3] Create frontend/components/notifications/email-preferences-form.tsx with channel toggles, frequency dropdown, Do Not Disturb time inputs
- [ ] T048 [US3] Create frontend/components/notifications/notification-settings.tsx page with email preferences, push settings, per-type configuration
- [ ] T049 [US3] Add email endpoints to frontend/lib/api-client.ts: getEmailPreferences(), updateEmailPreferences()
- [ ] T050 [US3] Add notification settings link to user dropdown in frontend/components/layout/user-nav.tsx

**Checkpoint**: US3 Complete - Emails send with Deep Space styling, preferences work, webhooks handle bounces

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story improvements, performance, and final touches

- [ ] T051 [P] Add "Mark all as read" button to notification dropdown in frontend/components/notifications/notification-dropdown.tsx
- [ ] T052 [P] Implement notification pagination with "Load more" button in frontend/components/notifications/notification-dropdown.tsx
- [ ] T053 [P] Add smooth scroll animation with Framer Motion in frontend/components/notifications/notification-dropdown.tsx
- [ ] T054 [P] Create notification settings icon in frontend/components/notifications/notification-bell.tsx for quick access
- [ ] T055 Implement notification deduplication with 5-minute cache window in backend/app/services/notification_service.py
- [ ] T056 Add scheduled job for daily digest emails in backend/app/services/notification_service.py
- [ ] T057 Add scheduled job for weekly summary emails in backend/app/services/notification_service.py
- [ ] T058 Implement soft-delete archive for 30-day-old notifications in backend/app/services/notification_service.py
- [ ] T059 Add notification creation trigger on task due check in backend/app/routes/tasks.py
- [ ] T060 [P] Test all notification types (task_due, task_overdue, task_assigned, task_completed, task_reminder, system_update) render correctly
- [ ] T061 [P] Verify Deep Space theme consistency: glassmorphism, cyan glow `oklch(0.91 0.17 195)`, animations match task completion
- [ ] T062 [P] Verify responsive design on mobile for notification dropdown in frontend/components/notifications/notification-dropdown.tsx
- [ ] T063 Run quickstart.md validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase
  - US1 (In-App): No dependencies on other stories
  - US2 (Push): Can build on US1 notification infrastructure
  - US3 (Email): Can build on US1 notification infrastructure
- **Polish (Phase 6)**: Depends on all desired user stories

### User Story Dependencies

```
┌─────────────┐
│   Setup     │
│  (Phase 1)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Foundational│ ◄──── BLOCKS ALL STORIES
│  (Phase 2)  │
└──────┬──────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌─────────────┐                      ┌─────────────┐
│     US1     │                      │     US2     │
│ In-App Ctr  │                      │  Push Notif │
│   (Phase 3) │                      │   (Phase 4) │
└──────┬──────┘                      └──────┬──────┘
       │                                    │
       │                                    ▼
       │                            ┌─────────────┐
       │                            │     US3     │
       │                            │ Email Notif │
       │                            │   (Phase 5) │
       │                            └──────┬──────┘
       │                                    │
       └────────────────────┬───────────────┘
                            │
                            ▼
                   ┌─────────────┐
                   │    Polish   │
                   │  (Phase 6)  │
                   └─────────────┘
```

### Within Each User Story

- Models can be created in parallel (marked [P])
- Services depend on their models
- Endpoints depend on services
- Frontend components can be built in parallel with backend (marked [P])
- Integration happens after both sides are complete

### Parallel Opportunities

- **Setup**: T001-T004 can run in parallel (T001/T002 same .env file - coordinate)
- **Foundational**: T006-T009 models can be created in parallel
- **US1**: T012-T013 services parallel, T018-T022 frontend components parallel
- **US2**: T031-T032 frontend components parallel, backend depends on T027
- **US3**: T038-T040 email templates can be created in parallel
- **Cross-story**: US2 and US3 can proceed in parallel after US1 completes

---

## Parallel Example: User Story 1 (MVP)

```bash
# Launch all services together:
Task T012: "Create NotificationService in backend/app/services/notification_service.py"
Task T013: "Create SSEService in backend/app/services/sse_service.py"

# Launch all frontend components together:
Task T020: "Create notification-item.tsx"
Task T021: "Create notification-bell.tsx"
Task T022: "Create notification-dropdown.tsx"
Task T023: "Create notification-empty-state.tsx"
```

---

## Parallel Example: Email Templates (US3)

```bash
# All email templates can be created together:
Task T038: "Create task-overdue.tsx React Email template"
Task T039: "Create daily-digest.tsx React Email template"
Task T040: "Create weekly-summary.tsx React Email template"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T011) - CRITICAL
3. Complete Phase 3: User Story 1 (T012-T026)
4. **STOP and VALIDATE**: Test US1 independently
5. Deploy/demo In-App Notification Center

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. **Add US1** → Test independently → Deploy/Demo (MVP - In-App Center)
3. **Add US2** → Test independently → Deploy/Demo (+ Push Notifications)
4. **Add US3** → Test independently → Deploy/Demo (+ Email Notifications)
5. Each story adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T012-T026)
   - **Developer B**: User Story 2 (T027-T036) - waits for US1 notification infrastructure
   - **Developer C**: User Story 3 (T037-T050) - waits for US1 notification infrastructure
3. Stories complete and integrate independently

---

## Task Summary

| Phase | Tasks | Story | Focus |
|-------|-------|-------|-------|
| Phase 1: Setup | T001-T004 | - | Dependencies & Environment |
| Phase 2: Foundational | T005-T011 | All | Database Models |
| Phase 3: US1 In-App | T012-T026 | US1 | Notification Center |
| Phase 4: US2 Push | T027-T036 | US2 | Browser Push |
| Phase 5: US3 Email | T037-T050 | US3 | Email Notifications |
| Phase 6: Polish | T051-T063 | - | Cross-cutting |
| **Total** | **63 tasks** | 3 stories | Full notification system |

### Tasks per User Story

- **US1 (In-App)**: 15 tasks (T012-T026) - MVP
- **US2 (Push)**: 10 tasks (T027-T036)
- **US3 (Email)**: 14 tasks (T037-T050)

### Parallel Opportunities

- 24 tasks marked [P] can run in parallel within their phases
- US2 and US3 can proceed in parallel after US1 notification infrastructure

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US1/US2/US3] label maps task to user story for traceability
- Use Context7 for all external library questions:
  - Web Push: `/web-push-libs/web-push`
  - Resend: `/resend/resend-node`
  - SSE: `/sysid/sse-starlette`
  - TanStack Query: `/tanstack-query-guide`
  - FastAPI: `/fastapi-guide`
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
