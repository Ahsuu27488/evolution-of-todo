---
name: "phase-guard"
description: "Enforce phase isolation rules from constitution. Use when implementing features to prevent scope creep."
version: "1.0.0"
---

# Phase Guard Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User requests a feature that might belong to a different phase
- Implementation mentions technologies not allowed in current phase
- Code review or implementation task for any hackathon phase

## How This Skill Works

Step-by-step workflow:
1. **Detect Phase**: Identify current phase from context or spec location
2. **Check Scope**: Validate requested feature against phase boundaries
3. **Flag Violations**: Report if feature belongs to future/past phase
4. **Suggest Fix**: Recommend proper phase or spec update if needed

## Output Format

Provide structured output:
- **Current Phase**: Phase number and name
- **Requested Feature**: What user asked for
- **Verdict**: ALLOWED or BLOCKED with reason

## Constraints and Rules

- NEVER allow future-phase features to leak into earlier phases
- Reference constitution Section IV for phase boundaries
- Block implementation if phase mismatch detected
- Suggest updating spec if feature scope unclear

## Example

**Input**: "Add database persistence to Phase I console app"

**Output**:
```
Current Phase: Phase I (In-Memory Console)
Requested Feature: Database persistence
Verdict: BLOCKED - Databases are forbidden in Phase I per constitution §IV.4.2
Recommendation: This feature belongs in Phase II (Full-Stack Web)
```

## Supporting Files (Optional)

- `reference/phase-rules.md`: Phase isolation rules from constitution
