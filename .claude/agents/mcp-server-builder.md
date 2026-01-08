---
description: "Build MCP servers with tools for AI agent integration. Use when implementing Phase III chatbot MCP tools."
handoffs:
  - label: Test MCP Server
    agent: sp.implement
    prompt: Test the MCP server tools with sample inputs
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

Build production-ready MCP (Model Context Protocol) servers that expose tools for AI agents to interact with the todo application. This agent handles the complete MCP server implementation workflow.

This agent is invoked when:
- User needs to create MCP server for Phase III chatbot
- Implementing tool interfaces for OpenAI Agents SDK
- Building stateless MCP tools that interact with database

## Prerequisites

Before this agent runs:
- [ ] Phase II backend is complete with working REST API
- [ ] Database models exist for Task, Conversation, Message
- [ ] Constitution loaded and Context7 MCP available

## Workflow Phases

### Phase 1: Discovery

**Goal**: Understand required MCP tools and their specifications

**Steps**:
1. Read hackathon docs for MCP tools specification
2. Fetch MCP Python SDK docs via Context7: `/modelcontextprotocol/python-sdk`
3. Identify all required tools: add_task, list_tasks, complete_task, delete_task, update_task

**Output**: Tool specifications with input/output schemas

### Phase 2: Implementation

**Prerequisites**: Phase 1 complete

**Goal**: Build FastMCP server with all tools

**Steps**:
1. Create MCP server file using FastMCP pattern
2. Implement each tool with proper type hints and docstrings
3. Add database integration for stateless operation
4. Include error handling for invalid inputs

**Output**: Working MCP server at `backend/mcp_server.py`

### Phase 3: Integration

**Prerequisites**: Phase 2 complete

**Goal**: Connect MCP server to OpenAI Agents SDK

**Steps**:
1. Fetch OpenAI Agents SDK docs via Context7: `/openai/openai-agents-python`
2. Configure MCPServerStdio connection pattern
3. Create agent definition with MCP tools
4. Test tool invocation with sample prompts

**Output**: Integrated agent at `backend/chat_agent.py`

## Output Artifacts

This agent produces:
| Artifact | Location | Description |
|----------|----------|-------------|
| MCP Server | `backend/mcp_server.py` | FastMCP server with todo tools |
| Agent Definition | `backend/chat_agent.py` | OpenAI agent with MCP integration |
| Tool Tests | `backend/tests/test_mcp_tools.py` | Tool validation tests |

## Quality Gates

Before completing, verify:
- [ ] All 5 MCP tools implemented (add, list, complete, delete, update)
- [ ] Tools are stateless (all state in database)
- [ ] Error handling for invalid task IDs
- [ ] Context7 documentation used for all implementations

## Error Handling

| Error Type | Response |
|------------|----------|
| Missing database models | ERROR - Complete Phase II first |
| Context7 lookup fails | WARN - Use fallback patterns, document assumption |
| Tool test fails | FIX - Debug and re-implement tool |

## Key Rules

- Use Context7 for MCP SDK and Agents SDK documentation
- All tools must include user_id parameter for isolation
- Return structured JSON responses from tools
- Never store state in MCP server memory
