# Tasks: AI-Powered Todo Chatbot

**Input**: Design documents from `/specs/012-ai-chatbot-phase3/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/chat-api.yaml ✅, quickstart.md ✅

**Tests**: No explicit TDD requirement in spec. Tests are optional - focus on implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6, US7, US8)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for all backend code
- **Frontend**: `frontend/src/` for all frontend code
- **Tests**: `backend/tests/` for backend tests

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment setup

- [ ] T001 Add OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY to backend/.env with documentation
- [ ] T002 [P] Install backend Python dependencies: openai-agents-python mcp sse-starlette qdrant-client in backend/pyproject.toml
- [ ] T003 [P] Install frontend dependencies: @ai-sdk/sdk @ai-sdk/react in frontend/package.json
- [ ] T004 [P] Create backend directory structure: app/agents/, app/mcp/, app/mcp/tools/, app/chat/, app/search/, app/embeddings/, app/voice/
- [ ] T005 [P] Create frontend directory structure: src/app/chat/, src/components/chat/, src/lib/api/chat.ts, src/lib/hooks/use-chat.ts
- [ ] T006 [P] Update CLAUDE.md with Python 3.13+ requirement and Phase III context
- [ ] T007 [P] Update backend/.gitignore to exclude .env with new keys

**Checkpoint**: Environment ready, dependencies installed, directory structure created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create database migration for conversations table in backend/alembic/versions/
- [ ] T009 Create database migration for messages table in backend/alembic/versions/
- [ ] T010 Create database migration for agent_handoffs table in backend/alembic/versions/
- [ ] T011 Create database migration to extend tasks table with transcription_text, ai_summary, embedding_id in backend/alembic/versions/
- [ ] T012 [P] Create Conversation model in backend/app/models.py with UUID id, user_id, title, language_preference, message_count, created_at, updated_at
- [ ] T013 [P] Create Message model in backend/app/models.py with UUID id, conversation_id, correlation_id, role, content, tool_calls, created_at
- [ ] T014 [P] Create AgentHandoff model in backend/app/models.py with UUID id, conversation_id, from_agent, to_agent, reason, timestamp, context_snapshot
- [ ] T015 Extend Task model in backend/app/models.py with transcription_text, ai_summary, embedding_id fields
- [ ] T016 Create Qdrant 'tasks' collection with 1536-dim vectors, COSINE distance, user_id index in backend/app/search/qdrant_setup.py
- [ ] T017 [P] Create AsyncQdrantClient singleton in backend/app/search/client.py with URL and API key from env
- [ ] T018 [P] Create AsyncOpenAI client singleton in backend/app/embeddings/client.py for embeddings and GPT-4o-mini
- [ ] T019 Create AsyncOpenAI Whisper client in backend/app/voice/client.py for audio transcription
- [ ] T020 Create correlation ID middleware in backend/app/middleware/correlation.py for request tracing
- [ ] T021 Create structured logging utility in backend/app/utils/logging.py with correlation ID support
- [ ] T022 Create per-user rate limiting middleware (30 req/min) in backend/app/middleware/rate_limit.py with 429 response
- [ ] T023 [P] Create JWT authentication dependency in backend/app/api/deps.py extracting user_id from sub claim
- [ ] T024 [P] Create base MCP server scaffold using FastMCP in backend/app/mcp/server.py with streamable-http transport
- [ ] T025 Mount MCP server to FastAPI app in backend/app/main.py at /mcp route with CORS

**Checkpoint**: Database schema ready, Qdrant client configured, OpenAI clients configured, middleware deployed, MCP scaffold ready

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage todo list through natural conversation - the core value proposition

**Independent Test**: Send natural language commands to /api/chat and verify correct task operations are performed and stored in database

### Implementation for User Story 1

- [ ] T026 [P] [US1] Create add_task MCP tool in backend/app/mcp/tools/add_task.py with parameters user_id, title, description?, priority?, due_date?
- [ ] T027 [P] [US1] Create list_tasks MCP tool in backend/app/mcp/tools/list_tasks.py with parameters user_id, status?, limit?, offset?
- [ ] T028 [P] [US1] Create complete_task MCP tool in backend/app/mcp/tools/complete_task.py with parameters user_id, task_id
- [ ] T029 [P] [US1] Create delete_task MCP tool in backend/app/mcp/tools/delete_task.py with parameters user_id, task_id
- [ ] T030 [P] [US1] Create update_task MCP tool in backend/app/mcp/tools/update_task.py with parameters user_id, task_id, title?, description?, priority?, due_date?
- [ ] T031 [US1] Register all MCP tools in backend/app/mcp/server.py and validate tool schemas
- [ ] T032 [US1] Create TodoAssistant agent in backend/app/agents/todo_agent.py with GPT-4o-mini, natural language instructions, and MCP tools
- [ ] T033 [US1] Create chat service in backend/app/chat/service.py with Runner.run(), conversation persistence, and error handling
- [ ] T034 [US1] Create SSE streaming response generator in backend/app/chat/service.py yielding JSONServerSentEvent for message_start, token, message_done
- [ ] T035 [US1] Create POST /api/chat endpoint in backend/app/chat/router.py with SSE EventSourceResponse, JWT auth, rate limiting
- [ ] T036 [US1] Create conversation repository in backend/app/repositories/conversation.py for create, get, update, list
- [ ] T037 [US1] Create message repository in backend/app/repositories/message.py for create, list_by_conversation
- [ ] T038 [US1] Implement conversation auto-title generation after 3 messages using GPT-4o-mini in backend/app/chat/service.py
- [ ] T039 [US1] Create GET /api/conversations endpoint in backend/app/chat/router.py listing user's conversations
- [ ] T040 [US1] Create GET /api/conversations/{id} endpoint in backend/app/chat/router.py with messages
- [ ] T041 [US1] Create DELETE /api/conversations/{id} endpoint in backend/app/chat/router.py
- [ ] T042 [US1] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx with SSE EventSource and Deep Space theme
- [ ] T043 [US1] Create MessageList component in frontend/src/components/chat/MessageList.tsx with auto-scroll and message styling
- [ ] T044 [US1] Create MessageInput component in frontend/src/components/chat/MessageInput.tsx with send button and textarea
- [ ] T045 [US1] Create /chat route in frontend/src/app/chat/page.tsx with ChatInterface
- [ ] T046 [US1] Create chat API client in frontend/src/lib/api/chat.ts with EventSource connection and JWT token
- [ ] T047 [US1] Create useChat hook in frontend/src/lib/hooks/use-chat.ts for chat state and SSE connection management
- [ ] T048 [US1] Add error handling for unrecognized commands in backend/app/agents/todo_agent.py with clarification request
- [ ] T049 [US1] Add tool call logging in backend/app/chat/service.py for observability

**Checkpoint**: User Story 1 complete - users can chat to create, list, complete, update, delete tasks naturally

---

## Phase 4: User Story 2 - Conversational Context Memory (Priority: P2)

**Goal**: Enable multi-turn conversations with context awareness across messages

**Independent Test**: Engage in multi-turn conversation and verify AI correctly references previous messages

### Implementation for User Story 2

- [ ] T050 [P] [US2] Update conversation repository in backend/app/repositories/conversation.py to load full message history
- [ ] T051 [US2] Update chat service in backend/app/chat/service.py to load conversation history from DB before Runner.run()
- [ ] T052 [US2] Implement message context building in backend/app/chat/service.py passing last 50 messages to Runner
- [ ] T053 [US2] Update TodoAssistant agent instructions in backend/app/agents/todo_agent.py to reference conversation context
- [ ] T054 [US2] Add conversation resumption logic in backend/app/chat/service.py handling existing conversation_id
- [ ] T055 [US2] Create conversation updated_at timestamp trigger in backend/app/repositories/conversation.py on each message
- [ ] T056 [US2] Update MessageList component in frontend/src/components/chat/MessageList.tsx to load conversation history on mount

**Checkpoint**: User Story 2 complete - bot remembers context across multi-turn conversations

---

## Phase 5: User Story 3 - Semantic Task Search (Priority: P3)

**Goal**: Find tasks by meaning rather than exact keywords using vector embeddings

**Independent Test**: Create varied tasks, search with semantically related but keyword-different queries

### Implementation for User Story 3

- [ ] T057 [P] [US3] Create embedding service in backend/app/embeddings/service.py with text-embedding-3-small model
- [ ] T058 [P] [US3] Create Qdrant search service in backend/app/search/service.py with user-scoped query_points
- [ ] T059 [P] [US3] Create keyword fallback service in backend/app/search/fallback.py for Qdrant unavailability
- [ ] T060 [US3] Create semantic_search MCP tool in backend/app/mcp/tools/semantic_search.py with parameters user_id, query, limit
- [ ] T061 [US3] Register semantic_search tool in backend/app/mcp/server.py
- [ ] T062 [US3] Create task embedding generation hook in backend/app/embeddings/service.py called on task create/update
- [ ] T063 [US3] Update add_task MCP tool to trigger embedding generation in backend/app/mcp/tools/add_task.py
- [ ] T064 [US3] Update update_task MCP tool to regenerate embedding in backend/app/mcp/tools/update_task.py
- [ ] T065 [US3] Implement Qdrant circuit breaker in backend/app/search/service.py with fallback to keyword search
- [ ] T066 [US3] Update TodoAssistant agent in backend/app/agents/todo_agent.py to use semantic_search for "find" queries
- [ ] T067 [US3] Add Qdrant error logging with graceful degradation in backend/app/search/service.py

**Checkpoint**: User Story 3 complete - users can search tasks by meaning with fallback

---

## Phase 6: User Story 4 - Multi-Language Urdu Support (Priority: P4 - Bonus +100)

**Goal**: Enable Urdu language support for task management

**Independent Test**: Send commands in Urdu script and verify correct operations with Urdu responses

### Implementation for User Story 4

- [ ] T068 [P] [US4] Add language_preference field to Conversation model in backend/app/models.py (already created, validate)
- [ ] T069 [P] [US4] Create language detection utility in backend/app/utils/language.py detecting English vs Urdu from text
- [ ] T070 [US4] Update TodoAssistant agent instructions in backend/app/agents/todo_agent.py for Urdu command recognition
- [ ] T071 [US4] Update TodoAssistant agent instructions in backend/app/agents/todo_agent.py to respond in detected language
- [ ] T072 [US4] Add Urdu task management command patterns in backend/app/agents/todo_agent.py ("شامل کرو", "دکھاؤ", "مکمل")
- [ ] T073 [US4] Add code-switching handling in backend/app/agents/todo_agent.py for mixed English-Urdu
- [ ] T074 [US4] Update chat service in backend/app/chat/service.py to store detected language preference
- [ ] T075 [US4] Add UTF-8 validation for Urdu text storage in backend/app/models.py
- [ ] T076 [US4] Create RTL CSS utility in frontend/src/app/globals.css for Urdu text rendering
- [ ] T077 [US4] Update MessageList component in frontend/src/components/chat/MessageList.tsx with RTL support for Urdu
- [ ] T078 [US4] Update MessageInput component in frontend/src/components/chat/MessageInput.tsx with RTL for Urdu
- [ ] T079 [US4] Add language preference toggle to ChatInterface in frontend/src/components/chat/ChatInterface.tsx

**Checkpoint**: User Story 4 complete - Urdu language support with +100 bonus points achievable

---

## Phase 7: User Story 5 - Voice Command Input (Priority: P5 - Bonus +200)

**Goal**: Enable hands-free task management via voice commands with Whisper API

**Independent Test**: Record voice commands, verify Whisper transcription and task creation

### Implementation for User Story 5

- [ ] T080 [P] [US5] Create POST /api/chat/transcribe endpoint in backend/app/voice/router.py with multipart/form-data
- [ ] T081 [P] [US5] Implement Whisper API transcription in backend/app/voice/service.py with auto language detection
- [ ] T082 [US5] Add audio file validation in backend/app/voice/service.py (25MB max, supported formats)
- [ ] T083 [US5] Store transcription in task.transcription_text field in backend/app/mcp/tools/add_task.py
- [ ] T084 [US5] Create Whisper error handling in backend/app/voice/service.py with user-friendly messages
- [ ] T085 [US5] Mount voice router to FastAPI app in backend/app/main.py at /api/chat/transcribe
- [ ] T086 [US5] Create VoiceRecorder component in frontend/src/components/chat/VoiceRecorder.tsx with MediaRecorder
- [ ] T087 [US5] Add 30-second recording limit in frontend/src/components/chat/VoiceRecorder.tsx with countdown timer
- [ ] T088 [US5] Add recording visual feedback in frontend/src/components/chat/VoiceRecorder.tsx (pulse animation)
- [ ] T089 [US5] Add audio upload progress indicator in frontend/src/components/chat/VoiceRecorder.tsx
- [ ] T090 [US5] Integrate transcription endpoint in frontend/src/lib/api/chat.ts with audio upload
- [ ] T091 [US5] Add microphone button to MessageInput in frontend/src/components/chat/MessageInput.tsx
- [ ] T092 [US5] Add confirmation prompt for ambiguous transcriptions in backend/app/voice/service.py

**Checkpoint**: User Story 5 complete - Voice commands with +200 bonus points achievable

---

## Phase 8: User Story 6 - AI Task Summarization (Priority: P6)

**Goal**: Auto-generate concise summaries for long task descriptions

**Independent Test**: Create tasks with long descriptions and verify AI summaries generated

### Implementation for User Story 6

- [ ] T093 [P] [US6] Create summarization service in backend/app/services/summarization.py using GPT-4o-mini
- [ ] T094 [US6] Add summary generation trigger in backend/app/mcp/tools/add_task.py for descriptions > 100 chars
- [ ] T095 [US6] Add summary regeneration in backend/app/mcp/tools/update_task.py when description changes
- [ ] T096 [US6] Implement 100 character summary limit in backend/app/services/summarization.py
- [ ] T097 [US6] Add short description bypass in backend/app/services/summarization.py (< 50 chars)
- [ ] T098 [US6] Add summarization error handling in backend/app/services/summarization.py with fallback
- [ ] T099 [US6] Update Task component in frontend/src/components/tasks/TaskCard.tsx to display ai_summary instead of full description

**Checkpoint**: User Story 6 complete - AI summaries improve task readability

---

## Phase 9: User Story 7 - MCP Tool Integration (Priority: P7)

**Goal**: Complete MCP tool integration with stateless architecture

**Independent Test**: Invoke MCP tools directly and verify database operations

### Implementation for User Story 7

- [ ] T100 [P] [US7] Add user ownership validation to all MCP tools in backend/app/mcp/tools/ (404 not 403)
- [ ] T101 [P] [US7] Add structured error responses to all MCP tools in backend/app/mcp/tools/ with status, data/error, message
- [ ] T102 [US7] Validate stateless architecture in backend/app/mcp/tools/ - no in-memory state between calls
- [ ] T103 [US7] Add tool timeout handling in backend/app/mcp/server.py with 30-second limit
- [ ] T104 [US7] Add tool call logging in backend/app/mcp/server.py with parameters, results, timing
- [ ] T105 [US7] Create MCP tool integration tests in backend/tests/test_mcp/ verifying all tools independently

**Checkpoint**: User Story 7 complete - MCP tools are stateless, validated, and logged

---

## Phase 10: User Story 8 - Agent Handoffs and Specialization (Priority: P8 - Bonus +200)

**Goal**: Implement multi-agent architecture with specialized agents

**Independent Test**: Send requests triggering different agents and verify handoffs

### Implementation for User Story 8

- [ ] T106 [P] [US8] Create PlanningAgent in backend/app/agents/planning_agent.py with weekly planning instructions
- [ ] T107 [P] [US8] Create TaskQueryAgent in backend/app/agents/query_agent.py with search optimization instructions
- [ ] T108 [US8] Add handoff configurations to TodoAssistant in backend/app/agents/todo_agent.py with handoffs parameter
- [ ] T109 [US8] Create agent handoff tracking in backend/app/chat/service.py logging from_agent, to_agent, reason
- [ ] T110 [US8] Store AgentHandoff records in backend/app/chat/service.py on each handoff
- [ ] T111 [US8] Implement context preservation in backend/app/chat/service.py passing conversation history to new agent
- [ ] T112 [US8] Add handoff error handling in backend/app/chat/service.py with graceful fallback to main agent
- [ ] T113 [US8] Update agent instructions for handoff transparency in backend/app/agents/todo_agent.py, planning_agent.py, query_agent.py

**Checkpoint**: User Story 8 complete - Agent handoffs with +200 bonus points achievable

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T114 [P] Add typing indicators to ChatInterface in frontend/src/components/chat/TypingIndicator.tsx
- [ ] T115 [P] Create TaskCard component for chat in frontend/src/components/chat/TaskCard.tsx with quick actions
- [ ] T116 [P] Add task card rendering to chat in frontend/src/components/chat/MessageList.tsx for AI-created tasks
- [ ] T117 [P] Add quick actions to chat TaskCard in frontend/src/components/chat/TaskCard.tsx (complete, delete, edit)
- [ ] T118 Add conversation pagination to MessageList in frontend/src/components/chat/MessageList.tsx for long histories
- [ ] T119 Add message limit enforcement (50 messages) in backend/app/chat/service.py
- [ ] T120 Add conversation archive job (90 days) in backend/app/services/archive.py
- [ ] T121 [P] Add OpenAPI documentation for chat endpoints in backend/app/chat/router.py
- [ ] T122 [P] Add OpenAPI documentation for voice endpoints in backend/app/voice/router.py
- [ ] T123 Add correlation ID to all log entries in backend/app/utils/logging.py
- [ ] T124 Add OpenAI API circuit breaker in backend/app/services/openai_circuit.py
- [ ] T125 Add concurrent message queuing in backend/app/chat/service.py per conversation
- [ ] T126 Add prompt injection sanitization in backend/app/chat/service.py
- [ ] T127 Update quickstart.md with final setup instructions
- [ ] T128 Run database migrations and validate schema
- [ ] T129 Verify Qdrant collection creation and payload indexes
- [ ] T130 Test all user scenarios from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Setup (Phase 1)
    │
    ▼
Foundational (Phase 2) ── BLOCKS ALL USER STORIES
    │
    ├─────────────────────────────────────────────────────┐
    │                                                     │
    ▼                                                     ▼
User Stories 3-10 (Can proceed in parallel if staffed)   │
    │                                                     │
    └─────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
                                               Polish (Phase 11)
```

