"""Counterfactual Orchestrator for CLARITY.

This module provides end-to-end counterfactual sweep orchestration,
coordinating the full pipeline from baseline loading through probe
surface generation.

CRITICAL CONSTRAINTS (M09):
1. All computation must be deterministic given identical inputs.
2. No randomness, no datetime.now, no uuid.
3. No subprocess in CI tests (stubbed runner).
4. No direct r2l imports.
5. All floats rounded to 8 decimal places at storage.
6. Sequential execution only (no multiprocessing).
7. Masking uses fixed fill value (128 neutral gray).
8. No persistence layer (in-memory only).

The orchestrator coordinates:
- Baseline loading from fixture registry
- Grid mask generation
- R2L runner invocation (stubbed for CI)
- Metrics/Surface/Gradient computation
- Delta computation
- ProbeSurface aggregation

Typical workflow:
1. Load baseline image + spec from fixtures
2. Generate grid masks (k×k)
3. For each region:
   a. Apply mask to image
   b. Invoke R2L runner (stubbed)
   c. Compute metrics
   d. Compute delta vs baseline
4. Aggregate into ProbeSurface
5. Return JSON
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from PIL import Image

from app.clarity.evidence_overlay import (
    EvidenceMap,
    OverlayBundle,
    create_overlay_bundle,
    generate_stubbed_evidence_map,
)
from app.clarity.counterfactual_engine import (
    CounterfactualComputationError,
    CounterfactualProbe,
    ProbeResult,
    ProbeSurface,
    RegionMask,
    apply_mask,
    compute_probe_result,
    compute_probe_surface,
    generate_grid_masks,
)


# Default fixture directory relative to this module
DEFAULT_FIXTURES_DIR = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "baselines"


class OrchestratorError(Exception):
    """Raised when orchestration fails.

    This error indicates a failure during counterfactual orchestration, such as:
    - Baseline not found
    - Invalid configuration
    - Runner failure
    - Computation failure
    """

    pass


def _round8(value: float) -> float:
    """Round a value to 8 decimal places."""
    return round(value, 8)


@dataclass(frozen=True)
class BaselineSpec:
    """Specification for a baseline run.

    Attributes:
        baseline_id: Unique identifier for the baseline.
        image_path: Path to the baseline image file.
        prompt: The inference prompt.
        axis: The perturbation axis to probe.
        values: List of encoded axis values.
        expected_answer: Expected model answer (for stubbed runs).
        expected_justification: Expected justification (for stubbed runs).
        seed: Seed for reproducibility.
    """

    baseline_id: str
    image_path: Path
    prompt: str
    axis: str
    values: tuple[str, ...]
    expected_answer: str
    expected_justification: str
    seed: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "axis": self.axis,
            "baseline_id": self.baseline_id,
            "expected_answer": self.expected_answer,
            "expected_justification": self.expected_justification,
            "image_path": str(self.image_path),
            "prompt": self.prompt,
            "seed": self.seed,
            "values": list(self.values),
        }


@dataclass(frozen=True)
class RunnerResult:
    """Result from a runner invocation.

    Attributes:
        answer: The model's answer.
        justification: The model's justification.
        esi: Evidence Stability Index metric.
        drift: Justification drift metric.
        evidence_map: Optional evidence map from inference (M10).
    """

    answer: str
    justification: str
    esi: float
    drift: float
    evidence_map: EvidenceMap | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "answer": self.answer,
            "drift": self.drift,
            "esi": self.esi,
            "justification": self.justification,
        }
        if self.evidence_map is not None:
            result["evidence_map"] = self.evidence_map.to_dict()
        return result


class RunnerProtocol(Protocol):
    """Protocol for R2L runner implementations.

    This protocol allows for both real R2L invocation and stubbed
    implementations for CI testing.
    """

    def run(
        self,
        image: Image.Image,
        prompt: str,
        axis: str,
        value: str,
        seed: int,
    ) -> RunnerResult:
        """Run inference on an image.

        Args:
            image: The input image (may be masked).
            prompt: The inference prompt.
            axis: The perturbation axis.
            value: The encoded axis value.
            seed: Seed for reproducibility.

        Returns:
            RunnerResult with answer, justification, and metrics.

        Raises:
            OrchestratorError: If inference fails.
        """
        ...


class StubbedRunner:
    """Stubbed R2L runner for CI testing.

    This runner returns deterministic results based on the input
    parameters. No actual model inference is performed.

    The stubbed runner:
    - Returns deterministic answers based on masking
    - Simulates ESI/drift degradation when masked
    - Generates deterministic evidence maps (M10)
    - Is fully reproducible given identical inputs
    """

    def __init__(
        self,
        baseline_answer: str = "Normal findings.",
        baseline_justification: str = "No abnormalities detected.",
        baseline_esi: float = 1.0,
        baseline_drift: float = 0.0,
        evidence_width: int = 224,
        evidence_height: int = 224,
    ) -> None:
        """Initialize the stubbed runner.

        Args:
            baseline_answer: Answer to return for baseline (unmasked) runs.
            baseline_justification: Justification for baseline runs.
            baseline_esi: ESI metric for baseline runs.
            baseline_drift: Drift metric for baseline runs.
            evidence_width: Width of generated evidence maps.
            evidence_height: Height of generated evidence maps.
        """
        self._baseline_answer = baseline_answer
        self._baseline_justification = baseline_justification
        self._baseline_esi = baseline_esi
        self._baseline_drift = baseline_drift
        self._evidence_width = evidence_width
        self._evidence_height = evidence_height
        self._call_count = 0

    def run(
        self,
        image: Image.Image,
        prompt: str,
        axis: str,
        value: str,
        seed: int,
    ) -> RunnerResult:
        """Run stubbed inference.

        Returns deterministic results that simulate degradation when
        the image is masked (detected via pixel analysis).

        Args:
            image: The input image.
            prompt: The inference prompt.
            axis: The perturbation axis.
            value: The encoded axis value.
            seed: Seed for reproducibility.

        Returns:
            RunnerResult with deterministic metrics and evidence map.
        """
        self._call_count += 1

        # Generate deterministic evidence map based on seed and call count
        # Use a combined seed to vary the pattern per call while remaining deterministic
        combined_seed = seed + self._call_count
        evidence_map = generate_stubbed_evidence_map(
            width=self._evidence_width,
            height=self._evidence_height,
            seed=combined_seed,
        )

        # Detect if image is masked (has gray fill regions)
        is_masked = self._detect_masking(image)

        if is_masked:
            # Simulate degradation when masked
            # Use call count to create variation (deterministic)
            degradation = _round8(0.1 * (self._call_count % 10))
            return RunnerResult(
                answer=f"Uncertain findings (masked region {self._call_count}).",
                justification=f"Analysis limited due to occluded region. {self._baseline_justification}",
                esi=_round8(max(0.0, self._baseline_esi - degradation)),
                drift=_round8(min(1.0, self._baseline_drift + degradation)),
                evidence_map=evidence_map,
            )
        else:
            # Return baseline values for unmasked
            return RunnerResult(
                answer=self._baseline_answer,
                justification=self._baseline_justification,
                esi=_round8(self._baseline_esi),
                drift=_round8(self._baseline_drift),
                evidence_map=evidence_map,
            )

    def _detect_masking(self, image: Image.Image) -> bool:
        """Detect if an image has masked regions.

        Checks for presence of neutral gray (128, 128, 128) fill regions.

        Args:
            image: The image to check.

        Returns:
            True if masked regions detected.
        """
        if image.mode != "RGB":
            return False

        # Sample center pixels for efficiency
        width, height = image.size
        cx, cy = width // 2, height // 2

        # Check a small region around center
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x = max(0, min(width - 1, cx + dx))
                y = max(0, min(height - 1, cy + dy))
                pixel = image.getpixel((x, y))
                if pixel == (128, 128, 128):
                    return True

        return False

    @property
    def call_count(self) -> int:
        """Number of times run() has been called."""
        return self._call_count


def load_baseline_registry(fixtures_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load the baseline registry from fixtures.

    Args:
        fixtures_dir: Path to fixtures directory. Uses default if None.

    Returns:
        Dictionary mapping baseline_id to baseline metadata.

    Raises:
        OrchestratorError: If registry cannot be loaded.
    """
    if fixtures_dir is None:
        fixtures_dir = DEFAULT_FIXTURES_DIR

    registry_path = fixtures_dir / "registry.json"

    if not registry_path.exists():
        raise OrchestratorError(f"Baseline registry not found: {registry_path}")

    try:
        with open(registry_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("baselines", {})
    except json.JSONDecodeError as e:
        raise OrchestratorError(f"Invalid JSON in registry: {e}") from e


def load_baseline_spec(
    baseline_id: str,
    fixtures_dir: Path | None = None,
) -> BaselineSpec:
    """Load a baseline specification by ID.

    Args:
        baseline_id: The baseline identifier.
        fixtures_dir: Path to fixtures directory. Uses default if None.

    Returns:
        BaselineSpec with loaded data.

    Raises:
        OrchestratorError: If baseline not found or invalid.
    """
    if fixtures_dir is None:
        fixtures_dir = DEFAULT_FIXTURES_DIR

    registry = load_baseline_registry(fixtures_dir)

    if baseline_id not in registry:
        available = list(registry.keys())
        raise OrchestratorError(
            f"Baseline not found: {baseline_id}. Available: {available}"
        )

    entry = registry[baseline_id]
    spec_file = entry.get("spec_file")
    image_file = entry.get("image_file")

    if not spec_file or not image_file:
        raise OrchestratorError(f"Invalid registry entry for {baseline_id}")

    spec_path = fixtures_dir / spec_file
    image_path = fixtures_dir / image_file

    if not spec_path.exists():
        raise OrchestratorError(f"Spec file not found: {spec_path}")
    if not image_path.exists():
        raise OrchestratorError(f"Image file not found: {image_path}")

    try:
        with open(spec_path, encoding="utf-8") as f:
            spec_data = json.load(f)
    except json.JSONDecodeError as e:
        raise OrchestratorError(f"Invalid JSON in spec: {e}") from e

    return BaselineSpec(
        baseline_id=baseline_id,
        image_path=image_path,
        prompt=spec_data.get("prompt", ""),
        axis=spec_data.get("axis", ""),
        values=tuple(spec_data.get("values", [])),
        expected_answer=spec_data.get("expected_answer", ""),
        expected_justification=spec_data.get("expected_justification", ""),
        seed=spec_data.get("seed", 42),
    )


def list_available_baselines(fixtures_dir: Path | None = None) -> list[str]:
    """List all available baseline IDs.

    Args:
        fixtures_dir: Path to fixtures directory. Uses default if None.

    Returns:
        Sorted list of baseline IDs.
    """
    try:
        registry = load_baseline_registry(fixtures_dir)
        return sorted(registry.keys())
    except OrchestratorError:
        return []


@dataclass(frozen=True)
class OrchestratorConfig:
    """Configuration for the orchestrator.

    Attributes:
        grid_size: Grid size for region masking (k for k×k grid).
        axis: The perturbation axis to probe.
        value: The encoded axis value to probe.
    """

    grid_size: int
    axis: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "axis": self.axis,
            "grid_size": self.grid_size,
            "value": self.value,
        }


