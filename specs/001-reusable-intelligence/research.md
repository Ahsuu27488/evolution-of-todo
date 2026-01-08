# Research: Reusable Intelligence

**Feature**: 001-reusable-intelligence
**Date**: 2025-12-26
**Status**: Complete

## Research Questions

### Q1: Claude Code Skill Format

**Decision**: Use YAML frontmatter with name, description, version followed by markdown sections

**Rationale**: This is the format specified in `.claude/templates/SKILL-TEMPLATE.md` and matches Context7 documentation for Claude Code skills.

**Alternatives Considered**:
- JSON configuration: Rejected - not human-readable, harder to maintain
- Pure markdown without frontmatter: Rejected - missing metadata for discovery

**Source**: `.claude/templates/SKILL-TEMPLATE.md`, Context7 `/anthropics/claude-code`

---

### Q2: Claude Code Agent Format

**Decision**: Use YAML frontmatter with description, handoffs array followed by phases-based workflow

**Rationale**: This is the format specified in `.claude/templates/AGENT-TEMPLATE.md` and supports the required workflow phases pattern.

**Alternatives Considered**:
- Single flat document: Rejected - doesn't support complex multi-phase workflows
- Code-based agents: Rejected - skills/agents are configuration, not code

**Source**: `.claude/templates/AGENT-TEMPLATE.md`, Context7 `/anthropics/claude-code`

---

### Q3: Context7 MCP Tools

**Decision**: Use two-step workflow:
1. `mcp__plugin_context7_context7__resolve-library-id` - Find library ID
2. `mcp__plugin_context7_context7__get-library-docs` - Fetch documentation

**Rationale**: Context7 uses library IDs (format: `/org/project`) to identify documentation sources. Must resolve ID first, then fetch docs with specific topic.

**Key Parameters**:
- `resolve-library-id`: `libraryName` (string)
- `get-library-docs`: `context7CompatibleLibraryID` (string), `topic` (string, optional)

**Source**: Context7 MCP documentation, verified via testing

---

### Q4: Hackathon Phase Boundaries

**Decision**: Extract phase rules from constitution §IV.4.2 and encode in phase-guard skill

**Rationale**: Constitution is the authoritative source for phase boundaries. Encoding rules in a skill makes them automatically enforceable.

**Phase Boundaries**:
| Phase | Allowed | Forbidden |
|-------|---------|-----------|
| I | Add, Delete, Update, View, Complete | Databases, Files, Auth, Web, APIs |
| II | Phase I + Persistence, Auth, REST | Chatbot, AI, Kubernetes |
| III | Phase II + MCP, Agents SDK, ChatKit | Kubernetes, Kafka, Dapr |
| IV | Phase III + Docker, Minikube, Helm | Cloud, Kafka |
| V | All + Kafka, Dapr, Cloud | N/A |

**Source**: Constitution §IV.4.2, Hackathon-docs/

---

## Additional Findings

### Claude Code Discovery Mechanism

Skills are discovered automatically when placed in `.claude/skills/<name>/SKILL.md`. Agents are discovered from `.claude/agents/<name>.md`. No registration needed.

### Best Practices for Reusability

1. Keep skills focused and single-purpose
2. Use reference files for domain-specific data
3. Include clear triggers for auto-activation
4. Document constraints explicitly
5. Provide examples for common use cases

### Context7 Library IDs for Hackathon Stack

| Technology | Library ID | Benchmark Score |
|------------|-----------|-----------------|
| OpenAI Agents SDK | `/openai/openai-agents-python` | 86.4 |
| MCP Python SDK | `/modelcontextprotocol/python-sdk` | 89.2 |
| Claude Code | `/anthropics/claude-code` | 12.3 |

---

## Conclusion

All research questions answered. No NEEDS CLARIFICATION items remain. Ready for Phase 1 design.
