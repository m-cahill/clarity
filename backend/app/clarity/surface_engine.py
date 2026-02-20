"""Surface Engine for CLARITY.

This module provides the core computation engine for building robustness surfaces
from M05 metrics output. Surfaces aggregate ESI and Drift metrics into analyzable
structures with per-axis and global statistics.

CRITICAL CONSTRAINTS (M06):
1. All computation must be deterministic given identical MetricsResult.
2. No randomness, no datetime.now, no uuid.
3. No numpy — pure Python only.
4. No r2l imports.
5. No subprocess.
6. No file I/O.
7. All floats rounded to 8 decimal places at storage.
8. Deterministic ordering: axes alphabetical, values lexicographic.

The engine consumes:
- MetricsResult (from MetricsEngine)

And produces:
- RobustnessSurface with axis-level and global statistics
"""

from __future__ import annotations

import math

from app.clarity.metrics import MetricsResult
from app.clarity.surfaces import (
    AxisSurface,
    RobustnessSurface,
    SurfaceComputationError,
    SurfacePoint,
    _round8,
)


class SurfaceEngine:
    """Engine for computing robustness surfaces from metrics.

    The SurfaceEngine transforms MetricsResult (ESI + Drift metrics) into
    structured robustness surfaces with per-axis and global statistics.
    All computation is deterministic and produces identical results
    given identical input.

    The engine:
    1. Validates MetricsResult (non-empty, no NaN/inf)
    2. Joins ESI and Drift by axis name
    3. Joins values within each axis
    4. Computes per-axis mean and variance
    5. Computes global mean and variance
    6. Returns RobustnessSurface

    Example:
        >>> engine = SurfaceEngine()
        >>> surface = engine.compute(metrics_result)
        >>> print(f"Global ESI mean: {surface.global_mean_esi}")
    """

    def compute(self, metrics: MetricsResult) -> RobustnessSurface:
        """Compute robustness surface from metrics.

        Args:
            metrics: MetricsResult from MetricsEngine.compute().

        Returns:
            RobustnessSurface with axis surfaces and global statistics.

        Raises:
            SurfaceComputationError: If metrics are empty, axes don't match,
                values don't match, or contain NaN/inf values.
        """
        # Validate non-empty
        if not metrics.esi or not metrics.drift:
            raise SurfaceComputationError(
                "MetricsResult has no axes (empty ESI or Drift)"
            )

        # Build axis lookup for ESI and Drift
        esi_by_axis = {m.axis: m for m in metrics.esi}
        drift_by_axis = {m.axis: m for m in metrics.drift}

        # Validate axis sets match
        esi_axes = set(esi_by_axis.keys())
        drift_axes = set(drift_by_axis.keys())

        if esi_axes != drift_axes:
            esi_only = esi_axes - drift_axes
            drift_only = drift_axes - esi_axes
            raise SurfaceComputationError(
                f"Axis mismatch between ESI and Drift. "
                f"ESI-only: {sorted(esi_only)}, Drift-only: {sorted(drift_only)}"
            )

        # Process axes in alphabetical order
        sorted_axis_names = sorted(esi_axes)

        axis_surfaces: list[AxisSurface] = []
        all_points: list[SurfacePoint] = []

        for axis_name in sorted_axis_names:
            esi_metric = esi_by_axis[axis_name]
            drift_metric = drift_by_axis[axis_name]

            # Validate value sets match
            esi_values = set(esi_metric.value_scores.keys())
            drift_values = set(drift_metric.value_scores.keys())

            if esi_values != drift_values:
                esi_only = esi_values - drift_values
                drift_only = drift_values - esi_values
                raise SurfaceComputationError(
                    f"Value mismatch for axis '{axis_name}'. "
                    f"ESI-only: {sorted(esi_only)}, Drift-only: {sorted(drift_only)}"
                )

            # Build points in lexicographic order by value
            sorted_values = sorted(esi_values)
            points: list[SurfacePoint] = []

            for value in sorted_values:
                esi_score = esi_metric.value_scores[value]
                drift_score = drift_metric.value_scores[value]

                # Validate no NaN/inf
                if not math.isfinite(esi_score):
                    raise SurfaceComputationError(
                        f"Invalid ESI value for axis '{axis_name}', "
                        f"value '{value}': {esi_score}"
                    )
                if not math.isfinite(drift_score):
                    raise SurfaceComputationError(
                        f"Invalid Drift value for axis '{axis_name}', "
                        f"value '{value}': {drift_score}"
                    )

                point = SurfacePoint(
                    axis=axis_name,
                    value=value,
                    esi=_round8(esi_score),
                    drift=_round8(drift_score),
                )
                points.append(point)

            all_points.extend(points)

            # Compute axis statistics
            axis_surface = self._compute_axis_surface(axis_name, points)
            axis_surfaces.append(axis_surface)

        # Compute global statistics across all points
        global_stats = self._compute_global_statistics(all_points)

        return RobustnessSurface(
            axes=tuple(axis_surfaces),
            global_mean_esi=global_stats["mean_esi"],
            global_mean_drift=global_stats["mean_drift"],
            global_variance_esi=global_stats["variance_esi"],
            global_variance_drift=global_stats["variance_drift"],
        )

    def _compute_axis_surface(
        self, axis_name: str, points: list[SurfacePoint]
    ) -> AxisSurface:
        """Compute axis surface with mean and variance statistics.

        Args:
            axis_name: Name of the axis.
            points: List of SurfacePoint objects for this axis.

        Returns:
            AxisSurface with computed statistics.
        """
        n = len(points)

        # Compute means
        sum_esi = sum(p.esi for p in points)
        sum_drift = sum(p.drift for p in points)

        mean_esi = sum_esi / n
        mean_drift = sum_drift / n

        # Compute population variance
        sum_sq_esi = sum((p.esi - mean_esi) ** 2 for p in points)
        sum_sq_drift = sum((p.drift - mean_drift) ** 2 for p in points)

        variance_esi = sum_sq_esi / n
        variance_drift = sum_sq_drift / n

        return AxisSurface(
            axis=axis_name,
            points=tuple(points),
            mean_esi=_round8(mean_esi),
            mean_drift=_round8(mean_drift),
            variance_esi=_round8(variance_esi),
            variance_drift=_round8(variance_drift),
        )

    def _compute_global_statistics(
        self, all_points: list[SurfacePoint]
    ) -> dict[str, float]:
        """Compute global statistics across all points.

        Args:
            all_points: List of all SurfacePoint objects across all axes.

        Returns:
            Dictionary with mean_esi, mean_drift, variance_esi, variance_drift.
        """
        n = len(all_points)

        # Compute means
        sum_esi = sum(p.esi for p in all_points)
        sum_drift = sum(p.drift for p in all_points)

        mean_esi = sum_esi / n
        mean_drift = sum_drift / n

        # Compute population variance
        sum_sq_esi = sum((p.esi - mean_esi) ** 2 for p in all_points)
        sum_sq_drift = sum((p.drift - mean_drift) ** 2 for p in all_points)

        variance_esi = sum_sq_esi / n
        variance_drift = sum_sq_drift / n

        return {
            "mean_esi": _round8(mean_esi),
            "mean_drift": _round8(mean_drift),
            "variance_esi": _round8(variance_esi),
            "variance_drift": _round8(variance_drift),
        }

