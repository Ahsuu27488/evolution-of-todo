# Phase II Quickstart Guide

**Feature**: 006-phase2-fullstack-webapp
**Date**: 2025-12-29

---

## Prerequisites

- Node.js 18+ (for Next.js frontend)
- Python 3.13+ (for FastAPI backend)
- UV package manager (`pip install uv`)
- Neon DB account with a project created

---

## 1. Get Your Neon DB Connection String

1. Go to https://console.neon.tech
2. Select your project (or create one)
3. Click **Dashboard** → **Connection Details**
4. Click **Copy** on the connection string
5. It should look like:
   ```
   postgresql://username:password@ep-xxxxx-xxxxxx.region.aws.neon.tech/neondb?sslmode=require
   ```

---

## 2. Backend Setup (FastAPI + SQLModel)

### 2.1 Navigate to Backend Directory
```bash
cd /home/ahsan/Dev/Hackathons/Hackathon-II/evolution-of-todo/backend
```

### 2.2 Create Virtual Environment
```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 2.3 Install Dependencies
```bash
uv pip install fastapi uvicorn sqlmodel python-dotenv pyjwt psycopg2-binary
```

Or create `requirements.txt`:
```txt
fastapi>=0.109.0
uvicorn>=0.27.0
sqlmodel>=0.0.14
python-dotenv>=1.0.0
pyjwt>=2.8.0
psycopg2-binary>=2.9.9
```

Then:
```bash
uv pip install -r requirements.txt
```

### 2.4 Create Environment File
```bash
# backend/.env
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-super-secret-key-at-least-32-characters-long
CORS_ORIGINS=http://localhost:3000
```

### 2.5 Run Backend
```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

API docs at: http://localhost:8000/docs

---

## 3. Frontend Setup (Next.js + shadcn/ui)

### 3.1 Navigate to Frontend Directory
```bash
cd /home/ahsan/Dev/Hackathons/Hackathon-II/evolution-of-todo/frontend
```

### 3.2 Create Next.js App (if not exists)
```bash
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
```

### 3.3 Install Dependencies
```bash
npm install better-auth @neondatabase/serverless
npm install zod react-hook-form @hookform/resolvers
npm install lucide-react sonner
```

### 3.4 Initialize shadcn/ui
```bash
npx shadcn@latest init
```

Select:
- Style: Default
- Base color: Slate (or your preference)
- CSS variables: Yes

### 3.5 Add Required Components
```bash
npx shadcn@latest add button card checkbox dialog \
  alert-dialog form input label textarea \
  dropdown-menu sonner skeleton
```

### 3.6 Create Environment File
```bash
# frontend/.env.local
DATABASE_URL=postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-super-secret-key-at-least-32-characters-long
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Important**: `BETTER_AUTH_SECRET` must be identical in both frontend and backend!

### 3.7 Run Frontend
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## 4. Verify Setup

### 4.1 Check Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}
```

### 4.2 Check API Docs
Open http://localhost:8000/docs in browser.

### 4.3 Check Frontend
Open http://localhost:3000 in browser.

---

## 5. Project Structure After Setup

```
evolution-of-todo/
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   └── ui/          # shadcn components
│   ├── lib/
│   │   ├── auth.ts      # Better Auth config
│   │   └── utils.ts     # cn() helper
│   ├── .env.local
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── db.py
│   │   ├── auth.py
│   │   └── routes/
│   │       └── tasks.py
│   ├── .env
│   └── requirements.txt
│
└── specs/
    └── 006-phase2-fullstack-webapp/
```

---

## 6. Common Issues

### Issue: "DATABASE_URL environment variable is not set"
**Solution**: Ensure `.env` file exists and is in the correct directory.

### Issue: CORS errors in browser
**Solution**: Check `CORS_ORIGINS` in backend `.env` matches frontend URL exactly.

### Issue: "Invalid token" on API requests
**Solution**: Ensure `BETTER_AUTH_SECRET` is identical in both `.env` files.

### Issue: Neon connection timeout
**Solution**: Check connection string format includes `?sslmode=require`.

### Issue: shadcn components not found
**Solution**: Run `npx shadcn@latest add <component-name>` for each needed component.

---

## 7. Development Workflow

### Start Both Services
```bash
# Terminal 1: Backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Test API Manually
```bash
# Create task (replace TOKEN with actual JWT)
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Testing"}'
```

---

## 8. Next Steps

After setup is complete:

1. Run `/sp.tasks` to generate implementation tasks
2. Run `/sp.implement` to execute tasks
3. Test all CRUD operations
4. Deploy to Vercel (frontend) and Railway (backend)
5. Submit to hackathon

---

## Environment Variables Summary

| Variable | Frontend | Backend | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✓ | ✓ | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | ✓ | ✓ | Shared JWT secret (must match!) |
| `NEXT_PUBLIC_API_URL` | ✓ | - | Backend URL for frontend |
| `CORS_ORIGINS` | - | ✓ | Allowed frontend origins |
