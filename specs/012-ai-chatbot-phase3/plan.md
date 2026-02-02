# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `012-ai-chatbot-phase3` | **Date**: 2026-01-30 | **Spec**: [spec.md](./spec.md)

## Summary

Implement an AI-powered chatbot for the Evolution of Todo app using OpenAI Agents SDK with multi-agent handoffs, MCP (Model Context Protocol) tools for stateless task operations, semantic vector search with Qdrant, multi-language Urdu support, and voice commands via Whisper API. The chatbot provides natural language task management through conversation while maintaining stateless architecture with database persistence.

**Key Technologies:**
- OpenAI Agents SDK (`/openai/openai-agents-python` v0.7.0) - Multi-agent orchestration with handoffs
- MCP Python SDK (`/modelcontextprotocol/python-sdk`) - Standardized tool protocol
- FastAPI with SSE Starlette (`/sysid/sse-starlette`) - Streaming responses
- Qdrant Client (`/qdrant/qdrant-client`) - Semantic vector search
- OpenAI Whisper API - Voice transcription (multilingual including Urdu)

---

## Milestone 1: Backend Core & Observability

**Goal**: Establish foundation with data models, observability infrastructure, database migrations, and basic API endpoints.

**Deliverables**:
- Structured logging with correlation IDs
- Database models (Conversation, Message, AgentHandoff)
- Alembic migrations
- Basic conversation CRUD endpoints
- Health check with observability status

### 1.1 Observability Infrastructure (IMPLEMENT FIRST)

**★ Insight ─────────────────────────────────────**
Observability is NOT optional for distributed AI systems. With agent handoffs, MCP tool calls, external APIs (OpenAI, Qdrant, Whisper), and SSE streaming, debugging without structured logging is nearly impossible. This must be implemented FIRST.
─────────────────────────────────────────────────

**Files to Create**:
```
backend/app/observability/
├── __init__.py
├── logging_config.py    # structlog configuration
├── middleware.py         # Correlation ID middleware
├── tracer.py            # Request tracing context
└── metrics.py           # Performance metrics aggregation
```

**Implementation Tasks**:

| Task | File | Description |
|------|------|-------------|
| Configure structlog | `logging_config.py` | JSON/console output, processors for timestamp, correlation_id, user_id |
| Correlation middleware | `middleware.py` | Generate/extract X-Correlation-ID, propagate via contextvars |
| Request tracer | `tracer.py` | Log request start/end with duration_ms |
| Metrics aggregator | `metrics.py` | p50/p95/p99 latency, tool call stats, token tracking |

**Environment Variables**:
```bash
LOG_LEVEL=info                    # debug|info|warn|error
LOG_FORMAT=json                   # json|console (for dev)
CORRELATION_ID_HEADER=X-Correlation-ID
SLOW_QUERY_THRESHOLD_MS=500       # Log queries exceeding this
ENABLE_QUERY_LOGGING=true         # Log all DB queries at DEBUG
TOKEN_COST_PER_1K=0.0001          # For cost estimation
```

**Dependencies**:
```bash
pip install structlog>=24.0.0
```

**Integration Points**:
- Update `backend/app/main.py` to configure logging BEFORE any other imports
- Register `ObservabilityMiddleware` as first middleware in FastAPI app

---

### 1.2 Database Models

**Reference**: `data-model.md` for complete entity definitions

**Files to Create/Modify**:
```
backend/app/
├── models.py              # EXTEND: Add Conversation, Message, AgentHandoff
└── db.py                  # UPDATE: Include new models in get_session()
```

**New Models**:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Conversation` | Chat session | id (UUID), user_id, title, language_preference, message_count |
| `Message` | Single message | id (UUID), conversation_id, correlation_id, role, content, tool_calls (JSON) |
| `AgentHandoff` | Handoff tracking | id (UUID), conversation_id, correlation_id, from_agent, to_agent, reason |

**SQLModel Definitions**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(default="New Chat")
    language_preference: str = Field(default="auto")  # en/ur/auto
    message_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    correlation_id: str = Field(index=True)
    role: str = Field(...)  # "user" | "assistant" | "system"
    content: str = Field(...)
    tool_calls: Optional[dict] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentHandoff(SQLModel, table=True):
    __tablename__ = "agent_handoffs"
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    correlation_id: UUID = Field(index=True)
    from_agent: str = Field(...)
    to_agent: str = Field(...)
    reason: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context_snapshot: Optional[dict] = Field(default=None)
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None)
```

