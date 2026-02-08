---
title: Evolution of Todo API
emoji: ⚡
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Chronos Todo API Backend

FastAPI REST API serving the Evolution of Todo application with comprehensive task management, multi-channel notifications, and AI-powered chatbot.

## Version: 3.0.0 (Phase III)

Current implementation includes:
- **Phase II**: Full-stack web API with task CRUD, notifications, and authentication
- **Phase III**: AI chatbot with OpenAI Agents SDK, semantic search, and voice transcription

---

## Tech Stack

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.13+ | Runtime environment (strict requirement) |
| **FastAPI** | 0.109+ | REST API framework with async support |
| **Uvicorn** | 0.27+ | ASGI server |
| **Pydantic** | 2.0+ | Request/response validation |

### Database & ORM
| Technology | Purpose |
|------------|---------|
| **PostgreSQL** (via Neon) | Primary database with JSONB support |
| **SQLModel** | ORM with Pydantic integration |
| **asyncpg** | Async PostgreSQL driver |
| **SQLAlchemy** | Core ORM engine (async) |

### Authentication
| Technology | Purpose |
|------------|---------|
| **Better Auth** | Frontend JWT authentication |
| **python-jose** | JWT token verification |
| **bcrypt** (3.2.2) | Password hashing |
| **passlib** | Password hashing abstraction |

### Notification System
| Technology | Purpose |
|------------|---------|
| **sse-starlette** | Server-Sent Events for real-time updates |
| **pywebpush** | Web Push API for browser notifications |
| **resend** | Email delivery service |
| **svix** | Webhook signature verification |

### AI & Phase III Features
| Technology | Purpose |
|------------|---------|
| **openai-agents** | OpenAI Agents SDK for multi-agent chatbot |
| **openai** | OpenAI API client (gpt-4o-mini, text-embedding-3-small, whisper-1) |
| **mcp** | Model Context Protocol SDK for tools |
| **qdrant-client** | Vector database client for semantic search |
| **structlog** | Structured JSON logging |
| **langdetect** | Language detection (Urdu/English) |
| **aiofiles** | Async file operations for audio |

### Other Dependencies
| Technology | Purpose |
|------------|---------|
| **httpx** | Async HTTP client |
| **python-dotenv** | Environment variable loading |
| **slowapi** | Rate limiting |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app entry point
│   ├── db.py                        # Database session management
│   ├── models.py                    # Core data models (Task, User, Tag)
│   ├── errors.py                    # Error handlers and custom exceptions
│   ├── simple_auth.py               # JWT auth utilities
│   │
│   ├── routes/                      # API endpoints
│   │   ├── auth.py                  # Authentication (signup, signin, me)
│   │   ├── tasks.py                 # Task CRUD operations
│   │   ├── notifications.py         # Notification endpoints
│   │   └── chat.py                  # AI chatbot & transcription (Phase III)
│   │
│   ├── services/                    # Business logic
│   │   ├── notification_service.py  # Notification CRUD & dispatch
│   │   ├── sse_service.py           # SSE streaming
│   │   ├── push_service.py          # Web Push API
│   │   ├── email_service.py         # Resend email delivery
│   │   ├── scheduler_service.py     # Background digest jobs
│   │   ├── unsubscribe_service.py   # One-click unsubscribe
│   │   └── migration.py             # DB migration utilities
│   │
│   ├── models/                      # Database models
│   │   ├── notification.py          # Notification, NotificationPreference
│   │   ├── push_subscription.py     # Push subscription management
│   │   └── email_delivery_log.py    # Email delivery tracking
│   │
│   ├── ai/                          # Phase III: AI Chatbot
│   │   ├── agents/
│   │   │   ├── todo_agent.py        # Main TodoAgent + specialists
│   │   │   └── context.py            # Agent execution context
│   │   ├── models/
│   │   │   ├── conversation.py      # Chat session model
│   │   │   ├── message.py           # Message model with tool calls
│   │   │   ├── conversation_preference.py  # User chat settings
│   │   │   └── agent_handoff.py     # Agent transfer tracking
│   │   ├── services/
│   │   │   ├── openai_client.py     # OpenAI API (chat, embeddings, Whisper)
│   │   │   ├── qdrant_client.py     # Vector database client
│   │   │   └── runner_service.py    # Agent execution with streaming
│   │   ├── mcp/
│   │   │   ├── tools.py             # MCP tool implementations (task operations)
│   │   │   └── server.py            # MCP server instance
│   │   ├── utils/
│   │   │   ├── logging.py           # Structured logging with correlation
│   │   │   ├── language.py          # Urdu/English detection
│   │   │   ├── sanitize.py          # Prompt injection prevention
│   │   │   └── nlp.py               # NLP utilities
│   │   ├── rate_limit.py            # Per-user rate limiting
│   │   └── middleware.py            # Correlation ID middleware
│   │
│   └── __init__.py
│
├── tests/                           # Test suite
│   ├── conftest.py
│   └── test_mcp/
│       └── test_tools.py
│
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