### User Story Dependencies

| User Story | Can Start After | Dependencies |
|------------|-----------------|--------------|
| US1 (P1) Natural Language Tasks | Phase 2 Complete | None - Core story |
| US2 (P2) Context Memory | Phase 2 Complete | Extends US1 but independently testable |
| US3 (P3) Semantic Search | Phase 2 Complete | None - Independent feature |
| US4 (P4) Urdu Support | Phase 2 Complete | None - Language layer |
| US5 (P5) Voice Commands | Phase 2 Complete | None - Input method |
| US6 (P6) AI Summarization | Phase 2 Complete | Extends tasks from US1 |
| US7 (P7) MCP Integration | Phase 2 Complete | Tools created in US1 |
| US8 (P8) Agent Handoffs | Phase 2 Complete | Extends agents from US1 |

**Key Insight**: All user stories can start after Foundational phase. Most are independent and can be worked in parallel.

### Within Each User Story

1. **Parallel tasks marked [P]** can run simultaneously
2. **Non-parallel tasks** must complete in order
3. **Models before services before endpoints**
4. **Backend before frontend** for most stories

---

## Parallel Opportunities

### Setup (Phase 1) - All Parallel
```bash
T002, T003, T004, T005, T006, T007  # Can all run together
```

### Foundational (Phase 2) - Significant Parallelism
```bash
# Migration scripts (sequential due to alembic):
T008, T009, T010, T011

# Models (parallel):
T012, T013, T014, T015

# Clients (parallel):
T017, T018, T019

# Middleware (parallel):
T020, T021, T022, T023, T024
```

