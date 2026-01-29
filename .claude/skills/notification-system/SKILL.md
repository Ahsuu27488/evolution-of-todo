# Notification System Mastery

**name**: notification-system
**description**: Expert implementation of complete notification systems covering in-app (SSE), browser push (Web Push + VAPID), and email (Resend). Includes architecture patterns, key generation, service workers, webhook handling, and production best practices.

**allowed-tools**: [Read, Write, Edit, Glob, Grep, Bash, Task]

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NOTIFICATION ECOSYSTEM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │   Client     │  │   Client     │  │   Client     │                      │
│  │   Browser    │  │   Browser    │  │   Email App  │                      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                      │
│         │                 │                 │                               │
│         ▼                 ▼                 ▼                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NotificationGateway                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │   │
│  │  │ In-App (SSE)│ │ Push (VAPID)│ │  Email      │               │   │
│  │  │ Real-time   │ │ Browser     │ │  Resend     │               │   │
│  │  │ EventStream │ │ ServiceWorker│ │  SMTP/API   │               │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                         │
│                              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NotificationDispatcher                         │   │
│  │  - Checks user preferences                                        │   │
│  │  - Applies rate limits (push: 3/hour, urgent exempt)              │   │
│  │  - Deduplicates within 5-min window                               │   │
│  │  - Tracks delivery across all channels                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                         │
│                              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      Database Layer                                 │   │
│  │  notifications | notification_preferences                         │   │
│  │  push_subscriptions | email_delivery_logs                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Server-Sent Events (SSE) with sse-starlette

### Theoretical Foundation

**SSE** is a unidirectional push technology where servers maintain long-lived HTTP connections and send text/event-stream formatted data. Unlike WebSocket, SSE:
- Uses standard HTTP (no handshake overhead)
- Has built-in automatic reconnection
- Is text-only (no binary)
- Supports named events and IDs

### Implementation Pattern (FastAPI + sse-starlette)

**Context7 Reference**: `/sysid/sse-starlette` - 92.4 benchmark score

```python
from sse_starlette import EventSourceResponse, ServerSentEvent
from fastapi import Request
import asyncio

# Broadcast to multiple clients
class MessageBroadcaster:
    def __init__(self):
        self._clients: list[asyncio.Queue] = []

    def add_client(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._clients.append(queue)
        return queue

    def remove_client(self, queue: asyncio.Queue):
        if queue in self._clients:
            self._clients.remove(queue)

    async def broadcast(self, message: str, event: str | None = None):
        sse_event = ServerSentEvent(data=message, event=event)
        for queue in self._clients:
            try:
                queue.put_nowait(sse_event)
            except asyncio.QueueFull:
                self.remove_client(queue)

broadcaster = MessageBroadcaster()

# Async generator for SSE stream
async def event_stream(request: Request, user_id: str):
    try:
        while True:
            if await request.is_disconnected():
                break

            # Wait for events or send heartbeat
            yield {"event": "heartbeat", "data": f"ping:{user_id}"}
            await asyncio.sleep(30)
    except asyncio.CancelledError:
        pass

@app.get("/api/notifications/stream")
async def notification_stream(request: Request):
    return EventSourceResponse(
        event_stream(request, user_id),
        send_timeout=30,  # Prevent hanging connections
        headers={"Cache-Control": "no-cache"}
    )
```

### Client-Side EventSource Pattern

```typescript
// Auto-reconnecting SSE client
const eventSource = new EventSource('/api/notifications/stream')

eventSource.addEventListener('notification_created', (e) => {
  const notification = JSON.parse(e.data)
  // Update UI cache
  queryClient.setQueryData(['notifications'], (old) => [...old, notification])
})

eventSource.addEventListener('notification_read', (e) => {
  const { id, read_status } = JSON.parse(e.data)
  // Optimistic update
  queryClient.setQueryData(['notifications'], (old) =>
    old.map(n => n.id === id ? { ...n, read_status } : n)
  )
})

// Cleanup on unmount
return () => eventSource.close()
```

**Critical**: Always check `request.is_disconnected()` in async generators to prevent memory leaks from orphaned connections.

---

## Part 2: Web Push with VAPID Authentication

