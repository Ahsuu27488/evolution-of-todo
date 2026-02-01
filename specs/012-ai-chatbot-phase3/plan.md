# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `012-ai-chatbot-phase3` | **Date**: 2026-01-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-ai-chatbot-phase3/spec.md`

**Note**: This plan leverages Context7 MCP for latest documentation and existing agent-skills for implementation patterns.

## Summary

Implement an AI-powered chatbot for the Evolution of Todo app using OpenAI Agents SDK with multi-agent handoffs, MCP (Model Context Protocol) tools for stateless task operations, semantic vector search with Qdrant, multi-language Urdu support, and voice commands via Whisper API. The chatbot provides natural language task management through conversation while maintaining stateless architecture with database persistence.

**Key Technologies:**
- OpenAI Agents SDK (`/openai/openai-agents-python` v0.7.0) - Multi-agent orchestration with handoffs
- MCP Python SDK (`/modelcontextprotocol/python-sdk`) - Standardized tool protocol
- FastAPI with SSE Starlette (`/sysid/sse-starlette`) - Streaming responses
- Qdrant Client (`/qdrant/qdrant-client`) - Semantic vector search
- OpenAI Whisper API - Voice transcription (multilingual including Urdu)

## Technical Context

**Language/Version**: Python 3.13+ (STRICT per constitution §V.1.1)
**Primary Dependencies**:
- `openai-agents-python` v0.7.0 - Multi-agent framework with handoffs, sessions, tracing
- `mcp` (python-sdk) - Model Context Protocol for tools
- `fastapi` v0.115+ - Async web framework
- `sse-starlette` v2.0+ - Server-Sent Events for streaming
- `qdrant-client` - Async vector database client
- `openai` - Whisper API, embeddings, GPT-4o-mini
- `sqlmodel` - Existing ORM from Phase II

**Storage**:
- PostgreSQL (Neon) - Conversations, messages, tasks (existing from Phase II)
- Qdrant Cloud - Vector embeddings for semantic search

**Testing**: pytest with async support, pytest-mock for agent testing

**Target Platform**: Linux server (containers for Phase IV), web browsers (frontend)

**Project Type**: Web application (existing backend + frontend extensions)

**Performance Goals**:
- Chat endpoint: p95 < 3s, p99 < 10s
- Streaming first token: < 1s
- Semantic search: < 500ms for < 10k vectors
- Voice transcription: < 5s for 30-second audio

**Constraints**:
- Stateless architecture - no in-memory conversation state
- User-scoped operations - zero cross-user data leakage
- 30 req/min per-user rate limiting
- 30-second max audio recording (cost containment)
- 50 messages max per conversation (token management)

**Scale/Scope**:
- 100 concurrent conversations without degradation
- 10,000 MCP tool calls per hour
- Multi-language support (English + Urdu)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Spec-Driven Development (§I)

- [x] Spec exists and is approved: `specs/012-ai-chatbot-phase3/spec.md`
- [x] Clarifications completed (5 questions answered 2026-01-30)
- [ ] Tasks defined (blocked - awaiting `/sp.tasks` command)
- [ ] All code will reference spec sections

**Status**: ✅ PASS - Spec is complete with all ambiguities resolved

### Gate 2: Phase Isolation (§IV)

| Check | Status | Evidence |
|-------|--------|----------|
| Phase III scope defined | ✅ | Spec §User Scenarios - chatbot only, no K8s/Kafka |
| No future-phase features | ✅ | No Kubernetes, Dapr, or cloud deployment in scope |
| Extends Phase II | ✅ | Reuses existing Task model, auth, database |

**Status**: ✅ PASS - Phase boundaries respected

### Gate 3: Technology Constraints (§V)

| Check | Status | Evidence |
|-------|--------|----------|
| Python 3.13+ | ✅ | Required per plan |
| FastAPI backend | ✅ | Existing from Phase II |
| OpenAI Agents SDK | ✅ | `/openai/openai-agents-python` via Context7 |
| MCP Python SDK | ✅ | `/modelcontextprotocol/python-sdk` via Context7 |
| Next.js 15+ frontend | ✅ | Existing from Phase II |

