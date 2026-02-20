"""Tests for Gradient Engine (M07).

This test module provides comprehensive coverage for gradient estimation
and stability metrics computation including:

1. Basic Gradient Correctness (linear, constant, monotonic)
2. Endpoint Behavior (two-point, single-value)
3. Statistical Aggregation (mean/max verification)
4. Determinism (compute twice, different engines, input ordering)
5. Error Handling (empty surface, NaN/inf)
6. Rounding (8-decimal enforcement)
7. Guardrails (no numpy, subprocess, r2l, random, datetime, uuid)
8. to_dict() Serialization (deterministic, sorted keys)
9. Integration (INT-001: real sweep → metrics → surface → gradient)

Target: 45-60 tests minimum.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path
from typing import Any

import pytest

from app.clarity.gradient_engine import (
    AxisGradient,
    GradientComputationError,
    GradientEngine,
    GradientPoint,
    GradientSurface,
    _round8,
)
from app.clarity.metrics import DriftMetric, ESIMetric, MetricsResult
from app.clarity.surface_engine import SurfaceEngine
from app.clarity.surfaces import (
    AxisSurface,
    RobustnessSurface,
    SurfacePoint,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def engine() -> GradientEngine:
    """Create a GradientEngine instance."""
    return GradientEngine()


@pytest.fixture
def surface_engine() -> SurfaceEngine:
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


def make_surface(
    axes_data: dict[str, dict[str, tuple[float, float]]]
) -> RobustnessSurface:
    """Helper to create RobustnessSurface from simplified data.

    Args:
        axes_data: Dict mapping axis name to dict of value -> (esi, drift).

    Returns:
        RobustnessSurface via SurfaceEngine.
    """
    metrics = make_metrics(axes_data)
    engine = SurfaceEngine()
    return engine.compute(metrics)


# =============================================================================
# 1. Basic Gradient Correctness Tests
# =============================================================================


class TestBasicGradientCorrectness:
    """Tests for basic gradient computation correctness."""

    def test_constant_surface_zero_gradient(self, engine: GradientEngine) -> None:
        """Constant ESI/Drift across values produces zero gradients."""
        surface = make_surface({
            "brightness": {
                "0p8": (0.5, 0.1),
                "1p0": (0.5, 0.1),
                "1p2": (0.5, 0.1),
            },
        })

        grad = engine.compute(surface)

        # All gradients should be zero
        for gp in grad.axes[0].gradients:
            assert gp.d_esi == 0.0
            assert gp.d_drift == 0.0

        # Statistics should be zero
        assert grad.axes[0].mean_abs_esi_gradient == 0.0
        assert grad.axes[0].max_abs_esi_gradient == 0.0

    def test_linear_esi_slope(self, engine: GradientEngine) -> None:
        """Linear ESI progression produces consistent gradients."""
        # ESI: 0.0, 0.5, 1.0 → linear slope of 0.5 per step
        surface = make_surface({
            "brightness": {
                "0p8": (0.0, 0.0),
                "1p0": (0.5, 0.0),
                "1p2": (1.0, 0.0),
            },
        })

        grad = engine.compute(surface)

        # First point (forward diff): 0.5 - 0.0 = 0.5
        assert grad.axes[0].gradients[0].d_esi == 0.5
        # Middle point (central diff): (1.0 - 0.0) / 2 = 0.5
        assert grad.axes[0].gradients[1].d_esi == 0.5
        # Last point (backward diff): 1.0 - 0.5 = 0.5
        assert grad.axes[0].gradients[2].d_esi == 0.5

    def test_linear_drift_slope(self, engine: GradientEngine) -> None:
        """Linear Drift progression produces consistent gradients."""
        # Drift: 0.0, 0.1, 0.2 → linear slope of 0.1 per step
        surface = make_surface({
            "brightness": {
                "0p8": (1.0, 0.0),
                "1p0": (1.0, 0.1),
                "1p2": (1.0, 0.2),
            },
        })

        grad = engine.compute(surface)

        # All points should have gradient of 0.1
        assert grad.axes[0].gradients[0].d_drift == 0.1
        assert grad.axes[0].gradients[1].d_drift == 0.1
        assert grad.axes[0].gradients[2].d_drift == 0.1

    def test_monotonic_increase(self, engine: GradientEngine) -> None:
        """Monotonically increasing ESI produces positive gradients."""
        surface = make_surface({
            "brightness": {
                "v1": (0.1, 0.0),
                "v2": (0.3, 0.0),
                "v3": (0.7, 0.0),
                "v4": (0.9, 0.0),
            },
        })

        grad = engine.compute(surface)

        # All ESI gradients should be positive
        for gp in grad.axes[0].gradients:
            assert gp.d_esi > 0.0

    def test_monotonic_decrease(self, engine: GradientEngine) -> None:
        """Monotonically decreasing ESI produces negative gradients."""
        surface = make_surface({
            "brightness": {
                "v1": (0.9, 0.0),
                "v2": (0.7, 0.0),
                "v3": (0.3, 0.0),
                "v4": (0.1, 0.0),
            },
        })

        grad = engine.compute(surface)

        # All ESI gradients should be negative
        for gp in grad.axes[0].gradients:
            assert gp.d_esi < 0.0

    def test_nonlinear_central_difference(self, engine: GradientEngine) -> None:
        """Non-linear surface uses central difference correctly."""
        # ESI: 0.0, 0.1, 0.4, 0.9 (quadratic-like)
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.1, 0.0),
                "v3": (0.4, 0.0),
                "v4": (0.9, 0.0),
            },
        })

        grad = engine.compute(surface)

        # First: forward diff = 0.1 - 0.0 = 0.1
        assert grad.axes[0].gradients[0].d_esi == 0.1
        # Second: central diff = (0.4 - 0.0) / 2 = 0.2
        assert grad.axes[0].gradients[1].d_esi == 0.2
        # Third: central diff = (0.9 - 0.1) / 2 = 0.4
        assert grad.axes[0].gradients[2].d_esi == 0.4
        # Fourth: backward diff = 0.9 - 0.4 = 0.5
        assert grad.axes[0].gradients[3].d_esi == 0.5


# =============================================================================
# 2. Endpoint Behavior Tests
# =============================================================================


class TestEndpointBehavior:
    """Tests for endpoint gradient computation."""

    def test_two_point_axis(self, engine: GradientEngine) -> None:
        """Two-point axis uses simple difference for both points."""
        surface = make_surface({
            "brightness": {
                "v1": (0.2, 0.1),
                "v2": (0.8, 0.3),
            },
        })

        grad = engine.compute(surface)

        # Both points should have same gradient (0.8 - 0.2 = 0.6, 0.3 - 0.1 = 0.2)
        assert grad.axes[0].gradients[0].d_esi == 0.6
        assert grad.axes[0].gradients[1].d_esi == 0.6
        assert grad.axes[0].gradients[0].d_drift == 0.2
        assert grad.axes[0].gradients[1].d_drift == 0.2

    def test_single_value_axis_zero_gradient(self, engine: GradientEngine) -> None:
        """Single-value axis produces zero gradient."""
        surface = make_surface({
            "brightness": {
                "1p0": (0.75, 0.15),
            },
        })

        grad = engine.compute(surface)

        assert len(grad.axes[0].gradients) == 1
        assert grad.axes[0].gradients[0].d_esi == 0.0
        assert grad.axes[0].gradients[0].d_drift == 0.0

    def test_single_value_statistics_are_zero(self, engine: GradientEngine) -> None:
        """Single-value axis produces zero statistics."""
        surface = make_surface({
            "brightness": {
                "1p0": (0.75, 0.15),
            },
        })

        grad = engine.compute(surface)

        assert grad.axes[0].mean_abs_esi_gradient == 0.0
        assert grad.axes[0].max_abs_esi_gradient == 0.0
        assert grad.axes[0].mean_abs_drift_gradient == 0.0
        assert grad.axes[0].max_abs_drift_gradient == 0.0

    def test_three_point_forward_backward(self, engine: GradientEngine) -> None:
        """Three-point axis: forward, central, backward."""
        # ESI: 0.0, 0.4, 1.0
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.4, 0.0),
                "v3": (1.0, 0.0),
            },
        })

        grad = engine.compute(surface)

        # First: forward = 0.4 - 0.0 = 0.4
        assert grad.axes[0].gradients[0].d_esi == 0.4
        # Second: central = (1.0 - 0.0) / 2 = 0.5
        assert grad.axes[0].gradients[1].d_esi == 0.5
        # Third: backward = 1.0 - 0.4 = 0.6
        assert grad.axes[0].gradients[2].d_esi == 0.6


# =============================================================================
# 3. Statistical Aggregation Tests
# =============================================================================


class TestStatisticalAggregation:
    """Tests for mean/max gradient statistics."""

    def test_mean_abs_esi_gradient(self, engine: GradientEngine) -> None:
        """Mean absolute ESI gradient computed correctly."""
        # Gradients will be: 0.5, 0.5, 0.5 (linear) → mean = 0.5
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.5, 0.0),
                "v3": (1.0, 0.0),
            },
        })

        grad = engine.compute(surface)

        assert grad.axes[0].mean_abs_esi_gradient == 0.5

    def test_max_abs_esi_gradient(self, engine: GradientEngine) -> None:
        """Max absolute ESI gradient computed correctly."""
        # ESI: 0.0, 0.1, 0.5, 1.0
        # Gradients: 0.1, (0.5-0.0)/2=0.25, (1.0-0.1)/2=0.45, 0.5
        # Max = 0.5
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.1, 0.0),
                "v3": (0.5, 0.0),
                "v4": (1.0, 0.0),
            },
        })

        grad = engine.compute(surface)

        assert grad.axes[0].max_abs_esi_gradient == 0.5

    def test_mean_abs_drift_gradient(self, engine: GradientEngine) -> None:
        """Mean absolute Drift gradient computed correctly."""
        # Drift: 0.0, 0.2, 0.4 → gradients all 0.2
        surface = make_surface({
            "brightness": {
                "v1": (1.0, 0.0),
                "v2": (1.0, 0.2),
                "v3": (1.0, 0.4),
            },
        })

        grad = engine.compute(surface)

        assert grad.axes[0].mean_abs_drift_gradient == 0.2

    def test_max_abs_drift_gradient(self, engine: GradientEngine) -> None:
        """Max absolute Drift gradient computed correctly."""
        # Drift: 0.0, 0.1, 0.5 → gradients: 0.1, 0.25, 0.4, max = 0.4
        surface = make_surface({
            "brightness": {
                "v1": (1.0, 0.0),
                "v2": (1.0, 0.1),
                "v3": (1.0, 0.5),
            },
        })

        grad = engine.compute(surface)

        # forward: 0.1, central: (0.5-0.0)/2=0.25, backward: 0.5-0.1=0.4
        assert grad.axes[0].max_abs_drift_gradient == 0.4

    def test_global_mean_across_axes(self, engine: GradientEngine) -> None:
        """Global mean computed across all axes."""
        # Axis 1: 3 points with gradients [0.5, 0.5, 0.5] → mean 0.5
        # Axis 2: 2 points with gradients [0.2, 0.2] → mean 0.2
        # Global mean = (0.5+0.5+0.5+0.2+0.2) / 5 = 1.9 / 5 = 0.38
        surface = make_surface({
            "alpha": {
                "v1": (0.0, 0.0),
                "v2": (0.5, 0.0),
                "v3": (1.0, 0.0),
            },
            "beta": {
                "v1": (0.0, 0.0),
                "v2": (0.2, 0.0),
            },
        })

        grad = engine.compute(surface)

        assert grad.global_mean_abs_esi_gradient == 0.38

    def test_global_max_across_axes(self, engine: GradientEngine) -> None:
        """Global max is maximum across all axes."""
        surface = make_surface({
            "alpha": {
                "v1": (0.0, 0.0),
                "v2": (0.3, 0.0),
            },
            "beta": {
                "v1": (0.0, 0.0),
                "v2": (0.9, 0.0),  # Larger gradient
            },
        })

        grad = engine.compute(surface)

        assert grad.global_max_abs_esi_gradient == 0.9


# =============================================================================
# 4. Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests for deterministic computation."""

    def test_compute_twice_identical(self, engine: GradientEngine) -> None:
        """Computing twice produces identical results."""
        surface = make_surface({
            "brightness": {
                "0p8": (0.2, 0.15),
                "1p0": (0.5, 0.1),
                "1p2": (0.9, 0.05),
            },
            "contrast": {
                "0p9": (0.3, 0.2),
                "1p1": (0.7, 0.1),
            },
        })

        grad1 = engine.compute(surface)
        grad2 = engine.compute(surface)

        assert grad1 == grad2

    def test_same_input_different_engines(self) -> None:
        """Different engine instances produce identical results."""
        surface = make_surface({
            "brightness": {
                "v1": (0.1, 0.2),
                "v2": (0.4, 0.15),
                "v3": (0.8, 0.05),
            },
        })

        engine1 = GradientEngine()
        engine2 = GradientEngine()

        grad1 = engine1.compute(surface)
        grad2 = engine2.compute(surface)

        assert grad1 == grad2

    def test_to_dict_deterministic(self, engine: GradientEngine) -> None:
        """to_dict() produces identical output repeatedly."""
        surface = make_surface({
            "brightness": {
                "v1": (0.3, 0.1),
                "v2": (0.6, 0.05),
            },
        })

        grad = engine.compute(surface)

        dict1 = grad.to_dict()
        dict2 = grad.to_dict()

        assert dict1 == dict2
        assert json.dumps(dict1, sort_keys=True) == json.dumps(dict2, sort_keys=True)


