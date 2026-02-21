"""Surfaces Module for CLARITY.

This module provides data structures for representing robustness surfaces
computed from M05 metrics output. Surfaces aggregate ESI and Drift metrics
into analyzable structures suitable for gradient estimation and visualization.

CRITICAL CONSTRAINTS (M06+M14):
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
- (M14) ConfidenceSurfacePoint: Single axis value point with confidence metrics.
- (M14) ConfidenceSurface: Aggregated confidence surface for one axis.
- (M14) EntropySurfacePoint: Single axis value point with entropy metrics.
- (M14) EntropySurface: Aggregated entropy surface for one axis.
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


# M14 Rich Mode Surfaces


@dataclass(frozen=True)
class ConfidenceSurfacePoint:
    """Single point on a confidence surface (M14).

    Represents confidence metrics for a single axis value.

    Attributes:
        axis: The name of the perturbation axis.
        value: The encoded axis value (string).
        mean_confidence: Mean confidence score across seeds.
        csi: Confidence Stability Index for this value.
        confidence_variance: Variance of confidence scores.

    Example:
        >>> point = ConfidenceSurfacePoint(
        ...     axis="brightness",
        ...     value="0p8",
        ...     mean_confidence=0.85,
        ...     csi=0.95,
        ...     confidence_variance=0.0025,
        ... )
    """

    axis: str
    value: str
    mean_confidence: float
    csi: float
    confidence_variance: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with alphabetically sorted keys.
        """
        return {
            "axis": self.axis,
            "confidence_variance": self.confidence_variance,
            "csi": self.csi,
            "mean_confidence": self.mean_confidence,
            "value": self.value,
        }


@dataclass(frozen=True)
class ConfidenceSurface:
    """Aggregated confidence surface for a single axis (M14).

    Attributes:
        axis: The name of the perturbation axis.
        points: Tuple of ConfidenceSurfacePoint objects.
        mean_csi: Mean CSI across all values.
        overall_mean_confidence: Mean confidence across all values.
        overall_variance: Variance of confidence across all values.

    Example:
        >>> surface = ConfidenceSurface(
        ...     axis="brightness",
        ...     points=(point1, point2),
        ...     mean_csi=0.95,
        ...     overall_mean_confidence=0.85,
        ...     overall_variance=0.0025,
        ... )
    """

    axis: str
    points: tuple[ConfidenceSurfacePoint, ...]
    mean_csi: float
    overall_mean_confidence: float
    overall_variance: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with alphabetically sorted keys.
        """
        return {
            "axis": self.axis,
            "mean_csi": self.mean_csi,
            "overall_mean_confidence": self.overall_mean_confidence,
            "overall_variance": self.overall_variance,
            "points": [p.to_dict() for p in self.points],
        }


@dataclass(frozen=True)
class EntropySurfacePoint:
    """Single point on an entropy surface (M14).

    Represents entropy metrics for a single axis value.

    Attributes:
        axis: The name of the perturbation axis.
        value: The encoded axis value (string).
        mean_entropy: Mean entropy across seeds.
        edm: Entropy Drift Metric for this value.
        entropy_variance: Variance of entropy scores.

    Example:
        >>> point = EntropySurfacePoint(
        ...     axis="brightness",
        ...     value="0p8",
        ...     mean_entropy=2.3,
        ...     edm=0.05,
        ...     entropy_variance=0.01,
        ... )
    """

    axis: str
    value: str
    mean_entropy: float
    edm: float
    entropy_variance: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with alphabetically sorted keys.
        """
        return {
            "axis": self.axis,
            "edm": self.edm,
            "entropy_variance": self.entropy_variance,
            "mean_entropy": self.mean_entropy,
            "value": self.value,
        }


@dataclass(frozen=True)
class EntropySurface:
    """Aggregated entropy surface for a single axis (M14).

    Attributes:
        axis: The name of the perturbation axis.
        points: Tuple of EntropySurfacePoint objects.
        mean_edm: Mean EDM across all values.
        overall_mean_entropy: Mean entropy across all values.
        overall_variance: Variance of entropy across all values.
        baseline_entropy: Entropy of the baseline run.

    Example:
        >>> surface = EntropySurface(
        ...     axis="brightness",
        ...     points=(point1, point2),
        ...     mean_edm=0.05,
        ...     overall_mean_entropy=2.3,
        ...     overall_variance=0.01,
        ...     baseline_entropy=2.3,
        ... )
    """

    axis: str
    points: tuple[EntropySurfacePoint, ...]
    mean_edm: float
    overall_mean_entropy: float
    overall_variance: float
    baseline_entropy: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with alphabetically sorted keys.
        """
        result = {
            "axis": self.axis,
            "mean_edm": self.mean_edm,
            "overall_mean_entropy": self.overall_mean_entropy,
            "overall_variance": self.overall_variance,
            "points": [p.to_dict() for p in self.points],
        }
        if self.baseline_entropy is not None:
            result["baseline_entropy"] = self.baseline_entropy
        return result


@dataclass(frozen=True)
class RichSurfaces:
    """Collection of M14 rich mode surfaces.

    Combines confidence and entropy surfaces into a single structure
    for convenient serialization.

    Attributes:
        confidence_surfaces: Tuple of ConfidenceSurface objects.
        entropy_surfaces: Tuple of EntropySurface objects.
        global_mean_csi: Global mean CSI across all axes.
        global_mean_edm: Global mean EDM across all axes.

    Example:
        >>> rich = RichSurfaces(
        ...     confidence_surfaces=(conf1, conf2),
        ...     entropy_surfaces=(ent1, ent2),
        ...     global_mean_csi=0.95,
        ...     global_mean_edm=0.05,
        ... )
    """

    confidence_surfaces: tuple[ConfidenceSurface, ...]
    entropy_surfaces: tuple[EntropySurface, ...]
    global_mean_csi: float
    global_mean_edm: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with alphabetically sorted keys.
        """
        return {
            "confidence_surfaces": [s.to_dict() for s in self.confidence_surfaces],
            "entropy_surfaces": [s.to_dict() for s in self.entropy_surfaces],
            "global_mean_csi": self.global_mean_csi,
            "global_mean_edm": self.global_mean_edm,
        }

