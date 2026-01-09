---
name: spec-validator
description: Validate specs against constitution and quality criteria. Use when reviewing or creating specifications.
version: 2.0.0
---

# Spec Validator Mastery Skill

## Purpose

Ensures specifications meet **quality standards** and follow the spec-driven development methodology.

## When to Use This Skill

Activation triggers:
- User runs `/sp.specify` or creates a feature spec
- Reviewing specification documents for quality
- Before transitioning from spec to plan phase
- Validating spec completeness

## Validation Checklist

### 1. Structure Validation

All specs MUST have these sections:

| Section | Required | Description |
|---------|----------|-------------|
| **Feature Name** | ✅ | Clear, concise name |
| **User Stories** | ✅ | At least one user story |
| **Acceptance Criteria** | ✅ | Testable, measurable criteria |
| **Success Metrics** | ✅ | How we know it's "done" |
| **Out of Scope** | ✅ | What we're NOT building |

### 2. Content Quality Rules

#### ✅ DO

- **Focus on WHAT**, not HOW
- Use technology-agnostic language
- Write testable acceptance criteria
- Include specific success metrics
- Keep scope minimal and focused
- Use `NEEDS CLARIFICATION` sparingly (max 3)

#### ❌ DON'T

- Mention specific technologies (FastAPI, Next.js, etc.)
- Include implementation details
- Write vague or untestable criteria
- Over-specify edge cases
- Include "nice to have" features

### 3. Acceptance Criteria Format

Good acceptance criteria follow this pattern:

```
GIVEN [precondition]
WHEN [action/trigger]
THEN [observable outcome]
```

**Example**:
```
GIVEN a user has created tasks
WHEN they filter by "high priority"
THEN only tasks with priority=HIGH are displayed
```

### 4. Success Metrics

Must be **measurable** and **objective**:

| ❌ BAD | ✅ GOOD |
|--------|---------|
| "Should be fast" | "API responds < 200ms p95" |
| "Easy to use" | "Completes task in < 3 clicks" |
| "Works well" | "95% success rate on integration tests" |
| "Looks good" | "Matches design mockups in review" |

## Validation Process

### Step 1: Read Spec

```bash
# Locate spec file
specs/<feature-name>/spec.md
```

### Step 2: Check Structure

```python
def validate_structure(spec_path: str) -> ValidationResult:
    """Validate required sections exist."""
    required_sections = [
        "# Feature",
        "## User Stories",
        "## Acceptance Criteria",
        "## Success Metrics",
        "## Out of Scope"
    ]

    content = read_file(spec_path)
    missing = [s for s in required_sections if s not in content]

    if missing:
        return ValidationResult(
            status="FAIL",
            message=f"Missing sections: {missing}"
        )

    return ValidationResult(status="PASS")
```

### Step 3: Check Content Quality

```python
def validate_content(spec_path: str) -> ValidationResult:
    """Validate content follows rules."""
    content = read_file(spec_path)

    # Check for technology names (violation)
    tech_violations = []
    for tech in ["FastAPI", "Next.js", "React", "SQLModel", "Tailwind"]:
        if tech in content:
            tech_violations.append(tech)

    if tech_violations:
        return ValidationResult(
            status="FAIL",
            message=f"Technology names found (should be agnostic): {tech_violations}"
        )

    # Check NEEDS CLARIFICATION count
    nc_count = content.count("NEEDS CLARIFICATION")
    if nc_count > 3:
        return ValidationResult(
            status="FAIL",
            message=f"Too many NEEDS CLARIFICATION markers ({nc_count}/3 max)"
        )

    return ValidationResult(status="PASS")
```

## Output Format

```
┌─────────────────────────────────────────────────────────────────┐
│                     SPEC VALIDATION REPORT                     │
├─────────────────────────────────────────────────────────────────┤
│ Spec: specs/phase-2/user-authentication/spec.md                │
│ Status: ✅ PASS / ❌ FAIL                                        │
│                                                                 │
│ Issues Found:                                                   │
│   [❌] Line 45: Contains "FastAPI" (technology specific)       │
│   [❌] "NEEDS CLARIFICATION" count: 5 (max 3)                  │
│   [⚠️]  Acceptance criteria not testable (line 67)             │
│                                                                 │
│ Recommendations:                                                │
│   1. Replace "FastAPI" with "web API backend"                  │
│   2. Reduce clarification markers to 3 or fewer                 │
│   3. Rewrite criteria to use GIVEN/WHEN/THEN format            │
└─────────────────────────────────────────────────────────────────┘
```

## Common Issues

| Issue | Pattern | Fix |
|-------|---------|-----|
| Technology specific | "Use FastAPI to create..." | "Create a web API that..." |
| Implementation detail | "Store in PostgreSQL with..." | "Persist data for retrieval..." |
| Untestable criteria | "User experience is good" | "Task creation completes in < 2 seconds" |
| How instead of what | "Implement with React hooks..." | "User can toggle task completion..." |
| Vague requirements | "Should work well" | "Supports 100 concurrent users" |

## Validation Commands

```bash
# Validate a specific spec
python -m tools.validate_spec specs/<feature>/spec.md

# Validate all specs
python -m tools.validate_spec --all

# Auto-fix common issues
python -m tools.validate_spec --fix specs/<feature>/spec.md
```

## Example Validation

**Input Spec** (excerpt):
```markdown
## Acceptance Criteria

1. User can sign up with email using FastAPI
2. Use Next.js form with shadcn/ui components
3. Should load fast
```

**Validation Result**:
```markdown
❌ FAIL - Quality Issues Found

Issues:
  - Line 1: "FastAPI" is technology-specific
  - Line 2: "Next.js" and "shadcn/ui" are technologies
  - Line 3: "load fast" is not measurable

Suggested Rewrite:
```markdown
## Acceptance Criteria

GIVEN a new user visits the sign-up page
WHEN they submit a valid email and password
THEN their account is created and they are redirected to dashboard

GIVEN an existing user
WHEN they enter credentials
THEN they are logged in within 2 seconds
```
```

## Supporting Files

- `.specify/templates/spec-template.md`: Spec template
- `.specify/memory/constitution.md`: Quality standards
- `tools/validate_spec.py`: Validation script

## References

- **Spec Template**: `.specify/templates/spec-template.md`
- **Quality Criteria**: `.specify/memory/constitution.md §III`
