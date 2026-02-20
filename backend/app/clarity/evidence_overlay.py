"""Evidence Overlay Module for CLARITY.

This module provides evidence visualization capabilities including:
- Evidence maps from model outputs
- Normalized heatmaps for visualization
- Region extraction via threshold + BFS for CF-001 closure

CRITICAL CONSTRAINTS (M10):
1. All computation must be deterministic given identical inputs.
2. No randomness, no datetime.now, no uuid.
3. No subprocess.
4. No direct r2l imports.
5. All floats rounded to 8 decimal places at storage.
6. Deterministic BFS traversal (row-major order).
7. Frozen dataclasses only.
8. Region sorting: (area desc, x asc, y asc).
9. Fixed threshold = 0.7 for region extraction.
10. No new dependencies.

The module provides:
- EvidenceMap: Raw evidence values from runner
- Heatmap: Normalized 2D float matrix [0,1]
- OverlayRegion: Bounding box from threshold + BFS
- OverlayBundle: Complete overlay data for API response
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


# Fixed constants for M10
EVIDENCE_THRESHOLD: float = 0.7
DEFAULT_EVIDENCE_WIDTH: int = 224
DEFAULT_EVIDENCE_HEIGHT: int = 224


class EvidenceOverlayError(Exception):
    """Raised when evidence overlay computation fails.

    This error indicates a failure during evidence processing, such as:
    - Invalid evidence map dimensions
    - Invalid values (NaN, inf)
    - Empty input data
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
class EvidenceMap:
    """Raw evidence values from model inference.

    Represents a 2D matrix of evidence/attention values as returned
    by the model or stubbed runner.

    Attributes:
        width: Width of the evidence map in pixels.
        height: Height of the evidence map in pixels.
        values: 2D tuple of float values (row-major order).
                values[y][x] gives the evidence at pixel (x, y).

    Example:
        >>> evidence = EvidenceMap(
        ...     width=224,
        ...     height=224,
        ...     values=((0.1, 0.2, ...), ...)
        ... )
    """

    width: int
    height: int
    values: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        """Validate evidence map dimensions."""
        if self.width < 1 or self.height < 1:
            raise EvidenceOverlayError(
                f"Invalid dimensions: width={self.width}, height={self.height}"
            )
        if len(self.values) != self.height:
            raise EvidenceOverlayError(
                f"Values height mismatch: expected {self.height}, got {len(self.values)}"
            )
        for row_idx, row in enumerate(self.values):
            if len(row) != self.width:
                raise EvidenceOverlayError(
                    f"Row {row_idx} width mismatch: expected {self.width}, got {len(row)}"
                )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with width, height, and values (as nested lists).
        """
        return {
            "height": self.height,
            "values": [list(row) for row in self.values],
            "width": self.width,
        }


@dataclass(frozen=True)
class Heatmap:
    """Normalized heatmap for visualization.

    A 2D matrix of normalized float values in [0, 1] range,
    ready for colormap application on the frontend.

    Attributes:
        width: Width of the heatmap in pixels.
        height: Height of the heatmap in pixels.
        values: 2D tuple of normalized float values [0, 1].
                All values are rounded to 8 decimal places.

    Example:
        >>> heatmap = Heatmap(
        ...     width=224,
        ...     height=224,
        ...     values=((0.0, 0.1, ...), ...)
        ... )
    """

    width: int
    height: int
    values: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        """Validate heatmap dimensions and value ranges."""
        if self.width < 1 or self.height < 1:
            raise EvidenceOverlayError(
                f"Invalid dimensions: width={self.width}, height={self.height}"
            )
        if len(self.values) != self.height:
            raise EvidenceOverlayError(
                f"Values height mismatch: expected {self.height}, got {len(self.values)}"
            )
        for row_idx, row in enumerate(self.values):
            if len(row) != self.width:
                raise EvidenceOverlayError(
                    f"Row {row_idx} width mismatch: expected {self.width}, got {len(row)}"
                )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with width, height, and values (as nested lists).
        """
        return {
            "height": self.height,
            "values": [list(row) for row in self.values],
            "width": self.width,
        }


