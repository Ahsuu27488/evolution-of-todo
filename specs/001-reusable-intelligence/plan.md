# Implementation Plan: Reusable Intelligence

**Branch**: `001-reusable-intelligence` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-reusable-intelligence/spec.md`

## Summary

Create a suite of reusable intelligence assets (4 Skills + 4 Sub-Agents) that enforce hackathon rules, fetch documentation via Context7 MCP, and provide specialized workflows for each phase. These assets follow Claude Code's skill/agent templates and are designed for reuse across all 5 hackathon phases and future projects.

## Technical Context

**Language/Version**: Markdown (Skills/Agents are configuration files, not code)
**Primary Dependencies**: Claude Code Skills/Agents system, Context7 MCP
**Storage**: File-based (`.claude/skills/`, `.claude/agents/`)
**Testing**: Manual invocation testing ("What skills do you have?", "Use the X agent")
**Target Platform**: Claude Code CLI environment
**Project Type**: Configuration/Intelligence assets (not traditional software)
**Performance Goals**: N/A (configuration files)
**Constraints**: Must follow templates from `.claude/templates/`, must be portable to other projects
**Scale/Scope**: 4 Skills, 4 Sub-Agents, supporting all 5 hackathon phases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| §I.1.1 SDD Pipeline | PASS | Skills/Agents support the spec→plan→tasks→implement flow |
| §II.2.2 Context7 Mandate | PASS | context7-lookup skill enforces this requirement |
| §III.3.2 Reusable Intelligence | PASS | Primary focus of this feature |
| §IV.4.1 Phase Isolation | PASS | phase-guard skill enforces this requirement |
| §VI.6.1 Clean Architecture | PASS | Skills are lightweight, Agents handle complexity |
| §X.10.1 Bonus: Reusable Intelligence | TARGET | This feature earns +200 bonus points |

**Gate Result**: PASS - No violations detected

## Project Structure

### Documentation (this feature)

```text
specs/001-reusable-intelligence/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # N/A - no API contracts for config files
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
.claude/
├── skills/
│   ├── context7-lookup/
│   │   ├── SKILL.md           # Documentation lookup skill
│   │   └── reference/
│   │       └── library-ids.md # Quick reference for hackathon stack
│   ├── phase-guard/
│   │   ├── SKILL.md           # Phase boundary enforcement
│   │   └── reference/
│   │       └── phase-rules.md # Phase isolation rules
│   ├── todo-domain/
│   │   ├── SKILL.md           # Todo app domain knowledge
│   │   └── reference/
│   │       └── data-models.md # Standard data models per phase
│   └── spec-validator/
│       ├── SKILL.md           # Specification quality checker
│       └── reference/
│           └── quality-checklist.md # Validation criteria
├── agents/
│   ├── mcp-server-builder.md  # Phase III MCP server creation
│   ├── k8s-deployer.md        # Phase IV/V Kubernetes deployment
│   ├── dapr-integrator.md     # Phase V Dapr integration
│   └── fullstack-scaffolder.md # Phase II project scaffolding
└── templates/
    ├── SKILL-TEMPLATE.md      # Template for new skills
    └── AGENT-TEMPLATE.md      # Template for new agents
```

**Structure Decision**: Configuration-based structure under `.claude/` directory following Claude Code conventions. No traditional `src/` structure needed since these are intelligence assets, not executable code.

## Complexity Tracking

> **No violations requiring justification**

All assets follow the template patterns. No additional complexity introduced.

---

## Phase 0: Research

### Research Questions

Since this feature creates configuration files (Skills/Agents) rather than executable code, the research focuses on:

1. **Claude Code Skill Format**: What is the exact structure required?
2. **Claude Code Agent Format**: What is the exact structure required?
3. **Context7 MCP Tools**: What are the exact function signatures?
4. **Hackathon Phase Rules**: What are the exact boundaries per phase?

### Findings

All questions were answered during the spec phase by:
- Reading `.claude/templates/SKILL-TEMPLATE.md` and `AGENT-TEMPLATE.md`
- Fetching Context7 documentation for Claude Code (`/anthropics/claude-code`)
- Analyzing hackathon docs in `Hackathon-docs/`
- Reading the constitution for phase boundaries

**No additional research needed** - all clarifications resolved during specification.

---

## Phase 1: Design

### Data Model

Since this feature creates configuration files, the "data model" is the structure of Skills and Agents:

#### Skill Structure
```yaml
---
name: "skill-name"
description: "Brief description. Use when trigger conditions."
version: "1.0.0"
---

# Skill Title

## When to Use This Skill
- Activation trigger 1
- Activation trigger 2

## How This Skill Works
1. Step 1
2. Step 2

## Output Format
- Output component 1
- Output component 2

## Constraints and Rules
- Constraint 1
- Constraint 2

## Example
Input: "example"
Output: "result"
```

#### Agent Structure
```yaml
---
description: "Brief description. Use case trigger."
handoffs:
  - label: Handoff Label
    agent: next-agent
    prompt: What to pass
    send: true/false
---

## User Input
$ARGUMENTS

## Purpose
Agent purpose and invocation triggers

## Prerequisites
- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Workflow Phases
### Phase 1: Name
Goal, Steps, Output

### Phase 2: Name
Goal, Steps, Output

## Output Artifacts
| Artifact | Location | Description |

## Quality Gates
- [ ] Gate 1
- [ ] Gate 2

## Error Handling
| Error Type | Response |

## Key Rules
- Rule 1
- Rule 2
```

### Contracts

N/A - This feature creates configuration files, not APIs. No contracts needed.

### Integration Points

| Asset | Integrates With | Purpose |
|-------|-----------------|---------|
| context7-lookup | Context7 MCP Server | Fetch documentation |
| phase-guard | Constitution §IV | Enforce phase boundaries |
| todo-domain | Spec data models | Apply consistent models |
| spec-validator | Spec template | Validate quality |
| mcp-server-builder | MCP Python SDK | Build Phase III servers |
| k8s-deployer | Docker, Helm, kubectl | Phase IV/V deployments |
| dapr-integrator | Dapr CLI, Components | Phase V event-driven |
| fullstack-scaffolder | Next.js, FastAPI | Phase II structure |

---

## Implementation Status

**Status**: COMPLETE

All 4 Skills and 4 Sub-Agents have been created following the templates:

### Skills Created
| Skill | Status | Files |
|-------|--------|-------|
| context7-lookup | Complete | SKILL.md, reference/library-ids.md |
| phase-guard | Complete | SKILL.md, reference/phase-rules.md |
| todo-domain | Complete | SKILL.md, reference/data-models.md |
| spec-validator | Complete | SKILL.md, reference/quality-checklist.md |

### Agents Created
| Agent | Status | File |
|-------|--------|------|
| mcp-server-builder | Complete | mcp-server-builder.md |
| k8s-deployer | Complete | k8s-deployer.md |
| dapr-integrator | Complete | dapr-integrator.md |
| fullstack-scaffolder | Complete | fullstack-scaffolder.md |

---

## Next Steps

1. Run `/sp.tasks` to generate formal task breakdown (optional - assets already complete)
2. Test skills by asking "What skills do you have?"
3. Test agents by invoking "Use the mcp-server-builder agent"
4. Proceed to Phase I specification with `/sp.specify` for the todo console app
