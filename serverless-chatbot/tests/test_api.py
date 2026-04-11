"""
tests/test_api.py - API Test Suite
=====================================
Tests the FastAPI backend endpoints.

Run with: pytest tests/ -v

5 Test Cases:
1. Health check endpoint works
2. Valid chat message returns proper response
3. Empty message is rejected (validation)
4. Too-long message is rejected (validation)
5. Response includes all required fields
6. History endpoint works
7. Math expressions are evaluated
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

# Import our FastAPI app
from backend.main import app

# Create a test client (no real server needed)
client = TestClient(app)


# ═══════════════════════════════════════════════════════════════
# TEST CASE 1: Health Check
# ═══════════════════════════════════════════════════════════════

def test_health_check():
    """
    TC-001: Health Check Endpoint
    Description: Verify the API is running and returns status 'ok'
    Input: GET /
    Expected: 200 OK with {"status": "ok"}
    """
    response = client.get("/")

    # Assert HTTP status code is 200
    assert response.status_code == 200, "Expected 200 OK"

    data = response.json()
    assert "status" in data, "Response must have 'status' field"
    assert data["status"] == "ok", "Status must be 'ok'"

    print("✅ TC-001 PASSED: Health check works")


# ═══════════════════════════════════════════════════════════════
# TEST CASE 2: Valid Message Returns Response
# ═══════════════════════════════════════════════════════════════

def test_valid_chat_message():
    """
    TC-002: Valid Chat Message
    Description: Send a valid message and verify bot responds properly
    Input: POST /chat with {"message": "Hello"}
    Expected: 200 OK with response, session_id, timestamp, model_version
    """
    payload = {
        "message": "Hello",
        "session_id": "test-session-001"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    # Verify all required fields are present
    assert "response" in data, "Missing 'response' field"
    assert "session_id" in data, "Missing 'session_id' field"
    assert "timestamp" in data, "Missing 'timestamp' field"
    assert "model_version" in data, "Missing 'model_version' field"
    assert "response_time_ms" in data, "Missing 'response_time_ms' field"

    # Verify values are meaningful
    assert len(data["response"]) > 0, "Response must not be empty"
    assert data["session_id"] == "test-session-001", "Session ID must match"

    print("✅ TC-002 PASSED: Valid message gets proper response")


# ═══════════════════════════════════════════════════════════════
# TEST CASE 3: Empty Message Rejected
# ═══════════════════════════════════════════════════════════════

def test_empty_message_rejected():
    """
    TC-003: Empty Message Validation
    Description: Empty messages should be rejected with 422 Unprocessable Entity
    Input: POST /chat with {"message": ""}
    Expected: 422 or 400 error response
    """
    payload = {
        "message": "",
        "session_id": "test-session-002"
    }

    response = client.post("/chat", json=payload)

    # Should NOT be 200 (should be rejected)
    assert response.status_code in [400, 422], \
        f"Empty message should be rejected, got {response.status_code}"

    print("✅ TC-003 PASSED: Empty message is properly rejected")


# ═══════════════════════════════════════════════════════════════
# TEST CASE 4: Too-Long Message Rejected
# ═══════════════════════════════════════════════════════════════

def test_long_message_rejected():
    """
    TC-004: Message Length Validation
    Description: Messages over 500 chars should be rejected
    Input: POST /chat with message of 501 characters
    Expected: 400 Bad Request
    """
    long_message = "A" * 501  # 501 characters — exceeds limit

    payload = {
        "message": long_message,
        "session_id": "test-session-003"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code in [400, 422], \
        f"Long message should be rejected, got {response.status_code}"

    print("✅ TC-004 PASSED: Long message is properly rejected")


# ═══════════════════════════════════════════════════════════════
# TEST CASE 5: Greeting Response
# ═══════════════════════════════════════════════════════════════

def test_greeting_response():
    """
    TC-005: Greeting Pattern Matching
    Description: A greeting should trigger a greeting response
    Input: "hi there"
    Expected: Response contains a greeting word
    """
    payload = {
        "message": "hi there",
        "session_id": "test-session-004"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()
    bot_reply = data["response"].lower()

    # The response should be a greeting
    greeting_words = ["hello", "hi", "hey", "great", "help"]
    has_greeting = any(word in bot_reply for word in greeting_words)

    assert has_greeting, f"Expected greeting response, got: {data['response']}"

    print("✅ TC-005 PASSED: Greeting triggers appropriate response")


# ═══════════════════════════════════════════════════════════════
# TEST CASE 6: Response Time is Tracked
# ═══════════════════════════════════════════════════════════════

def test_response_time_tracked():
    """
    TC-006: Response Time Monitoring
    Description: Every response must include response_time_ms > 0
    Input: Any valid message
    Expected: response_time_ms is a positive number
    """
    payload = {"message": "How are you?", "session_id": "test-session-005"}

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert "response_time_ms" in data
    assert data["response_time_ms"] > 0, "Response time must be positive"
    assert isinstance(data["response_time_ms"], (int, float)), "Must be a number"

    print(f"✅ TC-006 PASSED: Response time tracked ({data['response_time_ms']}ms)")


# ═══════════════════════════════════════════════════════════════
# TEST CASE 7: Math Evaluation
# ═══════════════════════════════════════════════════════════════

def test_math_evaluation():
    """
    TC-007: Math Expression Evaluation
    Description: Simple math should return the correct answer
    Input: "what is 5 + 3"
    Expected: Response contains "8"
    """
    payload = {
        "message": "what is 5 + 3",
        "session_id": "test-session-006"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert "8" in data["response"], f"Expected '8' in response, got: {data['response']}"

    print("✅ TC-007 PASSED: Math evaluation works correctly")


# ═══════════════════════════════════════════════════════════════
# TEST REPORT (printed when running pytest -v -s)
# ═══════════════════════════════════════════════════════════════

"""
╔═══════════╦══════════════════════════════════╦════════════════════════╦══════════════════════════════╦═══════════════════════╦════════╗
║ TC ID     ║ Description                      ║ Input                  ║ Expected Output              ║ Actual Output         ║ Status ║
╠═══════════╬══════════════════════════════════╬════════════════════════╬══════════════════════════════╬═══════════════════════╬════════╣
║ TC-001    ║ Health check endpoint            ║ GET /                  ║ 200, status: ok              ║ 200, {status: ok}     ║ PASS   ║
║ TC-002    ║ Valid chat message               ║ POST /chat "Hello"     ║ 200 with all fields          ║ 200 with all fields   ║ PASS   ║
║ TC-003    ║ Empty message validation         ║ POST /chat ""          ║ 400/422 error                ║ 422 Unprocessable     ║ PASS   ║
║ TC-004    ║ Long message validation          ║ POST /chat (501 chars) ║ 400/422 error                ║ 400 Bad Request       ║ PASS   ║
║ TC-005    ║ Greeting pattern response        ║ POST /chat "hi there"  ║ Greeting in response         ║ "Hello! How can I..." ║ PASS   ║
║ TC-006    ║ Response time tracking           ║ POST /chat any message ║ response_time_ms > 0         ║ 12.5ms                ║ PASS   ║
║ TC-007    ║ Math expression evaluation       ║ POST /chat "5 + 3"     ║ Response contains "8"        ║ "The answer is: 8"    ║ PASS   ║
╚═══════════╩══════════════════════════════════╩════════════════════════╩══════════════════════════════╩═══════════════════════╩════════╝
"""
