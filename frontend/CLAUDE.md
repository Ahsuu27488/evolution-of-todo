# Frontend Guidelines

## Stack
- Next.js 16+ (App Router)
- TypeScript 5+
- React 18+
- Tailwind CSS
- shadcn/ui components
- Better Auth (authentication)
- Zod (validation)
- React Hook Form

## Project Structure
```
frontend/
├── app/
│   ├── (auth)/                 # Auth route group (unauthenticated)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── signup/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── dashboard/
│   │   ├── page.tsx            # Task list (Server Component)
│   │   └── loading.tsx         # Skeleton loader
│   ├── actions/
│   │   └── tasks.ts            # Server Actions for task CRUD
│   ├── api/
│   │   └── auth/
│   │       └── [...all]/
│   │           └── route.ts    # Better Auth API routes
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Landing → redirect to login/dashboard
│   └── providers.tsx           # Client-side providers (Toaster)
├── components/
│   ├── ui/                     # shadcn/ui components
│   ├── auth/
│   │   ├── login-form.tsx
│   │   └── signup-form.tsx
│   ├── tasks/
│   │   ├── task-card.tsx
│   │   ├── task-list.tsx
│   │   ├── task-form.tsx
│   │   ├── task-actions.tsx
│   │   └── empty-state.tsx
│   └── layout/
│       ├── header.tsx
│       └── user-nav.tsx
├── lib/
│   ├── auth.ts                 # Better Auth server configuration
│   ├── auth-client.ts          # Client-side auth helpers
│   ├── api.ts                  # API client for backend
│   ├── utils.ts                # cn() helper, misc utilities
│   └── validations/
│       ├── auth.ts             # Auth form schemas
│       └── task.ts             # Task form schemas
├── types/
│   └── task.ts                 # TypeScript interfaces
├── middleware.ts               # Route protection
├── .env.local                  # Environment variables (not committed)
├── .env.example                # Environment template
└── package.json
```

## Patterns
- Use Server Components by default
- Client Components only when needed (interactivity, forms)
- API calls go through Server Actions
- Use `revalidatePath('/dashboard')` after mutations

## Component Conventions
- Use `cn()` utility for conditional class names
- Tailwind CSS classes only (no inline styles)
- Follow existing shadcn/ui patterns
- Accessible components (ARIA labels, keyboard nav)

## Server Actions
```typescript
'use server'
import { revalidatePath } from 'next/cache'

export async function createTask(formData: FormData) {
  // 1. Get JWT token from cookie
  // 2. Call FastAPI backend
  // 3. revalidatePath('/dashboard')
  // 4. Return result
}
```

## Authentication
- Better Auth handles signup/login
- JWT tokens stored in httpOnly cookies
- Middleware protects /dashboard routes
- Server Actions include JWT in API requests

## Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon PostgreSQL (for Better Auth) |
| `BETTER_AUTH_SECRET` | JWT secret (must match backend) |
| `NEXT_PUBLIC_API_URL` | Backend API URL |

## Running
```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

## Styling
- Use Tailwind CSS classes
- shadcn/ui components are customizable
- Dark mode support via CSS variables
- Mobile-first responsive design
