"""Gradient Engine for CLARITY.

This module provides gradient estimation and stability metrics over robustness
surfaces. Gradients quantify local slope (sensitivity) of ESI and Drift metrics
along perturbation axes, enabling detection of "failure cliffs" and unstable
reasoning regions.

CRITICAL CONSTRAINTS (M07):
1. All computation must be deterministic given identical RobustnessSurface.
2. No randomness, no datetime.now, no uuid.
3. No numpy — pure Python only.
4. No r2l imports.
5. No subprocess.
6. No file I/O.
7. All floats rounded to 8 decimal places at storage.
8. Deterministic ordering: axes alphabetical, values lexicographic.
9. Pure consumer of RobustnessSurface — no mutation.

The engine consumes:
- RobustnessSurface (from SurfaceEngine)

And produces:
- GradientSurface with axis-level and global stability metrics

Gradient Computation:
- Interior points: central difference (f[i+1] - f[i-1]) / 2
- Endpoints: simple first difference (forward/backward)
- Single-value axis: zero gradient
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.clarity.surfaces import AxisSurface, RobustnessSurface, SurfacePoint


class GradientComputationError(Exception):
    """Raised when gradient computation fails.

    This error indicates a failure during gradient computation, such as:
    - Empty RobustnessSurface (no axes)
    - NaN or inf values in surface
    - Invalid surface structure
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
class GradientPoint:
    """Single gradient point on a robustness surface.

    Represents the local slope (gradient) of ESI and Drift at a specific
    axis value position.

    Attributes:
        axis: The name of the perturbation axis.
        value: The encoded axis value (string).
        d_esi: Gradient (slope) of ESI at this point.
        d_drift: Gradient (slope) of Drift at this point.

    Example:
        >>> point = GradientPoint(
        ...     axis="brightness",
        ...     value="1p0",
        ...     d_esi=0.125,
        ...     d_drift=-0.05,
        ... )
    """

    axis: str
    value: str
    d_esi: float
    d_drift: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with axis, d_drift, d_esi, value keys (alphabetical).
        """
        return {
            "axis": self.axis,
            "d_drift": self.d_drift,
            "d_esi": self.d_esi,
            "value": self.value,
        }


@dataclass(frozen=True)
class AxisGradient:
    """Gradient summary for a single perturbation axis.

    Aggregates all gradient points for one axis with computed stability
    metrics (mean and max absolute gradients) for both ESI and Drift.

    Attributes:
        axis: The name of the perturbation axis.
        gradients: Tuple of GradientPoint objects, ordered by value.
        mean_abs_esi_gradient: Mean of absolute ESI gradients.
        max_abs_esi_gradient: Maximum absolute ESI gradient.
        mean_abs_drift_gradient: Mean of absolute Drift gradients.
        max_abs_drift_gradient: Maximum absolute Drift gradient.

    Example:
        >>> axis_grad = AxisGradient(
        ...     axis="brightness",
        ...     gradients=(gp1, gp2, gp3),
        ...     mean_abs_esi_gradient=0.1,
        ...     max_abs_esi_gradient=0.25,
        ...     mean_abs_drift_gradient=0.05,
        ...     max_abs_drift_gradient=0.1,
        ... )
    """

    axis: str
    gradients: tuple[GradientPoint, ...]
    mean_abs_esi_gradient: float
    max_abs_esi_gradient: float
    mean_abs_drift_gradient: float
    max_abs_drift_gradient: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.
        Gradients are serialized in their natural (lexicographic) order.

        Returns:
            Dictionary with axis, gradients, max_abs_drift_gradient,
            max_abs_esi_gradient, mean_abs_drift_gradient,
            mean_abs_esi_gradient keys (alphabetical).
        """
        return {
            "axis": self.axis,
            "gradients": [g.to_dict() for g in self.gradients],
            "max_abs_drift_gradient": self.max_abs_drift_gradient,
            "max_abs_esi_gradient": self.max_abs_esi_gradient,
            "mean_abs_drift_gradient": self.mean_abs_drift_gradient,
            "mean_abs_esi_gradient": self.mean_abs_esi_gradient,
        }