### Theoretical Foundation

**VAPID** (Voluntary Application Server Identification) uses ECDSA on the P-256 curve to generate cryptographic keypairs:
- **Private Key**: Signs JWT claims for push service authentication
- **Public Key**: Embedded in JWT header for verification
- **Application Server Key**: Uncompressed point (X962 encoding) for browser subscription

**Key Format Mismatch Warning**: The frontend requires a DIFFERENT encoding than the backend:
- Frontend: Uncompressed point (X962) → Base64url
- Backend: Raw 32-byte scalar → Base64url

### Key Generation with py_vapid

**Context7 Reference**: `/web-push-libs/vapid` - 71 benchmark score

```python
from py_vapid import Vapid02 as Vapid
from cryptography.hazmat.primitives import serialization
from py_vapid import b64urlencode
import base64

# 1. Generate ECDSA P-256 keypair
vapid = Vapid()
vapid.generate_keys()

# 2. Get Application Server Key (for frontend/browser)
raw_pub = vapid.public_key.public_bytes(
    serialization.Encoding.X962,
    serialization.PublicFormat.UncompressedPoint
)
app_server_key = b64urlencode(raw_pub)
print(f"NEXT_PUBLIC_VAPID_PUBLIC_KEY={app_server_key}")

# 3. Get Private Key (for backend/pywebpush)
private_numbers = vapid.private_key.private_numbers()
private_value = private_numbers.private_value
private_bytes = private_value.to_bytes(32, byteorder='big')
vapid_private_key = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')
print(f"VAPID_PRIVATE_KEY={vapid_private_key}")

# 4. Get Public Key (for backend verification)
public_numbers = vapid.public_key.public_numbers()
public_bytes = public_numbers.x.to_bytes(32, 'big') + public_numbers.y.to_bytes(32, 'big')
vapid_public_key = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')
print(f"VAPID_PUBLIC_KEY={vapid_public_key}")
```

**CLI Alternative**:
```bash
# Generate keys
python -m py_vapid.main --gen

# Get application server key
python -m py_vapid.main --applicationServerKey
```

### Push Subscription Flow

```javascript
// Frontend: Subscribe to push
const registration = await navigator.serviceWorker.ready
const subscription = await registration.pushManager.subscribe({
  userVisibleOnly: true,
  applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY
})

// Send to backend
await fetch('/api/notifications/push/subscribe', {
  method: 'POST',
  body: JSON.stringify({
    subscription: subscription.toJSON(),
    device_info: { userAgent: navigator.userAgent, platform: navigator.platform }
  })
})
```

```python
# Backend: Send push notification
from pywebpush import webpush

subscription_data = {  # From database
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": { "p256dh": "...", "auth": "..." }
}

webpush(
  subscription_info=subscription_data,
  data=json.dumps({"title": "Task Due", "body": "Complete your task"}),
  vapid_private_key=os.getenv("VAPID_PRIVATE_KEY"),
  vapid_claims={"sub": "mailto:admin@example.com"},
  timeout=5
)
```

### Service Worker Implementation

```javascript
// sw.js - Handle incoming push
self.addEventListener('push', (event) => {
  if (!event.data) return

  const data = event.data.json()
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/icon.png',
      badge: '/badge.png',
      data: { url: data.url || '/dashboard' },
      tag: data.tag || 'default',
      requireInteraction: data.urgent || false,
      vibrate: data.urgent ? [200, 100, 200] : undefined
    })
  )
})

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url || '/dashboard'
  event.waitUntil(
    clients.openWindow(url) ||
    clients.matchAll({ type: 'window' }).then(clients => {
      for (const client of clients) {
        if (client.url.includes(url.split('?')[0])) {
          return client.focus()
        }
      }
      return clients[0]?.openWindow(url)
    })
  )
})
```

### Rate Limiting Pattern

Per spec, limit to 3 push/hour but exempt urgent notifications (overdue, due within 1 hour):

