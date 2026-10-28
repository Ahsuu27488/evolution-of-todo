# Chronos design: "night observatory"

**Direction.** Chronos is a to-do list you can talk to, named after the Greek god of time. The interface is a
night observatory: ink-blue surfaces, starlight text and one warm accent, sun gold, for the "now" core and
primary actions. A cool orbit blue supports it.

**Signature idea: the orrery.** A live 3D model (`frontend/components/three/`) puts a glowing "now" core at
the centre, with tasks as moons on three orbits: today, this week, later.
- Landing: the hero. Scrolling through the pinned first screen swings the tilted orbits into a flat dial and
  reveals what each orbit means (native sticky scroll, no scroll-jacking).
- Login / signup: a calm version beside the form (wide screens only).
- Dashboard: "Your orbits", a small orrery whose moons are your real open tasks (`frontend/lib/orbits.ts`).

## Tokens (`frontend/app/globals.css`)

| Token | Dark | Light ("day sky") |
|---|---|---|
| background | `oklch(0.18 0.035 265)` ink | `oklch(0.975 0.008 255)` |
| card / popover | `0.215` / `0.245` lightness steps | white |
| foreground | `oklch(0.94 0.012 265)` starlight | `oklch(0.22 0.04 265)` ink |
| primary | `oklch(0.82 0.14 78)` sun gold | `oklch(0.64 0.145 66)` deeper gold |
| secondary | `oklch(0.76 0.09 245)` orbit blue | `oklch(0.5 0.11 250)` |

Type: Funnel Display (headlines, `--font-display`), Hanken Grotesk (UI, `--font-sans`), Noto Nastaliq Urdu (Urdu).
Fluid sizes `--step-display`, `--step-h1`, `--step-h2`. Motion: `--ease-out`, `--dur-fast/ui/enter`.
Status: `--custom-success` (done), `--custom-warning` (due soon), `--custom-destructive` (overdue, delete),
orbit blue (info); Tailwind `success`, `warning`, `destructive`, `secondary`.
Radius: one system from `--radius` (0.875rem): fields and menu rows `radius-md`, cards `radius-2xl`, dialogs
`radius-3xl`, pills and icon buttons full.

## Surfaces (D-009)

| Layer | Utility | Used by |
|---|---|---|
| Page content | `.surface` (solid card, hairline highlight) | task cards, orbit panel, settings sections, empty / error states, profile |
| Floating over glass or content | `.surface-pop` (solid popover colour, `--shadow-pop`) | dropdown menus, select lists, popovers (date picker), notification menu, toasts |
| Floating, modal | `.glass-modal` + `.scrim` | dialogs, alert dialogs, push prompt; the chat panel |
| Floating chrome | `.glass` | nav pill, unsaved-changes bar |

Never glass on glass: anything that opens from a glass element is `.surface-pop`. Reduced transparency,
more contrast or no `backdrop-filter` all fall back to opaque surfaces.

## Component rules

- Sentence case everywhere ("New task", "Notification settings"); buttons are verbs; no arrow on buttons.
- Targets: 40-44 px (icon buttons `size-10`, fields `h-11` on phones and `h-10` from `md`); checkbox and
  switch reach 40 px through an `::after` hit area.
- Every control has hover, `focus-visible` ring (`ring-[3px] ring-ring/50`), active (scale 0.97), disabled,
  loading (`aria-busy`, spinner, present-tense label such as "Saving"), and its screen has empty and error states.
- Status is a soft tint (`Badge` `success/warning/danger/info/accent/muted`, `Callout` tones), never a
  full-colour card or a glow. Priority is a coloured dot (high: destructive, medium: gold, low: muted).
- Inline status messages use `Callout`; transient results use toasts (`components/ui/sonner.tsx`).
- Emails (`backend/app/services/email_service.py`): hex equivalents of the tokens (clients ignore CSS
  variables), table layout, light by default with a dark-mode block, one gold button.

## 3D rules

- HTML first: every headline and action is real DOM; the canvas is decoration (`aria-hidden`).
- `<Orrery>` shows a CSS poster of the same composition at the same size, then lazy-loads the scene in the
  browser only when on screen, and pauses rendering off-screen.
- Reduced motion: a still frame. No WebGL, or 2 or fewer cores / 2 GB or less memory: the poster only.
- DPR capped at 1.75 (1.5 for the mini). Lazy 3D chunk: about 188 kB gzipped (three + R3F), off the
  initial load (`/` first-load JS 207 kB).

## Before / after

Earlier pass (landing, auth, dashboard, chat):

| Surface | Before | After |
|---|---|---|
| Landing | `before/landing-1440.jpg`, `before/landing-1440-scrolled.jpg` | `after/landing-1440.jpg`, `after/landing-dial-1440.jpg`, `after/landing-signed-in-1440.jpg` |
| Login | `before/login-1440.jpg` | `after/login-1440.jpg` |
| Dashboard | (not captured: it needed a running backend) | `after/dashboard-1440.jpg` |
| Chat | (not captured) | `after/chat-1440.jpg` |
| Mobile | (not captured) | `after/landing-orrery-375.png`, `after/bento-375.jpg` |

Component pass (2026-10-28). Files are `<surface>-<width>-<theme>.jpg` at 1440 and 375 px, dark and light,
in `before/components/` and `after/components/`. 768 and 320 px were checked as well but are not committed
(regenerate them with the script below).

| Surface | Before | After |
|---|---|---|
| Dashboard | `dashboard` | `dashboard`, `dashboard-loading`, `dashboard-error`, `empty-filtered` |
| Task dialog | `task-dialog`, `priority-select`, `due-date-popover` | `task-dialog`, `form-select` (repeat), `due-date-popover` |
| Task menu, delete | `task-menu`, `delete-dialog` | `task-menu`, `delete-dialog` |
| Toolbar sort | `sort-select` | `sort-select` |
| Account menu | `account-menu` | `account-menu` |
| Notification menu | `notifications` | `notifications` |
| Settings | `settings-push`, `settings-email`, `settings-in-app` | the same, plus `settings-email-unsaved` and `toast` |
| Profile | `profile` | `profile` |
| Push prompt, error page | (not reachable in a capture) | `push-modal`, `error-page` (from a temporary local gallery page, not committed) |
| Emails | `before/emails/<name>-<640 or 375>-<theme>.jpg` | `after/emails/`: task-due, task-overdue, task-assigned, daily-digest, weekly-summary, welcome (plus `.html`) |

Regenerate: `python frontend/scripts/capture-ui.py <out_dir> [--quick] [--widths=320,768] [--only=dashboard]`
(dev server on :3100, backend on :8100, test account in `frontend/.env.local`) and
`backend/scripts/render_emails.py` (see its docstring).