**Extended Task Model**:
```python
# Add to existing Task model
class Task(SQLModel, table=True):
    # ... existing fields ...
    transcription_text: Optional[str] = Field(default=None)
    ai_summary: Optional[str] = Field(default=None)  # Max 100 chars
    embedding_id: Optional[str] = Field(default=None)  # Qdrant vector reference
```

---

### 1.3 Database Migrations

**Files to Create**:
```
backend/alembic/versions/
└── 001_add_chat_tables.py    # Alembic migration
```

**Migration Tasks**:

| Operation | Table | Details |
|-----------|-------|---------|
| CREATE | `conversations` | With indexes on user_id, updated_at |
| CREATE | `messages` | With indexes on conversation_id, correlation_id |
| CREATE | `agent_handoffs` | With indexes on conversation_id, correlation_id, timestamp, success |
| ALTER | `tasks` | Add transcription_text, ai_summary, embedding_id columns |

**Commands**:
```bash
cd backend
alembic revision --autogenerate -m "Add chat tables for Phase III"
alembic upgrade head
```

---

### 1.4 Basic API Endpoints

**Files to Create**:
```
backend/app/api/
└── conversations.py     # Conversation CRUD endpoints
```

**Endpoints**:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/conversations` | Create new conversation |
| GET | `/api/conversations` | List user's conversations (paginated) |
| GET | `/api/conversations/{id}` | Get conversation with messages |
| DELETE | `/api/conversations/{id}` | Delete conversation (cascade messages) |

**Pydantic Schemas**:
```python
class ConversationCreate(SQLModel):
    title: str | None = None
    language_preference: str = "auto"

class ConversationPublic(SQLModel):
    id: UUID
    user_id: str
    title: str
    language_preference: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class MessagePublic(SQLModel):
    id: UUID
    conversation_id: UUID
    correlation_id: str
    role: str
    content: str
    tool_calls: dict | None
    created_at: datetime
```

---

### 1.5 Health Check Endpoint

**File to Update**:
```
backend/app/api/health.py    # EXTEND: Add observability status
```

**Enhanced Health Check**:
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "ok",  # Check DB connection
            "logging": "configured",  # Verify structlog ready
            "qdrant": "not_configured",  # Will be ok in Milestone 2
            "openai": "not_configured",  # Will be ok in Milestone 2
        }
    }
```

---

## Milestone 2: Backend Logic & Testing

**Goal**: Implement core AI logic including agents, MCP tools, streaming, and comprehensive testing.

**Deliverables**:
- OpenAI Agents SDK integration with multi-agent handoffs
- MCP server with task management tools
- Qdrant semantic search service
- Whisper transcription service
- SSE streaming chat endpoint
- Unit and integration tests

### 2.1 MCP Server Implementation

**Reference**: Use `mcp-server-builder` agent skill for implementation workflow

**Files to Create**:
```
backend/app/mcp/
├── __init__.py
├── server.py              # FastMCP server setup
└── tools/
    ├── __init__.py
    ├── add_task.py
    ├── list_tasks.py
    ├── complete_task.py
    ├── delete_task.py
    ├── update_task.py
    └── semantic_search.py
```

**MCP Tools Specification**:

| Tool | Parameters | Returns | Description |
|------|------------|---------|-------------|
| `add_task` | user_id, title, description?, priority?, due_date? | {status, task_id, task} | Create new task |
| `list_tasks` | user_id, status?, limit?, offset? | {status, tasks, total} | List user's tasks |
| `complete_task` | user_id, task_id | {status, task} | Mark task complete |
| `delete_task` | user_id, task_id | {status, deleted} | Delete task |
| `update_task` | user_id, task_id, title?, description?, priority?, due_date? | {status, task} | Update task |
| `semantic_search` | user_id, query, limit | {status, results} | Search by meaning |

**FastMCP Setup**:
```python
from mcp.server.fastmcp import FastMCP
from contextvars import ContextVar

mcp = FastMCP("TodoAssistant")

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

@mcp.tool()
async def add_task(user_id: str, title: str, description: str | None = None,
                   priority: str = "MEDIUM", due_date: str | None = None) -> dict:
    """Create a new task for the user."""
    correlation_id = correlation_id_var.get()
    logger.info("mcp_tool_call_start", tool_name="add_task", user_id=user_id,
                correlation_id=correlation_id)
    # Implementation...
```

