"""M23: supported-combination truth table guardrails (readiness pack)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
READINESS_DIR = REPO_ROOT / "docs" / "readiness"
MATRIX_PATH = READINESS_DIR / "CLARITY_COMPATIBILITY_MATRIX.md"
ASSUMPTIONS_PATH = READINESS_DIR / "CLARITY_CONSUMER_ASSUMPTIONS.md"
CHECKLIST_PATH = READINESS_DIR / "CLARITY_TRANSFER_CHECKLIST.md"
PUBLIC_SURFACE_MODULE = "app.clarity.public_surface"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "path",
    [
        MATRIX_PATH,
        ASSUMPTIONS_PATH,
        CHECKLIST_PATH,
    ],
)
def test_m23_pack_documents_exist(path: Path) -> None:
    """Readiness pack lists these files; assert presence."""
    assert path.is_file(), f"expected M23 readiness file: {path.relative_to(REPO_ROOT)}"


def test_compatibility_matrix_names_public_surface_consistently() -> None:
    """Must align with M21 frozen module string."""
    text = _read(MATRIX_PATH)
    assert PUBLIC_SURFACE_MODULE in text
    assert "PUBLIC_SURFACE" in text or "public_surface" in text


def test_m23_docs_do_not_bless_http_as_readiness_canonical() -> None:
    """HTTP must remain non-canonical for readiness (M21)."""
    for path in (MATRIX_PATH, ASSUMPTIONS_PATH, CHECKLIST_PATH):
        text = _read(path)
        lower = text.lower()
        assert "non-canonical" in lower or ("not" in lower and "canonical" in lower)
        # If the doc uses the phrase "readiness-canonical", it must be explicitly negated
        # ("not readiness-canonical" contains the substring — positive blessing is forbidden).
        for match in re.finditer(r"(?i)readiness[- ]canonical", text):
            prefix = text[max(0, match.start() - 48) : match.start()].lower()
            assert "not" in prefix, (
                f"{path.name}: 'readiness-canonical' must follow a negation (M21 HTTP posture)"
            )


def test_compatibility_matrix_does_not_equate_orchestrator_with_full_bundle() -> None:
    """Orchestrator-only must not be presented as full-bundle support."""
    text = _read(MATRIX_PATH)
    lower = text.lower()
    assert "orchestrator" in lower and "full bundle" in lower
    assert "not" in lower or "without" in lower or "alone" in lower


def test_compatibility_matrix_status_vocabulary() -> None:
    """Controlled honesty vocabulary for combination rows."""
    text = _read(MATRIX_PATH)
    for word in ("**Supported**", "**Unsupported**", "**Unknown**"):
        assert word in text, f"missing status token: {word}"


def test_supported_rows_have_evidence_column() -> None:
    """Each Supported row must have a non-empty Evidence cell (table §4)."""
    text = _read(MATRIX_PATH)
    lines = text.splitlines()
    in_table = False
    for line in lines:
        if line.startswith("| ID |"):
            in_table = True
            continue
        if line.startswith("## 5."):
            break
        if not in_table or not line.startswith("|"):
            continue
        if "| **Supported** |" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        # Table: | ID | Invocation | Mode | Output | Context | Status | Evidence | Notes | Owner |
        if len(parts) < 10:
            pytest.fail(f"unexpected table row shape: {line!r}")
        status = parts[6]
        evidence = parts[7]
        assert "**Supported**" in status
        assert evidence, f"Supported row missing evidence: {line!r}"
        assert len(evidence) > 3, f"evidence too thin: {line!r}"


def test_assumptions_cross_link_matrix_and_checklist() -> None:
    text = _read(ASSUMPTIONS_PATH)
    assert "CLARITY_COMPATIBILITY_MATRIX.md" in text
    assert "CLARITY_TRANSFER_CHECKLIST.md" in text


def test_checklist_cross_links_matrix() -> None:
    text = _read(CHECKLIST_PATH)
    assert "CLARITY_COMPATIBILITY_MATRIX.md" in text
    assert "CLARITY_CONSUMER_ASSUMPTIONS.md" in text


def test_compatibility_matrix_includes_http_non_canonical_wording() -> None:
    text = _read(MATRIX_PATH)
    assert re.search(r"(?i)http.*non-canonical|non-canonical.*http", text)
