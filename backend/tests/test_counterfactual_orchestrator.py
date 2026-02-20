"""Tests for Counterfactual Orchestrator (M09).

This module contains comprehensive tests for the counterfactual orchestrator,
including stubbed runner, baseline loading, and end-to-end orchestration.

Test Categories:
1. Baseline Registry Loading (8 tests)
2. Baseline Spec Loading (9 tests)
3. Stubbed Runner (10 tests)
4. Orchestrator Configuration (5 tests)
5. Orchestrator Execution (8 tests)
6. Determinism (4 tests)
7. Error Handling (6 tests)
8. Serialization (5 tests)
9. Guardrails AST-based (6 tests)
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PIL import Image

from app.clarity import (
    CounterfactualComputationError,
    ProbeSurface,
)
from app.clarity.counterfactual_orchestrator import (
    BaselineSpec,
    CounterfactualOrchestrator,
    OrchestratorConfig,
    OrchestratorError,
    OrchestratorResult,
    RunnerResult,
    StubbedRunner,
    list_available_baselines,
    load_baseline_registry,
    load_baseline_spec,
)


# Fixtures directory for tests
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "baselines"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the fixtures directory path."""
    return FIXTURES_DIR


@pytest.fixture
def stubbed_runner() -> StubbedRunner:
    """Return a default stubbed runner."""
    return StubbedRunner()


@pytest.fixture
def orchestrator(stubbed_runner: StubbedRunner, fixtures_dir: Path) -> CounterfactualOrchestrator:
    """Return an orchestrator with stubbed runner."""
    return CounterfactualOrchestrator(stubbed_runner, fixtures_dir)


@pytest.fixture
def test_image() -> Image.Image:
    """Create a simple test image."""
    return Image.new("RGB", (64, 64), (100, 100, 100))


@pytest.fixture
def masked_test_image() -> Image.Image:
    """Create a test image with masked region."""
    img = Image.new("RGB", (64, 64), (100, 100, 100))
    # Add gray fill in center
    for x in range(30, 35):
        for y in range(30, 35):
            img.putpixel((x, y), (128, 128, 128))
    return img


# =============================================================================
# Category 1: Baseline Registry Loading (8 tests)
# =============================================================================


class TestBaselineRegistryLoading:
    """Tests for baseline registry loading."""

    def test_load_registry_success(self, fixtures_dir: Path) -> None:
        """Test successful registry loading."""
        registry = load_baseline_registry(fixtures_dir)
        assert isinstance(registry, dict)
        assert len(registry) >= 1

    def test_load_registry_contains_expected_baselines(self, fixtures_dir: Path) -> None:
        """Test registry contains expected baseline IDs."""
        registry = load_baseline_registry(fixtures_dir)
        assert "test-baseline-001" in registry
        assert "test-baseline-002" in registry

    def test_load_registry_entry_has_required_fields(self, fixtures_dir: Path) -> None:
        """Test registry entries have required fields."""
        registry = load_baseline_registry(fixtures_dir)
        entry = registry["test-baseline-001"]
        assert "name" in entry
        assert "image_file" in entry
        assert "spec_file" in entry

    def test_load_registry_missing_directory_raises(self, tmp_path: Path) -> None:
        """Test missing directory raises error."""
        with pytest.raises(OrchestratorError, match="registry not found"):
            load_baseline_registry(tmp_path / "nonexistent")

    def test_load_registry_missing_file_raises(self, tmp_path: Path) -> None:
        """Test missing registry file raises error."""
        tmp_path.mkdir(exist_ok=True)
        with pytest.raises(OrchestratorError, match="registry not found"):
            load_baseline_registry(tmp_path)

    def test_load_registry_invalid_json_raises(self, tmp_path: Path) -> None:
        """Test invalid JSON raises error."""
        registry_path = tmp_path / "registry.json"
        registry_path.write_text("not valid json{")
        with pytest.raises(OrchestratorError, match="Invalid JSON"):
            load_baseline_registry(tmp_path)

    def test_load_registry_empty_baselines(self, tmp_path: Path) -> None:
        """Test empty baselines returns empty dict."""
        registry_path = tmp_path / "registry.json"
        registry_path.write_text('{"baselines": {}}')
        registry = load_baseline_registry(tmp_path)
        assert registry == {}

    def test_list_available_baselines(self, fixtures_dir: Path) -> None:
        """Test listing available baselines."""
        baselines = list_available_baselines(fixtures_dir)
        assert isinstance(baselines, list)
        assert "test-baseline-001" in baselines
        assert baselines == sorted(baselines)  # Should be sorted


