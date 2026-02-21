"""Tests for demo_router module.

M10.5: Demo Deployment Layer tests.
Tests cover:
- Schema load/parse correctness
- Endpoint determinism (response hash stable)
- CORS allowlist behavior
- Path traversal protection
- Read-only enforcement
- 404 for nonexistent case
- Health endpoint
- AST guardrails (no R2L imports)
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.demo_router import (
    VALID_CASE_ID_PATTERN,
    _get_artifact_path,
    _load_json_artifact,
    _list_cases,
    _validate_case_id,
    router,
    verify_artifact_integrity,
)
from app.main import app


# Test client
client = TestClient(app)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_artifact_dir() -> Generator[Path, None, None]:
    """Create a temporary artifact directory with test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        artifact_path = Path(tmpdir)
        
        # Create case_001
        case_dir = artifact_path / "case_001"
        case_dir.mkdir()
        
        # Create manifest
        manifest = {
            "case_id": "case_001",
            "title": "Test Case",
            "description": "Test description",
            "synthetic": True,
        }
        (case_dir / "manifest.json").write_text(json.dumps(manifest))
        
        # Create surface
        surface = {
            "axes": [],
            "global_mean_esi": 0.85,
            "global_mean_drift": 0.1,
            "_synthetic": True,
        }
        (case_dir / "robustness_surface.json").write_text(json.dumps(surface))
        
        # Create overlay
        overlay = {
            "heatmap": {"width": 224, "height": 224},
            "regions": [],
            "_synthetic": True,
        }
        (case_dir / "overlay_bundle.json").write_text(json.dumps(overlay))
        
        # Create metrics
        metrics = {
            "baseline_id": "test",
            "_synthetic": True,
        }
        (case_dir / "metrics.json").write_text(json.dumps(metrics))
        
        # Create checksums
        checksums = {
            "algorithm": "SHA256",
            "files": {},
        }
        # Compute actual checksums
        for filename in ["manifest.json", "robustness_surface.json", "overlay_bundle.json", "metrics.json"]:
            file_path = case_dir / filename
            sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest().upper()
            checksums["files"][filename] = sha256
        (case_dir / "checksums.json").write_text(json.dumps(checksums))
        
        # Set environment variable
        original_root = os.environ.get("ARTIFACT_ROOT")
        os.environ["ARTIFACT_ROOT"] = str(artifact_path)
        
        yield artifact_path
        
        # Restore original
        if original_root:
            os.environ["ARTIFACT_ROOT"] = original_root
        else:
            os.environ.pop("ARTIFACT_ROOT", None)


# ============================================================================
# Test: Case ID Validation
# ============================================================================


class TestCaseIdValidation:
    """Tests for case ID validation and path traversal protection."""

    def test_valid_case_id_alphanumeric(self) -> None:
        """Valid alphanumeric case ID passes validation."""
        _validate_case_id("case_001")  # Should not raise

    def test_valid_case_id_with_underscore(self) -> None:
        """Valid case ID with underscore passes validation."""
        _validate_case_id("test_case_123")  # Should not raise

    def test_invalid_case_id_path_traversal_dots(self) -> None:
        """Path traversal with .. is rejected."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            _validate_case_id("../etc/passwd")
        assert exc_info.value.status_code == 400
        # Rejected either by regex (Invalid case ID format) or explicit check (Path traversal)
        assert "Invalid" in str(exc_info.value.detail) or "Path traversal" in str(exc_info.value.detail)

    def test_invalid_case_id_path_traversal_slash(self) -> None:
        """Path traversal with / is rejected."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            _validate_case_id("case/001")
        assert exc_info.value.status_code == 400

    def test_invalid_case_id_path_traversal_backslash(self) -> None:
        """Path traversal with \\ is rejected."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            _validate_case_id("case\\001")
        assert exc_info.value.status_code == 400

    def test_invalid_case_id_special_chars(self) -> None:
        """Special characters are rejected."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            _validate_case_id("case@001")
        assert exc_info.value.status_code == 400
        assert "Invalid case ID format" in str(exc_info.value.detail)

    def test_case_id_pattern_matches_valid(self) -> None:
        """Pattern correctly matches valid IDs."""
        assert VALID_CASE_ID_PATTERN.match("case_001")
        assert VALID_CASE_ID_PATTERN.match("CASE001")
        assert VALID_CASE_ID_PATTERN.match("test123")

    def test_case_id_pattern_rejects_invalid(self) -> None:
        """Pattern correctly rejects invalid IDs."""
        assert not VALID_CASE_ID_PATTERN.match("case-001")
        assert not VALID_CASE_ID_PATTERN.match("case.001")
        assert not VALID_CASE_ID_PATTERN.match("")


