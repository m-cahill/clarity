"""Surfaces Module for CLARITY.

This module provides data structures for representing robustness surfaces
computed from M05 metrics output. Surfaces aggregate ESI and Drift metrics
into analyzable structures suitable for gradient estimation and visualization.

CRITICAL CONSTRAINTS (M06):
1. All structures must be deterministic given identical input.
2. No randomness, no datetime.now, no uuid.
3. No numpy — pure Python only.
4. No r2l imports.
5. No subprocess.
6. All floats rounded to 8 decimal places at storage.
7. Frozen dataclasses only.
8. Deterministic to_dict() with sorted keys.

Structures defined:
- SurfacePoint: Single axis value point with ESI and Drift.
- AxisSurface: Aggregated surface for one axis with mean/variance.
- RobustnessSurface: Full surface across all axes with global statistics.
- SurfaceComputationError: Raised when surface computation fails.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class SurfaceComputationError(Exception):
    """Raised when surface computation fails.

    This error indicates a failure during surface computation, such as:
    - Empty MetricsResult (no axes)
    - Axis mismatch between ESI and Drift
    - Value mismatch within an axis
    - NaN or inf values in input metrics
    """

    pass


def _round8(value: float) -> float:
    """Round a value to 8 decimal places.

    Args:
        value: The float value to round.

    Returns:
        The value rounded to 8 decimal places.
    """
    return round(value, 8)


@dataclass(frozen=True)
class SurfacePoint:
    """Single point on a robustness surface.

    Represents the ESI and Drift metrics for a single axis value.

    Attributes:
        axis: The name of the perturbation axis.
        value: The encoded axis value (string).
        esi: Evidence Stability Index for this value.
        drift: Justification Drift for this value.

    Example:
        >>> point = SurfacePoint(
        ...     axis="brightness",
        ...     value="0p8",
        ...     esi=0.66666667,
        ...     drift=0.15,
        ... )
    """

    axis: str
    value: str
    esi: float
    drift: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with axis, drift, esi, value keys (alphabetical).
        """
        return {
            "axis": self.axis,
            "drift": self.drift,
            "esi": self.esi,
            "value": self.value,
        }


@dataclass(frozen=True)
class AxisSurface:
    """Robustness surface for a single perturbation axis.

    Aggregates all value points for one axis with computed mean and variance
    statistics for both ESI and Drift.

    Attributes:
        axis: The name of the perturbation axis.
        points: Tuple of SurfacePoint objects, ordered lexicographically by value.
        mean_esi: Mean ESI across all values (population mean).
        mean_drift: Mean Drift across all values (population mean).
        variance_esi: Variance of ESI across values (population variance).
        variance_drift: Variance of Drift across values (population variance).

    Example:
        >>> surface = AxisSurface(
        ...     axis="brightness",
        ...     points=(point1, point2),
        ...     mean_esi=0.83333333,
        ...     mean_drift=0.075,
        ...     variance_esi=0.02777778,
        ...     variance_drift=0.005625,
        ... )
    """

    axis: str
    points: tuple[SurfacePoint, ...]
    mean_esi: float
    mean_drift: float
    variance_esi: float
    variance_drift: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.
        Points are serialized in their natural (lexicographic) order.

        Returns:
            Dictionary with axis, mean_drift, mean_esi, points,
            variance_drift, variance_esi keys (alphabetical).
        """
        return {
            "axis": self.axis,
            "mean_drift": self.mean_drift,
            "mean_esi": self.mean_esi,
            "points": [p.to_dict() for p in self.points],
            "variance_drift": self.variance_drift,
            "variance_esi": self.variance_esi,
        }


@dataclass(frozen=True)
class RobustnessSurface:
    """Complete robustness surface across all perturbation axes.

    Aggregates all axis surfaces with global mean and variance statistics
    computed across all points.

    Attributes:
        axes: Tuple of AxisSurface objects, ordered alphabetically by axis name.
        global_mean_esi: Mean ESI across all points (population mean).
        global_mean_drift: Mean Drift across all points (population mean).
        global_variance_esi: Variance of ESI across all points (population variance).
        global_variance_drift: Variance of Drift across all points (population variance).

    Example:
        >>> surface = RobustnessSurface(
        ...     axes=(axis_surface1, axis_surface2),
        ...     global_mean_esi=0.75,
        ...     global_mean_drift=0.125,
        ...     global_variance_esi=0.0625,
        ...     global_variance_drift=0.015625,
        ... )
    """

    axes: tuple[AxisSurface, ...]
    global_mean_esi: float
    global_mean_drift: float
    global_variance_esi: float
    global_variance_drift: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.
        Axes are serialized in their natural (alphabetical) order.

        Returns:
            Dictionary with axes, global_mean_drift, global_mean_esi,
            global_variance_drift, global_variance_esi keys (alphabetical).
        """
        return {
            "axes": [a.to_dict() for a in self.axes],
            "global_mean_drift": self.global_mean_drift,
            "global_mean_esi": self.global_mean_esi,
            "global_variance_drift": self.global_variance_drift,
            "global_variance_esi": self.global_variance_esi,
        }

