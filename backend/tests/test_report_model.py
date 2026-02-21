"""Tests for CLARITY Report Data Models.

This module tests the frozen dataclasses in report_model.py.

Test coverage:
- Dataclass immutability
- Float rounding to 8 decimal places
- to_dict serialization
- Alphabetical key ordering
- Edge cases and validation
"""

from __future__ import annotations

import pytest

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


class TestReportMetadata:
    """Tests for ReportMetadata dataclass."""

    def test_create_basic(self) -> None:
        """Test basic metadata creation."""
        metadata = ReportMetadata(
            case_id="case_001",
            title="Test Report",
            generated_at="2026-02-20T00:00:00Z",
            clarity_version="v0.0.11-m10",
            r2l_sha="abc123",
            adapter_id="test_adapter",
            rich_mode=False,
            sweep_manifest_hash="hash123",
        )

        assert metadata.case_id == "case_001"
        assert metadata.title == "Test Report"
        assert metadata.serialization_version == SERIALIZATION_VERSION

    def test_frozen(self) -> None:
        """Test that metadata is immutable."""
        metadata = ReportMetadata(
            case_id="case_001",
            title="Test",
            generated_at="2026-01-01T00:00:00Z",
            clarity_version="v1",
            r2l_sha="sha",
            adapter_id="adapter",
            rich_mode=True,
            sweep_manifest_hash="hash",
        )

        with pytest.raises(AttributeError):
            metadata.case_id = "new_id"  # type: ignore[misc]

    def test_to_dict_keys_sorted(self) -> None:
        """Test that to_dict returns alphabetically sorted keys."""
        metadata = ReportMetadata(
            case_id="case_001",
            title="Test",
            generated_at="2026-01-01T00:00:00Z",
            clarity_version="v1",
            r2l_sha="sha",
            adapter_id="adapter",
            rich_mode=True,
            sweep_manifest_hash="hash",
        )

        d = metadata.to_dict()
        keys = list(d.keys())
        assert keys == sorted(keys)


class TestReportMetrics:
    """Tests for ReportMetrics dataclass."""

    def test_float_rounding(self) -> None:
        """Test that floats are rounded to 8 decimal places."""
        metrics = ReportMetrics(
            baseline_esi=0.123456789012345,
            baseline_drift=0.987654321098765,
            global_mean_esi=0.5,
            global_mean_drift=0.1,
            global_variance_esi=0.001,
            global_variance_drift=0.002,
            monte_carlo_present=False,
        )

        assert metrics.baseline_esi == 0.12345679
        assert metrics.baseline_drift == 0.98765432

    def test_monte_carlo_optional(self) -> None:
        """Test Monte Carlo fields are optional."""
        metrics = ReportMetrics(
            baseline_esi=0.9,
            baseline_drift=0.1,
            global_mean_esi=0.8,
            global_mean_drift=0.2,
            global_variance_esi=0.01,
            global_variance_drift=0.02,
            monte_carlo_present=True,
            monte_carlo_entropy=0.5,
        )

        assert metrics.monte_carlo_present is True
        assert metrics.monte_carlo_entropy == 0.5

    def test_to_dict_without_monte_carlo(self) -> None:
        """Test to_dict excludes None monte_carlo_entropy."""
        metrics = ReportMetrics(
            baseline_esi=0.9,
            baseline_drift=0.1,
            global_mean_esi=0.8,
            global_mean_drift=0.2,
            global_variance_esi=0.01,
            global_variance_drift=0.02,
            monte_carlo_present=False,
        )

        d = metrics.to_dict()
        assert "monte_carlo_entropy" not in d

    def test_to_dict_with_monte_carlo(self) -> None:
        """Test to_dict includes monte_carlo_entropy when present."""
        metrics = ReportMetrics(
            baseline_esi=0.9,
            baseline_drift=0.1,
            global_mean_esi=0.8,
            global_mean_drift=0.2,
            global_variance_esi=0.01,
            global_variance_drift=0.02,
            monte_carlo_present=True,
            monte_carlo_entropy=0.75,
        )

        d = metrics.to_dict()
        assert "monte_carlo_entropy" in d
        assert d["monte_carlo_entropy"] == 0.75


