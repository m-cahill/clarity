"""M20: artifact contract guardrails — fixtures, structure, ordering, stable JSON.

Readiness authority: docs/readiness/CLARITY_ARTIFACT_CONTRACT.md

Does not duplicate boundary/namespace tests (see test_boundary_contract.py).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.clarity.surfaces import _round8

REPO_ROOT = Path(__file__).resolve().parents[2]
M15_FIXTURE_DIR = (
    REPO_ROOT / "backend" / "tests" / "fixtures" / "baselines" / "m15_real_ui"
)

# Committed fixture bytes — stable-hash evidence for the frozen bundle (M20).
M15_SHA256 = {
    "sweep_manifest.json": "c8de28b41acb458f41f0107a19a306646d16db8898e6fc3fb79b4d779c1b9beb",
    "robustness_surface.json": "73a2d6940e40213cd21f980055ebeecd6077dd03f326e16f6d64b6ef7d3fb572",
    "monte_carlo_stats.json": "14490feff254234b49995efe387232b4a5ae9ea6739f8a50bda0aca76afdda2f",
}

REQUIRED_BUNDLE_JSON = (
    "sweep_manifest.json",
    "robustness_surface.json",
    "monte_carlo_stats.json",
)


def _canonical_json_dumps(obj: object) -> str:
    """Match scripts/m15_real_ui_sweep.py deterministic_json_dumps."""
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=True)


def test_m15_fixture_dir_has_required_bundle_artifacts() -> None:
    """Required JSON files exist for the full analytical bundle (semantic completeness)."""
    for name in REQUIRED_BUNDLE_JSON:
        path = M15_FIXTURE_DIR / name
        assert path.is_file(), f"missing required artifact: {path}"


@pytest.mark.parametrize("filename", list(M15_SHA256))
def test_m15_required_artifact_sha256(filename: str) -> None:
    """Stable-hash evidence for contract-relevant JSON (committed bytes)."""
    path = M15_FIXTURE_DIR / filename
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == M15_SHA256[filename]


@pytest.mark.parametrize("filename", REQUIRED_BUNDLE_JSON)
def test_m15_json_roundtrip_preserves_bytes(filename: str) -> None:
    """Serialization stability for m15-style JSON: sort_keys + indent=2 + ensure_ascii=True."""
    path = M15_FIXTURE_DIR / filename
    raw = path.read_text(encoding="utf-8").rstrip("\r\n")
    parsed = json.loads(raw)
    out = _canonical_json_dumps(parsed)
    assert out == raw


def test_robustness_surface_axis_ordering_alphabetical() -> None:
    """Axes appear in alphabetical order by name (contract ordering)."""
    path = M15_FIXTURE_DIR / "robustness_surface.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    axes = data["axes"]
    names = [a["axis"] for a in axes]
    assert names == sorted(names)
    for ax in axes:
        values = [p["value"] for p in ax["points"]]
        assert values == sorted(values)


def test_robustness_surface_required_top_level_keys() -> None:
    path = M15_FIXTURE_DIR / "robustness_surface.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in (
        "axes",
        "global_mean_drift",
        "global_mean_esi",
        "global_variance_drift",
        "global_variance_esi",
    ):
        assert key in data


def test_monte_carlo_stats_required_top_level_keys() -> None:
    path = M15_FIXTURE_DIR / "monte_carlo_stats.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "axes" in data
    assert "monte_carlo" in data
    assert "total_runs" in data
    mc = data["monte_carlo"]
    assert "seeds" in mc
    assert list(mc["seeds"]) == sorted(mc["seeds"])


def test_sweep_manifest_m15_rich_shape_keys() -> None:
    """Rich aggregate manifest (M15 family) — expected keys for this fixture class."""
    path = M15_FIXTURE_DIR / "sweep_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("axes", "seeds", "results", "sweep_id"):
        assert key in data
    assert data["results"], "results must be non-empty for this fixture"
    assert isinstance(data["axes"], dict)


def test_surface_engine_round8_matches_documented_rule() -> None:
    """Float storage rule for surface computation path: round(value, 8)."""
    assert _round8(1.234567890123) == round(1.234567890123, 8)


def test_presentation_pdf_not_in_required_bundle() -> None:
    """Report PDFs are not part of the required JSON bundle identity (M20)."""
    assert "clarity_report.pdf" not in REQUIRED_BUNDLE_JSON


def test_optional_rich_surfaces_exist_in_m15_fixture() -> None:
    """Optional artifacts may accompany the bundle; fixture includes them."""
    for name in ("confidence_surface.json", "entropy_surface.json"):
        assert (M15_FIXTURE_DIR / name).is_file()