**Transport**: `streamable-http` mounted in FastAPI application (in-process)

---

### 2.2 OpenAI Agents SDK Integration

**Reference**: Use `openai-agents-guide` skill for agent patterns

**Files to Create**:
```
backend/app/agents/
├── __init__.py
├── base.py               # Agent configuration and runner
├── todo_agent.py         # TodoAssistant - main agent
├── planning_agent.py     # PlanningAgent - weekly planning specialist
└── query_agent.py        # TaskQueryAgent - search specialist
```

**Agent Specifications**:

| Agent | Purpose | Triggers | Handoffs |
|-------|---------|----------|----------|
| `TodoAssistant` | Main agent for general commands | All initial requests | PlanningAgent, TaskQueryAgent |
| `PlanningAgent` | Weekly planning and prioritization | "plan my week", "help me prioritize", "what should I focus on" | Returns to TodoAssistant |
| `TaskQueryAgent` | Complex task searches and filtering | "find", "search", "show me [concept]" | Returns to TodoAssistant |

**Agent Pattern**:
```python
from openai import OpenAI
from openai.agents import Agent, Runner

client = OpenAI()

todo_assistant = Agent(
    name="TodoAssistant",
    instructions=(
        "You are a helpful todo assistant. Use MCP tools to manage tasks. "
        "Hand off to PlanningAgent for weekly planning, "
        "TaskQueryAgent for complex searches."
    ),
    tools=mcp_tools,  # Loaded from MCP server
    handoffs=[planning_agent, query_agent],
)

async def run_agent(conversation_history: list[Message], user_message: str) -> AsyncIterator[str]:
    """Run agent with streaming response."""
    context = [msg.to_openai_format() for msg in conversation_history]
    result = Runner.run_streaming(
        agent=todo_assistant,
        context=context,
        input=user_message,
    )
    async for chunk in result:
        yield chunk
```

---

### 2.3 Qdrant Integration

**Reference**: Use `qdrant-guide` skill for vector patterns

**Files to Create**:
```
backend/app/search/
├── __init__.py
├── service.py            # Qdrant async client
└── fallback.py           # Keyword search fallback
```

**Qdrant Configuration**:
```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantService:
    def __init__(self, url: str, api_key: str | None = None):
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.collection_name = "tasks"
        self.vector_size = 1536  # text-embedding-3-small

    async def ensure_collection(self):
        """Create collection if not exists."""
        await self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE,
            ),
        )
        # Create payload indexes for filtering
        await self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="user_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )

    async def search(self, user_id: str, query_vector: list[float], limit: int = 10):
        """Search vectors scoped to user."""
        return await self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=limit,
        )
```

---

### 2.4 Embedding Service

**Files to Create**:
```
backend/app/embeddings/
├── __init__.py
└── service.py            # OpenAI text-embedding-3-small
```

**Implementation**:
```python
from openai import AsyncOpenAI

class EmbeddingService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_task(self, task: Task) -> str:
        """Generate and store embedding for task."""
        text = f"{task.title}. {task.description or ''}"
        vector = await self.embed(text)
        # Store in Qdrant and return embedding_id
```

---

### 2.5 Whisper Transcription Service

**Reference**: Use `whisper-guide` skill for transcription patterns

**Files to Create**:
```
backend/app/voice/
├── __init__.py
└── service.py            # Whisper API integration
```

**Implementation**:
```python
from openai import AsyncOpenAI

class TranscriptionService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe(self, audio_file: bytes, filename: str) -> dict:
        """Transcribe audio file using Whisper."""
        from io import BytesIO

        buffer = BytesIO(audio_file)
        buffer.name = filename

        transcription = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            response_format="verbose_json",
        )

        return {
            "text": transcription.text,
            "language": transcription.language,
            "duration": transcription.duration,
        }
```

**Transcription Endpoint**:
```python
@router.post("/api/chat/transcribe")
async def transcribe_audio(
    request: Request,
    file: UploadFile,
    language: str | None = None,
    user_id: str = Depends(get_current_user_id),
):
    """Transcribe audio file to text."""
    # Validate file size (max 25 MB)
    # Validate file format
    # Call TranscriptionService
    # Return transcription
```

