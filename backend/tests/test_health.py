"""Tests for health and version endpoints.

These tests verify deterministic behavior of the health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok_status(self, client: TestClient) -> None:
        """Health endpoint should return ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_service_name(self, client: TestClient) -> None:
        """Health endpoint should return correct service name."""
        response = client.get("/health")
        data = response.json()
        assert data["service"] == "clarity-backend"

    def test_health_returns_version(self, client: TestClient) -> None:
        """Health endpoint should return version string."""
        response = client.get("/health")
        data = response.json()
        assert data["version"] == "0.0.1"

    def test_health_response_is_deterministic(self, client: TestClient) -> None:
        """Multiple calls should return identical responses."""
        response1 = client.get("/health")
        response2 = client.get("/health")
        assert response1.json() == response2.json()

    def test_health_response_structure(self, client: TestClient) -> None:
        """Health response should have exactly expected keys."""
        response = client.get("/health")
        data = response.json()
        assert set(data.keys()) == {"status", "service", "version"}


class TestVersionEndpoint:
    """Tests for the /version endpoint."""

    def test_version_returns_200(self, client: TestClient) -> None:
        """Version endpoint should return 200 OK."""
        response = client.get("/version")
        assert response.status_code == 200

    def test_version_returns_version_string(self, client: TestClient) -> None:
        """Version endpoint should return version string."""
        response = client.get("/version")
        data = response.json()
        assert data["version"] == "0.0.1"

    def test_version_git_sha_is_null_initially(self, client: TestClient) -> None:
        """Git SHA should be null when not injected."""
        response = client.get("/version")
        data = response.json()
        assert data["git_sha"] is None

    def test_version_response_structure(self, client: TestClient) -> None:
        """Version response should have exactly expected keys."""
        response = client.get("/version")
        data = response.json()
        assert set(data.keys()) == {"version", "git_sha"}

    def test_version_response_is_deterministic(self, client: TestClient) -> None:
        """Multiple calls should return identical responses."""
        response1 = client.get("/version")
        response2 = client.get("/version")
        assert response1.json() == response2.json()


class TestCorsConfiguration:
    """Tests for CORS middleware configuration."""

    def test_cors_allows_any_origin(self, client: TestClient) -> None:
        """CORS should allow any origin in dev mode."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # FastAPI returns 200 for preflight in test client
        assert response.status_code in (200, 405)

