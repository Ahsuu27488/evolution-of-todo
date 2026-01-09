---
name: openai-agents-guide
description: Fetch OpenAI Agents SDK documentation and apply AI agent best practices. Use when implementing AI chatbots, agents, or tool-calling patterns (Phase III).
version: 2.0.0
---

# OpenAI Agents SDK Mastery Skill

## When to Use This Skill

Activation triggers:
- Implementing AI agents with OpenAI Agents SDK
- Creating agents that call tools/MCP functions
- Building chatbot with function calling
- Phase III chatbot development

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Server                           │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │         OpenAI Agents SDK                     │  │   │
│  │  │  ┌─────────────┐    ┌─────────────────────┐  │  │   │
│  │  │  │   Agent     │───▶│  MCP Server Tools   │  │  │   │
│  │  │  │  (gpt-4o)   │    │  (add_task, etc.)    │  │   │
│  │  │  └─────────────┘    └─────────────────────┘  │  │   │
│  │  │                                               │  │   │
│  │  │  ┌───────────────────────────────────────┐  │  │   │
│  │  │  │         Runner                         │  │  │   │
│  │  │  │  (executes agent, manages state)     │  │  │   │
│  │  │  └───────────────────────────────────────┘  │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Agent Definition

```python
# agents/todo_agent.py
from openai_agents import Agent
from tools.mcp_tools import add_task, list_tasks, complete_task

todo_agent = Agent(
    name="TodoAssistant",
    model="gpt-4o-mini",
    instructions="""You are a helpful todo list assistant.

When users want to:
- Add a task: Use add_task tool
- View tasks: Use list_tasks tool
- Complete a task: Use complete_task tool

Always confirm actions with friendly responses.
Handle errors gracefully.""",
    tools=[add_task, list_tasks, complete_task],
)
```

## Stateless Runner Pattern

```python
# routes/chat.py
from fastapi import APIRouter
from openai_agents import Runner
from agents.todo_agent import todo_agent
from db import get_conversation_messages, save_message

router = APIRouter()

@router.post("/api/chat")
async def chat(request: ChatRequest):
    # Load conversation history from DB (stateless!)
    history = await get_conversation_messages(request.conversation_id)

    # Build messages including history
    messages = history + [{"role": "user", "content": request.message}]

    # Run agent
    runner = Runner(agent=todo_agent, context={"user_id": request.user_id})
    result = await runner.run(messages)

    # Save to database
    await save_message(request.conversation_id, "user", request.message)
    await save_message(request.conversation_id, "assistant", result.response)

    return {"response": result.response, "tool_calls": result.tool_calls}
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Stateless | Store state in database, not memory |
| Tool functions | Register MCP tools as agent tools |
| Error handling | Graceful degradation on tool failures |
| Context passing | Pass user_id in agent context |

## Context7 Topics

| Topic | Query String |
|-------|--------------|
| Agent | "OpenAI Agents SDK agent definition" |
| Runner | "Runner execution streaming" |
| Tools | "Agent tool registration function calling" |
| Context | "Passing context to tools" |