---

## Features

### Phase I: Core Task Management
- Create, read, update, delete tasks
- Task filtering by status, priority, tags
- Task search with pagination
- Recurring tasks (daily, weekly, monthly)
- Audit logging for all task modifications

### Phase II: Full-Stack Web Application
- JWT authentication with Better Auth
- Multi-channel notifications (in-app, email, push)
- Real-time updates via SSE
- Daily/weekly digest emails
- One-click unsubscribe (RFC 8058)
- User timezone support

### Phase III: AI Chatbot
- **Natural Language Task Management**: Add, complete, update tasks via chat
- **Multi-Agent Architecture**: TodoAgent, PlanningAgent, QueryAgent
- **Semantic Search**: Vector-based task search using embeddings
- **Voice Input**: Audio transcription via Whisper API
- **Bilingual Support**: English and Urdu (Roman + script)
- **Streaming Responses**: Token-by-token SSE streaming
- **Tool Calling**: AI can invoke task management operations
- **Conversation Management**: Persistent chat history with title generation

---

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Create new user account |
| POST | `/signin` | Sign in with email/password |
| GET | `/me` | Get current user profile |
| PUT | `/profile` | Update user profile |

### Tasks (`/api/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List tasks with filtering |
| POST | `/` | Create new task |
| GET | `/{task_id}` | Get task details |
| PUT | `/{task_id}` | Update task |
| DELETE | `/{task_id}` | Delete task |
| POST | `/{task_id}/complete` | Toggle task completion |
| GET | `/{task_id}/logs` | Get task audit logs |

### Notifications (`/api/notifications`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List notifications |
| PUT | `/{id}/read` | Mark as read |
| PUT | `/read-all` | Mark all as read |
| GET | `/settings` | Get notification preferences |
| PUT | `/settings` | Update preferences |
| GET | `/stream` | SSE notification stream |
| POST | `/push/subscribe` | Subscribe to push notifications |
| DELETE | `/push/unsubscribe` | Unsubscribe from push |
| POST | `/email/unsubscribe` | One-click email unsubscribe |

### Chat (Phase III) (`/api/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Send chat message (SSE streaming) |
| POST | `/transcribe` | Transcribe audio file |
| GET | `/conversations` | List conversations |
| GET | `/conversations/{id}` | Get conversation with messages |
| DELETE | `/conversations/{id}` | Delete conversation |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check with DB/Qdrant status |
| GET | `/` | Root endpoint with API info |
| GET | `/docs` | Interactive API documentation (Swagger) |

---

## Environment Variables

### Required
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Authentication
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
```

### Phase III: AI Features
```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_WHISPER_MODEL=whisper-1

# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Features
PHASE_III_ENABLED=true
MAX_MESSAGE_LENGTH=5000
MAX_AUDIO_SIZE_MB=25
```

### Notification System
```bash
# Resend Email
RESEND_API_KEY=re_...

# Web Push (generate with: openssl ecparam -name prime256v1 -genkey -noout -out vapid.pem)
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_PUBLIC_KEY=your-vapid-public-key

# Webhook Secret (for Resend webhooks)
WEBHOOK_SECRET=your-webhook-secret

# Frontend URL (for unsubscribe links)
FRONTEND_URL=http://localhost:3000
```

### CORS
```bash
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Running Locally

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Run Database Migrations
```bash
python -c "import asyncio; from app.db import create_db_and_tables; asyncio.run(create_db_and_tables())"
```

### 4. Start Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

---

## Database Schema

### Core Tables
- **users**: User accounts (managed by Better Auth)
- **tasks**: Task items with JSONB tags and metadata
- **tags**: Tag definitions with colors
- **task_logs**: Audit trail for task modifications

### Notification Tables
- **notifications**: Notification records with delivery tracking
- **notification_preferences**: Per-user notification settings
- **push_subscriptions**: Browser push subscription data
- **email_delivery_logs**: Email delivery status tracking

### Phase III Tables
- **conversations**: Chat sessions with message history
- **messages**: Individual messages with tool call tracking
- **conversation_preferences**: User chat settings
- **agent_handoffs**: Agent transfer audit trail

---

## AI Chatbot Features

