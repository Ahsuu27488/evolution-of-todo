<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 1.3.0 -> 1.4.0 (MINOR - elevated Context7 to primary source of truth)
Modified Principles:
  - Section III.1 "Context7 MCP Mandate": Strengthened to establish Context7 as PRIMARY source of truth
  - Section II.2 "Required Actions": Updated to reference Context7 as primary source
Added Sections:
  - III.1.2 "Context7 Primary Source Priority" - New core directive for all coding tasks
Removed Sections: None
Templates Status:
  - .specify/templates/plan-template.md: No changes needed
  - .specify/templates/spec-template.md: No changes needed
  - .specify/templates/tasks-template.md: No changes needed
  - Command files: None exist (verified)
Follow-up TODOs: None
================================================================================
-->

# Evolution of Todo - Project Constitution

> **Supreme Governing Document** for the "Evolution of Todo" Hackathon Project.
> This constitution remains stable across all five phases and governs all AI agents.

---

## 0. Competitive Excellence Commitment

### 0.1 Mission Statement
**This project commits to achieving TOP PLACEMENT in the hackathon through:**
- Complete implementation of ALL 5 phases (1000 base points)
- Achievement of ALL bonus objectives (+600 bonus points)
- Superior code quality and documentation
- Exceptional demonstration of Spec-Driven Development

### 0.2 Bonus Points Commitment (MANDATORY)

| Bonus Category | Points | Status | Implementation |
|----------------|--------|--------|----------------|
| **Reusable Intelligence** | +200 | ACTIVE | Skills and Sub-Agents in `.claude/` |
| **Cloud-Native Blueprints** | +200 | ACTIVE | `cloud-native-blueprint` skill + `cloud-native-blueprints` agent |
| **Multi-Language (Urdu)** | +100 | PLANNED | `urdu-language-guide` skill for Phase III |
| **Voice Commands** | +200 | PLANNED | `voice-commands-guide` skill for Phase III |
| **TOTAL BONUS** | **+600** | - | All categories will be achieved |

### 0.3 Excellence Standards
- Every phase MUST exceed minimum requirements
- Documentation MUST be comprehensive and professional
- Code MUST demonstrate best practices consistently
- Demo video MUST showcase all features effectively
- Reusable assets MUST be portable to future projects

---

## I. Spec-Driven Development (SDD) - MANDATORY

### 1.1 Core Mandate
**No agent may write code without approved specs and tasks.**

All work MUST follow the strict pipeline:
```
Constitution -> Specify (WHAT) -> Plan (HOW) -> Tasks (WORK UNITS) -> Implement (CODE)
```

### 1.2 Refinement Rule
- Refinement occurs at the **spec level**, never at the code level
- If implementation reveals issues, update the spec first, then regenerate tasks
- Code is a derivative artifact of specifications

### 1.3 Verification Before Implementation
Before any `/sp.implement` command:
1. Verify spec completeness against acceptance criteria
2. Confirm all tasks reference spec sections
3. Validate no future-phase features leak into current phase

---

## II. Agent Behavior Rules (NON-NEGOTIABLE)

### 2.1 Prohibited Actions
- **No manual coding by humans** - All code generated via Claude Code
- **No feature invention** - Only implement what specs define
- **No deviation from approved specifications**
- **No code generation without Task ID reference**
- **No architecture changes without Plan update**
- **No reliance on training data for external libraries** - Use Context7 instead

### 2.2 Required Actions
- Reference Task IDs in all code comments: `[Task]: T-XXX`
- Link code to spec sections: `[From]: spec.md §X.X, plan.md §X.X`
- **Treat Context7 as PRIMARY source of truth for ALL coding tasks** (see §III.1)
- Create PHR (Prompt History Record) after every significant interaction
- Suggest ADRs for architecturally significant decisions

### 2.3 Human-as-Tool Strategy
Invoke the user for input when encountering:
1. **Ambiguous Requirements** - Ask 2-3 targeted clarifying questions
2. **Unforeseen Dependencies** - Surface and request prioritization
3. **Architectural Uncertainty** - Present options with tradeoffs
4. **Completion Checkpoints** - Summarize and confirm next steps

