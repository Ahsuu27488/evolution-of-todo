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
Radius: one system from `--radius` (0.875rem). Glass (`.glass`, `.glass-modal`) only on the floating layer:
navigation pill, chat panel, dialogs, popovers. Content sits on `.surface` (solid). Reduced transparency,
more contrast or no `backdrop-filter` all fall back to opaque surfaces.

## 3D rules

- HTML first: every headline and action is real DOM; the canvas is decoration (`aria-hidden`).
- `<Orrery>` shows a CSS poster of the same composition at the same size, then lazy-loads the scene in the
  browser only when on screen, and pauses rendering off-screen.
- Reduced motion: a still frame. No WebGL, or 2 or fewer cores / 2 GB or less memory: the poster only.
- DPR capped at 1.75 (1.5 for the mini). Lazy 3D chunk: about 188 kB gzipped (three + R3F), off the
  initial load (`/` first-load JS 207 kB).

## Before / after

| Surface | Before | After |
|---|---|---|
| Landing | `before/landing-1440.jpg`, `before/landing-1440-scrolled.jpg` | `after/landing-1440.jpg`, `after/landing-dial-1440.jpg`, `after/landing-signed-in-1440.jpg` |
| Login | `before/login-1440.jpg` | `after/login-1440.jpg` |
| Dashboard | (not captured: it needed a running backend) | `after/dashboard-1440.jpg` |
| Chat | (not captured) | `after/chat-1440.jpg` |
| Mobile | (not captured) | `after/landing-orrery-375.png`, `after/bento-375.jpg` |