# =============================================================================
# Category 2: Baseline Spec Loading (9 tests)
# =============================================================================


class TestBaselineSpecLoading:
    """Tests for baseline spec loading."""

    def test_load_spec_success(self, fixtures_dir: Path) -> None:
        """Test successful spec loading."""
        spec = load_baseline_spec("test-baseline-001", fixtures_dir)
        assert isinstance(spec, BaselineSpec)

    def test_load_spec_has_correct_id(self, fixtures_dir: Path) -> None:
        """Test spec has correct baseline_id."""
        spec = load_baseline_spec("test-baseline-001", fixtures_dir)
        assert spec.baseline_id == "test-baseline-001"

    def test_load_spec_has_image_path(self, fixtures_dir: Path) -> None:
        """Test spec has valid image path."""
        spec = load_baseline_spec("test-baseline-001", fixtures_dir)
        assert spec.image_path.exists()
        assert spec.image_path.suffix == ".png"

    def test_load_spec_has_prompt(self, fixtures_dir: Path) -> None:
        """Test spec has prompt."""
        spec = load_baseline_spec("test-baseline-001", fixtures_dir)
        assert spec.prompt
        assert isinstance(spec.prompt, str)

    def test_load_spec_has_axis(self, fixtures_dir: Path) -> None:
        """Test spec has axis."""
        spec = load_baseline_spec("test-baseline-001", fixtures_dir)
        assert spec.axis
        assert isinstance(spec.axis, str)

    def test_load_spec_has_values(self, fixtures_dir: Path) -> None:
        """Test spec has values tuple."""
        spec = load_baseline_spec("test-baseline-001", fixtures_dir)
        assert spec.values
        assert isinstance(spec.values, tuple)

    def test_load_spec_missing_baseline_raises(self, fixtures_dir: Path) -> None:
        """Test missing baseline raises error."""
        with pytest.raises(OrchestratorError, match="Baseline not found"):
            load_baseline_spec("nonexistent-baseline", fixtures_dir)

    def test_load_spec_to_dict(self, fixtures_dir: Path) -> None:
        """Test spec to_dict() produces valid output."""
        spec = load_baseline_spec("test-baseline-001", fixtures_dir)
        d = spec.to_dict()
        assert "baseline_id" in d
        assert "image_path" in d
        assert "prompt" in d
        assert "axis" in d
        assert d["values"] == list(spec.values)

    def test_load_different_baselines(self, fixtures_dir: Path) -> None:
        """Test loading different baselines."""
        spec1 = load_baseline_spec("test-baseline-001", fixtures_dir)
        spec2 = load_baseline_spec("test-baseline-002", fixtures_dir)
        assert spec1.baseline_id != spec2.baseline_id
        assert spec1.axis != spec2.axis


# =============================================================================
# Category 3: Stubbed Runner (10 tests)
# =============================================================================


