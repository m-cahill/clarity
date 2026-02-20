# 📌 M08 Plan — Counterfactual Probe Engine

**Project:** CLARITY  
**Milestone:** M08 — Counterfactual Probe  
**Baseline Tag:** `v0.0.8-m07`  
**Branch to create:** `m08-counterfactual-probe`  
**Mode:** Additive, deterministic, contract-preserving

---

## 1️⃣ Milestone Objective

M06 → Surfaces  
M07 → Gradients  
M08 → **Counterfactual Stability Probing**

M08 introduces the ability to:

> Systematically mask or perturb specific evidence regions and quantify the causal impact on model reasoning stability.

This moves CLARITY from:

* *Describing robustness*
* *Measuring slope sensitivity*

to:

* **Testing causal evidence dependence**

Without M08, CLARITY cannot answer:

* Does the model truly depend on this region?
* Is the diagnostic claim stable under structured region removal?
* Are gradients reflective of true causal dependence?

---

## 2️⃣ Locked Answers (Design Decisions)

### 2.1 What is a "Region"?

**Region = a physical image-space region (mask), not an axis value.**

* **Definition:** a deterministic **image mask** defined in **normalized image coordinates** (e.g., bbox or a fixed grid cell) that can be applied to the *base image* to produce a counterfactual variant.
* **Not**: a sweep axis/value, and **not** an abstract aggregation slice.
* **Source of region definitions:** **CLARITY-defined** in M08 (not extracted from R2L evidence maps). Evidence-map-derived regions are explicitly **future** (M10+ overlays).

### 2.2 Masking Strategy

**Masking = generate a new deterministic image variant by occluding the region in pixel space**, then run the usual evaluation stack on that variant.

* **Operationally:** apply a deterministic occlusion transform (e.g., fill region with a fixed value — using `128` as neutral gray).
* **Do not** remove points from aggregation.
* **Do not** "neutralize" metrics post-hoc.

Masking happens **at the image artifact level** (input image), not at MetricsResult/SurfacePoint.

### 2.3 Integration Flow

M08 consumes **the baseline run artifacts / sweep outputs** and produces **counterfactual probe artifacts** by re-invoking the CLARITY pipeline.

**Locked flow:**

1. Select a baseline evaluation context (image + prompt/spec + seed list).
2. Produce masked image variant deterministically.
3. Invoke the existing harness path to run inference on masked image (same seeds).
4. Re-run existing analysis stack on the masked run outputs:
   * `MetricsEngine` → `SurfaceEngine` → `GradientEngine`
5. Compare against baseline results and store deltas.

This preserves "CLARITY is a pure consumer of R2L" and keeps counterfactuals as real re-evaluations.

### 2.4 Region ID Semantics

`region_id` is **CLARITY-defined and deterministic**, derived from the region geometry and masking scheme.

**Scheme (locked):** Grid masks with format:
```
grid_r{row}_c{col}_k{grid_size}
```

Example: `grid_r0_c1_k3` = row 0, column 1, in a 3×3 grid.

### 2.5 ProbeResult Granularity

Each `ProbeResult` represents **one region mask applied to one evaluation coordinate**.

**(A)** — "single region masked at a single sweep coordinate."

The atomic unit is `(region_id, axis, value)` → one delta record.

### 2.6 Test Count Threshold

**50 tests is the hard minimum for M08 completion.**

Target: 50–65 tests.

---

## 3️⃣ Explicit Scope Definition

### ✅ In Scope

**Backend Only**

New module:
```
backend/app/clarity/counterfactual_engine.py
```

New dataclasses:
* `RegionMask` — defines grid cell region geometry
* `CounterfactualProbe` — specifies which region at which coordinate
* `ProbeResult` — stores delta metrics for one probe
* `ProbeSurface` — aggregates all probe results with summary statistics
* `CounterfactualComputationError` — raised on probe failures

New functions:
* `generate_grid_masks(k: int)` — produces deterministic grid mask definitions
* `apply_mask(image: bytes, mask: RegionMask, fill_value: int)` — applies occlusion
* `CounterfactualEngine.probe()` — executes probe and returns results

New tests:
```
backend/tests/test_counterfactual_engine.py
```

Integration extension:
* Real sweep → metrics → surface → gradient → counterfactual

### ❌ Out of Scope

* Visualization
* Heatmaps
* Monte Carlo sampling (M09+)
* Gradient step-size generalization
* Performance optimization
* GPU parallelization
* UI
* Evidence-map-derived regions (M10+)

---

## 4️⃣ Data Model

### RegionMask

```python
@dataclass(frozen=True)
class RegionMask:
    region_id: str           # e.g., "grid_r0_c1_k3"
    row: int                 # Grid row (0-indexed)
    col: int                 # Grid column (0-indexed)
    grid_size: int           # Grid dimension (e.g., 3 for 3x3)
    # Normalized coordinates [0.0, 1.0]
    x_min: float
    y_min: float
    x_max: float
    y_max: float
```

### CounterfactualProbe

```python
@dataclass(frozen=True)
class CounterfactualProbe:
    region_id: str           # Which region is masked
    axis: str                # Which perturbation axis
    value: str               # Which axis value (encoded)
```

Represents a specific region mask at a specific sweep coordinate.

### ProbeResult

```python
@dataclass(frozen=True)
class ProbeResult:
    probe: CounterfactualProbe
    baseline_esi: float
    masked_esi: float
    delta_esi: float
    baseline_drift: float
    masked_drift: float
    delta_drift: float
```

Difference between baseline metric and masked metric.

### ProbeSurface

