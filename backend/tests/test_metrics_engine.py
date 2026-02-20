"""Tests for CLARITY Metrics Engine (M05).

This test suite validates:
1. Levenshtein correctness (known pairs, edge cases, Unicode)
2. Baseline selection (first run, deterministic)
3. ESI calculation (synthetic sweeps, exact numeric expectations)
4. Drift calculation (controlled justifications, known distances)
5. Determinism (run twice, compare results)
6. Guardrails (no subprocess, no r2l imports, no random, no datetime, no uuid)

All tests use synthetic sweep fixtures created in temporary directories.
"""

from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from app.clarity.metrics import (
    DriftMetric,
    ESIMetric,
    MetricComputationError,
    MetricsResult,
    extract_answer,
    extract_justification,
    levenshtein_distance,
    normalized_levenshtein,
    round_metric,
)
from app.clarity.metrics_engine import MetricsEngine


# =============================================================================
# Test Fixtures
# =============================================================================


def create_trace_pack(
    output: str | None = None,
    answer: str | None = None,
    justification: str | None = None,
) -> str:
    """Create a minimal trace_pack.jsonl content.

    Args:
        output: Value for the "output" field (None to omit).
        answer: Value for the "answer" field (None to omit).
        justification: Value for the "justification" field (None to omit).

    Returns:
        JSONL content as string.
    """
    record: dict[str, Any] = {"step": 1, "event": "inference_complete"}

    if output is not None:
        record["output"] = output
    if answer is not None:
        record["answer"] = answer
    if justification is not None:
        record["justification"] = justification

    return json.dumps(record) + "\n"


def create_synthetic_sweep(
    tmp_path: Path,
    axes: dict[str, list[Any]],
    seeds: list[int],
    run_data: list[dict[str, Any]],
) -> Path:
    """Create a synthetic sweep directory for testing.

    Args:
        tmp_path: Base temp directory.
        axes: Axes definition (name -> values list).
        seeds: List of seeds.
        run_data: List of dicts with keys:
                 - axis_values: dict[str, Any]
                 - seed: int
                 - output: str (for trace pack)
                 - justification: str | None (for trace pack)

    Returns:
        Path to the sweep directory.
    """
    sweep_dir = tmp_path / "sweep_output"
    sweep_dir.mkdir()
    runs_dir = sweep_dir / "runs"
    runs_dir.mkdir()

    # Build manifest runs list
    manifest_runs = []

    for run in run_data:
        axis_values = run["axis_values"]
        seed = run["seed"]
        output = run["output"]
        justification = run.get("justification")

        # Build directory name (same as M04 logic)
        segments = []
        for name in sorted(axis_values.keys()):
            # Simple encoding for tests
            value = axis_values[name]
            encoded = str(value).replace(".", "p").replace("-", "m")
            segments.append(f"{name}={encoded}")
        segments.append(f"seed={seed}")
        dir_name = "_".join(segments)

        run_dir = runs_dir / dir_name
        run_dir.mkdir()

        # Write trace_pack.jsonl
        trace_content = create_trace_pack(
            output=output,
            justification=justification,
        )
        (run_dir / "trace_pack.jsonl").write_text(trace_content, encoding="utf-8")

        # Write manifest.json (minimal)
        manifest_content = {
            "run_id": f"test-{dir_name}",
            "timestamp": "2026-02-19T12:00:00Z",
            "seed": seed,
            "artifacts": ["trace_pack.jsonl"],
        }
        (run_dir / "manifest.json").write_text(
            json.dumps(manifest_content, indent=2), encoding="utf-8"
        )

        manifest_runs.append({
            "axis_values": axis_values,
            "seed": seed,
            "manifest_hash": "abc123",
        })

    # Write sweep_manifest.json
    sweep_manifest = {
        "axes": axes,
        "seeds": seeds,
        "runs": manifest_runs,
    }
    (sweep_dir / "sweep_manifest.json").write_text(
        json.dumps(sweep_manifest, sort_keys=True, indent=2), encoding="utf-8"
    )

    return sweep_dir


# =============================================================================
# A. Levenshtein Correctness Tests
# =============================================================================


