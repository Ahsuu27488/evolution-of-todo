● 📊 Notification Delivery Timing Report

  What's Working ✅
  ┌────────────────────┬─────────────────────────────────┬────────────────────┬───────────────────────┐
  │      Channel       │             Trigger             │       Timing       │        Status         │
  ├────────────────────┼─────────────────────────────────┼────────────────────┼───────────────────────┤
  │ In-App (SSE)       │ Any notification creation       │ <200ms (immediate) │ ✅ Real-time          │
  ├────────────────────┼─────────────────────────────────┼────────────────────┼───────────────────────┤
  │ Push Notifications │ Task creation, completion       │ Immediate          │ ✅ Working            │
  ├────────────────────┼─────────────────────────────────┼────────────────────┼───────────────────────┤
  │ Email (Immediate)  │ Task creation, completion       │ <30s (Resend)      │ ✅ Working            │
  ├────────────────────┼─────────────────────────────────┼────────────────────┼───────────────────────┤
  │ Email Digest       │ Daily at 8:00 AM                │ Scheduled          │ ⏳ Requires scheduler │
  ├────────────────────┼─────────────────────────────────┼────────────────────┼───────────────────────┤
  │ Email Summary      │ Mondays at 9:00 AM              │ Scheduled          │ ⏳ Requires scheduler │
  ├────────────────────┼─────────────────────────────────┼────────────────────┼───────────────────────┤
  │ Task Reminders     │ Hourly check for tasks due <1hr │ Check: hourly      │ ⏳ Requires scheduler │
  └────────────────────┴─────────────────────────────────┴────────────────────┴───────────────────────┘
  ---
  Missing Triggers (Not Sending) 🚨
  ┌─────────────────────────────────────────────┬───────────────────┬────────────────────────────┐
  │                    Event                    │    Should Send    │         Currently          │
  ├─────────────────────────────────────────────┼───────────────────┼────────────────────────────┤
  │ Task updated (title, description, due date) │ Push notification │ ❌ Not triggered           │
  ├─────────────────────────────────────────────┼───────────────────┼────────────────────────────┤
  │ Task deleted                                │ Notification      │ ❌ Not triggered           │
  ├─────────────────────────────────────────────┼───────────────────┼────────────────────────────┤
  │ Task becomes overdue                        │ Immediate alert   │ ❌ Only hourly check       │
  ├─────────────────────────────────────────────┼───────────────────┼────────────────────────────┤
  │ Task assigned (multi-user)                  │ Notification      │ ❌ Feature not implemented │
  └─────────────────────────────────────────────┴───────────────────┴────────────────────────────┘
  ---
  Timing Characteristics
  ┌───────────────────────┬──────────────────────────────────────────────┐
  │   Notification Type   │                    Timing                    │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ Immediate (real-time) │ In-app, Push, Email on task create/complete  │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ Hourly checks         │ Task due reminders, Task overdue detection   │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ Scheduled             │ Daily digest (8am), Weekly summary (Mon 9am) │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ Rate limited          │ Push: max 3/hour (urgent exempt)             │
  └───────────────────────┴──────────────────────────────────────────────┘
  ---
  Potential Delays
  ┌───────────────────────────┬─────────────────────────────────┬────────────────────┐
  │           Area            │         Potential Delay         │       Impact       │
  ├───────────────────────────┼─────────────────────────────────┼────────────────────┤
  │ Scheduler not running     │ No digests/reminders            │ High               │
  ├───────────────────────────┼─────────────────────────────────┼────────────────────┤
  │ Hourly reminder check     │ Up to 59min delay for reminders │ Medium             │
  ├───────────────────────────┼─────────────────────────────────┼────────────────────┤
  │ Email sending             │ 5-30s (Resend API)              │ Low                │
  ├───────────────────────────┼─────────────────────────────────┼────────────────────┤
  │ Push subscription expired │ Failed delivery                 │ User action needed │
  └───────────────────────────┴─────────────────────────────────┴────────────────────┘
  ---
  Bottom Line

  What Works Now:
  - ✅ Real-time in-app notifications (SSE)
  - ✅ Push notifications on task create/complete
  - ✅ Email notifications on task create/complete
  - ✅ Test email/push buttons work

  Requires Scheduler Running:
  - ⏳ Daily/weekly email digests
  - ⏳ Task due reminders (hourly check)
  - ⏳ Task overdue detection (hourly check)

  To fully test timing, you need to:
  1. Ensure the scheduler service is running
  2. Create tasks with due dates to trigger reminders
  3. Wait for the hourly/daily/weekly scheduled jobs