---

### 2.6 SSE Streaming Chat Endpoint

**Files to Create**:
```
backend/app/chat/
├── __init__.py
├── router.py             # /api/chat with SSE
└── service.py            # Chat business logic
```

**SSE Streaming Pattern**:
```python
from sse_starlette.sse import EventSourceResponse, JSONServerSentEvent

@router.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    correlation_id: str = Depends(get_correlation_id),
):
    """Send message and receive streaming AI response."""

    async def event_generator():
        # Create/get conversation
        conversation = await get_or_create_conversation(
            user_id=user_id,
            conversation_id=request.conversation_id,
        )

        # Save user message
        user_message = await create_message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            correlation_id=correlation_id,
        )

        yield JSONServerSentEvent({
            "event": "message_start",
            "data": {
                "conversation_id": str(conversation.id),
                "message_id": str(user_message.id),
                "correlation_id": correlation_id,
            }
        })

        # Run agent with streaming
        try:
            async for token in run_agent(
                conversation=conversation,
                user_message=request.message,
                correlation_id=correlation_id,
            ):
                yield JSONServerSentEvent({"event": "token", "data": {"content": token}})

            yield JSONServerSentEvent({"event": "message_done"})

        except Exception as e:
            logger.error("chat_error", correlation_id=correlation_id, error=str(e))
            yield JSONServerSentEvent({"event": "error", "data": {"message": "An error occurred"}})

    return EventSourceResponse(event_generator())
```

---

### 2.7 Unit Tests

**Files to Create**:
```
backend/tests/
├── test_mcp/
│   ├── __init__.py
│   ├── test_add_task.py
│   ├── test_list_tasks.py
│   ├── test_complete_task.py
│   ├── test_delete_task.py
│   ├── test_update_task.py
│   └── test_semantic_search.py
├── test_agents/
│   ├── __init__.py
│   ├── test_todo_agent.py
│   ├── test_planning_agent.py
│   └── test_query_agent.py
└── test_services/
    ├── __init__.py
    ├── test_embeddings.py
    ├── test_qdrant.py
    └── test_transcription.py
```

**Test Dependencies**:
```bash
pip install pytest pytest-asyncio pytest-mock
```

**Test Example**:
```python
import pytest
from app.mcp.tools.add_task import add_task

@pytest.mark.asyncio
async def test_add_task_creates_task(db_session):
    result = await add_task(
        user_id="test_user",
        title="Test Task",
        description="Test Description",
    )
    assert result["status"] == "success"
    assert "task_id" in result
```

---

### 2.8 Integration Tests

**Files to Create**:
```
backend/tests/integration/
├── __init__.py
├── test_chat_endpoint.py
├── test_conversation_flow.py
└── test_agent_handoffs.py
```

**Integration Test Example**:
```python
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

@pytest.mark.asyncio
async def test_chat_creates_task(async_client: AsyncClient, auth_token: str):
    response = await async_client.post(
        "/api/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
```

---

## Milestone 3: Frontend Implementation

**Goal**: Build complete chat interface with voice input, task cards, and Deep Space theme styling.

**Deliverables**:
- Chat interface components using ChatKit
- Voice recorder with 30-second limit
- Task cards with inline actions
- SSE streaming integration
- Floating chat widget
- Deep Space theme styling

### 3.1 Chat API Client

**Files to Create**:
```
frontend/lib/api/
└── chat.ts              # Chat API with SSE support
```

**Implementation**:
```typescript
export class ChatApiClient {
  private async getAuthToken(): Promise<string | null> {
    const response = await fetch(`${this.appUrl}/api/auth/token`, {
      credentials: "include",
    })
    const data = await response.json()
    return data.token
  }

  async *streamChat(message: string, conversationId?: string): AsyncGenerator<ChatEvent> {
    const token = await this.getAuthToken()
    const response = await fetch(`${this.apiUrl}/api/chat`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message, conversation_id }),
    })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split("\n")

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = JSON.parse(line.slice(6))
          yield data
        }
      }
    }
  }
}
```

---

### 3.2 Chat Components

**Reference**: Use `chatkit-guide` skill for ChatKit patterns

