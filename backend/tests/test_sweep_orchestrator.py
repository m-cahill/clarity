"""Tests for sweep_orchestrator.py.

This test module validates the sweep orchestrator including:
- Cartesian expansion (correct count, ordering, determinism)
- Directory naming (encoding, no collisions, OS-safe)
- Spec injection (original unmutated, perturbations injected, seed injected)
- Integration with fake_r2l
- Sweep manifest content and determinism
- Error handling (output_root exists, invalid config)

Coverage target: ≥90%
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from app.clarity.r2l_runner import R2LRunner
from app.clarity.sweep_models import SweepAxis, SweepConfig
from app.clarity.sweep_orchestrator import (
    OutputDirectoryExistsError,
    SweepExecutionError,
    SweepOrchestrator,
    SweepResult,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def fake_r2l_path() -> Path:
    """Path to the fake R2L CLI script."""
    return Path(__file__).parent / "fixtures" / "fake_r2l.py"


@pytest.fixture
def r2l_runner(fake_r2l_path: Path) -> R2LRunner:
    """Create an R2LRunner using the fake R2L CLI."""
    executable = f"{sys.executable} {fake_r2l_path}"
    return R2LRunner(r2l_executable=executable, timeout_seconds=30)


@pytest.fixture
def base_spec_file(tmp_path: Path) -> Path:
    """Create a minimal base spec file."""
    spec_path = tmp_path / "base_spec.json"
    spec_content = {
        "name": "test_spec",
        "version": "1.0.0",
        "existing_field": "value",
    }
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec_content, f)
    return spec_path


@pytest.fixture
def simple_config(base_spec_file: Path) -> SweepConfig:
    """Create a simple sweep config with one axis and one seed."""
    return SweepConfig(
        base_spec_path=base_spec_file,
        axes=(SweepAxis(name="brightness", values=(0.8, 1.0, 1.2)),),
        seeds=(42,),
        adapter="test-adapter",
    )


@pytest.fixture
def multi_axis_config(base_spec_file: Path) -> SweepConfig:
    """Create a config with multiple axes and seeds."""
    return SweepConfig(
        base_spec_path=base_spec_file,
        axes=(
            SweepAxis(name="brightness", values=(0.8, 1.0)),
            SweepAxis(name="contrast", values=(0.9, 1.1)),
        ),
        seeds=(42, 43),
        adapter="test-adapter",
    )


# =============================================================================
# SweepOrchestrator Init Tests
# =============================================================================


class TestSweepOrchestratorInit:
    """Tests for SweepOrchestrator initialization."""

    def test_valid_init(
        self, r2l_runner: R2LRunner, tmp_path: Path
    ) -> None:
        """Test valid orchestrator initialization."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)
        assert orchestrator.runner is r2l_runner
        assert orchestrator.output_root == output_root

    def test_none_runner_raises(self, tmp_path: Path) -> None:
        """Test that None runner raises ValueError."""
        with pytest.raises(ValueError, match="runner must not be None"):
            SweepOrchestrator(None, tmp_path / "output")  # type: ignore

    def test_none_output_root_raises(self, r2l_runner: R2LRunner) -> None:
        """Test that None output_root raises ValueError."""
        with pytest.raises(ValueError, match="output_root must not be None"):
            SweepOrchestrator(r2l_runner, None)  # type: ignore


# =============================================================================
# Execute Tests - Basic
# =============================================================================


