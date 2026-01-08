---
name: "docker-guide"
description: "Fetch Docker documentation and apply containerization best practices. Use when building Dockerfiles, docker-compose, or containerizing applications (Phase IV+)."
version: "1.0.0"
---

# Docker Containerization Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions creating Dockerfiles or docker-compose configurations
- Implementation requires containerizing an application
- User asks about Docker best practices, multi-stage builds, or image optimization
- Phase IV deployment work begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect Docker-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/docker/docs` and relevant topic
3. **Apply Patterns**: Use official Docker patterns for the specific use case
4. **Validate**: Ensure Dockerfile follows best practices (multi-stage, minimal images, layer caching)

## Output Format

Provide structured output:
- **Context7 Source**: `/docker/docs`
- **Pattern Applied**: Specific Docker pattern used (multi-stage, compose, etc.)
- **Key Commands**: Relevant Docker CLI commands
- **Best Practices**: Applied optimizations

## Constraints and Rules

- ALWAYS use multi-stage builds for production images
- NEVER include secrets or credentials in images
- Prefer slim/alpine base images when possible
- Use .dockerignore to exclude unnecessary files
- Pin versions for reproducible builds
- This skill applies to Phase IV and later only

## Example

**Input**: "Containerize the FastAPI backend"

**Output**:
```
Context7 Source: /docker/docs (topic: python dockerfile)
Pattern Applied: Multi-stage build with Python slim
Key Commands: docker build -t todo-backend ., docker-compose up
Best Practices:
- Multi-stage build (builder + runtime)
- Non-root user
- Health check endpoint
- Layer caching for pip install
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `python dockerfile` | FastAPI/Python containerization |
| `node dockerfile` | Next.js frontend containerization |
| `docker compose` | Multi-container orchestration |
| `multi-stage builds` | Production image optimization |
| `health checks` | Container health monitoring |
