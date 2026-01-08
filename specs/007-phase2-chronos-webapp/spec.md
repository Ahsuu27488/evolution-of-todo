# Feature Specification: Phase II - "Chronos" Professional Web App (AI-Architecture Ready)

**Feature Branch**: `007-phase2-chronos-webapp`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Feature: Phase II - 'Chronos' Professional Web App (AI-Architecture Ready). Create a majestic, industry-grade Task Management UI that supports standard interactions (clicks/forms) BUT is architecturally ready for Voice/AI integration."

## Executive Summary

Transform the Phase I in-memory console Todo application into a production-ready, visually stunning full-stack web application named "Chronos AI." This phase establishes the "body" for a future "Jarvis" AI brain - delivering an extraordinary task management experience with glassmorphism aesthetics, advanced task features from Phase I, and architectural readiness for Phase III voice/AI integration.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover and Sign Up (Priority: P1)

A new visitor lands on the "Evolution of Todo" landing page and is captivated by the futuristic deep space glassmorphism design. They see a compelling call-to-action and learn about upcoming voice features. They decide to create an account, sign up with email/password, and are automatically logged in to their new task dashboard.

**Why this priority**: User acquisition is the funnel entry. The landing page must convert visitors to sign-ups, and registration must be frictionless.

**Independent Test**: Can be fully tested by visiting the landing page, clicking "Start Your Journey," completing signup, and verifying redirect to dashboard.

**Acceptance Scenarios**:

1. **Given** a visitor on the landing page, **When** they click "Start Your Journey" and enter valid email/password, **Then** an account is created and they are redirected to their dashboard with welcome message
2. **Given** a visitor on the landing page, **When** they scroll to "Coming Soon" section, **Then** they see teaser content about future Voice Command features
3. **Given** a visitor attempting signup, **When** they enter an email already in use, **Then** they see clear error "Email already registered. Try logging in?"
4. **Given** a visitor on signup form, **When** they enter password under 8 characters, **Then** they see real-time validation feedback "Password must be at least 8 characters"

---

### User Story 2 - Authenticate and Access Dashboard (Priority: P1)

A returning user visits the app, logs in with their credentials, and lands on their personalized task dashboard. The Command Center bar at the bottom immediately catches their eye - ready for future voice commands but currently accepting text input.

**Why this priority**: Authentication gates all functionality. Users must be able to securely access their data. The Command Center establishes the AI-readiness narrative.

**Independent Test**: Can be fully tested by logging in with valid credentials and verifying dashboard access with Command Center visible.

**Acceptance Scenarios**:

1. **Given** a registered user on the login page, **When** they enter correct credentials, **Then** they are authenticated and redirected to their task dashboard
2. **Given** a logged-in user viewing the dashboard, **When** they look at the bottom of the screen, **Then** they see the Command Center bar with "Ask Chronos anything..." placeholder and microphone icon
3. **Given** a user entering incorrect credentials, **When** they submit the login form, **Then** they see "Invalid email or password" without revealing which field is wrong
4. **Given** an unauthenticated user, **When** they try to access `/dashboard`, **Then** they are redirected to the login page

---

### User Story 3 - Create Task with Glass Modal (Priority: P1)

An authenticated user wants to add a new task. They click the floating action button or use the Command Center, and a stunning glassmorphism modal slides in from the bottom. They enter a title, optional description, select priority, add tags with animated color picker, and set a due date. The task is created with a satisfying animation.

**Why this priority**: Task creation is the core value proposition. The modal's visual quality establishes the "extraordinary" experience.

**Independent Test**: Can be fully tested by clicking "Add Task," filling in various fields, and verifying the task appears in the list with glassmorphism animation.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the dashboard, **When** they click the "+" floating action button, **Then** a glassmorphism modal slides in from bottom with backdrop blur effect
2. **Given** a user creating a task, **When** they enter title and select priority from dropdown, **Then** the task is saved with priority indicator and appears in their list with slide-in animation
3. **Given** a user creating a task, **When** they add multiple tags with different colors, **Then** tags are stored and displayed with their assigned colors
4. **Given** a user setting a due date, **When** they select date from picker, **Then** the date is saved and displayed in human-readable format (e.g., "Today," "Tomorrow," "Jan 15")
5. **Given** a user enabling recurring task, **When** they select "Weekly" from recurrence dropdown, **Then** the task is marked for weekly recurrence

