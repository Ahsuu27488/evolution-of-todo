---
name: "fastapi-guide"
description: "Fetch FastAPI documentation and apply web API best practices. Use when building REST APIs, endpoints, or backend services (Phase II+)."
version: "1.0.0"
---

# FastAPI Development Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions FastAPI, Pydantic models, or REST endpoints
- Implementation requires creating API routes or middleware
- User asks about dependency injection, async handlers, or OpenAPI
- Phase II backend development begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect FastAPI-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/fastapi/fastapi` and relevant topic
3. **Apply Patterns**: Use official FastAPI patterns for the specific feature
4. **Validate**: Ensure code follows FastAPI best practices (type hints, Pydantic, async)

## Output Format

Provide structured output:
- **Context7 Source**: `/fastapi/fastapi`
- **Pattern Applied**: FastAPI pattern used (router, dependency, etc.)
- **Key Decorators**: @app.get, @app.post, Depends(), etc.
- **Best Practices**: Applied optimizations

## Constraints and Rules

- ALWAYS use Pydantic models for request/response validation
- ALWAYS add proper type hints for all parameters
- Use dependency injection for shared logic
- Implement proper error handling with HTTPException
- Add OpenAPI documentation (summary, description, tags)
- This skill applies to Phase II and later only

## Example

**Input**: "Create a CRUD API for todos"

**Output**:
```
Context7 Source: /fastapi/fastapi (topic: crud operations)
Pattern Applied: APIRouter with Pydantic models
Key Decorators:
- @router.get("/todos") - List all
- @router.post("/todos") - Create new
- @router.put("/todos/{id}") - Update
- @router.delete("/todos/{id}") - Delete
Best Practices:
- TodoCreate/TodoResponse Pydantic models
- Dependency injection for database session
- HTTP status codes (201 for create, 204 for delete)
- Async endpoints for I/O operations
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `path operations` | Creating API endpoints |
| `pydantic models` | Request/response validation |
| `dependency injection` | Shared logic and resources |
| `authentication` | JWT, OAuth2 patterns |
| `middleware` | Request/response processing |
| `background tasks` | Async task execution |