class TestStubbedRunner:
    """Tests for stubbed R2L runner."""

    def test_runner_returns_result(self, stubbed_runner: StubbedRunner, test_image: Image.Image) -> None:
        """Test runner returns RunnerResult."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert isinstance(result, RunnerResult)

    def test_runner_result_has_answer(self, stubbed_runner: StubbedRunner, test_image: Image.Image) -> None:
        """Test result has answer."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert result.answer
        assert isinstance(result.answer, str)

    def test_runner_result_has_justification(self, stubbed_runner: StubbedRunner, test_image: Image.Image) -> None:
        """Test result has justification."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert result.justification
        assert isinstance(result.justification, str)

    def test_runner_result_has_metrics(self, stubbed_runner: StubbedRunner, test_image: Image.Image) -> None:
        """Test result has ESI and drift."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert 0.0 <= result.esi <= 1.0
        assert 0.0 <= result.drift <= 1.0

    def test_runner_detects_unmasked_image(self, stubbed_runner: StubbedRunner, test_image: Image.Image) -> None:
        """Test runner returns baseline values for unmasked image."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert result.esi == 1.0
        assert result.drift == 0.0

    def test_runner_detects_masked_image(self, stubbed_runner: StubbedRunner, masked_test_image: Image.Image) -> None:
        """Test runner detects masking and degrades metrics."""
        result = stubbed_runner.run(masked_test_image, "prompt", "axis", "value", 42)
        # Masked should show degradation
        assert "masked" in result.answer.lower() or "uncertain" in result.answer.lower()

    def test_runner_call_count_increments(self, stubbed_runner: StubbedRunner, test_image: Image.Image) -> None:
        """Test call count increments."""
        assert stubbed_runner.call_count == 0
        stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert stubbed_runner.call_count == 1
        stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert stubbed_runner.call_count == 2

    def test_runner_result_to_dict(self, stubbed_runner: StubbedRunner, test_image: Image.Image) -> None:
        """Test RunnerResult to_dict()."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        d = result.to_dict()
        assert "answer" in d
        assert "justification" in d
        assert "esi" in d
        assert "drift" in d

    def test_runner_custom_baseline_values(self, test_image: Image.Image) -> None:
        """Test runner with custom baseline values."""
        runner = StubbedRunner(
            baseline_answer="Custom answer",
            baseline_esi=0.9,
            baseline_drift=0.1,
        )
        result = runner.run(test_image, "prompt", "axis", "value", 42)
        assert result.answer == "Custom answer"
        assert result.esi == 0.9
        assert result.drift == 0.1

    def test_runner_deterministic_across_calls(self, test_image: Image.Image) -> None:
        """Test runner produces deterministic results for same input."""
        runner1 = StubbedRunner()
        runner2 = StubbedRunner()
        result1 = runner1.run(test_image, "prompt", "axis", "value", 42)
        result2 = runner2.run(test_image, "prompt", "axis", "value", 42)
        assert result1.esi == result2.esi
        assert result1.drift == result2.drift


# =============================================================================
# Category 4: Orchestrator Configuration (5 tests)
# =============================================================================


class TestOrchestratorConfiguration:
    """Tests for orchestrator configuration."""

    def test_config_creation(self) -> None:
        """Test OrchestratorConfig creation."""
        config = OrchestratorConfig(grid_size=3, axis="brightness", value="1p0")
        assert config.grid_size == 3
        assert config.axis == "brightness"
        assert config.value == "1p0"

    def test_config_is_frozen(self) -> None:
        """Test config is immutable."""
        config = OrchestratorConfig(grid_size=3, axis="brightness", value="1p0")
        with pytest.raises(Exception):  # FrozenInstanceError
            config.grid_size = 5  # type: ignore

    def test_config_to_dict(self) -> None:
        """Test config to_dict()."""
        config = OrchestratorConfig(grid_size=3, axis="brightness", value="1p0")
        d = config.to_dict()
        assert d == {"axis": "brightness", "grid_size": 3, "value": "1p0"}

    def test_config_equality(self) -> None:
        """Test config equality."""
        config1 = OrchestratorConfig(grid_size=3, axis="brightness", value="1p0")
        config2 = OrchestratorConfig(grid_size=3, axis="brightness", value="1p0")
        assert config1 == config2

    def test_config_hashable(self) -> None:
        """Test config is hashable."""
        config = OrchestratorConfig(grid_size=3, axis="brightness", value="1p0")
        _ = hash(config)  # Should not raise