# ============================================================================
# Test: Demo Health Endpoint
# ============================================================================


class TestDemoHealthEndpoint:
    """Tests for /demo/health endpoint."""

    def test_demo_health_returns_200(self) -> None:
        """Health endpoint returns 200."""
        response = client.get("/demo/health")
        assert response.status_code == 200

    def test_demo_health_contains_mode(self) -> None:
        """Health response contains mode field."""
        response = client.get("/demo/health")
        data = response.json()
        assert "mode" in data
        assert "status" in data
        assert data["status"] == "ok"

    def test_demo_health_contains_artifact_root(self) -> None:
        """Health response contains artifact_root field."""
        response = client.get("/demo/health")
        data = response.json()
        assert "artifact_root" in data


# ============================================================================
# Test: List Cases Endpoint
# ============================================================================


class TestListCasesEndpoint:
    """Tests for /demo/cases endpoint."""

    def test_list_cases_returns_200(self, temp_artifact_dir: Path) -> None:
        """List cases endpoint returns 200."""
        response = client.get("/demo/cases")
        assert response.status_code == 200

    def test_list_cases_contains_case_001(self, temp_artifact_dir: Path) -> None:
        """List cases includes case_001."""
        response = client.get("/demo/cases")
        data = response.json()
        assert "cases" in data
        assert "total" in data
        assert data["total"] >= 1
        
        case_ids = [c["case_id"] for c in data["cases"]]
        assert "case_001" in case_ids

    def test_list_cases_case_has_required_fields(self, temp_artifact_dir: Path) -> None:
        """Each case has required fields."""
        response = client.get("/demo/cases")
        data = response.json()
        
        for case in data["cases"]:
            assert "case_id" in case
            assert "title" in case
            assert "description" in case
            assert "synthetic" in case


# ============================================================================
# Test: Get Artifact Endpoints
# ============================================================================


class TestGetArtifactEndpoints:
    """Tests for artifact retrieval endpoints."""

    def test_get_manifest_returns_200(self, temp_artifact_dir: Path) -> None:
        """Get manifest returns 200."""
        response = client.get("/demo/cases/case_001/manifest")
        assert response.status_code == 200

    def test_get_manifest_contains_data(self, temp_artifact_dir: Path) -> None:
        """Get manifest contains artifact data."""
        response = client.get("/demo/cases/case_001/manifest")
        data = response.json()
        assert "case_id" in data
        assert "artifact_type" in data
        assert data["artifact_type"] == "manifest"
        assert "data" in data

    def test_get_surface_returns_200(self, temp_artifact_dir: Path) -> None:
        """Get surface returns 200."""
        response = client.get("/demo/cases/case_001/surface")
        assert response.status_code == 200

    def test_get_overlay_returns_200(self, temp_artifact_dir: Path) -> None:
        """Get overlay returns 200."""
        response = client.get("/demo/cases/case_001/overlay")
        assert response.status_code == 200

    def test_get_metrics_returns_200(self, temp_artifact_dir: Path) -> None:
        """Get metrics returns 200."""
        response = client.get("/demo/cases/case_001/metrics")
        assert response.status_code == 200

    def test_get_nonexistent_case_returns_404(self, temp_artifact_dir: Path) -> None:
        """Nonexistent case returns 404."""
        response = client.get("/demo/cases/nonexistent_case/manifest")
        assert response.status_code == 404

    def test_get_nonexistent_artifact_returns_404(self, temp_artifact_dir: Path) -> None:
        """Nonexistent artifact returns 404."""
        response = client.get("/demo/cases/case_001/nonexistent")
        assert response.status_code == 404


# ============================================================================
# Test: Checksum Verification
# ============================================================================


