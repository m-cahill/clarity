"""Demo Router for CLARITY.

This module provides read-only endpoints for serving precomputed demo artifacts.
It is activated when APP_ENV=demo and serves synthetic data for demonstration.

CRITICAL CONSTRAINTS (M10.5):
1. Read-only access to artifacts - no writes.
2. No R2L imports.
3. No subprocess.
4. No artifact generation.
5. Path traversal protection.
6. CORS restricted to ALLOWED_ORIGIN when set.
7. Deterministic responses.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Router prefix for demo endpoints
router = APIRouter(prefix="/demo", tags=["demo"])


def _get_artifact_root() -> str:
    """Get artifact root from environment (allows runtime override)."""
    return os.environ.get("ARTIFACT_ROOT", "demo_artifacts")


def _get_app_env() -> str:
    """Get app environment from environment (allows runtime override)."""
    return os.environ.get("APP_ENV", "development")


class CaseInfo(BaseModel):
    """Summary information about a demo case."""

    case_id: str
    title: str
    description: str
    synthetic: bool


class CaseListResponse(BaseModel):
    """Response for listing available cases."""

    cases: list[CaseInfo]
    total: int


class ArtifactResponse(BaseModel):
    """Generic artifact response wrapper."""

    case_id: str
    artifact_type: str
    data: dict[str, Any]
    synthetic: bool


class DemoHealthResponse(BaseModel):
    """Health response for demo mode."""

    status: str
    mode: str
    artifact_root: str
    cases_available: int


# Regex pattern for valid case IDs (alphanumeric + underscore only)
VALID_CASE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


def _get_artifact_path() -> Path:
    """Get the artifact root path.

    Returns:
        Path to artifact directory.

    Raises:
        HTTPException: If artifact root doesn't exist.
    """
    artifact_root = _get_artifact_root()
    
    # Support both absolute and relative paths
    if os.path.isabs(artifact_root):
        artifact_path = Path(artifact_root)
    else:
        # Relative to backend directory
        artifact_path = Path(__file__).parent.parent.parent / artifact_root

    if not artifact_path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Artifact directory not found: {artifact_root}",
        )

    return artifact_path


def _validate_case_id(case_id: str) -> None:
    """Validate case ID to prevent path traversal.

    Args:
        case_id: The case ID to validate.

    Raises:
        HTTPException: If case ID is invalid.
    """
    if not VALID_CASE_ID_PATTERN.match(case_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid case ID format: {case_id}",
        )

    # Additional path traversal protection
    if ".." in case_id or "/" in case_id or "\\" in case_id:
        raise HTTPException(
            status_code=400,
            detail="Path traversal detected",
        )


def _load_json_artifact(case_id: str, filename: str) -> dict[str, Any]:
    """Load a JSON artifact for a case.

    Args:
        case_id: The case identifier.
        filename: The artifact filename.

    Returns:
        Parsed JSON data.

    Raises:
        HTTPException: If artifact not found or invalid.
    """
    _validate_case_id(case_id)

    artifact_path = _get_artifact_path() / case_id / filename

    # Verify path is within artifact root (defense in depth)
    try:
        artifact_path = artifact_path.resolve()
        artifact_root = _get_artifact_path().resolve()
        if not str(artifact_path).startswith(str(artifact_root)):
            raise HTTPException(
                status_code=400,
                detail="Path traversal detected",
            )
    except (ValueError, RuntimeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid path",
        )

    if not artifact_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Artifact not found: {case_id}/{filename}",
        )

    try:
        with open(artifact_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in artifact {artifact_path}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Invalid artifact format: {filename}",
        )


def _list_cases() -> list[CaseInfo]:
    """List all available demo cases.

    Returns:
        List of CaseInfo objects.
    """
    artifact_path = _get_artifact_path()
    cases: list[CaseInfo] = []

    for case_dir in sorted(artifact_path.iterdir()):
        if not case_dir.is_dir():
            continue

        manifest_path = case_dir / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)

            cases.append(
                CaseInfo(
                    case_id=manifest.get("case_id", case_dir.name),
                    title=manifest.get("title", "Untitled"),
                    description=manifest.get("description", ""),
                    synthetic=manifest.get("synthetic", True),
                )
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Skipping invalid case {case_dir.name}: {e}")
            continue

    return cases


@router.get("/health", response_model=DemoHealthResponse)
def demo_health() -> DemoHealthResponse:
    """Demo mode health check.

    Returns status and artifact availability.
    """
    try:
        cases = _list_cases()
        cases_count = len(cases)
    except HTTPException:
        cases_count = 0

    app_env = _get_app_env()
    artifact_root = _get_artifact_root()
    
    return DemoHealthResponse(
        status="ok",
        mode="demo" if app_env == "demo" else app_env,
        artifact_root=artifact_root,
        cases_available=cases_count,
    )


@router.get("/cases", response_model=CaseListResponse)
def list_cases() -> CaseListResponse:
    """List available demo cases.

    Returns all cases with manifest information.
    """
    cases = _list_cases()
    return CaseListResponse(
        cases=cases,
        total=len(cases),
    )


@router.get("/cases/{case_id}/manifest", response_model=ArtifactResponse)
def get_manifest(case_id: str) -> ArtifactResponse:
    """Get case manifest.

    Args:
        case_id: The case identifier.

    Returns:
        Manifest data wrapped in ArtifactResponse.
    """
    data = _load_json_artifact(case_id, "manifest.json")
    return ArtifactResponse(
        case_id=case_id,
        artifact_type="manifest",
        data=data,
        synthetic=data.get("synthetic", True),
    )


@router.get("/cases/{case_id}/surface", response_model=ArtifactResponse)
def get_surface(case_id: str) -> ArtifactResponse:
    """Get robustness surface data.

    Args:
        case_id: The case identifier.

    Returns:
        Surface data wrapped in ArtifactResponse.
    """
    data = _load_json_artifact(case_id, "robustness_surface.json")
    return ArtifactResponse(
        case_id=case_id,
        artifact_type="robustness_surface",
        data=data,
        synthetic=data.get("_synthetic", True),
    )


@router.get("/cases/{case_id}/overlay", response_model=ArtifactResponse)
def get_overlay(case_id: str) -> ArtifactResponse:
    """Get overlay bundle data.

    Args:
        case_id: The case identifier.

    Returns:
        Overlay bundle data wrapped in ArtifactResponse.
    """
    data = _load_json_artifact(case_id, "overlay_bundle.json")
    return ArtifactResponse(
        case_id=case_id,
        artifact_type="overlay_bundle",
        data=data,
        synthetic=data.get("_synthetic", True),
    )


@router.get("/cases/{case_id}/metrics", response_model=ArtifactResponse)
def get_metrics(case_id: str) -> ArtifactResponse:
    """Get probe metrics data.

    Args:
        case_id: The case identifier.

    Returns:
        Metrics data wrapped in ArtifactResponse.
    """
    data = _load_json_artifact(case_id, "metrics.json")
    return ArtifactResponse(
        case_id=case_id,
        artifact_type="metrics",
        data=data,
        synthetic=data.get("_synthetic", True),
    )


@router.get("/cases/{case_id}/checksums")
def get_checksums(case_id: str) -> dict[str, Any]:
    """Get artifact checksums.

    Args:
        case_id: The case identifier.

    Returns:
        Checksums data.
    """
    return _load_json_artifact(case_id, "checksums.json")


def verify_artifact_integrity(case_id: str) -> dict[str, bool]:
    """Verify artifact integrity against checksums.

    Args:
        case_id: The case identifier.

    Returns:
        Dictionary mapping filename to integrity status.
    """
    _validate_case_id(case_id)
    checksums = _load_json_artifact(case_id, "checksums.json")

    results: dict[str, bool] = {}
    artifact_path = _get_artifact_path() / case_id

    for filename, expected_hash in checksums.get("files", {}).items():
        file_path = artifact_path / filename
        if not file_path.exists():
            results[filename] = False
            continue

        # Compute actual hash (normalize line endings for cross-platform)
        content = file_path.read_bytes()
        # Normalize CRLF to LF for consistent hashing across platforms
        content_normalized = content.replace(b"\r\n", b"\n")
        actual_hash = hashlib.sha256(content_normalized).hexdigest().upper()
        results[filename] = actual_hash == expected_hash.upper()

    return results


@router.get("/cases/{case_id}/verify")
def verify_case(case_id: str) -> dict[str, Any]:
    """Verify case artifact integrity.

    Args:
        case_id: The case identifier.

    Returns:
        Verification results with pass/fail for each artifact.
    """
    results = verify_artifact_integrity(case_id)
    all_valid = all(results.values()) if results else False

    return {
        "case_id": case_id,
        "valid": all_valid,
        "files": results,
    }