### User Story 1 (Phase 3) - MCP Tools Parallel
```bash
# All MCP tools (parallel):
T026, T027, T028, T029, T030

# Frontend components (parallel):
T042, T043, T044
```

### User Story 8 (Phase 10) - Agents Parallel
```bash
# Agent creation (parallel):
T106, T107
```

### Cross-Story Parallelism
Once Foundational phase completes, different team members can work on different user stories simultaneously:
- Developer A: US1 (Natural Language)
- Developer B: US3 (Semantic Search)
- Developer C: US4 (Urdu Support)
- Developer D: US5 (Voice Commands)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**For rapid delivery, implement only User Story 1:**

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T025) - CRITICAL
3. Complete Phase 3: User Story 1 (T026-T049)
4. **STOP and VALIDATE**: Test natural language task management
5. Deploy/demo if ready

**MVP delivers**:
- Chat interface with SSE streaming
- Natural language task creation, listing, completion, updates, deletion
- Conversation management
- Multi-turn context awareness

### Incremental Delivery (Recommended)

**Add stories one at a time for continuous value:**

1. Foundation → US1 → **MVP Deploy** (Core chatbot)
2. Add US3 (Semantic Search) → **Deploy** (Better discovery)
3. Add US4 (Urdu Support) → **Deploy** (+100 bonus points!)
4. Add US5 (Voice Commands) → **Deploy** (+200 bonus points!)
5. Add US8 (Agent Handoffs) → **Deploy** (+200 bonus points!)
6. Total: +500 bonus points achievable

