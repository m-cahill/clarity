"""Tests for Counterfactual API Router (M09).

This module contains API-level tests for the counterfactual endpoints.

Test Categories:
1. POST /counterfactual/run (8 tests)
2. GET /counterfactual/baselines (4 tests)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Return test client."""
    return TestClient(app)


# =============================================================================
# Category 1: POST /counterfactual/run (8 tests)
# =============================================================================


class TestCounterfactualRunEndpoint:
    """Tests for POST /counterfactual/run."""

    def test_run_success(self, client: TestClient) -> None:
        """Test successful run endpoint."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "test-baseline-001",
                "grid_size": 2,
                "axis": "brightness",
                "value": "1p0",
            },
        )
        assert response.status_code == 200

    def test_run_returns_baseline_id(self, client: TestClient) -> None:
        """Test response contains baseline_id."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "test-baseline-001",
                "grid_size": 2,
                "axis": "brightness",
                "value": "1p0",
            },
        )
        data = response.json()
        assert data["baseline_id"] == "test-baseline-001"

    def test_run_returns_config(self, client: TestClient) -> None:
        """Test response contains config."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "test-baseline-001",
                "grid_size": 3,
                "axis": "brightness",
                "value": "1p0",
            },
        )
        data = response.json()
        assert data["config"]["grid_size"] == 3
        assert data["config"]["axis"] == "brightness"

    def test_run_returns_probe_surface(self, client: TestClient) -> None:
        """Test response contains probe_surface."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "test-baseline-001",
                "grid_size": 2,
                "axis": "brightness",
                "value": "1p0",
            },
        )
        data = response.json()
        assert "probe_surface" in data
        assert "results" in data["probe_surface"]
        assert len(data["probe_surface"]["results"]) == 4  # 2×2

    def test_run_invalid_baseline_returns_400(self, client: TestClient) -> None:
        """Test invalid baseline returns 400."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "nonexistent",
                "grid_size": 2,
                "axis": "brightness",
                "value": "1p0",
            },
        )
        assert response.status_code == 400
        assert "Baseline not found" in response.json()["detail"]

    def test_run_invalid_grid_size_returns_422(self, client: TestClient) -> None:
        """Test invalid grid_size returns 422 (validation error)."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "test-baseline-001",
                "grid_size": 0,  # Must be >= 1
                "axis": "brightness",
                "value": "1p0",
            },
        )
        assert response.status_code == 422

    def test_run_missing_field_returns_422(self, client: TestClient) -> None:
        """Test missing required field returns 422."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "test-baseline-001",
                # Missing axis and value
            },
        )
        assert response.status_code == 422

    def test_run_default_grid_size(self, client: TestClient) -> None:
        """Test default grid_size is used if not provided."""
        response = client.post(
            "/counterfactual/run",
            json={
                "baseline_id": "test-baseline-001",
                "axis": "brightness",
                "value": "1p0",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["grid_size"] == 3  # Default


# =============================================================================
# Category 2: GET /counterfactual/baselines (4 tests)
# =============================================================================


class TestBaselinesEndpoint:
    """Tests for GET /counterfactual/baselines."""

    def test_baselines_returns_200(self, client: TestClient) -> None:
        """Test baselines endpoint returns 200."""
        response = client.get("/counterfactual/baselines")
        assert response.status_code == 200

    def test_baselines_returns_list(self, client: TestClient) -> None:
        """Test baselines endpoint returns list."""
        response = client.get("/counterfactual/baselines")
        data = response.json()
        assert "baselines" in data
        assert isinstance(data["baselines"], list)

    def test_baselines_contains_expected(self, client: TestClient) -> None:
        """Test baselines contains expected IDs."""
        response = client.get("/counterfactual/baselines")
        data = response.json()
        assert "test-baseline-001" in data["baselines"]
        assert "test-baseline-002" in data["baselines"]

    def test_baselines_sorted(self, client: TestClient) -> None:
        """Test baselines are sorted."""
        response = client.get("/counterfactual/baselines")
        data = response.json()
        assert data["baselines"] == sorted(data["baselines"])

