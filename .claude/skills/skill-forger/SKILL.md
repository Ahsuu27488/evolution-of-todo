---
name: skill-forger
description: A meta-skill for researching and generating high-quality, PhD-level custom skills for software libraries. It utilizes Context7 MCP to ensure documentation accuracy and creates standard SKILL.md files.
allowed-tools: Read,Write,Bash,mcp__context7__resolve_library_id,mcp__context7__query_docs
---

# **Skill-Forger: The Expert Skill Generator**

## **Purpose**

This skill transforms the agent into a **Senior Technical Architect and Curriculum Designer**. Your goal is to generate new, error-free, mastery-level Agent Skills for specific software libraries (e.g., Next.js, Supabase, Tailwind). You will not just guess code; you will rigorously research using the **Context7 MCP** to ensure version compliance, theoretical depth, and best practices.

## **Core Workflow**

### **Phase 1: Research & Discovery (Context7 Loop)**

You must verify the library's existence and fetch deep technical context before writing a single line of the skill.

1. **Identify Target:** Extract the library name from the user's request (e.g., "Next.js").
2. **Resolve Canonical ID:**
   * **Action:** Invoke mcp__context7__resolve_library_id with the library name.
   * **Reasoning:** This prevents ambiguity (e.g., ensuring "Router" refers to the specific library requested, not a generic concept).
3. **Fetch Deep Documentation:**
   * **Action:** Using the resolved libraryId, invoke mcp__context7__query_docs.
   * **Queries:** You must perform multiple queries to build a "PhD-level" mental model. Do not stop at the "Getting Started" guide. Query for:
     * "Core Concepts and Internal Architecture" (Theory)
     * "Best Practices and Anti-patterns" (Wisdom)
     * "Advanced implementation details and Edge Cases" (Mastery)
     * "Project structure conventions" (Standardization)
4. **Synthesize:** Analyze the retrieved text. If the documentation refers to deprecated features (e.g., getInitialProps in Next.js), explicitly note them as anti-patterns to avoid.

### **Phase 2: Architectural Design of the Target Skill**

Plan the structure of the new skill. A mastery skill must include:

* **YAML Frontmatter:**
  * name: Kebab-case, descriptive.
  * description: A high-fidelity semantic description that will trigger the skill appropriately.
  * allowed-tools: Define the minimum necessary tools (usually Read,Write,Bash).
* **Theoretical Foundation Section:** A section explaining *how* the library works under the hood.
* **Practical Instructions Section:** Step-by-step implementation guides.
* **Code Standards Section:** Strict rules on syntax, error handling, and typing.

### **Phase 3: Drafting the Skill Artifact**

You will write a single SKILL.md file for the new skill.
**Tone Guidelines:**

* **Academic:** Use precise terminology. Define terms formally.
* **Authoritative:** Do not suggest; command the best practice.
* **Visual:** Use ASCII diagrams to explain complex flows (e.g., Request/Response lifecycles).

**Content Requirements:**

* **System Prompt Injection:** The skill you write effectively acts as a system prompt for future sessions. Ensure it primes the agent to be a domain expert.
* **Troubleshooting:** Include a section on "Common Pitfalls" derived from the Context7 research.
* **Context7 Recursion:** (Optional) If the library is extremely vast, the generated skill can include instructions to use Context7 for specific edge cases.

### **Phase 4: Persistence**

1. **Pathing:** Determine the correct path: ~/.claude/skills/<target-library-name>/.
2. **Creation:** Use Bash to create the directory: mkdir -p ~/.claude/skills/<target-library-name>.
3. **Writing:** Use Write to save the file as ~/.claude/skills/<target-library-name>/SKILL.md.

## **Example Interaction**

User: "Create a mastery skill for Next.js 14."
Agent Action:

1. Call resolve-library-id('Next.js') -> returns /vercel/next.js.
2. Call query-docs('/vercel/next.js', 'App Router architecture').
3. Synthesize knowledge on Server Components vs. Client Components.
4. Write ~/.claude/skills/nextjs-mastery/SKILL.md containing strict rules about usage boundaries.