@dataclass(frozen=True)
class OverlayRegion:
    """A region extracted from evidence map via thresholding.

    Represents a bounding box around a connected component of
    high-evidence pixels (above threshold).

    Attributes:
        region_id: Unique identifier (e.g., "evidence_r0").
        x_min: Left edge in normalized coordinates [0, 1].
        y_min: Top edge in normalized coordinates [0, 1].
        x_max: Right edge in normalized coordinates [0, 1].
        y_max: Bottom edge in normalized coordinates [0, 1].
        area: Normalized area (x_max - x_min) * (y_max - y_min).

    Example:
        >>> region = OverlayRegion(
        ...     region_id="evidence_r0",
        ...     x_min=0.2, y_min=0.3,
        ...     x_max=0.5, y_max=0.6,
        ...     area=0.09,
        ... )
    """

    region_id: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    area: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all attributes in alphabetical key order.
        """
        return {
            "area": self.area,
            "region_id": self.region_id,
            "x_max": self.x_max,
            "x_min": self.x_min,
            "y_max": self.y_max,
            "y_min": self.y_min,
        }


@dataclass(frozen=True)
class OverlayBundle:
    """Complete overlay data for API response.

    Contains all visualization data needed by the frontend:
    - Evidence map (raw values)
    - Heatmap (normalized for colormap)
    - Regions (bounding boxes from threshold + BFS)

    Attributes:
        evidence_map: The raw evidence map from inference.
        heatmap: Normalized heatmap for visualization.
        regions: Tuple of extracted regions, sorted by (area desc, x asc, y asc).

    Example:
        >>> bundle = OverlayBundle(
        ...     evidence_map=evidence,
        ...     heatmap=heatmap,
        ...     regions=(region1, region2),
        ... )
    """

    evidence_map: EvidenceMap
    heatmap: Heatmap
    regions: tuple[OverlayRegion, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with evidence_map, heatmap, and regions.
        """
        return {
            "evidence_map": self.evidence_map.to_dict(),
            "heatmap": self.heatmap.to_dict(),
            "regions": [r.to_dict() for r in self.regions],
        }


def generate_stubbed_evidence_map(
    width: int = DEFAULT_EVIDENCE_WIDTH,
    height: int = DEFAULT_EVIDENCE_HEIGHT,
    seed: int = 42,
) -> EvidenceMap:
    """Generate a deterministic stubbed evidence map.

    Creates a synthetic evidence map with 2-3 Gaussian-like bumps
    at fixed positions. The pattern is fully deterministic based
    on the seed parameter.

    Args:
        width: Width of the evidence map.
        height: Height of the evidence map.
        seed: Seed for deterministic pattern generation.
              Different seeds produce different bump positions.

    Returns:
        EvidenceMap with deterministic synthetic values.

    Example:
        >>> evidence = generate_stubbed_evidence_map(224, 224, seed=42)
        >>> evidence.width
        224
    """
    if width < 1 or height < 1:
        raise EvidenceOverlayError(
            f"Invalid dimensions: width={width}, height={height}"
        )

    # Fixed bump parameters based on seed
    # Use simple deterministic formulas to vary positions
    bump_count = 2 + (seed % 2)  # 2 or 3 bumps

    # Bump centers as fractions of image dimensions
    # Deterministic based on seed
    bumps: list[tuple[float, float, float]] = []  # (cx, cy, sigma)

    for i in range(bump_count):
        # Deterministic center calculation
        cx = 0.3 + 0.2 * i + 0.1 * ((seed + i) % 3)
        cy = 0.3 + 0.15 * i + 0.1 * ((seed + i * 2) % 4)
        sigma = 0.08 + 0.02 * (i % 2)

        # Clamp to valid range
        cx = max(0.1, min(0.9, cx))
        cy = max(0.1, min(0.9, cy))

        bumps.append((cx, cy, sigma))

    # Generate values
    rows: list[tuple[float, ...]] = []

    for y in range(height):
        row: list[float] = []
        ny = y / (height - 1) if height > 1 else 0.5

        for x in range(width):
            nx = x / (width - 1) if width > 1 else 0.5

            # Sum Gaussian contributions from all bumps
            value = 0.0
            for cx, cy, sigma in bumps:
                dx = nx - cx
                dy = ny - cy
                dist_sq = dx * dx + dy * dy
                # Gaussian formula: exp(-dist^2 / (2 * sigma^2))
                value += math.exp(-dist_sq / (2 * sigma * sigma))

            # Clamp to [0, 1] and round
            value = _round8(max(0.0, min(1.0, value)))
            row.append(value)

        rows.append(tuple(row))

    return EvidenceMap(
        width=width,
        height=height,
        values=tuple(rows),
    )


