# Sub-Agent Template

Use this template to create new Sub-Agents for Claude Code. Sub-agents are specialized agents that run in isolated context with guaranteed invocation for complex, multi-step tasks.

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Location** | `.claude/agents/<agent-name>.md` |
| **Invocation** | Explicit ("Use the X agent") - Guaranteed |
| **Context** | Separate (isolated conversation) |
| **Best For** | Complex, isolated, multi-step tasks |

## Skills vs Sub-Agents Decision Matrix

| Criteria | Choose Skill | Choose Sub-Agent |
|----------|-------------|------------------|
| **Complexity** | Simple, focused | Complex, multi-step |
| **Invocation** | Automatic (soft) | Explicit (guaranteed) |
| **Context needs** | Shared with main conversation | Isolated/separate |
| **Frequency** | Repeated often | Occasional, specialized |
| **Example** | Blog planning, PDF extraction | Security audit, full refactor |

## Directory Structure

```
.claude/agents/
├── <agent-name>.md           # Agent definition (required)
└── <another-agent>.md
```

## Template

Copy this template to `.claude/agents/<your-agent-name>.md`:

```markdown
---
description: "{{BRIEF_DESCRIPTION}}. {{USE_CASE_TRIGGER}}."
handoffs:
  - label: {{HANDOFF_LABEL}}
    agent: {{NEXT_AGENT_NAME}}
    prompt: {{HANDOFF_PROMPT}}
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

{{AGENT_PURPOSE}}

This agent is invoked when:
- {{INVOCATION_TRIGGER_1}}
- {{INVOCATION_TRIGGER_2}}
- {{INVOCATION_TRIGGER_3}}

## Prerequisites

Before this agent runs:
- [ ] {{PREREQUISITE_1}}: e.g., "Feature spec exists at specs/<feature>/spec.md"
- [ ] {{PREREQUISITE_2}}: e.g., "Constitution loaded from .specify/memory/constitution.md"
- [ ] {{PREREQUISITE_3}}: e.g., "Required dependencies installed"

## Workflow Phases

### Phase 1: {{PHASE_1_NAME}}

**Goal**: {{Phase 1 objective}}

**Steps**:
1. {{Step 1.1}}
2. {{Step 1.2}}
3. {{Step 1.3}}

**Output**: {{Phase 1 deliverable}}

### Phase 2: {{PHASE_2_NAME}}

**Prerequisites**: Phase 1 complete

**Goal**: {{Phase 2 objective}}

**Steps**:
1. {{Step 2.1}}
2. {{Step 2.2}}
3. {{Step 2.3}}

**Output**: {{Phase 2 deliverable}}

### Phase 3: {{PHASE_3_NAME}}

**Prerequisites**: Phase 2 complete

**Goal**: {{Phase 3 objective}}

**Steps**:
1. {{Step 3.1}}
2. {{Step 3.2}}
3. {{Step 3.3}}

**Output**: {{Phase 3 deliverable}}

## Output Artifacts

This agent produces:
| Artifact | Location | Description |
|----------|----------|-------------|
| {{ARTIFACT_1}} | `{{PATH_1}}` | {{Description}} |
| {{ARTIFACT_2}} | `{{PATH_2}}` | {{Description}} |
| {{ARTIFACT_3}} | `{{PATH_3}}` | {{Description}} |

## Quality Gates

Before completing, verify:
- [ ] {{GATE_1}}: e.g., "All placeholders resolved"
- [ ] {{GATE_2}}: e.g., "Output files exist at expected paths"
- [ ] {{GATE_3}}: e.g., "No ERROR states in workflow"

## Error Handling

| Error Type | Response |
|------------|----------|
| {{ERROR_1}} | {{How to handle}} |
| {{ERROR_2}} | {{How to handle}} |
| Missing prerequisite | ERROR and report what's missing |

## Key Rules

- {{RULE_1}}: e.g., "Use absolute paths"
- {{RULE_2}}: e.g., "ERROR on gate failures"
- {{RULE_3}}: e.g., "Never auto-proceed without validation"

---

## Post-Completion (Optional: PHR Creation)

As the main request completes, create a PHR (Prompt History Record):

1) **Determine Stage**: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) **Generate Title and Route**:
   - Title: 3-7 words (slug for filename)
   - Route by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/`
     - `general` → `history/prompts/general/`

