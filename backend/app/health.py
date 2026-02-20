"""Health and version endpoints for CLARITY backend.

These endpoints provide basic service health information and version details.
They are designed to produce deterministic JSON output for E2E verification.
"""

from typing import Optional

from pydantic import BaseModel

from backend.app import __version__


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""

    status: str
    service: str
    version: str


class VersionResponse(BaseModel):
    """Response model for /version endpoint."""

    version: str
    git_sha: Optional[str]


def get_health() -> HealthResponse:
    """Get service health status.

    Returns:
        HealthResponse with status, service name, and version.
    """
    return HealthResponse(
        status="ok",
        service="clarity-backend",
        version=__version__,
    )


def get_version() -> VersionResponse:
    """Get service version information.

    Returns:
        VersionResponse with version and git SHA (if available).
    """
    # Git SHA injection placeholder - will be set at build time in future
    return VersionResponse(
        version=__version__,
        git_sha=None,
    )

