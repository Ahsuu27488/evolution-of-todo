#!/usr/bin/env python3
"""Comprehensive A-to-Z backend API test suite.

Tests all endpoints and functionality of the Chronos Todo API.
Run this script to verify the backend is working correctly.

Usage:
    python scripts/test_all.py
"""

import sys
import json
import uuid
from datetime import datetime, timedelta
from typing import Any

import requests
from jose import jwt

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = "http://localhost:8000"
SECRET_KEY = "mlHt/eQkNbw8oSExN56WdGS0dxwBdNGtMtG0XJ7jveE="
ALGORITHM = "HS256"

# Test user credentials
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPass123"
TEST_NAME = "Test User"

# Global variables for storing test data
AUTH_TOKEN = None
TASK_ID = None

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Test results tracking
results = []


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def print_header(title: str):
    """Print a section header."""
    print(f"\n{BLUE}{'═' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{title.center(60)}{RESET}")
    print(f"{BLUE}{'═' * 60}{RESET}\n")


def print_test(name: str):
    """Print a test name."""
    print(f"{YELLOW}▶ {name}{RESET}")


def print_pass(msg: str):
    """Print a passed test."""
    print(f"  {GREEN}✓ PASS{RESET}: {msg}")


def print_fail(msg: str):
    """Print a failed test."""
    print(f"  {RED}✗ FAIL{RESET}: {msg}")


def print_skip(msg: str):
    """Print a skipped test."""
    print(f"  {YELLOW}○ SKIP{RESET}: {msg}")


