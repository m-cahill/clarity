"""Tests for Surface Engine (M06).

This test module provides comprehensive coverage for robustness surface
computation including:

1. Surface Construction (single/multiple axes, single/multi-value)
2. Statistical Correctness (known datasets, variance, asymmetric distributions)
3. Determinism (compute twice → identical results)
4. Rounding (8-decimal enforcement)
5. Guardrails (no numpy, subprocess, r2l, random, datetime, uuid)
6. Error Handling (empty input, missing values, NaN/inf)
7. to_dict() Serialization (deterministic, sorted keys)

Target: 50-70 tests minimum.
"""

from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest

from app.clarity.metrics import DriftMetric, ESIMetric, MetricsResult
from app.clarity.surface_engine import SurfaceEngine
from app.clarity.surfaces import (
    AxisSurface,
    RobustnessSurface,
    SurfaceComputationError,
    SurfacePoint,
    _round8,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def engine() -> SurfaceEngine:
    """Create a SurfaceEngine instance."""
    return SurfaceEngine()


def make_metrics(
    axes_data: dict[str, dict[str, tuple[float, float]]]
) -> MetricsResult:
    """Helper to create MetricsResult from simplified data.

    Args:
        axes_data: Dict mapping axis name to dict of value -> (esi, drift).

    Returns:
        MetricsResult with ESI and Drift metrics.
    """
    esi_metrics = []
    drift_metrics = []

    for axis_name in sorted(axes_data.keys()):
        values = axes_data[axis_name]
        esi_scores = {v: scores[0] for v, scores in values.items()}
        drift_scores = {v: scores[1] for v, scores in values.items()}

        # Compute overall as mean of value scores
        if esi_scores:
            overall_esi = sum(esi_scores.values()) / len(esi_scores)
            overall_drift = sum(drift_scores.values()) / len(drift_scores)
        else:
            overall_esi = 0.0
            overall_drift = 0.0

        esi_metrics.append(
            ESIMetric(
                axis=axis_name,
                value_scores=esi_scores,
                overall_score=round(overall_esi, 8),
            )
        )
        drift_metrics.append(
            DriftMetric(
                axis=axis_name,
                value_scores=drift_scores,
                overall_score=round(overall_drift, 8),
            )
        )

    return MetricsResult(esi=tuple(esi_metrics), drift=tuple(drift_metrics))


# =============================================================================
# 1. Surface Construction Tests
# =============================================================================


class TestSurfaceConstruction:
    """Tests for basic surface construction."""

    def test_single_axis_single_value(self, engine: SurfaceEngine) -> None:
        """Test surface with one axis and one value."""
        metrics = make_metrics({
            "brightness": {"1p0": (1.0, 0.0)},
        })

        surface = engine.compute(metrics)

        assert len(surface.axes) == 1
        assert surface.axes[0].axis == "brightness"
        assert len(surface.axes[0].points) == 1
        assert surface.axes[0].points[0].value == "1p0"
        assert surface.axes[0].points[0].esi == 1.0
        assert surface.axes[0].points[0].drift == 0.0

    def test_single_axis_multiple_values(self, engine: SurfaceEngine) -> None:
        """Test surface with one axis and multiple values."""
        metrics = make_metrics({
            "brightness": {
                "0p8": (0.5, 0.2),
                "1p0": (1.0, 0.0),
                "1p2": (0.75, 0.1),
            },
        })

        surface = engine.compute(metrics)

        assert len(surface.axes) == 1
        assert len(surface.axes[0].points) == 3
        # Values should be in lexicographic order
        assert surface.axes[0].points[0].value == "0p8"
        assert surface.axes[0].points[1].value == "1p0"
        assert surface.axes[0].points[2].value == "1p2"

    def test_multiple_axes_single_value_each(self, engine: SurfaceEngine) -> None:
        """Test surface with multiple axes, one value each."""
        metrics = make_metrics({
            "brightness": {"1p0": (1.0, 0.0)},
            "contrast": {"1p0": (0.8, 0.05)},
        })

        surface = engine.compute(metrics)

        assert len(surface.axes) == 2
        # Axes should be in alphabetical order
        assert surface.axes[0].axis == "brightness"
        assert surface.axes[1].axis == "contrast"

    def test_multiple_axes_multiple_values(self, engine: SurfaceEngine) -> None:
        """Test surface with multiple axes and multiple values."""
        metrics = make_metrics({
            "brightness": {
                "0p8": (0.6, 0.15),
                "1p0": (1.0, 0.0),
            },
            "contrast": {
                "0p9": (0.8, 0.1),
                "1p1": (0.9, 0.05),
            },
        })

        surface = engine.compute(metrics)

        assert len(surface.axes) == 2
        assert len(surface.axes[0].points) == 2
        assert len(surface.axes[1].points) == 2

    def test_axis_alphabetical_ordering(self, engine: SurfaceEngine) -> None:
        """Test that axes are ordered alphabetically."""
        metrics = make_metrics({
            "zoom": {"1p0": (0.9, 0.05)},
            "alpha": {"1p0": (0.8, 0.1)},
            "beta": {"1p0": (0.7, 0.15)},
        })

        surface = engine.compute(metrics)

        assert [a.axis for a in surface.axes] == ["alpha", "beta", "zoom"]

    def test_value_lexicographic_ordering(self, engine: SurfaceEngine) -> None:
        """Test that values are ordered lexicographically."""
        metrics = make_metrics({
            "brightness": {
                "1p2": (0.75, 0.1),
                "0p8": (0.5, 0.2),
                "1p0": (1.0, 0.0),
            },
        })

        surface = engine.compute(metrics)

        values = [p.value for p in surface.axes[0].points]
        assert values == ["0p8", "1p0", "1p2"]


# =============================================================================
# 2. Statistical Correctness Tests
# =============================================================================


class TestStatisticalCorrectness:
    """Tests for statistical calculations (mean, variance)."""

    def test_mean_calculation_simple(self, engine: SurfaceEngine) -> None:
        """Test mean calculation with simple values."""
        # ESI: [0.2, 0.4, 0.6] -> mean = 0.4
        # Drift: [0.1, 0.2, 0.3] -> mean = 0.2
        metrics = make_metrics({
            "brightness": {
                "a": (0.2, 0.1),
                "b": (0.4, 0.2),
                "c": (0.6, 0.3),
            },
        })

        surface = engine.compute(metrics)

        assert surface.axes[0].mean_esi == 0.4
        assert surface.axes[0].mean_drift == 0.2

    def test_variance_calculation_simple(self, engine: SurfaceEngine) -> None:
        """Test population variance calculation."""
        # ESI: [0.2, 0.4, 0.6] -> mean = 0.4
        # Variance = ((0.2-0.4)^2 + (0.4-0.4)^2 + (0.6-0.4)^2) / 3
        #          = (0.04 + 0 + 0.04) / 3 = 0.08 / 3 = 0.02666667
        metrics = make_metrics({
            "brightness": {
                "a": (0.2, 0.1),
                "b": (0.4, 0.2),
                "c": (0.6, 0.3),
            },
        })

        surface = engine.compute(metrics)

        expected_variance = (0.04 + 0 + 0.04) / 3
        assert surface.axes[0].variance_esi == _round8(expected_variance)

    def test_variance_zero_when_all_values_equal(self, engine: SurfaceEngine) -> None:
        """Test variance is 0.0 when all values are equal."""
        metrics = make_metrics({
            "brightness": {
                "a": (0.5, 0.1),
                "b": (0.5, 0.1),
                "c": (0.5, 0.1),
            },
        })

        surface = engine.compute(metrics)

        assert surface.axes[0].variance_esi == 0.0
        assert surface.axes[0].variance_drift == 0.0

    def test_single_value_variance_is_zero(self, engine: SurfaceEngine) -> None:
        """Test variance is 0.0 for single-value axis."""
        metrics = make_metrics({
            "brightness": {"single": (0.75, 0.25)},
        })

        surface = engine.compute(metrics)

        assert surface.axes[0].variance_esi == 0.0
        assert surface.axes[0].variance_drift == 0.0
        assert surface.axes[0].mean_esi == 0.75
        assert surface.axes[0].mean_drift == 0.25

    def test_asymmetric_distribution(self, engine: SurfaceEngine) -> None:
        """Test with asymmetric distribution."""
        # ESI: [0.1, 0.1, 0.1, 0.9] -> mean = 0.3
        metrics = make_metrics({
            "brightness": {
                "a": (0.1, 0.0),
                "b": (0.1, 0.0),
                "c": (0.1, 0.0),
                "d": (0.9, 0.0),
            },
        })

        surface = engine.compute(metrics)

        expected_mean = (0.1 + 0.1 + 0.1 + 0.9) / 4
        assert surface.axes[0].mean_esi == _round8(expected_mean)

        # Variance = sum((x - 0.3)^2) / 4
        # = ((0.1-0.3)^2 * 3 + (0.9-0.3)^2) / 4
        # = (0.04 * 3 + 0.36) / 4 = (0.12 + 0.36) / 4 = 0.48 / 4 = 0.12
        expected_variance = 0.12
        assert surface.axes[0].variance_esi == _round8(expected_variance)

    def test_global_mean_across_axes(self, engine: SurfaceEngine) -> None:
        """Test global mean computation across all axes."""
        # Axis 1: [0.2, 0.4] -> mean = 0.3
        # Axis 2: [0.6, 0.8] -> mean = 0.7
        # Global mean of all 4 points: (0.2+0.4+0.6+0.8)/4 = 0.5
        metrics = make_metrics({
            "alpha": {
                "a": (0.2, 0.1),
                "b": (0.4, 0.2),
            },
            "beta": {
                "a": (0.6, 0.3),
                "b": (0.8, 0.4),
            },
        })

        surface = engine.compute(metrics)

        assert surface.global_mean_esi == 0.5
        assert surface.global_mean_drift == 0.25

    def test_global_variance_across_axes(self, engine: SurfaceEngine) -> None:
        """Test global variance computation across all axes."""
        # All points: [0.2, 0.4, 0.6, 0.8] -> mean = 0.5
        # Variance = sum((x-0.5)^2) / 4
        # = (0.09 + 0.01 + 0.01 + 0.09) / 4 = 0.2 / 4 = 0.05
        metrics = make_metrics({
            "alpha": {
                "a": (0.2, 0.1),
                "b": (0.4, 0.2),
            },
            "beta": {
                "a": (0.6, 0.3),
                "b": (0.8, 0.4),
            },
        })

        surface = engine.compute(metrics)

        expected_variance = 0.05
        assert surface.global_variance_esi == _round8(expected_variance)

    def test_known_dataset_brightness_contrast(self, engine: SurfaceEngine) -> None:
        """Test with documented known dataset for exact verification."""
        # brightness: 0p8=0.25, 1p0=1.0 -> mean = 0.625
        # contrast: 0p9=0.5, 1p1=0.75 -> mean = 0.625
        # Global: [0.25, 1.0, 0.5, 0.75] -> mean = 0.625
        metrics = make_metrics({
            "brightness": {
                "0p8": (0.25, 0.3),
                "1p0": (1.0, 0.0),
            },
            "contrast": {
                "0p9": (0.5, 0.2),
                "1p1": (0.75, 0.1),
            },
        })

        surface = engine.compute(metrics)

        # Per-axis means
        assert surface.axes[0].mean_esi == _round8((0.25 + 1.0) / 2)  # 0.625
        assert surface.axes[1].mean_esi == _round8((0.5 + 0.75) / 2)  # 0.625

        # Global mean
        assert surface.global_mean_esi == _round8((0.25 + 1.0 + 0.5 + 0.75) / 4)

    def test_variance_with_extreme_values(self, engine: SurfaceEngine) -> None:
        """Test variance with extreme values (0 and 1)."""
        metrics = make_metrics({
            "brightness": {
                "a": (0.0, 0.0),
                "b": (1.0, 1.0),
            },
        })

        surface = engine.compute(metrics)

        # Mean = 0.5, Variance = (0.25 + 0.25) / 2 = 0.25
        assert surface.axes[0].mean_esi == 0.5
        assert surface.axes[0].variance_esi == 0.25


# =============================================================================
# 3. Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_compute_twice_identical(self, engine: SurfaceEngine) -> None:
        """Test that computing twice produces identical results."""
        metrics = make_metrics({
            "brightness": {
                "0p8": (0.5, 0.2),
                "1p0": (1.0, 0.0),
            },
            "contrast": {
                "0p9": (0.75, 0.1),
                "1p1": (0.8, 0.05),
            },
        })

        surface1 = engine.compute(metrics)
        surface2 = engine.compute(metrics)

        assert surface1 == surface2

    def test_same_input_different_engines(self) -> None:
        """Test that different engine instances produce identical results."""
        metrics = make_metrics({
            "brightness": {"1p0": (0.9, 0.05)},
        })

        engine1 = SurfaceEngine()
        engine2 = SurfaceEngine()

        surface1 = engine1.compute(metrics)
        surface2 = engine2.compute(metrics)

        assert surface1 == surface2

    def test_ordering_independent_of_input_order(self, engine: SurfaceEngine) -> None:
        """Test that output ordering is deterministic regardless of input order."""
        # Create metrics with different input orderings
        esi1 = (
            ESIMetric(axis="beta", value_scores={"x": 0.5}, overall_score=0.5),
            ESIMetric(axis="alpha", value_scores={"x": 0.6}, overall_score=0.6),
        )
        drift1 = (
            DriftMetric(axis="beta", value_scores={"x": 0.1}, overall_score=0.1),
            DriftMetric(axis="alpha", value_scores={"x": 0.2}, overall_score=0.2),
        )
        metrics1 = MetricsResult(esi=esi1, drift=drift1)

        esi2 = (
            ESIMetric(axis="alpha", value_scores={"x": 0.6}, overall_score=0.6),
            ESIMetric(axis="beta", value_scores={"x": 0.5}, overall_score=0.5),
        )
        drift2 = (
            DriftMetric(axis="alpha", value_scores={"x": 0.2}, overall_score=0.2),
            DriftMetric(axis="beta", value_scores={"x": 0.1}, overall_score=0.1),
        )
        metrics2 = MetricsResult(esi=esi2, drift=drift2)

        surface1 = engine.compute(metrics1)
        surface2 = engine.compute(metrics2)

        # Both should have alpha first (alphabetical)
        assert surface1.axes[0].axis == "alpha"
        assert surface2.axes[0].axis == "alpha"
        assert surface1 == surface2


# =============================================================================
# 4. Rounding Tests
# =============================================================================


class TestRounding:
    """Tests for 8-decimal rounding enforcement."""

    def test_round8_function(self) -> None:
        """Test _round8 helper function."""
        assert _round8(0.123456789) == 0.12345679
        assert _round8(0.333333333333) == 0.33333333
        assert _round8(1.0) == 1.0
        assert _round8(0.0) == 0.0

    def test_surface_point_values_rounded(self, engine: SurfaceEngine) -> None:
        """Test that SurfacePoint values are rounded."""
        metrics = make_metrics({
            "brightness": {"a": (0.123456789, 0.987654321)},
        })

        surface = engine.compute(metrics)

        assert surface.axes[0].points[0].esi == 0.12345679
        assert surface.axes[0].points[0].drift == 0.98765432

    def test_axis_mean_rounded(self, engine: SurfaceEngine) -> None:
        """Test that axis mean is rounded to 8 decimals."""
        # 1/3 = 0.333333...
        metrics = make_metrics({
            "brightness": {
                "a": (0.0, 0.0),
                "b": (0.5, 0.0),
                "c": (0.5, 0.0),
            },
        })

        surface = engine.compute(metrics)

        # Mean = 1.0 / 3 = 0.33333333...
        expected = _round8(1.0 / 3)
        assert surface.axes[0].mean_esi == expected

    def test_variance_rounded(self, engine: SurfaceEngine) -> None:
        """Test that variance is rounded to 8 decimals."""
        metrics = make_metrics({
            "brightness": {
                "a": (0.0, 0.0),
                "b": (1.0, 0.0),
                "c": (0.5, 0.0),
            },
        })

        surface = engine.compute(metrics)

        # Mean = 0.5
        # Variance = (0.25 + 0.25 + 0) / 3 = 0.16666666...
        expected = _round8(0.5 / 3)
        assert surface.axes[0].variance_esi == expected

    def test_global_statistics_rounded(self, engine: SurfaceEngine) -> None:
        """Test that global statistics are rounded."""
        metrics = make_metrics({
            "brightness": {
                "a": (0.33333333, 0.16666667),
            },
        })

        surface = engine.compute(metrics)

        # Values should maintain 8-decimal precision
        assert surface.global_mean_esi == 0.33333333
        assert surface.global_mean_drift == 0.16666667


# =============================================================================
# 5. Guardrails Tests (AST-based)
# =============================================================================


class TestGuardrails:
    """AST-based tests ensuring forbidden imports are absent."""

    @pytest.fixture
    def surfaces_source(self) -> str:
        """Load surfaces.py source code."""
        path = Path(__file__).parent.parent / "app" / "clarity" / "surfaces.py"
        return path.read_text(encoding="utf-8")

    @pytest.fixture
    def engine_source(self) -> str:
        """Load surface_engine.py source code."""
        path = Path(__file__).parent.parent / "app" / "clarity" / "surface_engine.py"
        return path.read_text(encoding="utf-8")

    def _get_imports(self, source: str) -> set[str]:
        """Extract all imported module names from source."""
        tree = ast.parse(source)
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        return imports

    def test_surfaces_no_numpy(self, surfaces_source: str) -> None:
        """Verify surfaces.py does not import numpy."""
        imports = self._get_imports(surfaces_source)
        assert "numpy" not in imports, "surfaces.py must not import numpy"

    def test_surfaces_no_subprocess(self, surfaces_source: str) -> None:
        """Verify surfaces.py does not import subprocess."""
        imports = self._get_imports(surfaces_source)
        assert "subprocess" not in imports, "surfaces.py must not import subprocess"

    def test_surfaces_no_random(self, surfaces_source: str) -> None:
        """Verify surfaces.py does not import random."""
        imports = self._get_imports(surfaces_source)
        assert "random" not in imports, "surfaces.py must not import random"

    def test_surfaces_no_datetime(self, surfaces_source: str) -> None:
        """Verify surfaces.py does not import datetime."""
        imports = self._get_imports(surfaces_source)
        assert "datetime" not in imports, "surfaces.py must not import datetime"

    def test_surfaces_no_uuid(self, surfaces_source: str) -> None:
        """Verify surfaces.py does not import uuid."""
        imports = self._get_imports(surfaces_source)
        assert "uuid" not in imports, "surfaces.py must not import uuid"

    def test_surfaces_no_r2l(self, surfaces_source: str) -> None:
        """Verify surfaces.py does not import r2l modules."""
        imports = self._get_imports(surfaces_source)
        r2l_imports = [i for i in imports if "r2l" in i.lower()]
        assert not r2l_imports, f"surfaces.py must not import r2l: {r2l_imports}"

    def test_engine_no_numpy(self, engine_source: str) -> None:
        """Verify surface_engine.py does not import numpy."""
        imports = self._get_imports(engine_source)
        assert "numpy" not in imports, "surface_engine.py must not import numpy"

    def test_engine_no_subprocess(self, engine_source: str) -> None:
        """Verify surface_engine.py does not import subprocess."""
        imports = self._get_imports(engine_source)
        assert "subprocess" not in imports

    def test_engine_no_random(self, engine_source: str) -> None:
        """Verify surface_engine.py does not import random."""
        imports = self._get_imports(engine_source)
        assert "random" not in imports

    def test_engine_no_datetime(self, engine_source: str) -> None:
        """Verify surface_engine.py does not import datetime."""
        imports = self._get_imports(engine_source)
        assert "datetime" not in imports

    def test_engine_no_uuid(self, engine_source: str) -> None:
        """Verify surface_engine.py does not import uuid."""
        imports = self._get_imports(engine_source)
        assert "uuid" not in imports

    def test_engine_no_r2l(self, engine_source: str) -> None:
        """Verify surface_engine.py does not import r2l modules."""
        imports = self._get_imports(engine_source)
        r2l_imports = [i for i in imports if "r2l" in i.lower()]
        assert not r2l_imports


# =============================================================================
# 6. Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_empty_esi_raises(self, engine: SurfaceEngine) -> None:
        """Test that empty ESI raises SurfaceComputationError."""
        metrics = MetricsResult(
            esi=(),
            drift=(DriftMetric(axis="a", value_scores={"x": 0.1}, overall_score=0.1),),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "no axes" in str(exc_info.value).lower()

    def test_empty_drift_raises(self, engine: SurfaceEngine) -> None:
        """Test that empty Drift raises SurfaceComputationError."""
        metrics = MetricsResult(
            esi=(ESIMetric(axis="a", value_scores={"x": 0.5}, overall_score=0.5),),
            drift=(),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "no axes" in str(exc_info.value).lower()

    def test_axis_mismatch_esi_only(self, engine: SurfaceEngine) -> None:
        """Test error when axis exists only in ESI."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(axis="a", value_scores={"x": 0.5}, overall_score=0.5),
                ESIMetric(axis="b", value_scores={"x": 0.6}, overall_score=0.6),
            ),
            drift=(
                DriftMetric(axis="a", value_scores={"x": 0.1}, overall_score=0.1),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "mismatch" in str(exc_info.value).lower()
        assert "b" in str(exc_info.value)

    def test_axis_mismatch_drift_only(self, engine: SurfaceEngine) -> None:
        """Test error when axis exists only in Drift."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(axis="a", value_scores={"x": 0.5}, overall_score=0.5),
            ),
            drift=(
                DriftMetric(axis="a", value_scores={"x": 0.1}, overall_score=0.1),
                DriftMetric(axis="c", value_scores={"x": 0.2}, overall_score=0.2),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "mismatch" in str(exc_info.value).lower()
        assert "c" in str(exc_info.value)

    def test_value_mismatch_esi_only(self, engine: SurfaceEngine) -> None:
        """Test error when value exists only in ESI for an axis."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(
                    axis="a",
                    value_scores={"x": 0.5, "y": 0.6},
                    overall_score=0.55,
                ),
            ),
            drift=(
                DriftMetric(
                    axis="a",
                    value_scores={"x": 0.1},
                    overall_score=0.1,
                ),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "value mismatch" in str(exc_info.value).lower()
        assert "y" in str(exc_info.value)

    def test_value_mismatch_drift_only(self, engine: SurfaceEngine) -> None:
        """Test error when value exists only in Drift for an axis."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(
                    axis="a",
                    value_scores={"x": 0.5},
                    overall_score=0.5,
                ),
            ),
            drift=(
                DriftMetric(
                    axis="a",
                    value_scores={"x": 0.1, "z": 0.2},
                    overall_score=0.15,
                ),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "value mismatch" in str(exc_info.value).lower()
        assert "z" in str(exc_info.value)

    def test_nan_esi_raises(self, engine: SurfaceEngine) -> None:
        """Test that NaN in ESI raises SurfaceComputationError."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(
                    axis="a",
                    value_scores={"x": float("nan")},
                    overall_score=0.5,
                ),
            ),
            drift=(
                DriftMetric(
                    axis="a",
                    value_scores={"x": 0.1},
                    overall_score=0.1,
                ),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "invalid" in str(exc_info.value).lower()

    def test_inf_esi_raises(self, engine: SurfaceEngine) -> None:
        """Test that inf in ESI raises SurfaceComputationError."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(
                    axis="a",
                    value_scores={"x": float("inf")},
                    overall_score=0.5,
                ),
            ),
            drift=(
                DriftMetric(
                    axis="a",
                    value_scores={"x": 0.1},
                    overall_score=0.1,
                ),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "invalid" in str(exc_info.value).lower()

    def test_negative_inf_drift_raises(self, engine: SurfaceEngine) -> None:
        """Test that -inf in Drift raises SurfaceComputationError."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(
                    axis="a",
                    value_scores={"x": 0.5},
                    overall_score=0.5,
                ),
            ),
            drift=(
                DriftMetric(
                    axis="a",
                    value_scores={"x": float("-inf")},
                    overall_score=0.1,
                ),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "invalid" in str(exc_info.value).lower()

    def test_nan_drift_raises(self, engine: SurfaceEngine) -> None:
        """Test that NaN in Drift raises SurfaceComputationError."""
        metrics = MetricsResult(
            esi=(
                ESIMetric(
                    axis="a",
                    value_scores={"x": 0.5},
                    overall_score=0.5,
                ),
            ),
            drift=(
                DriftMetric(
                    axis="a",
                    value_scores={"x": float("nan")},
                    overall_score=0.1,
                ),
            ),
        )

        with pytest.raises(SurfaceComputationError) as exc_info:
            engine.compute(metrics)

        assert "invalid" in str(exc_info.value).lower()


# =============================================================================
# 7. to_dict() Serialization Tests
# =============================================================================


class TestToDict:
    """Tests for to_dict() serialization."""

    def test_surface_point_to_dict(self) -> None:
        """Test SurfacePoint.to_dict() returns correct structure."""
        point = SurfacePoint(axis="brightness", value="0p8", esi=0.5, drift=0.2)

        result = point.to_dict()

        assert result == {
            "axis": "brightness",
            "drift": 0.2,
            "esi": 0.5,
            "value": "0p8",
        }

    def test_surface_point_to_dict_sorted_keys(self) -> None:
        """Test SurfacePoint.to_dict() has alphabetically sorted keys."""
        point = SurfacePoint(axis="a", value="v", esi=0.1, drift=0.2)

        result = point.to_dict()

        assert list(result.keys()) == ["axis", "drift", "esi", "value"]

    def test_axis_surface_to_dict(self) -> None:
        """Test AxisSurface.to_dict() returns correct structure."""
        point = SurfacePoint(axis="brightness", value="1p0", esi=1.0, drift=0.0)
        surface = AxisSurface(
            axis="brightness",
            points=(point,),
            mean_esi=1.0,
            mean_drift=0.0,
            variance_esi=0.0,
            variance_drift=0.0,
        )

        result = surface.to_dict()

        assert result["axis"] == "brightness"
        assert result["mean_esi"] == 1.0
        assert result["mean_drift"] == 0.0
        assert result["variance_esi"] == 0.0
        assert result["variance_drift"] == 0.0
        assert len(result["points"]) == 1
        assert result["points"][0]["value"] == "1p0"

    def test_axis_surface_to_dict_sorted_keys(self) -> None:
        """Test AxisSurface.to_dict() has alphabetically sorted keys."""
        point = SurfacePoint(axis="a", value="v", esi=0.1, drift=0.2)
        surface = AxisSurface(
            axis="a",
            points=(point,),
            mean_esi=0.1,
            mean_drift=0.2,
            variance_esi=0.0,
            variance_drift=0.0,
        )

        result = surface.to_dict()

        expected_keys = [
            "axis",
            "mean_drift",
            "mean_esi",
            "points",
            "variance_drift",
            "variance_esi",
        ]
        assert list(result.keys()) == expected_keys

    def test_robustness_surface_to_dict(self, engine: SurfaceEngine) -> None:
        """Test RobustnessSurface.to_dict() returns correct structure."""
        metrics = make_metrics({
            "brightness": {"1p0": (1.0, 0.0)},
        })

        surface = engine.compute(metrics)
        result = surface.to_dict()

        assert "axes" in result
        assert "global_mean_esi" in result
        assert "global_mean_drift" in result
        assert "global_variance_esi" in result
        assert "global_variance_drift" in result
        assert len(result["axes"]) == 1

    def test_robustness_surface_to_dict_sorted_keys(
        self, engine: SurfaceEngine
    ) -> None:
        """Test RobustnessSurface.to_dict() has alphabetically sorted keys."""
        metrics = make_metrics({"a": {"x": (0.5, 0.1)}})

        surface = engine.compute(metrics)
        result = surface.to_dict()

        expected_keys = [
            "axes",
            "global_mean_drift",
            "global_mean_esi",
            "global_variance_drift",
            "global_variance_esi",
        ]
        assert list(result.keys()) == expected_keys

    def test_to_dict_deterministic(self, engine: SurfaceEngine) -> None:
        """Test that to_dict() produces identical output on repeated calls."""
        metrics = make_metrics({
            "brightness": {"0p8": (0.5, 0.2), "1p0": (1.0, 0.0)},
            "contrast": {"0p9": (0.75, 0.1)},
        })

        surface = engine.compute(metrics)

        dict1 = surface.to_dict()
        dict2 = surface.to_dict()

        assert dict1 == dict2

    def test_to_dict_preserves_point_order(self, engine: SurfaceEngine) -> None:
        """Test that to_dict() preserves lexicographic point order."""
        metrics = make_metrics({
            "brightness": {
                "c": (0.3, 0.3),
                "a": (0.1, 0.1),
                "b": (0.2, 0.2),
            },
        })

        surface = engine.compute(metrics)
        result = surface.to_dict()

        values = [p["value"] for p in result["axes"][0]["points"]]
        assert values == ["a", "b", "c"]


# =============================================================================
# 8. Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for complete surface computation."""

    def test_full_surface_computation(self, engine: SurfaceEngine) -> None:
        """Test complete surface computation with multiple axes."""
        metrics = make_metrics({
            "brightness": {
                "0p8": (0.6, 0.15),
                "1p0": (1.0, 0.0),
                "1p2": (0.8, 0.05),
            },
            "contrast": {
                "0p9": (0.7, 0.12),
                "1p1": (0.9, 0.03),
            },
        })

        surface = engine.compute(metrics)

        # Verify structure
        assert isinstance(surface, RobustnessSurface)
        assert len(surface.axes) == 2

        # Verify axis ordering
        assert surface.axes[0].axis == "brightness"
        assert surface.axes[1].axis == "contrast"

        # Verify point counts
        assert len(surface.axes[0].points) == 3
        assert len(surface.axes[1].points) == 2

        # Verify all statistics are computed
        assert math.isfinite(surface.global_mean_esi)
        assert math.isfinite(surface.global_mean_drift)
        assert math.isfinite(surface.global_variance_esi)
        assert math.isfinite(surface.global_variance_drift)

    def test_surface_immutability(self, engine: SurfaceEngine) -> None:
        """Test that all surface components are immutable (frozen)."""
        metrics = make_metrics({
            "brightness": {"1p0": (1.0, 0.0)},
        })

        surface = engine.compute(metrics)

        # Verify frozen dataclass behavior
        with pytest.raises(AttributeError):
            surface.global_mean_esi = 0.5  # type: ignore

        with pytest.raises(AttributeError):
            surface.axes[0].mean_esi = 0.5  # type: ignore

        with pytest.raises(AttributeError):
            surface.axes[0].points[0].esi = 0.5  # type: ignore

    def test_large_surface_computation(self, engine: SurfaceEngine) -> None:
        """Test surface computation with many axes and values."""
        # Create 10 axes with 10 values each = 100 points
        axes_data: dict[str, dict[str, tuple[float, float]]] = {}

        for i in range(10):
            axis_name = f"axis_{i:02d}"
            values: dict[str, tuple[float, float]] = {}
            for j in range(10):
                value_name = f"val_{j:02d}"
                esi = (i * 10 + j) / 100.0
                drift = (99 - i * 10 - j) / 100.0
                values[value_name] = (esi, drift)
            axes_data[axis_name] = values

        metrics = make_metrics(axes_data)
        surface = engine.compute(metrics)

        assert len(surface.axes) == 10
        for axis in surface.axes:
            assert len(axis.points) == 10

        # Verify determinism
        surface2 = engine.compute(metrics)
        assert surface == surface2


# =============================================================================
# 9. Dataclass Tests
# =============================================================================


class TestDataclasses:
    """Tests for dataclass properties and behavior."""

    def test_surface_point_equality(self) -> None:
        """Test SurfacePoint equality comparison."""
        p1 = SurfacePoint(axis="a", value="v", esi=0.5, drift=0.1)
        p2 = SurfacePoint(axis="a", value="v", esi=0.5, drift=0.1)
        p3 = SurfacePoint(axis="a", value="v", esi=0.6, drift=0.1)

        assert p1 == p2
        assert p1 != p3

    def test_surface_point_hashable(self) -> None:
        """Test that SurfacePoint is hashable (frozen)."""
        p1 = SurfacePoint(axis="a", value="v", esi=0.5, drift=0.1)
        p2 = SurfacePoint(axis="a", value="v", esi=0.5, drift=0.1)

        # Should be usable in sets
        points = {p1, p2}
        assert len(points) == 1

    def test_axis_surface_hashable(self) -> None:
        """Test that AxisSurface is hashable (frozen)."""
        point = SurfacePoint(axis="a", value="v", esi=0.5, drift=0.1)
        surface = AxisSurface(
            axis="a",
            points=(point,),
            mean_esi=0.5,
            mean_drift=0.1,
            variance_esi=0.0,
            variance_drift=0.0,
        )

        # Should be usable in sets
        surfaces = {surface}
        assert len(surfaces) == 1

    def test_robustness_surface_hashable(self, engine: SurfaceEngine) -> None:
        """Test that RobustnessSurface is hashable (frozen)."""
        metrics = make_metrics({"a": {"x": (0.5, 0.1)}})

        surface = engine.compute(metrics)

        # Should be usable in sets
        surfaces = {surface}
        assert len(surfaces) == 1

    def test_surface_computation_error_message(self) -> None:
        """Test SurfaceComputationError has correct message."""
        error = SurfaceComputationError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

