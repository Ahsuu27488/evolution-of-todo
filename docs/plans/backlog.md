# Backlog: agreed next work

Ideas the owner wants done after the redesign branch lands (agreed 2026-10-28). Not started. Each one gets
its own branch and plan when picked up; tick it off here and note the PR.

## Owner decisions that shape the work

- **Kairos runs on a free LLM API**, e.g. the free Gemini API tier, not paid OpenAI. Keys live only in
  `backend/.env` and the HF Space secrets.
- **Qdrant**: if the cluster is gone or broken, Claude may fix or recreate it in the owner's own Chrome
  (Claude in Chrome), then put the new endpoint and key in `.env` / Space secrets (never in git).

## 1. Kairos on Gemini (first)

- Use Gemini's OpenAI-compatible endpoint (`https://generativelanguage.googleapis.com/v1beta/openai/`)
  through the Agents SDK's `OpenAIChatCompletionsModel` with an `AsyncOpenAI(base_url=..., api_key=...)`
  client, so the agents, tools and handoffs stay as they are. Model name from env (a current Flash model on
  the free tier); turn off OpenAI tracing when no OpenAI key is set.
- Check tool calling and handoffs on Gemini end to end (the main risk), and the free-tier rate limits:
  show a friendly "Kairos is busy, try again in a minute" on 429.
- Embeddings for Qdrant: switch to a Gemini embedding model; the vector size changes, so recreate the
  collection and re-embed with `backend/scripts/resync_qdrant_embeddings.py`.
- Voice input: replace OpenAI Whisper with Gemini audio input or Groq's free Whisper.
- Record it as a decision (supersedes the OpenAI-only setup) and update `.env.example` names.

## 2. Qdrant

- Check whether the cluster still exists; if not, create a free cluster, set `QDRANT_URL` / `QDRANT_API_KEY`,
  re-index (see 1). Related Reminders item: "Demo revival" (Agency HQ).

## 3. Product ideas, roughly by value

1. Today view and a Kairos morning brief ("3 due today, 1 overdue"), one tap to plan the day.
2. Drag a moon between orbits on the dashboard orrery to reschedule (Later -> Today).
3. Natural-language quick-add bar on the dashboard ("dentist fri 11 #health !high"), parsed as you type.
4. Subtasks / checklists; Kairos can break a task into steps.
5. Weekly review on Sunday: done, slipped, a proposal for next week.
6. Google Calendar sync: push dated tasks, pull meetings so planning knows busy hours.
7. Focus mode: per-task timer, the orrery core pulses as it counts down.
8. Streaks and a quiet completion heatmap on the profile.
9. Shared lists (family groceries, small team).
10. Offline-first PWA: cache the shell and tasks, "Share to Chronos" target (save a task from WhatsApp).
11. Kairos memory of preferences ("I work 10 to 6", "Fridays are light").
12. Snooze, undo toast after delete, saved filters, a tag manager, keyboard shortcuts throughout.
13. Full Urdu UI with right-to-left layout; data export / import; email-to-task.

## 4. Engineering

- Postgres service in CI so the 35 DB tests run on every PR (they skip there today).
- Convert ~40 `datetime.utcnow()` calls to aware UTC, then lift the `sqlmodel<0.0.45` pin (D-005).
- Bold custom font in the share image (`app/opengraph-image.tsx`).
- Lighthouse mobile run and a real-phone test of the orrery; check emails in real mail apps.
