# Changelog

> Newest first. Each entry: date, commit (or "uncommitted"), what changed, and for fixes the root cause.
> This is the history; STATUS.md holds only the current truth.

## 2026-10-28 · feat: emails, push and in-app notifications on the new design

- **Email templates** (`EmailTemplates` in `services/email_service.py`): all six (due soon, overdue, new
  task, daily digest, weekly summary, welcome) plus a generic `message()` rebuilt on the night-observatory
  palette in email-safe hex (D-009): table layout, day-sky light by default and ink for dark-mode clients,
  app icon header, status as a small label, one gold button, no emoji, gradients or Title Case. The old
  dark mode left the welcome email's feature headings dark-on-dark (invisible). Subjects lose their emoji
  ("Due soon: …", "Overdue: …", "Your tasks for Wednesday 28 October", "Welcome to Chronos, Ayla").
- **Task titles were inserted into email HTML unescaped**; every user-provided string is now escaped.
  **Due dates printed as raw ISO** (`2026-10-29T17:00:00`); `friendly_due()` formats them ("Thu 29 Oct, 17:00").
  The welcome email's invented `support@chronostodo.com` address is gone.
- **Push icons were missing**: payloads defaulted to `/favicon.png`, which does not exist; they now use
  `/icon-192.png` and the monochrome `/badge-96.png`. Service worker default title "Chronos".
