/sp.specify Read Constitution and create specs for Phase 3: AI-Powered Todo Chatbot

CONTEXT GATHERING (Step 1):
- Read Hackathon.md to understand Phase 3 requirements
- Read all README.md and CLAUDE.md files in codebase
- Read constitution.md and existing specs from phases 1 & 2
- Understand our current architecture and implementation state

PHASE 3 REQUIREMENTS (from Hackathon.md):
Core Features (200 points):
- AI-Powered Todo Chatbot using OpenAI Agents SDK
- Natural language task management (e.g., "Reschedule my morning meetings to 2 PM")
- Integration with existing Next.js frontend and FastAPI backend
- Official MCP SDK integration for tool use

Bonus Features to Target:
- Semantic/Vector Search using Qdrant (+implementing Advanced Level features)
- Multi-language Support (Urdu) (+100 points)
- Voice Commands (+200 points)
- Reusable Intelligence via Subagents and Agent Skills (+200 points)

TECHNOLOGY STACK:
- OpenAI GPT-4o mini for all AI operations
- OpenAI Agents SDK for chatbot
- Official MCP SDK for tool integration
- Qdrant for vector database (semantic search)
- Environment variables: OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_URL (already in backend/.env)

AI CAPABILITIES TO IMPLEMENT:
1. Conversational Task Management
   - Natural language parsing for todo operations
   - Context-aware task suggestions
   - Smart task scheduling and rescheduling

2. AI-Enhanced Features
   - Task summaries and insights
   - Smart suggestions based on user patterns
   - Automated email generation for tasks
   - Semantic search across tasks using vector embeddings

3. MCP Server Integration
   - Create MCP server with todo management tools
   - Enable AI agent to use tools through conversation
   - Jarvis-level interaction: AI communicates naturally and executes autonomously

CRITICAL INSTRUCTION:
Use Context7 (context7.com) to access official documentation:
- OpenAI Agents SDK documentation
- OpenAI API documentation for GPT-4o mini
- Qdrant documentation for vector database
- Official MCP SDK documentation
- Any other technology mentioned above


CONSTRAINTS:
- Must maintain compatibility with existing Phase 2 implementation
- Must follow constitution.md principles
- All code must be generated through spec-driven process
- No manual coding - iterate on specs until Claude Code generates correct output
- Must reference task IDs when implementing

SUCCESS CRITERIA:
- Achieve all Phase 3 core requirements (200 points)
- Implement at least 2-3 bonus features (400-600+ points total)
- Create reusable AI components (Agent Skills/Subagents)
- Demonstrate Jarvis-level autonomous operation
- Outperform competitors through comprehensive bonus feature implementation

Begin by reading all context documents, then create comprehensive specs following the SDD workflow.

-------------------------------------------------------

