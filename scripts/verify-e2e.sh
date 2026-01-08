#!/bin/bash
# E2E Verification Script for Phase 0 REPAIR
# Tests: Signup -> Signin -> Create Task flow

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "=========================================="
echo "  E2E Verification - Phase 0 REPAIR"
echo "=========================================="
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo "=========================================="

# Helper to check server health
check_server() {
    local url=$1
    local name=$2

    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is NOT running"
        return 1
    fi
}

# Test 1: Check servers are running
echo -e "\n${YELLOW}[T023] Testing Server Health...${NC}"
check_server "$BACKEND_URL/docs" "Backend" || exit 1
check_server "$FRONTEND_URL" "Frontend" || exit 1

# Test 2: Test Better Auth Signup API
echo -e "\n${YELLOW}[T024] Testing Signup Flow...${NC}"

# Generate random test user
TIMESTAMP=$(date +%s)
TEST_EMAIL="test_user_${TIMESTAMP}@example.com"
TEST_PASSWORD="TestPassword123!"

echo "Creating test user: $TEST_EMAIL"

# Better Auth 1.x uses /api/auth/sign-up/email for email/password signup
SIGNUP_RESPONSE=$(curl -s -X POST "$FRONTEND_URL/api/auth/sign-up/email" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"name\":\"Test User\"}" || echo "")

if echo "$SIGNUP_RESPONSE" | grep -q "user"; then
    echo -e "${GREEN}✓${NC} Signup successful"
    USER_ID=$(echo "$SIGNUP_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    echo "  User ID: $USER_ID"
else
    echo -e "${RED}✗${NC} Signup failed"
    echo "  Response: $SIGNUP_RESPONSE"
fi

# Test 3: Test Signin Flow
echo -e "\n${YELLOW}[T025] Testing Signin Flow...${NC}"

# Better Auth 1.x uses /api/auth/sign-in/email for email/password signin
SIGNIN_RESPONSE=$(curl -s -X POST "$FRONTEND_URL/api/auth/sign-in/email" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" || echo "")

if echo "$SIGNIN_RESPONSE" | grep -q "token\|user"; then
    echo -e "${GREEN}✓${NC} Signin successful"
    TOKEN=$(echo "$SIGNIN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    if [ -z "$TOKEN" ]; then
        # Token might be in a cookie, check for session
        echo "  Session established (cookie-based auth)"
    else
        echo "  Token obtained: ${TOKEN:0:20}..."
    fi
else
    echo -e "${RED}✗${NC} Signin failed"
    echo "  Response: $SIGNIN_RESPONSE"
fi

# Test 4: Test Create Task Flow (via Backend API with JWT)
echo -e "\n${YELLOW}[T026] Testing Create Task Flow...${NC}"

# Get session token from signin cookies
SESSION_COOKIE=$(curl -s -i -X POST "$FRONTEND_URL/api/auth/sign-in/email" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
    | grep -i "set-cookie.*session" | head -1)

if [ -n "$SESSION_COOKIE" ]; then
    # Extract cookie value
    COOKIE_VALUE=$(echo "$SESSION_COOKIE" | grep -o "session=[^;]*" | cut -d'=' -f2)

    # Create task via backend API
    TASK_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/tasks" \
        -H "Content-Type: application/json" \
        -H "Cookie: session=$COOKIE_VALUE" \
        -d '{"title":"E2E Test Task","description":"Created during verification","priority":"medium"}' || echo "")

    if echo "$TASK_RESPONSE" | grep -q "id\|title"; then
        echo -e "${GREEN}✓${NC} Create Task successful"
        TASK_ID=$(echo "$TASK_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
        echo "  Task ID: $TASK_ID"
    else
        echo -e "${RED}✗${NC} Create Task failed"
        echo "  Response: $TASK_RESPONSE"
    fi
else
    echo -e "${YELLOW}⚠${NC} Could not extract session cookie, manual verification needed"
fi

# Test 5: Verify task retrieval
echo -e "\n${YELLOW}[BONUS] Testing List Tasks...${NC}"

if [ -n "$COOKIE_VALUE" ]; then
    LIST_RESPONSE=$(curl -s -H "Cookie: session=$COOKIE_VALUE" "$BACKEND_URL/api/tasks" || echo "")

    if echo "$LIST_RESPONSE" | grep -q "\["; then
        echo -e "${GREEN}✓${NC} List Tasks successful"
        TASK_COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id"' | wc -l)
        echo "  Total tasks: $TASK_COUNT"
    else
        echo -e "${RED}✗${NC} List Tasks failed"
        echo "  Response: $LIST_RESPONSE"
    fi
fi

echo -e "\n=========================================="
echo -e "${GREEN}✓ Verification Complete!${NC}"
echo "=========================================="
echo -e "\nTest user created:"
echo "  Email:    $TEST_EMAIL"
echo "  Password: $TEST_PASSWORD"
echo -e "\nYou can use these credentials to manually test the UI at:"
echo "  $FRONTEND_URL"
