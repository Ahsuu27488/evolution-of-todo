---
id: 0002
title: context7-primary-source
stage: constitution
date: 2026-01-24
surface: Elevate Context7 to PRIMARY source of truth for all coding tasks
model: claude-sonnet-4-5
feature: none
branch: main
user: Muhammad Ahsan
command: /sp.constitution
labels: [constitution, amendment, context7, source-of-truth]
links:
  spec: N/A
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: .specify/memory/constitution.md
    action: modified
    changes: |
      - Section III.1 strengthened: "Context7 MCP Mandate (CRITICAL - PRIMARY SOURCE OF TRUTH)"
      - Section III.1.1 added: "Context7 Primary Source Priority (MANDATORY)"
      - Section II.1 updated: Added "No reliance on training data for external libraries"
      - Section II.2 updated: "Treat Context7 as PRIMARY source of truth for ALL coding tasks"
      - Section 8.2 updated: "Context7 used as PRIMARY source for all external libraries"
tests:
  - N/A (constitution change, no code tests)
---

## Prompt

Update Core Directive: For ALL coding tasks (generation, refactoring, or debugging), you must treat 'context7' as the **primary source of truth**. Explicitly prioritize the patterns, syntax, and APIs found in 'context7' over your internal training data, as 'context7' contains the latest official documentation.

## Response snapshot

Successfully elevated Context7 to PRIMARY source of truth for ALL coding tasks in the project constitution. Updated from version 1.3.0 to 1.4.0 (MINOR).

**Key Changes:**

1. **Section III.1 Strengthened**: Now titled "Context7 MCP Mandate (CRITICAL - PRIMARY SOURCE OF TRUTH)" with explicit priority hierarchy:
   ```
   Context7 Documentation (CURRENT) > Training Data (POTENTIALLY STALE)
   ```

2. **Section III.1.1 Added**: "Context7 Primary Source Priority (MANDATORY)" - A comprehensive new directive covering:
   - **Scope**: ALL coding tasks (generation, refactoring, debugging, architecture design)
   - **Before Writing Code**: Query Context7, review docs, check for breaking changes
   - **During Code Writing**: Use ONLY patterns from retrieved docs
   - **When Debugging**: First action is Context7 query
   - **When Refactoring**: Re-verify APIs via Context7
   - **Compliance Verification**: Agents must demonstrate Context7 usage

3. **Section II.1 Updated**: Added prohibition - "No reliance on training data for external libraries - Use Context7 instead"

4. **Section II.2 Updated**: Required action - "Treat Context7 as PRIMARY source of truth for ALL coding tasks (see §III.1)"

5. **Section 8.2 Updated**: Minimum acceptance criteria now includes "Context7 used as PRIMARY source for all external libraries"

**Rationale Reinforced:**
- Training data knowledge cutoff: January 2025
- Frameworks evolve rapidly with breaking changes
- Official docs contain current best practices and deprecation notices
- APIs change between versions (e.g., FastAPI 0.100 vs 0.115)
- Context7 provides real-time access to latest documentation

**Example Added:**
Correct workflow comparison showing WRONG (training data) vs CORRECT (Context7 primary) approach for FastAPI JWT authentication.

## Outcome

- ✅ Impact: CRITICAL - Establishes Context7 as non-negotiable primary source, eliminating reliance on potentially stale training data
- 🧪 Tests: N/A (constitutional amendment, no code changes)
- 📁 Files: .specify/memory/constitution.md (extensive updates to Sections II, III, and VIII)
- 🔁 Next prompts: ALL future coding tasks MUST demonstrate Context7 as primary source
- 🧠 Reflection: This amendment transforms Context7 from "best practice" to "constitutional requirement" with explicit compliance verification. It addresses the fundamental issue that AI training data has temporal limitations while official documentation is continuously updated.

## Evaluation notes (flywheel)

- Failure modes observed: Prior to this amendment, agents could rely on training data knowledge (cutoff: Jan 2025) leading to use of deprecated APIs, outdated patterns, and incorrect assumptions about library behavior
- Graders run and results (PASS/FAIL): N/A (constitution change)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor compliance with Context7-primary directive in upcoming coding tasks. Consider implementing automated verification checks if violations occur. Track correlation between Context7 usage and successful implementations.
