---
name: "nextjs-guide"
description: "Fetch Next.js documentation and apply React/frontend best practices. Use when building pages, components, or frontend features (Phase II+)."
version: "1.0.0"
---

# Next.js Development Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions Next.js, React components, or frontend pages
- Implementation requires App Router, server components, or client components
- User asks about routing, data fetching, or SSR/SSG
- Phase II frontend development begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect Next.js-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/vercel/next.js` and relevant topic
3. **Apply Patterns**: Use official Next.js patterns for the specific feature
4. **Validate**: Ensure code follows Next.js best practices (App Router, RSC, etc.)

## Output Format

Provide structured output:
- **Context7 Source**: `/vercel/next.js`
- **Pattern Applied**: Next.js pattern used (App Router, Server Action, etc.)
- **Component Type**: Server Component or Client Component
- **Best Practices**: Applied optimizations

## Constraints and Rules

- ALWAYS use App Router (app/ directory) for new projects
- Default to Server Components, use 'use client' only when needed
- Use Server Actions for mutations
- Implement proper loading and error states
- Optimize images with next/image
- This skill applies to Phase II and later only

## Example

**Input**: "Create a todo list page with add functionality"

**Output**:
```
Context7 Source: /vercel/next.js (topic: app router forms)
Pattern Applied: Server Components + Server Actions
Component Type:
- app/todos/page.tsx - Server Component (data fetching)
- components/TodoForm.tsx - Client Component (interactivity)
Best Practices:
- Server Action for form submission
- Optimistic updates with useOptimistic
- Loading.tsx for streaming
- Error.tsx for error boundary
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `app router` | File-based routing |
| `server components` | Data fetching, SEO |
| `client components` | Interactivity, hooks |
| `server actions` | Form handling, mutations |
| `data fetching` | fetch, cache, revalidation |
| `middleware` | Auth, redirects |
