# Data Model: AI-Powered Todo Chatbot

**Feature**: 012-ai-chatbot-phase3
**Date**: 2026-01-30
**Status**: Complete

## Observability & Audit Fields

**★ Insight ─────────────────────────────────────**
Every entity includes observability fields for distributed tracing. The `correlation_id` propagates through the entire request lifecycle, enabling end-to-end tracing from API ingress through agent handoffs to database operations.
─────────────────────────────────────────────────

### Cross-Cutting Observability Fields

All new entities include these standard observability fields:

| Field | Type | Purpose |
|-------|------|---------|
| `correlation_id` | UUID (indexed) | Distributed tracing across services |
| `created_at` | timestamp (UTC) | Audit trail - entity creation |
| `updated_at` | timestamp (UTC) | Audit trail - last modification |

**Index Strategy**: `correlation_id` is indexed on all entities for log queries to reconstruct request flows.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (existing from Phase II)                   │
│                              ┌─────────────────────────────────────────┐   │
│                              │ id: str (auth|...)                    │   │
│                              │ email: str                            │   │
│                              │ ...                                   │   │
│                              └─────────────────────────────────────────┘   │
│                                             │                              │
│                                             │ user_id                      │
│                                             ▼                              │
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONVERSATION (new)                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ id: UUID (PK)                                                           ││
│  │ user_id: str (FK → USER)                                              ││
│  │ title: str (auto-generated after 3 messages)                            ││
│  │ language_preference: str (en/ur/auto)                                  ││
│  │ message_count: int                                                     ││
│  │ created_at: datetime                                                   ││
│  │ updated_at: datetime                                                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                             │                              │
│                                             │ conversation_id              │
│                    ┌────────────────────────┼────────────────────────┐      │
│                    ▼                        ▼                        ▼      │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────┐│
│  │    MESSAGE (new)        │  │  AGENT_HANDOFF (new)    │  │    TASK (extended)  ││
│  │ ───────────────────────│  │ ───────────────────────│  │ ────────────────────││
│  │ id: UUID (PK)          │  │ id: UUID (PK)          │  │ id: int (PK)        ││
│  │ conversation_id: UUID  │  │ conversation_id: UUID  │  │ user_id: str        ││
│  │ correlation_id: str    │  │ from_agent: str         │  │ title: str          ││
│  │ role: str              │  │ to_agent: str           │  │ ...                 ││
│  │ content: str           │  │ reason: str             │  │ transcription_text: ││
│  │ tool_calls: JSON       │  │ timestamp: datetime     │  │   str | NULL ← NEW   ││
│  │ created_at: datetime   │  │ context_snapshot: JSON  │  │ ai_summary: str |    ││
│  └─────────────────────────┘  └─────────────────────────┘  │   NULL ← NEW        ││
│                                                        │ embedding_id: str |   ││
│                                                        │   NULL ← NEW         ││
│                                                        └───────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## New Entities

### 1. Conversation

**Purpose**: Represents a chat session between a user and the AI.

**Table Name**: `conversations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique conversation identifier |
| `user_id` | str | FK, NOT NULL, INDEX | Reference to users table |
| `title` | str | NOT NULL, DEFAULT "New Chat" | Auto-generated after 3 messages via GPT-4o-mini |
| `language_preference` | str | NOT NULL, DEFAULT "auto" | en/ur/auto - affects AI responses |
| `message_count` | int | NOT NULL, DEFAULT 0 | Track for auto-title generation trigger |
| `created_at` | timestamp | NOT NULL, DEFAULT NOW() | Conversation creation time |
| `updated_at` | timestamp | NOT NULL, DEFAULT NOW() | Last activity time |

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for listing user's conversations)
- `idx_conversations_updated_at` on `updated_at` (for sorting by recent activity)

**SQLModel Definition**:

```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(default="New Chat")
    language_preference: str = Field(default="auto")  # en/ur/auto
    message_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
    handoffs: list["AgentHandoff"] = Relationship(back_populates="conversation")
```

**Title Generation Logic** (from clarification):
- Generate title after 3 messages using GPT-4o-mini
- Summarize first 3 messages to create meaningful title
- User can override with custom title

---

### 2. Message

**Purpose**: Represents a single message within a conversation.

**Table Name**: `messages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique message identifier |
| `conversation_id` | UUID | FK, NOT NULL, INDEX | Reference to conversations |
| `correlation_id` | UUID | INDEX | **Distributed tracing ID** - links to structured logs for full request lifecycle |
| `role` | str | NOT NULL | user/assistant/system |
| `content` | str | NOT NULL | Message content (supports UTF-8 for Urdu) |
| `tool_calls` | JSON | NULL | Array of tools invoked by AI with execution metadata |
| `created_at` | timestamp | NOT NULL, DEFAULT NOW() | Message creation time |

