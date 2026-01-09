---
name: context7-lookup
description: Fetch official documentation for libraries, frameworks, and tools using Context7 MCP. Use when implementing with external dependencies or asking about library APIs.
version: 2.0.0
---

# Context7 Documentation Lookup Skill

## Theoretical Foundation

Context7 is an MCP server that provides:
- **Official Documentation**: Curated docs from library sources
- **Code Examples**: Real-world usage patterns
- **Version Awareness**: Specific version documentation
- **High-Quality Sources**: Filtered by reputation and benchmark scores

### The Lookup Pipeline

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      CONTEXT7 DOCUMENTATION PIPELINE                          │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  User Query: "How do I use FastAPI dependencies?"                             │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    Step 1: Resolve Library ID                       │     │
│  │  ┌─────────────────────────────────────────────────────────────┐   │     │
│  │  │ mcp__context7__resolve-library_id                           │   │     │
│  │  │   query: "FastAPI dependency injection"                     │   │     │
│  │  │   libraryName: "fastapi"                                    │   │     │
│  │  └─────────────────────────────────────────────────────────────┘   │     │
│  │                          │                                         │     │
│  │                          ▼                                         │     │
│  │  Returns: Library ID, Reputation, Snippets, Benchmark             │     │
│  │  Best Match: /websites/fastapi_tiangolo (High, 12067 snippets)  │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    Step 2: Query Documentation                       │     │
│  │  ┌─────────────────────────────────────────────────────────────┐   │     │
│  │  │ mcp__context7__query-docs                                   │   │     │
│  │  │   libraryId: "/websites/fastapi_tiangolo"                  │   │     │
│  │  │   query: "dependency injection Depends Annotated"           │   │     │
│  │  └─────────────────────────────────────────────────────────────┘   │     │
│  │                          │                                         │     │
│  │                          ▼                                         │     │
│  │  Returns: Code examples with source URLs                          │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    Step 3: Apply to Implementation                  │     │
│  │  • Synthesize patterns from examples                                │     │
│  │  • Adapt code to specific use case                                   │     │
│  │  • Cite Context7 source in output                                    │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

## When to Use This Skill

Activation triggers:
- Implementing with external libraries (FastAPI, Next.js, SQLModel, etc.)
- User asks "how do I use X" for any framework
- Need to verify API usage patterns
- Unknown library or version-specific behavior
- Best practices for a specific technology

## Resolution Strategy

### Step 1: Resolve Library ID

Always call `mcp__context7__resolve-library-id` first:

```python
# Input parameters
libraryName: str  # The library name (e.g., "fastapi", "next.js")
query: str       # Context about what you're trying to do

# Selection criteria (in order of priority)
1. Name match score
2. Source reputation (High > Medium > Low)
3. Benchmark score (higher is better)
4. Code snippet count (more examples = better)
```

### Step 2: Query Documentation

Use the resolved library ID:

```python
# Input parameters
libraryId: str  # The resolved Context7 ID (e.g., "/websites/fastapi_tiangolo")
query: str     # Specific topic or question

# Tips for good queries
- Be specific: "dependency injection Depends Annotated" not "dependencies"
- Include version if relevant: "Next.js 15 app router" not "Next.js routing"
- Focus on patterns: "CRUD FastAPI SQLModel" not "how to make API"
```

### Step 3: Synthesize and Apply

- Extract patterns from multiple code examples
- Identify the canonical approach (most examples agree)
- Note any version-specific differences
- Cite the Context7 source in output

## Output Format

Always include:
- **Context7 Source**: The library ID used
- **Key Patterns**: Code patterns extracted from docs
- **Applied**: How the pattern was used in implementation

## Common Library IDs (Reference)

| Library | Context7 ID |
|---------|-------------|
| Better Auth | `/better-auth/better-auth` |
| FastAPI | `/websites/fastapi_tiangolo` |
| Next.js | `/vercel/next.js` |
| SQLModel | `/websites/sqlmodel_tiangolo` |
| shadcn/ui | `/websites/ui_shadcn` |
| Tailwind CSS | `/tailwindlabs/tailwindcss` |
| Radix UI | `/radix-ui/primitives` |
| Framer Motion | `/framer/motion` |
| Docker | `/docker/docs` |
| Kubernetes | `/websites/kubernetes_io` |
| Helm | `/helm/helm` |
| Kafka | `/dpkp/kafka-python` |
| Dapr | `/websites/dapr_io` |

## Query Patterns by Technology

### FastAPI
| Need | Query |
|------|-------|
| CRUD | "CRUD create read update delete Pydantic" |
| Auth | "JWT OAuth2 Bearer token dependency injection" |
| Validation | "Pydantic Field validation error handling" |
| Database | "SQLModel session select where relationship" |

### Next.js
| Need | Query |
|------|-------|
| Routing | "App Router file-based routing pages layout" |
| Server Actions | "Server Actions useFormState mutations 'use server'" |
| Data Fetching | "fetch caching revalidate async await server components" |
| Middleware | "middleware authentication redirect headers runtime" |

### SQLModel
| Need | Query |
|------|-------|
| Models | "SQLModel table Field primary_key foreign_key" |
| Queries | "select where order_by limit offset session exec" |
| Relationships | "Relationship back_populates foreign_key join" |
| FastAPI | "FastAPI SQLModel Depends Session response_model" |

## Example Interaction

**User**: "How do I add dependency injection to FastAPI?"

**Agent Process**:
1. Resolve: `mcp__context7__resolve-library-id("fastapi")`
2. Query: `mcp__context7__query-docs("/websites/fastapi_tiangolo", "dependency injection Depends Annotated")`
3. Apply: Use pattern from docs to implement

**Output**:
```
Context7 Source: /websites/fastapi_tiangolo

Key Pattern: Annotated Dependencies (Python 3.10+)
from typing import Annotated
from fastapi import Depends

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/tasks")
def get_tasks(session: SessionDep):
    return session.exec(select(Task)).all()

Applied: Created get_session dependency and SessionDep type alias for clean dependency injection
```

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Not resolving ID first | Always call resolve-library-id before query-docs |
| Using generic queries | Be specific about the feature you need |
| Ignoring reputation | Prefer "High" reputation sources |
| Not citing source | Always mention Context7 source in output |

## Constraints

- ALWAYS use Context7 before implementing with external libraries
- NEVER rely solely on training data for API usage
- Prefer High reputation sources
- Report if no documentation match found
- Maximum 3 Context7 calls per question (to avoid over-fetching)

## References

- **Context7**: https://context7.com
- **MCP Docs**: https://modelcontextprotocol.io