---

### User Story 4 - View and Organize Tasks (Priority: P1)

An authenticated user wants to see all their tasks with rich context. The dashboard displays tasks as beautiful glass cards with priority indicators, tag colors, due dates, and completion status. Users can filter by status/priority/tags and sort by various criteria.

**Why this priority**: Task viewing is the most frequent action. The visual quality establishes user satisfaction and engagement.

**Independent Test**: Can be fully tested by creating multiple tasks with different properties and applying filters/sorts to verify correct organization.

**Acceptance Scenarios**:

1. **Given** an authenticated user with tasks, **When** they visit the dashboard, **Then** they see their tasks as glass cards with priority colored borders, tag badges, due date indicators, and completion status
2. **Given** a user viewing tasks, **When** they click "Filter by: High Priority," **Then** only high-priority tasks are displayed with filter chip active
3. **Given** a user with many tasks, **When** they search for "meeting" in the search bar, **Then** only tasks with "meeting" in title/description/tags are displayed
4. **Given** a user sorting tasks, **When** they select "Sort by: Due Date," **Then** tasks reorder with nearest deadlines at top
5. **Given** a new user with no tasks, **When** they visit the dashboard, **Then** they see an illustrated empty state with "lonely astronaut" imagery and call-to-action

---

### User Story 5 - Mark Task Complete with Celebration (Priority: P1)

A user completes a task and clicks the completion checkbox. The task card glows, confetti particles explode, and a subtle achievement sound plays (muted by default). If the task was recurring, the next occurrence is automatically scheduled.

**Why this priority**: Completion tracking is fundamental. The celebration creates positive reinforcement and engagement.

**Independent Test**: Can be fully tested by clicking a task's completion toggle and verifying visual feedback, confetti effect, and recurring task behavior.

**Acceptance Scenarios**:

1. **Given** a user with an incomplete task, **When** they click the completion checkbox, **Then** the task glows cyan, strikes through with animation, and confetti particles burst from the card
2. **Given** a user with a completed task, **When** they click the completion checkbox again, **Then** the task reverts to incomplete status with reverse animation
3. **Given** a user marking a recurring "Weekly" task complete, **When** the action completes, **Then** a new task is auto-created with due date 7 days later and same properties
4. **Given** a user with sound enabled, **When** they mark a task complete, **Then** a pleasant achievement sound plays
5. **Given** a user toggling completion, **When** the action completes, **Then** the change persists after page refresh

---

### User Story 6 - Edit and Delete Tasks (Priority: P2)

A user needs to modify a task's details or remove it entirely. They can click edit on a task card to open the glass modal with pre-filled data, or click delete to confirm removal. Task history is logged for audit.

**Why this priority**: Tasks evolve and need cleanup. The audit log provides accountability and history tracking.

**Independent Test**: Can be fully tested by editing various fields on existing tasks and deleting tasks with confirmation.

**Acceptance Scenarios**:

1. **Given** a user viewing a task, **When** they click the edit icon, **Then** the glassmorphism modal appears with all current task data pre-filled
2. **Given** a user editing a task, **When** they modify the title and click "Save," **Then** changes are persisted with animation and visible immediately
3. **Given** a user clicking delete on a task, **When** they confirm in the dialog, **Then** the task card disintegrates with glow trail effect and is permanently removed
4. **Given** a task that has been modified multiple times, **When** user views task history, **Then** they see a chronological list of all changes with timestamps

---

### User Story 7 - Command Center Text Input (Priority: P2)

While voice integration is Phase III, users can currently type commands into the Command Center bar. Basic natural language parsing allows creating tasks via text (e.g., "Add meeting with John tomorrow at 2pm high priority").

**Why this priority**: This establishes the command pattern for future voice integration and provides immediate value.

**Independent Test**: Can be fully tested by typing various command formats into the Command Center and verifying task creation.