**Files to Create**:
```
frontend/components/chat/
├── ChatInterface.tsx     # Main chat container
├── MessageList.tsx       # Message display with SSE
├── MessageInput.tsx      # Text input with voice button
├── TypingIndicator.tsx   # Loading state
├── TaskCard.tsx          # Inline task cards
└── VoiceRecorder.tsx     # Microphone + recording UI
```

**ChatInterface Component**:
```typescript
"use client"

import { useState } from "react"
import { useChatSSE } from "@/hooks/use-chat"

export function ChatInterface() {
  const { messages, sendMessage, isStreaming } = useChatSSE()

  return (
    <div className="flex flex-col h-full bg-background">
      <MessageList messages={messages} />
      {isStreaming && <TypingIndicator />}
      <MessageInput onSend={sendMessage} />
    </div>
  )
}
```

**VoiceRecorder Component**:
```typescript
"use client"

import { useState, useRef } from "react"

export function VoiceRecorder({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [isRecording, setIsRecording] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const [duration, setDuration] = useState(0)

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mediaRecorder = new MediaRecorder(stream)
    mediaRecorderRef.current = mediaRecorder

    mediaRecorder.ondataavailable = async (event) => {
      if (event.data.size > 0) {
        // Upload to /api/chat/transcribe
        const transcription = await transcribeAudio(event.data)
        onTranscript(transcription.text)
      }
    }

    mediaRecorder.start()
    setIsRecording(true)

    // 30-second limit
    setTimeout(() => {
      if (mediaRecorder.state === "recording") {
        mediaRecorder.stop()
        setIsRecording(false)
      }
    }, 30000)
  }

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      className={cn(
        "rounded-full p-3 transition-colors",
        isRecording ? "bg-destructive animate-pulse" : "bg-primary"
      )}
    >
      <Mic className="h-5 w-5" />
    </button>
  )
}
```

---

### 3.3 Chat Hooks

**Files to Create**:
```
frontend/hooks/
├── use-chat.ts           # Chat state with SSE
├── use-conversations.ts  # Conversation CRUD
└── use-voice-input.ts    # Voice recording state
```

**useChat Hook**:
```typescript
import { useMutation } from "@tanstack/react-query"
import { useCallback, useEffect, useState } from "react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export function useChatSSE(conversationId?: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)

  const sendMessage = useCallback(async (content: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsStreaming(true)

    // Stream response
    let assistantContent = ""
    for await (const event of chatApi.streamChat(content, conversationId)) {
      if (event.event === "token") {
        assistantContent += event.data.content
        // Update last message with streaming content
      } else if (event.event === "message_done") {
        setIsStreaming(false)
      }
    }
  }, [conversationId])

  return { messages, sendMessage, isStreaming }
}
```

---

### 3.4 Deep Space Theme Styling

**Reference**: `specs/012-ai-chatbot-phase3/CLAUDE.md` for color values

**CSS Variables** (already in frontend from Phase II):
```css
/* Deep Space Theme - OKLCH Color Space */
--custom-background: oklch(0.08 0.01 270);     /* Deep space black */
--custom-foreground: oklch(0.95 0.01 270);     /* Near white */
--custom-primary: oklch(0.91 0.17 195);        /* Neon cyan #00f5ff */
--custom-secondary: oklch(0.65 0.26 293);      /* Neon purple #a855f7 */
--glass-bg: rgba(255, 255, 255, 0.05);
--glass-border: rgba(255, 255, 255, 0.1);
--glow-primary: 0 0 20px rgba(0, 245, 255, 0.3);
```

**Component Styling**:
```typescript
// Message bubble with glassmorphism
const messageBubble = cn(
  "max-w-[80%] rounded-2xl px-4 py-2",
  "bg-glass-bg backdrop-blur-md border border-glass-border",
  role === "user" ? "ml-auto bg-primary/20" : "mr-auto"
)
```

---

### 3.5 Task Cards in Chat

**Files to Create**:
```
frontend/components/chat/TaskCard.tsx
```

**Implementation**:
```typescript
export function TaskCard({ task }: { task: Task }) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-glass-bg border border-glass-border">
      <button
        onClick={() => toggleComplete(task.id)}
        className={cn(
          "w-5 h-5 rounded border-2 flex items-center justify-center",
          task.completed ? "bg-success border-success" : "border-muted"
        )}
      >
        {task.completed && <Check className="h-3 w-3" />}
      </button>
      <div className="flex-1">
        <p className={cn("text-sm", task.completed && "line-through text-muted")}>
          {task.title}
        </p>
      </div>
      <button onClick={() => deleteTask(task.id)} className="text-destructive">
        <Trash2 className="h-4 w-4" />
      </button>
    </div>
  )
}
```

