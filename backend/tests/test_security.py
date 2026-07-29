import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.security.rate_limit import LoginRateLimiter


def test_production_rejects_default_jwt_secret() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET_KEY"):
        Settings(environment="production", jwt_secret_key="change-me-in-production")


def test_rate_limiter_blocks_after_limit_and_can_reset() -> None:
    limiter = LoginRateLimiter()
    assert limiter.allowed("client", 2, 60)
    assert limiter.allowed("client", 2, 60)
    assert not limiter.allowed("client", 2, 60)
    limiter.reset("client")
    assert limiter.allowed("client", 2, 60)


def test_invalid_and_expired_tokens_are_rejected(client: TestClient) -> None:
    assert client.get(
        "/api/v1/staff/dashboard", headers={"Authorization": "Bearer not-a-jwt"}
    ).status_code == 401


def test_security_headers_are_present(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_login_rate_limit_returns_429(client: TestClient) -> None:
    for _ in range(5):
        response = client.post(
            "/api/v1/staff/login",
            json={"email": "rate-limit@example.test", "password": "wrong"},
        )
        assert response.status_code == 401
    response = client.post(
        "/api/v1/staff/login",
        json={"email": "rate-limit@example.test", "password": "wrong"},
    )
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
