"""Report API Router for CLARITY.

This module provides the FastAPI router for PDF report generation.

CRITICAL CONSTRAINTS (M11):
1. All responses must be deterministic.
2. No randomness, no datetime.now, no uuid.
3. No subprocess, no r2l imports.
4. Only supports demo cases in M11.
5. Streams PDF bytes directly.

M12 ADDITIONS:
- Deterministic caching with SHA256 keys
- Atomic writes for cache safety
- File locking for concurrency control
- 409 response for concurrent identical requests

Endpoints:
- POST /report/generate - Generate a PDF report for a case
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.clarity.cache import CacheManager, compute_case_hash
from app.clarity.cache.cache_manager import CacheInProgressError

logger = logging.getLogger(__name__)

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
from app.clarity.report.report_renderer import render_report_to_pdf


router = APIRouter(prefix="/report", tags=["report"])

# Path to demo artifacts (relative to backend directory)
DEMO_ARTIFACTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "demo_artifacts"

# Fixed fallback timestamp
FALLBACK_TIMESTAMP = "1970-01-01T00:00:00Z"

# Global cache manager instance (M12)
_cache_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """Get or create the global cache manager.

    Returns:
        CacheManager instance.
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


class ReportGenerateRequest(BaseModel):
    """Request body for report generation endpoint.

    Attributes:
        case_id: The case ID to generate a report for.
    """

    case_id: str = Field(
        ...,
        description="The case ID to generate a report for",
        min_length=1,
        max_length=255,
    )


class ReportGenerateError(Exception):
    """Error raised during report generation."""

    pass


