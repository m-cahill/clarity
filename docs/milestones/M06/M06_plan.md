# 📌 M06 Plan — Robustness Surfaces

**Status:** In Progress  
**Baseline:** M05 (`v0.0.6-m05`)

---

## Milestone Objective

Implement deterministic robustness surface construction from M05 metrics output.

M06 will:

* Consume `MetricsResult` from `MetricsEngine`
* Build axis-aligned robustness surfaces for:
  * ESI
  * Justification Drift
* Produce structured surface representations suitable for:
  * Visualization
  * Gradient estimation (M07)
  * Monte Carlo stability analysis (M08)
* Maintain full determinism guarantees

M06 is a **pure analytical layer** — no R2L invocation, no perturbation execution.

---

## Architectural Positioning

```
M02 → Perturbations
M03 → R2L Harness
M04 → Sweep Orchestrator
M05 → Metrics (ESI + Drift)
M06 → Robustness Surfaces   ← NEW
M07 → Gradient / Stability Estimation
```

M06 operates strictly on:

* `MetricsResult` (from M05)
* No filesystem scanning
* No sweep_manifest.json reading (metrics → surfaces layer only)

---

## New Modules

### 1️⃣ `backend/app/clarity/surfaces.py`

#### Data Models (Frozen Dataclasses)

```python
SurfacePoint
AxisSurface
RobustnessSurface
SurfaceComputationError
```

#### `SurfacePoint`

Represents one axis value point.

Fields:

* `axis: str`
* `value: str` (encoded value from M04)
* `esi: float`
* `drift: float`

#### `AxisSurface`

Represents one axis surface.

Fields:

* `axis: str`
* `points: tuple[SurfacePoint, ...]`
* `mean_esi: float`
* `mean_drift: float`
* `variance_esi: float`
* `variance_drift: float`

#### `RobustnessSurface`

Represents full surface across axes.

Fields:

* `axes: tuple[AxisSurface, ...]`
* `global_mean_esi: float`
* `global_mean_drift: float`
* `global_variance_esi: float`
* `global_variance_drift: float`

All floats rounded to 8 decimals at storage time.

### 2️⃣ `backend/app/clarity/surface_engine.py`

#### Class

```python
SurfaceEngine
```

#### Method

```python
compute(metrics: MetricsResult) -> RobustnessSurface
```

#### Responsibilities

* Deterministic axis ordering (alphabetical)
* Deterministic value ordering (lexicographic)
* Compute:
  * Per-axis mean
  * Per-axis variance
  * Global mean
  * Global variance
* No numpy
* Pure Python statistics
* No randomness
* No filesystem writes

---

## Mathematical Definitions

Given axis A with value set V:

For each value v:

* ESI_v
* Drift_v

Axis Mean:

```
mean_esi = sum(ESI_v) / |V|
mean_drift = sum(Drift_v) / |V|
```

Axis Variance (population variance):

```
variance = sum((x - mean)^2) / |V|
```

Global metrics:

* Compute across all axis/value points

All results rounded to 8 decimals.

---

## Determinism Constraints

* No random
* No datetime
* No uuid
* No numpy
* No subprocess
* No r2l imports
* All floats rounded at assignment
* Input ordering preserved from MetricsResult
* Frozen dataclasses

---

## Locked Answers

### Q1: MetricsResult Structure

M06 consumes only what `MetricsEngine.compute()` returns — the `MetricsResult` dataclass.

### Q2: Axis/Value Mapping

MetricsResult is sufficient. Do not read `sweep_manifest.json` in M06.

* `MetricsResult.esi` contains per-axis `ESIMetric` objects with `value_scores`
* `MetricsResult.drift` contains per-axis `DriftMetric` objects with `value_scores`

M06 should:

* Join ESI + Drift by `axis` name
* For each axis, join values by the value key (string) used in `value_scores`

If an axis exists in ESI but not Drift (or vice versa), raise `SurfaceComputationError`.
If a value exists in one but not the other for the same axis, raise.

### Q3: Synthetic Test Data

Create synthetic metrics dataset inside tests. Construct `MetricsResult` directly.

### Q4: Surface JSON Export

Include `to_dict()` methods for future serialization, but no file I/O in M06.
`to_dict()` must be deterministic (sorted keys, deterministic ordering).

### Q5: Empty/Edge Cases

* Empty input (no axes): raise `SurfaceComputationError`
* Single-value axes: Allowed. Variance = 0.0 (rounded)
* NaN/inf values: Reject with `SurfaceComputationError`. Use `math.isfinite()`

---

## Test Plan

### `backend/tests/test_surface_engine.py`

Minimum 50–70 tests.

#### Categories

1. **Surface Construction**
   * Single axis
   * Multiple axes
   * Single value axis
   * Multi-value axis

2. **Statistical Correctness**
   * Known small datasets with exact expected mean/variance
   * Zero variance cases
   * Asymmetric distributions

3. **Determinism**
   * Compute twice → identical RobustnessSurface
   * Ordering identical

4. **Rounding**
   * 8-decimal rounding enforced

5. **Guardrails**
   AST-based checks ensuring:
   * No numpy
   * No subprocess
   * No r2l
   * No random
   * No datetime
   * No uuid

6. **Error Handling**
   * Empty MetricsResult → raise SurfaceComputationError
   * Missing axis values → error
   * NaN/inf values → error

7. **to_dict() Serialization**
   * Verify deterministic output
   * Verify sorted keys
   * Verify round-trip structure

---

## Coverage Targets

| Module            | Target                                |
| ----------------- | ------------------------------------- |
| surfaces.py       | ≥95%                                  |
| surface_engine.py | ≥90%                                  |
| Overall backend   | ≥90% (no regression below M05 94.61%) |

---

## Exit Criteria

M06 is complete when:

* RobustnessSurface computed deterministically
* All statistical calculations verified by known datasets
* 8-decimal rounding enforced everywhere
* CI green first run
* Coverage targets met
* No boundary violations
* No HIGH issues introduced

---

## What M06 Enables

After M06, CLARITY will have:

* Axis-level robustness surfaces
* Quantified sensitivity to perturbations
* Structural stability metrics
* Foundation for:
  * Gradient estimation (M07)
  * Surface visualization
  * Kaggle submission material

---

## What Not To Do In M06

* No visualization
* No plotting
* No file output
* No integration with real M04 output yet (that's INT-001)
* No performance optimization
* No Monte Carlo

This is strictly deterministic surface construction.

---

## Governance Artifacts

* `docs/milestones/M06/M06_plan.md` ← this file
* `docs/milestones/M06/M06_toolcalls.md`
* `docs/milestones/M06/M06_run1.md` (after CI)
* `docs/milestones/M06/M06_audit.md` (after completion)
* `docs/milestones/M06/M06_summary.md` (after completion)
