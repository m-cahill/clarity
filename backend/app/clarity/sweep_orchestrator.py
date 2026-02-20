"""Sweep Orchestrator for CLARITY.

This module provides the core sweep execution engine that:
- Computes Cartesian product of perturbation axes and seeds
- Creates deterministic output directory structure
- Invokes R2L for each combination via R2LRunner
- Produces canonical sweep manifest

CRITICAL CONSTRAINTS (M04):
1. All R2L invocation must go through R2LRunner (no direct subprocess).
2. All artifact loading must go through artifact_loader.
3. No randomness without explicit seed.
4. No datetime.now / uuid / OS entropy.
5. Sequential execution only (no parallelization).
6. Output directory must not exist (no overwriting).
7. Spec injection must not mutate original file.

This is a control-plane milestone — orchestrator does NOT apply perturbations.
It only injects perturbation parameters into spec for R2L to execute.
"""

from __future__ import annotations

import copy
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.clarity.artifact_loader import hash_artifact
from app.clarity.r2l_runner import R2LRunner
from app.clarity.sweep_models import (
    SweepConfig,
    SweepRunRecord,
    build_run_directory_name,
)


class SweepExecutionError(Exception):
    """Raised when sweep execution fails.

    This error indicates a failure during sweep execution, such as:
    - Output directory already exists
    - R2L invocation failure
    - Artifact validation failure
    """

    pass


class OutputDirectoryExistsError(SweepExecutionError):
    """Raised when output_root already exists.

    CLARITY does not overwrite previous sweep results.
    Each sweep must write to a fresh directory.
    """

    pass


@dataclass(frozen=True)
class SweepResult:
    """Result of a completed sweep execution.

    Immutable record containing all run records and path to sweep manifest.

    Attributes:
        runs: Tuple of SweepRunRecord objects, one per run.
        sweep_manifest_path: Path to the sweep_manifest.json file.
    """

    runs: tuple[SweepRunRecord, ...]
    sweep_manifest_path: Path