def _load_json_file(path: Path) -> dict[str, Any]:
    """Load and parse a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON as dictionary.

    Raises:
        ReportGenerateError: If file not found or invalid JSON.
    """
    if not path.exists():
        raise ReportGenerateError(f"File not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ReportGenerateError(f"Invalid JSON in {path}: {e}") from e


def _get_timestamp(manifest: dict[str, Any]) -> str:
    """Extract timestamp from manifest with fallback.

    Precedence:
    1. manifest["created_at"]
    2. manifest["timestamp"]
    3. manifest["generated_at"]
    4. FALLBACK_TIMESTAMP

    Args:
        manifest: The manifest dictionary.

    Returns:
        ISO format timestamp string.
    """
    for field in ["created_at", "timestamp", "generated_at"]:
        if field in manifest and manifest[field]:
            return str(manifest[field])
    return FALLBACK_TIMESTAMP


def _compute_manifest_hash(manifest: dict[str, Any]) -> str:
    """Compute a deterministic hash of the manifest.

    Args:
        manifest: The manifest dictionary.

    Returns:
        SHA256 hash hex string.
    """
    # Sort keys for determinism
    json_str = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


def _build_report_from_artifacts(
    case_id: str,
    manifest: dict[str, Any],
    robustness: dict[str, Any],
    overlay: dict[str, Any],
    metrics: dict[str, Any],
) -> ClarityReport:
    """Build a ClarityReport from demo artifact data.

    Args:
        case_id: The case identifier.
        manifest: Parsed manifest.json data.
        robustness: Parsed robustness_surface.json data.
        overlay: Parsed overlay_bundle.json data.
        metrics: Parsed metrics.json data.

    Returns:
        ClarityReport instance.
    """
    # Build metadata
    metadata = ReportMetadata(
        case_id=case_id,
        title=manifest.get("title", "CLARITY Report"),
        generated_at=_get_timestamp(manifest),
        clarity_version=manifest.get("clarity_version", "unknown"),
        r2l_sha=manifest.get("r2l_sha", "N/A"),
        adapter_id=manifest.get("baseline_id", "unknown"),
        rich_mode=manifest.get("config", {}).get("rich_mode", False),
        sweep_manifest_hash=_compute_manifest_hash(manifest),
        serialization_version=SERIALIZATION_VERSION,
    )

    # Build metrics
    baseline_metrics = metrics.get("baseline_metrics", {})
    report_metrics = ReportMetrics(
        baseline_esi=baseline_metrics.get("esi", 0.0),
        baseline_drift=baseline_metrics.get("drift", 0.0),
        global_mean_esi=robustness.get("global_mean_esi", 0.0),
        global_mean_drift=robustness.get("global_mean_drift", 0.0),
        global_variance_esi=robustness.get("global_variance_esi", 0.0),
        global_variance_drift=robustness.get("global_variance_drift", 0.0),
        monte_carlo_present=False,
        monte_carlo_entropy=None,
    )

    # Build robustness surfaces
    surfaces: list[ReportRobustnessSurface] = []
    for axis_data in sorted(robustness.get("axes", []), key=lambda a: a.get("axis", "")):
        points: list[SurfacePoint] = []
        for point_data in sorted(
            axis_data.get("points", []), key=lambda p: p.get("value", "")
        ):
            points.append(SurfacePoint(
                axis=point_data.get("axis", ""),
                value=point_data.get("value", ""),
                esi=point_data.get("esi", 0.0),
                drift=point_data.get("drift", 0.0),
            ))

        surfaces.append(ReportRobustnessSurface(
            axis=axis_data.get("axis", ""),
            mean_esi=axis_data.get("mean_esi", 0.0),
            mean_drift=axis_data.get("mean_drift", 0.0),
            variance_esi=axis_data.get("variance_esi", 0.0),
            variance_drift=axis_data.get("variance_drift", 0.0),
            points=tuple(points),
        ))

    # Build overlay section
    overlay_regions: list[OverlayRegion] = []
    total_area = 0.0
    image_dims = manifest.get("image_dimensions", {})
    image_width = image_dims.get("width", 224)
    image_height = image_dims.get("height", 224)
    total_pixels = image_width * image_height

    for region_data in sorted(
        overlay.get("regions", []), key=lambda r: r.get("region_id", "")
    ):
        area = region_data.get("area", 0.0)
        # Normalize area if it's in pixels
        if isinstance(area, int) or area > 1.0:
            area = area / total_pixels
        total_area += area

        overlay_regions.append(OverlayRegion(
            region_id=region_data.get("region_id", ""),
            x_min=region_data.get("x_min", 0.0) / image_width if region_data.get("x_min", 0) > 1 else region_data.get("x_min", 0.0),
            y_min=region_data.get("y_min", 0.0) / image_height if region_data.get("y_min", 0) > 1 else region_data.get("y_min", 0.0),
            x_max=region_data.get("x_max", 0.0) / image_width if region_data.get("x_max", 0) > 1 else region_data.get("x_max", 0.0),
            y_max=region_data.get("y_max", 0.0) / image_height if region_data.get("y_max", 0) > 1 else region_data.get("y_max", 0.0),
            area=area,
            mean_evidence=region_data.get("mean_evidence", 0.0),
        ))

    overlay_section = ReportOverlaySection(
        image_width=image_width,
        image_height=image_height,
        regions=tuple(overlay_regions),
        total_evidence_area=total_area,
    )

    # Build probe surface
    probe_surface_data = metrics.get("probe_surface", {})
    probes: list[ProbeResult] = []
    for probe_data in sorted(
        probe_surface_data.get("probes", []),
        key=lambda p: (p.get("row", 0), p.get("col", 0)),
    ):
        probes.append(ProbeResult(
            row=probe_data.get("row", 0),
            col=probe_data.get("col", 0),
            delta_esi=probe_data.get("delta_esi", 0.0),
            delta_drift=probe_data.get("delta_drift", 0.0),
            masked_esi=probe_data.get("masked_esi", 0.0),
            masked_drift=probe_data.get("masked_drift", 0.0),
        ))

    probe_surface = ReportProbeSurface(
        grid_size=probe_surface_data.get("grid_size", 4),
        total_probes=probe_surface_data.get("total_probes", len(probes)),
        mean_delta_esi=probe_surface_data.get("mean_delta_esi", 0.0),
        mean_delta_drift=probe_surface_data.get("mean_delta_drift", 0.0),
        variance_delta_esi=probe_surface_data.get("variance_delta_esi", 0.0),
        variance_delta_drift=probe_surface_data.get("variance_delta_drift", 0.0),
        probes=tuple(probes),
    )

    # Build reproducibility block
    config = manifest.get("config", {})
    perturbation_axes = config.get("perturbation_axes", [])
    reproducibility = ReportSection(
        section_id="reproducibility",
        title="Reproducibility Block",
        content=(
            ("Case ID", case_id),
            ("CLARITY Version", metadata.clarity_version),
            ("R2L SHA", metadata.r2l_sha),
            ("Adapter Model", metadata.adapter_id),
            ("Rich Mode", "true" if metadata.rich_mode else "false"),
            ("Perturbation Axes", ", ".join(sorted(perturbation_axes))),
            ("Grid Size", str(config.get("grid_size", "N/A"))),
            ("Serialization Version", SERIALIZATION_VERSION),
            ("Manifest Hash", metadata.sweep_manifest_hash),
        ),
    )

    return ClarityReport(
        metadata=metadata,
        metrics=report_metrics,
        robustness_surfaces=tuple(surfaces),
        overlay_section=overlay_section,
        probe_surface=probe_surface,
        reproducibility=reproducibility,
    )


def load_demo_case(case_id: str) -> ClarityReport:
    """Load a demo case and build a ClarityReport.

    Args:
        case_id: The case identifier (e.g., "case_001").

    Returns:
        ClarityReport built from demo artifacts.

    Raises:
        ReportGenerateError: If case not found or data invalid.
    """
    case_dir = DEMO_ARTIFACTS_DIR / case_id

    if not case_dir.exists():
        raise ReportGenerateError(f"Case not found: {case_id}")

    # Load all artifact files
    manifest = _load_json_file(case_dir / "manifest.json")
    robustness = _load_json_file(case_dir / "robustness_surface.json")
    overlay = _load_json_file(case_dir / "overlay_bundle.json")
    metrics = _load_json_file(case_dir / "metrics.json")

    return _build_report_from_artifacts(
        case_id, manifest, robustness, overlay, metrics
    )


@router.post("/generate")
def generate_report(request: ReportGenerateRequest) -> Response:
    """Generate a PDF report for a case.

    This endpoint loads demo case artifacts, builds a ClarityReport,
    and renders it to a deterministic PDF.

    M12: Added caching and concurrency control.
    - Cache hit: Returns cached PDF immediately
    - Cache miss: Generates, caches, and returns PDF
    - Concurrent request: Returns 409 if another request is generating

    Args:
        request: The report generation request.

    Returns:
        PDF file as application/pdf response.

    Raises:
        HTTPException: If case not found, generation fails, or concurrent request.
    """
    case_dir = DEMO_ARTIFACTS_DIR / request.case_id

    if not case_dir.exists():
        raise HTTPException(status_code=404, detail=f"Case not found: {request.case_id}")

    try:
        # Compute cache key from case artifacts (M12)
        cache_key = compute_case_hash(case_dir)
        cache = get_cache_manager()

        def generate_pdf() -> bytes:
            """Generate PDF for caching."""
            logger.info(f"Generating report for case: {request.case_id}")
            report = load_demo_case(request.case_id)
            return render_report_to_pdf(report)

        # Get from cache or generate (M12)
        pdf_bytes = cache.get_or_create(
            cache_key=cache_key,
            generator=generate_pdf,
            extension=".pdf",
        )

        logger.debug(f"Report served for case: {request.case_id}, cache_key: {cache_key[:16]}...")

        # Return as PDF response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="clarity_report_{request.case_id}.pdf"',
                "X-Cache-Key": cache_key[:16],  # Partial key for debugging
            },
        )

    except CacheInProgressError as e:
        # Another request is generating the same report (M12)
        logger.warning(f"Concurrent report generation blocked: {request.case_id}")
        raise HTTPException(
            status_code=409,
            detail=f"Report generation in progress for case: {request.case_id}",
        ) from e

    except ReportGenerateError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    except Exception as e:
        logger.exception(f"Report generation failed for case: {request.case_id}")
        raise HTTPException(
            status_code=500, detail=f"Report generation failed: {e}"
        ) from e


@router.get("/cases")
def list_report_cases() -> dict[str, list[str]]:
    """List available cases for report generation.

    Returns:
        Dictionary with list of available case IDs.
    """
    cases: list[str] = []

    if DEMO_ARTIFACTS_DIR.exists():
        for case_dir in sorted(DEMO_ARTIFACTS_DIR.iterdir()):
            if case_dir.is_dir() and (case_dir / "manifest.json").exists():
                cases.append(case_dir.name)

    return {"cases": cases}

