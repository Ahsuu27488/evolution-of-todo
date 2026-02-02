# Feature Specification: AI-Powered Todo Chatbot

**Feature Branch**: `012-ai-chatbot-phase3`
**Created**: 2026-01-30
**Status**: Draft
**Input**: User description: "Phase 3: AI-Powered Todo Chatbot with OpenAI Agents SDK, MCP integration, semantic vector search with Qdrant, multi-language Urdu support, and voice commands"

## Clarifications

### Session 2026-01-30

- Q: Should the chat endpoint implement streaming responses (Server-Sent Events or similar) where the AI response streams token-by-token, or return complete responses after processing? → A: Streaming responses with SSE for token-by-token delivery
- Q: What level of observability should be implemented for the AI chatbot? This affects debugging, monitoring, and operational troubleshooting. → A: Structured logging with correlation IDs for full request tracing, tool calls, and agent handoffs
- Q: How should API rate limiting be implemented for the chat endpoint? This affects costs, user experience, and infrastructure requirements. → A: Per-user rate limiting at 30 requests/minute
- Q: When should conversation titles be auto-generated? This affects UX and API costs. → A: After 3 messages (enough context for meaningful title)
- Q: How should the MCP server be deployed? This affects architecture and deployment complexity. → A: In-process with FastAPI application (simpler, shared DB access, lower latency)

### Session 2026-02-02

- Q: What should happen when conversation history exceeds 50 messages? → A: Rolling window - keep last 50 messages with automatic summary of archived content for context continuity

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Management (Priority: P1)

A user wants to manage their todo list through natural conversation without learning UI commands. They type or speak commands like "Add a task to call mom tomorrow at 5pm" or "Show me my pending tasks" and the AI understands and executes the action.

**Why this priority**: This is the core value proposition of Phase 3 - transforming the todo app from a click-based interface to a conversational one. It delivers immediate value by making task management more intuitive and hands-free.

**Independent Test**: Can be fully tested by sending natural language commands to the chat endpoint and verifying the correct task operations are performed and stored in the database.

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** they send "Add a task to buy groceries", **Then** a new task is created with title "Buy groceries" and the AI confirms creation
2. **Given** a user has 5 tasks with 2 completed, **When** they ask "What's pending?", **Then** the AI returns only the 3 incomplete tasks
3. **Given** a user has task ID 3 "Call mom", **When** they say "Mark task 3 as complete", **Then** task 3's completed status is set to true and AI confirms
4. **Given** a user has task "Meeting at 3pm", **When** they say "Change task 5 to 'Meeting at 4pm'", **Then** task 5's title is updated to "Meeting at 4pm"
5. **Given** a user has 10 tasks, **When** they ask "Delete the old tasks", **Then** the AI asks for clarification on which tasks to delete (does not guess)
6. **Given** a user sends "Show me all tasks", **Then** the AI returns all tasks with their completion status, priorities, and due dates in a readable format

---

### User Story 2 - Conversational Context Memory (Priority: P2)

A user wants the chatbot to remember context across multiple messages within a conversation. They can say "Add a task for tomorrow" and when asked "What should the title be?", they reply "Call the dentist" and the AI correctly associates the title with the previously mentioned task.

**Why this priority**: Context awareness is essential for natural conversation flow. Without it, every interaction feels robotic. This builds on P1 but enables multi-turn conversations.

**Independent Test**: Can be fully tested by engaging in a multi-turn conversation and verifying the AI correctly references previous messages when resolving ambiguous requests.

**Acceptance Scenarios**:

1. **Given** a user says "I need to remember something", **When** the AI asks "What would you like to remember?" and user replies "Pay the electric bill", **Then** a task titled "Pay the electric bill" is created
2. **Given** a user asks "What do I have due today?", **When** they follow up with "And what about tomorrow?", **Then** the AI correctly shows tomorrow's tasks (not today's again)
3. **Given** a user says "Task 3 needs to be higher priority", **When** no task was discussed previously, **Then** the AI retrieves task 3 and updates its priority
4. **Given** a user's conversation includes 5 previous exchanges, **When** they send "Actually, make that urgent instead", **Then** the AI correctly identifies "that" refers to the most recently modified task
5. **Given** a user creates a conversation then reconnects after 1 hour, **When** they send "Show me what we discussed", **Then** the conversation history is preserved and displayed

---

### User Story 3 - Semantic Task Search (Priority: P3)

A user wants to find tasks by meaning rather than exact keywords. They search for "financial obligations" and the AI finds tasks containing "pay bills", "credit card payment", "rent", even though those exact words weren't in the query.

**Why this priority**: Semantic search significantly improves task discoverability. Users often don't remember exact task titles but remember the general concept. Requires Qdrant vector integration.

**Independent Test**: Can be fully tested by creating tasks with varied titles, then searching with semantically related but keyword-different queries, and verifying relevant tasks are returned.

**Acceptance Scenarios**:

1. **Given** a user has tasks "Buy vegetables", "Get groceries", "Purchase fruits", **When** they search for "food shopping", **Then** all three tasks are returned (semantic match)
2. **Given** a user has tasks "Call mom", "Email boss", "Text friend", **When** they search for "communications", **Then** all three tasks are returned
3. **Given** a user searches for "work stuff", **Then** tasks tagged with "work" and tasks with work-related keywords are ranked higher
4. **Given** a user has 100 tasks, **When** they search semantically, **Then** results are returned within 2 seconds with relevance ranking
5. **Given** a user searches for "urgent things", **Then** high priority tasks are ranked higher in results

---

### User Story 4 - Multi-Language Urdu Support (Priority: P4 - Bonus +100)

A user who speaks Urdu wants to manage their tasks in their native language. They type or speak "مجھے ایک ٹاسک شامل کرو" (Add me a task) and the AI understands, executes the command, and responds in Urdu.

**Why this priority**: Urdu support enables accessibility for millions of users. It demonstrates the AI's language versatility and qualifies for the +100 bonus points for multi-language support.

**Independent Test**: Can be fully tested by sending commands in Urdu script and verifying correct task operations with Urdu responses.

**Acceptance Scenarios**:

1. **Given** a user sends "مجھے کام کے لیے فون کرنا ہے" (I have to call for work), **When** the message is processed, **Then** a task is created with appropriate title (translated or preserved)
2. **Given** a user asks "میرے کون سے کام باقی ہیں؟" (Which of my tasks are remaining?), **Then** the AI responds in Urdu with pending tasks
3. **Given** a user commands "ٹاسک 3 مکمل کر دو" (Complete task 3), **Then** task 3 is marked complete and AI confirms in Urdu
4. **Given** a user mixes Urdu and English ("Add a task for آج دفتر جانا"), **Then** the AI handles code-switching correctly
5. **Given** the UI language preference is set to Urdu, **When** the chatbot responds, **Then** all UI elements and messages are in Urdu

---

### User Story 5 - Voice Command Input (Priority: P5 - Bonus +200)