3) **Create PHR**: Run `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Fill remaining placeholders, embed PROMPT_TEXT and RESPONSE_TEXT

4) **Validate**: No unresolved placeholders, correct path, print ID + path + stage + title
```

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{BRIEF_DESCRIPTION}}` | What the agent does | `Perform comprehensive security audit` |
| `{{USE_CASE_TRIGGER}}` | When to invoke | `Use when reviewing code for vulnerabilities` |
| `{{HANDOFF_LABEL}}` | Button/link label | `Create Tasks` |
| `{{NEXT_AGENT_NAME}}` | Agent to hand off to | `sp.tasks` |
| `{{AGENT_PURPOSE}}` | Detailed purpose | `Systematically review codebase for security issues` |
| `{{PHASE_N_NAME}}` | Workflow phase title | `Discovery`, `Analysis`, `Report` |
| `{{ARTIFACT_N}}` | Output file/document | `security-report.md` |
| `{{GATE_N}}` | Quality checkpoint | `All critical issues documented` |

## Handoffs Configuration

Handoffs allow agents to chain together:

```yaml
handoffs:
  - label: "Create Implementation Tasks"  # UI label
    agent: sp.tasks                        # Target agent
    prompt: "Break the plan into tasks"   # What to pass
    send: true                            # Auto-send or just suggest
```

### Handoff Patterns

| Pattern | Use Case |
|---------|----------|
| **Sequential** | `plan → tasks → implement` |
| **Conditional** | `analyze → (if issues) fix → verify` |
| **Parallel** | `spec → [design, research]` (manual) |

## Best Practices

### DO
- Define clear phase boundaries with prerequisites
- Include quality gates before completion
- Document all output artifacts with paths
- Handle errors explicitly with responses
- Use handoffs to chain related workflows

### DON'T
- Make phases too granular (cognitive overhead)
- Skip prerequisite validation
- Auto-proceed without gate checks
- Forget error handling for edge cases
- Duplicate logic from other agents

## Agent Categories

Common agent types:

| Category | Examples | Typical Phases |
|----------|----------|----------------|
| **Planning** | sp.plan, sp.spec | Discovery → Design → Validate |
| **Implementation** | sp.implement | Setup → Execute → Verify |
| **Analysis** | sp.analyze, security-audit | Scan → Analyze → Report |
| **Documentation** | docs-generator | Gather → Write → Review |
| **Testing** | test-generator | Identify → Generate → Validate |

## Testing Your Agent

After creating your agent:

1. **Verify discovery**: Ask Claude "What agents are available?"
2. **Test invocation**: "Use the <agent-name> agent to..."
3. **Check phases**: Verify each phase completes with expected outputs
4. **Test handoffs**: Confirm chained agents receive correct context
5. **Error paths**: Trigger error conditions and verify handling

## Example: Security Audit Agent

```markdown
---
description: "Perform comprehensive security audit on codebase. Use when reviewing for vulnerabilities."
handoffs:
  - label: Create Fix Tasks
    agent: sp.tasks
    prompt: Create tasks to fix identified security issues
    send: false
---

## Purpose

Systematically analyze codebase for OWASP Top 10 vulnerabilities,
credential exposure, and security best practices violations.

### Phase 1: Discovery
- Scan for sensitive file patterns (.env, credentials, keys)
- Identify authentication/authorization code paths
- Map data flow for injection points

### Phase 2: Analysis
- Check each discovery against security checklist
- Classify findings by severity (Critical/High/Medium/Low)
- Document reproduction steps

### Phase 3: Report
- Generate security-report.md with findings
- Prioritize remediation order
- Suggest handoff to sp.tasks for fixes

## Quality Gates
- [ ] All OWASP Top 10 categories checked
- [ ] No false positives in Critical/High findings
- [ ] Remediation steps actionable
```
