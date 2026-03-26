"""M18: lightweight readiness-pack guardrail — core files exist; README links resolve."""

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
)


@pytest.mark.parametrize("filename", REQUIRED_FILES)
def test_readiness_pack_required_files_exist(filename: str) -> None:
    path = READINESS_DIR / filename
    assert path.is_file(), f"expected readiness file missing: {path.relative_to(REPO_ROOT)}"


def test_readiness_readme_local_markdown_links_resolve() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    for match in re.finditer(r"\]\(([^)]+\.md)\)", text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (README_PATH.parent / target).resolve()
        assert resolved.is_file(), f"broken README link target: {target}"
