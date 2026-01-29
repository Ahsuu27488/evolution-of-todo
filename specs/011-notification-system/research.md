# Research: Notification System

**Feature**: 011-notification-system
**Date**: 2026-01-27
**Source**: Context7 MCP Documentation (Primary Source of Truth per Constitution §III.1)

## Executive Summary

Research completed for all three notification channels using Context7 documentation. Key decisions:

| Technology | Decision | Rationale |
|------------|----------|-----------|
| Web Push | `web-push` npm library | Node.js library with VAPID support, 97.1 benchmark score |
| Email | Resend Node.js SDK | Per spec decision, React email templates supported |
| Real-time | SSE Starlette (FastAPI) | Production-ready SSE for FastAPI, 92.4 benchmark |
| UI Components | Radix UI DropdownMenu | Already in use, shadcn/ui compatible |

---

## 1. Web Push Notifications (Browser)

### Library: `web-push` (web-push-libs/web-push)

**Source**: Context7 documentation

**Decision**: Use `web-push` npm library for server-side push notification delivery.

**Key Patterns from Documentation**:

#### VAPID Key Generation (One-Time Setup)
```javascript
const webpush = require('web-push');
const vapidKeys = webpush.generateVAPIDKeys();
// Store publicKey and privateKey in environment variables
```

#### Client-Side Subscription Pattern
```javascript
// Register service worker and subscribe
navigator.serviceWorker.register('/service-worker.js')
  .then(registration => registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
  }))
  .then(subscription => {
    // Send subscription to backend
    fetch('/api/push/subscribe', {
      method: 'POST',
      body: JSON.stringify(subscription)
    });
  });
```

#### Server-Side Send Pattern
```javascript
webpush.setVapidDetails(
  'mailto:admin@example.com',
  VAPID_PUBLIC_KEY,
  VAPID_PRIVATE_KEY
);

const payload = JSON.stringify({
  title: 'Task Due Soon',
  body: 'Complete task within 1 hour',
  icon: '/icon.png',
  data: { taskId: '123', url: '/dashboard' }
});

await webpush.sendNotification(pushSubscription, payload, {
  TTL: 3600,
  urgency: 'high'
});
```

**Error Handling Patterns**:
- `410` / `404`: Subscription expired → remove from database
- `429`: Rate limited → retry with exponential backoff

**Alternatives Considered**:
- Pusher Beams: Third-party service, adds dependency/cost
- Firebase Cloud Messaging: Google-specific, VAPID is standard

---

## 2. Email Notifications (Resend)

### Library: Resend Node.js SDK

**Source**: Context7 documentation

**Decision**: Use Resend Node.js SDK with React email templates (per spec requirement).

**Key Patterns from Documentation**:

#### Basic Send Pattern
```javascript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

await resend.emails.send({
  from: 'notifications@chronos-todo.app',
  to: user.email,
  subject: 'Task Overdue',
  react: <TaskOverdueEmail task={task} />
});
```

#### React Email Template Pattern
```javascript
function TaskOverdueEmail({ task }) {
  return jsx('div', {
    style: { backgroundColor: '#0a0a14', color: '#fff' },
    children: [
      jsx('h1', { children: 'Task Overdue' }),
      jsx('p', { children: task.title }),
      jsx('a', {
        href: `https://app.example.com/tasks/${task.id}`,
        style: {
          backgroundColor: '#00f5ff',
          color: '#000',
          padding: '10px 20px'
        },
        children: 'Complete Task'
      })
    ]
  });
}
```

#### Webhook Setup for Bounce Handling
```javascript
// Create webhook
await resend.webhooks.create({
  url: 'https://api.example.com/webhooks/resend',
  events: ['email.sent', 'email.delivered', 'email.bounced', 'email.opened']
});

// Verify webhook signature
const event = resend.webhooks.verify({
  payload: rawBody,
  headers: {
    id: req.headers['svix-id'],
    timestamp: req.headers['svix-timestamp'],
    signature: req.headers['svix-signature']
  },
  webhookSecret: process.env.RESEND_WEBHOOK_SECRET
});
```

**Alternatives Considered**:
- SendGrid: Lower free tier (100/day vs 3,000)
- AWS SES: More infrastructure setup required

---

## 3. Real-Time Notifications (SSE)

### Library: SSE Starlette for FastAPI

**Source**: Context7 documentation

**Decision**: Use Server-Sent Events (SSE) via `sse-starlette` for real-time in-app notifications.

**Key Patterns from Documentation**:

#### FastAPI SSE Endpoint Pattern
```python
from sse_starlette import EventSourceResponse
from fastapi import FastAPI, Request

app = FastAPI()