**Acceptance Scenarios**:

1. **Given** a user on the dashboard, **When** they click the Command Center input and type "Add call mom tomorrow," **Then** a task titled "Call mom" is created with due date set to tomorrow
2. **Given** a user typing a command, **When** they press Enter or click send, **Then** the command executes and input clears
3. **Given** a user typing an unrecognized command, **When** they submit, **Then** they see a helpful suggestion "Try: 'Add [task] [optional: due date]'"
4. **Given** a user focusing the Command Center, **When** they press Cmd/Ctrl+K, **Then** the input receives focus and expands to 90% width

---

### User Story 8 - Mobile Responsive Experience (Priority: P2)

A user opens the app on their phone. The entire interface adapts beautifully - the Command Center becomes thumb-friendly, task cards stack vertically, and the glassmorphism effects remain performant.

**Why this priority**: Mobile usage is essential for productivity. Users check tasks on-the-go.

**Independent Test**: Can be fully tested by accessing the app on mobile viewport (320px-768px) and verifying all features work.

**Acceptance Scenarios**:

1. **Given** a user on mobile device (375px width), **When** viewing the dashboard, **Then** task cards display in single-column layout with readable text
2. **Given** a user on mobile, **When** they view the Command Center, **Then** it remains fixed at bottom, full-width, with touch-friendly input height
3. **Given** a user on mobile, **When** they interact with buttons/checkboxes, **Then** all touch targets are at least 44x44 pixels
4. **Given** a user on mobile, **When** they open the task creation modal, **Then** it slides up as a bottom sheet covering 90% of screen

---

### User Story 9 - Data Isolation and Security (Priority: P3)

Each user's data is completely isolated. Users can only see and manage their own tasks. API requests are secured via JWT tokens. The database schema includes AI-ready fields for future use.

**Why this priority**: Security and privacy are foundational. The AI-ready fields prepare for Phase III without breaking changes.

**Independent Test**: Can be fully tested by creating tasks as User A, logging in as User B, and verifying no data leakage.

**Acceptance Scenarios**:

1. **Given** User A creates tasks, **When** User B logs in, **Then** User B cannot see or access User A's tasks by any means
2. **Given** a user making API requests, **When** their JWT token expires, **Then** subsequent requests return 401 Unauthorized and they're redirected to login
3. **Given** a user attempting to access another user's task ID directly, **When** the request hits the API, **Then** it returns 404 Not Found (not 403, to avoid ID enumeration)
4. **Given** database inspection, **When** viewing the tasks table, **Then** AI-ready fields (transcription_text, ai_summary, embedding_id) exist but are null for all tasks

---

### Edge Cases

- What happens when a user's session expires while editing a task? → Show friendly toast "Session expired. Please log in again" and redirect to login
- What happens when network connectivity is lost during task creation? → Show error toast "Connection failed. Tap to retry" with optimistic rollback
- What happens when two browser tabs are open and task is deleted in one? → Other tab shows stale data but refreshes on focus or next API call
- What happens when user enters extremely long task title (200+ characters)? → Truncate display with ellipsis, full text on hover/expand
- What happens when database connection fails entirely? → Show user-friendly error page "Service temporarily unavailable. We've been notified!"
- What happens when a recurring task is due but user deletes it before completion? → No new task is created; the recurrence chain ends
- What happens when user tries to create task with due date in the past? → Allow creation but display "Overdue" indicator in red
- What happens when Command Center receives ambiguous command "Add thing"? → Create task with minimal info and show tooltip "Add more details for better results"
- What happens when browser doesn't support backdrop-filter (glassmorphism)? → Gracefully degrade to semi-transparent backgrounds with solid colors
- What happens when user has 1000+ tasks? → Implement pagination or virtual scrolling to maintain performance

---

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Authorization
- **FR-001**: System MUST provide user registration with email (valid format) and password (minimum 8 characters)
- **FR-002**: System MUST authenticate users via email/password login
- **FR-003**: System MUST issue JWT tokens (7-day expiry) for authenticated sessions
- **FR-004**: System MUST validate JWT tokens on all protected API endpoints
- **FR-005**: System MUST provide secure logout functionality that clears client-side tokens
- **FR-006**: System MUST redirect unauthenticated users to landing/login page when accessing protected routes
- **FR-007**: System MUST hash passwords using industry-standard algorithm (bcrypt/argon2)

