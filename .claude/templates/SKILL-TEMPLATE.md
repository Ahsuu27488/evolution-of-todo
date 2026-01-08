# Skill Template

Use this template to create new Agent Skills for Claude Code. Skills are reusable capabilities that Claude automatically discovers and applies when relevant context is detected.

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Location** | `.claude/skills/<skill-name>/SKILL.md` |
| **Invocation** | Automatic (Claude decides when relevant) |
| **Context** | Shared (main conversation) |
| **Best For** | Lightweight, repeatable capabilities |

## Directory Structure

```
.claude/skills/<skill-name>/
├── SKILL.md                 # Main instructions (required)
├── scripts/                 # Optional: helper scripts
│   └── helper.py
└── reference/               # Optional: reference docs
    └── standards.md
```

## Template

Copy this template to `.claude/skills/<your-skill-name>/SKILL.md`:

```markdown
---
name: "{{SKILL_NAME}}"
description: "{{BRIEF_DESCRIPTION}}. Use when {{TRIGGER_CONDITIONS}}."
version: "1.0.0"
---

# {{SKILL_TITLE}}

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- {{TRIGGER_1}}: e.g., "User asks to plan a blog post"
- {{TRIGGER_2}}: e.g., "User mentions blog topics or headlines"
- {{TRIGGER_3}}: e.g., "User uploads a specific file type"

## How This Skill Works

Step-by-step workflow:
1. **{{STEP_1_NAME}}**: {{Step 1 description}}
2. **{{STEP_2_NAME}}**: {{Step 2 description}}
3. **{{STEP_3_NAME}}**: {{Step 3 description}}
4. **{{STEP_4_NAME}}**: {{Step 4 description}}

## Output Format

Provide structured output:
- **{{OUTPUT_1}}**: {{Description}}
- **{{OUTPUT_2}}**: {{Description}}
- **{{OUTPUT_3}}**: {{Description}}

## Constraints and Rules

- {{CONSTRAINT_1}}: e.g., "Keep responses under 500 words"
- {{CONSTRAINT_2}}: e.g., "Always include actionable items"
- {{CONSTRAINT_3}}: e.g., "Follow project coding standards"

## Example

**Input**: "{{EXAMPLE_USER_INPUT}}"

**Output**:
{{EXAMPLE_OUTPUT}}

## Supporting Files (Optional)

If this skill requires external tools or references:
- `scripts/{{script_name}}.py`: {{Purpose}}
- `reference/{{doc_name}}.md`: {{Purpose}}
```

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{SKILL_NAME}}` | Kebab-case identifier | `blog-planner` |
| `{{BRIEF_DESCRIPTION}}` | 1-2 sentence purpose | `Help plan engaging blog posts` |
| `{{TRIGGER_CONDITIONS}}` | When to activate | `user asks to plan or write blog content` |
| `{{SKILL_TITLE}}` | Human-readable title | `Blog Planning Skill` |
| `{{TRIGGER_N}}` | Specific activation patterns | `User mentions blog topics` |
| `{{STEP_N_NAME}}` | Workflow step name | `Research the topic` |
| `{{OUTPUT_N}}` | Output component | `Topic Summary` |
| `{{CONSTRAINT_N}}` | Rule or limitation | `Keep paragraphs under 4 sentences` |

## Best Practices

### DO
- Keep descriptions concise but specific for accurate activation
- Include 2-3 concrete examples in the skill file
- Define clear output formats for consistency
- Test activation with various phrasings

### DON'T
- Make triggers too broad (causes false activations)
- Include complex multi-step workflows (use subagents instead)
- Duplicate logic already in other skills
- Forget to version your skill updates

## Skill Categories

Common skill types to consider:

| Category | Examples | Typical Triggers |
|----------|----------|------------------|
| **Content** | blog-planner, docs-writer | "write", "draft", "create content" |
| **Analysis** | code-reviewer, log-analyzer | "review", "analyze", "check" |
| **Organization** | meeting-notes, task-organizer | "organize", "summarize", "structure" |
| **Extraction** | pdf-extractor, data-parser | file uploads, "extract", "parse" |
| **Learning** | learning-path, tutorial-creator | "learn", "teach", "explain how" |

## Testing Your Skill

After creating your skill:

1. **Restart Claude Code** to discover the new skill
2. **Test activation**: Use natural language that should trigger it
3. **Verify output**: Check if output matches your defined format
4. **Edge cases**: Try variations that should/shouldn't activate

Ask Claude: "What skills do you have?" to verify discovery.

## When to Use Skills vs Subagents

| Use Skills When | Use Subagents When |
|-----------------|-------------------|
| Task is predictable and repeatable | Task is complex with many variables |
| Automatic activation preferred | Guaranteed execution needed |
| Multiple similar tasks per session | Isolated context required |
| Simple, focused capability | Multi-step specialized workflows |