---

## III. Knowledge & Documentation Protocol

### 3.1 Context7 MCP Mandate (CRITICAL - PRIMARY SOURCE OF TRUTH)

**CORE DIRECTIVE: Context7 is the PRIMARY source of truth for ALL coding tasks.**

For **ALL coding activities** - including code generation, refactoring, or debugging - you MUST:

1. **Treat Context7 as the authoritative source** for patterns, syntax, and APIs
2. **Explicitly prioritize Context7 documentation over internal training data**
3. **Retrieve current documentation before using ANY**:
   - Framework (FastAPI, Next.js, SQLModel, Dapr, etc.)
   - Library (OpenAI Agents SDK, MCP SDK, kafka-python, etc.)
   - Service (Neon DB, Kubernetes, Helm, Docker, etc.)
   - Tool (kubectl-ai, kagent, Gordon, etc.)

**Mandatory Workflow:**
1. `mcp__plugin_context7_context7__resolve-library-id` - Get library ID
2. `mcp__plugin_context7_context7__query-docs` - Fetch current docs
3. **Apply ONLY retrieved patterns and APIs** in implementation
4. **Never rely on training data** for external library usage

**Priority Hierarchy:**
```
Context7 Documentation (CURRENT) > Training Data (POTENTIALLY STALE)
```

**Why Context7 is Primary:**
- Training data has a knowledge cutoff (January 2025)
- Frameworks evolve rapidly with breaking changes
- Official docs contain current best practices and deprecation notices
- APIs change between versions (e.g., FastAPI 0.100 vs 0.115)
- Context7 provides real-time access to latest documentation

**Prohibited Actions:**
- ❌ Writing code based solely on training data knowledge
- ❌ Assuming APIs without verifying in Context7
- ❌ Using deprecated patterns or syntax
- ❌ Guessing parameter names or function signatures

### 3.1.1 Context7 Primary Source Priority (MANDATORY)

**APPLIES TO: ALL coding tasks without exception**

**Scope:**
This requirement applies to **EVERY** instance of:
- **Code Generation**: Writing new code with external libraries
- **Refactoring**: Modifying existing code that uses external libraries
- **Debugging**: Investigating errors related to external libraries
- **Architecture Design**: Choosing between libraries or frameworks

**Explicit Prioritization Rules:**

1. **Before Writing Code**:
   - Query Context7 for the library/framework
   - Review current API documentation
   - Identify current best practices
   - Check for breaking changes or deprecations

2. **During Code Writing**:
   - Use ONLY patterns from retrieved Context7 documentation
   - Match function signatures exactly as shown in docs
   - Follow current examples from official documentation
   - Apply current error handling patterns

3. **When Debugging**:
   - First action: Query Context7 for relevant error patterns
   - Cross-reference error messages with documentation
   - Apply documented solutions before attempting alternatives
   - Verify against current library version docs

4. **When Refactoring**:
   - Re-verify APIs via Context7 before modifying
   - Check if newer patterns exist in current docs
   - Ensure refactored code follows current best practices

**Compliance Verification:**

For each coding task, agents MUST be able to demonstrate:
- ✅ Context7 was queried for all external libraries used
- ✅ Retrieved documentation matches the code written
- ✅ Patterns/syntax align with current official docs
- ✅ No training-data assumptions were made

**Example - Correct Workflow:**
```
Task: "Add JWT authentication to FastAPI backend"

WRONG (Training Data):
- Write code based on remembered FastAPI patterns from training
- Assume OAuth2PasswordBearer() signature
- Guess at middleware setup

CORRECT (Context7 Primary):
1. Query Context7: "fastapi latest authentication"
2. Retrieve current FastAPI security docs
3. Follow current OAuth2 flow examples from docs
4. Apply documented patterns exactly
5. Verify code matches retrieved documentation
```

### 3.1.2 Context7 Fallback Protocol (MANDATORY)