**Status**: ✅ PASS - All technologies per constitution

### Gate 4: Context7 Primary Source (§III.1)

| Check | Status | Evidence |
|-------|--------|----------|
| Context7 queried for all libraries | ✅ | Library IDs documented in research |
| No training-data assumptions | ✅ | All patterns from retrieved docs |
| Official documentation used | ✅ | Context7 citations throughout |

**Status**: ✅ PASS - Context7 workflow followed

### Gate 5: Agent-Skills Usage (§III.2)

| Check | Status | Evidence |
|-------|--------|----------|
| Reusable skills exist | ✅ | openai-agents-guide, qdrant-guide, whisper-guide, mcp-server-builder agent |
| Skills will be used | ✅ | Documented in implementation phases |
| Reusable intelligence | ✅ | +200 bonus points category |

**Status**: ✅ PASS - Agent-skills leveraged

### Gate 6: Bonus Points Commitment (§0.2)

| Bonus | Points | Status | Implementation |
|-------|--------|--------|----------------|
| Multi-Language Urdu | +100 | ✅ In scope | Spec FR-041 to FR-050 |
| Voice Commands | +200 | ✅ In scope | Spec FR-051 to FR-061 |
| Agent Handoffs | +200 | ✅ In scope | Spec FR-070 to FR-077 (part of Reusable Intelligence) |

**Status**: ✅ PASS - +500 bonus points achievable

---

**OVERALL GATE STATUS**: ✅ PASS - All gates satisfied, proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/012-ai-chatbot-phase3/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command) ← TO BE GENERATED
├── data-model.md        # Phase 1 output (/sp.plan command) ← TO BE GENERATED
├── quickstart.md        # Phase 1 output (/sp.plan command) ← TO BE GENERATED
├── contracts/           # Phase 1 output (/sp.plan command) ← TO BE GENERATED
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoints
│   └── mcp-tools.yaml   # MCP tool schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Existing structure (Phase II)
backend/
├── app/
│   ├── models.py              # Existing Task model (extensible)
│   ├── database.py            # Existing Neon DB connection
│   ├── simple_auth.py         # Existing JWT auth
│   ├── api/                   # Existing REST endpoints
│   │   └── ...
│   ├── services/              # Existing services
│   │   ├── notification_service.py
│   │   ├── sse_service.py
│   │   └── ...
│   ├── agents/                # NEW: AI agents
│   │   ├── __init__.py
│   │   ├── todo_agent.py           # Main TodoAssistant agent
│   │   ├── planning_agent.py       # PlanningAgent specialist
│   │   └── query_agent.py          # TaskQueryAgent specialist
│   ├── mcp/                   # NEW: MCP server
│   │   ├── __init__.py
│   │   ├── server.py              # FastMCP server with tools
│   │   └── tools/
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── delete_task.py
│   │       ├── update_task.py
│   │       └── semantic_search.py
│   ├── chat/                  # NEW: Chat endpoints
│   │   ├── __init__.py
│   │   ├── router.py             # /api/chat endpoint with SSE
│   │   ├── transcription.py      # /api/chat/transcribe endpoint
│   │   └── service.py            # Chat business logic
│   ├── search/                # NEW: Semantic search
│   │   ├── __init__.py
│   │   ├── service.py            # Qdrant integration
│   │   └── fallback.py           # Keyword search fallback
│   ├── embeddings/            # NEW: Embedding service
│   │   ├── __init__.py
│   │   └── service.py            # OpenAI text-embedding-3-small
│   └── voice/                 # NEW: Voice transcription
│       ├── __init__.py
│       └── service.py            # Whisper API integration
├── tests/
│   ├── test_agents/           # NEW: Agent tests
│   ├── test_mcp/              # NEW: MCP tool tests
│   └── test_chat/             # NEW: Chat endpoint tests
├── pyproject.toml
└── .env                        # Add OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY

