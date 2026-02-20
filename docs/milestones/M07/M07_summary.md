# 📌 Milestone Summary — M07: Gradient / Stability Estimation

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Phase:** Foundation  
**Milestone:** M07 — Gradient / Stability Estimation  
**Timeframe:** 2026-02-20 → 2026-02-20  
**Status:** Closed

---

## 1. Milestone Objective

Implement deterministic gradient estimation and stability metrics over robustness surfaces.

M06 established robustness surface construction. Without M07, CLARITY would have surfaces but no quantified sensitivity measurements. This milestone transforms CLARITY from a **descriptive instrument** into a **sensitivity-aware robustness instrument**.

M07 establishes:
- GradientPoint: Local slope at a specific axis/value position
- AxisGradient: Per-axis gradient summary with mean/max statistics
- GradientSurface: Complete gradient surface with global statistics
- GradientEngine: Deterministic gradient computation from RobustnessSurface

> **What would have been incomplete if this milestone did not exist?**  
> CLARITY could describe surfaces but could not quantify slope instability or detect "failure cliffs." M08 (Counterfactual Probe) and downstream visualization depend on gradient capabilities.

---

## 2. Scope Definition

### In Scope

**Backend (Gradient Engine Module):**
- `backend/app/clarity/gradient_engine.py` — GradientPoint, AxisGradient, GradientSurface, GradientComputationError, GradientEngine
- `_round8()` — 8-decimal rounding helper
- `to_dict()` methods on all dataclasses with sorted keys
- Finite difference gradient computation (central + endpoint)
- Stability metrics (mean/max absolute gradients)

**Tests:**
- `backend/tests/test_gradient_engine.py` — 52 comprehensive tests
- Basic Gradient Correctness (6 tests)
- Endpoint Behavior (4 tests)
- Statistical Aggregation (6 tests)
- Determinism (3 tests)
- Error Handling (5 tests)
- Rounding (4 tests)
- Guardrails AST-based (6 tests)
- to_dict() Serialization (7 tests)
- Dataclasses (5 tests)
- Integration (4 tests)
- INT-001 Real Sweep (2 tests)

**Governance:**
- `docs/milestones/M07/M07_plan.md` — Detailed plan with locked answers
- `docs/milestones/M07/M07_toolcalls.md` — Tool call log
- `docs/milestones/M07/M07_run1.md` — CI run analysis

### Out of Scope

- Gradient visualization / plotting (M09+)
- Parametric step-size support (M08+)
- Monte Carlo stability (M08)
- Counterfactual probe (M08)
- Performance optimization

**Scope did not change during execution.**

---

## 3. Work Executed

### High-Level Actions

| Action | Files | Lines |
|--------|-------|-------|
| Gradient engine module creation | 1 | +421 |
| __init__.py exports update | 1 | +16 |
| Test suite | 1 | +1198 |
| Governance docs | 3 | +498 |
| **Total** | 6 | +2133 |

### Commits

| SHA | Message | Type |
|-----|---------|------|
| `96b29c9` | feat(M07): implement gradient engine with stability metrics | Feature |
| `65d9899` | docs(M07): add CI run analysis M07_run1.md - all green first run | Docs |
| `d67218c` | docs(M07): update toolcalls log | Docs |
| `976412a` | Squash merge of PR #9 | Merge |

### Mechanical vs Semantic Changes

- **Mechanical:** __init__.py export additions
- **Semantic:** All gradient dataclasses, finite difference computation, stability metrics (mean/max), NaN/inf rejection, rounding, to_dict() serialization, INT-001 integration tests

---

## 4. Validation & Evidence

### Tests Run

| Tier | Framework | Count | Status |
|------|-----------|-------|--------|
| Backend Unit | Pytest | 461 | ✅ Pass |
| Frontend Unit | Vitest | 16 | ✅ Pass |
| E2E | Playwright | 5 | ✅ Pass |

### Coverage

| Component | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Backend (overall) | ≥85% | 95.74% | ✅ Pass |
| gradient_engine.py | ≥95% | 100% | ✅ Pass |

### Test Categories (New in M07)

| Category | Tests | Enforcement |
|----------|-------|-------------|
| Basic Gradient Correctness | 6 | Linear/constant/monotonic slope verification |
| Endpoint Behavior | 4 | Two-point, single-value, forward/backward difference |
| Statistical Aggregation | 6 | Known dataset mean/max verification |
| Determinism | 3 | Compute twice, different engines |
| Error Handling | 5 | Empty surface, NaN/inf rejection |
| Rounding | 4 | 8-decimal precision verified |
| Guardrails (AST) | 6 | No numpy/subprocess/random/datetime/uuid/r2l |
| to_dict() Serialization | 7 | Sorted keys, deterministic output |
| Dataclasses | 5 | Equality, hashability, frozen behavior |
| Integration | 4 | Full pipeline, immutability, large surfaces |
| INT-001 Real Sweep | 2 | Real sweep → metrics → surface → gradient |

### Failures Encountered and Resolved

None. CI green on first run.

**Evidence that validation is meaningful:**
- Gradient tests use known linear/constant/nonlinear surfaces with hand-calculated expected values
- Determinism tests run compute() twice and compare results
- Guardrail tests use AST parsing to verify no forbidden imports
- INT-001 tests exercise actual artifact loader path

---

## 5. CI / Automation Impact

### Workflows Affected

| Workflow | Status | Change |
|----------|--------|--------|
| `.github/workflows/ci.yml` | Unchanged | No modifications |

### Checks Added

None (existing checks maintained).

### Changes in Enforcement Behavior

