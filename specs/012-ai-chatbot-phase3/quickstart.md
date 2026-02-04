# Quickstart: AI-Powered Todo Chatbot

**Feature**: 012-ai-chatbot-phase3
**Date**: 2025-02-03
**Prerequisites**: Phase II (Full-Stack Web) complete
**Status**: All core user stories complete (T001-T113 ✅)

---

## Environment Setup

**★ Insight ─────────────────────────────────────**
Observability is configured FIRST, before any other services. This ensures all subsequent development is debuggable from day one. Structured logging with correlation IDs is non-negotiable for distributed AI systems.
─────────────────────────────────────────────────

### 1. Backend Environment Variables

Add to `backend/.env`:

```bash
# ==========================================
# EXISTING (Phase II)
# ==========================================
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=... (>=32 chars)
CORS_ORIGINS=http://localhost:3000

# ==========================================
# NEW (Phase III) - Observability
# ==========================================
# Logging Configuration (STRUCTURED LOGGING - MANDATORY)
LOG_LEVEL=info                    # debug|info|warn|error
LOG_FORMAT=json                   # json for prod, console for dev
CORRELATION_ID_HEADER=X-Correlation-ID
SLOW_QUERY_THRESHOLD_MS=500       # Log queries exceeding this
ENABLE_QUERY_LOGGING=true         # Log all DB queries at DEBUG level

# ==========================================
# NEW (Phase III) - External Services
# ==========================================
# OpenAI API (GPT-4o-mini, Whisper, embeddings)
OPENAI_API_KEY=sk-proj-...
TOKEN_COST_PER_1K=0.0001          # For cost estimation

# Qdrant Cloud (vector database)
QDRANT_URL=https://...
QDRANT_API_KEY=...

# Optional: Qdrant local (for development)
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=

# ==========================================
# NEW (Phase III) - Chat Configuration
# ==========================================
MAX_MESSAGE_LENGTH=5000           # Maximum chat message length
MAX_AUDIO_SIZE_MB=25              # Maximum audio file size for transcription
MAX_AUDIO_DURATION_SECONDS=30     # Maximum audio duration for voice input
```

### 2. Frontend Environment Variables

Add to `frontend/.env.local` (already configured for Phase II):

```bash
# No new variables needed - JWT auth flows through existing setup
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Installation

### Backend Dependencies

```bash
cd backend

# === OBSERVABILITY (INSTALL FIRST) ===
# Structured logging
pip install structlog

# === PHASE III DEPENDENCIES ===
# OpenAI Agents SDK
pip install openai-agents-python

# MCP Python SDK
pip install mcp

# SSE Streaming
pip install sse-starlette

# Qdrant Client
pip install qdrant-client

# OpenAI (if not already installed)
pip install openai

# Framer Motion (frontend)
cd ../frontend && npm install framer-motion

# Or install all at once
pip install structlog openai-agents-python mcp sse-starlette qdrant-client openai
```

### Update `pyproject.toml`

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    # Observability (must be first)
    "structlog>=24.0.0",
    # Phase III
    "openai-agents-python>=0.7.0",
    "mcp>=0.1.0",
    "sse-starlette>=2.0.0",
    "qdrant-client>=1.12.0",
]
```

---

## Observability Setup (REQUIRED)

All observability infrastructure is already implemented in:
- `backend/app/ai/utils/logging.py` - Structured logging with correlation IDs
- `backend/app/ai/middleware.py` - CorrelationMiddleware for request tracing

---

## Development Setup

### 1. Start Qdrant (Local Development)

**Option A: Docker (Recommended)**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Option B: Qdrant Cloud**
1. Sign up at https://cloud.qdrant.io/
2. Create new cluster (free tier available)
3. Copy URL and API key to `.env`

### 2. Run Database Migrations

```bash
cd backend

# Apply all migrations
python -m alembic upgrade head

# Verify conversations, messages, agent_handoffs tables exist
```

### 3. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at http://localhost:8000

### 4. Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

Frontend will be available at http://localhost:3000

---

## Verification

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

### 2. Check Authentication

```bash
# Login via frontend, then:
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

### 3. Test Chat Endpoint (SSE)

```bash
curl -N http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -d '{"message": "Hello, what can you do?"}'
```

Expected SSE response:
```
event: message_start
data: {"conversation_id": "...", "message_id": "..."}

event: token
data: {"content": "Hello"}

event: token
data: {"content": "!"}

