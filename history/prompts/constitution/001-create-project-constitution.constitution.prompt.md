---
id: 001
title: Create Project Constitution
stage: constitution
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: ahsan
command: user-request
labels: ["constitution", "hackathon", "spec-driven-development", "context7"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution is a governance document)
---

## Prompt

read all the files in Hackathon-docs and Create a strongest constitution file, and some of the additional suggestions are written below:
1. must use context7 mcp and read official documentations of every tool, service, framework, library, or anything that requires knowledge and intelligence, the template for creating the agent skill and sub agents is already available in .claude/templates

## Response snapshot

Created comprehensive constitution file at `.specify/memory/constitution.md` covering:

1. **Spec-Driven Development (SDD) Mandate** - Strict pipeline: Constitution → Specify → Plan → Tasks → Implement
2. **Agent Behavior Rules** - Prohibited and required actions for all AI agents
3. **Context7 MCP Mandate** - Critical requirement to fetch official docs before using any framework/library
4. **Phase Governance** - Strict isolation rules for all 5 hackathon phases with allowed/forbidden concepts
5. **Technology Constraints** - Phase-specific stacks (Python → FastAPI/Next.js → AI Chatbot → K8s → Cloud)
6. **Quality Principles** - Clean architecture, security standards, code standards
7. **Project Structure** - Complete repository layout with specs, history, PHR routing
8. **Workflow Execution Contract** - Minimum acceptance criteria for every request
9. **Governance** - Authority hierarchy, amendment process, compliance rules
10. **Bonus Objectives** - Reusable Intelligence, Cloud-Native Blueprints, Multi-language, Voice

Key additions per user request:
- Context7 MCP tools documented with exact function names and workflow
- Reusable Intelligence section mandating Skills and Sub-Agents creation
- Templates location referenced (.claude/templates/)

## Outcome

- Impact: Established supreme governing document for entire hackathon project
- Tests: N/A (governance document)
- Files: 1 file created (.specify/memory/constitution.md - 305 lines)
- Next prompts: /sp.specify for Phase I, create initial Skills/Sub-Agents
- Reflection: Constitution now enforces Context7 usage and reusable intelligence creation as mandatory, not optional

## Evaluation notes (flywheel)

- Failure modes observed: None - first constitution creation
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment: Test constitution enforcement in Phase I spec creation