async def event_stream(request: Request):
    """Stream notifications to client."""
    counter = 0
    try:
        while True:
            if await request.is_disconnected():
                break

            # Yield notification event
            yield {
                "data": {"id": "123", "title": "New notification"},
                "event": "notification",
                "id": str(counter)
            }
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        raise

@app.get("/notifications/stream")
async def notifications_stream(request: Request):
    return EventSourceResponse(
        event_stream(request),
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache"
        },
        ping=15  # Keep-alive ping every 15 seconds
    )
```

#### Client-Side EventSource Pattern
```javascript
const eventSource = new EventSource('/api/notifications/stream');

eventSource.addEventListener('notification', (event) => {
  const notification = JSON.parse(event.data);
  // Update UI with new notification
});

eventSource.onerror = () => {
  // Handle reconnection
};
```

**Alternatives Considered**:
- WebSocket: Bidirectional, overkill for server→client notifications
- Polling: Higher latency, more server load

---

## 4. UI Components (Notification Bell & Dropdown)

### Library: Radix UI DropdownMenu

**Source**: Context7 documentation

**Decision**: Use existing Radix UI DropdownMenu with Badge for notification bell.

**Key Patterns from Documentation**:

#### DropdownMenu with Badge Pattern
```tsx
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

<DropdownMenu.Root>
  <DropdownMenu.Trigger asChild>
    <Button variant="ghost" size="icon">
      <Bell className="h-5 w-5" />
      {unreadCount > 0 && (
        <Badge className="absolute -top-1 -right-1 h-5 w-5">
          {unreadCount}
        </Badge>
      )}
    </Button>
  </DropdownMenu.Trigger>
  <DropdownMenu.Content>
    <DropdownMenu.Label>Notifications</DropdownMenu.Label>
    <DropdownMenu.Separator />
    {/* Notification items */}
  </DropdownMenu.Content>
</DropdownMenu.Root>
```

**Alternatives Considered**:
- Popover: Similar functionality, DropdownMenu more semantic for lists

---

## 5. Service Worker Pattern (Push Notifications)

### Service Worker Registration

**Pattern from Web Push documentation**:

```javascript
// public/sw.js
self.addEventListener('push', (event) => {
  const data = event.data.json();

  const options = {
    body: data.body,
    icon: data.icon,
    badge: data.badge,
    data: { url: data.url }
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
```

---

## 6. Database Schema Considerations

From spec requirements and research:

| Table | Purpose |
|-------|---------|
| `notifications` | Store all notification events |
| `notification_preferences` | Per-user channel/type settings |
| `push_subscriptions` | Browser push subscriptions per user/device |
| `email_delivery_logs` | Track email delivery status |

**Key Indexes**:
- `notifications`: (user_id, created_at DESC), (read_status)
- `push_subscriptions`: (user_id), (endpoint)
- `email_delivery_logs`: (notification_id), (status)

---

## 7. Performance & Scaling Considerations

From research and spec requirements:

| Concern | Solution |
|---------|----------|
| 500ms response time (SC-001) | Pagination, indexed queries |
| 10k concurrent deliveries (SC-011) | Background task queue (Celery/fastapi-background) |
| Deduplication (FR-031) | 5-minute window cache with user+type key |
| 30-day archive (FR-035) | Scheduled job or partial index |

---

## 8. Security Considerations

| Threat | Mitigation |
|--------|------------|
| Push subscription hijacking | Verify user owns subscription endpoint |
| Webhook spoofing | Verify Svix signatures |
| Notification enumeration | 404 instead of 403 for ownership checks |
| Rate limit abuse | Exponential backoff, per-user quotas |

---

## 9. Deep Space Theme Integration

From earlier codebase exploration:

| Element | Value |
|---------|-------|
| Glassmorphism | `backdrop-blur`, `rgba(20,20,30,0.85)` |
| Cyan glow | `oklch(0.91 0.17 195)` (#00f5ff) |
| Animation | `slideInBottom`, `disintegrate` |
| Badge color | Destructive red for urgent, cyan for normal |

---

## 10. Open Questions Resolved

All clarification questions from spec have been answered:

| # | Question | Answer |
|---|----------|--------|
| Q1 | Urgent notifications | task_overdue + task_due within 1 hour |
| Q2 | Email service | Resend |
| Q3 | Retention | 30 days active, then archive |

---

## References

- Web Push Library: /web-push-libs/web-push
- Resend Node.js: /resend/resend-node
- SSE Starlette: /sysid/sse-starlette
- Radix UI: /radix-ui/website
- Constitution: `.specify/memory/constitution.md` (Context7 Primary Source Mandate)
