---
name: "helm-guide"
description: "Fetch Helm documentation and apply chart best practices. Use when creating Helm charts, templates, or managing releases (Phase IV+)."
version: "1.0.0"
---

# Helm Chart Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions Helm charts, templates, or releases
- Implementation requires packaging K8s manifests as Helm charts
- User asks about values.yaml, Chart.yaml, or Helm templating
- Phase IV deployment packaging begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Need**: Detect Helm-related requirement from context
2. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with `/helm/helm` and relevant topic
3. **Apply Patterns**: Use official Helm patterns for chart structure and templating
4. **Validate**: Ensure chart follows best practices (values schema, hooks, tests)

## Output Format

Provide structured output:
- **Context7 Source**: `/helm/helm`
- **Chart Structure**: Files being created/modified
- **Template Functions**: Helm functions used
- **Best Practices**: Applied patterns

## Constraints and Rules

- ALWAYS include Chart.yaml with proper metadata
- ALWAYS provide values.yaml with documented defaults
- Use named templates for reusable snippets
- Include NOTES.txt for post-install instructions
- Add schema validation with values.schema.json
- This skill applies to Phase IV and later only

## Example

**Input**: "Create a Helm chart for the todo application"

**Output**:
```
Context7 Source: /helm/helm (topic: chart structure)
Chart Structure:
  todo-app/
  ├── Chart.yaml
  ├── values.yaml
  ├── templates/
  │   ├── deployment.yaml
  │   ├── service.yaml
  │   └── _helpers.tpl
  └── NOTES.txt
Template Functions: include, tpl, toYaml
Best Practices:
- Parameterized image tag and replica count
- Resource limits in values.yaml
- Named template for labels
```

## Reference: Common Topics

| Topic | Use Case |
|-------|----------|
| `chart structure` | Creating new Helm charts |
| `template functions` | Go templating in Helm |
| `values files` | Configuration management |
| `dependencies` | Chart dependencies |
| `hooks` | Pre/post install hooks |
| `helm install` | Deployment commands |