class TestSurfacePoint:
    """Tests for SurfacePoint dataclass."""

    def test_create_and_round(self) -> None:
        """Test creation and float rounding."""
        point = SurfacePoint(
            axis="brightness",
            value="1p0",
            esi=0.912345678901234,
            drift=0.087654321098765,
        )

        assert point.axis == "brightness"
        assert point.value == "1p0"
        assert point.esi == 0.91234568
        assert point.drift == 0.08765432

    def test_to_dict_keys_sorted(self) -> None:
        """Test to_dict key ordering."""
        point = SurfacePoint(axis="a", value="v", esi=0.5, drift=0.1)
        d = point.to_dict()
        keys = list(d.keys())
        assert keys == sorted(keys)


class TestReportRobustnessSurface:
    """Tests for ReportRobustnessSurface dataclass."""

    def test_create_with_points(self) -> None:
        """Test creation with multiple points."""
        points = (
            SurfacePoint(axis="brightness", value="0p8", esi=0.9, drift=0.1),
            SurfacePoint(axis="brightness", value="1p0", esi=0.95, drift=0.05),
        )

        surface = ReportRobustnessSurface(
            axis="brightness",
            mean_esi=0.925,
            mean_drift=0.075,
            variance_esi=0.001,
            variance_drift=0.002,
            points=points,
        )

        assert surface.axis == "brightness"
        assert len(surface.points) == 2
        assert surface.mean_esi == 0.925

    def test_frozen(self) -> None:
        """Test immutability."""
        surface = ReportRobustnessSurface(
            axis="test",
            mean_esi=0.5,
            mean_drift=0.5,
            variance_esi=0.1,
            variance_drift=0.1,
            points=(),
        )

        with pytest.raises(AttributeError):
            surface.axis = "new"  # type: ignore[misc]


class TestOverlayRegion:
    """Tests for OverlayRegion dataclass."""

    def test_create_and_round(self) -> None:
        """Test creation and float rounding."""
        region = OverlayRegion(
            region_id="evidence_r0",
            x_min=0.25,
            y_min=0.25,
            x_max=0.75,
            y_max=0.75,
            area=0.25,
            mean_evidence=0.82345678901234,
        )

        assert region.region_id == "evidence_r0"
        assert region.mean_evidence == 0.82345679

    def test_to_dict(self) -> None:
        """Test to_dict serialization."""
        region = OverlayRegion(
            region_id="r1",
            x_min=0.1,
            y_min=0.2,
            x_max=0.3,
            y_max=0.4,
            area=0.04,
            mean_evidence=0.5,
        )

        d = region.to_dict()
        assert d["region_id"] == "r1"
        assert d["area"] == 0.04


class TestReportOverlaySection:
    """Tests for ReportOverlaySection dataclass."""

    def test_create_with_regions(self) -> None:
        """Test creation with regions."""
        regions = (
            OverlayRegion(
                region_id="r0",
                x_min=0.1, y_min=0.1, x_max=0.5, y_max=0.5,
                area=0.16, mean_evidence=0.8,
            ),
        )

        section = ReportOverlaySection(
            image_width=224,
            image_height=224,
            regions=regions,
            total_evidence_area=0.16,
        )

        assert section.image_width == 224
        assert len(section.regions) == 1
        assert section.total_evidence_area == 0.16


class TestProbeResult:
    """Tests for ProbeResult dataclass."""

    def test_create_and_round(self) -> None:
        """Test creation and float rounding."""
        probe = ProbeResult(
            row=1,
            col=2,
            delta_esi=-0.05123456789,
            delta_drift=0.02567890123,
            masked_esi=0.89876543210,
            masked_drift=0.07654321098,
        )

        assert probe.row == 1
        assert probe.col == 2
        assert probe.delta_esi == -0.05123457
        assert probe.masked_esi == 0.89876543


class TestReportProbeSurface:
    """Tests for ReportProbeSurface dataclass."""

    def test_create_with_probes(self) -> None:
        """Test creation with probe results."""
        probes = tuple(
            ProbeResult(row=r, col=c, delta_esi=-0.05, delta_drift=0.02,
                       masked_esi=0.9, masked_drift=0.07)
            for r in range(2) for c in range(2)
        )

        surface = ReportProbeSurface(
            grid_size=2,
            total_probes=4,
            mean_delta_esi=-0.05,
            mean_delta_drift=0.02,
            variance_delta_esi=0.001,
            variance_delta_drift=0.001,
            probes=probes,
        )

        assert surface.grid_size == 2
        assert len(surface.probes) == 4


