"""Counterfactual Engine for CLARITY.

This module provides counterfactual probing capabilities to test causal
evidence dependence by systematically masking image regions and measuring
the impact on model reasoning stability.

CRITICAL CONSTRAINTS (M08):
1. All computation must be deterministic given identical inputs.
2. No randomness, no datetime.now, no uuid.
3. No subprocess.
4. No direct r2l imports.
5. All floats rounded to 8 decimal places at storage.
6. Deterministic ordering: region_ids alphabetical, axes alphabetical.
7. Frozen dataclasses only.
8. Pure consumer of existing CLARITY modules.
9. Masking uses fixed fill value (128 neutral gray).
10. Grid-based region definitions only (M08 scope).

The engine consumes:
- Baseline image (PIL Image)
- RobustnessSurface or metric values for baseline

And produces:
- ProbeSurface with delta metrics per region/coordinate

Region Definition:
- Grid-based: k×k uniform grid over image
- Each cell identified by (row, col, grid_size)
- Normalized coordinates [0.0, 1.0] for position

Masking Strategy:
- Fill masked region with fixed neutral value (128)
- Preserve image dimensions
- Deterministic and reproducible
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PIL import Image


# Fixed fill value for masking (neutral gray)
MASK_FILL_VALUE: int = 128


class CounterfactualComputationError(Exception):
    """Raised when counterfactual computation fails.

    This error indicates a failure during counterfactual probing, such as:
    - Invalid region specification
    - Invalid image data
    - Empty probe set
    - Computation failure
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
class RegionMask:
    """Defines a rectangular region for masking.

    Represents a grid cell in normalized image coordinates [0.0, 1.0].

    Attributes:
        region_id: Unique identifier (e.g., "grid_r0_c1_k3").
        row: Grid row index (0-indexed).
        col: Grid column index (0-indexed).
        grid_size: Grid dimension (e.g., 3 for 3×3 grid).
        x_min: Left edge in normalized coordinates [0.0, 1.0].
        y_min: Top edge in normalized coordinates [0.0, 1.0].
        x_max: Right edge in normalized coordinates [0.0, 1.0].
        y_max: Bottom edge in normalized coordinates [0.0, 1.0].

    Example:
        >>> mask = RegionMask(
        ...     region_id="grid_r0_c1_k3",
        ...     row=0, col=1, grid_size=3,
        ...     x_min=0.33333333, y_min=0.0,
        ...     x_max=0.66666667, y_max=0.33333333,
        ... )
    """

    region_id: str
    row: int
    col: int
    grid_size: int
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with all attributes in alphabetical key order.
        """
        return {
            "col": self.col,
            "grid_size": self.grid_size,
            "region_id": self.region_id,
            "row": self.row,
            "x_max": self.x_max,
            "x_min": self.x_min,
            "y_max": self.y_max,
            "y_min": self.y_min,
        }


@dataclass(frozen=True)
class CounterfactualProbe:
    """Specifies a counterfactual probe configuration.

    Represents a specific region mask applied at a specific sweep coordinate.

    Attributes:
        region_id: Which region is masked.
        axis: Which perturbation axis (e.g., "brightness").
        value: Which axis value (encoded string, e.g., "1p0").

    Example:
        >>> probe = CounterfactualProbe(
        ...     region_id="grid_r0_c1_k3",
        ...     axis="brightness",
        ...     value="1p0",
        ... )
    """

    region_id: str
    axis: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with axis, region_id, value keys (alphabetical).
        """
        return {
            "axis": self.axis,
            "region_id": self.region_id,
            "value": self.value,
        }