@dataclass(frozen=True)
class OrchestratorResult:
    """Result from orchestrator execution.

    Attributes:
        baseline_id: The baseline that was probed.
        config: The orchestrator configuration.
        baseline_metrics: Metrics from baseline (unmasked) run.
        probe_surface: The computed probe surface.
        overlay_bundle: Visualization overlay data (M10).
    """

    baseline_id: str
    config: OrchestratorConfig
    baseline_metrics: RunnerResult
    probe_surface: ProbeSurface
    overlay_bundle: OverlayBundle

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "baseline_id": self.baseline_id,
            "baseline_metrics": self.baseline_metrics.to_dict(),
            "config": self.config.to_dict(),
            "overlay_bundle": self.overlay_bundle.to_dict(),
            "probe_surface": self.probe_surface.to_dict(),
        }


class CounterfactualOrchestrator:
    """Orchestrator for counterfactual sweep execution.

    The CounterfactualOrchestrator coordinates the full pipeline:
    1. Load baseline image + spec
    2. Generate grid masks
    3. Run baseline inference
    4. For each mask region, run masked inference
    5. Compute deltas
    6. Aggregate into ProbeSurface

    Example:
        >>> runner = StubbedRunner()
        >>> orchestrator = CounterfactualOrchestrator(runner)
        >>> result = orchestrator.run(
        ...     baseline_id="test-baseline-001",
        ...     grid_size=3,
        ...     axis="brightness",
        ...     value="1p0",
        ... )
        >>> print(result.probe_surface.mean_abs_delta_esi)
    """

    def __init__(
        self,
        runner: RunnerProtocol,
        fixtures_dir: Path | None = None,
    ) -> None:
        """Initialize the orchestrator.

        Args:
            runner: The R2L runner implementation (real or stubbed).
            fixtures_dir: Path to fixtures directory. Uses default if None.
        """
        self._runner = runner
        self._fixtures_dir = fixtures_dir or DEFAULT_FIXTURES_DIR

    def run(
        self,
        baseline_id: str,
        grid_size: int,
        axis: str,
        value: str,
    ) -> OrchestratorResult:
        """Execute a counterfactual sweep.

        Args:
            baseline_id: The baseline to probe.
            grid_size: Grid size for region masking (k for k×k).
            axis: The perturbation axis.
            value: The encoded axis value.

        Returns:
            OrchestratorResult with probe surface and metrics.

        Raises:
            OrchestratorError: If orchestration fails.
            CounterfactualComputationError: If computation fails.
        """
        # Validate grid_size
        if grid_size < 1:
            raise OrchestratorError(f"grid_size must be >= 1, got {grid_size}")

        # Load baseline
        spec = load_baseline_spec(baseline_id, self._fixtures_dir)
        image = self._load_image(spec.image_path)

        # Create config
        config = OrchestratorConfig(
            grid_size=grid_size,
            axis=axis,
            value=value,
        )

        # Run baseline inference
        baseline_result = self._runner.run(
            image=image,
            prompt=spec.prompt,
            axis=axis,
            value=value,
            seed=spec.seed,
        )

        # Generate grid masks
        masks = generate_grid_masks(grid_size)

        # Run masked inference for each region
        probe_results: list[ProbeResult] = []

        for mask in masks:
            # Apply mask to image
            masked_image = apply_mask(image, mask)

            # Run inference on masked image
            masked_result = self._runner.run(
                image=masked_image,
                prompt=spec.prompt,
                axis=axis,
                value=value,
                seed=spec.seed,
            )

            # Create probe and compute result
            probe = CounterfactualProbe(
                region_id=mask.region_id,
                axis=axis,
                value=value,
            )

            probe_result = compute_probe_result(
                probe=probe,
                baseline_esi=baseline_result.esi,
                baseline_drift=baseline_result.drift,
                masked_esi=masked_result.esi,
                masked_drift=masked_result.drift,
            )

            probe_results.append(probe_result)

        # Aggregate into surface
        probe_surface = compute_probe_surface(probe_results)

        # Create overlay bundle from baseline evidence map (M10)
        # Use the baseline run's evidence map for visualization
        if baseline_result.evidence_map is not None:
            overlay_bundle = create_overlay_bundle(baseline_result.evidence_map)
        else:
            # Fallback: generate a stubbed evidence map
            fallback_evidence = generate_stubbed_evidence_map(seed=spec.seed)
            overlay_bundle = create_overlay_bundle(fallback_evidence)

        return OrchestratorResult(
            baseline_id=baseline_id,
            config=config,
            baseline_metrics=baseline_result,
            probe_surface=probe_surface,
            overlay_bundle=overlay_bundle,
        )

    def _load_image(self, image_path: Path) -> Image.Image:
        """Load an image from path.

        Args:
            image_path: Path to image file.

        Returns:
            RGB PIL Image.

        Raises:
            OrchestratorError: If image cannot be loaded.
        """
        try:
            image = Image.open(image_path)
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise OrchestratorError(f"Failed to load image: {e}") from e

