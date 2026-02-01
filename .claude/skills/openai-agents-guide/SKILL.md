---
name: openai-agents-guide
description: Fetch OpenAI Agents SDK documentation and apply AI agent best practices. Use when implementing AI chatbots, agents, tool-calling patterns, or multi-agent handoffs (Phase III).
version: 3.0.0
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# OpenAI Agents SDK Mastery Skill

## Context7 Research Results

**Library ID**: `/openai/openai-agents-python`
**Source**: https://github.com/openai/openai-agents-python
**Reputation**: High
**Code Snippets**: 606+
**Latest Version**: v0.7.0

## When to Use This Skill

Activation triggers:
- Implementing AI agents with OpenAI Agents SDK
- Creating multi-agent systems with handoffs
- Building chatbot with function calling
- Phase III chatbot development

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 MULTI-AGENT ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              FastAPI Server                           │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │         OpenAI Agents SDK                     │  │   │
│  │  │  ┌─────────────┐    ┌─────────────────────┐  │  │   │
│  │  │  │  Main       │───▶│  MCP Server Tools   │  │  │   │
│  │  │  │  Agent      │    │  (add_task, etc.)    │  │  │   │
│  │  │  │ (Triage)    │    └─────────────────────┘  │  │   │
│  │  │  └──────┬──────┘                            │  │   │
│  │  │         │ handoffs                           │  │   │
│  │  │    ┌────┴────┐                               │  │   │
│  │  │    ▼         ▼                               │  │   │
│  │  │  ┌───────┐ ┌───────┐                         │  │   │
│  │  │  │Planning│ │Query  │                         │  │   │
│  │  │  │ Agent │ │Agent  │                         │  │   │
│  │  │  └───────┘ └───────┘                         │  │   │
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

## Core Agent Definition

```python
# agents/todo_agent.py
from openai_agents import Agent
from tools.mcp_tools import add_task, list_tasks, complete_task

todo_agent = Agent(
    name="TodoAssistant",
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

## Agent Handoffs and Specialization

### Basic Handoff Pattern

```python
from agents import Agent

# Specialized agents
planning_agent = Agent(
    name="PlanningAgent",
    handoff_description="Specialist for weekly planning and task prioritization",
    instructions="""You are a planning specialist.
Help users organize their week, prioritize tasks by urgency,
and identify scheduling conflicts.""",
)

query_agent = Agent(
    name="TaskQueryAgent",
    handoff_description="Specialist for complex task searches and filtering",
    instructions="""You are a search specialist.
Help users find tasks using semantic search, filters,
and complex queries.""",
)

# Main agent with handoffs
todo_agent = Agent(
    name="TodoAssistant",
    instructions="""You are a helpful todo assistant.
- For general commands: handle yourself
- For weekly planning: hand off to PlanningAgent
- For complex searches: hand off to TaskQueryAgent""",
    handoffs=[planning_agent, query_agent],
    tools=[add_task, list_tasks, complete_task],
)
```

### Handoff with Callbacks

```python
from agents import Agent, handoff, RunContextWrapper
from pydantic import BaseModel

class HandoffContext(BaseModel):
    reason: str
    original_query: str

async def on_handoff(ctx: RunContextWrapper, data: HandoffContext):
    # Log handoff for analytics
    print(f"Handoff to specialist: {data.reason}")
    # Could fetch additional context here

# Create handoff with customization
handoff_obj = handoff(
    agent=query_agent,
    on_handoff=on_handoff,
    input_type=HandoffContext,
    tool_name_override="complex_search",
    tool_description_override="Use for complex semantic searches and multi-criteria filtering",
)

todo_agent = Agent(
    name="TodoAssistant",
    handoffs=[handoff_obj],
)
```

### Triage Agent Pattern

```python
# Routing agent that delegates to specialists
triage_agent = Agent(
    name="TriageAgent",
    instructions="""You determine which agent should handle the request:
- "plan", "week", "schedule" -> PlanningAgent
- "find", "search", "overdue" -> TaskQueryAgent
- Otherwise handle yourself as TodoAssistant""",
    handoffs=[
        planning_agent,
        query_agent,
        # Can also include main agent for return path
    ],
)
```

## Context Preservation Across Handoffs

```python
from agents import Runner, RunContextWrapper
from typing import Dict, Any

class TodoContext(RunContextWrapper):
    user_id: str
    conversation_id: str
    preferences: Dict[str, Any]

# Pass context to Runner - automatically propagates through handoffs
result = await Runner.run(
    triage_agent,
    "Help me plan my week",
    context=TodoContext(
        user_id="user_123",
        conversation_id="conv_456",
        preferences={"timezone": "UTC", "language": "en"}
    )
)

# After handoff, the new agent has full conversation history
# Context is preserved automatically
print(f"Final agent: {result.last_agent.name}")
print(f"Full context available: {result.context}")
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

    # Run agent with context
    result = await Runner.run(
        todo_agent,
        messages,
        context={"user_id": request.user_id}
    )

    # Save to database
    await save_message(request.conversation_id, "user", request.message)
    await save_message(
        request.conversation_id,
        "assistant",
        result.final_output
    )

    return {
        "response": result.final_output,
        "agent": result.last_agent.name,
        "tool_calls": result.tool_calls,
    }
```

## Input Guardrails

```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput
from pydantic import BaseModel

class GuardrailOutput(BaseModel):
    is_valid: bool
    reason: str

guardrail_agent = Agent(
    name="Input Validator",
    instructions="Check if the user's request is valid for a todo app.",
    output_type=GuardrailOutput,
)

async def todo_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    output = result.final_output_as(GuardrailOutput)
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=not output.is_valid,
    )

# Add guardrails to main agent
safe_agent = Agent(
    name="SafeTodoAssistant",
    instructions="You are a todo assistant.",
    input_guardrails=[
        InputGuardrail(guardrail_function=todo_guardrail),
    ],
    handoffs=[planning_agent, query_agent],
)
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Stateless | Store state in database, not memory |
| Handoffs | Use for specialized domains, not simple branching |
| Context preservation | Pass via Runner context, auto-propagates |
| Tool functions | Register MCP tools as agent tools |
| Guardrails | Validate input before agent processing |
| Error handling | Graceful degradation on tool failures |
| Agent return path | Include main agent in handoff lists for return |

## Handoff Design Guidelines

### When to Use Handoffs

✅ **Use handoffs for:**
- Domain specialization (Planning, Queries, Analysis)
- Different instruction sets needed
- Modular agent architecture
- Reusable specialist agents

❌ **Don't use handoffs for:**
- Simple conditional logic (use instructions)
- Same domain with minor variations
- Performance optimization (handoffs have overhead)

### Handoff Description Best Practices

```python
# Good: Clear, actionable description
Agent(
    name="PlanningAgent",
    handoff_description="Use for weekly planning, task prioritization, and schedule analysis",
)

# Bad: Vague description
Agent(
    name="PlanningAgent",
    handoff_description="Helps with stuff",  # Not actionable
)
```

## Context7 Topics

| Topic | Query String |
|-------|--------------|
| Agent | "OpenAI Agents SDK agent definition" |
| Handoffs | "agent handoff multi-agent specialization context" |
| Runner | "Runner execution streaming" |
| Tools | "Agent tool registration function calling" |
| Guardrails | "input guardrail validation tripwire" |
| Realtime | "realtime agent handoff audio" |
