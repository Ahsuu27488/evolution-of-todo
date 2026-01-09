#!/bin/bash
# E2E Verification Script for Chronos Todo
# Tests: Signup -> Signin -> Create Task -> List Tasks flow

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "=========================================="
echo "  E2E Verification - Chronos Todo"
echo "=========================================="
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo "=========================================="

# Check if jq is available
if command -v jq &> /dev/null; then
    JQ_AVAILABLE=true
else
    JQ_AVAILABLE=false
    echo -e "${YELLOW}⚠${NC} jq not found - using fallback JSON parsing"
fi

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

# Helper to extract JSON value
extract_json() {
    local json=$1
    local key=$2

    if [ "$JQ_AVAILABLE" = true ]; then
        echo "$json" | jq -r ".$key // empty"
    else
        # Fallback: grep for "key":"value" or "key":number
        echo "$json" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:.*"\(.*\)".*/\1/' \
            || echo "$json" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*[0-9]*" | head -1 | sed 's/.*:.*\([0-9]*\).*/\1/'
    fi
}

# Test 1: Check servers are running
echo -e "\n${YELLOW}[1] Testing Server Health...${NC}"
check_server "$BACKEND_URL/api/health" "Backend" || exit 1
check_server "$FRONTEND_URL" "Frontend" || exit 1

# Test 2: Test Signup Flow (via Backend API)
echo -e "\n${YELLOW}[2] Testing Signup Flow...${NC}"

# Generate random test user
TIMESTAMP=$(date +%s)
TEST_EMAIL="e2e_test_${TIMESTAMP}@example.com"
TEST_PASSWORD="TestPassword123!"

echo "Creating test user: $TEST_EMAIL"

SIGNUP_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/signup" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"name\":\"E2E Test User\"}" || echo "")

USER_ID=$(extract_json "$SIGNUP_RESPONSE" "id")
USER_EMAIL=$(extract_json "$SIGNUP_RESPONSE" "email")

if [ -n "$USER_ID" ] || echo "$SIGNUP_RESPONSE" | grep -q "$TEST_EMAIL"; then
    echo -e "${GREEN}✓${NC} Signup successful"
    echo "  Email: $TEST_EMAIL"
else
    echo -e "${RED}✗${NC} Signup failed"
    echo "  Response: $SIGNUP_RESPONSE"
    exit 1
fi

# Test 3: Test Signin Flow
echo -e "\n${YELLOW}[3] Testing Signin Flow...${NC}"

SIGNIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/signin" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" || echo "")

TOKEN=$(extract_json "$SIGNIN_RESPONSE" "access_token")

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Signin successful"
    echo "  Token: ${TOKEN:0:25}..."
else
    echo -e "${RED}✗${NC} Signin failed"
    echo "  Response: $SIGNIN_RESPONSE"
    exit 1
fi

# Test 4: Test Create Task Flow
echo -e "\n${YELLOW}[4] Testing Create Task Flow...${NC}"

TASK_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/tasks" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"title":"E2E Test Task","description":"Created during verification","priority":"HIGH"}' || echo "")

TASK_ID=$(extract_json "$TASK_RESPONSE" "id")
TASK_TITLE=$(extract_json "$TASK_RESPONSE" "title")

if [ -n "$TASK_ID" ]; then
    echo -e "${GREEN}✓${NC} Create Task successful"
    echo "  Task ID: $TASK_ID"
    echo "  Title: $TASK_TITLE"
else
    echo -e "${RED}✗${NC} Create Task failed"
    echo "  Response: $TASK_RESPONSE"
    exit 1
fi

# Test 5: Test Get Specific Task
echo -e "\n${YELLOW}[5] Testing Get Task by ID...${NC}"

GET_TASK_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN" || echo "")

GET_TASK_TITLE=$(extract_json "$GET_TASK_RESPONSE" "title")

if [ "$GET_TASK_TITLE" = "E2E Test Task" ]; then
    echo -e "${GREEN}✓${NC} Get Task successful"
    echo "  Retrieved: $GET_TASK_TITLE"
else
    echo -e "${RED}✗${NC} Get Task failed"
    echo "  Response: $GET_TASK_RESPONSE"
fi

# Test 6: Test Update Task
echo -e "\n${YELLOW}[6] Testing Update Task...${NC}"

