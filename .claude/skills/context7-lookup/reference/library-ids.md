# Context7 Library IDs for Hackathon Stack

**Last Updated**: 2025-12-26

Quick reference for Context7 library IDs used in this hackathon. All IDs have been verified via `resolve-library-id`.

## Phase I: Console App
| Technology | Context7 Library ID | Benchmark | Notes |
|------------|---------------------|-----------|-------|
| Python | N/A | N/A | Standard library, no lookup needed |

## Phase II: Full-Stack Web
| Technology | Context7 Library ID | Benchmark | Notes |
|------------|---------------------|-----------|-------|
| FastAPI | `/fastapi/fastapi` | 87.2 | High reputation, Python web framework |
| SQLModel | `/websites/sqlmodel_tiangolo` | 78.2 | High reputation, ORM for FastAPI |
| Next.js | `/vercel/next.js` | 88.1 | High reputation, React framework |

## Phase III: AI Chatbot
| Technology | Context7 Library ID | Benchmark | Notes |
|------------|---------------------|-----------|-------|
| OpenAI Agents SDK | `/openai/openai-agents-python` | 86.4 | High reputation |
| MCP Python SDK | `/modelcontextprotocol/python-sdk` | 89.2 | High reputation |

## Phase IV: Local Kubernetes
| Technology | Context7 Library ID | Benchmark | Notes |
|------------|---------------------|-----------|-------|
| Docker | `/docker/docs` | 80.0 | High reputation, containerization |
| Kubernetes | `/websites/kubernetes_io` | 93.7 | High reputation, orchestration |
| Helm | `/helm/helm` | 68.5 | High reputation, K8s packages |

## Phase V: Cloud Deployment
| Technology | Context7 Library ID | Benchmark | Notes |
|------------|---------------------|-----------|-------|
| Dapr | `/websites/dapr_io` | 85.0 | High reputation, distributed runtime |
| Kafka (Python) | `/dpkp/kafka-python` | 89.8 | High reputation, event streaming |

## Claude Code Resources
| Technology | Context7 Library ID | Benchmark | Notes |
|------------|---------------------|-----------|-------|
| Claude Code | `/anthropics/claude-code` | 12.3 | High reputation |

## Alternative Library IDs

Some libraries have multiple valid IDs. Use alternatives if primary has issues:

| Technology | Alternative IDs |
|------------|-----------------|
| Docker | `/websites/docs_docker_com`, `/llmstxt/docker_llms_txt` |
| Kubernetes | `/kubernetes/kubernetes` (64.5) |
| Next.js | `/websites/nextjs` (80.3), `/websites/nextjs_app` (92.5) |
| SQLModel | `/fastapi/sqlmodel` (79.8) |
| Dapr | `/dapr/docs` (75.9), `/dapr/quickstarts` (89.9) |
| Kafka | `/apache/kafka` (76.9), `/confluentinc/confluent-kafka-python` (68.8) |

## Usage Example

```python
# Step 1: Resolve library ID (if not known)
mcp__plugin_context7_context7__resolve-library-id(libraryName="FastAPI")

# Step 2: Fetch documentation with topic
mcp__plugin_context7_context7__get-library-docs(
    context7CompatibleLibraryID="/fastapi/fastapi",
    topic="dependency injection"
)
```

## Phase Technology Summary

| Phase | Technologies |
|-------|-------------|
| **I** | Python standard library only |
| **II** | FastAPI, Next.js, SQLModel |
| **III** | Phase II + MCP SDK, OpenAI Agents SDK |
| **IV** | Phase III + Docker, Kubernetes, Helm |
| **V** | Phase IV + Dapr, Kafka |
