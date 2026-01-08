---
id: "0001"
title: "Phase II Chronos Web App Specification"
stage: "spec"
date: "2026-01-06"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "007-phase2-chronos-webapp"
branch: "007-phase2-chronos-webapp"
user: "ahsan"
command: "/sp.specify"
labels: ["specification", "phase2", "chronos", "fullstack", "ai-ready"]
links:
  spec: "/home/ahsan/Dev/Hackathons/Hackathon-II/evolution-of-todo/specs/007-phase2-chronos-webapp/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - /home/ahsan/Dev/Hackathons/Hackathon-II/evolution-of-todo/specs/007-phase2-chronos-webapp/spec.md
  - /home/ahsan/Dev/Hackathons/Hackathon-II/evolution-of-todo/specs/007-phase2-chronos-webapp/checklists/requirements.md
tests:
  - Validation checklist passed (all items)
---

## Prompt

Feature: Phase II - "Chronos" Professional Web App (AI-Architecture Ready)

# Context
First read the whole data base and understand what is built
We are building the Phase II Full-Stack Web App. We have scraped the old demo.
While this phase focuses on the Web UI and Database, we are designing it to be the "Body" for a future "Jarvis" AI brain.

# Goal
Create a majestic, industry-grade Task Management UI that supports standard interactions (clicks/forms) BUT is architecturally ready for Voice/AI integration.

# Branding
* **App Name:** "Chronos AI"
* **Aesthetic:** "Deep Space Glassmorphism" - Dark, neon accents (Cyan/Purple), futuristic transparency, heavy use of backdrop-blur.
* **Assets (Image Generation Prompts):**
    * **Hero Section:** "A futuristic 3D glass interface floating in a deep space void. Neon cyan and purple data streams connecting to a central glowing orb. Minimalist, 8k resolution, unreal engine 5 render style, cinematic lighting."
    * **Empty Task State:** "A lonely astronaut floating peacefully in deep space, looking at a blank holographic tablet. Relaxing atmosphere, stars in background, lo-fi aesthetic, digital art."

# Detailed Requirements

1.  **The "Extraordinary" UI (Next.js 16+ & Tailwind):**
    * **Visuals:** Use Shadcn/UI customized with a transparent, glass-like look (high opacity backgrounds with heavy blur).
    * **Animations:** Use `framer-motion` for complex interactions.
    * **The "Jarvis" Placeholder:** you MUST design the UI with a permanent "Command Center" bar at the bottom.
        * Currently, it will accept text input (Phase II).
        * Visually, it must include a "Microphone" icon (disabled or basic for now) so the layout is ready for Phase III Voice integration.

2.  **The Backend Foundation (FastAPI & SQLModel):**
    * **Standard Parity:** Implement all Phase I features (Recurring, Priority, Tags) using standard REST endpoints.
    * **AI-Ready Schema:** Design the Database Models (`models.py`) to include fields we WILL need later:
        * `user_id`: (Foreign Key) Links task to the authenticated user.
        * `transcription_text`: (Text, nullable) For storing future voice command logs.
        * `ai_summary`: (Text, nullable) For LLM-generated context of the task.
        * `embedding_id`: (Vector, nullable) Reserved for vector search later.
    * **Auth:** Secure the API using Better-Auth with JWT.

3.  **The Landing Page:**
    * A high-conversion landing page titled "The Evolution of Todo."
    * It should feature a "Coming Soon" section teasing the "Voice Command" features.

# Implementation Strategy
* **Focus:** Deliver the Visual Wow Factor and the Database solidity first.
* **Architecture:** The System Plan must show exactly where the OpenAI Agent will plug in later.

## Phase I Feature Completeness Checklist
- [ ] Recurring tasks with cron patterns (stored as string)
- [ ] Priority levels (High/Medium/Low) - Enum based
- [ ] Tags/Categories with color coding
- [ ] Search functionality (Frontend filtering for now)
- [ ] Filter by status/priority/tags
- [ ] Sort by due date/priority/creation date
- [ ] Task history/audit log (Simple table: `TaskLog`)

## Interaction Design (The "Wow" Moments)
1. **Task Creation:**
   - Modal appears with glass-morphism slide-in from bottom.
   - Real-time validation with micro-animations.
   - Tag selection with animated color picker.

2. **Task Completion:**
   - Confetti particle effect (use `canvas-confetti`).
   - Task card disintegrates with glow trail (Framer Motion `exit` prop).
   - Achievement sound (optional, muted by default).

3. **Loading States:**
   - Skeleton loaders with shimmer effect (`shadcn/skeleton`).
   - Never show spinners - always show content structure.

