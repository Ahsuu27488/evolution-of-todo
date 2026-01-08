# Specification Quality Checklist

## Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

## Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain (or max 3)
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Success criteria are technology-agnostic
- [ ] All acceptance scenarios are defined
- [ ] Edge cases are identified
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

## Feature Readiness
- [ ] All functional requirements have clear acceptance criteria
- [ ] User scenarios cover primary flows
- [ ] Feature meets measurable outcomes defined in Success Criteria
- [ ] No implementation details leak into specification

## Red Flags to Check

### Implementation Leaks
- Database names (PostgreSQL, Neon, etc.)
- Framework names (FastAPI, Next.js, etc.)
- API response formats (JSON structure)
- Technical metrics (response time, TPS)

### Vague Requirements
- "Should be fast" → Replace with "Users see results within 2 seconds"
- "Easy to use" → Replace with "Task completion in under 3 clicks"
- "Secure" → Replace with "Only authenticated users can access"

### Missing Context
- Who is the user?
- What is the trigger for this feature?
- What happens on success?
- What happens on failure?
