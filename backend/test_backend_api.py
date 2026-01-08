#!/usr/bin/env python3
"""Comprehensive backend API tests.

Tests all endpoints without relying on frontend authentication.
Creates a test JWT token directly to test protected endpoints.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Any

import requests
from jose import jwt

# Configuration
BASE_URL = "http://localhost:8000"
SECRET_KEY = "o6oQ8s/KB2vSHW8AWC4asxwgx07fgU1haOVjCfCNQ7w="
ALGORITHM = "HS256"

# Test user ID (simulating Better Auth user)
TEST_USER_ID = "test_user_backend_123"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_test(name: str):
    """Print test name."""
    print(f"\n{YELLOW}Testing: {name}{RESET}")


def print_pass(message: str):
    """Print passed test."""
    print(f"{GREEN}✓ PASS{RESET}: {message}")


def print_fail(message: str):
    """Print failed test."""
    print(f"{RED}✗ FAIL{RESET}: {message}")


def create_test_token() -> str:
    """Create a test JWT token for authentication."""
    payload = {
        "sub": TEST_USER_ID,
        "email": "test@backend.test",
        "name": "Backend Test User",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_headers() -> dict[str, str]:
    """Get headers with JWT token."""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def test_health_endpoints() -> bool:
    """Test health check endpoints."""
    all_passed = True

    # Test root endpoint
    print_test("Root endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Root endpoint - {data.get('message')}")
        else:
            print_fail(f"Root endpoint returned {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Root endpoint error: {e}")
        all_passed = False

    # Test health endpoint
    print_test("Health check endpoint")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Health check - status: {data.get('status')}")
        else:
            print_fail(f"Health check returned {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Health check error: {e}")
        all_passed = False

    return all_passed


def test_authentication_required() -> bool:
    """Test that endpoints require authentication."""
    all_passed = True

    print_test("Tasks endpoint without auth (should fail)")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", timeout=5)
        if response.status_code == 401:
            data = response.json()
            print_pass(f"Unauthorized - {data.get('detail')}")
        else:
            print_fail(f"Expected 401, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Error: {e}")
        all_passed = False

    return all_passed


def test_task_crud() -> bool:
    """Test Task CRUD operations."""
    all_passed = True
    headers = get_headers()
    task_id = None

    # Test CREATE task
    print_test("Create task")
    task_data = {
        "title": "Test Task from Backend",
        "description": "This is a test task created by backend API tests",
        "priority": "HIGH",
        "tags": [{"name": "test", "color": "#00f5ff"}],
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json=task_data,
            timeout=10,
        )
        if response.status_code == 201:
            task = response.json()
            task_id = task.get("id")
            print_pass(f"Task created - ID: {task_id}, Title: {task.get('title')}")
        else:
            print_fail(f"Create failed - {response.status_code}: {response.text}")
            all_passed = False
    except Exception as e:
        print_fail(f"Create error: {e}")
        all_passed = False

    if not task_id:
        return False

    # Test LIST tasks
    print_test("List tasks")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Listed {data.get('total', 0)} tasks")
        else:
            print_fail(f"List failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"List error: {e}")
        all_passed = False

    # Test GET single task
    print_test("Get single task")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/{task_id}",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            task = response.json()
            print_pass(f"Retrieved task - {task.get('title')}")
        else:
            print_fail(f"Get failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Get error: {e}")
        all_passed = False

    # Test UPDATE task
    print_test("Update task")
    update_data = {"title": "Updated Test Task", "priority": "MEDIUM"}
    try:
        response = requests.put(
            f"{BASE_URL}/api/tasks/{task_id}",
            headers=headers,
            json=update_data,
            timeout=10,
        )
        if response.status_code == 200:
            task = response.json()
            if task.get("title") == "Updated Test Task":
                print_pass(f"Task updated - new title: {task.get('title')}")
            else:
                print_fail("Update didn't apply")
                all_passed = False
        else:
            print_fail(f"Update failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Update error: {e}")
        all_passed = False

    # Test TOGGLE completion
    print_test("Toggle task completion")
    try:
        response = requests.patch(
            f"{BASE_URL}/api/tasks/{task_id}/complete",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            task = response.json()
            if task.get("completed") == True:
                print_pass(f"Task marked as completed")
            else:
                print_fail("Task completion not toggled")
                all_passed = False
        else:
            print_fail(f"Toggle failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Toggle error: {e}")
        all_passed = False

    # Test SEARCH tasks
    print_test("Search tasks")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/search?q=Updated",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Search found {data.get('total', 0)} tasks")
        else:
            print_fail(f"Search failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Search error: {e}")
        all_passed = False

    # Test FILTER by status
    print_test("Filter tasks by status (completed)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks?status=completed",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Filter found {data.get('total', 0)} completed tasks")
        else:
            print_fail(f"Filter failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Filter error: {e}")
        all_passed = False

    # Test FILTER by priority
    print_test("Filter tasks by priority (HIGH)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks?priority=HIGH",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Filter found {data.get('total', 0)} HIGH priority tasks")
        else:
            print_fail(f"Filter failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Filter error: {e}")
        all_passed = False

    # Test GET task logs
    print_test("Get task audit logs")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/{task_id}/logs",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            logs = response.json()
            print_pass(f"Retrieved {len(logs)} audit log entries")
        else:
            print_fail(f"Logs failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Logs error: {e}")
        all_passed = False

    # Test DELETE task
    print_test("Delete task")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/tasks/{task_id}",
            headers=headers,
            timeout=10,
        )
        if response.status_code in (200, 204):
            print_pass(f"Task deleted successfully")
        else:
            print_fail(f"Delete failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Delete error: {e}")
        all_passed = False

    # Verify deletion
    print_test("Verify task was deleted")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/{task_id}",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 404:
            print_pass("Task confirmed deleted (404)")
        else:
            print_fail(f"Task still exists - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Verify error: {e}")
        all_passed = False

    return all_passed


def test_multiple_tasks() -> bool:
    """Test creating and managing multiple tasks."""
    all_passed = True
    headers = get_headers()

    print_test("Create multiple tasks")
    tasks_to_create = [
        {"title": "Buy groceries", "priority": "HIGH"},
        {"title": "Call mom", "priority": "MEDIUM"},
        {"title": "Read documentation", "priority": "LOW"},
    ]

    created_ids = []
    for task_data in tasks_to_create:
        try:
            response = requests.post(
                f"{BASE_URL}/api/tasks",
                headers=headers,
                json=task_data,
                timeout=10,
            )
            if response.status_code == 201:
                task = response.json()
                created_ids.append(task.get("id"))
            else:
                print_fail(f"Failed to create: {task_data['title']}")
                all_passed = False
        except Exception as e:
            print_fail(f"Error creating task: {e}")
            all_passed = False

    print_pass(f"Created {len(created_ids)} tasks")

    # Test sorting
    print_test("Sort tasks by title")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks?sort_by=title&sort_order=asc",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Sorted {data.get('total', 0)} tasks by title")
        else:
            print_fail(f"Sort failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Sort error: {e}")
        all_passed = False

    # Test pagination
    print_test("Pagination (per_page=2)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks?per_page=2",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            if len(data.get("tasks", [])) <= 2:
                print_pass(f"Pagination working - returned {len(data.get('tasks', []))} tasks")
            else:
                print_fail(f"Pagination not working - returned {len(data.get('tasks', []))} tasks")
                all_passed = False
        else:
            print_fail(f"Pagination failed - {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Pagination error: {e}")
        all_passed = False

    # Cleanup
    print_test("Cleanup test tasks")
    for task_id in created_ids:
        try:
            requests.delete(
                f"{BASE_URL}/api/tasks/{task_id}",
                headers=headers,
                timeout=10,
            )
        except Exception:
            pass

    return all_passed


def test_error_handling() -> bool:
    """Test error handling for invalid requests."""
    all_passed = True
    headers = get_headers()

    print_test("Get non-existent task (404)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/99999",
            headers=headers,
            timeout=10,
        )
        if response.status_code == 404:
            print_pass("Correctly returned 404 for non-existent task")
        else:
            print_fail(f"Expected 404, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Error: {e}")
        all_passed = False

    print_test("Create task with invalid data (empty title)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json={"title": "", "priority": "HIGH"},
            timeout=10,
        )
        if response.status_code == 422:  # Validation error
            print_pass("Correctly rejected empty title")
        else:
            print_fail(f"Expected 422, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Error: {e}")
        all_passed = False

    print_test("Update non-existent task")
    try:
        response = requests.put(
            f"{BASE_URL}/api/tasks/99999",
            headers=headers,
            json={"title": "Updated"},
            timeout=10,
        )
        if response.status_code == 404:
            print_pass("Correctly returned 404 for update of non-existent task")
        else:
            print_fail(f"Expected 404, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Error: {e}")
        all_passed = False

    return all_passed


def main():
    """Run all tests."""
    print("=" * 60)
    print(" BACKEND API COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    results = {}

    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"\nBackend is running at {BASE_URL}")
    except Exception:
        print(f"\n{RED}ERROR: Backend is not running at {BASE_URL}")
        print("Start the backend with: uvicorn app.main:app --reload")
        sys.exit(1)

    # Run tests
    results["health"] = test_health_endpoints()
    results["auth_required"] = test_authentication_required()
    results["crud"] = test_task_crud()
    results["multiple"] = test_multiple_tasks()
    results["errors"] = test_error_handling()

    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(results.values())

    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test_name:20s}: {status}")

    print("=" * 60)
    print(f"Total: {passed}/{total} test suites passed")

    if passed == total:
        print(f"{GREEN}All tests passed!{RESET}")
        return 0
    else:
        print(f"{YELLOW}Some tests failed.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
