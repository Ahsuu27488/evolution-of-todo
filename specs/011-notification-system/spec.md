# Feature Specification: Notification System

**Feature Branch**: `011-notification-system`
**Created**: 2026-01-27
**Status**: Ready
**Input**: User description: "create a full fledged notification system including emails, browser push, and an in app notification center. the notifications themes and vibes must match out app. therefore youu will have to take a deep look of our app the styles, themes, css should match too"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - In-App Notification Center (Priority: P1)

A user wants to see all their notifications in one place without leaving the app. They click a bell icon in the header to reveal a dropdown showing their notification history with unread indicators, timestamps, and quick actions.

**Why this priority**: This is the foundation of the notification system. It provides immediate value by giving users a centralized place to view all alerts, works entirely within the existing app, and doesn't require external service integration.

**Independent Test**: Can be fully tested by creating a task notification and verifying it appears in the bell dropdown with correct styling, unread status, timestamp, and dismiss functionality.

**Acceptance Scenarios**:

1. **Given** a user has 3 unread notifications, **When** they click the bell icon, **Then** a glassmorphism dropdown appears showing all 3 notifications with cyan glow indicators
2. **Given** a user views their notification dropdown, **When** they click on a notification, **Then** the notification is marked as read and the relevant page/task opens
3. **Given** a user has 0 unread notifications, **When** they view the bell icon, **Then** no badge/count is displayed
4. **Given** a user has 10+ notifications, **When** they open the dropdown, **Then** they see a scrollable list with "Load more" option after the first 10

---

### User Story 2 - Browser Push Notifications (Priority: P2)

A user wants to receive notifications even when the browser is minimized or they're on another tab. They grant permission and receive alerts for upcoming due dates and task reminders.

**Why this priority**: Push notifications extend the app's reach beyond the active session, helping users stay on top of deadlines. Requires browser permission flow but builds on P1 notification infrastructure.

**Independent Test**: Can be fully tested by granting permission, creating a task with due date, and verifying a push notification appears when the browser is backgrounded.

**Acceptance Scenarios**:

1. **Given** a user has granted push permission, **When** a task is due in 1 hour, **Then** a styled push notification appears with task title and "View Task" action
2. **Given** a user has not granted push permission, **When** they first enable notifications in settings, **Then** a browser permission prompt appears
3. **Given** a user receives a push notification, **When** they click it, **Then** the app opens to the relevant task with confetti animation
4. **Given** a user has denied push permission, **When** they visit notification settings, **Then** permission status shows "Denied" with instructions to enable in browser settings

---

### User Story 3 - Email Notifications (Priority: P3)

A user wants to receive email summaries and urgent alerts for their tasks. They configure their preferences and receive beautifully styled emails matching the Deep Space aesthetic.

**Why this priority**: Email ensures users never miss important updates even when not using the browser. Builds on notification infrastructure but requires external service integration.

**Independent Test**: Can be fully tested by configuring email preferences, triggering a notification event, and verifying the received email has correct content, styling, and links.

**Acceptance Scenarios**:

1. **Given** a user has enabled daily digest emails, **When** the scheduled time arrives, **Then** they receive an HTML email with due/overdue tasks summary
2. **Given** a user has enabled urgent alerts, **When** a task becomes overdue, **Then** they receive an immediate email notification with task details and action link
3. **Given** a user clicks "Unsubscribe" in an email, **When** the link opens, **Then** their email preferences are updated and a confirmation page displays
4. **Given** a user changes their email preference to "Digest only", **When** a real-time event occurs, **Then** no immediate email is sent (only included in next digest)

---

### Edge Cases

- What happens when a user has 1,000+ notifications? (System should paginate and archive old notifications after 30 days)
- How does system handle push notification delivery failures? (Queue for retry and fall back to in-app notification)
- What happens when email bounces? (Mark email as invalid, disable email notifications for that user, show in-app notice)
- How does system handle duplicate notification events? (Deduplicate within 5-minute window)
- What happens when user is offline? (Queue notifications for delivery when connection restored)
- How does system handle notification rate limits? (Implement exponential backoff, respect browser/email provider limits)
- What happens when a linked task is deleted? (Soft-delete the notification, show "Task no longer exists" when clicked)

## Requirements *(mandatory)*

### Functional Requirements

#### In-App Notification Center
- **FR-001**: System MUST display a bell icon in the header with unread notification count badge
- **FR-002**: System MUST render notification dropdown with Deep Space glassmorphism styling (backdrop-blur, rgba(20,20,30,0.85) background)
- **FR-003**: System MUST display unread notifications with cyan glow indicator (`oklch(0.91 0.17 195)`) matching task completion visual language
- **FR-004**: System MUST support notification types: task_due, task_overdue, task_assigned, task_completed, task_reminder, system_update
- **FR-005**: System MUST mark notifications as read when clicked or viewed in dropdown
- **FR-006**: System MUST allow users to dismiss notifications with swipe/delete animation matching task card disintegrate effect
- **FR-007**: System MUST display relative timestamps (e.g., "5m ago", "2h ago", "Yesterday") matching chat UI patterns
- **FR-008**: System MUST support "Mark all as read" action
- **FR-009**: System MUST paginate notification list at 10 items with smooth scroll loading animation
- **FR-010**: System MUST persist notification read status per user
- **FR-011**: System MUST animate notification dropdown entrance with slideInBottom variant matching existing modal animations

