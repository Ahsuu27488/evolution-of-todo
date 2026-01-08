---
id: 003
title: Create Technology-Specific Skills
stage: misc
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: 001-reusable-intelligence
branch: 001-reusable-intelligence
user: ahsan
command: manual request
labels: ["skills", "context7", "docker", "kubernetes", "helm", "fastapi", "nextjs", "sqlmodel", "dapr", "kafka"]
links:
  spec: specs/001-reusable-intelligence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/docker-guide/SKILL.md
  - .claude/skills/kubernetes-guide/SKILL.md
  - .claude/skills/helm-guide/SKILL.md
  - .claude/skills/fastapi-guide/SKILL.md
  - .claude/skills/nextjs-guide/SKILL.md
  - .claude/skills/sqlmodel-guide/SKILL.md
  - .claude/skills/dapr-guide/SKILL.md
  - .claude/skills/kafka-guide/SKILL.md
  - .claude/skills/context7-lookup/reference/library-ids.md
tests:
  - Context7 MCP server health: PASS
  - Library ID resolution for all 8 technologies: PASS
  - Skills follow SKILL-TEMPLATE.md format: PASS
---

## Prompt

Create technology-specific skills for the hackathon stack using Context7 library IDs. Cover Docker, Kubernetes, Helm, FastAPI, Next.js, SQLModel, Dapr, and Kafka.

## Response snapshot

Created 8 new technology guide skills using verified Context7 library IDs:

**Context7 Library IDs Resolved:**
| Technology | Library ID | Benchmark Score |
|------------|-----------|-----------------|
| Docker | `/docker/docs` | 80.0 |
| Kubernetes | `/websites/kubernetes_io` | 93.7 |
| Helm | `/helm/helm` | 68.5 |
| FastAPI | `/fastapi/fastapi` | 87.2 |
| Next.js | `/vercel/next.js` | 88.1 |
| SQLModel | `/websites/sqlmodel_tiangolo` | 78.2 |
| Dapr | `/websites/dapr_io` | 85.0 |
| Kafka | `/dpkp/kafka-python` | 89.8 |

**Skills Created:**
1. `docker-guide` - Containerization best practices (Phase IV+)
2. `kubernetes-guide` - K8s deployment patterns (Phase IV+)
3. `helm-guide` - Chart creation and templating (Phase IV+)
4. `fastapi-guide` - REST API development (Phase II+)
5. `nextjs-guide` - React/frontend patterns (Phase II+)
6. `sqlmodel-guide` - Database modeling (Phase II+)
7. `dapr-guide` - Distributed systems patterns (Phase V)
8. `kafka-guide` - Event streaming (Phase V)

**Reference Updated:**
- `library-ids.md` now contains all verified Context7 IDs with benchmark scores and alternatives

## Outcome

- Impact: 8 new auto-activated skills with Context7 integration for documentation lookup
- Tests: Context7 connectivity verified, all library IDs resolved successfully
- Files: 8 skill files + 1 reference file created/updated
- Next prompts: Test skills by implementing Phase II features, verify auto-activation
- Reflection: Skills use Context7 for real-time doc lookup rather than relying on training data

## Evaluation notes (flywheel)

- Failure modes observed: Initial Write attempts interrupted; Context7 MCP required restart to verify connectivity
- Graders run and results (PASS/FAIL): Library ID resolution PASS for all 8 technologies
- Prompt variant (if applicable): N/A
- Next experiment: Test skill auto-activation during Phase II implementation to verify triggers work correctly