#### Task Management (Full Phase I Parity)
- **FR-008**: System MUST allow authenticated users to create tasks with title (required, 1-200 chars), description (optional, max 1000 chars), priority, tags, due date, and recurrence
- **FR-009**: System MUST support three priority levels: HIGH, MEDIUM (default), LOW
- **FR-010**: System MUST support tags (0-10 per task, max 30 chars each) with user-assigned colors
- **FR-011**: System MUST support due dates with date/time picker and human-readable display
- **FR-012**: System MUST support recurring tasks with patterns: DAILY, WEEKLY, MONTHLY
- **FR-013**: System MUST auto-create next occurrence when a recurring task is marked complete
- **FR-014**: System MUST allow users to view all their tasks with sorting and filtering
- **FR-015**: System MUST allow users to update any task field
- **FR-016**: System MUST allow users to delete tasks with confirmation
- **FR-017**: System MUST allow users to toggle task completion status
- **FR-018**: System MUST maintain task history/audit log for all modifications
- **FR-019**: System MUST persist all task data to Neon PostgreSQL database
- **FR-020**: System MUST associate tasks with the creating user (user_id foreign key)

#### Search, Filter, Sort
- **FR-021**: System MUST support keyword search across task titles and descriptions (case-insensitive)
- **FR-022**: System MUST support filtering by completion status (all/pending/completed)
- **FR-023**: System MUST support filtering by priority level (high/medium/low)
- **FR-024**: System MUST support filtering by due date (overdue/today/this_week/no_deadline)
- **FR-025**: System MUST support filtering by tags
- **FR-026**: System MUST support sorting by priority, due date, creation date, title, and status

#### AI-Ready Database Schema
- **FR-027**: Database tasks table MUST include `transcription_text` column (text, nullable) for future voice command logs
- **FR-028**: Database tasks table MUST include `ai_summary` column (text, nullable) for future LLM-generated context
- **FR-029**: Database tasks table MUST include `embedding_id` column (text/uuid, nullable) for future vector search
- **FR-030**: Database schema MUST include `task_logs` table for audit history (task_id, action, changed_fields, timestamp, user_id)

#### User Interface & Experience
- **FR-031**: System MUST provide responsive design for mobile (320px+), tablet (768px+), and desktop (1024px+)
- **FR-032**: System MUST display loading skeleton screens during async operations (no spinners)
- **FR-033**: System MUST show success/error feedback via toast notifications
- **FR-034**: System MUST provide visual distinction between completed and incomplete tasks
- **FR-035**: System MUST show illustrated empty state when user has no tasks
- **FR-036**: System MUST provide confirmation dialog before destructive actions (delete)
- **FR-037**: System MUST implement glassmorphism visual design with backdrop-blur effects
- **FR-038**: System MUST use "Deep Space" color scheme with cyan/purple neon accents
- **FR-039**: System MUST provide micro-animations for state transitions (slide-in, glow, fade)
- **FR-040**: System MUST trigger confetti particle effect on task completion
- **FR-041**: System MUST include permanent Command Center bar at bottom of dashboard
- **FR-042**: Command Center MUST include text input, microphone icon (Phase III placeholder), and send button
- **FR-043**: Command Center MUST accept text commands for basic task creation in Phase II
- **FR-044**: System MUST support keyboard shortcut (Cmd/Ctrl+K) to focus Command Center

#### Landing Page
- **FR-045**: System MUST provide public landing page titled "The Evolution of Todo"
- **FR-046**: Landing page MUST include Hero section with value proposition
- **FR-047**: Landing page MUST include "Coming Soon" section teasing Voice Command features
- **FR-048**: Landing page MUST include call-to-action to "Start Your Journey" (signup)