**CRITICAL FALLBACK RULE:**
When a proposed fix fails to resolve an error, the agent **MUST** retrieve and utilize Context7 documentation before attempting a second solution.

**Trigger Conditions:**
This protocol activates when ALL of the following occur:
1. An error or bug is encountered during implementation
2. The agent proposes and applies a fix
3. The fix fails (error persists, new error appears, or tests still fail)
4. The agent is about to attempt a second solution

**Required Actions (in order):**
1. **STOP** - Do not propose a second solution yet
2. **IDENTIFY** the relevant library/framework causing the error
3. **RETRIEVE** current documentation via Context7 MCP tools:
   ```
   resolve-library-id → query-docs
   ```
4. **ANALYZE** the retrieved documentation for:
   - Correct API usage patterns
   - Common pitfalls and error handling
   - Breaking changes or version-specific behavior
   - Official examples matching the use case
5. **APPLY** documentation-based solution
6. **VERIFY** the fix resolves the error before proceeding

**Prohibited Actions:**
- ❌ Attempting a second fix based on assumptions
- ❌ Guessing alternative solutions without documentation
- ❌ Trying multiple iterations without consulting official docs
- ❌ Relying on training data knowledge (may be outdated)

**Rationale:**
- Training data knowledge becomes stale quickly
- Frameworks evolve rapidly (FastAPI, Next.js, etc.)
- Official documentation contains current best practices
- Prevents "fix cycles" that waste time and complicate code
- Ensures solutions align with current library versions

**Example Flow:**
```
Error encountered → Proposed fix → Fix failed
→ [MANDATED] Context7 lookup on failing library
→ Apply doc-based solution → Verify success
```

### 3.2 Reusable Intelligence Assets
All agents MUST prioritize creating and using:

| Asset Type | Location | Purpose |
|------------|----------|---------|
| **Skills** | `.claude/skills/<name>/SKILL.md` | Lightweight, auto-activated capabilities |
| **Sub-Agents** | `.claude/agents/<name>.md` | Complex, multi-step isolated workflows |
| **Templates** | `.claude/templates/` | Standardized structures for skills/agents |

**Goal:** Assets created in this hackathon MUST be reusable in ALL future projects.

---

## IV. Phase Governance

### 4.1 Phase Isolation
- Each phase is **strictly scoped** by its specification
- Future-phase features MUST NEVER leak into earlier phases
- Architecture evolves ONLY through updated specs and plans

### 4.2 Phase Progression

| Phase | Scope | Allowed Features | Forbidden Concepts |
|-------|-------|------------------|-------------------|
| **I** | In-Memory Console | Add, Delete, Update, View, Mark Complete | Databases, Files, Auth, Web, APIs |
| **II** | Full-Stack Web | Phase I + Persistence, Auth, REST API | Chatbot, AI, Kubernetes |
| **III** | AI Chatbot | Phase II + MCP Server, Agents SDK, ChatKit | Kubernetes, Kafka, Dapr |
| **IV** | Local K8s | Phase III + Docker, Minikube, Helm | Cloud deployment, Kafka |
| **V** | Cloud Deployment | All features + Kafka, Dapr, AKS/GKE/OKE | N/A |

### 4.3 Phase Completion Criteria
Before advancing to next phase:
- [ ] All acceptance criteria from spec verified
- [ ] All tasks marked complete
- [ ] Working application demonstrates all features
- [ ] Code committed to GitHub with proper structure
- [ ] PHR created documenting the phase work

---

## V. Technology Constraints

### 5.1 Core Stack (All Phases)
| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | **3.13+ (STRICT - see V.1.1 below)** |
| Package Manager | UV | Latest |
| AI Assistant | Claude Code | Latest |
| Spec Management | Spec-Kit Plus | Latest |

### 5.1.1 Python Version Enforcement (MANDATORY)

**STRICT REQUIREMENT: Python 3.13.0 or higher MUST be used for all development.**

This is a non-negotiable requirement. No exceptions.

**Verification Commands:**
```bash
# Check current Python version
python --version  # MUST show "Python 3.13.0" or higher
python3 --version

# If using UV (recommended per spec)
uv python list
uv python pin 3.13

# If using pyenv
pyenv install 3.13
pyenv local 3.13
```

