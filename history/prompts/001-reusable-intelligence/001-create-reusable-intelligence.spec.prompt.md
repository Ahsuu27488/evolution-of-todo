---
id: 001
title: Create Reusable Intelligence Assets
stage: spec
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: 001-reusable-intelligence
branch: 001-reusable-intelligence
user: ahsan
command: /sp.specify
labels: ["reusable-intelligence", "skills", "agents", "context7", "hackathon"]
links:
  spec: specs/001-reusable-intelligence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/context7-lookup/SKILL.md
  - .claude/skills/context7-lookup/reference/library-ids.md
  - .claude/skills/phase-guard/SKILL.md
  - .claude/skills/phase-guard/reference/phase-rules.md
  - .claude/skills/todo-domain/SKILL.md
  - .claude/skills/todo-domain/reference/data-models.md
  - .claude/skills/spec-validator/SKILL.md
  - .claude/skills/spec-validator/reference/quality-checklist.md
  - .claude/agents/mcp-server-builder.md
  - .claude/agents/k8s-deployer.md
  - .claude/agents/dapr-integrator.md
  - .claude/agents/fullstack-scaffolder.md
  - specs/001-reusable-intelligence/spec.md
tests:
  - Skills discoverable via "What skills do you have?"
  - Agents invocable via "Use the X agent"
---

## Prompt

/sp.specify Reusable intelligence - read all the hackathon docs and then create the needed agent-skills and subagents using context7 mcp based on the templates available inside .claude/templates

## Response snapshot

Created comprehensive reusable intelligence assets for the Evolution of Todo hackathon:

**Skills Created (4):**
1. `context7-lookup` - Fetches official documentation for libraries/frameworks via Context7 MCP before implementation
2. `phase-guard` - Enforces phase isolation rules from constitution to prevent scope creep
3. `todo-domain` - Applies standard todo app data models and feature level knowledge
4. `spec-validator` - Validates specifications against quality criteria before planning

**Sub-Agents Created (4):**
1. `mcp-server-builder` - Builds MCP servers with tools for Phase III chatbot
2. `k8s-deployer` - Handles Docker and Kubernetes deployment for Phase IV/V
3. `dapr-integrator` - Integrates Dapr building blocks for Phase V event-driven architecture
4. `fullstack-scaffolder` - Scaffolds Phase II Next.js/FastAPI structure

All assets follow the templates from `.claude/templates/` and include:
- YAML frontmatter with description and triggers
- Step-by-step workflows
- Output formats and constraints
- Reference documentation files
- Quality gates and error handling

## Outcome

- Impact: Created foundational reusable intelligence for entire hackathon (+200 bonus points eligible)
- Tests: Skills auto-activate on relevant triggers; Agents invocable explicitly
- Files: 13 files created (4 skills with references, 4 agents, 1 spec)
- Next prompts: /sp.plan for Phase I, test skills by implementing Phase I features
- Reflection: Context7 documentation lookup is the most critical skill - ensures all implementations use current APIs

## Evaluation notes (flywheel)

- Failure modes observed: Initial skill format didn't match template exactly - corrected after reading templates
- Graders run and results (PASS/FAIL): Manual validation - skills follow template structure
- Prompt variant (if applicable): N/A
- Next experiment: Test context7-lookup skill activation during Phase I implementation