# =============================================================================
# Category 5: Orchestrator Execution (8 tests)
# =============================================================================


class TestOrchestratorExecution:
    """Tests for orchestrator execution."""

    def test_orchestrator_run_success(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test successful orchestration."""
        result = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=2,
            axis="brightness",
            value="1p0",
        )
        assert isinstance(result, OrchestratorResult)

    def test_orchestrator_result_has_baseline_id(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test result has correct baseline_id."""
        result = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=2,
            axis="brightness",
            value="1p0",
        )
        assert result.baseline_id == "test-baseline-001"

    def test_orchestrator_result_has_config(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test result has correct config."""
        result = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=2,
            axis="brightness",
            value="1p0",
        )
        assert result.config.grid_size == 2
        assert result.config.axis == "brightness"
        assert result.config.value == "1p0"

    def test_orchestrator_result_has_baseline_metrics(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test result has baseline metrics."""
        result = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=2,
            axis="brightness",
            value="1p0",
        )
        assert isinstance(result.baseline_metrics, RunnerResult)
        assert result.baseline_metrics.esi == 1.0  # Baseline is unmasked

    def test_orchestrator_result_has_probe_surface(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test result has probe surface."""
        result = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=2,
            axis="brightness",
            value="1p0",
        )
        assert isinstance(result.probe_surface, ProbeSurface)

    def test_orchestrator_probe_surface_has_correct_count(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test probe surface has k×k results."""
        result = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=3,
            axis="brightness",
            value="1p0",
        )
        assert len(result.probe_surface.results) == 9  # 3×3

    def test_orchestrator_result_to_dict(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test result to_dict() produces valid JSON."""
        result = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=2,
            axis="brightness",
            value="1p0",
        )
        d = result.to_dict()
        # Should be JSON serializable
        json_str = json.dumps(d, sort_keys=True)
        assert json_str

    def test_orchestrator_different_grid_sizes(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test different grid sizes."""
        result2 = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=2,
            axis="brightness",
            value="1p0",
        )
        result3 = orchestrator.run(
            baseline_id="test-baseline-001",
            grid_size=3,
            axis="brightness",
            value="1p0",
        )
        assert len(result2.probe_surface.results) == 4
        assert len(result3.probe_surface.results) == 9


