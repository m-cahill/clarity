"""Report Data Models for CLARITY.

This module defines frozen dataclasses for report data structures.

CRITICAL CONSTRAINTS (M11):
1. All dataclasses must be frozen (immutable).
2. All floats must be rounded to 8 decimal places at construction.
3. No randomness, no datetime.now, no uuid.
4. No subprocess, no r2l imports.
5. Deterministic field ordering (alphabetical in to_dict).
6. All fields must be serializable.
7. Tuple-only for collections (no lists).

The model hierarchy:
- ReportMetadata: Cover page information
- ReportMetrics: Core metrics summary
- ReportRobustnessSurface: Surface data per axis
- ReportOverlaySection: Evidence overlay data
- ReportProbeSurface: Counterfactual probe results
- ReportSection: Generic section container
- ClarityReport: Top-level report container
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Serialization version for M11
SERIALIZATION_VERSION = "M11_v1"


def _round8(value: float) -> float:
    """Round a value to 8 decimal places.

    Args:
        value: The float value to round.

    Returns:
        The value rounded to 8 decimal places.
    """
    return round(value, 8)


@dataclass(frozen=True)
class ReportMetadata:
    """Cover page metadata for a CLARITY report.

    Attributes:
        case_id: The case identifier.
        title: Report title.
        generated_at: Timestamp from manifest (ISO format).
        clarity_version: CLARITY version string.
        r2l_sha: R2L commit SHA (if available).
        adapter_id: Adapter model identifier.
        rich_mode: Whether rich mode was enabled.
        sweep_manifest_hash: Hash of the sweep manifest.
        serialization_version: Report format version.
    """

    case_id: str
    title: str
    generated_at: str
    clarity_version: str
    r2l_sha: str
    adapter_id: str
    rich_mode: bool
    sweep_manifest_hash: str
    serialization_version: str = SERIALIZATION_VERSION

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with alphabetical key ordering.

        Returns:
            Dictionary representation of metadata.
        """
        return {
            "adapter_id": self.adapter_id,
            "case_id": self.case_id,
            "clarity_version": self.clarity_version,
            "generated_at": self.generated_at,
            "r2l_sha": self.r2l_sha,
            "rich_mode": self.rich_mode,
            "serialization_version": self.serialization_version,
            "sweep_manifest_hash": self.sweep_manifest_hash,
            "title": self.title,
        }