**Observability Notes**:
- `correlation_id` enables querying logs to find: (a) the API request that created this message, (b) all MCP tool calls made during processing, (c) agent handoffs that occurred, (d) OpenAI API calls with token usage
- `tool_calls` JSON includes timing data for each tool call, enabling performance analysis

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id` (for loading conversation history)
- `idx_messages_correlation_id` on `correlation_id` (for tracing)

**SQLModel Definition**:

```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    correlation_id: str = Field(index=True)  # For tracing
    role: str = Field(...)  # "user" | "assistant" | "system"
    content: str = Field(...)  # Supports UTF-8 for Urdu text
    tool_calls: Optional[dict] = Field(default=None)  # JSON array of tool invocations
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Tool Calls JSON Schema**:

```json
[
  {
    "tool": "add_task",
    "parameters": {"user_id": "...", "title": "Buy groceries"},
    "result": {"status": "success", "task_id": 123}
  },
  {
    "tool": "semantic_search",
    "parameters": {"user_id": "...", "query": "financial tasks"},
    "result": {"status": "success", "tasks": [...]}
  }
]
```

---

### 3. AgentHandoff

**Purpose**: Tracks agent handoff events for analytics, debugging, and audit trail. Critical for understanding AI behavior in multi-agent systems.

**Table Name**: `agent_handoffs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique handoff identifier |
| `conversation_id` | UUID | FK, NOT NULL, INDEX | Reference to conversations |
| `correlation_id` | UUID | INDEX | **Links to structured logs** for full handoff tracing |
| `from_agent` | str | NOT NULL | Name of agent handing off |
| `to_agent` | str | NOT NULL | Name of agent receiving control |
| `reason` | str | NOT NULL | Why handoff occurred (AI-generated) |
| `timestamp` | timestamp | NOT NULL, DEFAULT NOW() | When handoff happened |
| `context_snapshot` | JSON | NULL | Conversation state at handoff (for debugging) |
| `success` | bool | NOT NULL, DEFAULT true | Whether handoff completed successfully |
| `error_message` | str | NULL | Error details if handoff failed |

**Observability Notes**:
- `correlation_id` enables linking handoffs to the full request lifecycle in logs
- `context_snapshot` stores conversation summary, active tasks, user state at handoff time
- `success` flag tracks failed handoffs for error rate monitoring
- Handoff records provide audit trail for understanding AI decision-making
- Can be queried to analyze: (a) handoff frequency by agent pair, (b) common handoff reasons, (c) failure patterns

**Indexes**:
- `idx_agent_handoffs_conversation_id` on `conversation_id`
- `idx_agent_handoffs_correlation_id` on `correlation_id` (for distributed tracing)
- `idx_agent_handoffs_timestamp` on `timestamp` (for analytics)
- `idx_agent_handoffs_success` on `success` (for error monitoring)

**SQLModel Definition**:

```python
class AgentHandoff(SQLModel, table=True):
    __tablename__ = "agent_handoffs"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    correlation_id: UUID = Field(index=True)  # For distributed tracing
    from_agent: str = Field(...)  # e.g., "TodoAssistant"
    to_agent: str = Field(...)     # e.g., "PlanningAgent"
    reason: str = Field(...)       # e.g., "User asked for weekly planning"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context_snapshot: Optional[dict] = Field(default=None)
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None)

    # Relationships
    conversation: Conversation = Relationship(back_populates="handoffs")
```

**Agent Names** (from spec):
- `TodoAssistant` - Main agent for general commands
- `PlanningAgent` - Specialist for weekly planning and prioritization
- `TaskQueryAgent` - Specialist for complex task searches and filtering

---

## Extended Entities

### 4. Task (Extended from Phase II)

**New Fields** (appended to existing Task model):

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `transcription_text` | str | NULL | Full voice transcription from Whisper API |
| `ai_summary` | str | NULL | LLM-generated summary (< 100 chars) |
| `embedding_id` | str | NULL | Reference to Qdrant vector |

**SQLModel Extension**:

```python
# Extending existing Task model from Phase II
class Task(SQLModel, table=True):
    # ... existing fields ...

    # Phase III: AI Chatbot fields
    transcription_text: Optional[str] = Field(default=None)
    ai_summary: Optional[str] = Field(default=None)  # Max 100 chars
    embedding_id: Optional[str] = Field(default=None)  # Qdrant vector reference
