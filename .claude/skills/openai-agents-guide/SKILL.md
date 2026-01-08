---
name: "openai-agents-guide"
description: "Fetch OpenAI Agents SDK documentation and apply AI agent best practices. Use when implementing AI chatbots, agents, or tool-calling patterns (Phase III)."
version: "1.0.0"
---

# OpenAI Agents SDK Development Guide

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions OpenAI Agents SDK, AI agents, or chatbot
- Implementation requires agent definition or tool registration
- User asks about conversation handling or agent runners
- Phase III chatbot development begins
- Need to integrate MCP tools with agents

## How This Skill Works

Step-by-step workflow:
1. **Identify Agent Need**: Detect AI agent requirement from context
2. **Fetch Agents SDK Docs**: Call Context7 for OpenAI Agents SDK patterns
3. **Design Agent**: Define agent with appropriate tools and instructions
4. **Implement Runner**: Set up async runner for conversation handling
5. **Integrate MCP**: Connect MCP server tools to agent

## Output Format

Provide structured output:
- **Context7 Source**: `/openai/openai-agents-python` or equivalent
- **Agent Definition**: Agent name, instructions, model
- **Tools Registered**: List of tools available to agent
- **Runner Pattern**: How to execute agent conversations
- **State Management**: How conversation state is handled

## Constraints and Rules

- ALWAYS use async patterns for agent execution
- ALWAYS define clear agent instructions for task-specific behavior
- Register MCP tools as agent tools
- Implement stateless request handling (state in DB, not memory)
- Handle tool call errors gracefully
- This skill applies to Phase III only

## Architecture Pattern

```
┌─────────────────┐     ┌─────────────────────────────────────────────┐
│   ChatKit UI    │     │              FastAPI Server                  │
│                 │────▶│  ┌─────────────────────────────────────┐    │
│   POST /chat    │     │  │     OpenAI Agents SDK                │    │
│                 │     │  │  ┌───────────┐    ┌───────────────┐  │    │
│                 │◀────│  │  │   Agent   │───▶│  MCP Server   │  │    │
│                 │     │  │  │  Runner   │    │  (Tools)      │  │    │
│                 │     │  │  └───────────┘    └───────────────┘  │    │
└─────────────────┘     │  └─────────────────────────────────────┘    │
                        └─────────────────────────────────────────────┘
```

## Example: Todo Agent Implementation

**Input**: "Create an AI agent for managing todos via natural language"

**Output**:

### 1. Agent Definition

```python
# agents/todo_agent.py
from openai_agents import Agent, Runner
from tools.mcp_tools import add_task, list_tasks, complete_task, delete_task, update_task

todo_agent = Agent(
    name="TodoAssistant",
    model="gpt-4o-mini",
    instructions="""You are a helpful todo list assistant. You help users manage their tasks.

When a user wants to:
- Add a task: Use the add_task tool
- View tasks: Use the list_tasks tool
- Complete a task: Use the complete_task tool
- Delete a task: Use the delete_task tool
- Update a task: Use the update_task tool

Always confirm actions with friendly, concise responses.
If a request is unclear, ask for clarification.
Handle errors gracefully and inform the user.""",
    tools=[add_task, list_tasks, complete_task, delete_task, update_task],
)
```

### 2. Runner Pattern (Stateless)

```python
# routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai_agents import Runner
from agents.todo_agent import todo_agent
from db import get_conversation_messages, save_message

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list[dict]

@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, request: ChatRequest):
    # Get or create conversation
    conversation_id = request.conversation_id or create_conversation(user_id)

    # Load conversation history from DB (stateless pattern)
    history = await get_conversation_messages(conversation_id)

    # Save user message
    await save_message(conversation_id, "user", request.message)

    # Build message array
    messages = history + [{"role": "user", "content": request.message}]

    # Run agent with MCP tools
    runner = Runner(agent=todo_agent, context={"user_id": user_id})
    result = await runner.run(messages)

    # Save assistant response
    await save_message(conversation_id, "assistant", result.response)

    return ChatResponse(
        conversation_id=conversation_id,
        response=result.response,
        tool_calls=result.tool_calls,
    )
```

### 3. MCP Tool Integration

```python
# tools/mcp_tools.py
from openai_agents import tool

@tool
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user."""
    # Call MCP server or direct DB operation
    result = await mcp_client.call_tool("add_task", {
        "user_id": user_id,
        "title": title,
        "description": description,
    })
    return result

@tool
async def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """List tasks for the user, optionally filtered by status."""
    result = await mcp_client.call_tool("list_tasks", {
        "user_id": user_id,
        "status": status,
    })
    return result

# ... similar for complete_task, delete_task, update_task
```

## Stateless Conversation Pattern

**Key Principle**: Server holds NO state between requests.

1. **Request arrives** with message and optional conversation_id
2. **Load history** from database
3. **Run agent** with full context
4. **Save response** to database
5. **Return response** to client
6. **Server forgets** everything (ready for next request)

**Benefits**:
- Horizontal scaling (any server handles any request)
- Resilience (server restarts don't lose state)
- Testability (each request is reproducible)

## Reference: Context7 Topics

| Topic | Use Case |
|-------|----------|
| `agent` | Agent definition patterns |
| `runner` | Execution and streaming |
| `tools` | Tool registration and calling |
| `context` | Passing context to tools |
| `streaming` | Real-time response streaming |