# =============================================================================
# 5. Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_empty_surface_raises(self, engine: GradientEngine) -> None:
        """Empty RobustnessSurface raises error."""
        empty_surface = RobustnessSurface(
            axes=(),
            global_mean_esi=0.0,
            global_mean_drift=0.0,
            global_variance_esi=0.0,
            global_variance_drift=0.0,
        )

        with pytest.raises(GradientComputationError, match="no axes"):
            engine.compute(empty_surface)

    def test_nan_esi_raises(self, engine: GradientEngine) -> None:
        """NaN in ESI raises error."""
        bad_surface = RobustnessSurface(
            axes=(
                AxisSurface(
                    axis="brightness",
                    points=(
                        SurfacePoint(
                            axis="brightness", value="1p0", esi=float("nan"), drift=0.1
                        ),
                    ),
                    mean_esi=float("nan"),
                    mean_drift=0.1,
                    variance_esi=0.0,
                    variance_drift=0.0,
                ),
            ),
            global_mean_esi=float("nan"),
            global_mean_drift=0.1,
            global_variance_esi=0.0,
            global_variance_drift=0.0,
        )

        with pytest.raises(GradientComputationError, match="Invalid ESI"):
            engine.compute(bad_surface)

    def test_inf_esi_raises(self, engine: GradientEngine) -> None:
        """Inf in ESI raises error."""
        bad_surface = RobustnessSurface(
            axes=(
                AxisSurface(
                    axis="brightness",
                    points=(
                        SurfacePoint(
                            axis="brightness", value="1p0", esi=float("inf"), drift=0.1
                        ),
                    ),
                    mean_esi=float("inf"),
                    mean_drift=0.1,
                    variance_esi=0.0,
                    variance_drift=0.0,
                ),
            ),
            global_mean_esi=float("inf"),
            global_mean_drift=0.1,
            global_variance_esi=0.0,
            global_variance_drift=0.0,
        )

        with pytest.raises(GradientComputationError, match="Invalid ESI"):
            engine.compute(bad_surface)

    def test_nan_drift_raises(self, engine: GradientEngine) -> None:
        """NaN in Drift raises error."""
        bad_surface = RobustnessSurface(
            axes=(
                AxisSurface(
                    axis="brightness",
                    points=(
                        SurfacePoint(
                            axis="brightness", value="1p0", esi=0.5, drift=float("nan")
                        ),
                    ),
                    mean_esi=0.5,
                    mean_drift=float("nan"),
                    variance_esi=0.0,
                    variance_drift=0.0,
                ),
            ),
            global_mean_esi=0.5,
            global_mean_drift=float("nan"),
            global_variance_esi=0.0,
            global_variance_drift=0.0,
        )

        with pytest.raises(GradientComputationError, match="Invalid Drift"):
            engine.compute(bad_surface)

    def test_negative_inf_drift_raises(self, engine: GradientEngine) -> None:
        """Negative inf in Drift raises error."""
        bad_surface = RobustnessSurface(
            axes=(
                AxisSurface(
                    axis="brightness",
                    points=(
                        SurfacePoint(
                            axis="brightness",
                            value="1p0",
                            esi=0.5,
                            drift=float("-inf"),
                        ),
                    ),
                    mean_esi=0.5,
                    mean_drift=float("-inf"),
                    variance_esi=0.0,
                    variance_drift=0.0,
                ),
            ),
            global_mean_esi=0.5,
            global_mean_drift=float("-inf"),
            global_variance_esi=0.0,
            global_variance_drift=0.0,
        )

        with pytest.raises(GradientComputationError, match="Invalid Drift"):
            engine.compute(bad_surface)