```python
_urgent_types = {NotificationType.TASK_OVERDUE, NotificationType.TASK_DUE}
_rate_limit_window = timedelta(hours=1)

def _check_rate_limit(user_id: str, notification_type: NotificationType) -> bool:
    if notification_type in _urgent_types:
        return True  # Exempt from rate limit

    recent = [ts for ts in _rate_tracker.get(user_id, [])
              if datetime.utcnow() - ts < _rate_limit_window]

    if len(recent) >= 3:
        return False

    _rate_tracker[user_id] = recent + [datetime.utcnow()]
    return True
```

---

## Part 3: Email Notifications with Resend

### Theoretical Foundation

**Resend** provides a modern email API with:
- Transactional sending via REST API
- Batch sending (up to 100 emails/request)
- Webhook events for delivery tracking
- Idempotency keys for deduplication

### Configuration and Initialization

**Context7 Reference**: `/resend/resend-python` - 89.6 benchmark score

```python
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")
DEFAULT_SENDER = "YourApp <noreply@yourdomain.com>"
```

### Sending Emails

```python
# Single email
params: resend.Emails.SendParams = {
    "from": DEFAULT_SENDER,
    "to": ["user@example.com"],
    "subject": "Task Overdue",
    "html": "<h1>Your task is overdue</h1>",
    "tags": [{"name": "category", "value": "todo_overdue"}]
}

email = resend.Emails.send(params)
# Returns: {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}
```

### Exception Handling Hierarchy

```python
import resend.exceptions

try:
    email = resend.Emails.send(params)
except resend.exceptions.MissingApiKeyError:
    # API key not set
    logger.critical("RESEND_API_KEY missing")
except resend.exceptions.InvalidApiKeyError:
    # API key invalid
    logger.error("RESEND_API_KEY invalid")
except resend.exceptions.ValidationError as e:
    # Email validation failed (4xx)
    logger.warning(f"Email validation failed: {e.message}, code: {e.code}")
except resend.exceptions.RateLimitError:
    # Rate limited (429)
    logger.warning("Resend rate limit exceeded")
    # Implement exponential backoff
except resend.exceptions.ApplicationError as e:
    # Server error (5xx)
    logger.error(f"Resend server error: {e.message}")
    # Retry with backoff
```

### Webhook Verification and Handling

Resend uses Svix for webhook signing. Verify signatures to prevent forgery:

```python
@app.post("/api/notifications/webhooks/resend")
async def resend_webhook(request: Request):
    body = await request.body()
    headers = {
        "svix-id": request.headers.get("svix-id"),
        "svix-timestamp": request.headers.get("svix-timestamp"),
        "svix-signature": request.headers.get("svix-signature"),
    }

    try:
        resend.Webhooks.verify({
            "payload": body,
            "headers": headers,
            "webhook_secret": os.getenv("RESEND_WEBHOOK_SECRET")
        })
    except ValueError:
        return {"error": "Invalid signature"}, 400

    event = json.loads(body)

    # Handle event types
    if event["type"] == "email.delivered":
        await mark_email_delivered(event["data"]["email_id"])
    elif event["type"] == "email.bounced":
        await disable_email_for_user(event["data"]["to"][0]["email"])
    elif event["type"] == "email.opened":
        await track_email_open(event["data"]["email_id"])

    return {"status": "processed"}
```

### Idempotency Pattern

Prevent duplicate emails on retry:

```python
from resend import Batch

options: resend.Batch.SendOptions = {
    "idempotency_key": f"daily-digest-{user_id}-{date}",
    "batch_validation": "permissive"
}

result = Batch.send(params, options)
# Subsequent calls with same key return same email_id
```

---

## Database Schema

### Core Tables

