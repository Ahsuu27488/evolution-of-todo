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

- What happens when a user sends a command the AI doesn't understand? (AI asks for clarification with example commands)
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
- **FR-016**: AI MUST extract task priorities from natural language ("urgent", "important", "high priority")
- **FR-017**: AI MUST extract due dates from natural language ("tomorrow", "next week", "Friday at 3pm")
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
- **FR-042**: AI MUST detect language from user message (English vs Urdu)
- **FR-043**: System MUST respond in the same language as user input
- **FR-044**: System MUST support task titles in Urdu characters
- **FR-045**: System MUST support mixed English-Urdu (code-switching)
- **FR-046**: AI MUST understand Urdu task management commands ("شامل کرو" for add, "دکھاؤ" for show)
- **FR-047**: System MUST store Urdu text correctly in PostgreSQL (UTF-8)
- **FR-048**: System MUST render Urdu text right-to-left in UI
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
- **FR-071**: System MUST implement PlanningAgent for weekly planning and prioritization
- **FR-072**: System MUST implement TaskQueryAgent for complex task searches and filtering
- **FR-073**: System MUST implement handoff mechanism between agents
- **FR-074**: Handoffs MUST preserve full conversation context
- **FR-075**: Specialized agents MUST return to main agent after completing specialized task
- **FR-076**: Agent handoffs MUST be transparent to user (seamless experience)
- **FR-077**: Each agent MUST have specialized instructions for its domain

#### ChatKit Frontend Integration

- **FR-078**: Frontend MUST use OpenAI ChatKit for chat UI
- **FR-079**: Chat interface MUST match Deep Space theme (glassmorphism, cyan accents)
- **FR-080**: Chat MUST display user messages and AI responses with different styling
- **FR-081**: Chat MUST show typing indicator only until first token arrives, then display streaming tokens in real-time
- **FR-082**: Chat MUST auto-scroll to latest message
- **FR-083**: Chat MUST support message history loading (pagination for long conversations)
- **FR-084**: System MUST render task cards in chat when AI creates/displays tasks
- **FR-085**: System MUST support quick actions on chat task cards (complete, delete, edit)
- **FR-086**: Chat MUST be accessible from /chat route and as a floating widget

#### Error Handling and Edge Cases

- **FR-087**: System MUST return 401 for requests without valid JWT
- **FR-088**: System MUST implement per-user rate limiting at 30 requests/minute, return 429 with retry-after header when exceeded
- **FR-089**: System MUST implement structured logging with correlation IDs for all requests
- **FR-090**: System MUST log all AI agent tool calls with parameters, results, and timing
- **FR-091**: System MUST log agent handoff events with from_agent, to_agent, and context snapshot
- **FR-092**: System MUST handle OpenAI API outages gracefully (cached responses or apology)
- **FR-093**: System MUST sanitize user input to prevent prompt injection
- **FR-094**: System MUST limit conversation history to last 50 messages per conversation
- **FR-095**: System MUST archive conversations older than 90 days
- **FR-096**: System MUST handle concurrent message processing (queue per conversation)
- **FR-097**: System MUST timeout AI agent calls after 30 seconds
- **FR-098**: System MUST implement circuit breaker for failing external APIs

### Key Entities

- **Conversation**: Represents a chat session with id, user_id, title (auto-generated after 3 messages via GPT-4o-mini summary, or user-set), language_preference (en/ur/auto), created_at, updated_at, message_count

- **Message**: Represents a single message with id, conversation_id, correlation_id (for tracing), role (user/assistant/system), content, tool_calls (JSON array of tools invoked), created_at

- **Task**: Extended from Phase II with new fields - transcription_text (full voice transcription), ai_summary (LLM-generated summary), embedding_id (Qdrant vector reference)

- **AgentHandoff**: Represents agent handoff events with id, conversation_id, from_agent, to_agent, reason, timestamp, context_snapshot

- **ConversationPreference**: User's chat settings with id, user_id, language (en/ur/auto), voice_enabled (bool), response_format (text/voice), notifications_enabled

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Chat endpoint responds within 3 seconds for 95% of requests
- **SC-002**: AI correctly identifies user intent (create/list/complete/delete/update) in 90% of natural language requests
- **SC-003**: Semantic search returns relevant results for 85% of conceptual queries
- **SC-004**: Urdu language support achieves 80% intent recognition accuracy
- **SC-005**: Voice transcription achieves 75% accuracy for clear English speech, 60% for Urdu
- **SC-006**: Agent handoffs complete successfully in 95% of cases without user confusion
- **SC-007**: MCP tools handle 10,000 calls per hour without degradation
- **SC-008**: Conversation history persists correctly across server restarts (100% data integrity)
- **SC-009**: User satisfaction score exceeds 4.0/5.0 for chatbot helpfulness
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