@dataclass(frozen=True)
class ProbeResult:
    """Result of a single counterfactual probe.

    Contains baseline and masked metric values along with computed deltas.

    Attributes:
        probe: The CounterfactualProbe that was executed.
        baseline_esi: ESI metric from baseline (unmasked) evaluation.
        masked_esi: ESI metric from masked evaluation.
        delta_esi: Difference (masked - baseline) for ESI.
        baseline_drift: Drift metric from baseline evaluation.
        masked_drift: Drift metric from masked evaluation.
        delta_drift: Difference (masked - baseline) for Drift.

    Example:
        >>> result = ProbeResult(
        ...     probe=probe,
        ...     baseline_esi=0.8,
        ...     masked_esi=0.5,
        ...     delta_esi=-0.3,
        ...     baseline_drift=0.1,
        ...     masked_drift=0.3,
        ...     delta_drift=0.2,
        ... )
    """

    probe: CounterfactualProbe
    baseline_esi: float
    masked_esi: float
    delta_esi: float
    baseline_drift: float
    masked_drift: float
    delta_drift: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with all attributes in alphabetical key order.
        """
        return {
            "baseline_drift": self.baseline_drift,
            "baseline_esi": self.baseline_esi,
            "delta_drift": self.delta_drift,
            "delta_esi": self.delta_esi,
            "masked_drift": self.masked_drift,
            "masked_esi": self.masked_esi,
            "probe": self.probe.to_dict(),
        }


@dataclass(frozen=True)
class ProbeSurface:
    """Aggregated results from all counterfactual probes.

    Contains all probe results with computed summary statistics for
    delta ESI and delta Drift across all probes.

    Attributes:
        results: Tuple of ProbeResult objects, ordered by (region_id, axis, value).
        mean_abs_delta_esi: Mean of absolute delta ESI values.
        max_abs_delta_esi: Maximum absolute delta ESI value.
        mean_abs_delta_drift: Mean of absolute delta Drift values.
        max_abs_delta_drift: Maximum absolute delta Drift value.

    Example:
        >>> surface = ProbeSurface(
        ...     results=(result1, result2),
        ...     mean_abs_delta_esi=0.15,
        ...     max_abs_delta_esi=0.3,
        ...     mean_abs_delta_drift=0.1,
        ...     max_abs_delta_drift=0.2,
        ... )
    """

    results: tuple[ProbeResult, ...]
    mean_abs_delta_esi: float
    max_abs_delta_esi: float
    mean_abs_delta_drift: float
    max_abs_delta_drift: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.

        Returns:
            Dictionary with all attributes in alphabetical key order.
        """
        return {
            "max_abs_delta_drift": self.max_abs_delta_drift,
            "max_abs_delta_esi": self.max_abs_delta_esi,
            "mean_abs_delta_drift": self.mean_abs_delta_drift,
            "mean_abs_delta_esi": self.mean_abs_delta_esi,
            "results": [r.to_dict() for r in self.results],
        }


def generate_grid_masks(grid_size: int) -> tuple[RegionMask, ...]:
    """Generate grid-based region masks.

    Creates k×k uniform grid masks over normalized image coordinates.
    Each cell is identified by (row, col) with deterministic region_id.

    Args:
        grid_size: Number of cells per dimension (e.g., 3 for 3×3 = 9 regions).

    Returns:
        Tuple of RegionMask objects, ordered by (row, col).

    Raises:
        CounterfactualComputationError: If grid_size < 1.

    Example:
        >>> masks = generate_grid_masks(3)
        >>> len(masks)
        9
        >>> masks[0].region_id
        'grid_r0_c0_k3'
    """
    if grid_size < 1:
        raise CounterfactualComputationError(
            f"grid_size must be >= 1, got {grid_size}"
        )

    cell_size = 1.0 / grid_size
    masks: list[RegionMask] = []

    for row in range(grid_size):
        for col in range(grid_size):
            region_id = f"grid_r{row}_c{col}_k{grid_size}"

            x_min = _round8(col * cell_size)
            y_min = _round8(row * cell_size)
            x_max = _round8((col + 1) * cell_size)
            y_max = _round8((row + 1) * cell_size)

            # Ensure boundary values are exactly 0.0 or 1.0
            if col == 0:
                x_min = 0.0
            if row == 0:
                y_min = 0.0
            if col == grid_size - 1:
                x_max = 1.0
            if row == grid_size - 1:
                y_max = 1.0

            masks.append(
                RegionMask(
                    region_id=region_id,
                    row=row,
                    col=col,
                    grid_size=grid_size,
                    x_min=x_min,
                    y_min=y_min,
                    x_max=x_max,
                    y_max=y_max,
                )
            )

    return tuple(masks)