A user wants to add and manage tasks hands-free using voice commands. They click a microphone button, speak "Remind me to take out the trash tonight at 7pm", the audio is sent to OpenAI's Whisper API for transcription, and the AI creates the task with the correct title and due time.

**Why this priority**: Voice input enables true hands-free task management while driving, cooking, or multitasking. Using server-side Whisper API provides superior accuracy, multi-language support (including Urdu), and consistent behavior across browsers. Qualifies for the +200 bonus points for voice commands.

**Independent Test**: Can be fully tested by recording voice commands, verifying Whisper API transcription, and confirming correct task creation.

**Acceptance Scenarios**:

1. **Given** a user clicks the microphone button, **When** they speak "Create a task called dentist appointment next Tuesday at 3pm" and the audio is transcribed via Whisper, **Then** a task is created with transcribed title and parsed due date
2. **Given** a user speaks "What's on my list today?", **Then** the AI responds with today's tasks (voice or text response based on user preference)
3. **Given** background noise is present, **When** a user speaks a command, **Then** the Whisper API handles noise robustly and system requests confirmation if the transcription seems ambiguous
4. **Given** a user speaks a long description, **When** the speech is transcribed by Whisper, **Then** the full transcription is stored in the task's transcription_text field
5. **Given** a user speaks in Urdu, **When** the voice input is processed by Whisper, **Then** the Urdu speech is transcribed accurately and the task is created correctly

---

### User Story 6 - AI Task Summarization (Priority: P6)

A user wants the AI to automatically generate concise summaries of their tasks. When they have a task with a long description "Call the dentist office to schedule an appointment for next month, ask about availability on Tuesday or Thursday afternoons, confirm if they accept my insurance", the AI generates a summary "Schedule dentist appointment - check Tue/Thu availability and insurance coverage."

**Why this priority**: AI summaries improve task list readability and help users quickly understand task scope. Demonstrates LLM integration capabilities.

**Independent Test**: Can be fully tested by creating tasks with long descriptions and verifying the AI generates accurate, concise summaries stored in the ai_summary field.

**Acceptance Scenarios**:

1. **Given** a user creates a task with 200+ character description, **When** the task is saved, **Then** an ai_summary is generated under 100 characters capturing the key points
2. **Given** a user updates a task description, **When** saved, **Then** the ai_summary is regenerated to reflect changes
3. **Given** a user has multiple tasks with summaries, **When** viewing the task list, **Then** summaries are displayed instead of full descriptions for better readability
4. **Given** a task description is already short (< 50 characters), **When** saved, **Then** no summary is generated (original is sufficient)

---

### User Story 7 - MCP Tool Integration (Priority: P7)

A developer wants the AI agent to use standardized MCP (Model Context Protocol) tools for all task operations. The agent doesn't directly access the database but instead calls MCP tools like `add_task`, `list_tasks`, `complete_task` which are stateless and handle persistence.

**Why this priority**: MCP integration creates a clean separation between AI logic and data operations. Tools can be reused across different AI interfaces and the architecture remains stateless and scalable.

**Independent Test**: Can be fully tested by invoking MCP tools directly and verifying they correctly operate on the database, then testing AI agent calls to these tools.

**Acceptance Scenarios**:

1. **Given** the AI agent determines a user wants to add a task, **When** the agent calls the add_task MCP tool, **Then** the task is persisted to Neon DB and the task_id is returned
2. **Given** the AI agent needs to show tasks, **When** it calls list_tasks MCP tool with status filter, **Then** only matching tasks for that user are returned
3. **Given** an MCP tool is called with invalid parameters, **When** the error occurs, **Then** a structured error response is returned and the AI agent explains the issue to the user
4. **Given** multiple conversations are active simultaneously, **When** MCP tools are called, **Then** each operation is scoped to the correct user_id (no cross-user data leakage)
5. **Given** the server restarts, **When** an MCP tool is called, **Then** it operates correctly with no in-memory state (stateless architecture verified)

---

### User Story 8 - Agent Handoffs and Specialization (Priority: P8 - Bonus +200)

A user wants the AI to route complex requests to specialized agents. When they ask "Help me plan my week", the main agent hands off to a PlanningAgent. When they ask "What's overdue?", a TaskQueryAgent handles it. Each agent is optimized for its domain.

**Why this priority**: Agent handoffs demonstrate sophisticated multi-agent architecture and qualify for the +200 bonus points for reusable intelligence via subagents.

**Independent Test**: Can be fully tested by sending requests that should trigger different agents and verifying correct handoff and specialized responses.

**Acceptance Scenarios**:

1. **Given** a user asks "What do I need to focus on this week?", **When** the request is processed, **Then** the conversation is handed to PlanningAgent which analyzes priorities and due dates
2. **Given** a user asks "Show me overdue tasks", **When** processed, **Then** TaskQueryAgent handles the request with optimized task querying logic
3. **Given** a PlanningAgent is active, **When** the user asks "Actually, just add a quick task", **Then** the agent hands back to TodoAssistant for task creation
4. **Given** an agent handoff occurs, **When** the conversation continues, **Then** the full conversation history is available to the new agent (context preserved)
5. **Given** a specialized agent encounters an error, **When** the failure occurs, **Then** control gracefully returns to the main agent with error explanation

---

### Edge Cases

- What happens when a user sends a command the AI doesn't understand? (AI asks for clarification with example commands: "Try: 'Add a task', 'Show my tasks', 'Complete task 1'")
- How does system handle concurrent updates to the same task? (Last write wins with optimistic locking, conflict notification)
- What happens when Qdrant vector search is unavailable? (Fallback to keyword search, log error, notify user)
- How does system handle extremely long task descriptions (>1000 characters)? (Truncate with ellipsis for display, store full text, generate summary)
- What happens when audio transcription is ambiguous or unclear? (Request user confirmation: "Did you say: [transcription]?")
- How does system handle user switching accounts mid-conversation? (Invalidate conversation context, require new conversation start)
- What happens when MCP tool times out (>30 seconds)? (Return error to AI agent, agent apologizes and suggests retry)
- What happens when a task referenced by ID no longer exists? (AI explains "Task X was deleted" and offers to show remaining tasks)
- How does system handle emoji and special characters in task titles? (Store as-is, escape in JSON responses, render in UI)
- What happens when OpenAI API rate limit is hit? (Queue request, return "processing" status, retry with exponential backoff)
- What happens when uploaded audio file exceeds 25 MB limit? (Reject with error message, suggest shorter recording)
- What happens when Whisper API returns non-ASCII text (Urdu, Chinese, etc.)? (Store as UTF-8, display correctly in UI)
- What happens when audio file format is not supported? (Return 415 error with list of supported formats)
- What happens when user sends extremely long message (>5000 characters)? (Reject with 400 error, suggest breaking into multiple messages)
- What happens when rapid consecutive messages from same user? (Queue per conversation, process sequentially, maintain order)
- What happens when conversation exceeds 50 message limit? (Rolling window: archive oldest messages with AI-generated summary, keep last 50 active)
- What happens when Qdrant search returns zero results? (Return empty results, offer keyword search alternative)
- What happens with mixed script text (Arabic + English numbers)? (Store as UTF-8, render with appropriate direction per segment)
- What happens with circular agent handoffs (Agent A → B → A)? (Detect and prevent after 2 hops, return to main agent)
- What happens during zero-state (no tasks, first-time user)? (Show welcome message, suggest first task creation)
- What happens when user switches language mid-conversation? (Detect language change, update conversation preference, adapt responses)
- What happens when user sends emoji-only message? (Treat as normal message, AI interprets emoji contextually: 👍 = confirmation, ❓ = question)
- What happens when user tries to use voice and text input simultaneously? (UI prevents: microphone button disables text input, typing disables mic)
- What happens when extending beyond 3 agents? (Architecture supports N agents via handoffs array, new agents must follow handoff return pattern)

