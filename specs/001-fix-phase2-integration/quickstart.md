# Quickstart Guide: Phase II Development Setup

**Feature**: 001-fix-phase2-integration
**Date**: 2026-01-06

## Prerequisites

- **Node.js**: 18+ installed
- **Python**: 3.13+ installed
- **UV**: Latest version installed
- **NeonDB Account**: Free account at https://neon.tech
- **Git**: For version control

---

## Step 1: Clone and Navigate

```bash
cd /home/ahsan/Dev/Hackathons/Hackathon-II/evolution-of-todo
```

---

## Step 2: NeonDB Setup

1. **Create NeonDB Project**:
   - Go to https://neon.tech
   - Create a new project
   - Copy the connection string

2. **Set DATABASE_URL**:
   ```bash
   # Format (replace with your actual values)
   postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
   ```

---

## Step 3: Backend Setup

```bash
cd backend

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=your-neon-db-url-here?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-here
CORS_ORIGINS=http://localhost:3000
EOF

# Generate a secure secret
python -c "import secrets; print(f'BETTER_AUTH_SECRET={secrets.token_urlsafe(32)}')"
```

**Test Backend**:
```bash
# Run database connection test
python neondb_test.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Expected output: `INFO: Uvicorn running on http://0.0.0.0:8000`

---

## Step 4: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << 'EOF'
DATABASE_URL=your-neon-db-url-here?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-here  # MUST MATCH BACKEND!
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

**Important**: `BETTER_AUTH_SECRET` must be **identical** in both `.env` files!

**Test Frontend**:
```bash
# Build frontend (check for errors)
npm run build

# Start development server
npm run dev
```

Expected output: `ready - started server on 0.0.0.0:3000`

---

## Step 5: Verify Integration

### 5.1 Database Connection

```bash
cd backend
python neondb_test.py
```

Expected: `✅ Database connection successful!`

### 5.2 Backend API

Open http://localhost:8000/docs in your browser.

You should see the FastAPI automatic documentation with all task endpoints.

### 5.3 Frontend Application

1. Open http://localhost:3000
2. Click "Sign Up"
3. Enter email and password
4. Submit form

Expected: You should be redirected to the dashboard.

### 5.4 Create Task Test

1. On the dashboard, click "Add Task"
2. Enter a title
3. Submit

Expected: Task appears in the list and persists after refresh.

---

## Environment Variable Reference

| Variable | Frontend | Backend | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | ✅ | Neon PostgreSQL connection (same DB) |
| `BETTER_AUTH_SECRET` | ✅ | ✅ | JWT signing secret (MUST match!) |
| `BETTER_AUTH_URL` | ✅ | ❌ | Frontend URL for JWKS |
| `NEXT_PUBLIC_API_URL` | ✅ | ❌ | Backend API base URL |
| `CORS_ORIGINS` | ❌ | ✅ | Allowed frontend origins |

---

## Common Issues and Fixes

### Issue: "Database connection failed"

**Fix**: Ensure `DATABASE_URL` includes `?sslmode=require`

```bash
# Correct
DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/db?sslmode=require

# Wrong (will fail)
DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/db
```

### Issue: "401 Unauthorized" on API calls

**Fix**: Verify `BETTER_AUTH_SECRET` is identical in both `.env` files

```bash
# backend/.env
echo $BETTER_AUTH_SECRET

# frontend/.env.local
echo $BETTER_AUTH_SECRET

# These must output the same value!
```

### Issue: "CORS error" in browser console

**Fix**: Ensure `CORS_ORIGINS` in backend includes the frontend URL

```bash
# backend/.env
CORS_ORIGINS=http://localhost:3000
```

### Issue: "Module not found" errors

**Fix**: Reinstall dependencies

```bash
# Backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Development Workflow

### Running Both Services

Terminal 1 (Backend):
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### Testing the Full Flow

1. Open http://localhost:3000
2. Sign up as a new user
3. Create a task
4. Refresh the page (task should persist)
5. Mark task as complete
6. Delete the task

---

## File Structure Reference

```
evolution-of-todo/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # SQLModel models
│   │   ├── db.py                # Database connection
│   │   ├── jwt_middleware.py    # JWT verification
│   │   └── routes/
│   │       └── tasks.py         # Task endpoints
│   ├── .env                     # Backend env vars
│   └── .venv/                   # Python virtual env
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/             # Login/signup pages
│   │   ├── dashboard/          # Protected dashboard
│   │   ├── actions/            # Server Actions
│   │   └── api/auth/           # Better Auth API
│   ├── components/             # UI components
│   ├── lib/                    # Utilities & API client
│   └── .env.local              # Frontend env vars
│
├── src/                        # Phase I console app (unchanged)
└── specs/                      # Feature specifications
```

---

## Next Steps After Setup

1. ✅ Backend and frontend both running
2. ✅ Can sign up and log in
3. ✅ Tasks persist in database
4. ✅ JWT authentication working

**Proceed to**: `/sp.tasks` to generate implementation tasks.
