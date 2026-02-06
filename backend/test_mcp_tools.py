#!/usr/bin/env python3
"""
Test script to verify all MCP tools are accessible to the agent.

Run with: python test_mcp_tools.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai.agents.todo_agent import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    get_task,
    semantic_search,
    MCP_TOOLS,
    AGENT_AVAILABLE,
)
from app.ai.agents.context import TodoContext


class MockSession:
    """Mock database session for testing."""
    async def commit(self):
        print("  [MockSession] Commit called")

    async def refresh(self, obj):
        pass

    def add(self, obj):
        print(f"  [MockSession] Adding: {type(obj).__name__}")


async def test_tool_signatures():
    """Test that all tools have correct signatures."""
    print("=" * 60)
    print("MCP Tools Availability Test")
    print("=" * 60)

    print(f"\n1. OpenAI Agents SDK Available: {AGENT_AVAILABLE}")

    print(f"\n2. MCP_TOOLS List:")
    print(f"   - Total tools: {len(MCP_TOOLS)}")
    for i, tool in enumerate(MCP_TOOLS, 1):
        # Handle both function objects and FunctionTool wrappers
        if hasattr(tool, '__name__'):
            tool_name = tool.__name__
        elif hasattr(tool, 'name'):
            tool_name = tool.name
        elif hasattr(tool, '__class__'):
            tool_name = f"{tool.__class__.__name__}"
        else:
            tool_name = str(type(tool))
        print(f"   - Tool {i}: {tool_name}")

    # Expected tools
    expected_tools = [
        "add_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        "update_task",
        "get_task",
        "semantic_search",
    ]

    print(f"\n3. Expected vs Actual Tools:")
    tool_names = []
    for t in MCP_TOOLS:
        if hasattr(t, 'name'):
            tool_names.append(t.name)
        elif hasattr(t, '__name__'):
            tool_names.append(t.__name__)
        else:
            tool_names.append(str(type(t)))

    for expected in expected_tools:
        status = "✓ FOUND" if expected in tool_names else "✗ MISSING"
        print(f"   - {expected}: {status}")

    missing = [t for t in expected_tools if t not in tool_names]
    if missing:
        print(f"\n   ⚠️  MISSING TOOLS: {missing}")
        return False

    print("\n4. Tool Parameters (from FunctionTool schema):")
    import json
    for tool in MCP_TOOLS:
        if tool:
            tool_name = getattr(tool, 'name', str(type(tool)))
            # Get params from schema
            if hasattr(tool, 'params_json_schema'):
                params = tool.params_json_schema.get('properties', {}).keys()
                required = tool.params_json_schema.get('required', [])
                print(f"   - {tool_name}({', '.join(params)})")
                if 'ctx' in required:
                    print(f"     ✓ ctx is required parameter")
                else:
                    print(f"     ✗ ctx is NOT in required params: {required}")
            else:
                print(f"   - {tool_name}: (no schema available)")

    print("\n5. Testing Tool Accessibility with Mock Context:")

    # Create a mock context
    ctx = TodoContext(
        user_id="test_user_123",
        conversation_id="test_conv",
        correlation_id="test_corr",
        session=MockSession(),
    )

    # Test that tools can be called (they will fail due to mock session, but we check signature)
    results = {}
    for tool_name, tool_func in [
        ("add_task", add_task),
        ("list_tasks", list_tasks),
        ("complete_task", complete_task),
        ("delete_task", delete_task),
        ("update_task", update_task),
        ("get_task", get_task),
        ("semantic_search", semantic_search),
    ]:
        if tool_func is None:
            print(f"   - {tool_name}: ✗ None (SDK not available)")
            results[tool_name] = "MISSING"
            continue

        try:
            # Try to get signature
            sig = inspect.signature(tool_func)
            results[tool_name] = "OK"
            print(f"   - {tool_name}: ✓ Accessible")
        except Exception as e:
            results[tool_name] = f"ERROR: {e}"
            print(f"   - {tool_name}: ✗ {e}")

    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    all_ok = all(r == "OK" for r in results.values())
    if all_ok:
        print("✓ All MCP tools are accessible!")
        return True
    else:
        print("✗ Some tools have issues:")
        for tool, status in results.items():
            if status != "OK":
                print(f"  - {tool}: {status}")
        return False


async def test_agent_instructions():
    """Test that agent instructions mention all tools."""
    print("\n" + "=" * 60)
    print("Agent Instructions Test")
    print("=" * 60)

    from app.ai.agents.todo_agent import get_todo_agent

    agent = get_todo_agent()
    if agent is None:
        print("✗ Agent not available (SDK not installed)")
        return False

    print(f"\nAgent Name: {agent.name}")
    print(f"\nInstructions mentions:")

    instructions = agent.instructions

    tool_keywords = {
        "add_task": "add_task",
        "list_tasks": "list_tasks",
        "complete_task": "complete_task",
        "delete_task": "delete_task",
        "update_task": "update_task",
        "get_task": "get_task",
        "semantic_search": "semantic_search",
    }

    for tool, keyword in tool_keywords.items():
        found = keyword in instructions
        status = "✓" if found else "✗"
        print(f"  {status} {tool}: {'found' if found else 'NOT FOUND'}")

    print(f"\nAgent tools list length: {len(agent.tools)}")
    for i, tool in enumerate(agent.tools):
        print(f"  - Tool {i+1}: {tool.name if hasattr(tool, 'name') else type(tool).__name__}")

    return True


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCP Tools Systematic Test")
    print("=" * 60 + "\n")

    tools_ok = await test_tool_signatures()
    agent_ok = await test_agent_instructions()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    if tools_ok and agent_ok:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