# =============================================================================
# Category 6: Determinism (4 tests)
# =============================================================================


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_orchestrator_deterministic_results(self, fixtures_dir: Path) -> None:
        """Test orchestrator produces identical results on double-run."""
        runner1 = StubbedRunner()
        runner2 = StubbedRunner()
        orch1 = CounterfactualOrchestrator(runner1, fixtures_dir)
        orch2 = CounterfactualOrchestrator(runner2, fixtures_dir)

        result1 = orch1.run("test-baseline-001", 2, "brightness", "1p0")
        result2 = orch2.run("test-baseline-001", 2, "brightness", "1p0")

        # Compare serialized output
        assert result1.to_dict() == result2.to_dict()

    def test_probe_surface_deterministic_ordering(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test probe results are deterministically ordered."""
        result1 = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")

        # Reset orchestrator
        runner = StubbedRunner()
        orch2 = CounterfactualOrchestrator(runner, FIXTURES_DIR)
        result2 = orch2.run("test-baseline-001", 2, "brightness", "1p0")

        # Region IDs should be in same order
        ids1 = [r.probe.region_id for r in result1.probe_surface.results]
        ids2 = [r.probe.region_id for r in result2.probe_surface.results]
        assert ids1 == ids2

    def test_region_id_format_stable(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test region ID format is stable."""
        result = orchestrator.run("test-baseline-001", 3, "brightness", "1p0")
        ids = [r.probe.region_id for r in result.probe_surface.results]
        # Should follow grid_rX_cY_kZ format
        for region_id in ids:
            assert region_id.startswith("grid_r")
            assert "_c" in region_id
            assert "_k3" in region_id

    def test_baseline_metrics_deterministic(self, fixtures_dir: Path) -> None:
        """Test baseline metrics are deterministic."""
        runner1 = StubbedRunner()
        runner2 = StubbedRunner()
        orch1 = CounterfactualOrchestrator(runner1, fixtures_dir)
        orch2 = CounterfactualOrchestrator(runner2, fixtures_dir)

        result1 = orch1.run("test-baseline-001", 2, "brightness", "1p0")
        result2 = orch2.run("test-baseline-001", 2, "brightness", "1p0")

        assert result1.baseline_metrics.esi == result2.baseline_metrics.esi
        assert result1.baseline_metrics.drift == result2.baseline_metrics.drift


# =============================================================================
# Category 7: Error Handling (6 tests)
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_baseline_id_raises(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test invalid baseline ID raises error."""
        with pytest.raises(OrchestratorError, match="Baseline not found"):
            orchestrator.run("invalid-baseline", 3, "brightness", "1p0")

    def test_invalid_grid_size_raises(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test invalid grid_size raises error."""
        with pytest.raises(OrchestratorError, match="grid_size must be >= 1"):
            orchestrator.run("test-baseline-001", 0, "brightness", "1p0")

    def test_negative_grid_size_raises(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test negative grid_size raises error."""
        with pytest.raises(OrchestratorError, match="grid_size must be >= 1"):
            orchestrator.run("test-baseline-001", -1, "brightness", "1p0")

    def test_missing_image_raises(self, tmp_path: Path) -> None:
        """Test missing image file raises error."""
        # Create minimal registry pointing to nonexistent image
        registry = {"baselines": {"bad": {"image_file": "missing.png", "spec_file": "spec.json"}}}
        (tmp_path / "registry.json").write_text(json.dumps(registry))
        (tmp_path / "spec.json").write_text('{"axis": "x", "values": []}')

        runner = StubbedRunner()
        orch = CounterfactualOrchestrator(runner, tmp_path)
        with pytest.raises(OrchestratorError, match="Image file not found"):
            orch.run("bad", 2, "x", "v")

    def test_missing_spec_raises(self, tmp_path: Path) -> None:
        """Test missing spec file raises error."""
        registry = {"baselines": {"bad": {"image_file": "img.png", "spec_file": "missing.json"}}}
        (tmp_path / "registry.json").write_text(json.dumps(registry))
        # Create a dummy image
        Image.new("RGB", (10, 10)).save(tmp_path / "img.png")

        runner = StubbedRunner()
        orch = CounterfactualOrchestrator(runner, tmp_path)
        with pytest.raises(OrchestratorError, match="Spec file not found"):
            orch.run("bad", 2, "x", "v")

    def test_empty_baselines_list_with_bad_dir(self) -> None:
        """Test listing baselines with bad directory returns empty."""
        baselines = list_available_baselines(Path("/nonexistent"))
        assert baselines == []


# =============================================================================
# Category 8: Serialization (5 tests)
# =============================================================================


class TestSerialization:
    """Tests for serialization."""

    def test_orchestrator_result_json_serializable(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test result is JSON serializable."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        d = result.to_dict()
        json_str = json.dumps(d, sort_keys=True)
        parsed = json.loads(json_str)
        assert parsed["baseline_id"] == "test-baseline-001"

    def test_probe_surface_json_serializable(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test probe surface is JSON serializable."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        d = result.probe_surface.to_dict()
        json_str = json.dumps(d, sort_keys=True)
        parsed = json.loads(json_str)
        assert "results" in parsed

    def test_sorted_keys_in_output(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test output uses sorted keys."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        d = result.to_dict()
        # Check top-level keys are sorted
        keys = list(d.keys())
        assert keys == sorted(keys)

    def test_metrics_rounded_to_8_decimals(self, orchestrator: CounterfactualOrchestrator) -> None:
        """Test metrics are rounded to 8 decimals."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        for probe_result in result.probe_surface.results:
            # Check string representation of floats
            esi_str = f"{probe_result.delta_esi:.8f}"
            drift_str = f"{probe_result.delta_drift:.8f}"
            # Verify round-trip
            assert float(esi_str) == probe_result.delta_esi
            assert float(drift_str) == probe_result.delta_drift

    def test_config_json_roundtrip(self) -> None:
        """Test config survives JSON roundtrip."""
        config = OrchestratorConfig(grid_size=4, axis="contrast", value="0p9")
        d = config.to_dict()
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        config2 = OrchestratorConfig(**parsed)
        assert config == config2


# =============================================================================
# Category 9: Guardrails AST-based (6 tests)
# =============================================================================


class TestGuardrailsAST:
    """AST-based tests to verify no forbidden imports."""

    @pytest.fixture
    def orchestrator_source(self) -> str:
        """Load orchestrator module source."""
        module_path = Path(__file__).parent.parent / "app" / "clarity" / "counterfactual_orchestrator.py"
        return module_path.read_text(encoding="utf-8")

    def test_no_subprocess_import(self, orchestrator_source: str) -> None:
        """Test no subprocess import."""
        tree = ast.parse(orchestrator_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "subprocess"
            if isinstance(node, ast.ImportFrom):
                assert node.module != "subprocess"

    def test_no_random_import(self, orchestrator_source: str) -> None:
        """Test no random import."""
        tree = ast.parse(orchestrator_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "random"
            if isinstance(node, ast.ImportFrom):
                assert node.module != "random"

    def test_no_datetime_now(self, orchestrator_source: str) -> None:
        """Test no datetime.now() usage in actual code (not in comments/docstrings)."""
        tree = ast.parse(orchestrator_source)
        for node in ast.walk(tree):
            # Check for datetime.now() or datetime.utcnow() calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("now", "utcnow"):
                        if isinstance(node.func.value, ast.Attribute):
                            if node.func.value.attr == "datetime":
                                pytest.fail("datetime.now() or datetime.utcnow() usage found")
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id == "datetime":
                                pytest.fail("datetime.now() or datetime.utcnow() usage found")

    def test_no_uuid_import(self, orchestrator_source: str) -> None:
        """Test no uuid import."""
        tree = ast.parse(orchestrator_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "uuid"
            if isinstance(node, ast.ImportFrom):
                assert node.module != "uuid"

    def test_no_r2l_import(self, orchestrator_source: str) -> None:
        """Test no direct r2l import."""
        tree = ast.parse(orchestrator_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("r2l")

    def test_no_numpy_import(self, orchestrator_source: str) -> None:
        """Test no numpy import."""
        tree = ast.parse(orchestrator_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "numpy"
                    assert alias.name != "np"
            if isinstance(node, ast.ImportFrom):
                assert node.module != "numpy"


# =============================================================================
# Category 10: M10 Evidence Overlay Integration (12 tests)
# =============================================================================


class TestM10EvidenceOverlayIntegration:
    """Tests for M10 evidence overlay integration in orchestrator."""

    def test_runner_result_has_evidence_map(
        self, stubbed_runner: StubbedRunner, test_image: Image.Image
    ) -> None:
        """Test that runner result includes evidence map."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert result.evidence_map is not None
        assert result.evidence_map.width == 224
        assert result.evidence_map.height == 224

    def test_runner_result_evidence_map_to_dict(
        self, stubbed_runner: StubbedRunner, test_image: Image.Image
    ) -> None:
        """Test that evidence map is included in to_dict()."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        d = result.to_dict()
        assert "evidence_map" in d
        assert d["evidence_map"]["width"] == 224
        assert d["evidence_map"]["height"] == 224

    def test_runner_evidence_map_deterministic(
        self, test_image: Image.Image
    ) -> None:
        """Test that evidence map is deterministic for same seed."""
        runner1 = StubbedRunner()
        runner2 = StubbedRunner()
        r1 = runner1.run(test_image, "prompt", "axis", "value", 42)
        r2 = runner2.run(test_image, "prompt", "axis", "value", 42)
        assert r1.evidence_map is not None
        assert r2.evidence_map is not None
        assert r1.evidence_map.values == r2.evidence_map.values

    def test_orchestrator_result_has_overlay_bundle(
        self, orchestrator: CounterfactualOrchestrator
    ) -> None:
        """Test that orchestrator result includes overlay_bundle."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        assert result.overlay_bundle is not None

    def test_overlay_bundle_has_evidence_map(
        self, orchestrator: CounterfactualOrchestrator
    ) -> None:
        """Test that overlay bundle has evidence map."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        assert result.overlay_bundle.evidence_map is not None
        assert result.overlay_bundle.evidence_map.width == 224

    def test_overlay_bundle_has_heatmap(
        self, orchestrator: CounterfactualOrchestrator
    ) -> None:
        """Test that overlay bundle has normalized heatmap."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        assert result.overlay_bundle.heatmap is not None
        # Heatmap should have same dimensions
        assert result.overlay_bundle.heatmap.width == result.overlay_bundle.evidence_map.width

    def test_overlay_bundle_has_regions(
        self, orchestrator: CounterfactualOrchestrator
    ) -> None:
        """Test that overlay bundle has extracted regions."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        assert result.overlay_bundle.regions is not None
        assert isinstance(result.overlay_bundle.regions, tuple)

    def test_overlay_bundle_in_to_dict(
        self, orchestrator: CounterfactualOrchestrator
    ) -> None:
        """Test that overlay_bundle is included in to_dict()."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        d = result.to_dict()
        assert "overlay_bundle" in d
        assert "evidence_map" in d["overlay_bundle"]
        assert "heatmap" in d["overlay_bundle"]
        assert "regions" in d["overlay_bundle"]

    def test_overlay_bundle_json_serializable(
        self, orchestrator: CounterfactualOrchestrator
    ) -> None:
        """Test that overlay_bundle is JSON serializable."""
        result = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        d = result.to_dict()
        json_str = json.dumps(d["overlay_bundle"], sort_keys=True)
        parsed = json.loads(json_str)
        assert "evidence_map" in parsed
        assert "heatmap" in parsed
        assert "regions" in parsed

    def test_overlay_bundle_deterministic(
        self, orchestrator: CounterfactualOrchestrator
    ) -> None:
        """Test that overlay bundle is deterministic across runs."""
        r1 = orchestrator.run("test-baseline-001", 2, "brightness", "1p0")
        # Create new orchestrator for fresh run
        runner2 = StubbedRunner()
        orch2 = CounterfactualOrchestrator(runner2, FIXTURES_DIR)
        r2 = orch2.run("test-baseline-001", 2, "brightness", "1p0")
        # Compare overlay bundles
        assert r1.overlay_bundle.to_dict() == r2.overlay_bundle.to_dict()

    def test_runner_custom_evidence_dimensions(
        self, test_image: Image.Image
    ) -> None:
        """Test runner with custom evidence dimensions."""
        runner = StubbedRunner(evidence_width=100, evidence_height=80)
        result = runner.run(test_image, "prompt", "axis", "value", 42)
        assert result.evidence_map is not None
        assert result.evidence_map.width == 100
        assert result.evidence_map.height == 80

    def test_evidence_map_values_valid_range(
        self, stubbed_runner: StubbedRunner, test_image: Image.Image
    ) -> None:
        """Test that evidence map values are in valid range [0, 1]."""
        result = stubbed_runner.run(test_image, "prompt", "axis", "value", 42)
        assert result.evidence_map is not None
        for row in result.evidence_map.values:
            for value in row:
                assert 0.0 <= value <= 1.0
