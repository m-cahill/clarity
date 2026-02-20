"""Metrics Engine for CLARITY.

This module provides the core computation engine for calculating ESI
(Evidence Stability Index) and Justification Drift metrics from sweep output.

CRITICAL CONSTRAINTS (M05):
1. All computation must be deterministic given identical sweep output.
2. No randomness, no datetime.now, no uuid.
3. No numpy — pure Python only.
4. No r2l imports.
5. All invocations via artifact_loader for file access.
6. No side effects (no file writes).
7. Sequential execution only.

The engine consumes:
- sweep_manifest.json
- Per-run manifest.json
- Per-run trace_pack.jsonl

And produces:
- MetricsResult with ESI and Drift metrics per axis
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.clarity.artifact_loader import load_trace_pack
from app.clarity.metrics import (
    DriftMetric,
    ESIMetric,
    MetricComputationError,
    MetricsResult,
    extract_answer,
    extract_justification,
    normalized_levenshtein,
    round_metric,
)
from app.clarity.sweep_models import encode_axis_value


class MetricsEngine:
    """Engine for computing metrics from sweep output.

    The MetricsEngine computes ESI and Justification Drift metrics from
    a completed sweep directory. All computation is deterministic and
    produces identical results given identical input.

    The engine:
    1. Loads sweep_manifest.json
    2. Loads all run trace packs
    3. Identifies baseline run (first in deterministic order)
    4. Extracts answers + justifications
    5. Computes ESI per axis
    6. Computes Drift per axis
    7. Returns MetricsResult

    Example:
        >>> engine = MetricsEngine()
        >>> result = engine.compute(Path("sweep_output"))
        >>> print(f"ESI for brightness: {result.esi[0].overall_score}")
    """

    def compute(self, sweep_dir: Path) -> MetricsResult:
        """Compute metrics from a sweep directory.

        Args:
            sweep_dir: Path to the sweep output directory containing
                      sweep_manifest.json and runs/ subdirectory.

        Returns:
            MetricsResult containing ESI and Drift metrics for all axes.

        Raises:
            MetricComputationError: If sweep is invalid or computation fails.
            FileNotFoundError: If required files are missing.
        """
        sweep_dir = sweep_dir.resolve()

        # Load sweep manifest
        manifest = self._load_sweep_manifest(sweep_dir)

        # Validate non-empty
        runs_data = manifest.get("runs", [])
        if not runs_data:
            raise MetricComputationError("Sweep has zero runs")

        # Load axes definition
        axes_def = manifest.get("axes", {})
        if not axes_def:
            raise MetricComputationError("Sweep manifest missing axes definition")

        # Load all run data (answers + justifications)
        runs_dir = sweep_dir / "runs"
        run_records = self._load_run_data(runs_data, runs_dir)

        # Baseline is first run
        baseline = run_records[0]

        # Compute metrics per axis
        esi_metrics = self._compute_esi(axes_def, run_records, baseline)
        drift_metrics = self._compute_drift(axes_def, run_records, baseline)

        return MetricsResult(
            esi=tuple(esi_metrics),
            drift=tuple(drift_metrics),
        )

    def _load_sweep_manifest(self, sweep_dir: Path) -> dict[str, Any]:
        """Load and parse sweep_manifest.json.

        Args:
            sweep_dir: Path to sweep output directory.

        Returns:
            Parsed manifest dictionary.

        Raises:
            FileNotFoundError: If manifest does not exist.
            MetricComputationError: If manifest is invalid JSON.
        """
        manifest_path = sweep_dir / "sweep_manifest.json"

        if not manifest_path.exists():
            raise FileNotFoundError(f"Sweep manifest not found: {manifest_path}")

        try:
            with open(manifest_path, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise MetricComputationError(
                f"Invalid JSON in sweep manifest: {manifest_path}: {e}"
            ) from e

    def _load_run_data(
        self, runs_data: list[dict[str, Any]], runs_dir: Path
    ) -> list[dict[str, Any]]:
        """Load answer and justification data for all runs.

        Args:
            runs_data: List of run records from sweep manifest.
            runs_dir: Path to runs directory.

        Returns:
            List of run records augmented with 'answer' and 'justification'.
        """
        result = []

        for run in runs_data:
            axis_values = run.get("axis_values", {})
            seed = run.get("seed")

            # Build directory name (same logic as M04)
            dir_name = self._build_run_directory_name(axis_values, seed)
            run_dir = runs_dir / dir_name

            # Load trace pack
            trace_pack_path = run_dir / "trace_pack.jsonl"
            traces = load_trace_pack(trace_pack_path)

            # Extract answer and justification
            answer = extract_answer(traces)
            justification = extract_justification(traces)

            result.append({
                "axis_values": axis_values,
                "seed": seed,
                "answer": answer,
                "justification": justification,
            })

        return result

    def _build_run_directory_name(
        self, axis_values: dict[str, Any], seed: int
    ) -> str:
        """Build directory name for a run (mirrors M04 logic).

        Args:
            axis_values: Dictionary mapping axis names to values.
            seed: The seed for this run.

        Returns:
            Deterministic directory name string.
        """
        segments = []
        for name in sorted(axis_values.keys()):
            encoded_value = encode_axis_value(axis_values[name])
            segments.append(f"{name}={encoded_value}")
        segments.append(f"seed={seed}")
        return "_".join(segments)

    def _compute_esi(
        self,
        axes_def: dict[str, list[Any]],
        run_records: list[dict[str, Any]],
        baseline: dict[str, Any],
    ) -> list[ESIMetric]:
        """Compute ESI metrics for all axes.

        ESI measures the proportion of runs where the answer matches baseline,
        grouped by axis value.

        Args:
            axes_def: Axes definition from sweep manifest.
            run_records: List of run records with answers.
            baseline: The baseline run record.

        Returns:
            List of ESIMetric objects, sorted by axis name.
        """
        baseline_answer = baseline["answer"]

        # Get sorted axis names
        sorted_axes = sorted(axes_def.keys())

        esi_metrics = []

        for axis_name in sorted_axes:
            axis_values = axes_def[axis_name]

            # Group runs by axis value for this axis
            # value_key -> list of (matches_baseline: bool)
            value_matches: dict[str, list[bool]] = defaultdict(list)

            for run in run_records:
                run_axis_value = run["axis_values"].get(axis_name)
                value_key = encode_axis_value(run_axis_value)

                matches = run["answer"] == baseline_answer
                value_matches[value_key].append(matches)

            # Compute ESI per value
            value_scores: dict[str, float] = {}

            # Sort values lexicographically by encoded key
            sorted_value_keys = sorted(value_matches.keys())

            for value_key in sorted_value_keys:
                matches_list = value_matches[value_key]
                if matches_list:
                    proportion = sum(matches_list) / len(matches_list)
                    value_scores[value_key] = round_metric(proportion)
                else:
                    value_scores[value_key] = round_metric(0.0)

            # Compute overall ESI (mean across values)
            if value_scores:
                overall = sum(value_scores.values()) / len(value_scores)
            else:
                overall = 0.0

            esi_metrics.append(
                ESIMetric(
                    axis=axis_name,
                    value_scores=value_scores,
                    overall_score=round_metric(overall),
                )
            )

        return esi_metrics

    def _compute_drift(
        self,
        axes_def: dict[str, list[Any]],
        run_records: list[dict[str, Any]],
        baseline: dict[str, Any],
    ) -> list[DriftMetric]:
        """Compute drift metrics for all axes.

        Drift measures the normalized Levenshtein distance between baseline
        justification and each run's justification, grouped by axis value.

        Args:
            axes_def: Axes definition from sweep manifest.
            run_records: List of run records with justifications.
            baseline: The baseline run record.

        Returns:
            List of DriftMetric objects, sorted by axis name.
        """
        baseline_justification = baseline["justification"]

        # Get sorted axis names
        sorted_axes = sorted(axes_def.keys())

        drift_metrics = []

        for axis_name in sorted_axes:
            # Group runs by axis value for this axis
            # value_key -> list of drift values
            value_drifts: dict[str, list[float]] = defaultdict(list)

            for run in run_records:
                run_axis_value = run["axis_values"].get(axis_name)
                value_key = encode_axis_value(run_axis_value)

                drift = normalized_levenshtein(
                    baseline_justification, run["justification"]
                )
                value_drifts[value_key].append(drift)

            # Compute drift per value
            value_scores: dict[str, float] = {}

            # Sort values lexicographically by encoded key
            sorted_value_keys = sorted(value_drifts.keys())

            for value_key in sorted_value_keys:
                drifts_list = value_drifts[value_key]
                if drifts_list:
                    mean_drift = sum(drifts_list) / len(drifts_list)
                    value_scores[value_key] = round_metric(mean_drift)
                else:
                    value_scores[value_key] = round_metric(0.0)

            # Compute overall drift (mean across values)
            if value_scores:
                overall = sum(value_scores.values()) / len(value_scores)
            else:
                overall = 0.0

            drift_metrics.append(
                DriftMetric(
                    axis=axis_name,
                    value_scores=value_scores,
                    overall_score=round_metric(overall),
                )
            )

        return drift_metrics