### Parallel Team Strategy

**With multiple developers after Foundational phase:**

```
                   Foundational Complete (T008-T025)
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
   Developer A                 Developer B                 Developer C
   US1 (T026-T049)            US3 (T057-T067)            US4 (T068-T079)
   + US2 (T050-T056)          + US6 (T093-T099)           + US5 (T080-T092)
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
                          Developer D (US7, US8)
                          T100-T113
                                    │
                                    ▼
                            Polish (T114-T130)
```

---

## Summary

### Task Count by Phase

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1: Setup | 7 | Environment, dependencies, structure |
| Phase 2: Foundational | 18 | Database, clients, middleware, MCP |
| Phase 3: US1 | 24 | Natural language task management |
| Phase 4: US2 | 7 | Context memory |
| Phase 5: US3 | 11 | Semantic search |
| Phase 6: US4 | 12 | Urdu support (+100 bonus) |
| Phase 7: US5 | 13 | Voice commands (+200 bonus) |
| Phase 8: US6 | 7 | AI summarization |
| Phase 9: US7 | 6 | MCP integration |
| Phase 10: US8 | 8 | Agent handoffs (+200 bonus) |
| Phase 11: Polish | 17 | Cross-cutting concerns |
| **TOTAL** | **130** | All tasks |

### Task Count by User Story

