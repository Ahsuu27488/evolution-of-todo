# Project Status

> Current truth only: what works now, what doesn't, what's next. History goes in CHANGELOG.md, reasons in
> DECISIONS.md. Updated in the same commit as every code change (the commit-msg hook checks). Keep it short:
> it is loaded into every agent session.

**Last updated:** 2026-10-28 · **Code at:** branch `chore/repair-shipshape-3d-redesign`
**In one line:** Chronos (Next.js 15 + FastAPI + Neon + OpenAI Agents) builds, installs and passes its checks
again after a repair pass, and every screen, dialog, menu, email and notification now follows the "night
observatory" design with a 3D orrery (D-007, D-009).

## What works (verified)

- Frontend type check, lint, unit tests and production build: `npm run typecheck`, `npm run lint`, `npm test`
  (5 tests), `npm run build` all pass (2026-10-28).
- Redesign checked in the browser against the local backend (2026-10-27): landing (orrery hero, scroll-to-dial,
  bento), login/signup, dashboard (orbit panel updates live when a task is completed), chat panel, light mode,
  320 and 375 px with no horizontal scroll (theme toggle reachable on phones). Before/after screenshots in
  `docs/design/`.
- Component pass checked in the browser (2026-10-28) at 1440, 768, 375 and 320 px, dark and light, against
  the local backend: dashboard (loading, error, filtered-empty), task dialog with its selects and date
  popover, task menu, delete confirmation, sort select, account menu, notification menu, settings (push,
  email with unsaved-changes bar, in-app), toasts, profile, push prompt, error page, chat task cards and
  skeleton. No horizontal scroll at 320 px. Screenshots: `docs/design/` (README table).
- Emails rendered and checked in Chromium, light and dark, 640 and 375 px (`backend/scripts/render_emails.py`).
- Fresh-eyes review (shipshape-reviewer) run on the whole branch; its 5 findings are fixed (CHANGELOG).
- Kairos chat (2026-10-28): opens (button, Ctrl/Cmd+K), sends, and shows failures inline; with no
  `OPENAI_API_KEY` locally the agent stops at "Missing credentials", so real replies are NOT verified here.
- Brand assets served: favicon.ico, icon.svg, apple-icon, manifest, share card (checked in the browser).
- Backend installs from `requirements.txt` on Python 3.14 and the app imports with all 30 API paths
  (`tests/test_core.py::test_app_registers_all_routers`, 2026-10-27).
- Sign-up, sign-in and `/api/auth/me` work end to end (`tests/test_auth_routes.py`, and in the browser), thanks to
  the `sqlmodel<0.0.45` pin (the test fails on 0.0.48).
- Backend tests: 64 pass against a real Postgres 16 (`TEST_DATABASE_URL`, 2026-10-28); without one, 29 DB-free
  tests pass and the 35 DB tests skip.
- Route protection: `/dashboard`, `/profile`, `/settings/*` redirect to `/login` without the `auth_token`
  cookie (`frontend/lib/routes.test.ts`; the old middleware treated every path as public).

## In progress

- `chore/repair-shipshape-3d-redesign` - repairs, shipshape adoption and the 3D redesign, all committed.
  Not pushed or merged; lands through a pull request.

## Live state

- 2026-10-28: PR 7 merged; the HF Space did not start because of the port mismatch (fixed by `app_port: 8000`
  in `backend/README.md`). Whether the Space runs after that fix: see the next entry once checked.
- Frontend live at https://chronos.ahsandev.site (README). Host not recorded in the repo (likely Vercel).
- Backend: `.github/workflows/deploy-hf.yml` pushes `backend/` to the Hugging Face Space
  `Ahsuu27488/evolution-of-todo-api` on **every push to main that touches `backend/`**. Merging this branch
  deploys the dependency pins and the models refactor to that Space.
- Helm chart (`helm/chronos-todo`) and Phase IV/V docs exist; whether a cluster is running is not recorded.

## Known gaps

0. Local Python is 3.14 but CI and the HF Docker image use 3.13: 3.14 does not evaluate annotations at
   import, so a missing import can pass locally. Run the tests under 3.12/3.13 before merging backend changes.
1. CI runs backend tests without Postgres, so the MCP tool tests skip there (add a Postgres service to ci.yml).
2. Vercel's package manager may change: `pnpm-lock.yaml` was removed (npm + `package-lock.json` only, D-004).
3. Many specs/docs still describe Better Auth; the live auth is the backend JWT in the `auth_token` cookie (D-003).
4. ~40 `datetime.utcnow()` call sites write naive datetimes; they block upgrading past `sqlmodel<0.0.45` (D-005).
   Pydantic class-based `Config` deprecation warnings too.
5. Root `CLAUDE.md` and `backend/CLAUDE.md` contain long phase-era notes that partly predate the code.
6. Lighthouse and a real-phone test of the orrery have not been run. Emails are verified as rendered HTML
   in Chromium only (not in Gmail / Outlook / Apple Mail), and no real email or push was sent locally
   (no Resend or VAPID keys).
7. Kairos replies untested end to end (needs an OpenAI key); the share card uses the default font.
8. Clearing the due date of an existing task does not remove it: `PUT /api/tasks/{id}` ignores `null`
   (`routes/tasks.py`). The form sends nothing for a cleared date.

## Next

1. Review the branch and open the PR (human merges; merging deploys the backend, see Live state).
2. Add a Postgres service to CI so the MCP tool tests run on every PR.
3. Confirm the frontend host builds with npm after the lockfile change.
4. Then the agreed backlog in `docs/plans/backlog.md`, starting with Kairos on the free Gemini API and
   fixing Qdrant.

## How to run and check

- Frontend: `cd frontend && npm ci && npm run dev` (needs `NEXT_PUBLIC_API_URL`, see `.env.example`)
- Frontend checks: `npm run typecheck && npm run lint && npm test && npm run build`
- Backend: `cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt pytest pytest-asyncio`
  then `uvicorn app.main:app --reload` (needs `DATABASE_URL`, `BETTER_AUTH_SECRET`)
- Backend tests: `cd backend && .venv/Scripts/python -m pytest -q` (64 passing with `TEST_DATABASE_URL`, e.g.
  `postgresql+asyncpg://postgres@127.0.0.1:<port>/test_todo`; 9 passing + 35 skipped without)
- No local Postgres? `py -3.12 -m pip install pgserver` gives an embedded one; append `?sslmode=disable` to a
  local `DATABASE_URL` (Neon URLs keep SSL required).
