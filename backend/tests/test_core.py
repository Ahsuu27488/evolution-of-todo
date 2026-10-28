"""Database-free tests for the app's core wiring.

These run without Postgres (conftest sets placeholder env vars) and call the
real modules: URL normalisation, the models package, JWT round-trip and the
FastAPI app's route table.
"""

import pytest
from fastapi import HTTPException

from app.db import ssl_mode, to_async_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "postgresql://u:p@host/db?sslmode=require&channel_binding=require",
            "postgresql+asyncpg://u:p@host/db",
        ),
        # Legacy scheme used by Heroku/Render; SQLAlchemy has no "postgres" dialect.
        ("postgres://u:p@host:5432/db", "postgresql+asyncpg://u:p@host:5432/db"),
        ("postgresql+asyncpg://u:p@host/db", "postgresql+asyncpg://u:p@host/db"),
    ],
)
def test_to_async_url(url: str, expected: str) -> None:
    assert to_async_url(url) == expected


def test_ssl_required_unless_disabled() -> None:
    assert ssl_mode("postgresql://u:p@neon/db?sslmode=require") == "require"
    assert ssl_mode("postgresql://u:p@neon/db") == "require"
    assert ssl_mode("postgresql://postgres@127.0.0.1:5432/db?sslmode=disable") is False


def test_async_url_is_accepted_by_sqlalchemy() -> None:
    from sqlalchemy.engine import make_url

    url = make_url(to_async_url("postgres://u:p@host/db"))
    assert url.get_dialect().driver == "asyncpg"


def test_models_package_exports_core_and_notification_models() -> None:
    import app.models as models
    from app.models.core import Task

    assert models.Task is Task
    assert models.Task.__tablename__ == "tasks"
    for name in ("User", "TaskLog", "Notification", "PushSubscription", "EmailDeliveryLog"):
        assert hasattr(models, name), name


def test_jwt_round_trip() -> None:
    from app.simple_auth import create_access_token, verify_token

    token = create_access_token({"sub": "user-123"})
    assert verify_token(token)["sub"] == "user-123"


def test_jwt_rejects_tampered_token() -> None:
    from app.simple_auth import create_access_token, verify_token

    token = create_access_token({"sub": "user-123"})
    with pytest.raises(HTTPException):
        verify_token(token[:-2] + ("aa" if not token.endswith("aa") else "bb"))


def test_app_registers_all_routers() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    for path in (
        "/api/health",
        "/api/auth/signin",
        "/api/tasks",
        "/api/notifications/stream",
        "/api/chat",
    ):
        assert path in paths, path


def test_agents_sdk_usage_accepts_installed_openai() -> None:
    """Regression: openai 2.45+ made InputTokensDetails.cache_write_tokens required,
    so openai-agents 0.8 failed every chat run while building Usage()."""
    from agents.usage import Usage

    Usage()
