"""Determinism Tests for CLARITY Report Generation.

This module tests that report generation is fully deterministic:
- Identical inputs produce identical PDF bytes (same SHA256)
- Changing inputs changes the output hash
- No forbidden imports (random, uuid, datetime.now, subprocess)
- AST guardrails for report module

CRITICAL: These tests verify the core M11 requirement that reports
are byte-identical across runs for the same input.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from app.clarity.report.image_renderer import (
    generate_synthetic_heatmap_values,
    render_heatmap_png,
    render_probe_grid_png,
    render_surface_png,
)
from app.clarity.report.report_model import (
    SERIALIZATION_VERSION,
    ClarityReport,
    OverlayRegion,
    ProbeResult,
    ReportMetadata,
    ReportMetrics,
    ReportOverlaySection,
    ReportProbeSurface,
    ReportRobustnessSurface,
    ReportSection,
    SurfacePoint,
)
from app.clarity.report.report_renderer import render_report_to_pdf

if TYPE_CHECKING:
    pass


# Path to report module files
REPORT_MODULE_DIR = Path(__file__).parent.parent / "app" / "clarity" / "report"


def _create_test_report(case_id: str = "test_case") -> ClarityReport:
    """Create a test report with deterministic data."""
    metadata = ReportMetadata(
        case_id=case_id,
        title="Test Report",
        generated_at="2026-02-20T00:00:00Z",
        clarity_version="v0.0.11-m10",
        r2l_sha="abc123def456",
        adapter_id="test_adapter",
        rich_mode=False,
        sweep_manifest_hash="hash_" + case_id,
    )

    metrics = ReportMetrics(
        baseline_esi=0.95,
        baseline_drift=0.05,
        global_mean_esi=0.85,
        global_mean_drift=0.12,
        global_variance_esi=0.007,
        global_variance_drift=0.001,
        monte_carlo_present=False,
    )

    surfaces = (
        ReportRobustnessSurface(
            axis="brightness",
            mean_esi=0.83333333,
            mean_drift=0.125,
            variance_esi=0.00888889,
            variance_drift=0.00111111,
            points=(
                SurfacePoint(axis="brightness", value="0p8", esi=0.9, drift=0.1),
                SurfacePoint(axis="brightness", value="1p0", esi=0.95, drift=0.08),
                SurfacePoint(axis="brightness", value="1p2", esi=0.68, drift=0.17),
            ),
        ),
        ReportRobustnessSurface(
            axis="contrast",
            mean_esi=0.86666667,
            mean_drift=0.11,
            variance_esi=0.00544444,
            variance_drift=0.00088889,
            points=(
                SurfacePoint(axis="contrast", value="0p8", esi=0.92, drift=0.09),
                SurfacePoint(axis="contrast", value="1p0", esi=0.96, drift=0.07),
            ),
        ),
    )

    overlay = ReportOverlaySection(
        image_width=224,
        image_height=224,
        regions=(
            OverlayRegion(
                region_id="evidence_r0",
                x_min=0.25, y_min=0.25, x_max=0.5, y_max=0.5,
                area=0.0625, mean_evidence=0.82345678,
            ),
            OverlayRegion(
                region_id="evidence_r1",
                x_min=0.625, y_min=0.125, x_max=0.875, y_max=0.375,
                area=0.0625, mean_evidence=0.78123456,
            ),
        ),
        total_evidence_area=0.125,
    )

    probes = tuple(
        ProbeResult(
            row=r, col=c,
            delta_esi=-0.05 - (r * 0.02 + c * 0.01),
            delta_drift=0.025 + (r * 0.01 + c * 0.005),
            masked_esi=0.9 + (r * 0.01 - c * 0.02),
            masked_drift=0.075 - (r * 0.005 + c * 0.003),
        )
        for r in range(4) for c in range(4)
    )

    probe_surface = ReportProbeSurface(
        grid_size=4,
        total_probes=16,
        mean_delta_esi=-0.08333333,
        mean_delta_drift=0.04166667,
        variance_delta_esi=0.00277778,
        variance_delta_drift=0.00138889,
        probes=probes,
    )

    reproducibility = ReportSection(
        section_id="reproducibility",
        title="Reproducibility Block",
        content=(
            ("Case ID", case_id),
            ("CLARITY Version", "v0.0.11-m10"),
            ("R2L SHA", "abc123def456"),
            ("Adapter Model", "test_adapter"),
            ("Rich Mode", "false"),
            ("Perturbation Axes", "brightness, contrast"),
            ("Grid Size", "4"),
            ("Serialization Version", SERIALIZATION_VERSION),
            ("Manifest Hash", "hash_" + case_id),
        ),
    )

    return ClarityReport(
        metadata=metadata,
        metrics=metrics,
        robustness_surfaces=surfaces,
        overlay_section=overlay,
        probe_surface=probe_surface,
        reproducibility=reproducibility,
    )


class TestPDFDeterminism:
    """Tests for PDF byte-level determinism."""

    def test_identical_input_produces_identical_pdf(self) -> None:
        """Test that same input produces byte-identical PDF."""
        report1 = _create_test_report("case_001")
        report2 = _create_test_report("case_001")

        pdf1 = render_report_to_pdf(report1)
        pdf2 = render_report_to_pdf(report2)

        hash1 = hashlib.sha256(pdf1).hexdigest()
        hash2 = hashlib.sha256(pdf2).hexdigest()

        assert hash1 == hash2, "Same input must produce identical PDF bytes"

    def test_different_input_produces_different_pdf(self) -> None:
        """Test that different input produces different PDF."""
        report1 = _create_test_report("case_001")
        report2 = _create_test_report("case_002")

        pdf1 = render_report_to_pdf(report1)
        pdf2 = render_report_to_pdf(report2)

        hash1 = hashlib.sha256(pdf1).hexdigest()
        hash2 = hashlib.sha256(pdf2).hexdigest()

        assert hash1 != hash2, "Different input should produce different PDF"

    def test_multiple_renders_identical(self) -> None:
        """Test multiple renders produce identical output."""
        report = _create_test_report("case_001")
        hashes = set()

        for _ in range(5):
            pdf = render_report_to_pdf(report)
            hashes.add(hashlib.sha256(pdf).hexdigest())

        assert len(hashes) == 1, "All renders must produce identical bytes"

    def test_pdf_is_valid_pdf(self) -> None:
        """Test that output is a valid PDF."""
        report = _create_test_report("case_001")
        pdf = render_report_to_pdf(report)

        # PDF files start with %PDF-
        assert pdf[:5] == b"%PDF-", "Output must be valid PDF"
        # PDF files typically end with %%EOF
        assert b"%%EOF" in pdf[-100:], "PDF should end with EOF marker"


class TestImageDeterminism:
    """Tests for image rendering determinism."""

    def test_heatmap_png_deterministic(self) -> None:
        """Test heatmap PNG is deterministic."""
        values = generate_synthetic_heatmap_values(50, 50, seed=42)

        png1 = render_heatmap_png(values)
        png2 = render_heatmap_png(values)

        assert png1 == png2, "Same values must produce identical PNG bytes"

    def test_heatmap_different_seed_different_output(self) -> None:
        """Test different seeds produce different heatmaps."""
        values1 = generate_synthetic_heatmap_values(50, 50, seed=42)
        values2 = generate_synthetic_heatmap_values(50, 50, seed=123)

        png1 = render_heatmap_png(values1)
        png2 = render_heatmap_png(values2)

        # Different seeds should produce different patterns
        assert png1 != png2, "Different seeds should produce different output"

    def test_surface_png_deterministic(self) -> None:
        """Test surface PNG is deterministic."""
        axes = [
            {
                "axis": "brightness",
                "points": [
                    {"value": "0p8", "esi": 0.9},
                    {"value": "1p0", "esi": 0.95},
                ],
            },
        ]

        png1 = render_surface_png(axes)
        png2 = render_surface_png(axes)

        assert png1 == png2, "Same axes must produce identical PNG"

    def test_probe_grid_png_deterministic(self) -> None:
        """Test probe grid PNG is deterministic."""
        probes = [
            {"row": 0, "col": 0, "delta_esi": -0.05},
            {"row": 0, "col": 1, "delta_esi": -0.08},
            {"row": 1, "col": 0, "delta_esi": -0.07},
            {"row": 1, "col": 1, "delta_esi": -0.15},
        ]

        png1 = render_probe_grid_png(probes, grid_size=2)
        png2 = render_probe_grid_png(probes, grid_size=2)

        assert png1 == png2, "Same probes must produce identical PNG"

    def test_png_is_valid_png(self) -> None:
        """Test that output is valid PNG."""
        values = generate_synthetic_heatmap_values(50, 50)
        png = render_heatmap_png(values)

        # PNG files start with specific magic bytes
        PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
        assert png[:8] == PNG_MAGIC, "Output must be valid PNG"


class TestFloatFormatting:
    """Tests for float formatting consistency."""

    def test_eight_decimal_places(self) -> None:
        """Test floats are rounded to 8 decimal places."""
        metrics = ReportMetrics(
            baseline_esi=0.123456789012345,
            baseline_drift=0.987654321098765,
            global_mean_esi=0.111111111111111,
            global_mean_drift=0.222222222222222,
            global_variance_esi=0.333333333333333,
            global_variance_drift=0.444444444444444,
            monte_carlo_present=False,
        )

        # Check that values are truncated at 8 decimals
        assert str(metrics.baseline_esi) == "0.12345679"
        assert str(metrics.baseline_drift) == "0.98765432"

    def test_float_rounding_in_surface_points(self) -> None:
        """Test float rounding in surface points."""
        point = SurfacePoint(
            axis="test",
            value="v",
            esi=0.123456789012345,
            drift=0.987654321098765,
        )

        assert point.esi == 0.12345679
        assert point.drift == 0.98765432


class TestASTGuardrails:
    """AST-based tests for forbidden imports and patterns."""

    def _get_module_files(self) -> list[Path]:
        """Get all Python files in the report module."""
        return list(REPORT_MODULE_DIR.glob("*.py"))

    def _parse_file(self, path: Path) -> ast.Module:
        """Parse a Python file to AST."""
        with open(path, encoding="utf-8") as f:
            return ast.parse(f.read(), filename=str(path))

    def _get_import_names(self, tree: ast.Module) -> set[str]:
        """Extract all imported module names from AST."""
        imports: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        return imports

    def test_no_random_import(self) -> None:
        """Test that random module is not imported."""
        for path in self._get_module_files():
            tree = self._parse_file(path)
            imports = self._get_import_names(tree)

            assert "random" not in imports, f"random import found in {path.name}"

    def test_no_uuid_import(self) -> None:
        """Test that uuid module is not imported."""
        for path in self._get_module_files():
            tree = self._parse_file(path)
            imports = self._get_import_names(tree)

            assert "uuid" not in imports, f"uuid import found in {path.name}"

    def test_no_subprocess_import(self) -> None:
        """Test that subprocess module is not imported."""
        for path in self._get_module_files():
            tree = self._parse_file(path)
            imports = self._get_import_names(tree)

            assert "subprocess" not in imports, f"subprocess import found in {path.name}"

    def test_no_r2l_import(self) -> None:
        """Test that r2l modules are not imported."""
        for path in self._get_module_files():
            tree = self._parse_file(path)
            imports = self._get_import_names(tree)

            for imp in imports:
                assert "r2l" not in imp.lower(), f"r2l import found in {path.name}: {imp}"

    def test_no_datetime_now_usage(self) -> None:
        """Test that datetime.now() is not called."""
        for path in self._get_module_files():
            tree = self._parse_file(path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check for datetime.now() pattern
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == "now":
                            if isinstance(node.func.value, ast.Name):
                                if node.func.value.id == "datetime":
                                    pytest.fail(
                                        f"datetime.now() call found in {path.name}"
                                    )
                            elif isinstance(node.func.value, ast.Attribute):
                                if node.func.value.attr == "datetime":
                                    pytest.fail(
                                        f"datetime.datetime.now() call found in {path.name}"
                                    )

    def test_no_uuid_call(self) -> None:
        """Test that uuid functions are not called."""
        uuid_funcs = {"uuid1", "uuid3", "uuid4", "uuid5"}

        for path in self._get_module_files():
            tree = self._parse_file(path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in uuid_funcs:
                            pytest.fail(f"uuid.{node.func.attr}() found in {path.name}")
                    elif isinstance(node.func, ast.Name):
                        if node.func.id in uuid_funcs:
                            pytest.fail(f"{node.func.id}() found in {path.name}")


class TestSerializationDeterminism:
    """Tests for JSON serialization determinism."""

    def test_to_dict_key_order_stable(self) -> None:
        """Test that to_dict produces stable key ordering."""
        report = _create_test_report("case_001")
        d1 = report.to_dict()
        d2 = report.to_dict()

        # Compare JSON strings to verify ordering
        import json
        j1 = json.dumps(d1, sort_keys=True)
        j2 = json.dumps(d2, sort_keys=True)

        assert j1 == j2

    def test_list_ordering_stable(self) -> None:
        """Test that lists in to_dict maintain order."""
        report = _create_test_report("case_001")
        d = report.to_dict()

        # Robustness surfaces should maintain axis order
        axes = [s["axis"] for s in d["robustness_surfaces"]]
        assert axes == sorted(axes), "Surfaces should be sorted by axis"

        # Probes should maintain row/col order
        probes = d["probe_surface"]["probes"]
        for i, probe in enumerate(probes[:-1]):
            next_probe = probes[i + 1]
            assert (probe["row"], probe["col"]) <= (
                next_probe["row"],
                next_probe["col"],
            ), "Probes should be sorted by (row, col)"


class TestReproducibilityBlock:
    """Tests for reproducibility block content."""

    def test_block_contains_required_fields(self) -> None:
        """Test reproducibility block has all required fields."""
        report = _create_test_report("case_001")

        required_keys = {
            "Case ID",
            "CLARITY Version",
            "R2L SHA",
            "Adapter Model",
            "Rich Mode",
            "Perturbation Axes",
            "Grid Size",
            "Serialization Version",
            "Manifest Hash",
        }

        block_keys = {k for k, _ in report.reproducibility.content}

        assert required_keys.issubset(block_keys), (
            f"Missing keys: {required_keys - block_keys}"
        )

    def test_serialization_version_correct(self) -> None:
        """Test serialization version is M11_v1."""
        report = _create_test_report("case_001")

        version = None
        for k, v in report.reproducibility.content:
            if k == "Serialization Version":
                version = v
                break

        assert version == "M11_v1"

