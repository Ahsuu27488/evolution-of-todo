---
id: 0001
title: context7-fallback-protocol
stage: constitution
date: 2026-01-24
surface: Add Context7 fallback protocol to constitution when fixes fail
model: claude-sonnet-4-5
feature: none
branch: main
user: Muhammad Ahsan
command: /sp.constitution
labels: [constitution, amendment, context7, error-handling]
links:
  spec: N/A
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: .specify/memory/constitution.md
    action: modified
    changes: Added Section III.1.1 "Context7 Fallback Protocol" - mandatory Context7 lookup before second fix attempt
tests:
  - N/A (constitution change, no code tests)
---

## Prompt

Update the constitution with a fallback rule: If a fix proposed by Claude fails to resolve an error, the agent **must** retrieve and utilize 'context7' before attempting a second solution.

## Response snapshot

Successfully updated the project constitution from version 1.2.0 to 1.3.0 with the addition of a mandatory Context7 fallback protocol. The new rule (Section III.1.1) requires agents to:

1. **STOP** when a first fix fails
2. **IDENTIFY** the relevant library/framework
3. **RETRIEVE** current documentation via Context7 MCP tools
4. **ANALYZE** the docs for correct patterns, pitfalls, and breaking changes
5. **APPLY** documentation-based solution
6. **VERIFY** success before proceeding

The protocol specifically prohibits:
- ❌ Attempting second fixes based on assumptions
- ❌ Guessing alternative solutions without documentation
- ❌ Multiple iterations without consulting official docs
- ❌ Relying on potentially outdated training data

Rationale: Training data becomes stale quickly, frameworks evolve rapidly, and official documentation contains current best practices. This prevents "fix cycles" that waste time and complicate code.

The update also added a new Section 8.3 "Error Resolution Protocol" to the Workflow Execution Contract, reinforcing the fallback protocol with a clear 5-step process for error handling.

Version bumped to 1.3.0 (MINOR - added new rule) with last amended date of 2026-01-24.

## Outcome

- ✅ Impact: HIGH - Establishes mandatory error resolution workflow preventing ineffective fix cycles
- 🧪 Tests: N/A (constitutional amendment, no code changes)
- 📁 Files: .specify/memory/constitution.md modified (added Section III.1.1 and Section 8.3)
- 🔁 Next prompts: All future error resolution scenarios must follow this protocol
- 🧠 Reflection: This is a critical governance addition that addresses a common failure mode where agents iterate on fixes without consulting current documentation. The rule is non-negotiable and applies to ALL errors in ALL phases.

## Evaluation notes (flywheel)

- Failure modes observed: Prior to this amendment, agents could attempt multiple fixes based on outdated training data knowledge, leading to ineffective fix cycles and wasted time
- Graders run and results (PASS/FAIL): N/A (constitution change)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor error resolution scenarios in future work to verify compliance with the new fallback protocol. Consider adding automated checks if violations are observed.