def apply_mask(
    image: Image.Image,
    mask: RegionMask,
    fill_value: int = MASK_FILL_VALUE,
) -> Image.Image:
    """Apply a region mask to an image.

    Creates a copy of the image with the specified region filled with
    a constant value. The original image is not modified.

    Args:
        image: PIL Image to mask (RGB mode expected).
        mask: RegionMask defining the region to fill.
        fill_value: Grayscale value to fill the region (0-255).
                   Default is MASK_FILL_VALUE (128).

    Returns:
        New PIL Image with the masked region filled.

    Raises:
        CounterfactualComputationError: If image is invalid or mask is invalid.

    Example:
        >>> masked_img = apply_mask(original_img, mask, fill_value=128)
    """
    if image is None:
        raise CounterfactualComputationError("Image cannot be None")

    if image.mode != "RGB":
        raise CounterfactualComputationError(
            f"Image must be RGB mode, got {image.mode}"
        )

    if not (0 <= fill_value <= 255):
        raise CounterfactualComputationError(
            f"fill_value must be 0-255, got {fill_value}"
        )

    # Validate mask coordinates
    if not (0.0 <= mask.x_min < mask.x_max <= 1.0):
        raise CounterfactualComputationError(
            f"Invalid mask x coordinates: x_min={mask.x_min}, x_max={mask.x_max}"
        )
    if not (0.0 <= mask.y_min < mask.y_max <= 1.0):
        raise CounterfactualComputationError(
            f"Invalid mask y coordinates: y_min={mask.y_min}, y_max={mask.y_max}"
        )

    # Create a copy to avoid mutation
    result = image.copy()

    # Convert normalized coordinates to pixel coordinates
    width, height = image.size

    # Calculate pixel bounds (integer)
    x1 = int(mask.x_min * width)
    y1 = int(mask.y_min * height)
    x2 = int(mask.x_max * width)
    y2 = int(mask.y_max * height)

    # Clamp to image bounds
    x1 = max(0, min(x1, width))
    y1 = max(0, min(y1, height))
    x2 = max(0, min(x2, width))
    y2 = max(0, min(y2, height))

    # Skip if region is empty after rounding
    if x2 <= x1 or y2 <= y1:
        return result

    # Create fill color tuple (RGB)
    fill_color = (fill_value, fill_value, fill_value)

    # Fill the region using PIL's paste with a solid color image
    region_width = x2 - x1
    region_height = y2 - y1
    fill_region = Image.new("RGB", (region_width, region_height), fill_color)
    result.paste(fill_region, (x1, y1))

    return result


def compute_probe_result(
    probe: CounterfactualProbe,
    baseline_esi: float,
    baseline_drift: float,
    masked_esi: float,
    masked_drift: float,
) -> ProbeResult:
    """Compute a ProbeResult from baseline and masked metrics.

    Calculates delta values (masked - baseline) with 8-decimal rounding.

    Args:
        probe: The CounterfactualProbe specification.
        baseline_esi: ESI from baseline (unmasked) evaluation.
        baseline_drift: Drift from baseline evaluation.
        masked_esi: ESI from masked evaluation.
        masked_drift: Drift from masked evaluation.

    Returns:
        ProbeResult with computed deltas.

    Raises:
        CounterfactualComputationError: If any metric is NaN or inf.
    """
    import math

    # Validate inputs are finite
    for name, value in [
        ("baseline_esi", baseline_esi),
        ("baseline_drift", baseline_drift),
        ("masked_esi", masked_esi),
        ("masked_drift", masked_drift),
    ]:
        if not math.isfinite(value):
            raise CounterfactualComputationError(
                f"Invalid {name} value: {value} (must be finite)"
            )

    delta_esi = _round8(masked_esi - baseline_esi)
    delta_drift = _round8(masked_drift - baseline_drift)

    return ProbeResult(
        probe=probe,
        baseline_esi=_round8(baseline_esi),
        masked_esi=_round8(masked_esi),
        delta_esi=delta_esi,
        baseline_drift=_round8(baseline_drift),
        masked_drift=_round8(masked_drift),
        delta_drift=delta_drift,
    )