def create_test_token(email: str) -> str:
    """Create a test JWT token."""
    payload = {
        "sub": email,
        "email": email,
        "name": TEST_NAME,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_auth_headers(email: str) -> dict:
    """Get headers with JWT token."""
    token = create_test_token(email)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def assert_response(response, expected_status: int, description: str) -> bool:
    """Assert response status code and return success."""
    if response.status_code == expected_status:
        print_pass(f"{description} (status {response.status_code})")
        return True
    else:
        print_fail(f"{description} - expected {expected_status}, got {response.status_code}")
        if response.text:
            print(f"       Response: {response.text[:100]}")
        return False


def assert_json_field(response, field: str, expected_value: Any, description: str) -> bool:
    """Assert JSON field equals expected value."""
    try:
        data = response.json()
        actual_value = data.get(field)
        if actual_value == expected_value:
            print_pass(f"{description} ({field}={expected_value})")
            return True
        else:
            print_fail(f"{description} - expected {field}={expected_value}, got {actual_value}")
            return False
    except Exception as e:
        print_fail(f"{description} - JSON parse error: {e}")
        return False


# =============================================================================
# TEST SUITES
# =============================================================================

def test_health_endpoints() -> bool:
    """Test health check endpoints."""
    print_header("HEALTH ENDPOINTS")
    all_passed = True

    # Test root endpoint
    print_test("GET / (root endpoint)")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        all_passed &= assert_response(response, 200, "Root endpoint returns 200")
        if response.status_code == 200:
            data = response.json()
            if data.get("version") == "2.0.0":
                print_pass("API version is 2.0.0")
            else:
                print_fail(f"API version mismatch: {data.get('version')}")
                all_passed = False
    except Exception as e:
        print_fail(f"Root endpoint error: {e}")
        all_passed = False

    # Test health endpoint
    print_test("GET /api/health (health check)")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        all_passed &= assert_response(response, 200, "Health check returns 200")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print_pass("Health status is 'ok'")
            else:
                print_fail(f"Health status: {data.get('status')}")
                all_passed = False
    except Exception as e:
        print_fail(f"Health check error: {e}")
        all_passed = False

    return all_passed


def test_authentication() -> bool:
    """Test authentication endpoints."""
    print_header("AUTHENTICATION")
    global AUTH_TOKEN
    all_passed = True

    # Test signup
    print_test(f"POST /api/auth/signup (create user: {TEST_EMAIL})")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD, "name": TEST_NAME},
            timeout=30,
        )
        all_passed &= assert_response(response, 201, "User created successfully")
        if response.status_code in (200, 201):
            data = response.json()
            if data.get("email") == TEST_EMAIL:
                print_pass(f"User email matches: {TEST_EMAIL}")
            if data.get("name") == TEST_NAME:
                print_pass(f"User name matches: {TEST_NAME}")
    except Exception as e:
        print_fail(f"Signup error: {e}")
        all_passed = False
        return False

    # Test signin
    print_test("POST /api/auth/signin (get JWT token)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signin",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Signin successful")
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print_pass("JWT token received")
                # Store token for later tests
                global AUTH_TOKEN
                AUTH_TOKEN = data["access_token"]
            else:
                print_fail("No access_token in response")
                all_passed = False
    except Exception as e:
        print_fail(f"Signin error: {e}")
        all_passed = False

    # Test /me endpoint
    print_test("GET /api/auth/me (get current user)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Get current user successful")
        if response.status_code == 200:
            data = response.json()
            if data.get("email") == TEST_EMAIL:
                print_pass("Current user email matches")
    except Exception as e:
        print_fail(f"Get /me error: {e}")
        all_passed = False

    return all_passed


def test_task_crud() -> bool:
    """Test Task CRUD operations."""
    print_header("TASK CRUD")
    global TASK_ID
    all_passed = True
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}

    # Test create task
    print_test("POST /api/tasks (create task)")
    task_data = {
        "title": "Test Task A",
        "description": "This is a test task",
        "priority": "HIGH",
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json=task_data,
            timeout=30,
        )
        all_passed &= assert_response(response, 201, "Task created")
        if response.status_code in (200, 201):
            task = response.json()
            global TASK_ID
            TASK_ID = task.get("id")
            print_pass(f"Task created with ID: {TASK_ID}")
    except Exception as e:
        print_fail(f"Create task error: {e}")
        all_passed = False
        return False

    # Test list tasks
    print_test("GET /api/tasks (list all tasks)")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", headers=headers, timeout=10)
        all_passed &= assert_response(response, 200, "List tasks successful")
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Total tasks: {data.get('total', 0)}")
    except Exception as e:
        print_fail(f"List tasks error: {e}")
        all_passed = False

    # Test get specific task
    print_test(f"GET /api/tasks/{TASK_ID} (get specific task)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/{TASK_ID}",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Get task successful")
    except Exception as e:
        print_fail(f"Get task error: {e}")
        all_passed = False

    # Test update task
    print_test(f"PUT /api/tasks/{TASK_ID} (update task)")
    try:
        response = requests.put(
            f"{BASE_URL}/api/tasks/{TASK_ID}",
            headers=headers,
            json={"title": "Updated Test Task", "priority": "MEDIUM"},
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Update successful")
        if response.status_code == 200:
            data = response.json()
            if data.get("title") == "Updated Test Task":
                print_pass("Title updated successfully")
            if data.get("priority") == "MEDIUM":
                print_pass("Priority updated to MEDIUM")
    except Exception as e:
        print_fail(f"Update task error: {e}")
        all_passed = False

    return all_passed


def test_task_completion_toggle() -> bool:
    """Test task completion toggle."""
    print_header("TASK COMPLETION TOGGLE")
    all_passed = True
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    # Test mark complete
    print_test(f"PATCH /api/tasks/{TASK_ID}/complete (mark complete)")
    try:
        response = requests.patch(
            f"{BASE_URL}/api/tasks/{TASK_ID}/complete",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Toggle successful")
        if response.status_code == 200:
            data = response.json()
            if data.get("completed") == True:
                print_pass("Task marked as completed")
            else:
                print_fail("Task completed flag not set")
                all_passed = False
    except Exception as e:
        print_fail(f"Toggle complete error: {e}")
        all_passed = False

    # Test mark incomplete (toggle back)
    print_test(f"PATCH /api/tasks/{TASK_ID}/complete (toggle back to incomplete)")
    try:
        response = requests.patch(
            f"{BASE_URL}/api/tasks/{TASK_ID}/complete",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Toggle back successful")
        if response.status_code == 200:
            data = response.json()
            if data.get("completed") == False:
                print_pass("Task marked as incomplete")
    except Exception as e:
        print_fail(f"Toggle back error: {e}")
        all_passed = False

    return all_passed


def test_search_and_filters() -> bool:
    """Test search and filter functionality."""
    print_header("SEARCH AND FILTERS")
    all_passed = True
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    # Test search
    print_test('GET /api/tasks/search?q=Updated')
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/search?q=Updated",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Search successful")
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Search found {data.get('total', 0)} results")
    except Exception as e:
        print_fail(f"Search error: {e}")
        all_passed = False

    # Test filter by status
    print_test('GET /api/tasks?status=pending')
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks?status=pending",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Filter by status successful")
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Found {data.get('total', 0)} pending tasks")
    except Exception as e:
        print_fail(f"Filter error: {e}")
        all_passed = False

    # Test filter by priority
    print_test('GET /api/tasks?priority=MEDIUM')
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks?priority=MEDIUM",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Filter by priority successful")
        if response.status_code == 200:
            data = response.json()
            print_pass(f"Found {data.get('total', 0)} MEDIUM priority tasks")
    except Exception as e:
        print_fail(f"Filter by priority error: {e}")
        all_passed = False

    return all_passed


def test_audit_logs() -> bool:
    """Test audit log functionality."""
    print_header("AUDIT LOGS")
    all_passed = True
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    print_test(f"GET /api/tasks/{TASK_ID}/logs (get audit trail)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/{TASK_ID}/logs",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Get logs successful")
        if response.status_code == 200:
            logs = response.json()
            if isinstance(logs, list):
                print_pass(f"Retrieved {len(logs)} audit log entries")
                # Check for expected actions
                actions = [log.get("action") for log in logs]
                if "created" in actions:
                    print_pass("Audit log contains 'created' action")
                if "updated" in actions:
                    print_pass("Audit log contains 'updated' action")
    except Exception as e:
        print_fail(f"Get logs error: {e}")
        all_passed = False

    return all_passed


def test_error_handling() -> bool:
    """Test error handling."""
    print_header("ERROR HANDLING")
    all_passed = True
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}

    # Test 404 - non-existent task
    print_test("GET /api/tasks/99999 (404 Not Found)")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/99999", headers=headers, timeout=10)
        all_passed &= assert_response(response, 404, "Returns 404")
        if response.status_code == 404:
            data = response.json()
            if "not found" in data.get("detail", "").lower():
                print_pass("Error message indicates 'not found'")
    except Exception as e:
        print_fail(f"404 test error: {e}")
        all_passed = False

    # Test 401 - unauthorized
    print_test("GET /api/tasks without auth (401 Unauthorized)")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", timeout=10)
        all_passed &= assert_response(response, 401, "Returns 401")
        if response.status_code == 401:
            data = response.json()
            if data.get("code") == "UNAUTHORIZED":
                print_pass("Error code is UNAUTHORIZED")
    except Exception as e:
        print_fail(f"401 test error: {e}")
        all_passed = False

    # Test 422 - validation error (empty title)
    print_test("POST /api/tasks with empty title (422 Validation Error)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json={"title": "", "priority": "HIGH"},
            timeout=30,
        )
        all_passed &= assert_response(response, 422, "Returns 422")
        if response.status_code == 422:
            print_pass("Validation error correctly rejected empty title")
    except Exception as e:
        print_fail(f"422 test error: {e}")
        all_passed = False

    # Test 401 - wrong password
    print_test("POST /api/auth/signin with wrong password")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signin",
            json={"email": TEST_EMAIL, "password": "WrongPassword123"},
            timeout=30,
        )
        all_passed &= assert_response(response, 401, "Returns 401")
        if response.status_code == 401:
            data = response.json()
            if "invalid" in data.get("detail", "").lower() or "email or password" in data.get("detail", "").lower():
                print_pass("Error message indicates invalid credentials")
    except Exception as e:
        print_fail(f"Wrong password test error: {e}")
        all_passed = False

    return all_passed