# =============================================================================
# 6. Rounding Tests
# =============================================================================


class TestRounding:
    """Tests for 8-decimal rounding."""

    def test_round8_function(self) -> None:
        """_round8 rounds to 8 decimals."""
        assert _round8(0.123456789) == 0.12345679
        assert _round8(0.123456781) == 0.12345678
        assert _round8(1.0) == 1.0

    def test_gradient_values_rounded(self, engine: GradientEngine) -> None:
        """Gradient values are rounded to 8 decimals."""
        # Create surface that produces non-round gradients
        # ESI: 0.0, 0.33333333..., 0.66666666...
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.33333333, 0.0),
                "v3": (0.66666666, 0.0),
            },
        })

        grad = engine.compute(surface)

        # All gradient values should be at most 8 decimal places
        for gp in grad.axes[0].gradients:
            s = str(gp.d_esi)
            if "." in s:
                decimals = len(s.split(".")[1])
                assert decimals <= 8

    def test_statistics_rounded(self, engine: GradientEngine) -> None:
        """Statistics are rounded to 8 decimals."""
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.33333333, 0.0),
                "v3": (0.66666666, 0.0),
            },
        })

        grad = engine.compute(surface)

        # Check axis-level stats
        stats = [
            grad.axes[0].mean_abs_esi_gradient,
            grad.axes[0].max_abs_esi_gradient,
        ]
        for stat in stats:
            s = str(stat)
            if "." in s:
                decimals = len(s.split(".")[1])
                assert decimals <= 8

    def test_global_statistics_rounded(self, engine: GradientEngine) -> None:
        """Global statistics are rounded to 8 decimals."""
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.33333333, 0.0),
                "v3": (0.66666666, 0.0),
            },
        })

        grad = engine.compute(surface)

        stats = [
            grad.global_mean_abs_esi_gradient,
            grad.global_max_abs_esi_gradient,
            grad.global_mean_abs_drift_gradient,
            grad.global_max_abs_drift_gradient,
        ]
        for stat in stats:
            s = str(stat)
            if "." in s:
                decimals = len(s.split(".")[1])
                assert decimals <= 8