### Error Handling Specifications

**★ Insight ─────────────────────────────────────**
Error messages must balance helpfulness with security. Never expose internal details to clients, but provide enough information for users to understand what went wrong and how to fix it.
─────────────────────────────────────────────────

#### Error Message Templates

| Error Type | User Message | Log Level | HTTP Status |
|------------|--------------|-----------|-------------|
| `auth_missing` | "Please sign in to access the chat" | INFO | 401 |
| `auth_invalid` | "Your session expired. Please sign in again" | WARN | 401 |
| `auth_expired` | "Your session expired. Please refresh to continue" | INFO | 401 |
| `rate_limit_exceeded` | "You're sending messages too quickly. Please wait {seconds} seconds." | INFO | 429 |
| `message_too_long` | "Your message is too long. Maximum is 5000 characters." | INFO | 400 |
| `conversation_not_found` | "This conversation doesn't exist or was deleted." | INFO | 404 |
| `task_not_found` | "Task {task_id} doesn't exist or was deleted." | INFO | 404 |
| `mcp_tool_timeout` | "The request took too long. Please try again." | WARN | 504 |
| `openai_rate_limit` | "The service is busy. Your request is queued and will be processed shortly." | WARN | 503 |
| `openai_unavailable` | "The AI service is temporarily unavailable. Please try again in a few minutes." | ERROR | 503 |
| `qdrant_unavailable` | "Search is temporarily unavailable. Using keyword search instead." | WARN | 200 (degraded) |
| `whisper_error` | "Could not transcribe audio. Please try again or type your message." | WARN | 500 |
| `audio_too_large` | "Audio file is too large. Maximum is 25 MB." | INFO | 413 |
| `audio_unsupported_format` | "Audio format not supported. Please use MP3, M4A, or WAV." | INFO | 415 |
| `transcription_confidence_low` | "I'm not sure I understood correctly. Did you say: '{transcription}'?" | INFO | 200 (confirmation) |
| `ambiguous_command` | "I'm not sure what you mean. Did you want to: create a task, show tasks, or complete a task?" | INFO | 200 (clarification) |

#### Retry Mechanism

**FR-099**: System MUST implement retry with exponential backoff for transient failures

- **Retryable errors**: OpenAI 429 (rate limit), OpenAI 5xx, Qdrant connection errors
- **Non-retryable**: 400 (bad request), 401 (auth), 403 (forbidden), 404 (not found)
- **Backoff strategy**: 1s, 2s, 4s, 8s (max 4 attempts)
- **Jitter**: Add random ±25% to backoff to prevent thundering herd

```python
async def retry_with_backoff(operation, max_attempts=4):
    for attempt in range(max_attempts):
        try:
            return await operation()
        except RetryableError as e:
            if attempt == max_attempts - 1:
                raise
            backoff = (2 ** attempt) + random.uniform(-0.25, 0.25)
            await asyncio.sleep(backoff)
```

#### JWT Token Refresh Flow

**FR-100**: System MUST handle JWT token refresh for long-running conversations

- **Token validation**: Check JWT exp claim on each request
- **Refresh mechanism**: Frontend calls /api/auth/token endpoint via Better Auth
- **Refresh trigger**: When JWT expires within 30 seconds
- **SSE handling**: If JWT expires during SSE stream, send event: `{"type": "auth_refresh_required"}`
- **Graceful period**: Allow 5-minute grace period for ongoing streams

#### Orphaned Conversation Handling

**FR-101**: System MUST handle orphaned conversations (user account deletion)

- **Detection**: Foreign key ON DELETE CASCADE from users to conversations
- **Archive before delete**: Soft-delete conversations 30 days before permanent deletion
- **Notification**: Email user before deletion if email available
- **Anonymization**: For anonymous users, delete after 90 days per FR-095

#### OpenAI Rate Limit Handling

**FR-102**: System MUST handle OpenAI API rate limits gracefully

- **Detection**: Catch 429 responses from OpenAI API
- **Response**: Return 503 to client with Retry-After header
- **Queue**: Queue request for retry after rate limit window
- **Logging**: Log rate limit events with tokens used and window reset time
- **Circuit breaker**: Open circuit after 5 consecutive rate limit errors, reset after 60 seconds

#### Qdrant Connection Recovery

**FR-103**: System MUST implement Qdrant connection recovery

- **Health check**: Ping Qdrant before each search operation
- **Reconnection**: Exponential backoff reconnection: 1s, 2s, 4s, 8s, 16s (max 30s)
- **Fallback**: Use keyword search during Qdrant unavailability
- **Circuit breaker**: Open circuit after 3 consecutive failures, attempt reconnection every 30 seconds
- **State tracking**: Track connection state: CONNECTED, DISCONNECTED, RECONNECTING

### Non-Functional Requirements

**★ Insight ─────────────────────────────────────**
Non-functional requirements determine production readiness. Data retention, compliance, and cost management are not "nice-to-haves" - they're essential for sustainable operation.
─────────────────────────────────────────────────

#### Data Retention and Compliance

**FR-104**: System MUST implement data retention policies

| Data Type | Retention Period | Deletion Method |
|-----------|------------------|-----------------|
| Active conversations | 90 days | Soft-delete (marked deleted) |
| Archived conversations | 30 days in archive | Permanent deletion |
| Messages (in active conversations) | 90 days | Cascade with conversation |
| Messages (in archived conversations) | 30 days | Permanent deletion |
| Agent handoff records | 90 days | Permanent deletion |
| Transcriptions (in tasks) | As long as task exists | Cascade with task |
| AI summaries | As long as task exists | Cascade with task |
| Audit logs | 30 days | Permanent deletion |

**FR-105**: System MUST support GDPR right to erasure
- User can request account deletion via /api/account/delete
- All user data soft-deleted within 24 hours
- Permanent deletion within 30 days
- Email confirmation sent before permanent deletion

**FR-106**: System MUST implement data export functionality
- Users can export all data via /api/account/export
- Export format: JSON with all conversations, messages, tasks
- Export delivered via email or download link (expires in 24 hours)

#### Cost Management

**FR-107**: System MUST implement OpenAI API cost controls