class TestLevenshteinDistance:
    """Tests for levenshtein_distance function."""

    def test_identical_strings(self) -> None:
        """Identical strings have distance 0."""
        assert levenshtein_distance("hello", "hello") == 0

    def test_empty_strings(self) -> None:
        """Empty strings have distance 0."""
        assert levenshtein_distance("", "") == 0

    def test_one_empty_string(self) -> None:
        """Distance from empty to non-empty is length of non-empty."""
        assert levenshtein_distance("", "abc") == 3
        assert levenshtein_distance("abc", "") == 3

    def test_single_insertion(self) -> None:
        """Single character insertion has distance 1."""
        assert levenshtein_distance("cat", "cats") == 1

    def test_single_deletion(self) -> None:
        """Single character deletion has distance 1."""
        assert levenshtein_distance("cats", "cat") == 1

    def test_single_substitution(self) -> None:
        """Single character substitution has distance 1."""
        assert levenshtein_distance("cat", "car") == 1

    def test_kitten_sitting(self) -> None:
        """Classic example: kitten -> sitting = 3."""
        assert levenshtein_distance("kitten", "sitting") == 3

    def test_flaw_lawn(self) -> None:
        """flaw -> lawn = 2."""
        assert levenshtein_distance("flaw", "lawn") == 2

    def test_completely_different(self) -> None:
        """Completely different strings of same length."""
        assert levenshtein_distance("abc", "xyz") == 3

    def test_unicode_characters(self) -> None:
        """Unicode characters are handled correctly."""
        # café -> cafe = 1 (é -> e)
        assert levenshtein_distance("café", "cafe") == 1

    def test_unicode_emoji(self) -> None:
        """Emoji are treated as single characters."""
        assert levenshtein_distance("😀", "😃") == 1
        assert levenshtein_distance("hello😀", "hello😃") == 1

    def test_unicode_cjk(self) -> None:
        """CJK characters are handled correctly."""
        assert levenshtein_distance("日本語", "日本") == 1
        assert levenshtein_distance("你好", "您好") == 1

    def test_symmetric(self) -> None:
        """Distance is symmetric."""
        assert levenshtein_distance("abc", "def") == levenshtein_distance("def", "abc")

    def test_triangle_inequality(self) -> None:
        """Triangle inequality holds."""
        s1, s2, s3 = "abc", "abd", "aef"
        d12 = levenshtein_distance(s1, s2)
        d23 = levenshtein_distance(s2, s3)
        d13 = levenshtein_distance(s1, s3)
        assert d13 <= d12 + d23


class TestNormalizedLevenshtein:
    """Tests for normalized_levenshtein function."""

    def test_identical_strings(self) -> None:
        """Identical strings have normalized distance 0."""
        assert normalized_levenshtein("hello", "hello") == 0.0

    def test_both_empty(self) -> None:
        """Both empty strings returns 0.0 (not division by zero)."""
        assert normalized_levenshtein("", "") == 0.0

    def test_completely_different_same_length(self) -> None:
        """Completely different same-length strings have distance 1.0."""
        assert normalized_levenshtein("ab", "cd") == 1.0

    def test_normalized_value(self) -> None:
        """Normalized distance is in [0, 1]."""
        # kitten -> sitting: distance 3, max_len 7
        result = normalized_levenshtein("kitten", "sitting")
        assert result == pytest.approx(3 / 7, rel=1e-8)


class TestRoundMetric:
    """Tests for round_metric function."""

    def test_rounds_to_8_decimals(self) -> None:
        """Rounds to exactly 8 decimal places."""
        assert round_metric(0.123456789012) == 0.12345679

    def test_preserves_shorter_decimals(self) -> None:
        """Values with fewer decimals are preserved."""
        assert round_metric(0.5) == 0.5
        assert round_metric(1.0) == 1.0

    def test_zero(self) -> None:
        """Zero is preserved."""
        assert round_metric(0.0) == 0.0


# =============================================================================
# B. Answer/Justification Extraction Tests
# =============================================================================