def normalize_evidence_to_heatmap(evidence: EvidenceMap) -> Heatmap:
    """Normalize an evidence map to a heatmap.

    Applies min-max normalization to scale values to [0, 1].
    All values are rounded to 8 decimal places.

    Args:
        evidence: The evidence map to normalize.

    Returns:
        Heatmap with normalized values.

    Raises:
        EvidenceOverlayError: If evidence map is invalid.

    Example:
        >>> heatmap = normalize_evidence_to_heatmap(evidence)
        >>> all(0 <= v <= 1 for row in heatmap.values for v in row)
        True
    """
    # Find min and max values
    min_val = float("inf")
    max_val = float("-inf")

    for row in evidence.values:
        for value in row:
            if not math.isfinite(value):
                raise EvidenceOverlayError(f"Non-finite value in evidence map: {value}")
            if value < min_val:
                min_val = value
            if value > max_val:
                max_val = value

    # Handle edge case where all values are the same
    value_range = max_val - min_val
    if value_range < 1e-10:
        # All values are essentially the same
        # Return a constant heatmap (0.5 if there were values, or 0.0)
        const_val = 0.5 if max_val > 0 else 0.0
        normalized_rows = tuple(
            tuple(_round8(const_val) for _ in row)
            for row in evidence.values
        )
    else:
        # Min-max normalize
        normalized_rows = tuple(
            tuple(_round8((v - min_val) / value_range) for v in row)
            for row in evidence.values
        )

    return Heatmap(
        width=evidence.width,
        height=evidence.height,
        values=normalized_rows,
    )


def extract_regions_from_heatmap(
    heatmap: Heatmap,
    threshold: float = EVIDENCE_THRESHOLD,
) -> tuple[OverlayRegion, ...]:
    """Extract connected regions from heatmap via threshold + BFS.

    Performs thresholding to find pixels above threshold, then uses
    deterministic BFS (row-major order) to find connected components.
    Each component becomes an OverlayRegion with a bounding box.

    Args:
        heatmap: The normalized heatmap.
        threshold: Threshold value for region extraction (default 0.7).

    Returns:
        Tuple of OverlayRegion objects, sorted by (area desc, x asc, y asc).

    Example:
        >>> regions = extract_regions_from_heatmap(heatmap, threshold=0.7)
        >>> len(regions)
        2
    """
    if threshold < 0.0 or threshold > 1.0:
        raise EvidenceOverlayError(f"Invalid threshold: {threshold}")

    height = heatmap.height
    width = heatmap.width

    # Create binary mask of above-threshold pixels
    above_threshold: list[list[bool]] = []
    for row in heatmap.values:
        above_threshold.append([v > threshold for v in row])

    # Track visited pixels
    visited: list[list[bool]] = [[False] * width for _ in range(height)]

    # Find connected components via BFS (row-major order)
    components: list[list[tuple[int, int]]] = []

    for start_y in range(height):
        for start_x in range(width):
            if above_threshold[start_y][start_x] and not visited[start_y][start_x]:
                # Start BFS from this pixel
                component: list[tuple[int, int]] = []
                queue: list[tuple[int, int]] = [(start_x, start_y)]
                visited[start_y][start_x] = True

                while queue:
                    x, y = queue.pop(0)
                    component.append((x, y))

                    # Check 4-connected neighbors (row-major order for determinism)
                    # Order: up, left, right, down
                    neighbors = [
                        (x, y - 1),  # up
                        (x - 1, y),  # left
                        (x + 1, y),  # right
                        (x, y + 1),  # down
                    ]

                    for nx, ny in neighbors:
                        if 0 <= nx < width and 0 <= ny < height:
                            if above_threshold[ny][nx] and not visited[ny][nx]:
                                visited[ny][nx] = True
                                queue.append((nx, ny))

                if component:
                    components.append(component)

    # Convert components to OverlayRegions
    regions: list[OverlayRegion] = []

    for idx, component in enumerate(components):
        # Find bounding box
        min_x = min(p[0] for p in component)
        max_x = max(p[0] for p in component)
        min_y = min(p[1] for p in component)
        max_y = max(p[1] for p in component)

        # Convert to normalized coordinates
        # Use (pixel + 0.5) / dimension for center-based normalization
        # But for bounding boxes, use pixel edges
        x_min = _round8(min_x / width)
        y_min = _round8(min_y / height)
        x_max = _round8((max_x + 1) / width)
        y_max = _round8((max_y + 1) / height)

        # Clamp to [0, 1]
        x_min = max(0.0, min(1.0, x_min))
        y_min = max(0.0, min(1.0, y_min))
        x_max = max(0.0, min(1.0, x_max))
        y_max = max(0.0, min(1.0, y_max))

        # Compute area
        area = _round8((x_max - x_min) * (y_max - y_min))

        regions.append(
            OverlayRegion(
                region_id=f"evidence_r{idx}",
                x_min=x_min,
                y_min=y_min,
                x_max=x_max,
                y_max=y_max,
                area=area,
            )
        )

    # Sort by (area desc, x_min asc, y_min asc)
    sorted_regions = sorted(
        regions,
        key=lambda r: (-r.area, r.x_min, r.y_min),
    )

    # Re-assign region IDs after sorting
    final_regions: list[OverlayRegion] = []
    for idx, region in enumerate(sorted_regions):
        final_regions.append(
            OverlayRegion(
                region_id=f"evidence_r{idx}",
                x_min=region.x_min,
                y_min=region.y_min,
                x_max=region.x_max,
                y_max=region.y_max,
                area=region.area,
            )
        )

    return tuple(final_regions)