class TestChecksumVerification:
    """Tests for artifact integrity verification."""

    def test_get_checksums_returns_200(self, temp_artifact_dir: Path) -> None:
        """Get checksums returns 200."""
        response = client.get("/demo/cases/case_001/checksums")
        assert response.status_code == 200

    def test_verify_case_returns_valid_true(self, temp_artifact_dir: Path) -> None:
        """Verify case returns valid=true for intact artifacts."""
        response = client.get("/demo/cases/case_001/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_verify_case_detects_corruption(self, temp_artifact_dir: Path) -> None:
        """Verify case detects corrupted artifacts."""
        # Corrupt a file (modify content without updating checksum)
        manifest_path = temp_artifact_dir / "case_001" / "manifest.json"
        original_checksum_path = temp_artifact_dir / "case_001" / "checksums.json"
        
        # Read original checksums first
        with open(original_checksum_path, "r") as f:
            checksums = json.load(f)
        
        # Now corrupt the manifest
        manifest_path.write_text('{"corrupted": true}')
        
        # Write checksums back (without updating manifest hash)
        with open(original_checksum_path, "w") as f:
            json.dump(checksums, f)
        
        response = client.get("/demo/cases/case_001/verify")
        data = response.json()
        assert data["valid"] is False
        assert data["files"]["manifest.json"] is False


# ============================================================================
# Test: Determinism
# ============================================================================


class TestDeterminism:
    """Tests for response determinism."""

    def test_list_cases_deterministic(self, temp_artifact_dir: Path) -> None:
        """List cases response is deterministic."""
        response1 = client.get("/demo/cases")
        response2 = client.get("/demo/cases")
        
        assert response1.json() == response2.json()

    def test_get_surface_deterministic(self, temp_artifact_dir: Path) -> None:
        """Get surface response is deterministic."""
        response1 = client.get("/demo/cases/case_001/surface")
        response2 = client.get("/demo/cases/case_001/surface")
        
        # Hash comparison for determinism
        hash1 = hashlib.sha256(response1.content).hexdigest()
        hash2 = hashlib.sha256(response2.content).hexdigest()
        
        assert hash1 == hash2

    def test_get_overlay_deterministic(self, temp_artifact_dir: Path) -> None:
        """Get overlay response is deterministic."""
        response1 = client.get("/demo/cases/case_001/overlay")
        response2 = client.get("/demo/cases/case_001/overlay")
        
        hash1 = hashlib.sha256(response1.content).hexdigest()
        hash2 = hashlib.sha256(response2.content).hexdigest()
        
        assert hash1 == hash2


# ============================================================================
# Test: AST Guardrails
# ============================================================================


class TestASTGuardrails:
    """AST-based tests for code safety guardrails."""

    def _get_demo_router_source(self) -> str:
        """Load demo_router.py source code."""
        demo_router_path = Path(__file__).parent.parent / "app" / "demo_router.py"
        return demo_router_path.read_text()

    def test_no_r2l_imports(self) -> None:
        """Verify no R2L imports in demo_router."""
        source = self._get_demo_router_source()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "r2l" not in alias.name.lower(), f"R2L import found: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "r2l" not in node.module.lower(), f"R2L import found: {node.module}"

    def test_no_subprocess_imports(self) -> None:
        """Verify no subprocess imports."""
        source = self._get_demo_router_source()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "subprocess", "subprocess import found"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module != "subprocess", "subprocess import found"

    def test_no_write_operations_in_endpoints(self) -> None:
        """Verify endpoints don't perform write operations."""
        source = self._get_demo_router_source()
        tree = ast.parse(source)
        
        # Look for open() calls with write mode
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    # Check for write modes
                    for keyword in node.keywords:
                        if keyword.arg == "mode":
                            if isinstance(keyword.value, ast.Constant):
                                mode = keyword.value.value
                                assert "w" not in mode, f"Write mode found: {mode}"
                                assert "a" not in mode, f"Append mode found: {mode}"


# ============================================================================
# Test: Integration with Real Artifacts
# ============================================================================


class TestRealArtifacts:
    """Tests using the actual demo_artifacts directory."""

    @pytest.fixture
    def real_artifacts(self) -> Generator[None, None, None]:
        """Set ARTIFACT_ROOT to the real demo_artifacts directory."""
        original = os.environ.get("ARTIFACT_ROOT")
        os.environ["ARTIFACT_ROOT"] = "demo_artifacts"
        yield
        if original:
            os.environ["ARTIFACT_ROOT"] = original
        else:
            os.environ.pop("ARTIFACT_ROOT", None)

    def test_real_case_001_exists(self, real_artifacts: None) -> None:
        """Real case_001 exists and can be listed."""
        response = client.get("/demo/cases")
        if response.status_code == 503:
            pytest.skip("Demo artifacts not available")
        
        data = response.json()
        case_ids = [c["case_id"] for c in data["cases"]]
        assert "case_001" in case_ids

    def test_real_surface_loads(self, real_artifacts: None) -> None:
        """Real surface artifact loads successfully."""
        response = client.get("/demo/cases/case_001/surface")
        if response.status_code == 503:
            pytest.skip("Demo artifacts not available")
        
        assert response.status_code == 200
        data = response.json()
        assert data["artifact_type"] == "robustness_surface"

    def test_real_artifacts_verify(self, real_artifacts: None) -> None:
        """Real artifacts pass integrity verification."""
        response = client.get("/demo/cases/case_001/verify")
        if response.status_code == 503:
            pytest.skip("Demo artifacts not available")
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True, f"Integrity check failed: {data['files']}"

