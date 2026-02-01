---
name: qdrant-guide
description: Guide for implementing Qdrant vector database with FastAPI backend and Next.js 15.2 frontend. Use when implementing semantic search endpoints in FastAPI, embedding storage and retrieval for multi-user todo apps, user-scoped vector filtering, RAG systems with fallback to keyword search, or MCP tool integration.
---

# Qdrant Guide

Qdrant vector database integration for semantic task search in multi-user todo applications with FastAPI + Next.js 15.2.

## Quick Start

**Python (FastAPI) with Async Client:**
```python
from qdrant_client import AsyncQdrantClient, models
import os

client = AsyncQdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# Create collection
await client.create_collection(
    collection_name="tasks",
    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
)

# Upsert task embedding
await client.upsert(
    collection_name="tasks",
    points=[
        models.PointStruct(
            id=task_id,
            vector=embedding,
            payload={"user_id": user_id, "title": title, "completed": False}
        )
    ],
)

# User-scoped search
results = await client.query_points(
    collection_name="tasks",
    query=query_vector,
    query_filter=models.Filter(
        must=[models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
    ),
    limit=10,
).points
```

## Installation

```bash
# Python async client
pip install qdrant-client

# Docker (local development)
docker run -p 6333:6333 qdrant/qdrant

# Cloud (production)
# Set QDRANT_URL and QDRANT_API_KEY in .env
```

## Distance Metrics

| Metric | Use Case | Formula |
|--------|----------|---------|
| `Cosine` | **Default** - OpenAI embeddings | Dot product on normalized vectors |
| `Euclid` | L2 distance | Straight-line distance |

```python
# Cosine for OpenAI text-embedding-3-small (1536 dimensions)
models.VectorParams(size=1536, distance=models.Distance.COSINE)
```

## FastAPI Backend

### Service Layer with User Scoping

```python
# app/services/qdrant_service.py
from qdrant_client import AsyncQdrantClient, models
from typing import Any
import os
import logging

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        self.collection = "tasks"

    async def create_collection(self) -> None:
        """Create tasks collection with user_id index."""
        try:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE,
                ),
            )
            # Index user_id for fast filtering
            await self.client.create_payload_index(
                collection_name=self.collection,
                field_name="user_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    async def index_task(
        self,
        task_id: int,
        user_id: str,
        embedding: list[float],
        title: str,
        completed: bool = False,
    ) -> None:
        """Store or update task embedding."""
        point = models.PointStruct(
            id=task_id,
            vector=embedding,
            payload={
                "user_id": user_id,
                "title": title,
                "completed": completed,
            },
        )
        await self.client.upsert(collection_name=self.collection, points=[point])

    async def search_tasks(
        self,
        user_id: str,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[models.PointStruct]:
        """Search tasks scoped to user (multi-user isolation)."""
        try:
            results = await self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=models.Filter(
                    must=[models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )]
                ),
                with_payload=True,
            )
            return results.points
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            raise

# Singleton
_qdrant_service = None

def get_qdrant_service() -> QdrantService:
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
```

### MCP Tool Integration

```python
# app/mcp/tools/semantic_search.py
from app.services.qdrant_service import get_qdrant_service
from app.services.embedding_service import get_embedding_service

async def semantic_search_tool(user_id: str, query: str, limit: int = 10) -> dict:
    """
    MCP tool: Search tasks by meaning (not keywords).

    Returns semantically similar tasks for the user.
    Falls back to keyword search if Qdrant fails.
    """
    qdrant = get_qdrant_service()
    embedding = get_embedding_service()

    try:
        # Generate query embedding
        query_vector = await embedding.embed(query)

        # Search with user scoping
        results = await qdrant.search_tasks(
            user_id=user_id,
            query_vector=query_vector,
            limit=limit,
        )

        return {
            "status": "success",
            "data": [
                {
                    "task_id": r.id,
                    "score": r.score,
                    "title": r.payload.get("title"),
                }
                for r in results
            ]
        }
    except Exception as e:
        # Fallback to keyword search (FR-038)
        logger.warning(f"Qdrant unavailable, using keyword fallback: {e}")
        return await keyword_search_fallback(user_id, query, limit)
```

### Error Handling with Fallback

