"""Unit tests for JWT verification middleware."""

import os
import sys
import importlib
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

# Define test constants
TEST_SECRET = "test-secret-key-for-testing-only-32-chars"
TEST_ALGORITHM = "HS256"

# Set environment variable BEFORE importing/reloading app modules
os.environ["BETTER_AUTH_SECRET"] = TEST_SECRET

# Import and reload the module to ensure it picks up the environment variable
import app.jwt_middleware
importlib.reload(app.jwt_middleware)

from app.jwt_middleware import (
    JWTTokenPayload,
    decode_jwt_token,
    extract_token_from_header,
    get_current_user_id,
    verify_jwt_token,
)

def create_test_token(
    payload: dict,
    expires_in: int = 3600,
    secret: str = TEST_SECRET,
) -> str:
    """Create a test JWT token with dynamic timestamps using system time."""
    now = int(time.time())
    token_payload = {
        **payload,
        "iat": now,
        "exp": now + expires_in,
    }
    return jwt.encode(token_payload, secret, algorithm=TEST_ALGORITHM)


class TestJWTTokenPayload:
    """Tests for JWTTokenPayload class."""

    def test_payload_with_all_fields(self):
        """Test payload parsing with all standard fields."""
        now = int(time.time())
        payload = {
            "sub": "user123",
            "email": "user@example.com",
            "name": "Test User",
            "sessionId": "sess_abc123",
            "iat": now,
            "exp": now + 3600,
        }
        token = JWTTokenPayload(payload)

        assert token.sub == "user123"
        assert token.email == "user@example.com"
        assert token.name == "Test User"
        assert token.session_id == "sess_abc123"
        assert token.iat == now
        assert token.exp == now + 3600

    def test_payload_with_minimal_fields(self):
        """Test payload parsing with only required fields."""
        payload = {"sub": "minimal_user"}
        token = JWTTokenPayload(payload)

        assert token.sub == "minimal_user"
        assert token.email is None
        assert token.name is None
        assert token.session_id is None

    def test_payload_repr(self):
        """Test __repr__ method includes sub and session_id."""
        payload = {"sub": "user123", "sessionId": "sess_abc"}
        token = JWTTokenPayload(payload)

        repr_str = repr(token)
        assert "user123" in repr_str
        assert "sess_abc" in repr_str


class TestDecodeJWTToken:
    """Tests for decode_jwt_token function."""

    def test_valid_token_decoding(self):
        """Test decoding a valid JWT token."""
        token = create_test_token({"sub": "user123", "email": "user@example.com"})
        payload = decode_jwt_token(token)

        assert isinstance(payload, JWTTokenPayload)
        assert payload.sub == "user123"
        assert payload.email == "user@example.com"

    def test_token_with_bearer_prefix(self):
        """Test decoding token with Bearer prefix."""
        token = create_test_token({"sub": "user456"})
        payload = decode_jwt_token(f"Bearer {token}")

        assert payload.sub == "user456"

    def test_expired_token(self):
        """Test that expired tokens raise HTTPException."""
        # Create token that expired 1 hour ago
        token = create_test_token({"sub": "user123"}, expires_in=-3600)

        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token(token)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_invalid_signature(self):
        """Test that tokens with invalid signature raise HTTPException."""
        # Create token with different secret
        token = create_test_token({"sub": "user123"}, secret="different-secret")

        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token(token)

        assert exc_info.value.status_code == 401
        assert "signature" in exc_info.value.detail.lower()

    def test_malformed_token(self):
        """Test that malformed tokens raise HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token("not-a-valid-token")

        assert exc_info.value.status_code == 401


class TestVerifyJWTToken:
    """Tests for verify_jwt_token dependency."""

    def test_valid_credentials(self):
        """Test verification with valid credentials."""
        token = create_test_token({"sub": "user789"})
        credentials = MagicMock()
        credentials.credentials = token
        credentials.__bool__ = MagicMock(return_value=True)

        payload = verify_jwt_token(credentials)
        assert payload.sub == "user789"

    def test_no_credentials(self):
        """Test that missing credentials raise HTTPException."""
        credentials = None

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(credentials)

        assert exc_info.value.status_code == 403

    def test_empty_token(self):
        """Test that empty token raises HTTPException."""
        credentials = MagicMock()
        credentials.credentials = ""
        credentials.__bool__ = MagicMock(return_value=True)

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(credentials)

        assert exc_info.value.status_code == 401


class TestGetCurrentUserID:
    """Tests for get_current_user_id function."""

    def test_valid_user_id(self):
        """Test extracting user ID from valid payload."""
        payload = JWTTokenPayload({"sub": "user123"})

        user_id = get_current_user_id(payload)
        assert user_id == "user123"

    def test_missing_sub_claim(self):
        """Test that missing 'sub' claim raises HTTPException."""
        payload = JWTTokenPayload({"email": "user@example.com"})

        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(payload)

        assert exc_info.value.status_code == 401
        assert "user identifier" in exc_info.value.detail.lower()


class TestExtractTokenFromHeader:
    """Tests for extract_token_from_header function."""

    def test_extract_bearer_token(self):
        """Test extracting token from Bearer header."""
        request = MagicMock()
        request.headers.get.return_value = "Bearer test-token-abc"

        token = extract_token_from_header(request)
        assert token == "test-token-abc"

    def test_extract_plain_token(self):
        """Test extracting plain token without Bearer prefix."""
        request = MagicMock()
        request.headers.get.return_value = "plain-token-xyz"

        token = extract_token_from_header(request)
        assert token == "plain-token-xyz"

    def test_no_auth_header(self):
        """Test that missing auth header returns None."""
        request = MagicMock()
        request.headers.get.return_value = None

        token = extract_token_from_header(request)
        assert token is None


class TestJWTWorkflow:
    """Integration-style tests for complete JWT workflow."""

    def test_complete_auth_flow(self):
        """Test complete authentication flow: create -> verify -> extract."""
        # 1. Create token
        token = create_test_token({
            "sub": "workflow_user",
            "email": "workflow@example.com",
            "sessionId": "sess_workflow_123"
        })

        # 2. Decode token
        payload = decode_jwt_token(token)
        assert payload.sub == "workflow_user"
        assert payload.email == "workflow@example.com"
        assert payload.session_id == "sess_workflow_123"

        # 3. Get user ID
        user_id = get_current_user_id(payload)
        assert user_id == "workflow_user"

    def test_user_isolation(self):
        """Test that user isolation works correctly."""
        # Create tokens for two different users
        token_user_a = create_test_token({"sub": "user_a"})
        token_user_b = create_test_token({"sub": "user_b"})

        payload_a = decode_jwt_token(token_user_a)
        payload_b = decode_jwt_token(token_user_b)

        assert payload_a.sub != payload_b.sub
        assert payload_a.sub == "user_a"
        assert payload_b.sub == "user_b"
