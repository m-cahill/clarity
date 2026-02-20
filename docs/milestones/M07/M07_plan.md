# 📌 M07 Plan — Gradient / Stability Estimation

**Project:** CLARITY
**Milestone:** M07 — Gradient / Stability Estimation
**Branch to create:** `m07-gradient-stability`
**Baseline:** `v0.0.7-m06` (`0d3ba66`)
**Mode:** Additive, deterministic, contract-preserving
**Scope Size:** PR-sized, computation-only, no visualization

---

## 1️⃣ Milestone Objective

M06 established deterministic robustness surface construction.

M07 must:

1. Compute **local gradient estimates** over robustness surfaces.
2. Quantify **stability metrics** derived from those gradients.
3. Extend deterministic analysis without breaking:
   - Surface contract
   - R2L boundary
   - Determinism guarantees
   - Serialization guarantees

M07 transforms surfaces from *descriptive statistics* into *sensitivity measurements*.

> Without M07, CLARITY can describe surfaces but cannot quantify slope instability or detect "failure cliffs."

---

## 2️⃣ Explicit Scope Definition

### ✅ In Scope

**Backend Only**

New module:
```
backend/app/clarity/gradient_engine.py
```

New dataclasses (in new module):
- `GradientPoint`
- `AxisGradient`
- `GradientSurface`
- `GradientComputationError`

New tests:
```
backend/tests/test_gradient_engine.py
```

Extend integration test:
- Real sweep → metrics → surface → gradient (INT-001 completion)

Update:
- `__init__.py` exports (minimal)
- Governance docs for M07

### ❌ Out of Scope

- Visualization
- Plotting
- UI
- Monte Carlo variance (M08)
- Counterfactual probe (M08)
- Performance optimization
- Parallelization
- GPU scheduling
- Changes to R2L

---

## 3️⃣ Architecture Design

### 3.1 Contract Preservation

M07 consumes:
```
RobustnessSurface (from M06)
```

It must NOT:
- Recompute metrics
- Modify surface values
- Reorder axes
- Mutate surface data

It operates as a **pure consumer** of surface objects.

### 3.2 Data Model

#### GradientPoint

Represents slope at a specific axis/value index.

```python
@dataclass(frozen=True)
class GradientPoint:
    axis: str
    value: str
    d_esi: float
    d_drift: float
```

#### AxisGradient

```python
@dataclass(frozen=True)
class AxisGradient:
    axis: str
    gradients: tuple[GradientPoint, ...]
    mean_abs_esi_gradient: float
    max_abs_esi_gradient: float
    mean_abs_drift_gradient: float
    max_abs_drift_gradient: float
```

#### GradientSurface

```python
@dataclass(frozen=True)
class GradientSurface:
    axes: tuple[AxisGradient, ...]
    global_mean_abs_esi_gradient: float
    global_max_abs_esi_gradient: float
    global_mean_abs_drift_gradient: float
    global_max_abs_drift_gradient: float
```

All values:
- Rounded at storage (8 decimals)
- Deterministically ordered
- Immutable

---

## 4️⃣ Gradient Computation Specification

### 4.1 Finite Difference Rule

Given sorted values along axis:

For each internal index `i`:
```
(f[i+1] - f[i-1]) / 2
```

For endpoints:
- Forward: `f[1] - f[0]`
- Backward: `f[n] - f[n-1]`

This must:
- Use ordered axis from M06
- Be deterministic
- Reject NaN/inf

### 4.2 Stability Metrics

For each axis compute:
- Mean absolute gradient
- Max absolute gradient

Global:
- Mean of all absolute gradients
- Max of all absolute gradients

Interpretation (not encoded in code):
- High max → failure cliff
- High mean → unstable reasoning region

---

## 5️⃣ Determinism Constraints

Must preserve all M06 invariants:
- No numpy
- No randomness
- No datetime
- No uuid
- No subprocess
- No R2L imports

Add AST guardrail tests mirroring M06 pattern.

---

## 6️⃣ Test Plan (Enterprise-Level)

Minimum expected: **45–60 new tests**

### Categories

#### 1. Basic Gradient Correctness
- Linear slope
- Constant surface → zero gradient
- Monotonic increase
- Monotonic decrease