#### API Design
- **FR-049**: Backend MUST expose RESTful API endpoints under `/api/` prefix
- **FR-050**: API MUST return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- **FR-051**: API MUST return JSON responses with consistent structure
- **FR-052**: API MUST validate request payloads and return clear error messages
- **FR-053**: API MUST include CORS headers for frontend-backend communication

#### Data Security
- **FR-054**: System MUST enforce data isolation - users can only access their own tasks
- **FR-055**: System MUST validate user ownership on all task operations (read/update/delete)
- **FR-056**: System MUST use HTTPS for all communications in production
- **FR-057**: System MUST never expose internal error details to client responses

### Key Entities

- **User**: Represents a registered user with authentication credentials (id, email, name, created_at) - managed by Better Auth
- **Task**: Represents a todo item with full feature set
  - id (unique identifier)
  - user_id (foreign key to user, owner)
  - title (required, 1-200 characters)
  - description (optional, max 1000 characters)
  - priority (enum: HIGH/MEDIUM/LOW)
  - completed (boolean)
  - tags (array of {name, color} objects, 0-10 items)
  - due_date (datetime, nullable)
  - recurrence_pattern (enum: null/DAILY/WEEKLY/MONTHLY)
  - transcription_text (text, nullable, AI-ready)
  - ai_summary (text, nullable, AI-ready)
  - embedding_id (text, nullable, AI-ready)
  - created_at (timestamp)
  - updated_at (timestamp)
- **TaskLog**: Represents audit trail for task modifications
  - id (unique identifier)
  - task_id (foreign key to task)
  - user_id (foreign key to user, who made change)
  - action (enum: created/updated/deleted/completed/uncompleted/recurred)
  - changed_fields (JSON, before/after values)
  - timestamp (when action occurred)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**User Experience:**
- **SC-001**: Users can complete the full landing-page-to-first-task flow in under 90 seconds
- **SC-002**: Task creation (including all optional fields) completes within 2 seconds from form submit to UI update
- **SC-003**: Task list renders within 1.5 seconds for users with up to 100 tasks
- **SC-004**: Confetti animation completes within 2 seconds without blocking user interaction
- **SC-005**: Command Center text input responds to keystrokes with under 50ms latency

**Visual Design:**
- **SC-006**: Glassmorphism effects maintain 60fps animations on target devices (desktop/mobile)
- **SC-007**: Color contrast ratios meet WCAG AA standards (4.5:1 for normal text)
- **SC-008**: All interactive elements have visible hover/focus states

**Functionality:**
- **SC-009**: All Phase I features (Basic + Intermediate + Advanced) are fully functional in web UI
- **SC-010**: 100% of CRUD operations persist correctly across page refreshes and re-login
- **SC-011**: Zero data leakage between users (verified through security testing)
- **SC-012**: Recurring tasks auto-create next occurrence within 500ms of completion

**Performance:**
- **SC-013**: First Contentful Paint occurs in under 1.5 seconds on standard broadband
- **SC-014**: Time to Interactive occurs in under 3 seconds on standard broadband
- **SC-015**: Application achieves Lighthouse Performance score of 90+
- **SC-016**: Application achieves Lighthouse Accessibility score of 90+

**Architecture:**
- **SC-017**: Database schema includes all AI-ready fields (transcription_text, ai_summary, embedding_id)
- **SC-018**: Command Center UI component is present and functional on all pages
- **SC-019**: Frontend code structure allows swapping Command Center input for voice recorder without layout changes

---

## Assumptions

1. Users have modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions) supporting CSS backdrop-filter
2. Users have reliable internet connectivity for cloud database operations
3. Neon DB free tier is sufficient for hackathon usage levels
4. Better Auth JWT plugin provides necessary token functionality for FastAPI integration
5. Single timezone handling (UTC) is acceptable for task timestamps in Phase II
6. Email verification is not required for initial registration (can be added as enhancement)
7. Password reset functionality is out of scope for Phase II (can be added later)
8. Command Center natural language parsing will be basic regex/pattern matching in Phase II; sophisticated NLP deferred to Phase III
9. Confetti and achievement sound libraries are available and don't require licensing
10. Glassmorphism effects will gracefully degrade on older browsers without backdrop-filter support
11. Microphone icon in Command Center is visual only; non-functional in Phase II