def create_overlay_bundle(
    evidence: EvidenceMap,
    threshold: float = EVIDENCE_THRESHOLD,
) -> OverlayBundle:
    """Create a complete overlay bundle from an evidence map.

    Performs full pipeline:
    1. Normalize evidence to heatmap
    2. Extract regions via threshold + BFS
    3. Bundle everything for API response

    Args:
        evidence: The raw evidence map.
        threshold: Threshold for region extraction (default 0.7).

    Returns:
        OverlayBundle with heatmap and regions.

    Example:
        >>> bundle = create_overlay_bundle(evidence)
        >>> bundle.heatmap.width
        224
    """
    heatmap = normalize_evidence_to_heatmap(evidence)
    regions = extract_regions_from_heatmap(heatmap, threshold)

    return OverlayBundle(
        evidence_map=evidence,
        heatmap=heatmap,
        regions=regions,
    )


class EvidenceOverlayEngine:
    """Engine for computing evidence overlays.

    The EvidenceOverlayEngine provides an instance-based API for
    evidence visualization, consistent with other CLARITY engines.

    Example:
        >>> engine = EvidenceOverlayEngine()
        >>> evidence = engine.generate_stubbed_evidence(seed=42)
        >>> bundle = engine.create_bundle(evidence)
    """

    def generate_stubbed_evidence(
        self,
        width: int = DEFAULT_EVIDENCE_WIDTH,
        height: int = DEFAULT_EVIDENCE_HEIGHT,
        seed: int = 42,
    ) -> EvidenceMap:
        """Generate a deterministic stubbed evidence map.

        Delegates to generate_stubbed_evidence_map().

        Args:
            width: Width of the evidence map.
            height: Height of the evidence map.
            seed: Seed for deterministic pattern.

        Returns:
            EvidenceMap with synthetic values.
        """
        return generate_stubbed_evidence_map(width, height, seed)

    def normalize(self, evidence: EvidenceMap) -> Heatmap:
        """Normalize evidence to heatmap.

        Delegates to normalize_evidence_to_heatmap().

        Args:
            evidence: The evidence map to normalize.

        Returns:
            Normalized heatmap.
        """
        return normalize_evidence_to_heatmap(evidence)

    def extract_regions(
        self,
        heatmap: Heatmap,
        threshold: float = EVIDENCE_THRESHOLD,
    ) -> tuple[OverlayRegion, ...]:
        """Extract regions from heatmap.

        Delegates to extract_regions_from_heatmap().

        Args:
            heatmap: The heatmap to process.
            threshold: Threshold for extraction.

        Returns:
            Tuple of OverlayRegion objects.
        """
        return extract_regions_from_heatmap(heatmap, threshold)

    def create_bundle(
        self,
        evidence: EvidenceMap,
        threshold: float = EVIDENCE_THRESHOLD,
    ) -> OverlayBundle:
        """Create a complete overlay bundle.

        Delegates to create_overlay_bundle().

        Args:
            evidence: The evidence map.
            threshold: Threshold for region extraction.

        Returns:
            Complete OverlayBundle.
        """
        return create_overlay_bundle(evidence, threshold)

