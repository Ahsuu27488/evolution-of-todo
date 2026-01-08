# Evolution of Todo - Hackathon II

Full-stack todo application built with **Spec-Driven Development** demonstrating the evolution from a simple console app to a multi-user web application.

## Project Phases

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase I** | ✅ Complete | In-memory Python console app |
| **Phase II** | ✅ Complete | Full-stack web application |
| Phase III | ⏳ Pending | AI-powered chatbot |
| Phase IV | ⏳ Pending | Local Kubernetes deployment |
| Phase V | ⏳ Pending | Advanced cloud deployment |

---

## Phase II: Full-Stack Web Application

A modern, multi-user todo application with authentication and persistent storage.

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16+ (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, SQLModel, Python 3.13+ |
| **Database** | Neon Serverless PostgreSQL |
| **Auth** | Better Auth with JWT |

### Features

- ✅ User registration and authentication
- ✅ Task CRUD (Create, Read, Update, Delete)
- ✅ Mark tasks complete/incomplete
- ✅ Data isolation between users
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Optimistic UI updates
- ✅ Toast notifications

### Quick Start

#### Prerequisites

- Node.js 18+
- Python 3.13+
- Neon DB account ([sign up free](https://neon.tech))

#### 1. Clone and Setup

```bash
cd evolution-of-todo
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Neon DATABASE_URL and BETTER_AUTH_SECRET
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with your DATABASE_URL and BETTER_AUTH_SECRET
```

#### 4. Configure Environment Variables

**backend/.env:**
```env
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-here
CORS_ORIGINS=http://localhost:3000
```

**frontend/.env.local:**
```env
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> **Important:** `BETTER_AUTH_SECRET` must be identical in both files!

#### 5. Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### 6. Access the Application

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Project Structure

```
evolution-of-todo/
├── frontend/                    # Next.js 16+ App Router
│   ├── app/
│   │   ├── (auth)/             # Auth pages (login, signup)
│   │   ├── dashboard/          # Protected dashboard
│   │   ├── actions/            # Server Actions
│   │   └── api/auth/           # Better Auth routes
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── auth/               # Auth forms
│   │   ├── tasks/              # Task components
│   │   └── layout/             # Header, UserNav
│   ├── lib/
│   │   ├── auth.ts             # Better Auth config
│   │   ├── api.ts              # API client
│   │   └── validations/        # Zod schemas
│   └── types/                  # TypeScript types
│
├── backend/                     # FastAPI + SQLModel
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── models.py           # SQLModel models
│   │   ├── db.py               # Database connection
│   │   ├── auth.py             # JWT verification
│   │   └── routes/
│   │       └── tasks.py        # Task endpoints
│   └── requirements.txt
│
├── specs/                       # Specification documents
│   └── 006-phase2-fullstack-webapp/
│       ├── spec.md             # Requirements
│       ├── plan.md             # Technical design
│       ├── tasks.md            # Implementation tasks
│       └── contracts/
│           └── openapi.yaml    # API contract
│
└── src/                         # Phase I console app
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/{user_id}/tasks` | List user's tasks |
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks/{id}` | Get task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

---

## Phase I: Console Application

An in-memory Python todo application with 9 features.

### Running Phase I

```bash
# Start with empty task list
python3 src/main.py

# Start with demo data
python3 src/main.py --demo
```

### Phase I Features

- Add, view, update, delete tasks
- Mark complete/incomplete
- Priorities (HIGH/MEDIUM/LOW)
- Tags/categories
- Search and filter
- Sort by various fields

---

## Development

### Spec-Driven Development

This project uses **Spec-Driven Development** with:

- **Spec-Kit Plus** for specification management
- **Claude Code** for AI-assisted development
- **AGENTS.md** for cross-agent coordination

### Documentation

- `specs/` - Feature specifications
- `history/prompts/` - Prompt History Records
- `history/adr/` - Architecture Decision Records
- `.claude/skills/` - Reusable intelligence

---

## License

Hackathon II Project - Panaversity

---

*Built with Spec-Driven Development using Claude Code*