#### Browser Push Notifications
- **FR-012**: System MUST request browser push permission through a styled modal (not native prompt)
- **FR-013**: System MUST display permission status in notification settings (Granted, Denied, Not requested)
- **FR-014**: System MUST send push notifications for task_due (1 hour before), task_overdue (immediate), task_reminder (user-scheduled)
- **FR-015**: System MUST include action buttons in push notifications ("Complete", "Snooze", "View")
- **FR-016**: System MUST respect user's notification preferences (all, urgent only, none)
- **FR-017**: System MUST handle permission denial gracefully by showing in-app notifications as fallback
- **FR-018**: System MUST store push subscription per user for multi-device support
- **FR-019**: System MUST revoke push notifications when subscription becomes invalid
- **FR-020**: System MUST throttle push notifications to maximum 3 per hour per user (except urgent: task_overdue and task_due within 1 hour)

#### Email Notifications
- **FR-021**: System MUST send HTML emails matching Deep Space visual theme (dark background, cyan/purple accents, glassmorphism cards)
- **FR-022**: System MUST support email notification types: immediate (urgent), daily digest (6 AM user time), weekly summary (Monday 9 AM)
- **FR-023**: System MUST include one-click unsubscribe link in all emails
- **FR-024**: System MUST include actionable links in emails (Complete task, View task, Snooze)
- **FR-025**: System MUST handle bounced emails by disabling email notifications for that user
- **FR-026**: System MUST allow users to customize email frequency in settings
- **FR-027**: System MUST use Resend email service for delivery
- **FR-028**: System MUST respect user's timezone for digest scheduling
- **FR-029**: System MUST include plain text version for accessibility
- **FR-030**: System MUST verify email ownership before sending notifications (already verified from signup)

#### Cross-Channel Features
- **FR-031**: System MUST deduplicate notifications across channels (no push AND email for same event)
- **FR-032**: System MUST allow users to configure channel preferences per notification type
- **FR-033**: System MUST provide notification settings page with toggles for each type and channel
- **FR-034**: System MUST log all notification deliveries for audit and debugging
- **FR-035**: System MUST archive notifications older than 30 days from active view
- **FR-036**: System MUST support "Do not disturb" hours during which only urgent notifications are sent (task_overdue and task_due within 1 hour)

### Key Entities

- **Notification**: Represents a single alert event with id, user_id, type (task_due, task_overdue, etc.), title, message, data (JSON), read_status, created_at, sent_channels (array), related_task_id
- **NotificationPreference**: User's notification settings with id, user_id, notification_type, channel_enabled (in_app, push, email), frequency (immediate, daily, weekly), do_not_disturb_start, do_not_disturb_end
- **PushSubscription**: Browser push subscription with id, user_id, subscription_json, device_info, created_at, last_used_at
- **EmailDeliveryLog**: Email delivery tracking with id, notification_id, email, status (sent, delivered, bounced, opened), opened_at, clicked_at

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open notification center and see all notifications within 500ms
- **SC-002**: Push notifications are delivered within 10 seconds of trigger event
- **SC-003**: Email notifications are delivered within 30 seconds of trigger event
- **SC-004**: 95% of users successfully enable at least one notification channel within first week
- **SC-005**: Unread notification count badge displays within 200ms of new notification arrival
- **SC-006**: Users can mark all notifications as read with single click
- **SC-007**: Notification dropdown supports smooth scrolling through 100+ notifications without lag
- **SC-008**: Email open rate exceeds 40% for digest emails
- **SC-009**: Push notification click-through rate exceeds 25%
- **SC-010**: Zero notification spam (user can disable all non-urgent notifications)
- **SC-011**: System supports 10,000 concurrent notification deliveries without degradation
- **SC-012**: Visual design passes consistency review with 100% adherence to Deep Space theme (colors, animations, glassmorphism)

## Assumptions & Decisions

### User Choices from Clarification

| Question | Decision | Rationale |
|----------|----------|-----------|
| Urgent notifications | Task overdue + task due within 1 hour | Balance between staying informed and avoiding notification fatigue |
| Email service | Resend | Modern API with generous free tier (3,000 emails/month) and excellent templates |
| Retention policy | 30 days active, then archive | Lower storage requirements and faster query performance for typical user activity |

### Additional Assumptions

- Users have verified email addresses from signup (no additional verification needed)
- Browser push notifications require explicit user permission through a styled modal
- Notifications are user-scoped (no team/collaborator notifications in this feature)
- "Archived" notifications remain in database but excluded from active queries
- Timezone for digest scheduling is derived from user's profile or browser settings