class TestSweepOrchestratorExecuteBasic:
    """Basic execution tests for SweepOrchestrator."""

    def test_execute_single_axis_single_seed(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test executing a sweep with single axis and single seed."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(1.0,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        assert isinstance(result, SweepResult)
        assert len(result.runs) == 1
        assert result.sweep_manifest_path.exists()

    def test_execute_creates_output_structure(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that execute creates proper output directory structure."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        # Verify structure
        assert output_root.exists()
        assert (output_root / "runs").exists()
        assert (output_root / "sweep_manifest.json").exists()
        assert result.sweep_manifest_path == output_root / "sweep_manifest.json"

    def test_execute_correct_run_count(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that execute produces correct number of runs."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        # 3 brightness values × 1 seed = 3 runs
        assert len(result.runs) == 3
        assert len(result.runs) == simple_config.total_runs()


# =============================================================================
# Cartesian Expansion Tests
# =============================================================================


class TestCartesianExpansion:
    """Tests for Cartesian product expansion."""

    def test_correct_run_count_multi_axis(
        self,
        r2l_runner: R2LRunner,
        multi_axis_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test correct run count with multiple axes and seeds."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(multi_axis_config)

        # 2 brightness × 2 contrast × 2 seeds = 8 runs
        assert len(result.runs) == 8
        assert len(result.runs) == multi_axis_config.total_runs()

    def test_axis_value_combinations(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that all axis value combinations are covered."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(
                SweepAxis(name="a", values=(1, 2)),
                SweepAxis(name="b", values=(10, 20)),
            ),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        # Extract axis value combinations
        combinations = {
            (r.axis_values["a"], r.axis_values["b"]) for r in result.runs
        }
        expected = {(1, 10), (1, 20), (2, 10), (2, 20)}
        assert combinations == expected

    def test_all_seeds_covered(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that all seeds are covered for each axis combination."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="a", values=(1,)),),
            seeds=(42, 43, 44),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        seeds = {r.seed for r in result.runs}
        assert seeds == {42, 43, 44}

    def test_deterministic_ordering(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that execution order is deterministic."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(
                SweepAxis(name="z_axis", values=(1, 2)),
                SweepAxis(name="a_axis", values=(10, 20)),
            ),
            seeds=(42, 43),
            adapter="test-adapter",
        )

        # Run twice and compare ordering
        output1 = tmp_path / "sweep_output_1"
        output2 = tmp_path / "sweep_output_2"

        result1 = SweepOrchestrator(r2l_runner, output1).execute(config)
        result2 = SweepOrchestrator(r2l_runner, output2).execute(config)

        # Extract ordered list of (axis_values, seed)
        def extract_order(result: SweepResult) -> list[tuple[dict[str, Any], int]]:
            return [(dict(r.axis_values), r.seed) for r in result.runs]

        order1 = extract_order(result1)
        order2 = extract_order(result2)

        assert order1 == order2

    def test_alphabetical_axis_ordering(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that axes are processed in alphabetical order."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(
                SweepAxis(name="zebra", values=(1,)),
                SweepAxis(name="alpha", values=(2,)),
                SweepAxis(name="beta", values=(3,)),
            ),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        # Check directory name has alphabetical ordering
        dir_name = result.runs[0].output_dir.name
        # alpha should come before beta, beta before zebra
        assert "alpha=" in dir_name
        alpha_pos = dir_name.index("alpha=")
        beta_pos = dir_name.index("beta=")
        zebra_pos = dir_name.index("zebra=")
        assert alpha_pos < beta_pos < zebra_pos


# =============================================================================
# Directory Naming Tests
# =============================================================================


class TestDirectoryNaming:
    """Tests for run directory naming."""

    def test_no_directory_collisions(
        self,
        r2l_runner: R2LRunner,
        multi_axis_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that all run directories are unique."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(multi_axis_config)

        dir_names = [r.output_dir.name for r in result.runs]
        assert len(dir_names) == len(set(dir_names))

    def test_directory_name_format(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that directory names follow expected format."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        dir_name = result.runs[0].output_dir.name
        assert dir_name == "brightness=0p8_seed=42"

    def test_negative_value_encoding(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test encoding of negative values in directory names."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="offset", values=(-0.25,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        dir_name = result.runs[0].output_dir.name
        assert "offset=m0p25" in dir_name

    def test_run_directories_created(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that all run directories are created."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        for run in result.runs:
            assert run.output_dir.exists()
            assert run.output_dir.is_dir()


# =============================================================================
# Spec Injection Tests
# =============================================================================


class TestSpecInjection:
    """Tests for spec modification and injection."""

    def test_perturbations_injected(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that perturbations are injected into spec."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        # Read the modified spec
        spec_path = result.runs[0].output_dir / "spec.json"
        with open(spec_path, encoding="utf-8") as f:
            modified_spec = json.load(f)

        assert "perturbations" in modified_spec
        assert modified_spec["perturbations"]["brightness"] == 0.8

    def test_seed_injected(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that seed is injected into spec."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        # Read the modified spec
        spec_path = result.runs[0].output_dir / "spec.json"
        with open(spec_path, encoding="utf-8") as f:
            modified_spec = json.load(f)

        assert "seed" in modified_spec
        assert modified_spec["seed"] == 42

    def test_original_spec_not_mutated(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that original spec file is not mutated."""
        # Read original content
        with open(base_spec_file, encoding="utf-8") as f:
            original_content = f.read()

        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        orchestrator.execute(config)

        # Read content after execution
        with open(base_spec_file, encoding="utf-8") as f:
            after_content = f.read()

        assert original_content == after_content

    def test_existing_spec_fields_preserved(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that existing spec fields are preserved."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        # Read the modified spec
        spec_path = result.runs[0].output_dir / "spec.json"
        with open(spec_path, encoding="utf-8") as f:
            modified_spec = json.load(f)

        # Original fields should be preserved
        assert modified_spec["name"] == "test_spec"
        assert modified_spec["version"] == "1.0.0"
        assert modified_spec["existing_field"] == "value"

    def test_seed_overrides_existing(
        self,
        r2l_runner: R2LRunner,
        tmp_path: Path,
    ) -> None:
        """Test that seed injection overrides existing seed in spec."""
        # Create spec with existing seed
        spec_path = tmp_path / "spec_with_seed.json"
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump({"name": "test", "seed": 999}, f)

        config = SweepConfig(
            base_spec_path=spec_path,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        # Read the modified spec
        modified_spec_path = result.runs[0].output_dir / "spec.json"
        with open(modified_spec_path, encoding="utf-8") as f:
            modified_spec = json.load(f)

        # Sweep seed should override original
        assert modified_spec["seed"] == 42


# =============================================================================
# Sweep Manifest Tests
# =============================================================================


class TestSweepManifest:
    """Tests for sweep manifest generation."""

    def test_manifest_created(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that sweep_manifest.json is created."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        assert result.sweep_manifest_path.exists()
        assert result.sweep_manifest_path.name == "sweep_manifest.json"

    def test_manifest_contains_axes(
        self,
        r2l_runner: R2LRunner,
        multi_axis_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that manifest contains all axes."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(multi_axis_config)

        with open(result.sweep_manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert "axes" in manifest
        assert "brightness" in manifest["axes"]
        assert "contrast" in manifest["axes"]
        assert manifest["axes"]["brightness"] == [0.8, 1.0]
        assert manifest["axes"]["contrast"] == [0.9, 1.1]

    def test_manifest_contains_seeds(
        self,
        r2l_runner: R2LRunner,
        multi_axis_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that manifest contains seeds."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(multi_axis_config)

        with open(result.sweep_manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert "seeds" in manifest
        assert manifest["seeds"] == [42, 43]

    def test_manifest_contains_runs(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that manifest contains runs with correct structure."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        with open(result.sweep_manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        assert "runs" in manifest
        assert len(manifest["runs"]) == len(result.runs)

        for run in manifest["runs"]:
            assert "axis_values" in run
            assert "seed" in run
            assert "manifest_hash" in run

    def test_manifest_deterministic(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that manifest content is deterministic (byte-identical)."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(0.8, 1.0)),),
            seeds=(42,),
            adapter="test-adapter",
        )

        output1 = tmp_path / "sweep_output_1"
        output2 = tmp_path / "sweep_output_2"

        result1 = SweepOrchestrator(r2l_runner, output1).execute(config)
        result2 = SweepOrchestrator(r2l_runner, output2).execute(config)

        # Read manifest bytes
        with open(result1.sweep_manifest_path, "rb") as f:
            bytes1 = f.read()
        with open(result2.sweep_manifest_path, "rb") as f:
            bytes2 = f.read()

        assert bytes1 == bytes2

    def test_manifest_hashes_unique_per_seed(
        self,
        r2l_runner: R2LRunner,
        base_spec_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that manifest hashes are unique per seed."""
        config = SweepConfig(
            base_spec_path=base_spec_file,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42, 43, 44),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(config)

        hashes = [r.manifest_hash for r in result.runs]
        # All hashes should be unique (different seeds produce different manifests)
        assert len(hashes) == len(set(hashes))


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_output_root_exists_raises(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that existing output_root raises OutputDirectoryExistsError."""
        output_root = tmp_path / "sweep_output"
        output_root.mkdir(parents=True)

        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        with pytest.raises(OutputDirectoryExistsError, match="already exists"):
            orchestrator.execute(simple_config)

    def test_missing_base_spec_raises(
        self,
        r2l_runner: R2LRunner,
        tmp_path: Path,
    ) -> None:
        """Test that missing base spec raises SweepExecutionError."""
        config = SweepConfig(
            base_spec_path=tmp_path / "nonexistent.json",
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        with pytest.raises(SweepExecutionError, match="not found"):
            orchestrator.execute(config)

    def test_invalid_base_spec_json_raises(
        self,
        r2l_runner: R2LRunner,
        tmp_path: Path,
    ) -> None:
        """Test that invalid JSON in base spec raises SweepExecutionError."""
        spec_path = tmp_path / "invalid.json"
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        config = SweepConfig(
            base_spec_path=spec_path,
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="test-adapter",
        )
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        with pytest.raises(SweepExecutionError, match="Invalid JSON"):
            orchestrator.execute(config)


# =============================================================================
# Integration Tests with Fake R2L
# =============================================================================


class TestFakeR2LIntegration:
    """Integration tests using the fake R2L CLI."""

    def test_full_sweep_with_fake_r2l(
        self,
        r2l_runner: R2LRunner,
        multi_axis_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test full sweep execution with fake R2L."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(multi_axis_config)

        # Verify all runs completed
        assert len(result.runs) == multi_axis_config.total_runs()

        # Verify artifacts exist for each run
        for run in result.runs:
            assert (run.output_dir / "manifest.json").exists()
            assert (run.output_dir / "trace_pack.jsonl").exists()

    def test_manifest_hash_calculated(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that manifest hash is calculated for each run."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        for run in result.runs:
            assert run.manifest_hash
            assert len(run.manifest_hash) == 64  # SHA256 hex digest

    def test_artifacts_load_correctly(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that R2L artifacts can be loaded after sweep."""
        from app.clarity.artifact_loader import load_manifest, load_trace_pack

        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        for run in result.runs:
            manifest_path = run.output_dir / "manifest.json"
            trace_path = run.output_dir / "trace_pack.jsonl"

            manifest = load_manifest(manifest_path)
            traces = load_trace_pack(trace_path)

            assert "run_id" in manifest
            assert len(traces) > 0


# =============================================================================
# SweepResult Tests
# =============================================================================


class TestSweepResult:
    """Tests for SweepResult dataclass."""

    def test_result_immutability(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that SweepResult is frozen (immutable)."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        with pytest.raises(AttributeError):
            result.runs = ()  # type: ignore

    def test_result_runs_tuple(
        self,
        r2l_runner: R2LRunner,
        simple_config: SweepConfig,
        tmp_path: Path,
    ) -> None:
        """Test that result.runs is a tuple (immutable)."""
        output_root = tmp_path / "sweep_output"
        orchestrator = SweepOrchestrator(r2l_runner, output_root)

        result = orchestrator.execute(simple_config)

        assert isinstance(result.runs, tuple)

