# M05 — Metrics Core (ESI + Justification Drift)

**Status:** In Progress  
**Baseline:** M04 (`v0.0.5-m04`)  
**Branch:** `m05-metrics-core` (to be created)

---

## Objective

Compute:

1. **ESI — Evidence Stability Index**
2. **Justification Drift Metric**

Using only:

* Sweep output from M04
* Artifacts from M03
* No R2L internal imports
* No randomness
* Pure deterministic math

M05 must consume sweep results and produce reproducible numeric outputs.

This is the milestone that transforms CLARITY from a **sweep executor** into a **robustness measurement instrument**.

---

## Non-Negotiable Constraints

* No new randomness
* No `datetime.now()` / `uuid`
* No r2l imports
* No numpy (pure Python only)
* No subprocess
* All input data comes from:
  * `sweep_manifest.json`
  * Per-run `manifest.json`
  * Per-run `trace_pack.jsonl`
* All metric outputs must be deterministic given identical sweep output directory
* No concurrency
* No persistence layer yet
* No UI integration

---

## Locked Answers (Authoritative for M05)

### Answer Extraction from `trace_pack.jsonl`

Use the **last JSONL record**:

1. If `"output"` exists and is a non-empty string → use it
2. Else if `"answer"` exists and is a non-empty string → use it
3. Else → raise `MetricComputationError`

### Justification Extraction

* If `"justification"` missing → empty string `""`
* If present but non-string → coerce with `str(...)` (deterministic)
* Do NOT fall back to `"output"`
* Do NOT raise if missing

### Baseline Definition

Baseline = **first run in deterministic execution order**:
* Axes sorted alphabetically
* Axis values in declared order
* Seeds in declared order
* Baseline is `run[0]`

Do NOT search for identity values.

### MetricComputationError Location

Define in `metrics.py` alongside dataclasses.

### Empty Sweep Handling

Raise `MetricComputationError` if sweep has zero runs.

### Unicode in Levenshtein

Treat strings as Python `str` and compute distance by character, not bytes.
Tests must include at least one Unicode case.

### Rounding Rule

Round all stored float outputs to **8 decimal places** at the moment of storage in `value_scores` and `overall_score`.

### Ordering Rule

Metrics must be emitted in deterministic order:
* Axes alphabetical
* Values lexicographically by their serialized directory-safe encoding

---

## Deliverables

### A. Metrics Module (`backend/app/clarity/metrics.py`)

#### Data Structures

```python
@dataclass(frozen=True)
class ESIMetric:
    axis: str
    value_scores: dict[str, float]
    overall_score: float

@dataclass(frozen=True)
class DriftMetric:
    axis: str
    value_scores: dict[str, float]
    overall_score: float

@dataclass(frozen=True)
class MetricsResult:
    esi: tuple[ESIMetric, ...]
    drift: tuple[DriftMetric, ...]
```

All immutable. Sorted by axis name.

#### Exception

```python
class MetricComputationError(Exception):
    """Raised when metric computation fails."""
    pass
```

#### Levenshtein Implementation

Pure Python dynamic programming implementation.
* Character-based, not byte-based
* No external libraries
* Unicode safe

---

### B. Metrics Engine (`backend/app/clarity/metrics_engine.py`)

#### API

```python
class MetricsEngine:
    def compute(self, sweep_dir: Path) -> MetricsResult:
        ...
```

#### Steps

1. Load `sweep_manifest.json`
2. Load all run records
3. Identify baseline run (first in deterministic order)
4. Extract answers + justifications from each run's `trace_pack.jsonl`
5. Group by axis
6. Compute:
   * ESI per axis
   * Drift per axis
7. Return `MetricsResult`

No side effects. No writing files.

---

### C. Test Suite (`backend/tests/test_metrics_engine.py`)

#### Required Test Categories

1. **Levenshtein Correctness**
   * Known pairs
   * Edge cases (empty strings, identical strings)
   * Unicode safe

2. **Baseline Selection**
   * Baseline is first run
   * Deterministic behavior

3. **ESI Calculation**
   * Simple synthetic sweep
   * Known matches/mismatches
   * Exact numeric expectations

4. **Drift Calculation**
   * Controlled justifications
   * Known normalized distances
   * Check rounding to 8 decimals

5. **Determinism**
   * Run `compute()` twice
   * Compare `MetricsResult` objects
   * Compare serialized dict representations

6. **Guardrails**
   * No subprocess
   * No r2l imports
   * No random
   * No `datetime.now`
   * No uuid

---

## Coverage Targets

* `metrics.py` ≥ 95%
* `metrics_engine.py` ≥ 90%
* Overall backend ≥ 94% preferred, must remain ≥ 90%

---

## Formulas

### ESI (Evidence Stability Index)

For axis A:

```
ESI(A) = mean_over_values(
    proportion_of_seeds_where_answer_matches_baseline
)
```

### Justification Drift

Drift per run:

```
drift = levenshtein(baseline_justification, run_justification) / max_len
```

If both strings are empty: drift = 0.0

Aggregate:
* Mean drift across seeds per axis value
* Mean drift per axis

---

## Out of Scope

M05 does NOT:

* Persist metrics
* Plot surfaces
* Estimate gradients
* Perform Monte Carlo decoding
* Integrate UI
* Optimize performance
* Parallelize
* Add GPU logic

---

## Exit Criteria

M05 is complete when:

- [ ] ESI computed correctly on synthetic sweep
- [ ] Drift computed correctly
- [ ] Baseline selection deterministic
- [ ] All numeric outputs deterministic (8 decimal rounding)
- [ ] CI green first run
- [ ] Coverage targets met
- [ ] No HIGH issues introduced
- [ ] No boundary violations

---

## Implementation Notes

1. Do NOT over-generalize metric system
2. Do NOT create plugin architecture
3. Do NOT abstract prematurely
4. Keep metrics isolated and pure
5. No performance tuning

M05 is math + determinism.