**Acceptable Versions:**
- Python 3.13.0 ✅
- Python 3.13.1 ✅
- Python 3.13.2 ✅
- Python 3.14.x ✅ (when available)

**Unacceptable Versions:**
- Python 3.12.x or lower ❌
- Python 3.14.0-alpha/beta/rc ❌ (pre-releases only)

**Rationale:**
- Hackathon requirements explicitly specify Python 3.13+
- Modern type hinting and syntax features are required
- Dependency compatibility (asyncpg, sqlmodel, fastapi) validated for 3.13+
- Consistent environment across all team members

**Compliance Check:**
All agents MUST verify Python version before:
1. Creating any new virtual environment
2. Running any installation commands
3. Executing any Python code

### 5.2 Phase-Specific Stack

#### Phase I: Console Application
```
Python 3.13+ only (STRICT - see V.1.1)
In-memory data structures (dict/list)
No external dependencies except standard library
```

#### Phase II: Full-Stack Web
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth (JWT) |

#### Phase III: AI Chatbot
| Component | Technology |
|-----------|------------|
| Chat UI | OpenAI ChatKit |
| AI Framework | OpenAI Agents SDK |
| MCP Server | Official MCP SDK (Python) |
| State | Stateless endpoints + DB persistence |

#### Phase IV: Local Kubernetes
| Component | Technology |
|-----------|------------|
| Containerization | Docker (Docker Desktop) |
| Docker AI | Gordon (Docker AI Agent) |
| Orchestration | Kubernetes (Minikube) |
| Package Manager | Helm Charts |
| AI DevOps | kubectl-ai, Kagent |

#### Phase V: Cloud Deployment
| Component | Technology |
|-----------|------------|
| Cloud Platform | Azure AKS / Google GKE / Oracle OKE |
| Event Streaming | Kafka (Strimzi/Redpanda) |
| Distributed Runtime | Dapr (Pub/Sub, State, Jobs, Secrets) |
| CI/CD | GitHub Actions |

---

## VI. Quality Principles

### 6.1 Architecture Standards
- **Clean Architecture** - Clear separation of concerns
- **Stateless Services** - No in-memory state between requests (Phase III+)
- **Cloud-Native Readiness** - Design for horizontal scaling
- **Smallest Viable Diff** - Only change what's necessary

### 6.2 Code Standards
- Clear, readable code over clever solutions
- Explicit error handling for all edge cases
- No hardcoded secrets - use `.env` and environment variables
- Type hints required for all function signatures (Python)
- TypeScript strict mode (Frontend)

### 6.3 Security Standards
- OWASP Top 10 awareness - no SQL injection, XSS, command injection
- JWT validation on all protected endpoints
- User data isolation - users see only their own data
- Secrets in environment variables, never in code

### 6.4 Testing Philosophy
- Acceptance criteria = test cases
- Error paths explicitly tested
- Integration tests for cross-component flows

---

## VII. Project Structure

### 7.1 Repository Layout
```
evolution-of-todo/
├── .specify/                    # Spec-Kit configuration
│   ├── memory/
│   │   └── constitution.md      # This file (supreme authority)
│   ├── templates/               # Spec-Kit templates
│   └── scripts/                 # Helper scripts
├── .claude/                     # Claude Code configuration
│   ├── skills/                  # Reusable skills
│   ├── agents/                  # Sub-agents
│   └── templates/               # Skill/Agent templates
├── specs/                       # Feature specifications
│   └── <feature>/
│       ├── spec.md              # WHAT (requirements)
│       ├── plan.md              # HOW (architecture)
│       └── tasks.md             # WORK UNITS
├── history/                     # Audit trail
│   ├── prompts/                 # PHR records
│   │   ├── constitution/
│   │   ├── <feature-name>/
│   │   └── general/
│   └── adr/                     # Architecture Decision Records
├── src/                         # Source code (Phase I)
├── frontend/                    # Next.js app (Phase II+)
├── backend/                     # FastAPI server (Phase II+)
├── k8s/                         # Kubernetes manifests (Phase IV+)
│   └── helm/                    # Helm charts
├── CLAUDE.md                    # Claude Code instructions
└── README.md                    # Project documentation
```