| Metric | Limit | Action |
|--------|-------|--------|
| Tokens per user per day | 100,000 | Return warning, throttle requests |
| Tokens per user per month | 2,000,000 | Return error, suggest upgrade |
| Whisper transcriptions per day | 100 | Return error, suggest text input |
| Total tokens per hour (system) | 1,000,000 | Circuit breaker, alert admins |

**FR-108**: System MUST track and log API costs
- Log token usage per request (model, tokens, estimated cost)
- Aggregate costs per user per day/month
- Alert when approaching budget limits
- Cost estimates based on OpenAI pricing:
  - GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
  - text-embedding-3-small: $0.02/1M tokens
  - Whisper: $0.006/minute

#### Scalability Requirements

**FR-109**: System MUST scale to support growth

| Metric | Target | Notes |
|--------|--------|-------|
| Concurrent conversations | 100 (MVP), 1000 (Phase IV) | Per-instance, horizontal scaling |
| Messages per second | 50 (MVP), 500 (Phase IV) | With SSE streaming |
| MCP tool calls per minute | 500 (MVP), 5000 (Phase IV) | Stateless enables scaling |
| Vector search latency | < 500ms (p95) | For < 10k vectors |
| Database connections | 50 max | Connection pooling required |

#### Backup and Recovery

**FR-110**: System MUST implement backup procedures
- Database backup: Daily at 2 AM UTC, retained for 30 days
- Qdrant backup: Weekly snapshot, retained for 4 weeks
- Backup location: Secure cloud storage (encrypted)
- Recovery time objective (RTO): 4 hours
- Recovery point objective (RPO): 24 hours

#### Monitoring and Alerting

**FR-111**: System MUST implement production monitoring

| Metric | Alert Threshold | Severity |
|--------|----------------|----------|
| Error rate | > 5% | Critical |
| P95 latency | > 5 seconds | Warning |
| P99 latency | > 15 seconds | Critical |
| OpenAI failure rate | > 10% | Warning |
| Qdrant failure rate | > 5% | Warning |
| Database connection pool | > 90% utilized | Warning |
| Memory usage | > 80% | Critical |
| Disk usage | > 85% | Warning |

**FR-112**: System MUST provide health check endpoint
- GET /health returns: {status: "healthy", services: {db: "ok", qdrant: "ok", openai: "ok"}}
- Response time: < 100ms
- Used by load balancers for instance health

#### Performance Requirements

**FR-113**: System MUST meet performance targets

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Chat message send | 500ms | 3s | 10s |
| First token (SSE) | 300ms | 1s | 3s |
| Semantic search | 100ms | 500ms | 2s |
| Task creation | 200ms | 1s | 2s |
| Conversation list | 100ms | 500ms | 1s |
| Voice transcription | 1s | 3s | 10s |

#### Accessibility

**FR-114**: Frontend MUST meet WCAG 2.1 Level AA
- Keyboard navigation for all chat functions
- Screen reader announcements for new messages
- Focus indicators on all interactive elements
- Color contrast ratio ≥ 4.5:1 for text
- ARIA labels for chat interface components
- Voice input alternative (microphone button has keyboard shortcut)

#### User Feedback and Satisfaction Measurement

**FR-115**: System MUST collect user feedback for satisfaction measurement

- **Feedback trigger**: Show survey modal after every 5 chat sessions
- **Survey timing**: Display 30 seconds after session ends (not during active use)
- **Survey questions** (3 questions max):
  1. "How helpful was the chatbot today?" (1-5 stars)
  2. "Did the chatbot understand you correctly?" (Yes/No)
  3. "Any suggestions for improvement?" (optional text)
- **Storage**: Store responses in user_feedback table with user_id, timestamp, session_id
- **Aggregation**: Calculate average satisfaction score per user (SC-009: 4.0/5.0 target)
- **Opt-out**: Users can disable surveys via settings
- **Data retention**: Feedback data retained for 90 days

**FR-116**: System MUST track implicit satisfaction signals

- **Task completion rate**: % of chat-initiated tasks that are completed (not abandoned)
- **Clarification rate**: % of messages requiring AI clarification (lower = better)
- **Repeat usage**: % of users who return within 7 days (engagement metric)
- **Session length**: Average messages per conversation (engagement depth)

## Requirements *(mandatory)*

### Functional Requirements

#### Core Chatbot Features (200 points base)

- **FR-001**: System MUST provide POST /api/chat endpoint accepting message and optional conversation_id
- **FR-002**: System MUST use OpenAI Agents SDK with gpt-4o-mini model for agent logic
- **FR-003**: System MUST maintain conversation history in Neon DB (conversations and messages tables)
- **FR-004**: System MUST implement stateless Runner pattern - no in-memory conversation state between requests
- **FR-005**: System MUST persist user messages and assistant responses before returning response
- **FR-006**: System MUST support conversation resumption after server restart via database
- **FR-007**: System MUST authenticate all chat requests via JWT token (extract user_id from sub claim)
- **FR-008**: System MUST scope all operations to the authenticated user_id (no cross-user data access)
- **FR-009**: System MUST return response within 15 seconds for 95% of requests
- **FR-010**: System MUST support streaming responses via Server-Sent Events (SSE) for token-by-token delivery, providing real-time feedback as AI generates response

#### Natural Language Processing

- **FR-011**: AI MUST understand task creation commands ("add", "create", "remember", "remind me to")
- **FR-012**: AI MUST understand task listing commands ("show", "list", "what's", "display")
- **FR-013**: AI MUST understand task completion commands ("complete", "done", "finish", "mark as done")
- **FR-014**: AI MUST understand task deletion commands ("delete", "remove", "cancel")
- **FR-015**: AI MUST understand task update commands ("change", "update", "modify", "rename")
- **FR-016**: AI MUST extract task priorities from natural language with explicit mapping:
  - **"urgent"** → Priority.HIGH (most time-sensitive)
  - **"important"** → Priority.MEDIUM (significant but not urgent)
  - **"high priority"** → Priority.HIGH (explicitly stated importance)
  - **"low priority"** → Priority.LOW (explicitly stated low importance)
  - **"asap"** → Priority.HIGH (as soon as possible)
  - **"eventually"** → Priority.LOW (no urgency)
  - Default: Priority.MEDIUM if no priority specified
- **FR-017**: AI MUST extract due dates from natural language ("tomorrow", "next week", "Friday at 3pm")
  - **Ambiguity handling**: For "next Friday" on Thursday, interpret as the upcoming Friday (not the following week)
  - **Time defaults**: When time not specified, default to 9:00 AM for task due dates
  - **Timezone**: Use user's timezone preference (default UTC)
- **FR-018**: AI MUST handle ambiguous requests by asking clarifying questions
- **FR-019**: AI MUST confirm all actions with user before executing (undo opportunity)
- **FR-020**: AI MUST handle multi-turn conversations with context from previous messages

#### MCP Tools Specification