class TestExtractAnswer:
    """Tests for extract_answer function."""

    def test_uses_output_field(self) -> None:
        """Uses 'output' field when present and non-empty."""
        records = [{"step": 1, "output": "The answer is A"}]
        assert extract_answer(records) == "The answer is A"

    def test_uses_answer_field_when_no_output(self) -> None:
        """Falls back to 'answer' when 'output' is missing."""
        records = [{"step": 1, "answer": "The answer is B"}]
        assert extract_answer(records) == "The answer is B"

    def test_prefers_output_over_answer(self) -> None:
        """Prefers 'output' over 'answer' when both present."""
        records = [{"step": 1, "output": "Output value", "answer": "Answer value"}]
        assert extract_answer(records) == "Output value"

    def test_skips_empty_output(self) -> None:
        """Skips empty 'output' and uses 'answer'."""
        records = [{"step": 1, "output": "", "answer": "Fallback answer"}]
        assert extract_answer(records) == "Fallback answer"

    def test_raises_on_no_records(self) -> None:
        """Raises MetricComputationError when no records."""
        with pytest.raises(MetricComputationError, match="No trace records"):
            extract_answer([])

    def test_raises_on_missing_both_fields(self) -> None:
        """Raises MetricComputationError when both fields missing."""
        records = [{"step": 1, "event": "complete"}]
        with pytest.raises(MetricComputationError, match="No valid"):
            extract_answer(records)

    def test_uses_last_record(self) -> None:
        """Uses the last record in the list."""
        records = [
            {"step": 1, "output": "First"},
            {"step": 2, "output": "Second"},
            {"step": 3, "output": "Third"},
        ]
        assert extract_answer(records) == "Third"


class TestExtractJustification:
    """Tests for extract_justification function."""

    def test_returns_justification(self) -> None:
        """Returns justification when present."""
        records = [{"step": 1, "justification": "Because of X"}]
        assert extract_justification(records) == "Because of X"

    def test_returns_empty_when_missing(self) -> None:
        """Returns empty string when justification missing."""
        records = [{"step": 1, "output": "Answer"}]
        assert extract_justification(records) == ""

    def test_coerces_non_string(self) -> None:
        """Coerces non-string justification to string."""
        records = [{"step": 1, "justification": 42}]
        assert extract_justification(records) == "42"

        records = [{"step": 1, "justification": ["a", "b"]}]
        assert extract_justification(records) == "['a', 'b']"

    def test_raises_on_no_records(self) -> None:
        """Raises MetricComputationError when no records."""
        with pytest.raises(MetricComputationError, match="No trace records"):
            extract_justification([])

    def test_uses_last_record(self) -> None:
        """Uses the last record in the list."""
        records = [
            {"step": 1, "justification": "First"},
            {"step": 2, "justification": "Second"},
        ]
        assert extract_justification(records) == "Second"

    def test_does_not_fallback_to_output(self) -> None:
        """Does NOT fall back to output field."""
        records = [{"step": 1, "output": "Some output"}]
        assert extract_justification(records) == ""


# =============================================================================
# C. Baseline Selection Tests
# =============================================================================