class TestReportSection:
    """Tests for ReportSection dataclass."""

    def test_create(self) -> None:
        """Test basic creation."""
        section = ReportSection(
            section_id="reproducibility",
            title="Reproducibility Block",
            content=(
                ("Key1", "Value1"),
                ("Key2", "Value2"),
            ),
        )

        assert section.section_id == "reproducibility"
        assert len(section.content) == 2

    def test_to_dict(self) -> None:
        """Test to_dict conversion."""
        section = ReportSection(
            section_id="test",
            title="Test Section",
            content=(("A", "1"), ("B", "2")),
        )

        d = section.to_dict()
        assert d["content"]["A"] == "1"
        assert d["content"]["B"] == "2"


class TestClarityReport:
    """Tests for ClarityReport dataclass."""

    def _create_minimal_report(self) -> ClarityReport:
        """Create a minimal report for testing."""
        metadata = ReportMetadata(
            case_id="test",
            title="Test",
            generated_at="2026-01-01T00:00:00Z",
            clarity_version="v1",
            r2l_sha="sha",
            adapter_id="adapter",
            rich_mode=False,
            sweep_manifest_hash="hash",
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
                mean_esi=0.83,
                mean_drift=0.125,
                variance_esi=0.009,
                variance_drift=0.001,
                points=(
                    SurfacePoint(axis="brightness", value="1p0", esi=0.95, drift=0.08),
                ),
            ),
        )

        overlay = ReportOverlaySection(
            image_width=224,
            image_height=224,
            regions=(),
            total_evidence_area=0.0,
        )

        probe_surface = ReportProbeSurface(
            grid_size=2,
            total_probes=4,
            mean_delta_esi=-0.05,
            mean_delta_drift=0.025,
            variance_delta_esi=0.003,
            variance_delta_drift=0.001,
            probes=(
                ProbeResult(row=0, col=0, delta_esi=-0.05, delta_drift=0.025,
                           masked_esi=0.9, masked_drift=0.075),
            ),
        )

        reproducibility = ReportSection(
            section_id="reproducibility",
            title="Reproducibility Block",
            content=(
                ("Case ID", "test"),
                ("Serialization Version", SERIALIZATION_VERSION),
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

    def test_create(self) -> None:
        """Test report creation."""
        report = self._create_minimal_report()
        assert report.metadata.case_id == "test"
        assert len(report.robustness_surfaces) == 1

    def test_to_dict(self) -> None:
        """Test full to_dict serialization."""
        report = self._create_minimal_report()
        d = report.to_dict()

        assert "metadata" in d
        assert "metrics" in d
        assert "robustness_surfaces" in d
        assert "overlay_section" in d
        assert "probe_surface" in d
        assert "reproducibility" in d

    def test_to_dict_deterministic(self) -> None:
        """Test that to_dict produces identical output for same input."""
        report1 = self._create_minimal_report()
        report2 = self._create_minimal_report()

        d1 = report1.to_dict()
        d2 = report2.to_dict()

        assert d1 == d2

    def test_frozen(self) -> None:
        """Test report immutability."""
        report = self._create_minimal_report()

        with pytest.raises(AttributeError):
            report.metadata = None  # type: ignore[misc]


class TestSerializationVersion:
    """Tests for serialization version constant."""

    def test_version_format(self) -> None:
        """Test version is M11_v1 format."""
        assert SERIALIZATION_VERSION == "M11_v1"

    def test_version_in_metadata(self) -> None:
        """Test version appears in metadata."""
        metadata = ReportMetadata(
            case_id="test",
            title="Test",
            generated_at="2026-01-01T00:00:00Z",
            clarity_version="v1",
            r2l_sha="sha",
            adapter_id="adapter",
            rich_mode=False,
            sweep_manifest_hash="hash",
        )

        assert metadata.serialization_version == "M11_v1"

