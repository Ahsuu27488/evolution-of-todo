# Data Model: Reusable Intelligence

**Feature**: 001-reusable-intelligence
**Date**: 2025-12-26

## Overview

This feature creates configuration assets (Skills and Agents), not database entities. The "data model" describes the structure of these configuration files.

## Entity: Skill

A lightweight, auto-activated capability that Claude discovers and applies when relevant context is detected.

### Structure

```yaml
# Frontmatter (required)
---
name: string           # Kebab-case identifier (e.g., "context7-lookup")
description: string    # Brief description + trigger conditions
version: string        # Semantic version (e.g., "1.0.0")
---

# Body sections (required)
- When to Use This Skill    # Activation triggers
- How This Skill Works      # Step-by-step workflow
- Output Format             # What the skill produces
- Constraints and Rules     # Limitations and requirements
- Example                   # Input/output demonstration

# Optional
- Supporting Files          # References to scripts or docs
```

### Location

`.claude/skills/<skill-name>/SKILL.md`

### Validation Rules

- name: Required, kebab-case, unique across all skills
- description: Required, 1-2 sentences, includes "Use when" clause
- version: Required, semver format
- All body sections must be present

---

## Entity: Sub-Agent

A complex, isolated workflow with guaranteed invocation for multi-step tasks.

### Structure

```yaml
# Frontmatter (required)
---
description: string    # Brief description + use case trigger
handoffs:              # Optional: chain to other agents
  - label: string      # UI button label
    agent: string      # Target agent name
    prompt: string     # What to pass
    send: boolean      # Auto-send or suggest
---

# Body sections (required)
- User Input           # $ARGUMENTS placeholder
- Purpose              # Detailed purpose + invocation triggers
- Prerequisites        # Checklist before running
- Workflow Phases      # Multi-phase execution plan
- Output Artifacts     # What the agent produces (table)
- Quality Gates        # Checklist before completion
- Error Handling       # Error types and responses (table)
- Key Rules            # Constraints and requirements
```

### Location

`.claude/agents/<agent-name>.md`

### Validation Rules

- description: Required, includes use case trigger
- At least 2 workflow phases defined
- Quality gates must be checkboxes
- Error handling must be a table

---

## Entity: Phase

A hackathon development stage with specific technology boundaries.

### Structure

| Field | Type | Description |
|-------|------|-------------|
| number | int | Phase number (I-V) |
| name | string | Phase name |
| scope | string | Brief description |
| allowed | list[string] | Allowed features/technologies |
| forbidden | list[string] | Forbidden features/technologies |

### Values

Defined in Constitution §IV.4.2 and encoded in `phase-guard` skill.

---

## Entity: Task Model

Standard todo item structure used across all phases.

### Phase I Structure (In-Memory)

| Field | Type | Constraints |
|-------|------|-------------|
| id | int | Auto-incremented, unique |
| title | string | Required, 1-200 chars |
| description | string | Optional, max 1000 chars |
| completed | bool | Default: false |

### Phase II+ Structure (Database)

| Field | Type | Constraints |
|-------|------|-------------|
| id | int | Primary key, auto-increment |
| user_id | string | Foreign key to users, indexed |
| title | string | Not null, max 200 chars |
| description | string | Nullable, max 1000 chars |
| completed | bool | Default: false |
| created_at | datetime | Auto-set on create |
| updated_at | datetime | Auto-set on update |

Defined in `todo-domain` skill reference.

---

## Relationships

```
Constitution
    └── defines → Phase boundaries
    └── mandates → Context7 usage

Skill
    └── references → Constitution rules
    └── uses → Context7 MCP (context7-lookup)
    └── enforces → Phase boundaries (phase-guard)
    └── applies → Task Model (todo-domain)
    └── validates → Specifications (spec-validator)

Sub-Agent
    └── handoffs to → Other agents
    └── uses → Skills (implicitly)
    └── produces → Output artifacts
    └── follows → Workflow phases
```

---

## State Transitions

### Skill States

Skills are stateless - they activate when triggers match and complete when workflow finishes.

### Agent States

```
IDLE → INVOKED → PHASE_1 → PHASE_2 → ... → PHASE_N → COMPLETE
                     ↓                         ↓
                   ERROR ←───────────────── ERROR
```

Agents can ERROR from any phase if quality gates fail or prerequisites are missing.