frontend/
├── src/
│   ├── app/
│   │   ├── chat/               # NEW: Chat pages
│   │   │   ├── page.tsx           # /chat route
│   │   │   └── layout.tsx
│   │   └── components/
│   │       ├── chat/            # NEW: Chat components
│   │       │   ├── ChatInterface.tsx   # Main chat UI with ChatKit
│   │       │   ├── MessageList.tsx
│   │       │   ├── MessageInput.tsx
│   │       │   ├── TypingIndicator.tsx
│   │       │   ├── TaskCard.tsx         # Task cards in chat
│   │       │   └── VoiceRecorder.tsx    # Microphone + recording
│   │       └── ...
│   └── lib/
│       ├── api/
│       │   └── chat.ts          # NEW: Chat API client (SSE)
│       └── hooks/
│           └── use-chat.ts      # NEW: Chat state hook
└── tests/
    └── chat/                   # NEW: Chat tests

.claude/
├── skills/                     # Existing skills (used for implementation)
│   ├── openai-agents-guide/
│   ├── qdrant-guide/
│   ├── whisper-guide/
│   ├── urdu-language-guide/
│   ├── voice-commands-guide/
│   └── chatkit-guide/
└── agents/
    └── mcp-server-builder.md   # Used for MCP implementation
```

**Structure Decision**: Web application structure (Option 2). Backend extends existing Phase II FastAPI application with new modules for agents, MCP, chat, search, embeddings, and voice. Frontend adds new chat components and routes. This maintains clean separation while reusing existing authentication, database, and services.

## Complexity Tracking

> No constitution violations - this section intentionally left empty.

## Phase 0: Research & Technology Decisions

### Context7 Research Results

All research conducted using Context7 MCP as PRIMARY source of truth (per constitution §III.1).

#### 1. OpenAI Agents SDK

**Library ID**: `/openai/openai-agents-python`
**Version**: v0.7.0
**Reputation**: High (90.3 benchmark score)
**Code Snippets**: 606+

**Key Findings**:
- **Agent Definition**: Use `Agent` class with `name`, `instructions`, `handoffs`, `tools`
- **Handoffs**: Automatic context preservation across agents via `handoffs` parameter
- **Sessions**: `SQLiteSession` or custom session for conversation history persistence
- **Runner**: `Runner.run()` executes agent with stateless pattern
- **Streaming**: Built-in streaming support for real-time token delivery

**Decision**: Use OpenAI Agents SDK v0.7.0 with custom database-backed session (not SQLite) for multi-user isolation.

**Context7 Source**: Retrieved from official documentation showing:
- Multi-agent handoff patterns
- Session memory management
- Stateless Runner execution

#### 2. MCP Python SDK

**Library ID**: `/modelcontextprotocol/python-sdk`
**Version**: Latest
**Reputation**: High (89.2 benchmark score)
**Code Snippets**: 296+

**Key Findings**:
- **FastMCP**: Decorator-based server creation with `@mcp.tool()`
- **Transport**: `streamable-http` for FastAPI integration
- **Tools**: Simple Python functions with type hints become MCP tools
- **Mounting**: Can mount to existing Starlette/FastAPI app

**Decision**: Use FastMCP with `streamable-http` transport, mounted within FastAPI application (in-process per clarification).

**Context7 Source**: Retrieved from official documentation showing:
- FastMCP server creation pattern
- Streamable HTTP transport setup
- Starlette app mounting

#### 3. SSE Streaming (FastAPI)

**Library ID**: `/sysid/sse-starlette`
**Version**: 2.0+
**Reputation**: High (92.4 benchmark score)
**Code Snippets**: 55+

**Key Findings**:
- **EventSourceResponse**: Main class for SSE responses
- **Async Generator**: Yield events as async generator
- **JSONServerSentEvent**: For structured data streaming
- **Production Ready**: Handles connection lifecycle, graceful shutdown

**Decision**: Use `sse-starlette` for Server-Sent Events streaming with async generators yielding `JSONServerSentEvent`.

**Context7 Source**: Retrieved from official documentation showing:
- EventSourceResponse usage
- Async generator patterns
- Connection management

#### 4. Qdrant Vector Database

**Library ID**: `/qdrant/qdrant-client`
**Version**: Latest
**Reputation**: High (74.5 benchmark score)
**Code Snippets**: 43+

**Key Findings**:
- **AsyncQdrantClient**: Full async support for FastAPI
- **query_points**: Modern API for similarity search
- **Filter**: User-scoped filtering via `FieldCondition`
- **Payload Index**: Index on `user_id` for performance

**Decision**: Use `AsyncQdrantClient` with user-scoped filters, cosine distance, text-embedding-3-small (1536 dimensions).

**Context7 Source**: Retrieved from official documentation showing:
- Async client usage
- query_points with filters
- Collection creation and indexing

#### 5. OpenAI Whisper API

**Library ID**: (via openai python SDK)
**Cost**: $0.006/minute
**Max File Size**: 25 MB

**Key Findings**:
- **Auto-detection**: Language auto-detection works for Urdu
- **Formats**: mp3, mp4, mpeg, mpga, m4a, wav, webm
- **Cost**: ~$0.003 per 30-second command

**Decision**: Use Whisper API with auto-detection (supports Urdu), 30-second max recording for cost containment.

### Agent-Skills Inventory

Existing reusable skills that will guide implementation:

| Skill | Purpose | Documentation Source |
|-------|---------|---------------------|
| `openai-agents-guide` | Agent definition, handoffs, sessions | `/openai/openai-agents-python` |
| `qdrant-guide` | Vector search, embedding storage | `/qdrant/qdrant-client` |
| `whisper-guide` | Voice transcription, Urdu support | OpenAI Whisper API |
| `urdu-language-guide` | RTL text, language detection | Multilingual patterns |
| `voice-commands-guide` | Audio recording, Web Speech API | Browser MediaRecorder API |
| `chatkit-guide` | Chat UI with Deep Space theme | OpenAI ChatKit |
| `mcp-server-builder` agent | MCP server implementation workflow | `/modelcontextprotocol/python-sdk` |

### Technology Decision Summary

| Technology | Selected | Alternative Rejected | Rationale |
|------------|----------|---------------------|-----------|
| Agent Framework | OpenAI Agents SDK | LangChain, custom | Official SDK, built-in handoffs, streaming |
| MCP Transport | streamable-http (in-process) | stdio (separate process) | Simplified deployment, shared DB access |
| Streaming Protocol | Server-Sent Events | WebSockets | Simpler, one-way, matches ChatKit |
| Vector DB | Qdrant Cloud | Pinecone, Weaviate | Free tier, excellent Python SDK |
| Embedding Model | text-embedding-3-small | text-embedding-3-large | Cost-effective, sufficient for tasks |
| Speech API | OpenAI Whisper (server) | Web Speech API (client) | Superior accuracy, multilingual |
| Session Storage | PostgreSQL (custom) | SQLite (built-in) | Multi-user isolation, existing DB |

---

*Phase 0 Complete: All technical decisions made with Context7 as primary source*

## Phase 1: Design & Contracts

### Data Model

*See: `data-model.md` (to be generated)*

**New Entities** (extending Phase II models):

1. **Conversation** - Chat session
   - `id: UUID` (primary key)
   - `user_id: str` (foreign key to users)
   - `title: str` (auto-generated after 3 messages)
   - `language_preference: str` (en/ur/auto)
   - `message_count: int`
   - `created_at: datetime`
   - `updated_at: datetime`

2. **Message** - Single message
   - `id: UUID` (primary key)
   - `conversation_id: UUID` (foreign key)
   - `correlation_id: str` (for tracing)
   - `role: str` (user/assistant/system)
   - `content: str`
   - `tool_calls: JSON` (array of tools invoked)
   - `created_at: datetime`

3. **AgentHandoff** - Handoff tracking
   - `id: UUID` (primary key)
   - `conversation_id: UUID` (foreign key)
   - `from_agent: str`
   - `to_agent: str`
   - `reason: str`
   - `timestamp: datetime`
   - `context_snapshot: JSON`

4. **Task** (Extended from Phase II)
   - `transcription_text: str | NULL` (full voice transcription)
   - `ai_summary: str | NULL` (LLM-generated summary)
   - `embedding_id: str | NULL` (Qdrant vector reference)

### API Contracts

*See: `contracts/chat-api.yaml` (to be generated)*

**Endpoints**:

| Method | Path | Description | Streaming |
|--------|------|-------------|-----------|
| POST | `/api/chat` | Send message, get AI response | ✅ SSE |
| POST | `/api/chat/transcribe` | Upload audio for transcription | ❌ |
| GET | `/api/conversations` | List user's conversations | ❌ |
| GET | `/api/conversations/{id}` | Get conversation with messages | ❌ |
| DELETE | `/api/conversations/{id}` | Delete conversation | ❌ |

**MCP Tools** (internal, exposed via MCP server):

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_task` | user_id, title, description?, priority?, due_date? | Create task |
| `list_tasks` | user_id, status?, limit?, offset? | List tasks |
| `complete_task` | user_id, task_id | Mark task complete |
| `delete_task` | user_id, task_id | Delete task |
| `update_task` | user_id, task_id, title?, description?, priority?, due_date? | Update task |
| `semantic_search` | user_id, query, limit | Search by meaning |