#### 2. Endpoint Behavior
- Two-point axis
- Single-value axis → zero gradient

#### 3. Statistical Aggregation
- Known dataset mean/max verification
- Multi-axis global mean verification

#### 4. Determinism
- Compute twice → identical
- Different engine instances → identical
- Input ordering irrelevant

#### 5. Error Handling
- Empty surface
- NaN in surface
- Inf in surface
- Non-numeric values

#### 6. Rounding
- 8-decimal enforcement

#### 7. Guardrails (AST)
- No forbidden imports

#### 8. Integration (INT-001 Completion)
End-to-end:
```
Sweep → Metrics → Surface → Gradient
```

Using real M05 sweep directory artifact (or minimal fixture).

Must:
- Load actual sweep
- Run metrics
- Run surface
- Run gradient
- Assert determinism across two full executions

This closes INT-001 from M05/M06.

---

## 7️⃣ CI & Governance Requirements

Must:
- Maintain ≥ 95% coverage overall
- ≥ 100% coverage for new module
- No coverage regression in M06 files
- CI green first run
- No new dependencies
- No pyproject changes
- No workflow changes

CI signal must remain truthful per workflow prompt discipline.

---

## 8️⃣ Guardrails to Add

### New Required Guardrail Tests

1. Gradient determinism test
2. Surface immutability test
3. AST forbidden import scan
4. INT-001 real integration test
5. Rounding consistency test

---

## 9️⃣ Definition of Done

M07 is complete when:

- [ ] GradientEngine implemented
- [ ] 45+ new tests added
- [ ] 100% coverage on gradient module
- [ ] INT-001 closed with real sweep test
- [ ] CI green first run
- [ ] M07_plan.md created
- [ ] M07_toolcalls.md created
- [ ] M07_run1.md created
- [ ] M07_audit.md generated
- [ ] M07_summary.md generated
- [ ] clarity.md updated (milestone table)

---

## 🔟 Risk Assessment

| Risk | Mitigation |
|------|------------|
| Incorrect slope math | Known dataset tests |
| Determinism drift | Dual-run equality tests |
| Float instability | 8-decimal rounding |
| Axis misalignment | Reuse M06 ordering |
| Integration fragility | Real sweep INT-001 |

---

## 1️⃣1️⃣ Branch & Execution Protocol

Cursor Steps:

1. Create branch:
   ```
   git checkout -b m07-gradient-stability
   ```

2. Create:
   - `gradient_engine.py`
   - `test_gradient_engine.py`

3. Implement incrementally:
   - Dataclasses
   - Compute logic
   - Axis aggregation
   - Global aggregation

4. Run full test matrix locally

5. Push

6. Analyze CI with workflowprompt.md

7. Await decision

8. Close with unified audit prompt

---

## 1️⃣2️⃣ Explicit Constraints

- No surface mutation
- No schema drift
- No R2L coupling
- No breaking changes
- No opportunistic refactors
- No workflow edits
- No dependency additions

Additive discipline only.

---

## 1️⃣3️⃣ Expected Outcome

After M07:

CLARITY will support:
- Surface computation (M06)
- Gradient estimation (M07)
- Stability quantification
- Cliff detection capability
- Deterministic integration with real sweep

System maturity increases from:
> Descriptive robustness → Sensitivity-aware robustness instrument

---

## Locked Answers Summary

| Question | Answer |
|----------|--------|
| Q1: Input | `GradientEngine.compute(surface: RobustnessSurface) -> GradientSurface` |
| Q2: Dual metrics | Yes — compute for both ESI and Drift |
| Q3: Single-value axis | Return `GradientPoint` with `d_esi=0.0`, `d_drift=0.0` |
| Q4: Endpoint formula | Simple first difference (no `/2`); interior uses central difference `(f[i+1]-f[i-1])/2` |
| Q5: INT-001 fixture | Use existing or create minimal in `backend/tests/fixtures/sweeps/minimal_sweep_v1/` |
| Q6: to_dict() | Yes — add to all dataclasses with sorted keys |
| Q7: Sweep fixtures | Prefer existing real; create minimal if needed |

---

## INT-001 Fixture Notes

*To be documented during implementation if a new fixture is created.*

---

*End of M07 Plan*
