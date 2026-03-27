"""M18: readiness-pack guardrail — core files exist; README links resolve."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
READINESS_DIR = REPO_ROOT / "docs" / "readiness"
README_PATH = READINESS_DIR / "README.md"

REQUIRED_FILES = (
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
)


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_readiness_pack_required_files_exist(filename: str) -> None:
    path = READINESS_DIR / filename
    rel = path.relative_to(REPO_ROOT)
    assert path.is_file(), f"expected readiness file missing: {rel}"


def test_readiness_readme_local_markdown_links_resolve() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    for match in re.finditer(r"\]\(([^)]+\.md)\)", text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (README_PATH.parent / target).resolve()
        assert resolved.is_file(), f"broken README link target: {target}"