| User Story | Priority | Tasks | Bonus |
|------------|----------|-------|-------|
| US1: Natural Language Tasks | P1 | 24 | - |
| US2: Context Memory | P2 | 7 | - |
| US3: Semantic Search | P3 | 11 | - |
| US4: Urdu Support | P4 | 12 | +100 |
| US5: Voice Commands | P5 | 13 | +200 |
| US6: AI Summarization | P6 | 7 | - |
| US7: MCP Integration | P7 | 6 | - |
| US8: Agent Handoffs | P8 | 8 | +200 |
| **BONUS TOTAL** | | | **+500** |

### Parallel Execution Opportunities

- **Setup phase**: 6 of 7 tasks can run in parallel
- **Foundational phase**: ~60% can run in parallel
- **User Story phases**: ~40% can run in parallel within stories
- **Cross-story**: All 8 user stories can proceed in parallel after Foundational

### Format Validation

All 130 tasks follow the strict checklist format:
- ✅ Checkbox prefix: `- [ ]`
- ✅ Task ID: Sequential T001-T130
- ✅ [P] marker: Applied to parallelizable tasks
- ✅ [Story] label: Applied to all user story tasks
- ✅ File paths: Included in all implementation tasks

---

*Tasks Complete: Ready for implementation with MVP-first approach*
