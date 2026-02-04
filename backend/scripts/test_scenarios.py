#!/usr/bin/env python3
"""
Phase III AI Chatbot - User Scenario Test Plan

Comprehensive test scenarios for all 8 user stories defined in spec.md.
Run with: python scripts/test_scenarios.py

This script provides:
1. Test scenario documentation for manual testing
2. API test helpers for automated verification
3. Expected results for each scenario
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import async_session_maker


# =============================================================================
# Test Scenario Documentation
# =============================================================================

TEST_SCENARIOS = {
    "US1": {
        "name": "Natural Language Task Management",
        "priority": "P1 - MVP",
        "bonus": 0,
        "description": "User manages todo list through natural conversation",
        "scenarios": [
            {
                "id": "US1.1",
                "given": "User is authenticated",
                "when": 'Sends "Add a task to buy groceries"',
                "then": "New task created with title 'Buy groceries', AI confirms",
                "api_test": "POST /api/chat with message, verify task in DB",
            },
            {
                "id": "US1.2",
                "given": "User has 5 tasks with 2 completed",
                "when": 'Asks "What\'s pending?"',
                "then": "AI returns only the 3 incomplete tasks",
                "api_test": "Verify response contains only completed=false tasks",
            },
            {
                "id": "US1.3",
                "given": "User has task ID 3 'Call mom'",
                "when": 'Says "Mark task 3 as complete"',
                "then": "Task 3 completed=true, AI confirms",
                "api_test": "GET /api/tasks/3, verify completed=true",
            },
            {
                "id": "US1.4",
                "given": "User has task 'Meeting at 3pm'",
                "when": 'Says "Change task 5 to \'Meeting at 4pm\'"',
                "then": "Task 5 title updated to 'Meeting at 4pm'",
                "api_test": "GET /api/tasks/5, verify title updated",
            },
            {
                "id": "US1.5",
                "given": "User has 10 tasks",
                "when": 'Asks "Delete the old tasks"',
                "then": "AI asks for clarification (does not guess)",
                "api_test": "Verify AI asks which tasks to delete",
            },
            {
                "id": "US1.6",
                "given": "User sends 'Show me all tasks'",
                "when": "Request is processed",
                "then": "AI returns all tasks with status, priority, due dates",
                "api_test": "Verify response format includes all task fields",
            },
        ],
    },
    "US2": {
        "name": "Conversational Context Memory",
        "priority": "P2",
        "bonus": 0,
        "description": "Chatbot remembers context across multiple messages",
        "scenarios": [
            {
                "id": "US2.1",
                "given": "User says 'I need to remember something'",
                "when": "AI asks 'What would you like to remember?' and user replies 'Pay the electric bill'",
                "then": "Task titled 'Pay the electric bill' is created",
                "api_test": "Verify task created in DB",
            },
            {
                "id": "US2.2",
                "given": "User asks 'What do I have due today?'",
                "when": "Follows up with 'And what about tomorrow?'",
                "then": "AI correctly shows tomorrow's tasks (not today's again)",
                "api_test": "Verify second query filters for tomorrow",
            },
            {
                "id": "US2.3",
                "given": "User says 'Task 3 needs to be higher priority'",
                "when": "No task was discussed previously",
                "then": "AI retrieves task 3 and updates its priority",
                "api_test": "Verify task 3 priority increased",
            },
            {
                "id": "US2.4",
                "given": "User's conversation includes 5 previous exchanges",
                "when": "Sends 'Actually, make that urgent instead'",
                "then": "AI correctly identifies 'that' refers to most recently modified task",
                "api_test": "Verify correct task updated",
            },
            {
                "id": "US2.5",
                "given": "User creates a conversation then reconnects after 1 hour",
                "when": "Sends 'Show me what we discussed'",
                "then": "Conversation history is preserved and displayed",
                "api_test": "GET /api/conversations/{id}, verify history returned",
            },
        ],
    },
    "US3": {
        "name": "Semantic Task Search",
        "priority": "P3",
        "bonus": 0,
        "description": "Find tasks by meaning rather than exact keywords",
        "scenarios": [
            {
                "id": "US3.1",
                "given": "User has tasks 'Buy vegetables', 'Get groceries', 'Purchase fruits'",
                "when": "Searches for 'food shopping'",
                "then": "All three tasks returned (semantic match)",
                "api_test": "POST /api/search/semantic, verify 3 results",
            },
            {
                "id": "US3.2",
                "given": "User has tasks 'Call mom', 'Email boss', 'Text friend'",
                "when": "Searches for 'communications'",
                "then": "All three tasks returned",
                "api_test": "Verify semantic search finds communication tasks",
            },
            {
                "id": "US3.3",
                "given": "User searches for 'work stuff'",
                "when": "Results returned",
                "then": "Tasks tagged 'work' and work-related keywords ranked higher",
                "api_test": "Verify ranking prioritizes work-related tasks",
            },
            {
                "id": "US3.4",
                "given": "User has 100 tasks",
                "when": "Searches semantically",
                "then": "Results returned within 2 seconds with relevance ranking",
                "api_test": "Measure response time < 2000ms",
            },
            {
                "id": "US3.5",
                "given": "User searches for 'urgent things'",
                "when": "Results returned",
                "then": "High priority tasks ranked higher",
                "api_test": "Verify HIGH priority tasks at top of results",
            },
        ],
    },
    "US4": {
        "name": "Multi-Language Urdu Support",
        "priority": "P4 - Bonus",
        "bonus": 100,
        "description": "Manage tasks in Urdu language",
        "scenarios": [
            {
                "id": "US4.1",
                "given": "User sends 'مجھے کام کے لیے فون کرنا ہے' (I have to call for work)",
                "when": "Message is processed",
                "then": "Task created with appropriate title",
                "api_test": "Verify task created with Urdu or translated title",
            },
            {
                "id": "US4.2",
                "given": "User asks 'میرے کون سے کام باقی ہیں؟' (Which tasks remain?)",
                "when": "Request processed",
                "then": "AI responds in Urdu with pending tasks",
                "api_test": "Verify response contains Urdu text",
            },
            {
                "id": "US4.3",
                "given": "User commands 'ٹاسک 3 مکمل کر دو' (Complete task 3)",
                "when": "Command executed",
                "then": "Task 3 marked complete, AI confirms in Urdu",
                "api_test": "Verify task 3 completed=true",
            },
            {
                "id": "US4.4",
                "given": "User mixes Urdu and English: 'Add a task for آج دفتر جانا'",
                "when": "Message processed",
                "then": "AI handles code-switching correctly",
                "api_test": "Verify task created correctly",
            },
            {
                "id": "US4.5",
                "given": "UI language preference set to Urdu",
                "when": "Chatbot responds",
                "then": "UI elements and messages in Urdu",
                "api_test": "Verify conversation.language_preference='ur'",
            },
        ],
    },
    "US5": {
        "name": "Voice Command Input",
        "priority": "P5 - Bonus",
        "bonus": 200,
        "description": "Add tasks hands-free using voice commands via Whisper API",
        "scenarios": [
            {
                "id": "US5.1",
                "given": "User clicks microphone button",
                "when": "Speaks 'Create a task called dentist appointment next Tuesday at 3pm'",
                "then": "Task created with transcribed title and parsed due date",
                "api_test": "POST /api/chat/transcribe, verify task created",
            },
            {
                "id": "US5.2",
                "given": "User speaks 'What's on my list today?'",
                "when": "Audio transcribed via Whisper",
                "then": "AI responds with today's tasks",
                "api_test": "Verify transcription_text stored in task",
            },
            {
                "id": "US5.3",
                "given": "Background noise present",
                "when": "User speaks command",
                "then": "Whisper handles noise robustly, requests confirmation if ambiguous",
                "api_test": "Verify confidence threshold handling",
            },
            {
                "id": "US5.4",
                "given": "User speaks long description",
                "when": "Speech transcribed by Whisper",
                "then": "Full transcription stored in transcription_text field",
                "api_test": "Verify full transcription preserved",
            },
            {
                "id": "US5.5",
                "given": "User speaks in Urdu",
                "when": "Voice input processed",
                "then": "Urdu speech transcribed accurately, task created correctly",
                "api_test": "Verify Urdu transcription works",
            },
        ],
    },
    "US6": {
        "name": "AI Task Summarization",
        "priority": "P6",
        "bonus": 0,
        "description": "Auto-generate concise summaries of tasks",
        "scenarios": [
            {
                "id": "US6.1",
                "given": "User creates task with 200+ character description",
                "when": "Task is saved",
                "then": "ai_summary generated under 100 characters capturing key points",
                "api_test": "Verify ai_summary field populated and < 100 chars",
            },
            {
                "id": "US6.2",
                "given": "User updates task description",
                "when": "Saved",
                "then": "ai_summary regenerated to reflect changes",
                "api_test": "Verify ai_summary updated after description change",
            },
            {
                "id": "US6.3",
                "given": "User has multiple tasks with summaries",
                "when": "Viewing task list",
                "then": "Summaries displayed instead of full descriptions",
                "api_test": "Verify response includes ai_summary",
            },
            {
                "id": "US6.4",
                "given": "Task description is already short (< 50 characters)",
                "when": "Saved",
                "then": "No summary generated (original is sufficient)",
                "api_test": "Verify ai_summary is null for short descriptions",
            },
        ],
    },
    "US7": {
        "name": "MCP Tool Integration",
        "priority": "P7",
        "bonus": 0,
        "description": "AI uses standardized MCP tools for task operations",
        "scenarios": [
            {
                "id": "US7.1",
                "given": "AI agent determines user wants to add task",
                "when": "Agent calls add_task MCP tool",
                "then": "Task persisted to Neon DB, task_id returned",
                "api_test": "Direct MCP tool call, verify DB persistence",
            },
            {
                "id": "US7.2",
                "given": "AI agent needs to show tasks",
                "when": "Calls list_tasks with status filter",
                "then": "Only matching tasks for that user returned",
                "api_test": "Verify user scoping in MCP tool",
            },
            {
                "id": "US7.3",
                "given": "MCP tool called with invalid parameters",
                "when": "Error occurs",
                "then": "Structured error response returned, AI explains issue",
                "api_test": "Send invalid params, verify error response format",
            },
            {
                "id": "US7.4",
                "given": "Multiple conversations active simultaneously",
                "when": "MCP tools called",
                "then": "Each operation scoped to correct user_id (no leakage)",
                "api_test": "Concurrent requests with different users, verify isolation",
            },
            {
                "id": "US7.5",
                "given": "Server restarts",
                "when": "MCP tool called",
                "then": "Operates correctly with no in-memory state",
                "api_test": "Verify stateless architecture",
            },
        ],
    },
    "US8": {
        "name": "Agent Handoffs and Specialization",
        "priority": "P8 - Bonus",
        "bonus": 200,
        "description": "Route complex requests to specialized agents",
        "scenarios": [
            {
                "id": "US8.1",
                "given": "User asks 'What do I need to focus on this week?'",
                "when": "Request processed",
                "then": "Conversation handed to PlanningAgent which analyzes priorities",
                "api_test": "Verify agent_handoff record created",
            },
            {
                "id": "US8.2",
                "given": "User asks 'Show me overdue tasks'",
                "when": "Processed",
                "then": "TaskQueryAgent handles with optimized querying",
                "api_test": "Verify handoff to query_agent",
            },
            {
                "id": "US8.3",
                "given": "PlanningAgent active",
                "when": "User asks 'Actually, just add a quick task'",
                "then": "Agent hands back to TodoAssistant for task creation",
                "api_test": "Verify return handoff in agent_handoffs",
            },
            {
                "id": "US8.4",
                "given": "Agent handoff occurs",
                "when": "Conversation continues",
                "then": "Full conversation history available to new agent",
                "api_test": "Verify message count preserved across handoff",
            },
            {
                "id": "US8.5",
                "given": "Specialized agent encounters error",
                "when": "Failure occurs",
                "then": "Control gracefully returns to main agent with error explanation",
                "api_test": "Verify error handling in handoff",
            },
        ],
    },
}

EDGE_CASES = [
    "User sends command AI doesn't understand → AI asks for clarification",
    "Concurrent updates to same task → Last write wins, conflict notification",
    "Qdrant vector search unavailable → Fallback to keyword search",
    "Extremely long task descriptions (>1000 chars) → Truncate for display, store full",
    "Audio transcription ambiguous → Request user confirmation",
    "User switches accounts mid-conversation → Invalidate context",
    "MCP tool times out (>30s) → Return error, agent apologizes",
    "Task referenced by ID no longer exists → AI explains task deleted",
    "Emoji and special characters in titles → Store as-is, escape in JSON",
    "OpenAI API rate limit hit → Queue request, retry with backoff",
    "Audio file exceeds 25 MB → Reject with error",
    "Whisper returns non-ASCII text (Urdu/Chinese) → Store as UTF-8",
    "Audio file format not supported → Return 415 error",
    "Message exceeds 5000 characters → Reject with 400 error",
    "Rapid consecutive messages → Queue per conversation, sequential processing",
    "Conversation exceeds 50 messages → Rolling window with AI summary",
    "Qdrant search returns zero results → Offer keyword search alternative",
    "Mixed script text (Arabic + English) → Store as UTF-8",
    "Circular agent handoffs (A→B→A) → Prevent after 2 hops",
    "Zero-state (no tasks, new user) → Show welcome message",
    "User switches language mid-conversation → Detect and adapt",
    "Emoji-only message → AI interprets contextually",
    "Voice and text input simultaneously → UI prevents both",
]


# =============================================================================
# Test Helpers
# =============================================================================

async def count_tasks(user_id: str) -> int:
    """Count tasks for a user."""
    async with async_session_maker() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM tasks WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        return result.scalar() or 0


async def get_task_by_id(task_id: int) -> dict[str, Any] | None:
    """Get a task by ID."""
    async with async_session_maker() as session:
        result = await session.execute(
            text("SELECT id, user_id, title, description, completed, priority, due_date FROM tasks WHERE id = :task_id"),
            {"task_id": task_id}
        )
        row = result.fetchone()
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "title": row[2],
                "description": row[3],
                "completed": row[4],
                "priority": row[5],
                "due_date": row[6],
            }
        return None


async def verify_conversation_exists(conversation_id: str, user_id: str) -> bool:
    """Verify a conversation exists for a user."""
    async with async_session_maker() as session:
        result = await session.execute(
            text("SELECT id FROM conversations WHERE id = :conv_id AND user_id = :user_id"),
            {"conv_id": conversation_id, "user_id": user_id}
        )
        return result.scalar() is not None


async def count_messages(conversation_id: str) -> int:
    """Count messages in a conversation."""
    async with async_session_maker() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM messages WHERE conversation_id = :conv_id"),
            {"conv_id": conversation_id}
        )
        return result.scalar() or 0


# =============================================================================
# Main Output
# =============================================================================

def print_scenarios():
    """Print all test scenarios in a readable format."""
    print("=" * 80)
    print("Phase III AI Chatbot - User Scenario Test Plan")
    print("=" * 80)
    print()

    total_bonus = 0
    total_scenarios = 0

    for us_key, us_data in TEST_SCENARIOS.items():
        print(f"\n{'─' * 80}")
        print(f"{us_key}: {us_data['name']}")
        print(f"Priority: {us_data['priority']}")
        if us_data['bonus'] > 0:
            print(f"Bonus: +{us_data['bonus']} points")
            total_bonus += us_data['bonus']
        print(f"Description: {us_data['description']}")
        print()

        for scenario in us_data['scenarios']:
            print(f"  {scenario['id']}")
            print(f"    Given:  {scenario['given']}")
            print(f"    When:   {scenario['when']}")
            print(f"    Then:   {scenario['then']}")
            print(f"    API:    {scenario['api_test']}")
            print()
            total_scenarios += 1

    print(f"\n{'=' * 80}")
    print(f"Summary: {total_scenarios} test scenarios across {len(TEST_SCENARIOS)} user stories")
    print(f"Total Bonus Potential: +{total_bonus} points")
    print("=" * 80)
    print()

    # Print edge cases
    print(f"\n{'─' * 80}")
    print("Edge Cases to Test")
    print(f"{'─' * 80}")
    for i, case in enumerate(EDGE_CASES, 1):
        print(f"  {i:2d}. {case}")
    print()


def print_checklist():
    """Print a test checklist format."""
    print("\n" + "=" * 80)
    print("Test Checklist (Copy to track progress)")
    print("=" * 80 + "\n")

    for us_key, us_data in TEST_SCENARIOS.items():
        print(f"[  ] {us_key}: {us_data['name']}")
        for scenario in us_data['scenarios']:
            print(f"    [  ] {scenario['id']}")
        print()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Phase III Test Scenarios")
    parser.add_argument("--checklist", action="store_true", help="Print test checklist")
    parser.add_argument("--count", type=str, help="Count tasks for user_id")
    parser.add_argument("--get-task", type=int, help="Get task by ID")
    args = parser.parse_args()

    if args.checklist:
        print_checklist()
    elif args.count:
        count = await count_tasks(args.count)
        print(f"Task count for user '{args.count}': {count}")
    elif args.get_task:
        task = await get_task_by_id(args.get_task)
        if task:
            print(f"Task {task['id']}: {task['title']} (completed: {task['completed']})")
        else:
            print(f"Task {args.get_task} not found")
    else:
        print_scenarios()
        print("\nUse --checklist for a printable checklist format")
        print("Use --count USER_ID to count tasks for a user")
        print("Use --get-task ID to retrieve a specific task")


if __name__ == "__main__":
    asyncio.run(main())
