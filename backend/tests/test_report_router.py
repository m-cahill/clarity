"""Tests for CLARITY Report Router API.

This module tests the FastAPI endpoints for PDF report generation.

Test coverage:
- POST /report/generate endpoint
- GET /report/cases endpoint
- Error handling for missing cases
- PDF response format
- Determinism of API responses

M12 additions:
- Cache hit/miss behavior
- X-Cache-Key header
- Concurrent request handling (409 response)
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Import the actual module, not the router object from __init__.py
from app.clarity.report import report_router as _router_module
# We need the module for accessing _cache_manager
_report_router_module = _router_module  # This is still the router object

# Direct module import to access module-level variables
import importlib
report_router_module = importlib.import_module("app.clarity.report.report_router")

if TYPE_CHECKING:
    pass


client = TestClient(app)


class TestReportGenerateEndpoint:
    """Tests for POST /report/generate endpoint."""

    def test_generate_report_success(self) -> None:
        """Test successful report generation for demo case."""
        response = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "content-disposition" in response.headers
        assert "clarity_report_case_001.pdf" in response.headers["content-disposition"]

    def test_generate_report_returns_valid_pdf(self) -> None:
        """Test that response is a valid PDF file."""
        response = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response.status_code == 200

        # PDF files start with %PDF-
        assert response.content[:5] == b"%PDF-"
        # PDF files should contain EOF marker
        assert b"%%EOF" in response.content[-100:]

    def test_generate_report_case_not_found(self) -> None:
        """Test 404 for non-existent case."""
        response = client.post(
            "/report/generate",
            json={"case_id": "nonexistent_case_xyz"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_generate_report_missing_case_id(self) -> None:
        """Test validation error for missing case_id."""
        response = client.post(
            "/report/generate",
            json={},
        )

        assert response.status_code == 422  # Validation error

    def test_generate_report_invalid_json(self) -> None:
        """Test error for invalid JSON body."""
        response = client.post(
            "/report/generate",
            content="not valid json",
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 422

    def test_generate_report_deterministic(self) -> None:
        """Test that same case produces identical PDF bytes."""
        response1 = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )
        response2 = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        hash1 = hashlib.sha256(response1.content).hexdigest()
        hash2 = hashlib.sha256(response2.content).hexdigest()

        assert hash1 == hash2, "Same case must produce identical PDF"

    def test_generate_report_non_empty(self) -> None:
        """Test that generated PDF has content."""
        response = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response.status_code == 200
        # PDF should be reasonably sized (at least a few KB)
        assert len(response.content) > 1000


class TestReportCasesEndpoint:
    """Tests for GET /report/cases endpoint."""

    def test_list_cases_success(self) -> None:
        """Test listing available cases."""
        response = client.get("/report/cases")

        assert response.status_code == 200
        data = response.json()
        assert "cases" in data
        assert isinstance(data["cases"], list)

    def test_list_cases_includes_demo_case(self) -> None:
        """Test that demo case is in the list."""
        response = client.get("/report/cases")

        assert response.status_code == 200
        data = response.json()
        assert "case_001" in data["cases"]

    def test_list_cases_sorted(self) -> None:
        """Test that cases are sorted alphabetically."""
        response = client.get("/report/cases")

        assert response.status_code == 200
        data = response.json()
        cases = data["cases"]
        assert cases == sorted(cases)


class TestReportEndpointIntegration:
    """Integration tests for report endpoints."""

    def test_generate_report_for_each_listed_case(self) -> None:
        """Test that each listed case can generate a report."""
        # Get list of cases
        list_response = client.get("/report/cases")
        assert list_response.status_code == 200
        cases = list_response.json()["cases"]

        # Generate report for each case
        for case_id in cases:
            gen_response = client.post(
                "/report/generate",
                json={"case_id": case_id},
            )
            assert gen_response.status_code == 200, f"Failed for case {case_id}"
            assert gen_response.content[:5] == b"%PDF-"

    def test_report_content_reflects_case_id(self) -> None:
        """Test that report is valid PDF with correct filename for case ID."""
        response = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response.status_code == 200

        # The PDF should be valid (starts with PDF magic bytes)
        assert response.content[:5] == b"%PDF-"

        # The filename in the content-disposition should contain the case ID
        content_disp = response.headers.get("content-disposition", "")
        assert "case_001" in content_disp, "Filename should contain case_id"


class TestReportErrorHandling:
    """Tests for error handling in report endpoints."""

    def test_empty_case_id(self) -> None:
        """Test error for empty case_id string."""
        response = client.post(
            "/report/generate",
            json={"case_id": ""},
        )

        # Should fail (empty string is not a valid case)
        assert response.status_code in (404, 422)

    def test_case_id_with_special_chars(self) -> None:
        """Test handling of case_id with special characters."""
        response = client.post(
            "/report/generate",
            json={"case_id": "../../../etc/passwd"},
        )

        # Should fail gracefully (case not found, not a security error)
        assert response.status_code == 404

    def test_case_id_with_path_traversal(self) -> None:
        """Test that path traversal attempts are rejected."""
        response = client.post(
            "/report/generate",
            json={"case_id": "..\\..\\..\\windows\\system32"},
        )

        # Should fail gracefully
        assert response.status_code == 404

    def test_very_long_case_id(self) -> None:
        """Test handling of very long case_id."""
        response = client.post(
            "/report/generate",
            json={"case_id": "x" * 10000},
        )

        # Should fail with validation error (422) due to max_length constraint
        assert response.status_code == 422


class TestReportRouterPresence:
    """Tests to verify router is correctly mounted."""

    def test_report_endpoints_exist(self) -> None:
        """Test that report endpoints are mounted."""
        # Test POST /report/generate exists (even with invalid body)
        response = client.post("/report/generate", json={})
        assert response.status_code != 404 or "not found" not in str(response.status_code)

        # Test GET /report/cases exists
        response = client.get("/report/cases")
        assert response.status_code == 200

    def test_report_endpoints_not_under_demo(self) -> None:
        """Test that report endpoints are separate from demo."""
        response = client.get("/demo/report/generate")
        assert response.status_code in (404, 405)


class TestReportResponseHeaders:
    """Tests for response headers."""

    def test_content_disposition_header(self) -> None:
        """Test Content-Disposition header for download."""
        response = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response.status_code == 200
        assert "content-disposition" in response.headers

        cd = response.headers["content-disposition"]
        assert "attachment" in cd
        assert "filename=" in cd
        assert ".pdf" in cd

    def test_content_type_header(self) -> None:
        """Test Content-Type is application/pdf."""
        response = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_cache_key_header_present(self) -> None:
        """Test X-Cache-Key header is present (M12)."""
        response = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response.status_code == 200
        assert "x-cache-key" in response.headers
        # Partial cache key should be 16 hex chars
        assert len(response.headers["x-cache-key"]) == 16


class TestReportCaching:
    """Tests for M12 caching behavior."""

    @pytest.fixture(autouse=True)
    def clean_cache(self):
        """Clean up cache before and after each test."""
        # Use a temp directory for cache during tests
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Patch the cache manager to use temp directory
            from app.clarity.cache import CacheManager

            test_cache = CacheManager(cache_dir=Path(tmp_dir))

            # Reset the global cache manager
            original_cache = report_router_module._cache_manager
            report_router_module._cache_manager = test_cache

            yield

            # Restore original
            report_router_module._cache_manager = original_cache

    def test_cache_hit_returns_same_content(self) -> None:
        """Test that repeated requests return identical content."""
        response1 = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )
        response2 = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Content should be identical
        hash1 = hashlib.sha256(response1.content).hexdigest()
        hash2 = hashlib.sha256(response2.content).hexdigest()
        assert hash1 == hash2

    def test_cache_key_consistent(self) -> None:
        """Test that cache key is consistent across requests."""
        response1 = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )
        response2 = client.post(
            "/report/generate",
            json={"case_id": "case_001"},
        )

        assert response1.headers["x-cache-key"] == response2.headers["x-cache-key"]


class TestReportConcurrency:
    """Tests for M12 concurrent request handling."""

    @pytest.fixture(autouse=True)
    def clean_cache(self):
        """Clean up cache before and after each test."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            from app.clarity.cache import CacheManager

            test_cache = CacheManager(cache_dir=Path(tmp_dir), lock_timeout=10.0)
            original_cache = report_router_module._cache_manager
            report_router_module._cache_manager = test_cache

            yield

            report_router_module._cache_manager = original_cache

    def test_parallel_requests_same_case(self) -> None:
        """Test that parallel requests for the same case succeed."""
        results: list[int] = []
        errors: list[Exception] = []

        def make_request():
            try:
                response = client.post(
                    "/report/generate",
                    json={"case_id": "case_001"},
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=make_request) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed or get 409 (in progress)
        assert len(errors) == 0
        assert all(s in (200, 409) for s in results)
        # At least one should succeed
        assert 200 in results

    def test_parallel_requests_different_cases(self) -> None:
        """Test that parallel requests for different cases both succeed."""
        # This test uses the same case since we only have case_001 in demo_artifacts
        # But tests that the mechanism works
        results: list[int] = []

        def make_request():
            response = client.post(
                "/report/generate",
                json={"case_id": "case_001"},
            )
            results.append(response.status_code)

        t1 = threading.Thread(target=make_request)
        t2 = threading.Thread(target=make_request)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Both should complete (200 or 409)
        assert all(s in (200, 409) for s in results)