- **FR-021**: System MUST implement MCP server using official MCP Python SDK
- **FR-022**: MCP MUST expose add_task tool with parameters: user_id, title, description (optional), priority (optional), due_date (optional)
- **FR-023**: MCP MUST expose list_tasks tool with parameters: user_id, status (optional: all/pending/completed), limit (optional), offset (optional)
- **FR-024**: MCP MUST expose complete_task tool with parameters: user_id, task_id
- **FR-025**: MCP MUST expose delete_task tool with parameters: user_id, task_id
- **FR-026**: MCP MUST expose update_task tool with parameters: user_id, task_id, title (optional), description (optional), priority (optional), due_date (optional)
- **FR-027**: All MCP tools MUST be stateless (accept user_id, perform operation, return result)
- **FR-028**: MCP tools MUST return structured responses with status, data/error, and message
- **FR-029**: MCP tools MUST validate user owns the task before operations (404 if not, not 403)
- **FR-030**: MCP tool errors MUST be caught by AI agent and explained to user in natural language

#### Semantic Vector Search with Qdrant

- **FR-031**: System MUST integrate Qdrant vector database for semantic task search
- **FR-032**: System MUST generate embeddings for tasks using text-embedding-3-small model
- **FR-033**: System MUST store embedding_id in tasks table linking to Qdrant vector
- **FR-034**: System MUST create task embedding on task creation and update
- **FR-035**: System MUST expose semantic_search MCP tool with parameters: user_id, query, limit
- **FR-036**: System MUST return semantically similar tasks ranked by cosine similarity
- **FR-037**: Semantic search MUST find tasks by meaning not just keywords (e.g., "financial" finds "pay bills")
- **FR-038**: System MUST fallback to keyword search if Qdrant is unavailable
- **FR-039**: System MUST scope vector searches to user_id (no cross-user semantic search)
- **FR-040**: System MUST handle Qdrant connection errors gracefully with fallback

#### Multi-Language Urdu Support (+100 bonus)

- **FR-041**: System MUST support Urdu language input (Urdu script: اردو)
- **FR-042**: AI MUST detect language from user message (English vs Urdu) using character analysis
  - **Detection method**: If >30% of characters are in Unicode Arabic block (U+0600-U+06FF), classify as Urdu
  - **Code-switching detection**: Mixed text classified by dominant script, preserve both in storage
- **FR-043**: System MUST respond in the same language as user input
- **FR-044**: System MUST support task titles in Urdu characters
- **FR-045**: System MUST support mixed English-Urdu (code-switching) within same message
- **FR-046**: AI MUST understand Urdu task management commands:
  | English | Urdu | Roman Urdu |
  |---------|------|------------|
  | Add | شامل کرو | shamil karo |
  | Create | بنائو | banao |
  | Show | دکھاؤ | dikhao |
  | List | فہرست | fehrist |
  | Complete | مکمل | mukammal |
  | Done | ہو گیا | ho gaya |
  | Delete | حذف کرو | hazf karo |
  | Remove | ہٹاؤ | hatao |
  | Update | اپ ڈیٹ | update |
  | Change | تبدیل کرو | tabdeel karo |
  | Task | ٹاسک | task |
  | Tomorrow | کل | kal |
  | Today | آج | aaj |
  | Pending | زیر التوا | zair-e-intizaar |
  | Remaining | باقی | baqi |
  | Finish | ختم | khatam |
- **FR-047**: System MUST store Urdu text correctly in PostgreSQL (UTF-8)
- **FR-048**: System MUST render Urdu text right-to-left in UI using `dir="rtl"` attribute
- **FR-049**: User MUST be able to set language preference (auto-detect default)
- **FR-050**: AI MUST handle Roman Urdu (Urdu written with Latin script) optionally

#### Voice Commands (+200 bonus)