---

### 3.6 Floating Chat Widget

**Files to Create**:
```
frontend/components/chat/ChatFab.tsx
```

**Implementation**:
```typescript
"use client"

import { useState } from "react"
import { MessageCircle } from "lucide-react"

export function ChatFab() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-primary shadow-glow-primary flex items-center justify-center hover:scale-110 transition-transform"
      >
        <MessageCircle className="h-6 w-6" />
      </button>

      {isOpen && (
        <div className="fixed bottom-24 right-6 w-[400px] h-[600px] rounded-2xl bg-background border border-glass-border shadow-2xl">
          <ChatInterface onClose={() => setIsOpen(false)} />
        </div>
      )}
    </>
  )
}
```

---

## Milestone 4: Frontend Testing & Polish

**Goal**: Comprehensive testing, UX refinement, and production readiness.

**Deliverables**:
- E2E tests for chat flows
- Voice input testing
- Urdu language testing
- Accessibility audit (WCAG 2.1 AA)
- Performance optimization
- Error boundary handling

### 4.1 E2E Tests

**Files to Create**:
```
frontend/tests/e2e/
├── chat.spec.ts         # Chat flow E2E
├── voice.spec.ts        # Voice input E2E
├── task-creation.spec.ts # Task creation via chat
└── urdu-language.spec.ts # Urdu language support
```

**Test Framework**: Playwright
```bash
npm install -D @playwright/test
```

**E2E Test Example**:
```typescript
import { test, expect } from "@playwright/test"

test("user can create task via chat", async ({ page }) => {
  await page.goto("/chat")

  // Type message
  await page.fill('[data-testid="chat-input"]', "Add a task to buy groceries")
  await page.click('[data-testid="send-button"]')

  // Wait for AI response
  await page.waitForSelector('[data-testid="ai-message"]')

  // Verify task was created
  await page.goto("/dashboard")
  const taskCard = page.locator('text=Buy groceries')
  await expect(taskCard).toBeVisible()
})
```

---

### 4.2 Voice Input Testing

**Test Scenarios**:
```typescript
test("voice recording stops at 30 second limit", async ({ page }) => {
  // Mock MediaRecorder
  await page.evaluate(() => {
    window.MediaRecorder = class MockMediaRecorder {
      ondataavailable: ((event: any) => void) | null = null
      state = "recording"
      start() { /* ... */ }
      stop() { /* ... */ }
    }
  })

  // Start recording
  await page.click('[data-testid="voice-button"]')

  // Wait for 30-second timeout
  await page.waitForTimeout(31000)

  // Verify recording stopped
  const isRecording = await page.locator('[data-testid="voice-button"].recording').count()
  expect(isRecording).toBe(0)
})
```

---

### 4.3 Urdu Language Testing

**Test Scenarios**:
```typescript
test("chatbot understands Urdu commands", async ({ page }) => {
  await page.goto("/chat")

  // Send Urdu command
  await page.fill('[data-testid="chat-input"]', "مجھے ایک ٹاسک شامل کرو")
  await page.click('[data-testid="send-button"]')

  // Verify AI responds (may ask for task title)
  await page.waitForSelector('[data-testid="ai-message"]')

  // Send task title in Urdu
  await page.fill('[data-testid="chat-input"]', "گھر جا")
  await page.click('[data-testid="send-button"]')

  // Verify task was created
  await page.goto("/dashboard")
  const taskCard = page.locator('[data-testid="task-card"]:has-text("گھر جا")')
  await expect(taskCard).toBeVisible()
})
```

---

### 4.4 Accessibility Audit

**WCAG 2.1 Level AA Requirements**:

| Requirement | Component | Implementation |
|-------------|-----------|----------------|
| Keyboard navigation | All interactive elements | Tab index, Enter/Space handlers |
| Screen reader announcements | New messages | `aria-live="polite"` region |
| Focus indicators | All focusable elements | `ring-2 ring-primary` on focus |
| Color contrast | All text | ≥4.5:1 ratio (OKLCH values) |
| ARIA labels | Chat interface | `aria-label="Chat input"`, etc. |
| Voice input alternative | Voice button | Keyboard shortcut: `Cmd/Ctrl + V` |