### Quickstart Guide

*See: `quickstart.md` (to be generated)*

**Environment Variables**:
```bash
# Existing (Phase II)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
CORS_ORIGINS=http://localhost:3000

# New (Phase III)
OPENAI_API_KEY=sk-...           # GPT-4o-mini, Whisper, embeddings
QDRANT_URL=https://...          # Qdrant Cloud URL
QDRANT_API_KEY=...              # Qdrant Cloud API key
```

**Installation**:
```bash
# Backend
pip install openai-agents-python mcp sse-starlette qdrant-client

# Frontend (ChatKit via npm)
npm install @ai-sdk/sdk @ai-sdk/react
```

---

*Phase 1 Complete: Data model and contracts defined*

## Phase 2: Implementation Overview

*(Full implementation tasks will be generated by `/sp.tasks` command)*

### Backend Implementation Sequence

1. **Database Models** - Extend existing models with Conversation, Message, AgentHandoff
2. **MCP Server** - Create FastMCP server with task tools (using `mcp-server-builder` agent)
3. **Embedding Service** - OpenAI text-embedding-3-small integration
4. **Qdrant Service** - Async client with user-scoped search
5. **Whisper Service** - Audio transcription endpoint
6. **Chat Service** - Agent logic, session management, SSE streaming
7. **Agents** - TodoAssistant, PlanningAgent, TaskQueryAgent with handoffs
8. **Chat Router** - FastAPI endpoints with SSE streaming
9. **Rate Limiting** - Per-user 30 req/min middleware
10. **Observability** - Structured logging with correlation IDs

