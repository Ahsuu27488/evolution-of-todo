# Evolution of Todo — Hackathon II

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15.2.8-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-teal)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-Agents_SDK-green)](https://platform.openai.com/docs/agents)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A full-stack todo application demonstrating **Spec-Driven Development** across 5 evolutionary phases, from a simple console app to an **AI-powered chatbot with natural language task management**, deployed with Kubernetes on Oracle Cloud.

## 🚀 Live Demo

**Frontend**: https://chronos.ahsandev.site

## Project Phases

| Phase | Status | Description | Documentation |
|-------|--------|-------------|---------------|
| **Phase I** | ✅ Complete | In-memory Python console app | [`src/README.md`](src/README.md) |
| **Phase II** | ✅ Complete | Full-stack web application | [`backend/README.md`](backend/README.md) · [`frontend/README.md`](frontend/README.md) |
| **Phase III** | ✅ Complete | **AI-powered chatbot with OpenAI Agents SDK** | [`specs/012-ai-chatbot-phase3/README.md`](specs/012-ai-chatbot-phase3/README.md) |
| **Phase IV** | ✅ Complete | Local Kubernetes deployment (Minikube/Helm) | [`docs/phase4/README.md`](docs/phase4/README.md) |
| **Phase V** | ✅ Complete | Oracle OKE cloud deployment (Kafka/Dapr) | [`docs/phase5/README.md`](docs/phase5/README.md) |

---

## ✨ Phase III: Meet **Chronos** — Your AI Time Guardian

> *"Named after Chronos, the Greek personification of time — I am the guardian of your productivity and the keeper of your schedule."*

Phase III introduces **Chronos**, an intelligent AI assistant that transforms task management through natural conversation. Built with the **OpenAI Agents SDK** and **Model Context Protocol (MCP)**, Chronos represents the cutting edge of agentic AI technology.

### 🤖 Who is Chronos?

**Chronos** is not just another chatbot — it's a **multi-agent system** with a distinct personality and specialized capabilities:

| Attribute | Description |
|-----------|-------------|
| **Name** | Chronos (Greek: Χρόνος — personification of time) |
| **Role** | Time Guardian & Productivity Assistant |
| **Personality** | Warm but efficient, proactive, celebrates wins, mindful of work-life balance |
| **Languages** | Fluent in English and Urdu (اردو) — detects and responds in user's language |
| **Specialists** | Planning Agent (weekly scheduling), Query Agent (semantic search) |
| **Core Technology** | OpenAI Agents SDK + MCP Tools + gpt-4o-mini + Whisper API |

### 🌟 Chronos's Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHRONOS AI ASSISTANT                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │   TodoAgent  │  │ PlanningAgent│  │     QueryAgent         │ │
│  │   (Chronos)  │◄─┤   (Specialist)│   │    (Specialist)       │ │
│  │              │  │  - Weekly    │  │  - Semantic Search     │ │
│  │  - Main      │  │    Planning  │  │  - Complex Filters     │ │
│  │    Interface │  │  - Priority  │  │  - Task Discovery      │ │
│  │  - Handoffs  │  │    Mgmt     │  │                        │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP TOOLS (7 Tools)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ add_task │ │list_tasks│ │complete  │ │delete_task│           │
│  └──────────┘ └──────────┘ │_task     │ └──────────┘           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                         │
│  │update_task│ │ get_task │ │semantic  │                         │
│  │          │ │          │ │_search   │                         │
│  └──────────┘ └──────────┘ └──────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### 🎙️ Voice Input & Transcription

Chronos understands spoken commands through **Whisper API** integration:
- **30-second recording limit** — Quick voice memos
- **Urdu biasing** — Prevents Devanagari output for Urdu speakers
- **Ambiguity confirmation** — Asks for clarification when transcription is unclear
- **Multi-language support** — English, Urdu script (اردو), and Roman Urdu

### 🔍 Semantic Search (Vector Embeddings)

Unlike traditional keyword search, Chronos uses **Qdrant vector database** with OpenAI embeddings:
- **Search by meaning**: "grocery items" finds tasks with "buy milk", "eggs", "bread"
- **Topic discovery**: "work tasks" finds all professional-related items
- **User-scoped**: No cross-user data leakage
- **Circuit breaker**: Falls back to keyword search if Qdrant unavailable

### 🌐 Bilingual English/Urdu Support

Chronos is truly bilingual:

| Language | Support | Examples |
|----------|---------|----------|
| **English** | Full | "Add task", "Show pending", "Complete task 5" |
| **Urdu Script** (اردو) | Full with RTL | "ٹاسک شامل کرو", "میرے ٹاسکس دکھاؤ", "مکمل کر دیں" |
| **Roman Urdu** | Full | "Task add karo", "Mere tasks dikhao", "Complete kar do" |
| **Code-Switching** | Partial | "Add a task for آج" → Responds in dominant language |

---

## Phase IV & V: Kubernetes Deployment

### Cloud Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Kubernetes** | Minikube (local), Oracle OKE (cloud) | Container orchestration |
| **Helm** | Chart-based package management | Deployment automation |
| **Dapr** | Distributed Application Runtime | Service mesh, pub/sub, state |
| **Redpanda** | Kafka-compatible event streaming | Task events, reminders |
| **Docker** | Container images | `ahsandev/chronos-frontend`, `ahsandev/chronos-backend` |

### Deployment Artifacts

```
helm/chronos-todo/          # Helm chart
├── Chart.yaml
├── values.yaml             # Configuration (excluded from git - contains secrets)
├── templates/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── redpanda-deployment.yaml
│   ├── dapr-pubsub.yaml
│   └── secret.yaml
scripts/
├── deploy-minikube.sh       # Local K8s deployment
└── deploy-oracle.sh         # Oracle OKE cloud deployment
```

### Quick Deploy

**Minikube (Local):**
```bash
./scripts/deploy-minikube.sh
```

**Oracle OKE (Production):**
```bash
./scripts/deploy-oracle.sh
```

See [`DEPLOYMENT-GUIDE.md`](DEPLOYMENT-GUIDE.md) for full deployment instructions.

---

## Quick Overview

```
evolution-of-todo/
├── src/                    # Phase I: Console App
├── backend/                # Phase II: FastAPI Backend
│   ├── app/
│   │   ├── ai/             # Phase III: OpenAI Agents + MCP
│   │   ├── dapr/           # Phase V: Dapr client
│   │   └── routes/         # API endpoints
│   └── Dockerfile         # Phase IV/V: Container image
├── frontend/               # Phase II: Next.js Frontend
│   ├── app/                # Next.js App Router
│   ├── components/         # React components
│   ├── lib/
│   │   ├── dapr/           # Phase V: Dapr client
│   │   └── api/            # API client
│   └── Dockerfile         # Phase IV/V: Container image
├── helm/                   # Phase IV/V: Kubernetes Helm charts
├── scripts/                # Deployment scripts
└── docs/phase4/, phase5/   # Deployment documentation
```

## Tech Stack

### Phase II (Full-Stack Web App)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 15.2.8 | App Router, Server Components |
| **Frontend** | React 19.2.3 | UI framework |
| **Frontend** | TypeScript 5+ | Type safety |
| **Frontend** | Tailwind CSS v4 | Styling |
| **Frontend** | shadcn/ui | Component library |
| **Frontend** | TanStack Query 5+ | Server state |
| **Frontend** | Zustand 5+ | Client state |
| **Frontend** | Better Auth 1.4.9 | Authentication |
| **Backend** | FastAPI 0.115+ | REST API |
| **Backend** | SQLModel 0.21+ | ORM |
| **Backend** | Python 3.13+ | Runtime |
| **Database** | Neon PostgreSQL | Serverless Postgres |
| **Auth** | JWT (HS256) | Shared secret auth |

### Phase III (AI Chatbot) ⭐

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Framework** | OpenAI Agents SDK | Multi-agent system |
| **Model** | gpt-4o-mini | Main chat model |
| **Embeddings** | text-embedding-3-small | Vector search (1536 dims) |
| **Voice** | Whisper API (whisper-1) | Audio transcription |
| **Vector DB** | Qdrant Cloud | Semantic search storage |
| **MCP Protocol** | Official MCP SDK | Tool calling interface |
| **Language Detection** | langdetect | English/Urdu detection |
| **Logging** | structlog | Structured JSON logging |
| **Rate Limiting** | slowapi | Per-user API limits |

### Phase IV & V (Kubernetes) 🚀

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | Kubernetes | Container management |
| **Package Manager** | Helm | Deployment automation |
| **Service Mesh** | Dapr | Pub/sub, state, secrets |
| **Event Streaming** | Redpanda | Kafka-compatible broker |
| **Cloud** | Oracle OKE | Production deployment |

---

## Quick Start (Local Development)

### Prerequisites

- **Node.js** 20+
- **Python** 3.13+
- **Neon** DB account ([sign up free](https://neon.tech))
- **UV** package manager (recommended) or pip

### 1. Clone the Repository

```bash
git clone https://github.com/Ahsuu27488/evolution-of-todo.git
cd evolution-of-todo
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `backend/.env`:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require

# Authentication
BETTER_AUTH_SECRET=your-32-character-secret-here
CORS_ORIGINS=http://localhost:3000

# Phase III: AI Features
OPENAI_API_KEY=sk-your-openai-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Feature Flags
PHASE_III_ENABLED=true
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```env
# Database (shared with backend)
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require

# Authentication (MUST match backend!)
BETTER_AUTH_SECRET=your-32-character-secret-here
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI (for chatbot)
OPENAI_API_KEY=sk-your-openai-api-key
```

> **⚠️ Important:** `BETTER_AUTH_SECRET` must be **identical** in both `backend/.env` and `frontend/.env.local`!

### 4. Run Development Servers

**Terminal 1 — Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/api/health |

---

## Development

### Spec-Driven Development

This project uses **Spec-Driven Development** with:

- **Spec-Kit Plus** for specification management
- **Claude Code** for AI-assisted development
- **MCP Servers** for context-aware tooling

### Documentation Structure

- `specs/` — Feature specifications (spec, plan, tasks)
- `history/prompts/` — Prompt History Records (PHRs)
- `history/adr/` — Architecture Decision Records
- `.claude/skills/` — Reusable intelligence

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with Spec-Driven Development using Claude Code*