**Testing Tools**:
```bash
npm install -D @axe-core/playwright
```

---

### 4.5 Performance Optimization

**Optimization Targets**:

| Metric | Target | Implementation |
|--------|--------|----------------|
| First contentful paint | < 1s | Dynamic import for ChatInterface |
| Time to interactive | < 2s | Code splitting for chat components |
| SSE first token | < 1s | Optimistic UI updates |
| Bundle size | < 200KB | Tree-shaking, lazy loading |

**Implementation**:
```typescript
// Dynamic import for chat components
const ChatInterface = dynamic(
  () => import("@/components/chat/ChatInterface"),
  { loading: () => <ChatSkeleton />, ssr: false }
)
```

---

### 4.6 Error Boundaries

**Files to Create**:
```
frontend/components/chat/
└── ErrorBoundary.tsx    # React error boundary
```

**Implementation**:
```typescript
"use client"

import { Component, ReactNode } from "react"

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ChatErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
          <p className="text-destructive">Something went wrong. Please refresh.</p>
        </div>
      )
    }
    return this.props.children
  }
}
```

---

## Milestone Completion Criteria

### Milestone 1: Backend Core & Observability

- [ ] Structured logging configured with structlog
- [ ] Correlation ID middleware propagating through all requests
- [ ] Conversation, Message, AgentHandoff models defined
- [ ] Alembic migration executed successfully
- [ ] Conversation CRUD endpoints functional
- [ ] Health check returns observability status

### Milestone 2: Backend Logic & Testing

- [ ] MCP server with all 6 tools implemented
- [ ] Three agents (TodoAssistant, PlanningAgent, TaskQueryAgent) with handoffs
- [ ] Qdrant collection created with payload indexes
- [ ] Embedding service generating vectors
- [ ] Whisper transcription endpoint functional
- [ ] SSE streaming chat endpoint working
- [ ] Unit tests for MCP tools (80%+ coverage)
- [ ] Unit tests for agents (80%+ coverage)
- [ ] Integration tests for chat flow

### Milestone 3: Frontend Implementation

- [ ] ChatInterface component with SSE streaming
- [ ] VoiceRecorder with 30-second limit
- [ ] TaskCard component with inline actions
- [ ] ChatFab floating widget
- [ ] Deep Space theme styling applied
- [ ] useChat hook with SSE support
- [ ] Chat API client with streaming

### Milestone 4: Frontend Testing & Polish

- [ ] E2E tests for core chat flows
- [ ] Voice input E2E tests
- [ ] Urdu language E2E tests
- [ ] WCAG 2.1 Level AA compliance verified
- [ ] Performance targets met (FCP < 1s, TTI < 2s)
- [ ] Error boundaries implemented
- [ ] Production build tested

---

## Dependencies and Environment Variables

### Backend Dependencies

```toml
[project]
dependencies = [
    # Observability (install FIRST)
    "structlog>=24.0.0",

    # Existing (Phase II)
    "fastapi>=0.115.0",
    "sqlmodel>=0.0.22",
    "alembic>=1.13.0",

    # Phase III
    "openai-agents-python>=0.7.0",
    "mcp>=0.1.0",
    "sse-starlette>=2.0.0",
    "qdrant-client>=1.12.0",
    "openai>=1.0.0",
]
```

### Backend Environment Variables

```bash
# Existing (Phase II)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=... (>=32 chars)
CORS_ORIGINS=http://localhost:3000

# Observability
LOG_LEVEL=info
LOG_FORMAT=json

# Phase III
OPENAI_API_KEY=sk-proj-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
```

### Frontend Dependencies

```bash
npm install @ai-sdk/sdk @ai-sdk/react
npm install -D @playwright/test @axe-core/playwright
```

---

## Next Steps

1. ✅ Review this re-architected plan
2. ⏭️ Start Milestone 1: Implement observability infrastructure FIRST
3. ⏭️ Use Context7 and agent-skills during implementation
4. ⏭️ Run `/sp.tasks` to generate detailed implementation tasks

---

*Plan Re-architected: 4-Milestone structure for phased delivery*