event: message_done
data: {"final_output": "Hello! I can help you manage your todo list..."}
```

---

## Security Features (Phase III)

### Prompt Injection Sanitization (T126)

All user messages are sanitized for prompt injection attacks:
- Detects common injection patterns ("ignore instructions", "act as", etc.)
- Blocks suspicious inputs with 400 error
- Strips system instruction leaks from AI responses
- Logs all blocked attempts for security monitoring

### Concurrent Message Queuing (T125)

Per-conversation locks ensure sequential processing:
- Each conversation has its own asyncio.Lock
- Messages are processed in order received
- Prevents race conditions in agent state

### Conversation Archival (T120)

Soft delete pattern for 90-day retention:
- Conversations marked with `deleted_at` timestamp
- Background job archives old conversations
- Data preserved for audit trail

---

## Project Structure (Actual)

```
backend/app/
├── ai/                         # Phase III namespace
│   ├── agents/
│   │   └── context.py          # TodoContext for agent execution
│   ├── mcp/
│   │   └── tools.py             # TaskTools (add, list, complete, delete, semantic_search)
│   ├── models/
│   │   └── conversation.py      # Conversation, Message, AgentHandoff
│   ├── services/
│   │   ├── runner_service.py    # Chat orchestration with SSE streaming
│   │   └── openai_client.py     # GPT-4o-mini, Whisper, embeddings
│   ├── utils/
│   │   ├── logging.py           # Structured logging with correlation ID
│   │   ├── language.py          # Language detection (English vs Urdu)
│   │   └── sanitize.py          # Prompt injection sanitization (T126)
│   └── middleware.py            # CorrelationMiddleware for distributed tracing
├── routes/
│   └── chat.py                  # Chat endpoints (SSE, transcription, conversations)
└── services/
    └── scheduler_service.py     # Background jobs (includes conversation archival)

frontend/
├── components/
│   └── chat/                    # Chat UI components
│       ├── chat-panel.tsx       # Main chat interface with Deep Space theme
│       ├── chat-message.tsx     # Message display with markdown
│       ├── chat-input.tsx       # Message input with voice button
│       └── task-card.tsx        # Inline task cards with quick actions (T115-T117)
├── hooks/
│   └── use-chat.ts              # Chat state management
├── lib/
│   ├── api/
│   │   └── chat.ts              # Chat API client with SSE support
│   └── stores/
│       └── chat-store.ts        # Zustand store for chat UI state
└── types/
    └── chat.ts                  # Chat interfaces (Message, Conversation, ChatEvent)
```

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'agents'"

**Solution**:
```bash
pip install openai-agents-python
```

### Issue: Qdrant connection refused

**Solution**: Start Qdrant locally:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Issue: OpenAI API key invalid

**Solution**: Verify `OPENAI_API_KEY` in `.env` file

### Issue: SSE not streaming in browser

**Solution**: Check CORS settings - ensure SSE endpoint is allowed

### Issue: Prompt injection blocked

**Solution**: Rephrase your message. Legitimate queries like "ignore this task" may trigger false positives - try "mark this task as done" instead.

---

## Implementation Status

| User Story | Tasks | Status | Bonus |
|------------|-------|--------|-------|
| US1: Natural Language Task Management | T026-T049 | ✅ Complete | - |
| US2: Conversational Context Memory | T050-T056 | ✅ Complete | - |
| US3: Semantic Task Search | T057-T067 | ✅ Complete | - |
| US4: Urdu Language Support | T068-T079 | ✅ Complete | +100 |
| US5: Voice Command Input | T080-T092 | ✅ Complete | +200 |
| US6: AI Task Summarization | T093-T099 | ✅ Complete | - |
| US7: MCP Tool Integration | T100-T105 | ✅ Complete | - |
| US8: Agent Handoffs | T106-T113 | ✅ Complete | +200 |

**Phase 11 (Polish)** - Remaining tasks:
- T115-T118: Task cards in chat (✅ Complete)
- T120: Conversation archival (✅ Complete)
- T125: Concurrent message queuing (✅ Complete)
- T126: Prompt injection sanitization (✅ Complete)
- T127-T130: Documentation, migrations, verification, testing (⏳ In Progress)

---

## Next Steps

1. ✅ Review this quickstart guide
2. ✅ Set up environment variables
3. ✅ Install dependencies
4. ⏭️ Run database migrations (T128)
5. ⏭️ Verify Qdrant collection (T129)
6. ⏭️ Test user scenarios (T130)

---

*Quickstart Complete: All setup instructions documented*