---

## Out of Scope (Phase II Boundaries)

The following are explicitly NOT included in Phase II:
- **Voice input/recording** - defer to Phase III
- **OpenAI Agents SDK integration** - defer to Phase III
- **MCP server implementation** - defer to Phase III
- **AI chatbot conversation interface** - defer to Phase III
- **Social login providers** (Google, GitHub) - defer to later phase
- **Real-time collaboration/sync between devices** - defer to Phase V
- **WebSocket connections** - defer to Phase III
- **Team/shared task lists** - defer to later phase
- **Email notifications** - defer to later phase
- **Offline support/PWA features** - defer to later phase
- **Advanced natural language processing** in Command Center - defer to Phase III
- **Vector search implementation** (embedding_id field reserved only)
- **AI-generated task summaries** (ai_summary field reserved only)

---

## Dependencies

### External Services
- Neon DB account (free tier PostgreSQL)
- Vercel account for frontend deployment (free tier)
- Railway/Render account or similar for backend deployment (free tier options available)

### Environment Variables Required

| Variable | Frontend | Backend | Purpose |
|----------|----------|---------|---------|
| `DATABASE_URL` | ✅ | ✅ | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | ✅ | ✅ | Shared secret for JWT signing/verification |
| `NEXT_PUBLIC_API_URL` | ✅ | - | Backend API base URL |
| `CORS_ORIGINS` | - | ✅ | Allowed frontend origins for CORS |

---

## Branding Guidelines

### Visual Identity

**App Name:** Chronos AI

**Tagline:** "The Evolution of Todo"

**Aesthetic:** "Deep Space Glassmorphism"

**Color Palette:**
- Primary Background: Deep space black (#0a0a0f)
- Secondary Background: Semi-transparent glass (rgba(20, 20, 30, 0.7))
- Accent Cyan: Neon cyan (#00f5ff) for primary actions, high priority
- Accent Purple: Neon purple (#a855f7) for secondary actions, medium priority
- Accent Green: Success states (#22c55e)
- Accent Red: High priority, errors, overdue (#ef4444)
- Text Primary: White with slight transparency (#f0f0f0)
- Text Secondary: Gray (#a0a0b0)

**Typography:**
- Headings: Inter or system-ui, sans-serif, 600-700 weight
- Body: Inter or system-ui, sans-serif, 400 weight
- Monospace: JetBrains Mono for code/technical labels

**Effects:**
- Glassmorphism: `backdrop-filter: blur(12px)` + semi-transparent backgrounds
- Glow effects: `box-shadow: 0 0 20px` with accent colors
- Borders: 1px solid with low opacity white (rgba(255, 255, 255, 0.1))

### Illustration Prompts (for AI image generation)

**Hero Section:**
"A futuristic 3D glass interface floating in a deep space void. Neon cyan and purple data streams connecting to a central glowing orb. Minimalist, 8k resolution, unreal engine 5 render style, cinematic lighting."

**Empty Task State:**
"A lonely astronaut floating peacefully in deep space, looking at a blank holographic tablet. Relaxing atmosphere, stars in background, lo-fi aesthetic, digital art."

---

## Risk Considerations

1. **Glassmorphism Performance**: Heavy use of backdrop-filter may impact performance on low-end devices - implement fallback for older browsers
2. **JWT Token Security**: Ensure tokens are stored securely (httpOnly cookies preferred over localStorage)
3. **CORS Configuration**: Must be properly configured for frontend-backend communication across domains
4. **Database Connection Pooling**: Neon serverless may have cold start latency - implement connection pooling
5. **Recurring Task Edge Cases**: Complex scenarios (timezones, DST, deleted tasks) need careful handling
6. **Command Center Parsing**: Basic NLP in Phase II may frustrate users if expectations are set too high - set clear expectations in UI
7. **Animation Performance**: Confetti and complex animations must not block main thread - use Web Workers if needed
8. **AI-Ready Fields**: Unused database fields may confuse developers - document clearly that these are for Phase III
