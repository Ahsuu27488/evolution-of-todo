---
name: phase-guard
description: Enforce phase isolation rules from constitution. Use when implementing features to prevent scope creep.
version: 2.0.0
---

# Phase Guard Skill

## Purpose

Enforces **strict phase isolation** to prevent scope creep in hackathon development. Each phase has defined boundaries for technology, complexity, and feature scope.

## Phase Boundaries Reference

| Phase | Name | Key Constraints |
|-------|------|----------------|
| I | In-Memory Console | Standard library only, no databases, no web |
| II | Full-Stack Web | Database, web API, frontend, basic auth |
| III | AI Chatbot | OpenAI Agents, voice input, MCP tools |
| IV | Cloud Native | Docker, Kubernetes, Helm, deployment |
| V | Event Driven | Kafka, Dapr, microservices, distributed systems |

## When to Use This Skill

Activation triggers:
- User requests feature that might belong to different phase
- Implementation mentions technologies not allowed in current phase
- Code review or implementation task for any phase
- Validating spec against phase constraints

## Guard Logic

### 1. Detect Current Phase

Determine phase from:
- Branch name (e.g., `00X-phase-name`)
- Spec location (e.g., `specs/phase-X/`)
- Explicit user context
- Working directory patterns

### 2. Validate Request

Check if requested feature violates phase rules:

```python
def validate_phase_request(phase: int, feature: str, technologies: list[str]) -> GuardResult:
    """
    Validate if a feature request is allowed in the current phase.

    Returns: GuardResult with verdict and explanation
    """
    phase_rules = PHASE_RULES[phase]

    # Check technology constraints
    for tech in technologies:
        if tech in phase_rules["forbidden_techs"]:
            return GuardResult(
                allowed=False,
                reason=f"{tech} is not allowed in Phase {phase}",
                belongs_to=phase_rules["forbidden_techs"][tech]
            )

    # Check feature complexity
    if feature in phase_rules["forbidden_features"]:
        return GuardResult(
            allowed=False,
            reason=f"{feature} is too complex for Phase {phase}",
            belongs_to=phase_rules["forbidden_features"][feature]
        )

    return GuardResult(allowed=True)
```

## Forbidden by Phase

### Phase I (In-Memory Console)

❌ **FORBIDDEN**:
- Databases (PostgreSQL, MongoDB, etc.)
- Web frameworks (FastAPI, Flask, Express, etc.)
- Frontend frameworks (React, Next.js, Vue, etc.)
- External APIs
- File persistence (use `dict` only)
- Any `pip install` beyond standard library

✅ **ALLOWED**:
- Python standard library only
- `dataclasses`, `typing`, `datetime`, `enum`
- `dict`/`list` in-memory storage
- Console I/O with `input()`/`print()`

### Phase II (Full-Stack Web)

❌ **FORBIDDEN**:
- AI/ML models or APIs
- Voice input or speech recognition
- Message queues (Kafka, RabbitMQ)
- Microservices architectures
- Kubernetes containers

✅ **ALLOWED**:
- PostgreSQL database (Neon)
- FastAPI backend
- Next.js frontend
- shadcn/ui components
- Better Auth with JWT
- Docker (basic)

### Phase III (AI Chatbot)

❌ **FORBIDDEN**:
- Message queues or event streaming
- Kubernetes (basic only)
- Distributed systems patterns

✅ **ALLOWED**:
- OpenAI Agents SDK
- Web Speech API (voice input)
- MCP server tools
- ChatKit UI components
- All Phase II technologies

### Phase IV (Cloud Native)

❌ **FORBIDDEN**:
- Message queues
- Service mesh
- Advanced distributed patterns

✅ **ALLOWED**:
- Docker multi-stage builds
- Kubernetes manifests
- Helm charts
- CI/CD pipelines
- All Phase II+ technologies

### Phase V (Event Driven)

✅ **EVERYTHING ALLOWED**:
- Kafka pub/sub
- Dapr sidecars
- Microservices
- Event sourcing
- CQRS patterns
- All previous technologies

## Examples

### Example 1: Database in Phase I

**Input**: "Add PostgreSQL persistence to Phase I console app"

**Output**:
```
Current Phase: Phase I (In-Memory Console)
Requested Feature: Database persistence
Verdict: BLOCKED
Reason: Databases are forbidden in Phase I per constitution §IV.4.2
Belongs To: Phase II (Full-Stack Web)
Recommendation: Implement with in-memory dict storage for Phase I
```

### Example 2: Voice Input in Phase II

**Input**: "Add voice command input to Phase II web app"

**Output**:
```
Current Phase: Phase II (Full-Stack Web)
Requested Feature: Voice input via Web Speech API
Verdict: BLOCKED
Reason: Voice features are Phase III exclusive per constitution §IV.4.3
Belongs To: Phase III (AI Chatbot)
Recommendation: Defer to Phase III or implement text input only
```

### Example 3: Kubernetes in Phase II

**Input**: "Deploy the app to Kubernetes"

**Output**:
```
Current Phase: Phase II (Full-Stack Web)
Requested Feature: Kubernetes deployment
Verdict: BLOCKED
Reason: Kubernetes deployment is Phase IV per constitution §IV.4.4
Belongs To: Phase IV (Cloud Native)
Recommendation: Use simple deployment (Vercel for frontend, direct run for backend)
```

## Decision Flowchart

```
                    ┌─────────────────┐
                    │ Feature Request │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  What Phase?   │
                    └────────┬────────┘
                             ▼
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
     ┌─────────┐       ┌─────────┐       ┌─────────┐
     │ Phase I │       │Phase II  │       │Phase III│
     └────┬────┘       └────┬────┘       └────┬────┘
          ▼                  ▼                  ▼
     ┌─────────┐       ┌─────────┐       ┌─────────┐
     │DB?      │       │AI?      │       │Kafka?   │
     │Web?     │       │K8s?     │       │Dapr?    │
     │Ext Lib? │       │Voice?   │       │         │
     └────┬────┘       └────┬────┘       └────┬────┘
          │                  │                  │
          ▼                  ▼                  ▼
     BLOCKED             BLOCKED             BLOCKED
```

## Configuration

Phase rules can be configured in constitution:

```yaml
# .specify/memory/constitution.md
phase_rules:
  I:
    forbidden_techs:
      - PostgreSQL
      - FastAPI
      - Next.js
    allowed_techs:
      - Python standard library
    max_files: 10
    max_lines_per_file: 200

  II:
    forbidden_techs:
      - OpenAI Agents
      - Kafka
      - Kubernetes
    allowed_techs:
      - PostgreSQL
      - FastAPI
      - Next.js
      - Better Auth
```

## Enforcement

When this skill detects a violation:

1. **HALT** implementation immediately
2. **EXPLAIN** which phase the feature belongs to
3. **SUGGEST** alternative within current phase scope
4. **OPTION**: Ask user if they want to update spec for that phase

## References

- **Constitution**: `.specify/memory/constitution.md`
- **Specs**: `specs/phase-X/spec.md`
