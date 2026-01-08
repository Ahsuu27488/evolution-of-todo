---
name: "context7-lookup"
description: "Fetch official documentation for libraries, frameworks, and tools using Context7 MCP. Use when implementing with external dependencies or asking about library APIs."
version: "1.0.0"
---

# Context7 Documentation Lookup Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions implementing with FastAPI, Next.js, SQLModel, or other stack technologies
- Implementation requires knowledge of external library APIs
- User asks "how do I use X" for any framework or SDK

## How This Skill Works

Step-by-step workflow:
1. **Identify Library**: Extract library/framework name from user context
2. **Resolve ID**: Call `mcp__plugin_context7_context7__resolve-library-id` with library name
3. **Select Match**: Choose library with High reputation and highest benchmark score
4. **Fetch Docs**: Call `mcp__plugin_context7_context7__get-library-docs` with resolved ID and topic

## Output Format

Provide structured output:
- **Library**: Name and Context7 ID used
- **Key Patterns**: Code patterns retrieved from documentation
- **Applied**: How the knowledge was used in implementation

## Constraints and Rules

- ALWAYS use before implementing with external libraries
- NEVER assume API patterns from training data alone
- Prefer libraries with "High" source reputation
- Report if no documentation match found

## Example

**Input**: "Create an MCP server with tools for todo management"

**Output**:
```
Library: MCP Python SDK (/modelcontextprotocol/python-sdk)
Key Patterns: FastMCP server with @mcp.tool() decorators
Applied: Created todo MCP server with add_task, list_tasks, complete_task tools
```

## Supporting Files (Optional)

- `reference/library-ids.md`: Common library ID mappings for hackathon stack