UPDATE_RESPONSE=$(curl -s -X PUT "$BACKEND_URL/api/tasks/$TASK_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"title":"Updated E2E Task","priority":"MEDIUM"}' || echo "")

UPDATED_TITLE=$(extract_json "$UPDATE_RESPONSE" "title")
UPDATED_PRIORITY=$(extract_json "$UPDATE_RESPONSE" "priority")

if [ "$UPDATED_TITLE" = "Updated E2E Task" ]; then
    echo -e "${GREEN}✓${NC} Update Task successful"
    echo "  New title: $UPDATED_TITLE"
    echo "  New priority: $UPDATED_PRIORITY"
else
    echo -e "${RED}✗${NC} Update Task failed"
    echo "  Response: $UPDATE_RESPONSE"
fi

# Test 7: Test Task Completion Toggle
echo -e "\n${YELLOW}[7] Testing Toggle Task Completion...${NC}"

TOGGLE_RESPONSE=$(curl -s -X PATCH "$BACKEND_URL/api/tasks/$TASK_ID/complete" \
    -H "Authorization: Bearer $TOKEN" || echo "")

COMPLETED_STATUS=$(extract_json "$TOGGLE_RESPONSE" "completed")

if [ "$COMPLETED_STATUS" = "true" ]; then
    echo -e "${GREEN}✓${NC} Toggle complete successful"
    echo "  Task marked as completed"
else
    echo -e "${RED}✗${NC} Toggle complete failed"
    echo "  Response: $TOGGLE_RESPONSE"
fi

# Test 8: Test List Tasks
echo -e "\n${YELLOW}[8] Testing List Tasks...${NC}"

LIST_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks" \
    -H "Authorization: Bearer $TOKEN" || echo "")

if echo "$LIST_RESPONSE" | grep -q "id"; then
    if [ "$JQ_AVAILABLE" = true ]; then
        TASK_COUNT=$(echo "$LIST_RESPONSE" | jq '.total // length')
    else
        TASK_COUNT=$(echo "$LIST_RESPONSE" | grep -o '"id"' | wc -l)
    fi
    echo -e "${GREEN}✓${NC} List Tasks successful"
    echo "  Total tasks: $TASK_COUNT"
else
    echo -e "${RED}✗${NC} List Tasks failed"
    echo "  Response: $LIST_RESPONSE"
fi

# Test 9: Test Search Tasks
echo -e "\n${YELLOW}[9] Testing Search Tasks...${NC}"

SEARCH_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks/search?q=Updated" \
    -H "Authorization: Bearer $TOKEN" || echo "")

if echo "$SEARCH_RESPONSE" | grep -q "Updated"; then
    echo -e "${GREEN}✓${NC} Search Tasks successful"
else
    echo -e "${RED}✗${NC} Search Tasks failed"
    echo "  Response: $SEARCH_RESPONSE"
fi

# Test 10: Test Get Audit Logs
echo -e "\n${YELLOW}[10] Testing Get Audit Logs...${NC}"

LOGS_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks/$TASK_ID/logs" \
    -H "Authorization: Bearer $TOKEN" || echo "")

if echo "$LOGS_RESPONSE" | grep -q "\["; then
    if [ "$JQ_AVAILABLE" = true ]; then
        LOG_COUNT=$(echo "$LOGS_RESPONSE" | jq 'length')
    else
        LOG_COUNT=$(echo "$LOGS_RESPONSE" | grep -o '"action"' | wc -l)
    fi
    echo -e "${GREEN}✓${NC} Get Audit Logs successful"
    echo "  Log entries: $LOG_COUNT"
else
    echo -e "${RED}✗${NC} Get Audit Logs failed"
    echo "  Response: $LOGS_RESPONSE"
fi

# Test 11: Test Delete Task
echo -e "\n${YELLOW}[11] Testing Delete Task...${NC}"

DELETE_RESPONSE=$(curl -s -X DELETE "$BACKEND_URL/api/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN" || echo "")

if echo "$DELETE_RESPONSE" | grep -q "deleted\|success"; then
    echo -e "${GREEN}✓${NC} Delete Task successful"
else
    echo -e "${RED}✗${NC} Delete Task failed"
    echo "  Response: $DELETE_RESPONSE"
fi

# Verify deletion
VERIFY_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN" || echo "")

if echo "$VERIFY_RESPONSE" | grep -qi "not found"; then
    echo -e "${GREEN}✓${NC} Task verified deleted (404 response)"
fi

# Test 12: Test Error Handling - 404
echo -e "\n${YELLOW}[12] Testing Error Handling (404)...${NC}"

NOT_FOUND_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks/99999" \
    -H "Authorization: Bearer $TOKEN" || echo "")

if echo "$NOT_FOUND_RESPONSE" | grep -qi "not found"; then
    echo -e "${GREEN}✓${NC} 404 error handling works correctly"
else
    echo -e "${RED}✗${NC} 404 error handling failed"
fi

# Test 13: Test Error Handling - Unauthorized
echo -e "\n${YELLOW}[13] Testing Error Handling (401 Unauthorized)...${NC}"

UNAUTH_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/tasks" || echo "")

if echo "$UNAUTH_RESPONSE" | grep -qi "unauthorized\|authenticated"; then
    echo -e "${GREEN}✓${NC} 401 error handling works correctly"
else
    echo -e "${RED}✗${NC} 401 error handling failed"
fi

# Summary
echo -e "\n=========================================="
echo -e "${GREEN}✓ E2E Verification Complete!${NC}"
echo "=========================================="
echo -e "\nTest user credentials:"
echo "  Email:    $TEST_EMAIL"
echo "  Password: $TEST_PASSWORD"
echo -e "\nYou can use these credentials to manually test at:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL/docs"
echo "=========================================="