class SweepOrchestrator:
    """Deterministic multi-axis perturbation sweep engine.

    The orchestrator:
    - Computes Cartesian product of axes × seeds
    - Creates deterministic output directory structure
    - Invokes R2LRunner for each combination
    - Produces canonical sweep_manifest.json

    Execution is sequential and deterministic. The same SweepConfig
    will always produce:
    - Identical execution order
    - Identical directory names
    - Identical sweep_manifest.json bytes

    Attributes:
        runner: The R2LRunner instance for R2L invocation.
        output_root: Root directory for sweep output.

    Example:
        >>> runner = R2LRunner("python -m r2l.cli", timeout_seconds=300)
        >>> orchestrator = SweepOrchestrator(runner, Path("sweep_output"))
        >>> result = orchestrator.execute(config)
        >>> print(f"Completed {len(result.runs)} runs")
    """

    def __init__(self, runner: R2LRunner, output_root: Path) -> None:
        """Initialize the sweep orchestrator.

        Args:
            runner: R2LRunner instance for R2L CLI invocation.
            output_root: Root directory for sweep output. Must not exist.

        Raises:
            ValueError: If runner is None or output_root is empty.
        """
        if runner is None:
            raise ValueError("runner must not be None")
        if output_root is None:
            raise ValueError("output_root must not be None")

        self._runner = runner
        self._output_root = output_root

    @property
    def runner(self) -> R2LRunner:
        """The R2LRunner instance."""
        return self._runner

    @property
    def output_root(self) -> Path:
        """The output root directory."""
        return self._output_root

    def execute(self, config: SweepConfig) -> SweepResult:
        """Execute a complete perturbation sweep.

        This method:
        1. Validates output_root does not exist
        2. Creates output directory structure
        3. Computes Cartesian product of axes × seeds
        4. For each combination:
           - Creates run directory
           - Injects perturbations into spec
           - Invokes R2LRunner
           - Hashes manifest
           - Records SweepRunRecord
        5. Writes sweep_manifest.json
        6. Returns SweepResult

        Args:
            config: The sweep configuration to execute.

        Returns:
            SweepResult containing all run records and manifest path.

        Raises:
            OutputDirectoryExistsError: If output_root already exists.
            SweepExecutionError: If any run fails.
        """
        # Validate output_root does not exist
        output_root_resolved = self._output_root.resolve()
        if output_root_resolved.exists():
            raise OutputDirectoryExistsError(
                f"Output directory already exists: {output_root_resolved}. "
                "CLARITY does not overwrite previous sweep results."
            )

        # Create output directory structure
        output_root_resolved.mkdir(parents=True, exist_ok=False)
        runs_dir = output_root_resolved / "runs"
        runs_dir.mkdir(parents=True, exist_ok=False)

        # Load base spec (will be deep copied for each run)
        base_spec = self._load_base_spec(config.base_spec_path)

        # Compute Cartesian product with deterministic ordering
        run_combinations = self._compute_run_combinations(config)

        # Execute each run
        run_records: list[SweepRunRecord] = []
        for axis_values, seed in run_combinations:
            record = self._execute_single_run(
                config=config,
                base_spec=base_spec,
                axis_values=axis_values,
                seed=seed,
                runs_dir=runs_dir,
            )
            run_records.append(record)

        # Write sweep manifest
        sweep_manifest_path = self._write_sweep_manifest(
            config=config,
            run_records=run_records,
            output_root=output_root_resolved,
        )

        return SweepResult(
            runs=tuple(run_records),
            sweep_manifest_path=sweep_manifest_path,
        )

    def _load_base_spec(self, spec_path: Path) -> dict[str, Any]:
        """Load the base spec JSON file.

        Args:
            spec_path: Path to the spec file.

        Returns:
            Parsed JSON as dictionary.

        Raises:
            SweepExecutionError: If file does not exist or is invalid JSON.
        """
        if not spec_path.exists():
            raise SweepExecutionError(f"Base spec not found: {spec_path}")

        try:
            with open(spec_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise SweepExecutionError(
                f"Invalid JSON in base spec: {spec_path}: {e}"
            ) from e

    def _compute_run_combinations(
        self, config: SweepConfig
    ) -> list[tuple[dict[str, Any], int]]:
        """Compute all run combinations with deterministic ordering.

        Ordering rules:
        1. Axis names sorted alphabetically
        2. Axis values in declared order
        3. Seeds in declared order

        Args:
            config: The sweep configuration.

        Returns:
            List of (axis_values dict, seed) tuples in deterministic order.
        """
        # Sort axes by name for deterministic iteration
        sorted_axes = sorted(config.axes, key=lambda a: a.name)

        # Build list of (axis_name, values) for iteration
        axis_value_lists: list[tuple[str, tuple[Any, ...]]] = [
            (axis.name, axis.values) for axis in sorted_axes
        ]

        # Compute Cartesian product of axis values
        if axis_value_lists:
            axis_names = [name for name, _ in axis_value_lists]
            value_lists = [values for _, values in axis_value_lists]
            axis_combinations = list(itertools.product(*value_lists))
        else:
            # Edge case: no axes (shouldn't happen due to validation)
            axis_names = []
            axis_combinations = [()]

        # Build run combinations with seeds
        run_combinations: list[tuple[dict[str, Any], int]] = []
        for axis_values_tuple in axis_combinations:
            axis_values = dict(zip(axis_names, axis_values_tuple))
            for seed in config.seeds:
                run_combinations.append((axis_values, seed))

        return run_combinations

    def _execute_single_run(
        self,
        config: SweepConfig,
        base_spec: dict[str, Any],
        axis_values: dict[str, Any],
        seed: int,
        runs_dir: Path,
    ) -> SweepRunRecord:
        """Execute a single run within the sweep.

        Args:
            config: The sweep configuration.
            base_spec: The loaded base spec (will be deep copied).
            axis_values: Dictionary mapping axis names to values for this run.
            seed: The seed for this run.
            runs_dir: Parent directory for run directories.

        Returns:
            SweepRunRecord for this run.

        Raises:
            SweepExecutionError: If run fails.
        """
        # Build deterministic directory name
        dir_name = build_run_directory_name(axis_values, seed)
        run_dir = runs_dir / dir_name

        # Create run directory (atomic, fail if exists)
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError as e:
            raise SweepExecutionError(
                f"Run directory already exists (collision?): {run_dir}"
            ) from e

        # Create modified spec (deep copy to avoid mutating original)
        modified_spec = copy.deepcopy(base_spec)
        modified_spec["perturbations"] = axis_values
        modified_spec["seed"] = seed

        # Write modified spec to run directory
        spec_path = run_dir / "spec.json"
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(modified_spec, f, sort_keys=True, indent=2)

        # Invoke R2LRunner
        try:
            run_result = self._runner.run(
                config_path=spec_path,
                output_dir=run_dir,
                adapter=config.adapter,
                seed=seed,
            )
        except Exception as e:
            raise SweepExecutionError(
                f"R2L invocation failed for {dir_name}: {e}"
            ) from e

        # Hash manifest
        manifest_hash = hash_artifact(run_result.manifest_path)

        return SweepRunRecord(
            axis_values=axis_values,
            seed=seed,
            output_dir=run_dir,
            manifest_hash=manifest_hash,
        )

    def _write_sweep_manifest(
        self,
        config: SweepConfig,
        run_records: list[SweepRunRecord],
        output_root: Path,
    ) -> Path:
        """Write the canonical sweep_manifest.json.

        The manifest is written with deterministic formatting:
        - sort_keys=True
        - indent=2

        Args:
            config: The sweep configuration.
            run_records: List of completed run records.
            output_root: The output root directory.

        Returns:
            Path to the written sweep_manifest.json.
        """
        # Build axes dictionary (sorted by axis name)
        axes_dict: dict[str, list[Any]] = {}
        for axis in sorted(config.axes, key=lambda a: a.name):
            axes_dict[axis.name] = list(axis.values)

        # Build runs list
        runs_list: list[dict[str, Any]] = []
        for record in run_records:
            runs_list.append({
                "axis_values": record.axis_values,
                "seed": record.seed,
                "manifest_hash": record.manifest_hash,
            })

        # Build manifest
        manifest: dict[str, Any] = {
            "axes": axes_dict,
            "seeds": list(config.seeds),
            "runs": runs_list,
        }

        # Write with deterministic formatting
        manifest_path = output_root / "sweep_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, sort_keys=True, indent=2)

        return manifest_path