```python
# app/services/search_service.py
from app.services.qdrant_service import get_qdrant_service
from app.models import Task
from sqlmodel import select

class SearchService:
    def __init__(self):
        self.qdrant = get_qdrant_service()

    async def semantic_search_with_fallback(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
    ) -> dict:
        """
        Search tasks semantically with graceful fallback to keyword search.

        Implements FR-038 and FR-040: Handle Qdrant unavailability.
        """
        try:
            embedding_service = get_embedding_service()
            query_vector = await embedding_service.embed(query)

            # Try semantic search
            results = await self.qdrant.search_tasks(
                user_id=user_id,
                query_vector=query_vector,
                limit=limit,
                score_threshold=0.5,  # Minimum similarity
            )

            return {
                "mode": "semantic",
                "results": [
                    {"task_id": r.id, "score": r.score, "payload": r.payload}
                    for r in results
                ]
            }

        except Exception as e:
            # Fallback to keyword search
            logger.warning(f"Semantic search failed, using keyword fallback: {e}")
            return await self._keyword_search(user_id, query, limit)

    async def _keyword_search(self, user_id: str, query: str, limit: int) -> dict:
        """Fallback keyword search using PostgreSQL LIKE."""
        from app.database import get_session

        async with get_session() as session:
            statement = (
                select(Task)
                .where(Task.user_id == user_id)
                .where(Task.title.ilike(f"%{query}%"))
                .limit(limit)
            )
            results = await session.exec(statement)
            tasks = results.all()

            return {
                "mode": "keyword",
                "results": [
                    {"task_id": t.id, "score": 1.0, "payload": {"title": t.title}}
                    for t in tasks
                ]
            }
```

## Filtering Patterns

### User Scoping (Multi-Tenant)

```python
# Single user filtering (required for all searches)
Filter(
    must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
)

# Multiple users (admin only)
Filter(
    must=[FieldCondition(key="user_id", match=MatchAny(any=[user1, user2]))]
)
```

### Task Status Filtering

```python
# Pending tasks only
Filter(
    must=[
        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
        FieldCondition(key="completed", match=models.MatchValue(value=False)),
    ]
)

# High priority tasks
Filter(
    must=[
        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
        FieldCondition(key="priority", match=models.MatchValue(value="HIGH")),
    ]
)
```

### Date Range Filtering

```python
from qdrant_client.models import Range, Filter, FieldCondition

# Tasks due this week
Filter(
    must=[
        FieldCondition(key="user_id", match=MatchValue(value=user_id)),
        FieldCondition(
            key="due_date",
            range=Range(gte=start_timestamp, lte=end_timestamp)
        )
    ]
)
```

## Embedding Integration

### OpenAI text-embedding-3-small

```python
# app/services/embedding_service.py
from openai import AsyncOpenAI

class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.model = "text-embedding-3-small"  # 1536 dimensions

    async def embed(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [e.embedding for e in response.data]

# Singleton
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
```

### Task Embedding Hook

```python
# app/services/task_service.py
from app.services.embedding_service import get_embedding_service
from app.services.qdrant_service import get_qdrant_service

async def create_task_with_embedding(
    user_id: str,
    title: str,
    description: str | None = None,
    **kwargs
) -> Task:
    """Create task and generate embedding for semantic search."""
    # 1. Create task in database
    task = Task(user_id=user_id, title=title, description=description, **kwargs)
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # 2. Generate embedding from title + description
    embedding_service = get_embedding_service()
    text = f"{title}. {description or ''}"
    embedding = await embedding_service.embed(text)

    # 3. Store in Qdrant with user scoping
    qdrant = get_qdrant_service()
    await qdrant.index_task(
        task_id=task.id,
        user_id=user_id,
        embedding=embedding,
        title=title,
        completed=task.completed,
    )

    # 4. Store embedding_id in task
    task.embedding_id = str(task.id)
    await session.commit()

    return task
```

## Next.js 15.2 Frontend

### Semantic Search Client

```tsx
// lib/api/search.ts
import { API_URL } from '@/lib/config'

export interface SearchResult {
  task_id: number
  score: number
  title: string
}

export async function semanticSearch(
  query: string,
  limit: number = 10
): Promise<SearchResult[]> {
  const token = await getAuthToken() // Your JWT fetch

  const response = await fetch(`${API_URL}/api/search/semantic`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ query, limit }),
  })

  if (!response.ok) throw new Error('Search failed')

  const data = await response.json()
  return data.results
}
```

