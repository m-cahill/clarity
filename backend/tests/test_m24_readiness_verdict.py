"""M24: aggregate readiness verification — pack completeness, verdict consistency, ledger alignment."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
READINESS_DIR = REPO_ROOT / "docs" / "readiness"
CLARITY_PATH = REPO_ROOT / "docs" / "clarity.md"
LEDGER_PATH = READINESS_DIR / "READINESS_LEDGER.md"
SCORECARD_PATH = READINESS_DIR / "CLARITY_READINESS_SCORECARD.md"
CHANGE_CONTROL_PATH = READINESS_DIR / "CLARITY_CHANGE_CONTROL.md"

ALLOWED_VERDICTS = frozenset(
    {
        "READY FOR DOWNSTREAM ADOPTION",
        "CONDITIONALLY READY",
        "NOT READY",
    }
)

# End-of-M24 canonical pack files (readinessplan.md structure + M24 additions)
M24_EXPECTED_READINESS_FILES = (
    "readinessplan.md",
    "README.md",
    "READINESS_LEDGER.md",
    "READINESS_DECISIONS.md",
    "CLARITY_BOUNDARY_CONTRACT.md",
    "CLARITY_ASSUMED_GUARANTEES.md",
    "CLARITY_ARTIFACT_CONTRACT.md",
    "CLARITY_PUBLIC_SURFACE.md",
    "CLARITY_OPERATING_MANUAL.md",
    "CLARITY_IMPLEMENTATION_STATUS.md",
    "CLARITY_CONSUMER_ASSUMPTIONS.md",
    "CLARITY_COMPATIBILITY_MATRIX.md",
    "CLARITY_TRANSFER_CHECKLIST.md",
    "CLARITY_CHANGE_CONTROL.md",
    "CLARITY_READINESS_SCORECARD.md",
    "CLARITY_READINESS_REVIEW_ADDENDUM_M25.md",
)


@pytest.mark.parametrize("filename", M24_EXPECTED_READINESS_FILES)
def test_m24_all_canonical_readiness_pack_files_exist(filename: str) -> None:
    path = READINESS_DIR / filename
    rel = path.relative_to(REPO_ROOT)
    assert path.is_file(), f"expected M24 readiness file missing: {rel}"


def _extract_scorecard_verdict() -> str:
    text = SCORECARD_PATH.read_text(encoding="utf-8")
    m = re.search(r"\*\*Verdict:\*\*\s*`([^`]+)`", text)
    assert m, "scorecard must contain **Verdict:** `...` with an allowed token"
    verdict = m.group(1).strip()
    assert verdict in ALLOWED_VERDICTS, f"verdict not in allowed set: {verdict!r}"
    m_machine = re.search(
        r"\*\*M\d+_VERDICT \(machine check\):\*\*\s*`([^`]+)`",
        text,
    )
    assert m_machine, "scorecard must contain **M*_VERDICT (machine check):** line"
    assert m_machine.group(1).strip() == verdict, "machine-check verdict must match **Verdict:** line"
    return verdict


def _extract_readiness_from_ledger() -> str:
    text = LEDGER_PATH.read_text(encoding="utf-8")
    m = re.search(
        r"\|\s*\*\*Readiness\*\*\s*\|\s*\*\*`([^`]+)`\*\*\s*\|",
        text,
    )
    assert m, "ledger section 2 must contain | **Readiness** | **`...`** |"
    return m.group(1).strip()


def _extract_readiness_from_clarity_md() -> str:
    text = CLARITY_PATH.read_text(encoding="utf-8")
    m = re.search(
        r"\*\*Readiness status:\*\*\s*\*\*`([^`]+)`\*\*",
        text,
    )
    assert m, "docs/clarity.md must contain **Readiness status:** **`...`**"
    return m.group(1).strip()


def test_m24_scorecard_verdict_is_allowed_and_machine_aligned() -> None:
    _extract_scorecard_verdict()


def test_m24_ledger_clarity_scorecard_agree_on_readiness() -> None:
    v_score = _extract_scorecard_verdict()
    v_ledger = _extract_readiness_from_ledger()
    v_clarity = _extract_readiness_from_clarity_md()
    assert v_score == v_ledger == v_clarity, (
        f"verdict mismatch: scorecard={v_score!r} ledger={v_ledger!r} clarity.md={v_clarity!r}"
    )


def test_m24_change_control_names_contract_surfaces() -> None:
    text = CHANGE_CONTROL_PATH.read_text(encoding="utf-8")
    for needle in (
        "CLARITY_BOUNDARY_CONTRACT",
        "CLARITY_ARTIFACT_CONTRACT",
        "CLARITY_PUBLIC_SURFACE",
        "CLARITY_CONSUMER_ASSUMPTIONS",
        "CLARITY_COMPATIBILITY_MATRIX",
        "CLARITY_TRANSFER_CHECKLIST",
    ):
        assert needle in text, f"CLARITY_CHANGE_CONTROL.md must reference {needle}"


def test_m24_conditional_verdict_lists_conditions() -> None:
    verdict = _extract_scorecard_verdict()
    text = SCORECARD_PATH.read_text(encoding="utf-8")
    if verdict in ("CONDITIONALLY READY", "NOT READY"):
        assert re.search(
            r"##\s+9\.\s+Conditions and next actions",
            text,
        ), "conditional or negative verdict requires ## 9. Conditions and next actions"
        assert "C-M24-001" in text and "C-M24-002" in text and "C-M24-003" in text, (
            "expected C-M24-001..003 condition IDs in scorecard"
        )
    else:
        assert verdict == "READY FOR DOWNSTREAM ADOPTION"


def test_m24_ledger_records_final_verdict_section() -> None:
    text = LEDGER_PATH.read_text(encoding="utf-8")
    assert "## 7. Final verdict" in text
    v = _extract_scorecard_verdict()
    assert v in text, f"ledger §7 must echo scorecard verdict {v!r}"
