"""M21 public-surface contract tests (separate from artifact-contract tests)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from app.clarity.public_surface import (
    PUBLIC_SURFACE_SYMBOLS,
    R2LRunner,
    SweepAxis,
    SweepConfig,
    SweepOrchestrator,
)


def test_public_surface_smoke_import() -> None:
    """Public surface module imports and exposes frozen metadata."""
    import app.clarity.public_surface as ps

    assert hasattr(ps, "PUBLIC_SURFACE_SYMBOLS")
    assert ps.PUBLIC_SURFACE_SYMBOLS == frozenset(ps.__all__)


def test_public_surface_export_snapshot() -> None:
    """Frozen public names must match M21 contract (intentional edits only)."""
    expected = frozenset(
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
    assert PUBLIC_SURFACE_SYMBOLS == expected


@pytest.fixture
def fake_r2l_path() -> Path:
    return Path(__file__).parent / "fixtures" / "fake_r2l.py"


@pytest.fixture
def public_surface_runner(fake_r2l_path: Path) -> R2LRunner:
    executable = f"{sys.executable} {fake_r2l_path}"
    return R2LRunner(r2l_executable=executable, timeout_seconds=30)


def test_sanctioned_consumer_sweep_smoke(
    public_surface_runner: R2LRunner, tmp_path: Path
) -> None:
    """End-to-end sweep using only the canonical public_surface imports."""
    spec_path = tmp_path / "base_spec.json"
    spec_path.write_text(
        json.dumps({"name": "ps_contract", "version": "1.0.0"}), encoding="utf-8"
    )
    out_root = tmp_path / "sweep_out"
    config = SweepConfig(
        base_spec_path=spec_path,
        axes=(SweepAxis(name="brightness", values=(1.0,)),),
        seeds=(42,),
        adapter="test-adapter",
    )
    orchestrator = SweepOrchestrator(public_surface_runner, out_root)
    result = orchestrator.execute(config)
    assert result.sweep_manifest_path.is_file()
    assert len(result.runs) == 1