@dataclass(frozen=True)
class GradientSurface:
    """Complete gradient surface across all perturbation axes.

    Aggregates all axis gradients with global stability metrics computed
    across all gradient points.

    Attributes:
        axes: Tuple of AxisGradient objects, ordered alphabetically.
        global_mean_abs_esi_gradient: Mean of all absolute ESI gradients.
        global_max_abs_esi_gradient: Maximum absolute ESI gradient (global).
        global_mean_abs_drift_gradient: Mean of all absolute Drift gradients.
        global_max_abs_drift_gradient: Maximum absolute Drift gradient (global).

    Example:
        >>> grad_surface = GradientSurface(
        ...     axes=(axis_grad1, axis_grad2),
        ...     global_mean_abs_esi_gradient=0.15,
        ...     global_max_abs_esi_gradient=0.3,
        ...     global_mean_abs_drift_gradient=0.075,
        ...     global_max_abs_drift_gradient=0.15,
        ... )
    """

    axes: tuple[AxisGradient, ...]
    global_mean_abs_esi_gradient: float
    global_max_abs_esi_gradient: float
    global_mean_abs_drift_gradient: float
    global_max_abs_drift_gradient: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.
        Axes are serialized in their natural (alphabetical) order.

        Returns:
            Dictionary with axes, global_max_abs_drift_gradient,
            global_max_abs_esi_gradient, global_mean_abs_drift_gradient,
            global_mean_abs_esi_gradient keys (alphabetical).
        """
        return {
            "axes": [a.to_dict() for a in self.axes],
            "global_max_abs_drift_gradient": self.global_max_abs_drift_gradient,
            "global_max_abs_esi_gradient": self.global_max_abs_esi_gradient,
            "global_mean_abs_drift_gradient": self.global_mean_abs_drift_gradient,
            "global_mean_abs_esi_gradient": self.global_mean_abs_esi_gradient,
        }


class GradientEngine:
    """Engine for computing gradient surfaces from robustness surfaces.

    The GradientEngine transforms RobustnessSurface into GradientSurface
    by computing local gradients (slopes) at each point using finite
    difference methods.

    Gradient computation rules:
    1. Single-value axis: gradient = 0.0
    2. Two-point axis: forward/backward difference (f1 - f0)
    3. Interior points (N >= 3): central difference (f[i+1] - f[i-1]) / 2
    4. Endpoints (N >= 3): forward (i=0) or backward (i=n-1) difference

    All computation is deterministic and produces identical results
    given identical input.

    Example:
        >>> engine = GradientEngine()
        >>> grad_surface = engine.compute(robustness_surface)
        >>> print(f"Global max ESI gradient: {grad_surface.global_max_abs_esi_gradient}")
    """

    def compute(self, surface: RobustnessSurface) -> GradientSurface:
        """Compute gradient surface from robustness surface.

        Args:
            surface: RobustnessSurface from SurfaceEngine.compute().

        Returns:
            GradientSurface with axis gradients and global stability metrics.

        Raises:
            GradientComputationError: If surface is empty or contains
                invalid values (NaN/inf).
        """
        # Validate non-empty
        if not surface.axes:
            raise GradientComputationError(
                "RobustnessSurface has no axes (empty)"
            )

        # Process each axis (already in alphabetical order from M06)
        axis_gradients: list[AxisGradient] = []
        all_gradient_points: list[GradientPoint] = []

        for axis_surface in surface.axes:
            # Validate surface values
            self._validate_axis_surface(axis_surface)

            # Compute gradients for this axis
            gradient_points = self._compute_axis_gradients(axis_surface)
            all_gradient_points.extend(gradient_points)

            # Compute axis-level statistics
            axis_gradient = self._compute_axis_statistics(
                axis_surface.axis, gradient_points
            )
            axis_gradients.append(axis_gradient)

        # Compute global statistics
        global_stats = self._compute_global_statistics(all_gradient_points)

        return GradientSurface(
            axes=tuple(axis_gradients),
            global_mean_abs_esi_gradient=global_stats["mean_abs_esi"],
            global_max_abs_esi_gradient=global_stats["max_abs_esi"],
            global_mean_abs_drift_gradient=global_stats["mean_abs_drift"],
            global_max_abs_drift_gradient=global_stats["max_abs_drift"],
        )

    def _validate_axis_surface(self, axis_surface: AxisSurface) -> None:
        """Validate that axis surface contains finite values.

        Args:
            axis_surface: The AxisSurface to validate.

        Raises:
            GradientComputationError: If any ESI or Drift value is NaN/inf.
        """
        for point in axis_surface.points:
            if not math.isfinite(point.esi):
                raise GradientComputationError(
                    f"Invalid ESI value for axis '{axis_surface.axis}', "
                    f"value '{point.value}': {point.esi}"
                )
            if not math.isfinite(point.drift):
                raise GradientComputationError(
                    f"Invalid Drift value for axis '{axis_surface.axis}', "
                    f"value '{point.value}': {point.drift}"
                )

    def _compute_axis_gradients(
        self, axis_surface: AxisSurface
    ) -> list[GradientPoint]:
        """Compute gradient points for a single axis.

        Uses finite difference method:
        - Single point: gradient = 0.0
        - Two points: forward/backward difference
        - N >= 3 points: central difference for interior, forward/backward for endpoints

        Args:
            axis_surface: The AxisSurface to compute gradients for.

        Returns:
            List of GradientPoint objects in value order.
        """
        points = axis_surface.points
        n = len(points)
        axis_name = axis_surface.axis

        gradient_points: list[GradientPoint] = []

        for i, point in enumerate(points):
            if n == 1:
                # Single-value axis: zero gradient
                d_esi = 0.0
                d_drift = 0.0
            elif n == 2:
                # Two-point axis: simple difference (same for both endpoints)
                d_esi = points[1].esi - points[0].esi
                d_drift = points[1].drift - points[0].drift
            else:
                # N >= 3: use appropriate difference formula
                if i == 0:
                    # Forward difference for first point
                    d_esi = points[1].esi - points[0].esi
                    d_drift = points[1].drift - points[0].drift
                elif i == n - 1:
                    # Backward difference for last point
                    d_esi = points[n - 1].esi - points[n - 2].esi
                    d_drift = points[n - 1].drift - points[n - 2].drift
                else:
                    # Central difference for interior points
                    d_esi = (points[i + 1].esi - points[i - 1].esi) / 2
                    d_drift = (points[i + 1].drift - points[i - 1].drift) / 2

            gradient_points.append(
                GradientPoint(
                    axis=axis_name,
                    value=point.value,
                    d_esi=_round8(d_esi),
                    d_drift=_round8(d_drift),
                )
            )

        return gradient_points

    def _compute_axis_statistics(
        self, axis_name: str, gradient_points: list[GradientPoint]
    ) -> AxisGradient:
        """Compute axis-level gradient statistics.

        Args:
            axis_name: Name of the axis.
            gradient_points: List of GradientPoint objects for this axis.

        Returns:
            AxisGradient with computed statistics.
        """
        n = len(gradient_points)

        # Collect absolute gradients
        abs_esi_grads = [abs(gp.d_esi) for gp in gradient_points]
        abs_drift_grads = [abs(gp.d_drift) for gp in gradient_points]

        # Compute mean and max
        mean_abs_esi = sum(abs_esi_grads) / n
        max_abs_esi = max(abs_esi_grads)
        mean_abs_drift = sum(abs_drift_grads) / n
        max_abs_drift = max(abs_drift_grads)

        return AxisGradient(
            axis=axis_name,
            gradients=tuple(gradient_points),
            mean_abs_esi_gradient=_round8(mean_abs_esi),
            max_abs_esi_gradient=_round8(max_abs_esi),
            mean_abs_drift_gradient=_round8(mean_abs_drift),
            max_abs_drift_gradient=_round8(max_abs_drift),
        )

    def _compute_global_statistics(
        self, all_gradient_points: list[GradientPoint]
    ) -> dict[str, float]:
        """Compute global gradient statistics across all points.

        Args:
            all_gradient_points: List of all GradientPoint objects.

        Returns:
            Dictionary with mean_abs_esi, max_abs_esi, mean_abs_drift, max_abs_drift.
        """
        n = len(all_gradient_points)

        # Collect absolute gradients
        abs_esi_grads = [abs(gp.d_esi) for gp in all_gradient_points]
        abs_drift_grads = [abs(gp.d_drift) for gp in all_gradient_points]

        # Compute mean and max
        mean_abs_esi = sum(abs_esi_grads) / n
        max_abs_esi = max(abs_esi_grads)
        mean_abs_drift = sum(abs_drift_grads) / n
        max_abs_drift = max(abs_drift_grads)

        return {
            "mean_abs_esi": _round8(mean_abs_esi),
            "max_abs_esi": _round8(max_abs_esi),
            "mean_abs_drift": _round8(mean_abs_drift),
            "max_abs_drift": _round8(max_abs_drift),
        }