4. **Empty States:**
   - Use the DALL-E generated "Space Productivity" illustration defined in Branding.
   - Animated call-to-action button.

## Command Center Bar (Bottom Fixed)
- **Layout:** Glass card, 80% width, centered, 60px height. Z-Index: 50.
- **Components:**
  - Text input with placeholder: "Ask Chronos anything..."
  - Microphone icon (right side, pulsing animation when active).
  - Send button (gradient, only appears when text entered).
- **Behavior:**
  - Expands to 90% width on focus.
  - Shows recent commands as chips above input.
  - Keyboard shortcut: `Cmd/Ctrl + K` to focus.

## Landing Page Sections
1. **Hero:** "The Evolution of Todo" with 3D rotating task cards (Spline or Three.js).
2. **Feature Showcase:** Split-screen Before/After (Traditional Todo vs Chronos).
3. **AI Teaser:** "Coming Soon: Voice Commands" with video mockup.
4. **Social Proof:** "Join 10,000+ Productivity Pioneers".
5. **CTA:** "Start Your Journey" → Sign up form.

## Technical Stack Decisions
- **Frontend Framework:** Next.js 16 (App Router)
- **Styling:** Tailwind CSS + Shadcn/UI
- **Animation:** `framer-motion` (complex) + `auto-animate` (lists)
- **Data Fetching:** `TanStack Query` (React Query) - *Crucial for handling loading states/caching.*
- **Client State:** `Zustand` (for UI state like modals/sidebar).
- **Forms:** `react-hook-form` + `zod`.
- **Backend:** FastAPI + SQLModel (Async).
- **Database:** Neon (PostgreSQL).

## Performance Budget
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Lighthouse Score: 90+ (all categories)

## System Architecture (Phase II → III Readiness)

┌─────────────────────────────────────────┐
│         Frontend (Next.js)              │
│  ┌────────────────────────────────────┐ │
│  │  Command Center UI                 │ │
│  │  (Text Input → Future: Voice)      │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼──────────────────────────┘
                │
                │ REST API (Phase II)
                │ ↓
                │ WebSocket + MCP (Phase III)
                │
┌───────────────┼──────────────────────────┐
│  ┌────────────▼───────────────────────┐  │
│  │   FastAPI Backend                  │  │
│  │   (Currently: Standard Endpoints)  │  │
│  │   (Future: OpenAI Agent Router)    │  │
│  └────────────┬───────────────────────┘  │
│               │                           │
│  ┌────────────▼───────────────────────┐  │
│  │   Database (Neon PostgreSQL)       │  │
│  │   - tasks (with AI fields)         │  │
│  │   - transcriptions (future)        │  │
│  └────────────────────────────────────┘  │
└─────────────────────────────────────────┘

## Response snapshot

Created comprehensive specification for Phase II "Chronos" Professional Web App with:
- 9 prioritized user stories (P1, P2, P3) covering all major workflows
- 57 functional requirements organized by category
- 19 measurable, technology-agnostic success criteria
- AI-ready database schema with fields for Phase III continuity
- Complete branding guidelines with "Deep Space Glassmorphism" aesthetic
- 10 detailed edge cases with handling strategies
- Clear scope boundaries defining what's in/out for Phase II
- Risk considerations for implementation

Specification created at: /specs/007-phase2-chronos-webapp/spec.md
Validation checklist passed: /specs/007-phase2-chronos-webapp/checklists/requirements.md

## Outcome

- ✅ Impact: Specification complete with all Phase I features (Basic + Intermediate + Advanced) carried forward to web implementation, plus Command Center UI foundation for Phase III voice integration
- 🧪 Tests: Validation checklist passed 100% (15/15 items). No [NEEDS CLARIFICATION] markers. All user stories independently testable.
- 📁 Files: spec.md (430 lines), checklists/requirements.md created
- 🔁 Next prompts: Ready for `/sp.plan` to create architecture plan, or `/sp.clarify` if questions arise
- 🧠 Reflection: Successfully balanced "extraordinary" UI requirements (glassmorphism, animations, confetti) with solid technical foundation. AI-ready database schema fields (transcription_text, ai_summary, embedding_id) explicitly reserved for Phase III to prevent breaking changes later. Command Center bar specified as permanent UI element with text input now, voice input later - smart architectural decision for smooth phase transition.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification process completed smoothly
- Graders run and results (PASS/FAIL): PASS - Content quality, requirement completeness, feature readiness all validated
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding more specific acceptance criteria for animation performance (60fps target) if implementation challenges arise