class TestBaselineSelection:
    """Tests for baseline selection in MetricsEngine."""

    def test_baseline_is_first_run(self, tmp_path: Path) -> None:
        """Baseline is the first run in the manifest."""
        # Create sweep with known order
        axes = {"brightness": [0.8, 1.0, 1.2]}
        seeds = [42]
        run_data = [
            {"axis_values": {"brightness": 0.8}, "seed": 42, "output": "Answer A"},
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "Answer B"},
            {"axis_values": {"brightness": 1.2}, "seed": 42, "output": "Answer C"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        # ESI should show 1.0 for first value (matches itself)
        # and lower for others (don't match baseline)
        assert result.esi[0].value_scores["0p8"] == 1.0
        assert result.esi[0].value_scores["1p0"] == 0.0  # "Answer B" != "Answer A"
        assert result.esi[0].value_scores["1p2"] == 0.0  # "Answer C" != "Answer A"

    def test_baseline_deterministic(self, tmp_path: Path) -> None:
        """Baseline selection is deterministic across runs."""
        axes = {"brightness": [1.0]}
        seeds = [42]
        run_data = [
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "Stable"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result1 = engine.compute(sweep_dir)
        result2 = engine.compute(sweep_dir)

        # Results should be identical
        assert result1.esi == result2.esi
        assert result1.drift == result2.drift


# =============================================================================
# D. ESI Calculation Tests
# =============================================================================


class TestESICalculation:
    """Tests for ESI (Evidence Stability Index) calculation."""

    def test_all_matching_answers(self, tmp_path: Path) -> None:
        """All runs matching baseline gives ESI = 1.0."""
        axes = {"brightness": [0.8, 1.0, 1.2]}
        seeds = [42, 43]
        run_data = [
            {"axis_values": {"brightness": 0.8}, "seed": 42, "output": "Same answer"},
            {"axis_values": {"brightness": 0.8}, "seed": 43, "output": "Same answer"},
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "Same answer"},
            {"axis_values": {"brightness": 1.0}, "seed": 43, "output": "Same answer"},
            {"axis_values": {"brightness": 1.2}, "seed": 42, "output": "Same answer"},
            {"axis_values": {"brightness": 1.2}, "seed": 43, "output": "Same answer"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        assert len(result.esi) == 1
        esi = result.esi[0]
        assert esi.axis == "brightness"
        assert esi.overall_score == 1.0
        assert esi.value_scores["0p8"] == 1.0
        assert esi.value_scores["1p0"] == 1.0
        assert esi.value_scores["1p2"] == 1.0

    def test_no_matching_answers(self, tmp_path: Path) -> None:
        """No runs matching baseline gives ESI = proportion of baseline value."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            {"axis_values": {"brightness": 0.8}, "seed": 42, "output": "Baseline"},
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "Different"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        esi = result.esi[0]
        # 0.8 matches baseline (1.0), 1.0 doesn't (0.0)
        assert esi.value_scores["0p8"] == 1.0
        assert esi.value_scores["1p0"] == 0.0
        # Overall = (1.0 + 0.0) / 2 = 0.5
        assert esi.overall_score == 0.5

    def test_partial_matching(self, tmp_path: Path) -> None:
        """Partial matching gives proportional ESI."""
        axes = {"brightness": [1.0]}
        seeds = [42, 43, 44]
        run_data = [
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "Baseline"},
            {"axis_values": {"brightness": 1.0}, "seed": 43, "output": "Baseline"},
            {"axis_values": {"brightness": 1.0}, "seed": 44, "output": "Different"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        esi = result.esi[0]
        # 2 out of 3 match baseline
        assert esi.value_scores["1p0"] == pytest.approx(2 / 3, rel=1e-8)
        assert esi.overall_score == pytest.approx(2 / 3, rel=1e-8)

    def test_multi_axis_esi(self, tmp_path: Path) -> None:
        """ESI computed per axis in multi-axis sweep."""
        axes = {"brightness": [0.8, 1.0], "contrast": [0.9, 1.0]}
        seeds = [42]
        run_data = [
            # Baseline: brightness=0.8, contrast=0.9
            {
                "axis_values": {"brightness": 0.8, "contrast": 0.9},
                "seed": 42,
                "output": "Baseline",
            },
            {
                "axis_values": {"brightness": 0.8, "contrast": 1.0},
                "seed": 42,
                "output": "Baseline",
            },
            {
                "axis_values": {"brightness": 1.0, "contrast": 0.9},
                "seed": 42,
                "output": "Different",
            },
            {
                "axis_values": {"brightness": 1.0, "contrast": 1.0},
                "seed": 42,
                "output": "Different",
            },
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        # Should have 2 ESI metrics, sorted alphabetically
        assert len(result.esi) == 2
        assert result.esi[0].axis == "brightness"
        assert result.esi[1].axis == "contrast"

    def test_esi_rounding(self, tmp_path: Path) -> None:
        """ESI values are rounded to 8 decimal places."""
        axes = {"brightness": [1.0]}
        seeds = [42, 43, 44]
        run_data = [
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "A"},
            {"axis_values": {"brightness": 1.0}, "seed": 43, "output": "A"},
            {"axis_values": {"brightness": 1.0}, "seed": 44, "output": "B"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        esi = result.esi[0]
        # 2/3 = 0.666666... should round to 0.66666667
        assert esi.value_scores["1p0"] == 0.66666667
        assert esi.overall_score == 0.66666667


# =============================================================================
# E. Drift Calculation Tests
# =============================================================================


class TestDriftCalculation:
    """Tests for Justification Drift calculation."""

    def test_identical_justifications(self, tmp_path: Path) -> None:
        """Identical justifications give drift = 0."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            {
                "axis_values": {"brightness": 0.8},
                "seed": 42,
                "output": "A",
                "justification": "Because X",
            },
            {
                "axis_values": {"brightness": 1.0},
                "seed": 42,
                "output": "B",
                "justification": "Because X",
            },
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        drift = result.drift[0]
        assert drift.value_scores["0p8"] == 0.0
        assert drift.value_scores["1p0"] == 0.0
        assert drift.overall_score == 0.0

    def test_completely_different_justifications(self, tmp_path: Path) -> None:
        """Completely different justifications give drift = 1.0."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            {
                "axis_values": {"brightness": 0.8},
                "seed": 42,
                "output": "A",
                "justification": "ab",
            },
            {
                "axis_values": {"brightness": 1.0},
                "seed": 42,
                "output": "B",
                "justification": "cd",
            },
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        drift = result.drift[0]
        # baseline="ab", run="cd" -> distance=2, max_len=2 -> 1.0
        assert drift.value_scores["0p8"] == 0.0  # baseline matches itself
        assert drift.value_scores["1p0"] == 1.0  # completely different

    def test_partial_drift(self, tmp_path: Path) -> None:
        """Partial changes give proportional drift."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            {
                "axis_values": {"brightness": 0.8},
                "seed": 42,
                "output": "A",
                "justification": "hello",
            },
            {
                "axis_values": {"brightness": 1.0},
                "seed": 42,
                "output": "B",
                "justification": "hallo",
            },
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        drift = result.drift[0]
        # "hello" -> "hallo": distance=1, max_len=5 -> 0.2
        assert drift.value_scores["1p0"] == 0.2

    def test_empty_justifications(self, tmp_path: Path) -> None:
        """Empty justifications give drift = 0."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            {"axis_values": {"brightness": 0.8}, "seed": 42, "output": "A"},
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "B"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        drift = result.drift[0]
        # Both empty -> drift = 0
        assert drift.value_scores["0p8"] == 0.0
        assert drift.value_scores["1p0"] == 0.0

    def test_baseline_empty_run_nonempty(self, tmp_path: Path) -> None:
        """Drift from empty baseline to non-empty justification."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            # Baseline has no justification
            {"axis_values": {"brightness": 0.8}, "seed": 42, "output": "A"},
            # This run has justification
            {
                "axis_values": {"brightness": 1.0},
                "seed": 42,
                "output": "B",
                "justification": "Because",
            },
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        drift = result.drift[0]
        # "" -> "Because": distance=7, max_len=7 -> 1.0
        assert drift.value_scores["1p0"] == 1.0

    def test_drift_rounding(self, tmp_path: Path) -> None:
        """Drift values are rounded to 8 decimal places."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            {
                "axis_values": {"brightness": 0.8},
                "seed": 42,
                "output": "A",
                "justification": "abc",
            },
            {
                "axis_values": {"brightness": 1.0},
                "seed": 42,
                "output": "B",
                "justification": "abd",
            },
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        drift = result.drift[0]
        # "abc" -> "abd": distance=1, max_len=3 -> 0.333...
        assert drift.value_scores["1p0"] == 0.33333333

    def test_unicode_justifications(self, tmp_path: Path) -> None:
        """Unicode justifications are handled correctly."""
        axes = {"brightness": [0.8, 1.0]}
        seeds = [42]
        run_data = [
            {
                "axis_values": {"brightness": 0.8},
                "seed": 42,
                "output": "A",
                "justification": "café",
            },
            {
                "axis_values": {"brightness": 1.0},
                "seed": 42,
                "output": "B",
                "justification": "cafe",
            },
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        drift = result.drift[0]
        # "café" -> "cafe": distance=1, max_len=4 -> 0.25
        assert drift.value_scores["1p0"] == 0.25


# =============================================================================
# F. Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests verifying deterministic behavior."""

    def test_compute_twice_identical_results(self, tmp_path: Path) -> None:
        """Running compute() twice produces identical MetricsResult."""
        axes = {"brightness": [0.8, 1.0, 1.2], "contrast": [0.9, 1.0]}
        seeds = [42, 43]
        run_data = []
        for b in [0.8, 1.0, 1.2]:
            for c in [0.9, 1.0]:
                for s in [42, 43]:
                    run_data.append({
                        "axis_values": {"brightness": b, "contrast": c},
                        "seed": s,
                        "output": f"answer_{b}_{c}_{s}",
                        "justification": f"just_{b}_{c}_{s}",
                    })
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result1 = engine.compute(sweep_dir)
        result2 = engine.compute(sweep_dir)

        # Compare ESI
        assert result1.esi == result2.esi

        # Compare Drift
        assert result1.drift == result2.drift

    def test_metrics_sorted_by_axis(self, tmp_path: Path) -> None:
        """Metrics are sorted alphabetically by axis name."""
        # Use unsorted axis names
        axes = {"zebra": [1.0], "alpha": [1.0], "middle": [1.0]}
        seeds = [42]
        run_data = [
            {"axis_values": {"zebra": 1.0, "alpha": 1.0, "middle": 1.0}, "seed": 42, "output": "A"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        # Axes should be sorted
        axis_names = [m.axis for m in result.esi]
        assert axis_names == ["alpha", "middle", "zebra"]

        axis_names = [m.axis for m in result.drift]
        assert axis_names == ["alpha", "middle", "zebra"]

    def test_value_scores_sorted(self, tmp_path: Path) -> None:
        """Value scores are sorted lexicographically by encoded key."""
        axes = {"brightness": [1.2, 0.8, 1.0]}  # Intentionally unsorted
        seeds = [42]
        run_data = [
            {"axis_values": {"brightness": 1.2}, "seed": 42, "output": "A"},
            {"axis_values": {"brightness": 0.8}, "seed": 42, "output": "B"},
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "C"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        # Value keys should be sorted: 0p8, 1p0, 1p2
        esi_keys = list(result.esi[0].value_scores.keys())
        assert esi_keys == sorted(esi_keys)


# =============================================================================
# G. Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in MetricsEngine."""

    def test_raises_on_empty_sweep(self, tmp_path: Path) -> None:
        """Raises MetricComputationError on empty sweep."""
        sweep_dir = tmp_path / "sweep_output"
        sweep_dir.mkdir()

        # Write manifest with no runs
        manifest = {"axes": {"brightness": [1.0]}, "seeds": [42], "runs": []}
        (sweep_dir / "sweep_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

        engine = MetricsEngine()
        with pytest.raises(MetricComputationError, match="zero runs"):
            engine.compute(sweep_dir)

    def test_raises_on_missing_manifest(self, tmp_path: Path) -> None:
        """Raises FileNotFoundError on missing sweep_manifest.json."""
        sweep_dir = tmp_path / "sweep_output"
        sweep_dir.mkdir()

        engine = MetricsEngine()
        with pytest.raises(FileNotFoundError, match="sweep_manifest"):
            engine.compute(sweep_dir)

    def test_raises_on_missing_trace_pack(self, tmp_path: Path) -> None:
        """Raises FileNotFoundError on missing trace_pack.jsonl."""
        sweep_dir = tmp_path / "sweep_output"
        sweep_dir.mkdir()
        runs_dir = sweep_dir / "runs"
        runs_dir.mkdir()

        # Create run directory without trace_pack
        run_dir = runs_dir / "brightness=1p0_seed=42"
        run_dir.mkdir()

        manifest = {
            "axes": {"brightness": [1.0]},
            "seeds": [42],
            "runs": [{"axis_values": {"brightness": 1.0}, "seed": 42, "manifest_hash": "abc"}],
        }
        (sweep_dir / "sweep_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

        engine = MetricsEngine()
        with pytest.raises(FileNotFoundError, match="trace_pack"):
            engine.compute(sweep_dir)

    def test_raises_on_missing_answer(self, tmp_path: Path) -> None:
        """Raises MetricComputationError on missing answer in trace."""
        axes = {"brightness": [1.0]}
        seeds = [42]

        sweep_dir = tmp_path / "sweep_output"
        sweep_dir.mkdir()
        runs_dir = sweep_dir / "runs"
        runs_dir.mkdir()

        run_dir = runs_dir / "brightness=1p0_seed=42"
        run_dir.mkdir()

        # Write trace_pack without output or answer
        trace_content = json.dumps({"step": 1, "event": "done"}) + "\n"
        (run_dir / "trace_pack.jsonl").write_text(trace_content, encoding="utf-8")

        manifest = {
            "axes": axes,
            "seeds": seeds,
            "runs": [{"axis_values": {"brightness": 1.0}, "seed": 42, "manifest_hash": "abc"}],
        }
        (sweep_dir / "sweep_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

        engine = MetricsEngine()
        with pytest.raises(MetricComputationError, match="No valid"):
            engine.compute(sweep_dir)


# =============================================================================
# H. Guardrail Tests
# =============================================================================


class TestM05Guardrails:
    """AST-based guardrail tests for M05 modules."""

    def test_no_subprocess_import_in_metrics(self) -> None:
        """metrics.py does not import subprocess."""
        from app.clarity import metrics

        source = inspect.getsource(metrics)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "subprocess", "subprocess import forbidden"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "subprocess", "subprocess import forbidden"

    def test_no_subprocess_import_in_metrics_engine(self) -> None:
        """metrics_engine.py does not import subprocess."""
        from app.clarity import metrics_engine

        source = inspect.getsource(metrics_engine)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "subprocess", "subprocess import forbidden"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "subprocess", "subprocess import forbidden"

    def test_no_r2l_import_in_metrics(self) -> None:
        """metrics.py does not import r2l."""
        from app.clarity import metrics

        source = inspect.getsource(metrics)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("r2l"), "r2l import forbidden"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("r2l"), "r2l import forbidden"

    def test_no_r2l_import_in_metrics_engine(self) -> None:
        """metrics_engine.py does not import r2l."""
        from app.clarity import metrics_engine

        source = inspect.getsource(metrics_engine)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("r2l"), "r2l import forbidden"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("r2l"), "r2l import forbidden"

    def test_no_random_import_in_metrics(self) -> None:
        """metrics.py does not import random."""
        from app.clarity import metrics

        source = inspect.getsource(metrics)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "random", "random import forbidden"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "random", "random import forbidden"

    def test_no_random_import_in_metrics_engine(self) -> None:
        """metrics_engine.py does not import random."""
        from app.clarity import metrics_engine

        source = inspect.getsource(metrics_engine)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "random", "random import forbidden"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "random", "random import forbidden"

    def test_no_datetime_now_in_metrics(self) -> None:
        """metrics.py does not use datetime.now in code."""
        from app.clarity import metrics

        source = inspect.getsource(metrics)
        tree = ast.parse(source)

        # Look for datetime.now() calls in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr == "now":
                    # Check if it's being called (datetime.now())
                    parent = getattr(node, "_parent", None)
                    # If we find .now attribute access, that's suspicious
                    # Check if the value is 'datetime'
                    if isinstance(node.value, ast.Attribute):
                        if node.value.attr == "datetime":
                            raise AssertionError("datetime.now usage forbidden")
                    elif isinstance(node.value, ast.Name):
                        if node.value.id == "datetime":
                            raise AssertionError("datetime.now usage forbidden")

    def test_no_datetime_now_in_metrics_engine(self) -> None:
        """metrics_engine.py does not use datetime.now in code."""
        from app.clarity import metrics_engine

        source = inspect.getsource(metrics_engine)
        tree = ast.parse(source)

        # Look for datetime.now() calls in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr == "now":
                    if isinstance(node.value, ast.Attribute):
                        if node.value.attr == "datetime":
                            raise AssertionError("datetime.now usage forbidden")
                    elif isinstance(node.value, ast.Name):
                        if node.value.id == "datetime":
                            raise AssertionError("datetime.now usage forbidden")

    def test_no_uuid_in_metrics(self) -> None:
        """metrics.py does not import uuid."""
        from app.clarity import metrics

        source = inspect.getsource(metrics)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "uuid", "uuid import forbidden"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "uuid", "uuid import forbidden"

    def test_no_uuid_in_metrics_engine(self) -> None:
        """metrics_engine.py does not import uuid."""
        from app.clarity import metrics_engine

        source = inspect.getsource(metrics_engine)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "uuid", "uuid import forbidden"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "uuid", "uuid import forbidden"

    def test_no_numpy_in_metrics(self) -> None:
        """metrics.py does not import numpy."""
        from app.clarity import metrics

        source = inspect.getsource(metrics)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("numpy", "np"), "numpy import forbidden"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("numpy"), "numpy import forbidden"

    def test_no_numpy_in_metrics_engine(self) -> None:
        """metrics_engine.py does not import numpy."""
        from app.clarity import metrics_engine

        source = inspect.getsource(metrics_engine)
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("numpy", "np"), "numpy import forbidden"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("numpy"), "numpy import forbidden"


# =============================================================================
# I. Integration Tests
# =============================================================================


class TestMetricsIntegration:
    """Integration tests for the full metrics pipeline."""

    def test_full_sweep_computation(self, tmp_path: Path) -> None:
        """Full sweep with multiple axes, seeds, and realistic data."""
        axes = {"brightness": [0.8, 1.0, 1.2], "contrast": [0.9, 1.0, 1.1]}
        seeds = [42, 43]

        # Generate run data
        run_data = []
        answers = {
            (0.8, 0.9): "Normal findings",
            (0.8, 1.0): "Normal findings",
            (0.8, 1.1): "Minor opacity",
            (1.0, 0.9): "Normal findings",
            (1.0, 1.0): "Normal findings",
            (1.0, 1.1): "Normal findings",
            (1.2, 0.9): "Normal findings",
            (1.2, 1.0): "Minor opacity",
            (1.2, 1.1): "Minor opacity",
        }

        for b in [0.8, 1.0, 1.2]:
            for c in [0.9, 1.0, 1.1]:
                for s in [42, 43]:
                    run_data.append({
                        "axis_values": {"brightness": b, "contrast": c},
                        "seed": s,
                        "output": answers[(b, c)],
                        "justification": f"Analysis at b={b}, c={c}",
                    })

        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        # Verify structure
        assert len(result.esi) == 2
        assert len(result.drift) == 2
        assert result.esi[0].axis == "brightness"
        assert result.esi[1].axis == "contrast"

        # Verify ESI is in valid range
        for esi in result.esi:
            assert 0.0 <= esi.overall_score <= 1.0
            for score in esi.value_scores.values():
                assert 0.0 <= score <= 1.0

        # Verify drift is in valid range
        for drift in result.drift:
            assert 0.0 <= drift.overall_score <= 1.0
            for score in drift.value_scores.values():
                assert 0.0 <= score <= 1.0

    def test_dataclass_immutability(self, tmp_path: Path) -> None:
        """Verify all metric dataclasses are frozen."""
        axes = {"brightness": [1.0]}
        seeds = [42]
        run_data = [
            {"axis_values": {"brightness": 1.0}, "seed": 42, "output": "A"},
        ]
        sweep_dir = create_synthetic_sweep(tmp_path, axes, seeds, run_data)

        engine = MetricsEngine()
        result = engine.compute(sweep_dir)

        # ESIMetric should be frozen
        with pytest.raises(AttributeError):
            result.esi[0].axis = "modified"  # type: ignore

        # DriftMetric should be frozen
        with pytest.raises(AttributeError):
            result.drift[0].axis = "modified"  # type: ignore

        # MetricsResult should be frozen
        with pytest.raises(AttributeError):
            result.esi = ()  # type: ignore