def test_delete_task() -> bool:
    """Test task deletion."""
    print_header("TASK DELETION")
    all_passed = True
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    print_test(f"DELETE /api/tasks/{TASK_ID}")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/tasks/{TASK_ID}",
            headers=headers,
            timeout=30,
        )
        all_passed &= assert_response(response, 200, "Delete successful")
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                print_pass(f"Delete confirmation: {data.get('message')}")
    except Exception as e:
        print_fail(f"Delete error: {e}")
        all_passed = False
        return False

    # Verify deletion
    print_test(f"GET /api/tasks/{TASK_ID} (verify 404 after delete)")
    try:
        response = requests.get(
            f"{BASE_URL}/api/tasks/{TASK_ID}",
            headers=headers,
            timeout=30,
        )
        if response.status_code == 404:
            print_pass("Task confirmed deleted (404 response)")
        else:
            print_fail(f"Task still exists after delete: {response.status_code}")
            all_passed = False
    except Exception as e:
        print_fail(f"Verify deletion error: {e}")
        all_passed = False

    return all_passed


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    """Run all tests and report results."""
    print(f"\n{BOLD}{BLUE}{'╔' * 60}╗{RESET}")
    print(f"{BOLD}{BLUE}║{'CHRONOS TODO API - COMPREHENSIVE TEST SUITE'.center(58)}║{RESET}")
    print(f"{BOLD}{BLUE}{'╚' * 60}╝{RESET}")
    print(f"{BLUE}Testing: {BASE_URL}{RESET}\n")

    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
    except Exception:
        print(f"{RED}✗ ERROR: Backend is not running at {BASE_URL}{RESET}")
        print("Start the backend with: uvicorn app.main:app --reload --port 8000")
        return 1

    # Run all test suites
    suites = {
        "Health Endpoints": test_health_endpoints,
        "Authentication": test_authentication,
        "Task CRUD": test_task_crud,
        "Task Completion Toggle": test_task_completion_toggle,
        "Search & Filters": test_search_and_filters,
        "Audit Logs": test_audit_logs,
        "Error Handling": test_error_handling,
        "Task Deletion": test_delete_task,
    }

    for name, suite_func in suites.items():
        results.append((name, suite_func()))

    # Print summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for _, result in results if result)

    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {name:30s} {status}")

    print(f"\n{BLUE}{'─' * 60}{RESET}")
    print(f"  Total: {passed}/{total} test suites passed")
    print(f"{BLUE}{'─' * 60}{RESET}\n")

    if passed == total:
        print(f"{GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}✗ SOME TESTS FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
