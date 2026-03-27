"""M25: re-readiness verification — manifest identity, plan authority, verdict sync."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.clarity.manifest_schema_family import (
    FAMILY_RICH_AGGREGATE_V1,
    FAMILY_SWEEP_ORCHESTRATOR_V1,
    MANIFEST_SCHEMA_FAMILY,
    parse_manifest_schema_family,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CLARITY_PATH = REPO_ROOT / "docs" / "clarity.md"
READINESS_DIR = REPO_ROOT / "docs" / "readiness"
LEDGER_PATH = READINESS_DIR / "READINESS_LEDGER.md"
SCORECARD_PATH = READINESS_DIR / "CLARITY_READINESS_SCORECARD.md"
ADDENDUM_PATH = READINESS_DIR / "CLARITY_READINESS_REVIEW_ADDENDUM_M25.md"
ROOT_PLAN_STUB_PATH = REPO_ROOT / "docs" / "readinessplan.md"
CANONICAL_PLAN_PATH = READINESS_DIR / "readinessplan.md"
M15_MANIFEST = (
    REPO_ROOT
    / "backend"
    / "tests"
    / "fixtures"
    / "baselines"
    / "m15_real_ui"
    / "sweep_manifest.json"
)

READY_VERDICT = "READY FOR DOWNSTREAM ADOPTION"


def _extract_verdict_from_scorecard() -> str:
    text = SCORECARD_PATH.read_text(encoding="utf-8")
    m = re.search(r"\*\*Verdict:\*\*\s*`([^`]+)`", text)
    assert m, "scorecard must contain **Verdict:** `...`"
    return m.group(1).strip()


def _extract_readiness_status_clarity_md() -> str:
    text = CLARITY_PATH.read_text(encoding="utf-8")
    m = re.search(r"\*\*Readiness status:\*\*\s*\*\*`([^`]+)`\*\*", text)
    assert m, "docs/clarity.md must contain **Readiness status:** **`...`**"
    return m.group(1).strip()


def _extract_ledger_readiness_cell() -> str:
    text = LEDGER_PATH.read_text(encoding="utf-8")
    m = re.search(
        r"\|\s*\*\*Readiness\*\*\s*\|\s*\*\*`([^`]+)`\*\*\s*\|",
        text,
    )
    assert m, "ledger §2 must contain | **Readiness** | **`...`** |"
    return m.group(1).strip()


def test_m25_verdict_tokens_aligned_across_canonical_docs() -> None:
    v_score = _extract_verdict_from_scorecard()
    v_clarity = _extract_readiness_status_clarity_md()
    v_ledger = _extract_ledger_readiness_cell()
    assert v_score == v_clarity == v_ledger == READY_VERDICT, (
        f"verdict mismatch: scorecard={v_score!r} clarity={v_clarity!r} ledger={v_ledger!r}"
    )


def test_m25_addendum_documents_supersession() -> None:
    text = ADDENDUM_PATH.read_text(encoding="utf-8")
    assert "C-M24-001" in text
    assert READY_VERDICT in text


def test_m25_m15_fixture_manifest_is_self_identifying() -> None:
    import json

    data = json.loads(M15_MANIFEST.read_text(encoding="utf-8"))
    assert data.get(MANIFEST_SCHEMA_FAMILY) == FAMILY_RICH_AGGREGATE_V1
    assert parse_manifest_schema_family(data) == FAMILY_RICH_AGGREGATE_V1


def test_m25_root_readiness_plan_is_stub_not_duplicate_canonical_body() -> None:
    stub = ROOT_PLAN_STUB_PATH.read_text(encoding="utf-8")
    canonical = CANONICAL_PLAN_PATH.read_text(encoding="utf-8")
    assert len(stub) < len(canonical) // 4, "root readiness plan must stay a short redirect stub"
    assert "redirect" in stub.lower() or "canonical" in stub.lower()
    assert "# CLARITY Readiness Plan (M18–M24)" not in stub[:800]


def test_m25_canonical_readiness_plan_path_documented() -> None:
    """Consumers are pointed at one authoritative path (C-M24-003 cleared)."""
    combo = CLARITY_PATH.read_text(encoding="utf-8") + LEDGER_PATH.read_text(encoding="utf-8")
    assert "docs/readiness/readinessplan.md" in combo


def test_m25_scorecard_lists_cleared_m24_conditions_for_audit() -> None:
    text = SCORECARD_PATH.read_text(encoding="utf-8")
    assert "C-M24-001" in text and "C-M24-002" in text and "C-M24-003" in text
    assert _extract_verdict_from_scorecard() == READY_VERDICT


def test_m25_machine_verdict_line_matches_explicit_verdict() -> None:
    text = SCORECARD_PATH.read_text(encoding="utf-8")
    v = _extract_verdict_from_scorecard()
    m = re.search(r"\*\*M25_VERDICT \(machine check\):\*\*\s*`([^`]+)`", text)
    assert m, "scorecard must contain **M25_VERDICT (machine check):**"
    assert m.group(1).strip() == v


@pytest.mark.parametrize(
    "token",
    [FAMILY_SWEEP_ORCHESTRATOR_V1, FAMILY_RICH_AGGREGATE_V1],
)
def test_m25_known_family_tokens_documented_in_artifact_contract(token: str) -> None:
    contract = (READINESS_DIR / "CLARITY_ARTIFACT_CONTRACT.md").read_text(encoding="utf-8")
    assert token in contract