### Agent Architecture
```
User Message
    │
    ▼
TodoAgent (Main)
    │
    ├── PlanningAgent (weekly planning, prioritization)
    └── QueryAgent (semantic search, complex filtering)
```

### Tool Calling
The AI agent can invoke these MCP tools:
- `add_task`: Create task with auto-tag extraction
- `list_tasks`: List tasks with filters
- `complete_task`: Mark task as complete
- `update_task`: Modify task properties
- `delete_task`: Remove task
- `get_task`: Get task details
- `semantic_search`: Vector-based task search

### Semantic Search
- Uses OpenAI text-embedding-3-small (1536 dimensions)
- Stored in Qdrant vector database
- User-scoped search (no cross-user data leakage)
- Falls back to keyword search if Qdrant unavailable

### Voice Input (Whisper)
- Supports: mp3, mp4, mpeg, mpga, m4a, wav, webm
- Max file size: 25 MB
- Auto-detects language (English/Urdu)
- Urdu biasing prevents Devanagari output

### Language Support
- **English**: Full support
- **Urdu Script** (اردو): Full support with RTL rendering
- **Roman Urdu**: Transliterated Urdu supported
- **Code-Switching**: Mixed English-Urdu detected

---

## Background Jobs (Scheduler)

The scheduler runs these periodic tasks:

| Job | Schedule | Description |
|-----|----------|-------------|
| Daily Digest | 8 AM user time | Email summary of pending tasks |
| Weekly Summary | Monday 9 AM user time | Weekly task overview |
| Task Reminders | Every 15 min | Tasks due within 24 hours |
| Cleanup | Daily 2 AM UTC | Soft-delete old notifications |

---

## Architecture Patterns

### Async/Await Throughout
All database operations and external API calls use async/await for non-blocking I/O.

### Dependency Injection
FastAPI dependencies handle authentication and database sessions:
- `get_current_user_id`: Extracts user from JWT
- `get_session`: Provides database session

### Error Handling
- 404 not 403 for ownership checks (prevents ID enumeration)
- Structured error responses with correlation IDs
- Circuit breakers for external API failures

### Correlation ID Tracking
Every request gets a unique correlation ID for distributed tracing across:
- API calls
- MCP tool invocations
- Agent handoffs
- External API calls

---

## Security Features

### Authentication
- JWT signed with BETTER_AUTH_SECRET
- HS256 algorithm
- `sub` claim contains user ID
- Token extracted from `Authorization: Bearer <token>` header

### Rate Limiting
- 30 requests/minute per user (default)
- 10 req/min for transcription (expensive)
- Sliding window algorithm
- Returns 429 with `Retry-After` header

### Input Sanitization
- Prompt injection detection
- Max message length: 5000 characters
- System instruction redaction from outputs

### Data Isolation
- All queries scoped to user_id
- Vector search scoped to user_id
- 404 instead of 403 for ownership verification

---

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_mcp/test_tools.py
```

---

## Deployment

### Environment Variables for Production
- Set `DEBUG=false`
- Use strong `BETTER_AUTH_SECRET` (32+ chars)
- Configure `CORS_ORIGINS` for production domain
- Set `DATABASE_URL` to production PostgreSQL
- Configure `QDRANT_URL` for vector search
- Set `RESEND_API_KEY` for emails

### Health Checks
- `/api/health` returns status of database and Qdrant
- Use for load balancer health checks
- Returns 503 if any critical service is down

---

## Troubleshooting

### "OPENAI_API_KEY not found"
Phase III features require OpenAI API key. Set `OPENAI_API_KEY` in `.env`.

### "Qdrant connection failed"
Semantic search requires Qdrant. Set `QDRANT_URL` and `QDRANT_API_KEY`.

### "CORS error"
Add your frontend URL to `CORS_ORIGINS` in `.env`.

### "Rate limit exceeded"
Wait for the `Retry-After` seconds before retrying.

---

## Data Migration

### Legacy User Name Migration

The backend includes a migration service for migrating legacy single-name users to the new first_name/last_name schema:

**Migration Script**:
```bash
# Check migration status
python backend/scripts/migrate_users.py --status

# Preview changes (dry-run)
python backend/scripts/migrate_users.py --dry-run

# Run migration
python backend/scripts/migrate_users.py
```

**Migration Strategy**:
- Legacy `name` value becomes `first_name`
- `last_name` set to `NULL` (supports mononyms)
- Batch processing (100 users per batch)
- Zero-downtime with rollback safety
- Progress monitoring and integrity checks

---

## License

Part of the Evolution of Todo hackathon project.