```

**Field Details**:

1. **transcription_text**
   - Stores full voice transcription from Whisper API
   - Set when user creates task via voice command
   - Supports UTF-8 for Urdu transcriptions

2. **ai_summary**
   - Auto-generated for descriptions > 100 characters
   - Maximum 100 characters (spec FR-064)
   - Regenerated when description is updated (spec FR-065)
   - Uses GPT-4o-mini for cost efficiency (spec FR-067)

3. **embedding_id**
   - References Qdrant vector for semantic search
   - Generated from title + description using text-embedding-3-small
   - Created/updated on task create or update (spec FR-034)

---

## Qdrant Collection Schema

### Collection: `tasks`

**Vector Configuration**:
- **Size**: 1536 (text-embedding-3-small)
- **Distance**: COSINE
- **Storage**: Memory (for performance)

**Payload Schema**:

```python
{
    "user_id": "auth|123456",      # Required - for user scoping
    "title": "Buy groceries",       # Required - display text
    "description": "Get milk...",   # Optional - for context
    "completed": false,             # Required - for filtering
    "priority": "HIGH",             # Optional - for sorting
    "due_date": 1707520800          # Optional - Unix timestamp
}
```

**Payload Indexes**:

```python
# Create indexes for filtered fields
await client.create_payload_index(
    collection_name="tasks",
    field_name="user_id",
    field_schema=PayloadSchemaType.KEYWORD,
)

await client.create_payload_index(
    collection_name="tasks",
    field_name="completed",
    field_schema=PayloadSchemaType.KEYWORD,
)

await client.create_payload_index(
    collection_name="tasks",
    field_name="priority",
    field_schema=PayloadSchemaType.KEYWORD,
)
```

---

## Validation Rules

### Conversation

| Field | Validation |
|-------|------------|
| `language_preference` | Must be one of: "en", "ur", "auto" |
| `title` | Max 255 characters |
| `message_count` | Must be >= 0 |

### Message

| Field | Validation |
|-------|------------|
| `role` | Must be one of: "user", "assistant", "system" |
| `content` | Max 50,000 characters (supports UTF-8/Urdu) |
| `correlation_id` | UUID v4 format |

### Task (New Fields)

| Field | Validation |
|-------|------------|
| `transcription_text` | Max 10,000 characters |
| `ai_summary` | Max 100 characters (when generated) |
| `embedding_id` | Alphanumeric string (Qdrant point ID) |

---

## State Transitions

### Conversation States

```
┌─────────────┐     message_count < 3    ┌─────────────────────┐
│   Created   │ ───────────────────────▶ │  Awaiting Title     │
│  (title=""  │                          │  (auto-generate)     │
│  "New Chat") │ ◀─────────────────────── │  (after 3 msgs)     │
└─────────────┘     user sets title      └─────────────────────┘
       │                                    │
       │                                    ▼
       │                           ┌─────────────────────┐
       │                           │    Titled           │
       └───────────────────────────▶│  (user/AI generated) │
                                   └─────────────────────┘
```

### Message Role Transitions

```
┌────────┐   user sends    ┌───────────┐   AI thinks    ┌───────────┐
│  USER  │ ───────────────▶│  SYSTEM   │ ──────────────▶│ ASSISTANT │
│        │                 │(optional) │                 │           │
└────────┘                 └───────────┘                 └───────────┘
     ▲                                                         │
     │                         ┌───────────┐                  │
     └─────────────────────────│  TOOL     │◀─────────────────┘
           AI action           │  CALLS    │
                               └───────────┘
```

---

## Migration Notes

### Phase III Migration

1. **Create new tables**:
   - `conversations`
   - `messages`
   - `agent_handoffs`

2. **Alter existing table**:
   - `tasks` - Add `transcription_text`, `ai_summary`, `embedding_id`

3. **Create Qdrant collection**:
   - Collection name: `tasks`
   - Vector size: 1536
   - Distance: COSINE
   - Payload indexes: `user_id`, `completed`, `priority`

4. **Backfill embeddings**:
   - Generate embeddings for existing tasks
   - Batch upsert to Qdrant
   - Update `embedding_id` in tasks table

---

*Data Model Complete: All entities defined with SQLModel schemas*
