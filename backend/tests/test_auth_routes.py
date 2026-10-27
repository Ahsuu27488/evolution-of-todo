"""Auth routes against a real database (skipped without TEST_DATABASE_URL).

Regression: signup failed with "Datetime values must have timezone information"
once sqlmodel >= 0.0.45 was installed, because User.created_at defaulted to a
naive datetime.utcnow().
"""

from collections.abc import AsyncGenerator

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.main import app


async def _client(db_session: AsyncSession) -> httpx.AsyncClient:
    async def override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_signup_then_signin_then_me(db_session: AsyncSession) -> None:
    try:
        async with await _client(db_session) as client:
            created = await client.post(
                "/api/auth/signup",
                json={
                    "email": "orbit@example.test",
                    "password": "Orbit-Test-123",  # shipshape:allow-secret (test fixture)
                    "first_name": "Ayla",
                },
            )
            assert created.status_code == 201, created.text
            assert created.json()["created_at"]

            signed_in = await client.post(
                "/api/auth/signin",
                json={"email": "orbit@example.test", "password": "Orbit-Test-123"},
            )
            assert signed_in.status_code == 200, signed_in.text
            token = signed_in.json()["access_token"]

            me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me.status_code == 200, me.text
            assert me.json()["email"] == "orbit@example.test"
    finally:
        app.dependency_overrides.clear()