```sql
-- notifications: Primary event log
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    type notificationtype NOT NULL,
    title VARCHAR(200) NOT NULL,
    message VARCHAR(1000) NOT NULL,
    data JSONB DEFAULT '{}',
    related_task_id INTEGER REFERENCES tasks(id),
    read_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    sent_channels JSONB DEFAULT '[]',
    deleted_at TIMESTAMP  -- Soft delete for 30-day archive
);

-- Indexes for performance
CREATE INDEX ix_notifications_user_created ON notifications(user_id, created_at DESC, deleted_at);
CREATE INDEX ix_notifications_unread ON notifications(read_status, created_at) WHERE deleted_at IS NULL;

-- notification_preferences: Per-user settings
CREATE TABLE notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    notification_type notificationtype NOT NULL,
    in_app_enabled BOOLEAN DEFAULT TRUE,   -- Cannot disable
    push_enabled BOOLEAN DEFAULT FALSE,    -- Opt-in required
    email_enabled BOOLEAN DEFAULT FALSE,   -- Opt-in required
    frequency emailfrequency DEFAULT 'IMMEDIATE',
    dnd_start VARCHAR(5),  -- HH:MM format
    dnd_end VARCHAR(5),
    UNIQUE(user_id, notification_type)
);

-- push_subscriptions: Browser push subscriptions
CREATE TABLE push_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    subscription JSONB NOT NULL,  -- Full PushSubscription object
    device_info JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP DEFAULT NOW(),
    is_valid BOOLEAN DEFAULT TRUE
);

-- email_delivery_logs: Delivery tracking
CREATE TABLE email_delivery_logs (
    id SERIAL PRIMARY KEY,
    notification_id INTEGER REFERENCES notifications(id),
    email VARCHAR NOT NULL,
    status emaildeliverystatus DEFAULT 'SENT',
    sent_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    error_message VARCHAR(500),
    error_code VARCHAR(50)
);
```

---

## Common Pitfalls and Solutions

### 1. VAPID Key Format Errors
**Symptom**: `TypeError: Failed to fetch` or `InvalidRegistration`
**Cause**: Frontend and backend key format mismatch
**Solution**: Use `py_vapid` tool to generate both formats correctly:
```bash
python -m py_vapid.main --applicationServerKey  # Frontend
# Manually extract private key from PEM for backend
```

### 2. SSE Memory Leaks
**Symptom**: Memory usage grows over time
**Cause**: Not checking for client disconnection
**Solution**: Always check `await request.is_disconnected()` in async generators

### 3. Push Subscription Lost
**Symptom**: Push fails with 410 Gone
**Cause**: Subscription expired or user revoked permission
**Solution**: Mark `is_valid=False` in database, prompt user to re-subscribe

### 4. Email Bounce Loop
**Symptom**: Continuously sending to bounced addresses
**Cause**: Not processing bounce webhooks
**Solution**: Set `email_enabled=False` on bounce per spec FR-025

### 5. SSE Connection Timeout
**Symptom**: Clients disconnect after ~30 seconds
**Cause**: No heartbeat messages
**Solution**: Send ping every 30 seconds to keep connection alive

---

## Testing Checklist

- [ ] SSE: Client connects and receives events
- [ ] SSE: Automatic reconnection on disconnect
- [ ] SSE: Memory cleanup on disconnect
- [ ] Push: VAPID keys match between frontend/backend
- [ ] Push: Permission modal shows on first visit
- [ ] Push: Notification arrives when browser backgrounded
- [ ] Push: Click navigates to correct URL
- [ ] Push: Rate limit enforced (3/hour non-urgent)
- [ ] Push: Urgent notifications bypass rate limit
- [ ] Email: Send succeeds with valid template
- [ ] Email: Bounce webhook disables user email
- [ ] Email: Unsubscribe link works
- [ ] Deduplication prevents duplicate notifications
- [ ] Soft-deleted notifications excluded from queries

---

## Context7 Reference Commands

When implementing this system, use these Context7 queries for specific edge cases:

```bash
# VAPID key troubleshooting
/context7 /web-push-libs/vapid "key formats ECDSA P-256"

# SSE advanced patterns
/context7 /sysid/sse-starlette "broadcasting multiple clients"

# Resend error handling
/context7 /resend/resend-python "exception handling rate limits"

# Service worker patterns
/context7 /websites/resend "service worker registration"
```

---

## Production Checklist

- [ ] VAPID keys generated and stored securely
- [ ] Resend domain verified and sender email configured
- [ ] Webhook secret configured and stored
- [ ] Database indexes created for notification queries
- [ ] Soft-delete cleanup job scheduled (30-day retention)
- [ ] Push subscription cleanup job scheduled
- [ ] SSE heartbeat implemented (30-second interval)
- [ ] Error monitoring configured for all services
- [ ] Rate limiting implemented and tested
- [ ] Idempotency keys used for critical emails