- **FR-051**: System MUST provide microphone button in chat interface
- **FR-052**: System MUST provide POST /api/chat/transcribe endpoint accepting audio file (Multipart/form-data)
- **FR-053**: System MUST use OpenAI Whisper API (whisper-1 model) for server-side speech-to-text transcription
- **FR-054**: System MUST support audio formats: MP3, MP4, M4A, MPEG, MPGA, WAV, WEBM (max 25 MB file size)
- **FR-055**: System MUST transcribe voice input to text and return transcription before sending to chat endpoint
- **FR-056**: System MUST support Urdu speech recognition via Whisper's multilingual capabilities
- **FR-057**: System MUST automatically detect language from audio ( Whisper's language detection feature)
- **FR-058**: System MUST store full transcription in task.transcription_text field
- **FR-059**: System MUST provide visual feedback during recording and upload (pulse animation + upload progress)
- **FR-060**: System MUST limit audio recordings to 30 seconds maximum for cost containment
- **FR-061**: System MUST handle Whisper API errors gracefully (fallback to text input, show error message)

#### AI Task Summarization

- **FR-062**: System MUST generate AI summary for task descriptions > 100 characters
- **FR-063**: Summary MUST be stored in task.ai_summary field
- **FR-064**: Summary MUST be under 100 characters capturing key points
- **FR-065**: Summary MUST be regenerated when task description is updated
- **FR-066**: System MUST display summary in task list instead of full description
- **FR-067**: Summarization MUST use GPT-4o-mini for cost efficiency
- **FR-068**: System MUST handle summarization API errors (fallback to full description)
- **FR-069**: Short descriptions (< 50 chars) MUST NOT be summarized (use original)

#### Agent Handoffs and Specialization (+200 bonus)

- **FR-070**: System MUST implement main TodoAssistant agent for general commands
  - **Triggers**: All chat requests initially route through TodoAssistant
  - **Instructions**: Task CRUD, basic conversation handling, clarification requests
  - **Handoff criteria**: Detect keywords requiring specialized handling

- **FR-071**: System MUST implement PlanningAgent for weekly planning and prioritization
  - **Triggers**: Keywords: "plan my week", "help me prioritize", "what should I focus on", "organize my tasks"
  - **Instructions**: Analyze upcoming tasks, suggest priorities, identify overloaded days
  - **Return criteria**: After presenting plan or when user asks to create specific task

- **FR-072**: System MUST implement TaskQueryAgent for complex task searches and filtering
  - **Triggers**: Keywords: "find", "search", "show me [concept]", complex queries, semantic searches
  - **Instructions**: Use semantic_search tool, interpret results, filter by criteria
  - **Return criteria**: After presenting search results or when user selects a task

- **FR-073**: System MUST implement handoff mechanism between agents
  - **Handoff timeout**: < 100ms for transfer completion
  - **Context preservation**: Full conversation history passed to new agent
  - **Circular detection**: Prevent Agent A → B → A loops (max 2 hops before return to main)

- **FR-074**: Handoffs MUST preserve full conversation context
  - **Context snapshot**: Last 50 messages, active tasks mentioned, user preferences
  - **Handoff reason**: Logged in agent_handoffs table for debugging

- **FR-075**: Specialized agents MUST return to main agent after completing specialized task
  - **Auto-return**: After task completion (search results presented, plan created)
  - **User override**: User can explicitly request main agent ("nevermind", "cancel", "go back")

- **FR-076**: Agent handoffs MUST be transparent to user (seamless experience)
  - **No interruption**: Streaming continues during handoff
  - **Visual indicator**: Optional subtle badge showing current agent (for debugging)

- **FR-077**: Each agent MUST have specialized instructions for its domain
  - **TodoAssistant**: "You are a helpful todo assistant. Use MCP tools to manage tasks. Hand off to PlanningAgent for weekly planning, TaskQueryAgent for complex searches."
  - **PlanningAgent**: "You are a planning specialist. Analyze tasks, suggest priorities, identify time conflicts. Always return to TodoAssistant after presenting the plan."
  - **TaskQueryAgent**: "You are a search specialist. Use semantic_search for conceptual queries. Always return to TodoAssistant after presenting results."

**FR-078**: System MUST support extensible agent architecture for future expansion
- **Handoffs array**: Agents accept dynamic handoffs array for N agent support
- **New agent requirements**: Any new agent MUST:
  - Accept conversation history (last 50 messages)
  - Return to TodoAssistant after completing specialized task
  - Log handoff events to agent_handoffs table
  - Follow same instruction format (name, instructions, handoffs, tools)
- **Example future agents**: NotificationAgent (scheduling digest notifications), CalendarAgent (calendar integration), AnalyticsAgent (task insights)

#### ChatKit Frontend Integration

- **FR-079**: Frontend MUST use OpenAI ChatKit for chat UI
- **FR-080**: Chat interface MUST match Deep Space theme (glassmorphism, cyan accents) with specific color values:
  ```css
  /* Deep Space Theme - OKLCH Color Space */
  --custom-background: oklch(0.08 0.01 270);     /* Deep space black */
  --custom-foreground: oklch(0.95 0.01 270);     /* Near white */
  --custom-primary: oklch(0.91 0.17 195);        /* Neon cyan #00f5ff */
  --custom-secondary: oklch(0.65 0.26 293);      /* Neon purple #a855f7 */
  --custom-muted: oklch(0.25 0.01 270);          /* Dark gray */
  --custom-accent: oklch(0.70 0.20 330);         /* Pink accent */
  --custom-success: oklch(0.65 0.20 145);        /* Green */
  --custom-destructive: oklch(0.60 0.25 25);      /* Red */

  /* Glassmorphism effects */
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
  --glow-primary: 0 0 20px rgba(0, 245, 255, 0.3);

  /* Spacing */
  --chat-padding: 1rem;
  --message-gap: 0.75rem;
  --input-height: 60px;
  ```
- **FR-081**: Chat MUST display user messages and AI responses with different styling
- **FR-082**: Chat MUST show typing indicator only until first token arrives, then display streaming tokens in real-time
- **FR-083**: Chat MUST auto-scroll to latest message
- **FR-084**: Chat MUST support message history loading (pagination for long conversations)
- **FR-085**: System MUST render task cards in chat when AI creates/displays tasks
- **FR-086**: System MUST support quick actions on chat task cards (complete, delete, edit)
- **FR-087**: Chat MUST be accessible from /chat route and as a floating widget

#### Error Handling and Edge Cases

- **FR-088**: System MUST return 401 for requests without valid JWT
- **FR-089**: System MUST implement per-user rate limiting at 30 requests/minute, return 429 with retry-after header when exceeded
- **FR-090**: System MUST implement structured logging with correlation IDs for all requests
- **FR-091**: System MUST log all AI agent tool calls with parameters, results, and timing
- **FR-092**: System MUST log agent handoff events with from_agent, to_agent, and context snapshot
- **FR-093**: System MUST handle OpenAI API outages gracefully (cached responses or apology)
- **FR-094**: System MUST sanitize user input to prevent prompt injection
- **FR-095**: System MUST implement rolling window for conversation history: keep last 50 messages active, automatically archive older messages with AI-generated summary for context continuity
- **FR-096**: System MUST archive conversations older than 90 days
- **FR-097**: System MUST handle concurrent message processing (queue per conversation)
- **FR-098**: System MUST timeout AI agent calls after 30 seconds
- **FR-099**: System MUST implement circuit breaker for failing external APIs

---

## Observability & Structured Logging *(mandatory)*

### Backend Observability Requirements

**★ Insight ─────────────────────────────────────**
Observability is NOT optional for distributed AI systems. With agent handoffs, MCP tool calls, external APIs (OpenAI, Qdrant, Whisper), and SSE streaming, debugging without structured logging is nearly impossible. These requirements enforce "debuggability by default."
─────────────────────────────────────────────────

#### Log Schema Requirements

All log entries MUST follow this structured JSON schema:

```json
{
  "timestamp": "ISO-8601 with timezone (UTC)",
  "level": "debug|info|warn|error",
  "correlation_id": "UUID v4 - propagates through entire request",
  "user_id": "extracted from JWT sub claim",
  "service": "chat|mcp|agents|search|embeddings|voice",
  "component": "module or class name",
  "event_type": "specific event category",
  "message": "human-readable description",
  "data": {
    "key": "event-specific structured data"
  },
  "metrics": {
    "duration_ms": "operation duration",
    "tokens_used": "OpenAI token count",
    "db_queries": "number of database queries"
  },
  "error": {
    "type": "exception class name",
    "message": "error message",
    "stack_trace": "full stack trace (error level only)"
  }
}
```

#### Functional Requirements - Observability

- **LOG-001**: System MUST use Python `structlog` library for structured JSON logging
- **LOG-002**: System MUST generate and propagate `correlation_id` for ALL requests (generate if not provided in header)
- **LOG-003**: System MUST log correlation_id in: (a) ALL application logs, (b) ALL database queries (via comment), (c) ALL external API calls (via header)
- **LOG-004**: System MUST include `X-Correlation-ID` header in ALL API responses
- **LOG-005**: System MUST accept external `X-Correlation-ID` header from frontend for trace continuity
- **LOG-006**: System MUST log at `INFO` level for: request start, request end, agent handoffs, tool calls
- **LOG-007**: System MUST log at `DEBUG` level for: state transitions, context snapshots, internal decisions
- **LOG-008**: System MUST log at `WARN` level for: retries, fallback activations, degraded performance
- **LOG-009**: System MUST log at `ERROR` level for: all exceptions, API failures, timeouts
- **LOG-010**: System MUST NEVER log sensitive data: JWT tokens, API keys, user passwords, PII

#### Request Tracing Requirements

- **LOG-011**: System MUST log request start with: correlation_id, user_id, endpoint, method, path
- **LOG-012**: System MUST log request end with: correlation_id, status_code, duration_ms, response_size
- **LOG-013**: System MUST log all middleware events: auth validation, rate limit check, correlation ID binding
- **LOG-014**: System MUST log database queries with: correlation_id, table, operation_type, duration_ms, row_count
- **LOG-015**: System MUST use contextvars to propagate correlation_id across async boundaries

#### MCP Tool Logging Requirements

- **LOG-020**: System MUST log before each MCP tool call with: tool_name, parameters (sanitized), user_id, correlation_id
- **LOG-021**: System MUST log after each MCP tool call with: tool_name, result_status, duration_ms, error (if failed)
- **LOG-022**: System MUST log MCP tool call parameters with sensitive values redacted (passwords, tokens)
- **LOG-023**: System MUST aggregate tool call metrics: total_calls_by_tool, avg_duration_by_tool, error_rate_by_tool
- **LOG-024**: System MUST log tool validation failures with: field_name, validation_error, correlation_id

#### Agent Handoff Logging Requirements

- **LOG-030**: System MUST log agent handoff initiation with: from_agent, to_agent, reason, conversation_id, correlation_id
- **LOG-031**: System MUST log agent handoff completion with: from_agent, to_agent, duration_ms, success, correlation_id
- **LOG-032**: System MUST log agent handoff failures with: from_agent, to_agent, error_type, error_message, fallback_action
- **LOG-033**: System MUST store handoff records in `agent_handoffs` table for audit trail
- **LOG-034**: System MUST log context_snapshot on handoff (conversation state at handoff time)

#### External API Logging Requirements

- **LOG-040**: System MUST log OpenAI API calls with: model, endpoint_type (chat/embeddings/audio), tokens_used, duration_ms
- **LOG-041**: System MUST log Qdrant operations with: collection_name, operation_type, vector_count, duration_ms, success
- **LOG-042**: System MUST log Whisper transcriptions with: duration_seconds, detected_language, confidence, duration_ms
- **LOG-043**: System MUST log external API retries with: attempt_number, max_retries, error_code, backoff_ms
- **LOG-044**: System MUST log circuit breaker state changes with: service_name, old_state, new_state, failure_count

#### Streaming (SSE) Logging Requirements

- **LOG-050**: System MUST log SSE connection start with: correlation_id, user_id, conversation_id
- **LOG-051**: System MUST log SSE connection end with: correlation_id, duration_ms, tokens_sent, events_sent
- **LOG-052**: System MUST log SSE disconnections (abnormal) with: correlation_id, reason, bytes_sent
- **LOG-053**: System MUST log each SSE event type for debugging: message_start, token, tool_call, message_done, error

#### Performance Metrics Requirements

- **LOG-060**: System MUST log request duration percentiles: p50, p95, p99 (aggregated per minute)
- **LOG-061**: System MUST log database query performance: slow_query_threshold_ms=500, log queries exceeding threshold
- **LOG-062**: System MUST log active concurrent requests: current_count, user_id breakdown
- **LOG-063**: System MUST log rate limit events: user_id, requests_count, window_start, blocked=true|false
- **LOG-064**: System MUST log token usage: total_tokens_per_minute, cost_estimate

#### Error Tracking Requirements

- **LOG-070**: System MUST log all errors with full stack trace in `error.stack_trace` field
- **LOG-071**: System MUST include error categorization: validation_error|auth_error|api_error|db_error|unknown
- **LOG-072**: System MUST implement error aggregation: count unique errors per minute for alerting
- **LOG-073**: System MUST log user-friendly error messages separately from internal error details
- **LOG-074**: System MUST NEVER expose internal errors or stack traces to API clients

#### Log Storage & Retention

- **LOG-080**: System MUST write logs to stdout for container/Cloud logging capture
- **LOG-081**: System MUST support log level configuration via environment variable `LOG_LEVEL` (default: INFO)
- **LOG-082**: System MUST implement log sampling for DEBUG logs in production (sample_rate=0.01)
- **LOG-083**: System MUST retain logs for 30 days in production (compliance, debugging window)
- **LOG-084**: System MUST support structured log queries (JSON parsing) for debugging tools

#### Observability Success Criteria

- **SC-OBS-001**: 100% of requests have traceable correlation_id from ingress to egress
- **SC-OBS-002**: All MCP tool calls are auditable with parameters and results
- **SC-OBS-003**: All agent handoffs are traceable with context preservation verification
- **SC-OBS-004**: 95% of errors have sufficient context for root cause analysis within 5 minutes
- **SC-OBS-005**: Log query can reconstruct full conversation flow for any conversation_id
- **SC-OBS-006**: Performance bottlenecks identifiable from log metrics within 1 minute

---

## Acceptance Criteria for Observability

When implementing Phase III, developers must verify:

1. **Logs are queryable**: Can search logs by `correlation_id` and see entire request lifecycle
2. **Logs are structured**: All logs parse as valid JSON with consistent schema
3. **Logs are complete**: Every database operation, API call, and agent action is logged
4. **Logs are safe**: No secrets, tokens, or sensitive PII in log output
5. **Logs are actionable**: Error logs contain enough context to diagnose without code inspection

### Key Entities

- **Conversation**: Represents a chat session with id, user_id, title (auto-generated after 3 messages via GPT-4o-mini summary, or user-set), language_preference (en/ur/auto), created_at, updated_at, message_count

- **Message**: Represents a single message with id, conversation_id, correlation_id (for tracing), role (user/assistant/system), content, tool_calls (JSON array of tools invoked), created_at

- **Task**: Extended from Phase II with new fields - transcription_text (full voice transcription), ai_summary (LLM-generated summary), embedding_id (Qdrant vector reference)

- **AgentHandoff**: Represents agent handoff events with id, conversation_id, from_agent, to_agent, reason, timestamp, context_snapshot

- **ConversationPreference**: User's chat settings with id, user_id, language (en/ur/auto), voice_enabled (bool), response_format (text/voice), notifications_enabled

## Success Criteria *(mandatory)*

### Per-User Story Success Criteria

**★ Insight ─────────────────────────────────────**
Each user story has its own success criteria to enable independent testing and validation. Stories can be verified individually before integration.
─────────────────────────────────────────────────

#### User Story 1: Natural Language Task Management

- **SC-US1-001**: 90% of natural language task creation commands successfully create tasks
- **SC-US1-002**: 90% of task listing queries return correct filtered results
- **SC-US1-003**: 95% of task completion commands correctly update task status
- **SC-US1-004**: 85% of ambiguous requests trigger clarifying questions (not guesses)
- **SC-US1-005**: 100% of task operations are scoped to authenticated user_id (no leakage)
- **SC-US1-006**: SSE streaming delivers first token within 1 second for 95% of requests

#### User Story 2: Conversational Context Memory

- **SC-US2-001**: AI correctly references previous context in 90% of multi-turn conversations
- **SC-US2-002**: Conversation history persists across server restarts (100% data integrity)
- **SC-US2-003**: Resuming a conversation after 1 hour maintains full context
- **SC-US2-004**: Conversation auto-titles are generated after 3 messages with meaningful names
- **SC-US2-005**: Last 50 messages are correctly loaded and passed to agents

#### User Story 3: Semantic Task Search

- **SC-US3-001**: Semantic search returns relevant results for 85% of conceptual queries
- **SC-US3-002**: "Financial obligations" query finds tasks containing "pay bills", "credit card"
- **SC-US3-003**: Qdrant search completes within 500ms for collections < 10,000 vectors
- **SC-US3-004**: Fallback to keyword search activates within 1 second when Qdrant unavailable
- **SC-US3-005**: Search results are ranked by relevance (cosine similarity)

#### User Story 4: Multi-Language Urdu Support (+100 bonus)

- **SC-US4-001**: 80% of Urdu task commands are correctly identified and executed
- **SC-US4-002**: Language detection accuracy exceeds 90% for pure English or Urdu text
- **SC-US4-003**: Urdu text renders correctly with right-to-left alignment
- **SC-US4-004**: Mixed English-Urdu messages are handled correctly (code-switching)
- **SC-US4-005**: AI responses match detected language (English for English input, Urdu for Urdu)
- **SC-US4-006**: Urdu text is stored and retrieved without character corruption (UTF-8 validation)

#### User Story 5: Voice Command Input (+200 bonus)

- **SC-US5-001**: 75% transcription accuracy for clear English speech
- **SC-US5-002**: 60% transcription accuracy for Urdu speech
- **SC-US5-003**: Transcription completes within 5 seconds for 30-second audio
- **SC-US5-004**: Ambiguous transcriptions (< 80% confidence) trigger confirmation prompt
- **SC-US5-005**: Audio files exceeding 25 MB are rejected with clear error message
- **SC-US5-006**: Full transcription is stored in task.transcription_text field

#### User Story 6: AI Task Summarization

- **SC-US6-001**: AI summaries are generated for 100% of task descriptions > 100 characters
- **SC-US6-002**: Summaries are under 100 characters while preserving key information
- **SC-US6-003**: Summary regeneration occurs when description is updated
- **SC-US6-004**: Descriptions < 50 characters bypass summarization (use original)
- **SC-US6-005**: AI summaries reduce display length by 60% on average

#### User Story 7: MCP Tool Integration

- **SC-US7-001**: All MCP tools return structured responses with status, data/error, message
- **SC-US7-002**: 100% of MCP tool calls include correlation ID for tracing
- **SC-US7-003**: MCP tools handle 10,000 calls per hour without degradation
- **SC-US7-004**: Stateless architecture verified (server restart doesn't affect tool execution)
- **SC-US7-005**: Tool timeouts (> 30s) return graceful errors to AI agent

#### User Story 8: Agent Handoffs (+200 bonus)

- **SC-US8-001**: Agent handoffs complete successfully in 95% of cases
- **SC-US8-002**: Handoff completes within 100ms (no user-visible delay)
- **SC-US8-003**: Full conversation context preserved during handoff
- **SC-US8-004**: Circular handoffs (A→B→A) are detected and prevented
- **SC-US8-005**: Specialized agents return to main agent after task completion
- **SC-US8-006**: Agent handoff records are logged in database for audit trail

### Cross-Cutting Measurable Outcomes

- **SC-001**: Chat endpoint responds within 3 seconds for 95% of requests
- **SC-002**: AI correctly identifies user intent (create/list/complete/delete/update) in 90% of natural language requests
- **SC-003**: Semantic search returns relevant results for 85% of conceptual queries
- **SC-004**: Urdu language support achieves 80% intent recognition accuracy
- **SC-005**: Voice transcription achieves 75% accuracy for clear English speech, 60% for Urdu
- **SC-006**: Agent handoffs complete successfully in 95% of cases without user confusion
- **SC-007**: MCP tools handle 10,000 calls per hour without degradation
- **SC-008**: Conversation history persists correctly across server restarts (100% data integrity)
- **SC-009**: User satisfaction score exceeds 4.0/5.0 for chatbot helpfulness (measured via post-session survey)
- **SC-010**: 90% of users can complete basic task operations (add, list, complete) via chat within first session
- **SC-011**: System handles 100 concurrent conversations without response time degradation
- **SC-012**: Zero cross-user data leakage (all operations correctly scoped to user_id)
- **SC-013**: AI summaries reduce task description display length by 60% on average while preserving meaning
- **SC-014**: Fallback mechanisms (keyword search, error apologies) activate within 1 second of primary failure

### Technical Quality Metrics

- **SC-015**: Code coverage exceeds 80% for MCP tools and agent logic
- **SC-016**: All API endpoints have OpenAPI documentation in Swagger UI
- **SC-017**: Response time p95 < 3s, p99 < 10s for chat endpoint
- **SC-018**: Zero memory leaks in long-running agent processes (verified with load testing)
- **SC-019**: Database connection pooling handles 50 concurrent DB connections
- **SC-020**: Qdrant vector search completes within 500ms for collections < 10,000 vectors

### Non-Functional Success Criteria

- **SC-NFR-001**: Data retention policies enforced (90-day conversation archive)
- **SC-NFR-002**: GDPR right to erasure functional (account deletion within 30 days)
- **SC-NFR-003**: Cost limits enforced (per-user token quotas)
- **SC-NFR-004**: Health check endpoint responds within 100ms
- **SC-NFR-005**: Daily database backups completed successfully
- **SC-NFR-006**: Frontend meets WCAG 2.1 Level AA accessibility standards

## Assumptions & Decisions

### User Choices from Clarification

| Question | Decision | Rationale |
|----------|----------|-----------|
| Streaming Responses | SSE token-by-token | Better UX for AI chatbot, expected behavior, ChatKit supports natively |
| Observability | Structured logging with correlation IDs | Essential for debugging AI behavior, tracing tool calls, understanding agent handoffs |
| Rate Limiting | Per-user: 30 requests/minute | Prevents abuse, fair access, aligns with OpenAI's per-key limits |
| Conversation Title Generation | After 3 messages | Enough context for meaningful title, minimal added cost |
| MCP Server Deployment | In-process with FastAPI | Simpler for Phase III, shared DB access, lower latency |
| AI Model | GPT-4o-mini | Best balance of cost, speed, and capability for chatbot use case |
| Embedding Model | text-embedding-3-small | Cost-effective, good performance for task semantic search |
| Vector DB | Qdrant Cloud | Free tier available, excellent performance, Python SDK |
| Speech API | OpenAI Whisper API (whisper-1) | Server-side, superior accuracy, multilingual (including Urdu), consistent across browsers at $0.006/minute |
| Conversation Retention | 90 days | Balance between user utility and storage costs |
| Max History Messages | 50 per conversation | Token limit management while maintaining context |
| Max Audio Duration | 30 seconds | Cost containment ($0.003 per transcription) while sufficient for commands |

### Additional Assumptions

- Users have browsers supporting audio recording (MediaRecorder API: Chrome, Edge, Firefox, Safari)
- OpenAI API key is configured in backend environment variables (for both GPT-4o-mini and Whisper)
- Whisper API cost: ~$0.006 per minute = $0.003 per 30-second command
- Qdrant Cloud account is set up with API key in environment
- Better Auth JWT integration from Phase II continues to work
- Task model from Phase II is extended with new fields (backward compatible)
- Frontend ChatKit domain is added to OpenAI allowlist before deployment
- Audio files are uploaded via multipart/form-data with JWT authentication
- Urdu text rendering requires RTL support in frontend CSS
- Conversation titles are auto-generated after 3 messages using GPT-4o-mini to summarize the conversation context
- MCP server runs within the FastAPI application (not separate process for Phase III)
- Whisper API automatically detects language from audio (no explicit language parameter needed)