- Notification copy: "Due soon: …" / "Added: …" / "Done: …" with the due time as the body (was "Task Due
  Soon: X" plus "Your task 'X' is due soon"); test email and test push reworded, no emoji.
- Unsubscribe result pages (success and expired link) share one themed page (light and dark) instead of two
  gradient pages.
- Kairos's MCP tool schemas told it to colour tags `#00f5ff` / `#a855f7`, contradicting its prompt palette;
  they now list the same palette as `prompts.py`.
- Tests: `tests/test_email_templates.py` (palette, no emoji, escaping, unsubscribe link, date format, status
  page). Previews: `backend/scripts/render_emails.py` writes every email to HTML and screenshots it.

## 2026-10-28 · feat(frontend): notifications, settings, profile, account menu, error screen, chat pieces

- Notification menu: solid surface, rows instead of glass cards, type icons in status tints, gold unread
  dot (was a cyan border and glow), skeleton loading, error with retry, "Show more" that keeps earlier rows
  (it replaced them: the offset moved instead of the page growing), one "Notification settings" link (the
  cyan "Push Settings" link is gone). Rows, "Mark all read" and "Show more" are menu items, so the keyboard
  reaches them (Radix menus block Tab; the old buttons were unreachable). The bell is one shared
  `NotificationBell` with a gold count badge (was `rose-500`, and an unused duplicate).
- Push permission prompt rebuilt on the shared Dialog (was a cyan gradient icon and gradient button); shows
  a hint when the browser blocks it.
- Notification settings: "Notifications" page with a back link; tabs kept in `?tab=`; `SettingsSection` /
  `SettingsRow` frame; push, email and in-app tabs use `Badge` and `Callout` (emerald / rose / amber
  removed); email rows are a frequency select plus a switch, with a floating save bar for unsaved changes,
  skeleton loading and retry on error; time zone options show region and offset in the list only.
- Profile: left-aligned page with a back link, "Your name" section, first/last name side by side, read-only
  email, Save enabled only after a change, stays on the page after saving.
- Account menu: initials avatar, name and email header, real links (Profile, Notification settings),
  sign-out spinner. Theme switch: radio group with a sliding active pill, 36-40 px targets.
- Error screen: calm card with "Try again" and "Go to my tasks" and the error reference.
- Chat: inline task chips and task cards on tokens (dot priority, no `rgba` / `red-300` / gradient bars, no
  `confirm()`), skeleton shaped like the real messages (its shimmer keyframes never ran), voice button as a
  44 px circle (destructive while recording, gold when ready to send), `text-red-400` errors replaced.
- Copy: sentence case and plain verbs across these surfaces ("Confirm password", "Send a test", "Not now").

## 2026-10-28 · feat(frontend): task dialog, menus, tags and dashboard states; fix: error card never showed

- **Task list never showed its error card**: the tasks query returned a failed `Result` instead of throwing,
  so React Query saw success and the list fell through to the empty state ("No tasks yet") when the API was
  down. `useTaskFilters` and `useOrbitCounts` (same query key) now throw; the error card shows after the
  client's retries.
- **Clearing a due date failed validation** (`null` rejected by the create schema); `due_date` and
  `recurrence_pattern` accept `null`, and "Doesn't repeat" is now a choice. The backend still ignores `null`
  on update, so clearing a date on an existing task does not remove it yet (Known gaps).
- **Delete confirmation closed before "Deleting" could show**; it now stays open until the request settles.
- Task dialog: "New task" / "Edit task", no staggered field animations, priority as a one-tap segmented
  control (arrow keys work), due date and repeat side by side, sentence-case labels.
- Due date picker: field-styled trigger, quick picks (Today, Tomorrow, Next week), native time field, Done
  button; overdue / due-soon in the destructive / warning tones (was `orange-500`).
- Tag input: input-styled field, neutral chips with the tag colour as a dot, 24 px remove buttons with a
  larger hit area, comma adds a tag, inline hint for duplicates and invalid names. Tag palette aligned with
  Kairos's palette in `prompts.py` (was neon cyan / pink / green).
- Empty states: "Nothing in orbit yet" (small drawn orbit, add button) and a separate "No tasks match" with
  "Clear search and filters". Loading error card on `.surface` with retry spinner. Dashboard loading skeleton
  mirrors the real layout. Toolbar: search clear button, 36-44 px controls, short trigger labels so priority
  and sort fit side by side at 320 px. Task card: completion glow and `rgba` shadows removed.
- Confetti colours follow the theme.

## 2026-10-28 · feat(frontend): every UI primitive on the night-observatory tokens

- New tokens: `--custom-success`, `--custom-warning` (Tailwind `success`, `warning`), `--shadow-pop`,
  `--scrim`, `--switch-thumb`; utilities `.surface-pop` (solid floating layer) and `.scrim` (D-009).
  Removed the legacy `.glow-*`, `.text-glow`, `.border-priority-*`, `.transition-smooth` helpers and the
  spinner's drop-shadow glow. The iOS 16 px input rule now applies on phones only, so desktop fields keep 14 px.
- Dialog / alert dialog: glass panel, 3xl radius, display-font titles, 40 px close button, themed scrim
  (was `bg-black/50`); alert dialog gets an icon slot and a `variant` on its action (the red neon glow is gone).
- Dropdown menu, select, popover: solid `.surface-pop`, 40 px rows, gold check marks, select opens under its
  trigger (popper) and its chevron turns when open; `SelectItem` takes a `description` shown only in the list.
- Button (`text-white` removed, `aria-busy`), input/textarea (hover border), checkbox (20 px box, 40 px hit
  area), switch (26 × 44 px, theme-aware thumb), badge (soft `muted/accent/info/success/warning/danger`),
  card (`.surface`), tabs (segmented pill like the dashboard filter), skeleton, form messages, calendar
  (40 px days, gold today ring, no glow, no fixed height), new `Callout` for inline status messages.
- Toasts: dropped sonner's `richColors` (stock green/red fills); toasts use the solid surface with the status
  in the icon colour. The toast `--normal-bg` vars pointed at undefined `--popover`; now `--color-popover`.
  Kairos action toasts (`lib/utils/toast.tsx`) used a separate neon-bordered component; they now use the same
  toaster.

## 2026-10-28 · feat: Kairos assistant, new brand assets; fix: chat broken on current openai

- **Chat was broken on a fresh install**: openai 2.45+ made `InputTokensDetails.cache_write_tokens`
  required, so openai-agents 0.8 failed every chat run while building `Usage()`. Pinned `openai<2.45`
  (D-005); regression test `test_agents_sdk_usage_accepts_installed_openai`.
- **Dates for the agent**: the chat route sent only the UTC date and effectively no time zone, so early-morning
  users east of UTC got the wrong "today", and due times without an offset were stored as UTC. Now
  `build_time_context()` gives local date, time and offset from `users.timezone`, and
  `localize_due_date()` reads offset-less times in the user's zone (`tests/test_prompts.py`).
- **Kairos** (D-008): the assistant's name. Prompts moved to `app/ai/agents/prompts.py` and rewritten: one
  persona across main, planning and search modes (no "transfer" announcements), date/time rules, confirm before
  deletes and bulk actions, never invent or show IDs, task text treated as data (prompt-injection guard),
  short reply formats with examples, Roman Urdu support, new tag palette.
- **Chat window**: Kairos avatar and live status, themed auto-hiding scrollbar with fade edges, stick-to-bottom
  scrolling with "Jump to latest", Stop button (keeps the partial reply), character counter, Enter/Shift+Enter
  hint, Esc to close, Ctrl/Cmd+K to toggle, focus on open, dialog/log semantics, copy button on replies,
  suggestion chips that send on click, errors shown inline instead of a fading toast.
- **Brand assets**: the old neon clock favicon replaced by the orrery mark (`app/icon.svg`, `app/favicon.ico`,
  `app/apple-icon.png`, `public/icon-192/512.png`, monochrome `badge-96.png`, generated by
  `frontend/scripts/make-icons.py`); share card `app/opengraph-image.tsx` (the old `/og-image.png` never
  existed); `app/manifest.ts`; theme colours; per-page titles; metadata no longer points at a stale Vercel URL.
  `/opengraph-image` is public in the middleware so link previews work signed out.

## 2026-10-27 · fix: review findings

- Theme toggle was unreachable below 640 px (both headers hid it); phones now get the compact toggle.
- Landing nav overflowed its pill at 375 px; "Sign in" is hidden there (it is in the hero).
- Dashboard date heading: server and browser format the date with different locales/time zones; the text
  now opts out of the hydration check.
- Three Tailwind arbitrary values broken by the colour migration (spaces inside `shadow-[...]`) fixed.
- `canRunWebGL()` probed a new WebGL context on every mount; it now runs once and releases the context.
- `User.created_at` default back to naive UTC to match the column on the pinned sqlmodel.

## 2026-10-27 · fix(frontend): reduced-motion users saw no orbit legend

- The "Three orbits, one glance" legend was revealed only by scroll-linked opacity, which stayed at 0 with
  reduced motion. With reduced motion the hero is now one screen and the legend a normal section; the
  preference is read after mount so server and client HTML match.

## 2026-10-27 · feat(frontend): "night observatory" redesign with a 3D orrery

- New design tokens (OKLCH ink/starlight palette, sun-gold accent, Funnel Display + Hanken Grotesk, motion,
  radius) and Liquid Glass limited to the floating layer (D-007, `docs/design/README.md`).
- `components/three/`: WebGL orrery (React Three Fiber + three) with a CSS poster, lazy loading, off-screen
  pause, reduced-motion still frame and low-power fallback.
- Landing rebuilt: pinned orrery hero that flattens into a dial on scroll, product bento with a labelled
  example conversation, closing call to action, footer. Auth pages split with a calm orrery. Dashboard:
  "Your orbits" panel (`lib/orbits.ts`, unit-tested), date-led heading, solid wrapping toolbar, compact task
  cards with friendly dates. Chat panel moved onto theme tokens (light mode works) with a labelled button.
- Removed gradient text and all hard-coded neon cyan/purple; larger touch targets on Button/Input; labels on
  icon-only buttons (account menu, task actions, add task).

## 2026-10-27 · fix(backend): signup failed on current sqlmodel

- Sign-up raised "Datetime values must have timezone information": sqlmodel 0.0.45+ makes datetime columns
  timezone-aware and rejects naive values, and `routes/auth.py` writes `created_at=datetime.utcnow()`. Fixed by
  pinning `sqlmodel<0.0.45` (~40 `utcnow()` call sites write naive datetimes). Regression test
  `tests/test_auth_routes.py` (signup, signin, /me) fails on sqlmodel 0.0.48 and passes on the pin.
  (Corrected after review: an earlier note credited a `User.created_at` default change, which was reverted;
  signup never used that default.)

## 2026-10-27 · fix(backend): MCP tool calls and local Postgres

- `app/ai/mcp/server.py`: `_execute_tool_call` passed a removed `autocommit=` argument to `TaskTools`
  (every MCP `call_tool` raised TypeError), used `get_session()` (a FastAPI generator dependency) as a context
  manager, and referenced `ToolResponse` without importing it. Fixed; the caller now commits.
- `app/db.py:ssl_mode`: `sslmode=disable` in `DATABASE_URL` turns SSL off (SSL stays required by default).
- Tests: test engine uses `NullPool` (pooled asyncpg connections broke across per-test event loops); ownership
  tests assert the structured `error` field instead of message wording. 43/43 pass on Postgres 16.

## 2026-10-27 · shipshape adoption

- Project memory and workflow set up with shipshape (D-001): docs/, AGENTS.md, .shipshape/, .githooks/, CI
  (`.github/workflows/ci.yml` runs frontend and backend checks plus the docs gate), PR template.

## 2026-10-27 · 405e3a1 fix(backend)

- Dependencies install again: removed the `contextvars` backport (its `immutables` dep fails to build),
  added `sqlalchemy[asyncio]` (greenlet), pinned `mcp<2` / `openai<3` / `openai-agents<0.9` (mcp 2.x removed
  `Server.list_tools()` and crashed app import). Synced `pyproject.toml` + `uv.lock` (D-005).
- `postgres://` URLs became the nonexistent `postgres+asyncpg` dialect; fixed in `app/db.py:to_async_url`.
- Test harness repaired (`Base` import, removed `event_loop` fixture, one-time DB probe); new `tests/test_core.py`.

## 2026-10-27 · 92d242c refactor(backend)

- `app/models.py` → `app/models/core.py`; removed the importlib shadowing hack (D-006).

## 2026-10-27 · 7a8a974 fix(frontend)

- Route protection: `"/"` matched every path via `startsWith`, so app routes were public. Fixed in
  `lib/routes.ts` with regression tests.
- Build: removed the unused Better Auth stack that threw without `DATABASE_URL` during `next build` (D-003).
- Live notifications: SSE hit the Next origin without a token and was gated on localStorage; now streams from
  the backend with fetch + Bearer. Email preferences' `/api/auth/me` call fixed the same way.
- Lint errors fixed, ESLint ignores `.next/`, `test`/`typecheck` scripts, single npm lockfile (D-004).

## Earlier history

- Phases I-V delivered Jan-Feb 2026 (console app → full-stack → AI chatbot → K8s/Helm → Oracle OKE); see
  `git log` and `history/prompts/` for the spec-driven record.
