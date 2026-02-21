"""CLARITY Report Module.

This module provides deterministic PDF report generation for CLARITY.

M11 introduces audit-grade PDF reports that are:
- Deterministic (identical inputs → identical SHA256)
- Self-contained (no external dependencies at render time)
- Reproducible (includes full provenance metadata)

Components:
- report_model.py: Frozen dataclasses for report data
- image_renderer.py: Deterministic PNG generation
- report_renderer.py: ReportLab-based PDF rendering
- report_router.py: FastAPI router for report endpoint
"""

from app.clarity.report.report_model import (
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
from app.clarity.report.report_renderer import ReportRenderer, render_report_to_pdf
from app.clarity.report.report_router import router as report_router

__all__ = [
    "ClarityReport",
    "OverlayRegion",
    "ProbeResult",
    "ReportMetadata",
    "ReportMetrics",
    "ReportOverlaySection",
    "ReportProbeSurface",
    "ReportRenderer",
    "ReportRobustnessSurface",
    "ReportSection",
    "SurfacePoint",
    "render_report_to_pdf",
    "report_router",
]

