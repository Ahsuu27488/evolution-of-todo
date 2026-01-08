---
name: "spec-validator"
description: "Validate specs against constitution and quality criteria. Use when reviewing or creating specifications."
version: "1.0.0"
---

# Spec Validator Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User runs /sp.specify or creates a feature spec
- Reviewing specification documents for quality
- Before transitioning from spec to plan phase

## How This Skill Works

Step-by-step workflow:
1. **Load Spec**: Read the specification document
2. **Check Structure**: Verify all mandatory sections present
3. **Validate Content**: Ensure no implementation details leaked
4. **Report Issues**: List any quality violations found

## Output Format

Provide structured output:
- **Spec Path**: Location of validated spec
- **Status**: PASS or NEEDS_FIXES
- **Issues**: List of problems found (if any)

## Constraints and Rules

- Specs must focus on WHAT, never HOW
- No technology names in specs (no FastAPI, Next.js, etc.)
- All requirements must be testable
- Success criteria must be measurable and technology-agnostic
- Maximum 3 [NEEDS CLARIFICATION] markers allowed

## Example

**Input**: Review spec at `specs/phase-1/spec.md`

**Output**:
```
Spec Path: specs/phase-1/spec.md
Status: NEEDS_FIXES
Issues:
- Line 45: Contains implementation detail "using Python dict"
- Line 67: Success criteria mentions "response time" (too technical)
- Line 89: Requirement not testable - vague "should be fast"
```

## Supporting Files (Optional)

- `reference/quality-checklist.md`: Full quality validation criteria