### Search Component

```tsx
// app/components/TaskSearch.tsx
'use client'

import { useState, useTransition } from 'react'
import { semanticSearch } from '@/lib/api/search'

export function TaskSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isPending, startTransition] = useTransition()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    startTransition(async () => {
      const data = await semanticSearch(query)
      setResults(data)
    })
  }

  return (
    <form onSubmit={handleSearch} className="space-y-4">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by meaning (e.g., 'financial tasks')"
        className="w-full px-4 py-2 rounded-lg bg-muted border"
      />
      <button type="submit" disabled={isPending || !query.trim()}>
        {isPending ? 'Searching...' : 'Search'}
      </button>
      <SearchResults results={results} />
    </form>
  )
}
```

## Collection Schema for Tasks

### Payload Schema

```python
# Task payload in Qdrant
{
    "user_id": "auth|123456",    # Required - for user scoping
    "title": "Buy groceries",      # Required - display text
    "completed": False,            # Required - for filtering
    "priority": "HIGH",            # Optional - for sorting
    "due_date": 1707520800,        # Optional - Unix timestamp
}
```

### Index Configuration

```python
# Create indexes for filtered fields
await client.create_payload_index(
    collection_name="tasks",
    field_name="user_id",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

await client.create_payload_index(
    collection_name="tasks",
    field_name="completed",
    field_schema=models.PayloadSchemaType.KEYWORD,
)
```

## Common Patterns

### RAG Pattern for Task Context

```python
async def get_task_context_for_ai(
    user_id: str,
    query: str,
    limit: int = 5
) -> str:
    """
    Retrieve semantically relevant tasks for AI context.

    Used by AI agent to answer questions about user's tasks.
    """
    qdrant = get_qdrant_service()
    embedding = get_embedding_service()

    query_vector = await embedding.embed(query)
    results = await qdrant.search_tasks(user_id, query_vector, limit)

    # Format results for AI context
    context = "\n".join([
        f"- {r.payload['title']} (score: {r.score:.2f})"
        for r in results
    ])

    return context or "No relevant tasks found."
```

### Batch Indexing for Existing Tasks

```python
async def index_existing_tasks(user_id: str) -> int:
    """Backfill embeddings for tasks created before Qdrant integration."""
    from app.database import get_session
    from app.models import Task
    from sqlmodel import select

    async with get_session() as session:
        statement = select(Task).where(Task.user_id == user_id)
        results = await session.exec(statement)
        tasks = results.all()

    qdrant = get_qdrant_service()
    embedding = get_embedding_service()

    points = []
    for task in tasks:
        text = f"{task.title}. {task.description or ''}"
        vector = await embedding.embed(text)

        points.append(models.PointStruct(
            id=task.id,
            vector=vector,
            payload={
                "user_id": task.user_id,
                "title": task.title,
                "completed": task.completed,
            },
        ))

    # Batch upsert
    await qdrant.upsert_points("tasks", points)
    return len(points)
```

### Hybrid Search (Future Enhancement)

```python
# For advanced: combine semantic + keyword
# Requires sparse vectors configuration
client.create_collection(
    collection_name="tasks_hybrid",
    vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
    sparse_vectors_config={
        "text": models.SparseVectorParams()
    },
)
```

## Context7 Queries

For latest Qdrant patterns:

```bash
# Query Qdrant client docs
context7 query /qdrant/qdrant-client "async client query_points filter user_id"

# Query Qdrant REST API
context7 query /websites/api_qdrant_tech "payload index filtering"
```

## Resources

### references/

- `fastapi_patterns.md` - Complete FastAPI async integration
- `filtering.md` - Advanced filter conditions

### Key Implementation Notes

1. **User Scoping**: ALWAYS filter by `user_id` to prevent cross-user data leakage (FR-039)
2. **Fallback**: Implement keyword search fallback for Qdrant failures (FR-038, FR-040)
3. **Async Only**: Use `AsyncQdrantClient` for FastAPI compatibility
4. **Embedding ID**: Store `embedding_id` in Task model for direct lookup (FR-033)
5. **Re-indexing**: Update embeddings on task title/description changes (FR-034)