@dataclass(frozen=True)
class ReportMetrics:
    """Core metrics summary for a CLARITY report.

    Attributes:
        baseline_esi: Baseline ESI score.
        baseline_drift: Baseline drift score.
        global_mean_esi: Global mean ESI across all axes.
        global_mean_drift: Global mean drift across all axes.
        global_variance_esi: Global ESI variance.
        global_variance_drift: Global drift variance.
        monte_carlo_present: Whether Monte Carlo stats are present.
        monte_carlo_entropy: Monte Carlo entropy (if present).
    """

    baseline_esi: float
    baseline_drift: float
    global_mean_esi: float
    global_mean_drift: float
    global_variance_esi: float
    global_variance_drift: float
    monte_carlo_present: bool
    monte_carlo_entropy: float | None = None

    def __post_init__(self) -> None:
        """Validate and round all float fields."""
        # Use object.__setattr__ for frozen dataclass
        object.__setattr__(self, "baseline_esi", _round8(self.baseline_esi))
        object.__setattr__(self, "baseline_drift", _round8(self.baseline_drift))
        object.__setattr__(self, "global_mean_esi", _round8(self.global_mean_esi))
        object.__setattr__(self, "global_mean_drift", _round8(self.global_mean_drift))
        object.__setattr__(self, "global_variance_esi", _round8(self.global_variance_esi))
        object.__setattr__(self, "global_variance_drift", _round8(self.global_variance_drift))
        if self.monte_carlo_entropy is not None:
            object.__setattr__(
                self, "monte_carlo_entropy", _round8(self.monte_carlo_entropy)
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with alphabetical key ordering.

        Returns:
            Dictionary representation of metrics.
        """
        result: dict[str, Any] = {
            "baseline_drift": self.baseline_drift,
            "baseline_esi": self.baseline_esi,
            "global_mean_drift": self.global_mean_drift,
            "global_mean_esi": self.global_mean_esi,
            "global_variance_drift": self.global_variance_drift,
            "global_variance_esi": self.global_variance_esi,
            "monte_carlo_present": self.monte_carlo_present,
        }
        if self.monte_carlo_entropy is not None:
            result["monte_carlo_entropy"] = self.monte_carlo_entropy
        return result


@dataclass(frozen=True)
class SurfacePoint:
    """A single point on a robustness surface.

    Attributes:
        axis: The perturbation axis name.
        value: The encoded axis value.
        esi: ESI score at this point.
        drift: Drift score at this point.
    """

    axis: str
    value: str
    esi: float
    drift: float

    def __post_init__(self) -> None:
        """Round float fields."""
        object.__setattr__(self, "esi", _round8(self.esi))
        object.__setattr__(self, "drift", _round8(self.drift))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "axis": self.axis,
            "drift": self.drift,
            "esi": self.esi,
            "value": self.value,
        }


@dataclass(frozen=True)
class ReportRobustnessSurface:
    """Robustness surface data for a single axis.

    Attributes:
        axis: The perturbation axis name.
        mean_esi: Mean ESI for this axis.
        mean_drift: Mean drift for this axis.
        variance_esi: ESI variance for this axis.
        variance_drift: Drift variance for this axis.
        points: Tuple of surface points.
    """

    axis: str
    mean_esi: float
    mean_drift: float
    variance_esi: float
    variance_drift: float
    points: tuple[SurfacePoint, ...]

    def __post_init__(self) -> None:
        """Round float fields."""
        object.__setattr__(self, "mean_esi", _round8(self.mean_esi))
        object.__setattr__(self, "mean_drift", _round8(self.mean_drift))
        object.__setattr__(self, "variance_esi", _round8(self.variance_esi))
        object.__setattr__(self, "variance_drift", _round8(self.variance_drift))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
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
class OverlayRegion:
    """An evidence overlay region.

    Attributes:
        region_id: Unique region identifier.
        x_min: Left edge coordinate.
        y_min: Top edge coordinate.
        x_max: Right edge coordinate.
        y_max: Bottom edge coordinate.
        area: Region area.
        mean_evidence: Mean evidence value in region.
    """

    region_id: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    area: float
    mean_evidence: float

    def __post_init__(self) -> None:
        """Round float fields."""
        object.__setattr__(self, "x_min", _round8(self.x_min))
        object.__setattr__(self, "y_min", _round8(self.y_min))
        object.__setattr__(self, "x_max", _round8(self.x_max))
        object.__setattr__(self, "y_max", _round8(self.y_max))
        object.__setattr__(self, "area", _round8(self.area))
        object.__setattr__(self, "mean_evidence", _round8(self.mean_evidence))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "area": self.area,
            "mean_evidence": self.mean_evidence,
            "region_id": self.region_id,
            "x_max": self.x_max,
            "x_min": self.x_min,
            "y_max": self.y_max,
            "y_min": self.y_min,
        }


@dataclass(frozen=True)
class ReportOverlaySection:
    """Evidence overlay section data.

    Attributes:
        image_width: Width of the evidence image.
        image_height: Height of the evidence image.
        regions: Tuple of overlay regions.
        total_evidence_area: Total area covered by evidence regions.
    """

    image_width: int
    image_height: int
    regions: tuple[OverlayRegion, ...]
    total_evidence_area: float

    def __post_init__(self) -> None:
        """Round float fields."""
        object.__setattr__(self, "total_evidence_area", _round8(self.total_evidence_area))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "image_height": self.image_height,
            "image_width": self.image_width,
            "regions": [r.to_dict() for r in self.regions],
            "total_evidence_area": self.total_evidence_area,
        }


@dataclass(frozen=True)
class ProbeResult:
    """A single counterfactual probe result.

    Attributes:
        row: Grid row index.
        col: Grid column index.
        delta_esi: ESI change from masking.
        delta_drift: Drift change from masking.
        masked_esi: ESI after masking.
        masked_drift: Drift after masking.
    """

    row: int
    col: int
    delta_esi: float
    delta_drift: float
    masked_esi: float
    masked_drift: float

    def __post_init__(self) -> None:
        """Round float fields."""
        object.__setattr__(self, "delta_esi", _round8(self.delta_esi))
        object.__setattr__(self, "delta_drift", _round8(self.delta_drift))
        object.__setattr__(self, "masked_esi", _round8(self.masked_esi))
        object.__setattr__(self, "masked_drift", _round8(self.masked_drift))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "col": self.col,
            "delta_drift": self.delta_drift,
            "delta_esi": self.delta_esi,
            "masked_drift": self.masked_drift,
            "masked_esi": self.masked_esi,
            "row": self.row,
        }


@dataclass(frozen=True)
class ReportProbeSurface:
    """Counterfactual probe surface data.

    Attributes:
        grid_size: Size of the probe grid (k for k×k).
        total_probes: Total number of probes executed.
        mean_delta_esi: Mean ESI delta across all probes.
        mean_delta_drift: Mean drift delta across all probes.
        variance_delta_esi: Variance of ESI deltas.
        variance_delta_drift: Variance of drift deltas.
        probes: Tuple of probe results.
    """

    grid_size: int
    total_probes: int
    mean_delta_esi: float
    mean_delta_drift: float
    variance_delta_esi: float
    variance_delta_drift: float
    probes: tuple[ProbeResult, ...]

    def __post_init__(self) -> None:
        """Round float fields."""
        object.__setattr__(self, "mean_delta_esi", _round8(self.mean_delta_esi))
        object.__setattr__(self, "mean_delta_drift", _round8(self.mean_delta_drift))
        object.__setattr__(self, "variance_delta_esi", _round8(self.variance_delta_esi))
        object.__setattr__(self, "variance_delta_drift", _round8(self.variance_delta_drift))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "grid_size": self.grid_size,
            "mean_delta_drift": self.mean_delta_drift,
            "mean_delta_esi": self.mean_delta_esi,
            "probes": [p.to_dict() for p in self.probes],
            "total_probes": self.total_probes,
            "variance_delta_drift": self.variance_delta_drift,
            "variance_delta_esi": self.variance_delta_esi,
        }


@dataclass(frozen=True)
class ReportSection:
    """A generic report section.

    Attributes:
        section_id: Unique section identifier.
        title: Section title.
        content: Section content as key-value pairs.
    """

    section_id: str
    title: str
    content: tuple[tuple[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "content": {k: v for k, v in self.content},
            "section_id": self.section_id,
            "title": self.title,
        }


@dataclass(frozen=True)
class ClarityReport:
    """Top-level CLARITY report container.

    Attributes:
        metadata: Report metadata (cover page).
        metrics: Core metrics summary.
        robustness_surfaces: Tuple of robustness surface data.
        overlay_section: Evidence overlay data.
        probe_surface: Counterfactual probe results.
        reproducibility: Reproducibility block content.
    """

    metadata: ReportMetadata
    metrics: ReportMetrics
    robustness_surfaces: tuple[ReportRobustnessSurface, ...]
    overlay_section: ReportOverlaySection
    probe_surface: ReportProbeSurface
    reproducibility: ReportSection

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of the entire report.
        """
        return {
            "metadata": self.metadata.to_dict(),
            "metrics": self.metrics.to_dict(),
            "overlay_section": self.overlay_section.to_dict(),
            "probe_surface": self.probe_surface.to_dict(),
            "reproducibility": self.reproducibility.to_dict(),
            "robustness_surfaces": [s.to_dict() for s in self.robustness_surfaces],
        }