### 7.2 Monorepo Strategy
- Single repository for all phases
- CLAUDE.md at root with phase-specific instructions
- Subdirectory CLAUDE.md files for frontend/backend specifics
- Specs folder organized by feature

---

## VIII. Workflow Execution Contract

### 8.1 For Every Request
1. **Confirm** surface and success criteria (one sentence)
2. **List** constraints, invariants, non-goals
3. **Produce** artifact with acceptance checks inlined
4. **Add** follow-ups and risks (max 3 bullets)
5. **Create PHR** in appropriate subdirectory
6. **Suggest ADR** if architecturally significant decision detected

### 8.2 Minimum Acceptance Criteria
- [ ] Clear, testable acceptance criteria included
- [ ] Explicit error paths and constraints stated
- [ ] Smallest viable change; no unrelated edits
- [ ] Code references to modified/inspected files
- [ ] **Context7 used as PRIMARY source for all external libraries**

### 8.3 Error Resolution Protocol
When encountering errors during implementation:
1. **First attempt**: Apply initial fix based on analysis
2. **If fix fails**: **MANDATORY Context7 lookup** before second attempt
3. **Apply documentation-based solution**
4. **Verify** success before proceeding
5. **Log** the resolution in PHR for future reference

---

## IX. Governance

### 9.1 Authority Hierarchy
```
Constitution > Specify > Plan > Tasks > Implementation
```

If conflict arises, higher-level document takes precedence.

### 9.2 Amendment Process
1. Propose change with justification
2. Document in ADR
3. Update constitution
4. Notify all dependent artifacts

### 9.3 Compliance
- All agent outputs verified against this constitution
- Complexity must be justified against principles
- Violations require immediate correction

---

## X. Bonus Objectives (ALL COMMITTED)

### 10.1 Reusable Intelligence (+200 points) - ACTIVE
**Status**: Implemented in Feature 001-reusable-intelligence

Assets Created:
- **Skills** (12 total): phase-guard, spec-validator, todo-domain, context7-lookup, fastapi-guide, sqlmodel-guide, nextjs-guide, docker-guide, kubernetes-guide, helm-guide, kafka-guide, dapr-guide
- **Agents** (5 total): fullstack-scaffolder, k8s-deployer, mcp-server-builder, dapr-integrator, cloud-native-blueprints

### 10.2 Cloud-Native Blueprints (+200 points) - ACTIVE
**Status**: Implemented in Feature 002-bonus-points-excellence

Assets Created:
- `cloud-native-blueprint` skill - Generates Dockerfiles, K8s manifests, Helm charts
- `cloud-native-blueprints` agent - Orchestrates full deployment pipeline
- Templates for multi-stage Docker builds, Helm values, K8s resources

### 10.3 Multi-language Support (+100 points) - PLANNED
**Status**: Skill created, implementation in Phase III

Assets Created:
- `urdu-language-guide` skill - RTL text handling, language detection, bilingual agent instructions

Implementation Phase: Phase III (AI Chatbot)

### 10.4 Voice Commands (+200 points) - PLANNED
**Status**: Skill created, implementation in Phase III

Assets Created:
- `voice-commands-guide` skill - Web Speech API integration, transcription handling, confidence thresholds

Implementation Phase: Phase III (AI Chatbot)

### 10.5 Supporting Skills for Excellence
Additional skills created to ensure superior implementation:
- `better-auth-guide` - JWT authentication patterns for Phase II
- `openai-agents-guide` - Agents SDK patterns for Phase III
- `chatkit-guide` - ChatKit UI patterns for Phase III

---

**Version**: 1.4.0 | **Ratified**: 2025-12-26 | **Last Amended**: 2026-01-24

---

> *"No task = No code. No spec = No task. No constitution = No spec."*
>
> — Evolution of Todo Governing Principle