```python
@dataclass(frozen=True)
class ProbeSurface:
    results: tuple[ProbeResult, ...]
    mean_abs_delta_esi: float
    max_abs_delta_esi: float
    mean_abs_delta_drift: float
    max_abs_delta_drift: float
```

---

## 5️⃣ Deterministic Masking Strategy

Masking must be:

* Reproducible
* Value-index stable
* Region-ID deterministic
* Order-preserving

Implementation approach:

* Grid-based: divide image into k×k cells
* Each cell identified by (row, col, k)
* Fill masked region with fixed value (128 — neutral gray)
* Preserve image dimensions
* Preserve other regions unchanged

---

## 6️⃣ Computation Flow

For each probe:

1. Load baseline image artifact.
2. Generate RegionMask for target region.
3. Apply deterministic mask (fill with 128).
4. Run inference on masked image (same seeds).
5. Compute metrics via:
   * `MetricsEngine.compute()`
   * `SurfaceEngine.compute()`
6. Extract point metrics at target coordinate.
7. Compute delta vs baseline metrics.
8. Store deltas (rounded 8 decimals).

---

## 7️⃣ Test Plan (Enterprise-Level)

Target: **50–65 new tests** (minimum 50)

### Categories

#### 1. RegionMask Generation (8–10 tests)
* Grid mask generation produces correct count (k×k)
* Region IDs are deterministic
* Normalized coordinates are correct
* Edge cases: k=1, k=2, k=4

#### 2. Image Masking (8–10 tests)
* Mask application is deterministic
* Fill value is applied correctly
* Non-masked regions unchanged
* Image dimensions preserved
* Different image sizes handled

#### 3. Basic Delta Correctness (6–8 tests)
* Single region mask shifts ESI as expected
* Constant surface → zero delta (if baseline unchanged)
* Known mask → known delta verification

#### 4. Determinism (4–6 tests)
* Double-run equality
* Different engine instances identical
* Order independence

#### 5. Region ID Stability (4–6 tests)
* Same region ID → same masking
* Different region ID → different result
* ID format validation

#### 6. Error Handling (5–7 tests)
* Invalid region ID
* Missing baseline
* Invalid image data
* Empty probe set

#### 7. Integration (4–6 tests)
* Real sweep → counterfactual pipeline
* ProbeSurface immutability
* Full pipeline determinism

#### 8. Serialization (4–6 tests)
* to_dict() deterministic ordering
* All dataclasses serializable
* Sorted keys verified

#### 9. Guardrails AST-based (6 tests)
* No numpy imports
* No subprocess
* No random/uuid/datetime
* No R2L imports

---

## 8️⃣ CI & Governance Requirements

* Maintain ≥95% coverage overall
* ≥95% coverage on new module
* No workflow changes
* No dependency additions
* No CI flake introduction
* First-run green required

---

## 9️⃣ Definition of Done

M08 complete when:

- [ ] `counterfactual_engine.py` implemented
- [ ] ≥50 new tests
- [ ] ≥95% coverage on new module
- [ ] Integration test covers full pipeline
- [ ] CI green first run
- [ ] M08_plan.md created ✅
- [ ] M08_toolcalls.md maintained ✅
- [ ] M08_run1.md created
- [ ] clarity.md updated
- [ ] Tag prepared (`v0.0.9-m08`)

---

## 🔟 Risk Assessment

| Risk | Mitigation |
|------|------------|
| Mask logic non-deterministic | Fixed fill value (128), grid-based geometry |
| Artifact mutation | Deep copy enforcement |
| Performance regression | Small fixture scope, baseline-only probing |
| Metric drift misinterpreted | Explicit delta-only storage with baseline values |
| Region ordering instability | Stable sorting by region_id |
| Image dimension variance | Normalized coordinates [0.0, 1.0] |

---

## 1️⃣1️⃣ Architecture Constraints

### Hard Rules

* No direct R2L imports.
* Use existing artifact loader.
* Deterministic masking only.
* No randomness.
* No numpy.
* No datetime.
* No subprocess.
* 8-decimal rounding at storage.
* Frozen dataclasses.
* Deterministic ordering.

M08 must be a **pure consumer extension**, just like M07.

---

## 1️⃣2️⃣ Minimal Implementation Strategy

For smallest-possible audit-clean implementation:

1. **Grid-based masks** (3×3 = 9 regions)
2. **Probe baseline coordinate only** (no perturbation applied)
3. **Use 1–2 seeds** in fixtures
4. **Fixture-backed integration tests** (M07 INT-001 style)

This keeps the milestone PR-sized while delivering true counterfactual evaluation.

---

## 1️⃣3️⃣ Branch Protocol

```bash
git checkout -b m08-counterfactual-probe
```

Then:

1. Create module
2. Create test suite
3. Implement incrementally
4. Run full test matrix locally
5. Push
6. Analyze CI
7. Await decision
8. Generate audit + summary

---

## 1️⃣4️⃣ Audit Expectations (Pre-Declared)

M08 audit must explicitly evaluate:

* Causal delta correctness
* Determinism under masking
* No hidden R2L coupling
* No gradient mutation
* No schema drift

---

## 1️⃣5️⃣ Explicit Constraints

* No opportunistic refactors.
* No schema edits.
* No contract changes.
* No workflow edits.
* No dependency changes.
* Additive only.

---

## 1️⃣6️⃣ Expected System Evolution

After M08, CLARITY will support:

* Robustness surfaces (M06)
* Gradient sensitivity (M07)
* **Causal region dependence testing (M08)**

System maturity progression:

> Descriptive → Sensitivity-aware → Causality-aware

---

*End of M08 Plan*
