"""Test configuration and fixtures."""

import os

# Set environment variables for all tests
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-only-32-chars"
