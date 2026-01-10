# Quickstart: Advanced Dashboard UI Overhaul

**Feature**: 008-dashboard-ui-overhaul
**Date**: 2026-01-10

## Prerequisites

1. **Branch**: `008-dashboard-ui-overhaul`
2. **Node**: v18+ (via `nvm use` or system node)
3. **Backend**: Running on `http://localhost:8000`
4. **Database**: Neon PostgreSQL (already configured)

## Development Setup

### 1. Install Dependencies (if needed)

```bash
cd frontend
npm install
```

### 2. Start Development Servers

**Terminal 1 - Backend**:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Dashboard: http://localhost:3000/dashboard
- API Docs: http://localhost:8000/docs

## File Structure (This Feature)

```
frontend/
├── components/
│   ├── dashboard/
│   │   ├── dashboard-content.tsx    [MODIFY] - Main dashboard layout
│   │   ├── dashboard-toolbar.tsx    [CREATE] - Search, filter, sort controls
│   │   └── sort-dropdown.tsx        [CREATE] - Sort criterion selector
│   ├── tasks/
│   │   ├── task-form.tsx            [MODIFY] - Add due_date, tags, recurrence
│   │   └── task-card.tsx            [MODIFY] - Display new attributes
│   └── tags/
│       └── tag-input.tsx            [CREATE] - Tag management component
├── lib/
│   ├── hooks/
│   │   ├── use-debounce.ts          [CREATE] - Debounce hook for search
│   │   └── use-task-filters.ts      [CREATE] - Filter/sort logic hook
│   ├── validations/
│   │   └── task.ts                  [UPDATE] - Add due_date, tags, recurrence
│   └── utils/
│       └── tag-utils.ts             [CREATE] - Color generation, validation
```

## Key Files to Reference

| File | Purpose |
|------|---------|
| `lib/stores/ui-store.ts` | Filter state (already implemented) |
| `lib/api-client.ts` | API methods (all endpoints exist) |
| `app/globals.css` | Glassmorphism utilities |
| `lib/animations.ts` | Framer Motion variants |
| `types/task.ts` | TypeScript interfaces |

## Development Commands

```bash
# Type checking
npm run tsc -- --noEmit

# Linting
npm run lint

# Build verification
npm run build
```

## Testing Checklist

### Task Creation
- [ ] Create task with due date
- [ ] Create task with multiple tags
- [ ] Create task with recurrence pattern
- [ ] Verify all three together

### Filtering
- [ ] Status tabs (All/Pending/Completed)
- [ ] Priority dropdown (High/Medium/Low)
- [ ] Combined filters (e.g., Pending + High)

### Sorting
- [ ] Sort by Created Date
- [ ] Sort by Due Date (ascending/descending)
- [ ] Sort by Priority
- [ ] Sort by Title

### Search
- [ ] Type and see debounced results
- [ ] Clear search to reset
- [ ] Search with active filters

### Visual
- [ ] Glassmorphism matches hero page
- [ ] Task cards stagger in on load
- [ ] Overdue tasks show red highlight
- [ ] Tags display with correct colors
- [ ] Recurrence icon appears appropriately

### Responsive
- [ ] Mobile (< 640px) toolbar stacks
- [ ] Tablet (640-1024px) 2-row toolbar
- [ ] Desktop single row

## Common Issues

### "CORS Error" when creating task
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

### "JWT Expired" errors
- Sign out and sign in again
- Check `BETTER_AUTH_SECRET` matches between frontend and backend

### Tasks not updating
- Open TanStack Query Devtools to inspect cache
- Check browser console for API errors

### Glassmorphism not working
- Verify `globals.css` is imported in `app/layout.tsx`
- Check that `.glass` class exists in CSS

## Success Criteria Verification

```bash
# 1. Can create task with due date, tags, recurrence
#    → Open TaskForm, fill all fields, submit

# 2. Can sort by Due Date ascending
#    → Select "Due Date" from sort, ensure ascending (↑)

# 3. Can filter to High Priority only
#    → Select "High" from priority dropdown

# 4. Visual quality matches hero
#    → Navigate from / to /dashboard, compare aesthetics
```

## Next Steps After Implementation

1. Run all acceptance scenarios from [spec.md](spec.md)
2. Update screenshots for documentation
3. Create PR with description referencing this feature
4. Test on mobile viewport