| Aspect | Before (M06) | After (M07) |
|--------|--------------|-------------|
| Test count | 409 | 461 (+52) |
| Coverage | 95.16% | 95.74% (+0.58%) |
| Guardrail tests | 52 | 58 (+6) |

### CI Assessment

| Criterion | Result |
|-----------|--------|
| Blocked incorrect changes | ✅ N/A (first run green) |
| Validated correct changes | ✅ Yes (all checks passed) |
| Failed to observe relevant risk | ❌ No (all gates functional) |

### Signal Drift

None detected. CI remains truthful.

---

## 6. Issues & Exceptions

### Issues Encountered

None. No failures during implementation.

### New Issues Introduced

None. No HIGH issues introduced.

---

## 7. Deferred Work

| Item | Reason | Pre-existed? | Status Changed? |
|------|--------|--------------|-----------------|
| GOV-001: Branch protection | Requires admin | Yes (M00) | No |
| SEC-001: CORS permissive | Dev-only | Yes (M00) | No |
| SCAN-001: No security scanning | Not required for gradients | Yes (M01) | No |
| DEP-001: No dependency lockfile | Version floors sufficient | Yes (M02) | No |
| INT-001: Real pipeline integration | **RESOLVED** | Extended (M05) | **Closed** |

**INT-001 resolved with 2 comprehensive integration tests.**

**No untracked debt was introduced.**

---

## 8. Governance Outcomes

### What Changed in Governance Posture

| Before M07 | After M07 |
|------------|-----------|
| No gradient estimation | Deterministic gradient computation |
| No stability metrics | Per-axis and global mean/max absolute gradients |
| No sensitivity quantification | Slope-based sensitivity at each point |
| INT-001 deferred | INT-001 closed |

### What Is Now Provably True

1. **Gradient computation is deterministic** — Same RobustnessSurface produces identical GradientSurface
2. **Finite difference is correctly implemented** — Central difference for interior, forward/backward for endpoints
3. **Single-value axes produce zero gradient** — No undefined behavior
4. **Invalid floats are rejected** — NaN/inf values raise GradientComputationError
5. **Floats are rounded at storage** — 8-decimal precision, deterministic
6. **Ordering is deterministic** — Reuses M06 axis/value ordering
7. **Serialization is deterministic** — to_dict() produces sorted keys
8. **No forbidden imports** — AST guardrails verify at CI time
9. **Full pipeline integration verified** — Real sweep → gradient tested

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| GradientEngine implemented | ✅ Met | `gradient_engine.py` complete |
| 45+ new tests added | ✅ Met | 52 tests added |
| 100% coverage on gradient module | ✅ Met | 100% coverage verified |
| INT-001 closed with real sweep test | ✅ Met | 2 INT-001 tests pass |
| CI green first run | ✅ Met | Run 22237991249 all green |
| No boundary violations | ✅ Met | All 6 guardrail tests pass |
| No HIGH issues introduced | ✅ Met | No HIGH issues in audit |

**7/7 criteria met.**

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed to M08.**

M07 successfully established deterministic gradient estimation with:

- ✅ RobustnessSurface → GradientSurface transformation
- ✅ Finite difference gradient computation (central + endpoint)
- ✅ Per-axis mean/max absolute gradients
- ✅ Global mean/max absolute gradients
- ✅ Single-value axis handling (zero gradient)
- ✅ NaN/inf rejection
- ✅ 8-decimal rounding at storage
- ✅ Deterministic ordering and serialization
- ✅ 52 new tests across 11 categories
- ✅ 100% coverage on new module
- ✅ INT-001 closed
- ✅ CI green on first run

---

## 11. Authorized Next Step

Upon closeout:

1. ✅ PR #9 merged (`976412a`)
2. ✅ M07_audit.md generated
3. ✅ M07_summary.md generated
4. ⏳ Tag release (`v0.0.8-m07`)
5. ⏳ Update `docs/clarity.md`
6. Proceed to **M08: Counterfactual Probe**

**Constraints for M08:**
- Consume gradient output from M07 GradientEngine
- Maintain determinism constraints
- No direct R2L imports
- Region masking must be deterministic

---

## 12. Canonical References

### Commits

| SHA | Description |
|-----|-------------|
| `96b29c9` | feat(M07): implement gradient engine with stability metrics |
| `65d9899` | docs(M07): add CI run analysis |
| `d67218c` | docs(M07): update toolcalls log |
| `976412a` | Squash merge of PR #9 |

### Pull Requests

| PR | Title | Status |
|----|-------|--------|
| #9 | feat(M07): Gradient / Stability Estimation | ✅ Merged |

### Tags

| Tag | Description |
|-----|-------------|
| `v0.0.8-m07` | M07: Gradient / Stability Estimation (pending) |

### CI Runs

| Run ID | Commit | Status |
|--------|--------|--------|
| 22237991249 | `96b29c9` | ✅ Success (PR) |
| 22238354724 | `976412a` | ✅ Success (post-merge) |

### Documents

| Document | Path |
|----------|------|
| M07 Plan | `docs/milestones/M07/M07_plan.md` |
| M07 Tool Calls | `docs/milestones/M07/M07_toolcalls.md` |
| M07 CI Analysis | `docs/milestones/M07/M07_run1.md` |
| M07 Audit | `docs/milestones/M07/M07_audit.md` |
| M07 Summary | `docs/milestones/M07/M07_summary.md` |
| clarity.md | `docs/clarity.md` |

### Repository

- **GitHub:** https://github.com/m-cahill/clarity
- **Tag:** `v0.0.8-m07` (pending)
- **PR:** https://github.com/m-cahill/clarity/pull/9

---

*End of M07 Summary*

