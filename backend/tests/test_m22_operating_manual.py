"""M22: operating manual and implementation-status matrix guardrails."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.clarity.public_surface import PUBLIC_SURFACE_SYMBOLS

REPO_ROOT = Path(__file__).resolve().parents[2]
READINESS_DIR = REPO_ROOT / "docs" / "readiness"
MANUAL_PATH = READINESS_DIR / "CLARITY_OPERATING_MANUAL.md"
STATUS_PATH = READINESS_DIR / "CLARITY_IMPLEMENTATION_STATUS.md"
PUBLIC_SURFACE_DOC = READINESS_DIR / "CLARITY_PUBLIC_SURFACE.md"

# Must stay aligned with test_public_surface_contract.py::test_public_surface_export_snapshot
_EXPECTED_PUBLIC_SYMBOLS = frozenset(
    {
        "OutputDirectoryExistsError",
        "R2LInvocationError",
        "R2LRunner",
        "R2LRunResult",
        "R2LTimeoutError",
        "SweepAxis",
        "SweepConfig",
        "SweepConfigValidationError",
        "SweepExecutionError",
        "SweepOrchestrator",
        "SweepResult",
        "SweepRunRecord",
        "build_run_directory_name",
        "encode_axis_value",
    }
)


def test_public_surface_symbols_match_m21_freeze() -> None:
    """Manual consistency: code export set matches M21 contract tests."""
    assert PUBLIC_SURFACE_SYMBOLS == _EXPECTED_PUBLIC_SYMBOLS


def test_operating_manual_exists_and_references_public_surface_doc() -> None:
    text = MANUAL_PATH.read_text(encoding="utf-8")
    assert "CLARITY_PUBLIC_SURFACE.md" in text
    assert "app.clarity.public_surface" in text


def test_operating_manual_states_http_non_canonical_for_readiness() -> None:
    """Must not present HTTP API as the portability contract (M21)."""
    text = MANUAL_PATH.read_text(encoding="utf-8").lower()
    assert "non-canonical" in text
    assert "http" in text


def test_operating_manual_does_not_promote_package_root_as_canonical() -> None:
    """Discourage treating app.clarity root as the contract (M21)."""
    text = MANUAL_PATH.read_text(encoding="utf-8")
    assert "app.clarity.public_surface" in text
    # Manual should warn that package root is not the portability contract
    lower = text.lower()
    assert "not" in lower and "canonical" in lower


def test_implementation_status_public_surface_row() -> None:
    """M21 audit: public surface row Implemented + owner CLARITY_PUBLIC_SURFACE.md."""
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert re.search(
        r"Public invocation surface.*?Implemented.*CLARITY_PUBLIC_SURFACE\.md",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    ), "expected Matrix A row: public surface Implemented with CLARITY_PUBLIC_SURFACE.md owner"


def test_implementation_status_portability_not_claimed_implemented() -> None:
    """M22 does not claim M24 verdict."""
    text = STATUS_PATH.read_text(encoding="utf-8")
    # Scorecard row should be Planned, not Implemented as final verdict
    assert "NOT READY" in text or "Planned" in text


def test_no_placeholder_sections_as_current_behavior() -> None:
    """Guardrail: no obvious placeholder tokens in shipped M22 docs."""
    for path in (MANUAL_PATH, STATUS_PATH):
        text = path.read_text(encoding="utf-8")
        assert "TODO:" not in text
        assert "PLACEHOLDER" not in text.upper()
        assert "[TBD]" not in text


def test_readiness_pack_documents_reference_each_other() -> None:
    """Lightweight reference sanity: manual points to implementation status."""
    manual = MANUAL_PATH.read_text(encoding="utf-8")
    assert "CLARITY_IMPLEMENTATION_STATUS.md" in manual


def test_frozen_public_surface_doc_lists_same_symbols_as_code() -> None:
    """Cross-check: CLARITY_PUBLIC_SURFACE.md symbol table matches code exports."""
    doc = PUBLIC_SURFACE_DOC.read_text(encoding="utf-8")
    for name in sorted(PUBLIC_SURFACE_SYMBOLS):
        assert re.search(rf"\b{re.escape(name)}\b", doc), f"missing symbol in contract doc: {name}"
