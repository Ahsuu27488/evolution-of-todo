# Quickstart: Reusable Intelligence

**Feature**: 001-reusable-intelligence
**Date**: 2025-12-26

## Overview

This feature provides 4 Skills and 4 Sub-Agents for the Evolution of Todo hackathon. These assets are automatically discovered by Claude Code and help enforce hackathon rules, fetch documentation, and provide specialized workflows.

## Prerequisites

- Claude Code CLI installed and configured
- Context7 MCP server available
- Project cloned with `.claude/` directory structure

## Skills Usage

### 1. context7-lookup

**Purpose**: Fetch official documentation before implementing with external libraries.

**Auto-activates when**: You mention FastAPI, Next.js, MCP SDK, or other libraries.

**Example**:
```
You: "Implement an MCP server with tools for task management"
Claude: [Automatically fetches MCP Python SDK docs via Context7]
```

### 2. phase-guard

**Purpose**: Prevent implementing features from wrong phases.

**Auto-activates when**: You request features that might belong to different phases.

**Example**:
```
You: "Add database persistence to the console app"
Claude: "BLOCKED - Databases are forbidden in Phase I. This belongs in Phase II."
```

### 3. todo-domain

**Purpose**: Apply standard task data models consistently.

**Auto-activates when**: You implement todo/task features.

**Example**:
```
You: "Implement mark task complete"
Claude: [Uses standard Task model with completed boolean]
```

### 4. spec-validator

**Purpose**: Validate specifications before planning.

**Auto-activates when**: You create or review specifications.

**Example**:
```
You: "Review my spec for quality"
Claude: [Checks for implementation details, vague requirements, testability]
```

## Agents Usage

Agents require explicit invocation: "Use the X agent to..."

### 1. mcp-server-builder

**Purpose**: Build MCP servers for Phase III chatbot.

**Invoke**:
```
"Use the mcp-server-builder agent to create the todo MCP server"
```

**Produces**: `backend/mcp_server.py`, `backend/chat_agent.py`

### 2. k8s-deployer

**Purpose**: Deploy to Kubernetes for Phase IV/V.

**Invoke**:
```
"Use the k8s-deployer agent to containerize and deploy the application"
```

**Produces**: Dockerfiles, Helm charts, deployment scripts

### 3. dapr-integrator

**Purpose**: Integrate Dapr for Phase V event-driven architecture.

**Invoke**:
```
"Use the dapr-integrator agent to set up Kafka pub/sub"
```

**Produces**: Dapr components, event handlers

### 4. fullstack-scaffolder

**Purpose**: Scaffold Phase II project structure.

**Invoke**:
```
"Use the fullstack-scaffolder agent to create the web app structure"
```

**Produces**: `frontend/`, `backend/`, `docker-compose.yml`

## Verification

### Check Skills Discovery

```
You: "What skills do you have?"
```

Expected: Lists context7-lookup, phase-guard, todo-domain, spec-validator

### Check Agents Discovery

```
You: "What agents are available?"
```

Expected: Lists mcp-server-builder, k8s-deployer, dapr-integrator, fullstack-scaffolder

## File Locations

```
.claude/
├── skills/
│   ├── context7-lookup/SKILL.md
│   ├── phase-guard/SKILL.md
│   ├── todo-domain/SKILL.md
│   └── spec-validator/SKILL.md
└── agents/
    ├── mcp-server-builder.md
    ├── k8s-deployer.md
    ├── dapr-integrator.md
    └── fullstack-scaffolder.md
```

## Troubleshooting

### Skills not activating

1. Verify files exist in `.claude/skills/<name>/SKILL.md`
2. Restart Claude Code to re-discover skills
3. Check that triggers match your request phrasing

### Agents not found

1. Verify files exist in `.claude/agents/<name>.md`
2. Use explicit invocation: "Use the <agent-name> agent"
3. Check agent description matches your use case

### Context7 not working

1. Verify Context7 MCP server is configured
2. Check `mcp__plugin_context7_context7__resolve-library-id` is available
3. Try searching for a known library to test connection