def compute_probe_surface(results: list[ProbeResult]) -> ProbeSurface:
    """Compute ProbeSurface from a list of probe results.

    Aggregates results and computes summary statistics for delta metrics.
    Results are sorted by (region_id, axis, value) for deterministic ordering.

    Args:
        results: List of ProbeResult objects.

    Returns:
        ProbeSurface with sorted results and computed statistics.

    Raises:
        CounterfactualComputationError: If results list is empty.
    """
    if not results:
        raise CounterfactualComputationError(
            "Cannot compute ProbeSurface from empty results"
        )

    # Sort results by (region_id, axis, value) for deterministic ordering
    sorted_results = sorted(
        results,
        key=lambda r: (r.probe.region_id, r.probe.axis, r.probe.value),
    )

    # Compute summary statistics
    abs_delta_esi = [abs(r.delta_esi) for r in sorted_results]
    abs_delta_drift = [abs(r.delta_drift) for r in sorted_results]

    n = len(sorted_results)
    mean_abs_delta_esi = _round8(sum(abs_delta_esi) / n)
    max_abs_delta_esi = _round8(max(abs_delta_esi))
    mean_abs_delta_drift = _round8(sum(abs_delta_drift) / n)
    max_abs_delta_drift = _round8(max(abs_delta_drift))

    return ProbeSurface(
        results=tuple(sorted_results),
        mean_abs_delta_esi=mean_abs_delta_esi,
        max_abs_delta_esi=max_abs_delta_esi,
        mean_abs_delta_drift=mean_abs_delta_drift,
        max_abs_delta_drift=max_abs_delta_drift,
    )


class CounterfactualEngine:
    """Engine for computing counterfactual probes.

    The CounterfactualEngine applies region masks to images and computes
    delta metrics to measure causal evidence dependence.

    This engine is a pure consumer of CLARITY's metric pipeline:
    - Uses existing image utilities for masking
    - Computes deltas from provided metric values
    - Does not invoke R2L directly

    Typical workflow:
    1. Generate grid masks: generate_grid_masks(k)
    2. For each mask + coordinate combination:
       a. Apply mask to image: apply_mask(image, mask)
       b. Run inference on masked image (external)
       c. Compute metrics on masked run (external)
       d. Create ProbeResult with deltas
    3. Aggregate into ProbeSurface: compute_probe_surface(results)

    Example:
        >>> engine = CounterfactualEngine()
        >>> masks = generate_grid_masks(3)
        >>> # ... run masked evaluations externally ...
        >>> surface = engine.build_probe_surface(results)
    """

    def build_probe_surface(self, results: list[ProbeResult]) -> ProbeSurface:
        """Build a ProbeSurface from probe results.

        Delegates to compute_probe_surface for actual computation.
        This method provides an instance-based API for consistency
        with other CLARITY engines.

        Args:
            results: List of ProbeResult objects from probing.

        Returns:
            ProbeSurface with aggregated results and statistics.

        Raises:
            CounterfactualComputationError: If results list is empty.
        """
        return compute_probe_surface(results)

    def probe_single(
        self,
        image: Image.Image,
        mask: RegionMask,
        axis: str,
        value: str,
        baseline_esi: float,
        baseline_drift: float,
        masked_esi: float,
        masked_drift: float,
    ) -> ProbeResult:
        """Execute a single counterfactual probe.

        Creates a CounterfactualProbe and computes the ProbeResult
        from provided baseline and masked metrics.

        Note: This method does NOT run inference. The caller must:
        1. Apply the mask to the image (use apply_mask())
        2. Run inference on the masked image
        3. Compute metrics on the masked run
        4. Pass the results to this method

        Args:
            image: The original image (for validation only).
            mask: The RegionMask applied.
            axis: The perturbation axis name.
            value: The encoded axis value.
            baseline_esi: ESI from baseline evaluation.
            baseline_drift: Drift from baseline evaluation.
            masked_esi: ESI from masked evaluation.
            masked_drift: Drift from masked evaluation.

        Returns:
            ProbeResult with computed deltas.

        Raises:
            CounterfactualComputationError: On invalid inputs.
        """
        if image is None:
            raise CounterfactualComputationError("Image cannot be None")

        if not axis:
            raise CounterfactualComputationError("Axis cannot be empty")

        if not value:
            raise CounterfactualComputationError("Value cannot be empty")

        probe = CounterfactualProbe(
            region_id=mask.region_id,
            axis=axis,
            value=value,
        )

        return compute_probe_result(
            probe=probe,
            baseline_esi=baseline_esi,
            baseline_drift=baseline_drift,
            masked_esi=masked_esi,
            masked_drift=masked_drift,
        )

    def generate_masks(self, grid_size: int) -> tuple[RegionMask, ...]:
        """Generate grid-based region masks.

        Convenience method that delegates to generate_grid_masks().

        Args:
            grid_size: Number of cells per dimension.

        Returns:
            Tuple of RegionMask objects.

        Raises:
            CounterfactualComputationError: If grid_size < 1.
        """
        return generate_grid_masks(grid_size)

