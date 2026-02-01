# Quickstart: AI-Powered Todo Chatbot

**Feature**: 012-ai-chatbot-phase3
**Date**: 2026-01-30
**Prerequisites**: Phase II (Full-Stack Web) complete

---

## Environment Setup

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
# NEW (Phase III)
# ==========================================
# OpenAI API (GPT-4o-mini, Whisper, embeddings)
OPENAI_API_KEY=sk-proj-...

# Qdrant Cloud (vector database)
QDRANT_URL=https://...
QDRANT_API_KEY=...

# Optional: Qdrant local (for development)
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=
```

### 2. Frontend Environment Variables

Add to `frontend/.env.local` (already configured for Phase II):

```bash
# No new variables needed - JWT auth flows through existing setup
```

---

## Installation

### Backend Dependencies

```bash
cd backend

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

# Or install all at once
pip install openai-agents-python mcp sse-starlette qdrant-client openai
```

### Update `pyproject.toml`

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "openai-agents-python>=0.7.0",
    "mcp>=0.1.0",
    "sse-starlette>=2.0.0",
    "qdrant-client>=1.12.0",
]
```

### Frontend Dependencies

```bash
cd frontend

# ChatKit for AI chat UI
npm install @ai-sdk/sdk @ai-sdk/react

# Or if using specific versions
npm install @ai-sdk/sdk@latest @ai-sdk/react@latest
```

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

# Create new tables
python -m alembic revision --autogenerate -m "Add chat tables"
python -m alembic upgrade head
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

## Agent-Skills Reference

During implementation, use these existing skills:

| Skill | Command | Purpose |
|-------|---------|---------|
| OpenAI Agents | `openai-agents-guide` | Agent definition, handoffs |
| MCP Server | `mcp-server-builder` | MCP tool implementation |
| Qdrant | `qdrant-guide` | Vector search setup |
| Whisper | `whisper-guide` | Voice transcription |
| Urdu | `urdu-language-guide` | RTL text support |
| Voice Commands | `voice-commands-guide` | Audio recording UI |
| ChatKit | `chatkit-guide` | Chat UI components |

---

## Context7 Queries

During implementation, query Context7 for latest patterns:

```bash
# OpenAI Agents SDK
context7 query /openai/openai-agents-python "agent handoff context"

# MCP Python SDK
context7 query /modelcontextprotocol/python-sdk "FastMCP tool definition"

# SSE Streaming
context7 query /sysid/sse-starlette "EventSourceResponse async generator"

# Qdrant
context7 query /qdrant/qdrant-client "async query_points filter"
```

---

## Project Structure Reference

```
backend/
├── app/
│   ├── agents/                # NEW: AI agents
│   │   ├── todo_agent.py
│   │   ├── planning_agent.py
│   │   └── query_agent.py
│   ├── mcp/                   # NEW: MCP server
│   │   ├── server.py
│   │   └── tools/
│   ├── chat/                  # NEW: Chat endpoints
│   │   ├── router.py
│   │   └── service.py
│   ├── search/                # NEW: Semantic search
│   │   └── service.py
│   ├── embeddings/            # NEW: Embeddings
│   │   └── service.py
│   └── voice/                 # NEW: Voice transcription
│       └── service.py

frontend/
├── src/
│   ├── app/
│   │   └── chat/              # NEW: Chat page
│   └── components/
│       └── chat/              # NEW: Chat UI
│           ├── ChatInterface.tsx
│           ├── VoiceRecorder.tsx
│           └── TaskCard.tsx
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

---

## Next Steps

1. ✅ Review this quickstart guide
2. ✅ Set up environment variables
3. ✅ Install dependencies
4. ⏭️ Run `/sp.tasks` to generate implementation tasks
5. ⏭️ Follow tasks.md for implementation order

---

*Quickstart Complete: All setup instructions documented*