# =============================================================================
# 7. Guardrails Tests (AST-based)
# =============================================================================


class TestGuardrails:
    """AST-based tests for forbidden imports."""

    @pytest.fixture
    def gradient_engine_source(self) -> str:
        """Load gradient_engine.py source code."""
        path = Path(__file__).parent.parent / "app" / "clarity" / "gradient_engine.py"
        return path.read_text(encoding="utf-8")

    def test_no_numpy_import(self, gradient_engine_source: str) -> None:
        """gradient_engine.py does not import numpy."""
        tree = ast.parse(gradient_engine_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "numpy" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "numpy" not in node.module

    def test_no_subprocess_import(self, gradient_engine_source: str) -> None:
        """gradient_engine.py does not import subprocess."""
        tree = ast.parse(gradient_engine_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "subprocess" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "subprocess" not in node.module

    def test_no_random_import(self, gradient_engine_source: str) -> None:
        """gradient_engine.py does not import random."""
        tree = ast.parse(gradient_engine_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "random"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module != "random"

    def test_no_datetime_import(self, gradient_engine_source: str) -> None:
        """gradient_engine.py does not import datetime."""
        tree = ast.parse(gradient_engine_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "datetime"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module != "datetime"

    def test_no_uuid_import(self, gradient_engine_source: str) -> None:
        """gradient_engine.py does not import uuid."""
        tree = ast.parse(gradient_engine_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "uuid"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module != "uuid"

    def test_no_r2l_import(self, gradient_engine_source: str) -> None:
        """gradient_engine.py does not import r2l."""
        tree = ast.parse(gradient_engine_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "r2l" not in alias.name.lower()
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "r2l" not in node.module.lower()


# =============================================================================
# 8. to_dict() Serialization Tests
# =============================================================================


class TestToDict:
    """Tests for to_dict() serialization."""

    def test_gradient_point_to_dict(self) -> None:
        """GradientPoint.to_dict() produces correct output."""
        gp = GradientPoint(axis="brightness", value="1p0", d_esi=0.5, d_drift=0.1)

        d = gp.to_dict()

        assert d == {
            "axis": "brightness",
            "d_drift": 0.1,
            "d_esi": 0.5,
            "value": "1p0",
        }

    def test_gradient_point_to_dict_sorted_keys(self) -> None:
        """GradientPoint.to_dict() has sorted keys."""
        gp = GradientPoint(axis="brightness", value="1p0", d_esi=0.5, d_drift=0.1)

        d = gp.to_dict()

        assert list(d.keys()) == sorted(d.keys())

    def test_axis_gradient_to_dict(self, engine: GradientEngine) -> None:
        """AxisGradient.to_dict() produces correct output."""
        surface = make_surface({
            "brightness": {
                "v1": (0.0, 0.0),
                "v2": (0.5, 0.0),
            },
        })

        grad = engine.compute(surface)
        d = grad.axes[0].to_dict()

        assert "axis" in d
        assert "gradients" in d
        assert isinstance(d["gradients"], list)
        assert "mean_abs_esi_gradient" in d
        assert "max_abs_esi_gradient" in d

    def test_axis_gradient_to_dict_sorted_keys(self, engine: GradientEngine) -> None:
        """AxisGradient.to_dict() has sorted keys."""
        surface = make_surface({
            "brightness": {"v1": (0.0, 0.0), "v2": (0.5, 0.0)},
        })

        grad = engine.compute(surface)
        d = grad.axes[0].to_dict()

        assert list(d.keys()) == sorted(d.keys())

    def test_gradient_surface_to_dict(self, engine: GradientEngine) -> None:
        """GradientSurface.to_dict() produces correct output."""
        surface = make_surface({
            "alpha": {"v1": (0.0, 0.0), "v2": (0.5, 0.1)},
            "beta": {"v1": (0.3, 0.2)},
        })

        grad = engine.compute(surface)
        d = grad.to_dict()

        assert "axes" in d
        assert isinstance(d["axes"], list)
        assert len(d["axes"]) == 2
        assert "global_mean_abs_esi_gradient" in d
        assert "global_max_abs_esi_gradient" in d

    def test_gradient_surface_to_dict_sorted_keys(
        self, engine: GradientEngine
    ) -> None:
        """GradientSurface.to_dict() has sorted keys."""
        surface = make_surface({
            "brightness": {"v1": (0.0, 0.0), "v2": (0.5, 0.0)},
        })

        grad = engine.compute(surface)
        d = grad.to_dict()

        assert list(d.keys()) == sorted(d.keys())

    def test_to_dict_json_serializable(self, engine: GradientEngine) -> None:
        """to_dict() output is JSON serializable."""
        surface = make_surface({
            "brightness": {
                "v1": (0.1, 0.2),
                "v2": (0.4, 0.15),
                "v3": (0.9, 0.05),
            },
        })

        grad = engine.compute(surface)
        d = grad.to_dict()

        # Should not raise
        json_str = json.dumps(d)
        assert json_str


# =============================================================================
# 9. Dataclass Tests
# =============================================================================


class TestDataclasses:
    """Tests for dataclass behavior."""

    def test_gradient_point_equality(self) -> None:
        """GradientPoint equality works."""
        gp1 = GradientPoint(axis="b", value="1p0", d_esi=0.5, d_drift=0.1)
        gp2 = GradientPoint(axis="b", value="1p0", d_esi=0.5, d_drift=0.1)
        gp3 = GradientPoint(axis="b", value="1p0", d_esi=0.6, d_drift=0.1)

        assert gp1 == gp2
        assert gp1 != gp3

    def test_gradient_point_hashable(self) -> None:
        """GradientPoint is hashable."""
        gp = GradientPoint(axis="b", value="1p0", d_esi=0.5, d_drift=0.1)

        # Should not raise
        h = hash(gp)
        assert isinstance(h, int)

    def test_gradient_point_frozen(self) -> None:
        """GradientPoint is immutable."""
        gp = GradientPoint(axis="b", value="1p0", d_esi=0.5, d_drift=0.1)

        with pytest.raises(AttributeError):
            gp.d_esi = 0.9  # type: ignore

    def test_axis_gradient_frozen(self) -> None:
        """AxisGradient is immutable."""
        ag = AxisGradient(
            axis="b",
            gradients=(),
            mean_abs_esi_gradient=0.0,
            max_abs_esi_gradient=0.0,
            mean_abs_drift_gradient=0.0,
            max_abs_drift_gradient=0.0,
        )

        with pytest.raises(AttributeError):
            ag.axis = "c"  # type: ignore

    def test_gradient_surface_frozen(self) -> None:
        """GradientSurface is immutable."""
        gs = GradientSurface(
            axes=(),
            global_mean_abs_esi_gradient=0.0,
            global_max_abs_esi_gradient=0.0,
            global_mean_abs_drift_gradient=0.0,
            global_max_abs_drift_gradient=0.0,
        )

        with pytest.raises(AttributeError):
            gs.axes = ()  # type: ignore


# =============================================================================
# 10. Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests including INT-001 closure."""

    def test_metrics_to_surface_to_gradient(self) -> None:
        """Full pipeline: MetricsResult → Surface → Gradient."""
        metrics = make_metrics({
            "brightness": {
                "0p8": (0.6, 0.2),
                "1p0": (1.0, 0.0),
                "1p2": (0.4, 0.3),
            },
            "contrast": {
                "0p9": (0.8, 0.1),
                "1p1": (0.7, 0.15),
            },
        })

        surface_engine = SurfaceEngine()
        gradient_engine = GradientEngine()

        surface = surface_engine.compute(metrics)
        grad = gradient_engine.compute(surface)

        # Verify structure
        assert len(grad.axes) == 2
        assert grad.axes[0].axis == "brightness"
        assert grad.axes[1].axis == "contrast"
        assert len(grad.axes[0].gradients) == 3
        assert len(grad.axes[1].gradients) == 2

    def test_integration_determinism(self) -> None:
        """Full pipeline is deterministic across two runs."""
        metrics = make_metrics({
            "brightness": {
                "0p8": (0.5, 0.15),
                "1p0": (0.8, 0.05),
                "1p2": (0.3, 0.25),
            },
        })

        # Run 1
        se1 = SurfaceEngine()
        ge1 = GradientEngine()
        surface1 = se1.compute(metrics)
        grad1 = ge1.compute(surface1)

        # Run 2
        se2 = SurfaceEngine()
        ge2 = GradientEngine()
        surface2 = se2.compute(metrics)
        grad2 = ge2.compute(surface2)

        assert grad1 == grad2

    def test_surface_immutability_preserved(self, engine: GradientEngine) -> None:
        """Gradient computation does not mutate surface."""
        surface = make_surface({
            "brightness": {
                "v1": (0.3, 0.1),
                "v2": (0.6, 0.05),
                "v3": (0.9, 0.0),
            },
        })

        # Capture original values
        original_esi = surface.axes[0].points[0].esi
        original_dict = surface.to_dict()

        # Compute gradient
        engine.compute(surface)

        # Verify surface unchanged
        assert surface.axes[0].points[0].esi == original_esi
        assert surface.to_dict() == original_dict

    def test_large_surface(self, engine: GradientEngine) -> None:
        """Gradient computation handles large surfaces."""
        # 5 axes, 10 values each
        axes_data = {}
        for i in range(5):
            axis_name = f"axis_{i:02d}"
            values = {}
            for j in range(10):
                value_key = f"v{j:02d}"
                esi = j / 10.0
                drift = (9 - j) / 20.0
                values[value_key] = (esi, drift)
            axes_data[axis_name] = values

        surface = make_surface(axes_data)
        grad = engine.compute(surface)

        # Verify structure
        assert len(grad.axes) == 5
        for axis_grad in grad.axes:
            assert len(axis_grad.gradients) == 10


# =============================================================================
# 11. INT-001 Closure: Real Sweep Integration Test
# =============================================================================


class TestINT001RealSweepIntegration:
    """INT-001 closure: real sweep → metrics → surface → gradient.

    This test creates a minimal deterministic sweep fixture and exercises
    the full pipeline through actual file loading.
    """

    @pytest.fixture
    def minimal_sweep_dir(self, tmp_path: Path) -> Path:
        """Create a minimal sweep fixture for INT-001.

        Structure:
        minimal_sweep/
        ├── sweep_manifest.json
        └── runs/
            ├── brightness=0p8_seed=42/
            │   └── trace_pack.jsonl
            └── brightness=1p0_seed=42/
                └── trace_pack.jsonl
        """
        sweep_dir = tmp_path / "minimal_sweep"
        sweep_dir.mkdir()

        # Create sweep_manifest.json
        manifest = {
            "sweep_id": "test-sweep-001",
            "axes": {
                "brightness": [0.8, 1.0],
            },
            "seeds": [42],
            "runs": [
                {"axis_values": {"brightness": 0.8}, "seed": 42},
                {"axis_values": {"brightness": 1.0}, "seed": 42},
            ],
        }
        (sweep_dir / "sweep_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

        # Create runs directory
        runs_dir = sweep_dir / "runs"
        runs_dir.mkdir()

        # Create run 1: brightness=0p8_seed=42
        run1_dir = runs_dir / "brightness=0p8_seed=42"
        run1_dir.mkdir()
        trace1 = {"step": 1, "output": "diagnosis_A", "justification": "Finding X"}
        (run1_dir / "trace_pack.jsonl").write_text(
            json.dumps(trace1), encoding="utf-8"
        )

        # Create run 2: brightness=1p0_seed=42
        run2_dir = runs_dir / "brightness=1p0_seed=42"
        run2_dir.mkdir()
        trace2 = {"step": 1, "output": "diagnosis_A", "justification": "Finding X"}
        (run2_dir / "trace_pack.jsonl").write_text(
            json.dumps(trace2), encoding="utf-8"
        )

        return sweep_dir

    def test_real_sweep_to_gradient_determinism(
        self, minimal_sweep_dir: Path
    ) -> None:
        """Full pipeline from real sweep is deterministic."""
        from app.clarity.metrics_engine import MetricsEngine

        # Run pipeline twice
        me = MetricsEngine()
        se = SurfaceEngine()
        ge = GradientEngine()

        # First run
        metrics1 = me.compute(minimal_sweep_dir)
        surface1 = se.compute(metrics1)
        grad1 = ge.compute(surface1)

        # Second run (fresh instances)
        me2 = MetricsEngine()
        se2 = SurfaceEngine()
        ge2 = GradientEngine()

        metrics2 = me2.compute(minimal_sweep_dir)
        surface2 = se2.compute(metrics2)
        grad2 = ge2.compute(surface2)

        # Assert determinism
        assert grad1 == grad2
        assert grad1.to_dict() == grad2.to_dict()

    def test_real_sweep_produces_valid_gradient(
        self, minimal_sweep_dir: Path
    ) -> None:
        """Real sweep produces valid gradient structure."""
        from app.clarity.metrics_engine import MetricsEngine

        me = MetricsEngine()
        se = SurfaceEngine()
        ge = GradientEngine()

        metrics = me.compute(minimal_sweep_dir)
        surface = se.compute(metrics)
        grad = ge.compute(surface)

        # Verify structure
        assert len(grad.axes) == 1
        assert grad.axes[0].axis == "brightness"
        assert len(grad.axes[0].gradients) == 2

        # Two-point axis: both gradients are same
        assert grad.axes[0].gradients[0].d_esi == grad.axes[0].gradients[1].d_esi

        # Global stats exist
        assert isinstance(grad.global_mean_abs_esi_gradient, float)
        assert isinstance(grad.global_max_abs_esi_gradient, float)


# =============================================================================
# Test Count Summary
# =============================================================================

# Category breakdown:
# 1. Basic Gradient Correctness: 6 tests
# 2. Endpoint Behavior: 4 tests
# 3. Statistical Aggregation: 6 tests
# 4. Determinism: 3 tests
# 5. Error Handling: 5 tests
# 6. Rounding: 4 tests
# 7. Guardrails (AST): 6 tests
# 8. to_dict() Serialization: 7 tests
# 9. Dataclasses: 5 tests
# 10. Integration: 4 tests
# 11. INT-001 Real Sweep: 2 tests
#
# Total: 52 tests