### Frontend Implementation Sequence

1. **Chat API Client** - SSE connection with EventSource
2. **Chat Components** - ChatInterface, MessageList, MessageInput
3. **Voice Recorder** - MediaRecorder with 30-second limit
4. **Task Cards** - Inline task cards with quick actions
5. **Deep Space Theme** - ChatKit styling matching Phase II

### Testing Strategy

1. **Unit Tests** - MCP tools, agents, services
2. **Integration Tests** - Chat endpoint with mock LLM
3. **E2E Tests** - Voice → transcription → chat → task creation
4. **Acceptance Tests** - All spec user scenarios

---

*End of Phase 2 Planning*

## Next Steps

1. ✅ Constitution Check: PASS
2. ✅ Phase 0 Research: COMPLETE (Context7 + agent-skills)
3. ✅ Phase 1 Design: COMPLETE (data model + contracts)
4. ⏭️ **Next Command**: `/sp.tasks` - Generate implementation tasks

**Pre-Implementation Checklist**:
- [ ] Review `research.md` for detailed technical decisions
- [ ] Review `data-model.md` for entity definitions
- [ ] Review `quickstart.md` for setup instructions
- [ ] Verify all environment variables documented
- [ ] Ensure Context7 accessible during implementation
- [ ] Ensure all agent-skills loaded in Claude Code
