# 📌 Milestone Summary — M08: Counterfactual Probe Engine

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Phase:** Foundation  
**Milestone:** M08 — Counterfactual Probe Engine  
**Timeframe:** 2026-02-20 → 2026-02-20  
**Status:** Closed

---

## 1. Milestone Objective

Implement causal region dependence testing through deterministic image masking.

M07 established gradient-based sensitivity estimation. Without M08, CLARITY could measure slopes but could not test whether the model truly depends on specific image regions. This milestone transforms CLARITY from a **sensitivity-aware instrument** into a **causality-aware robustness instrument**.

M08 establishes:
- RegionMask: Grid-based region definitions in normalized coordinates
- CounterfactualProbe: Specification of region + axis + value to probe
- ProbeResult: Delta metrics storage (baseline vs masked)
- ProbeSurface: Aggregated results with summary statistics
- CounterfactualEngine: Orchestration of masking and delta computation

> **What would have been incomplete if this milestone did not exist?**  
> CLARITY could not answer: "Does the model truly depend on this region?" M09 (UI) and M10 (Visualization) depend on counterfactual probing capabilities.

---

## 2. Scope Definition

### In Scope

**Backend (Counterfactual Engine Module):**
- `backend/app/clarity/counterfactual_engine.py` — complete module
- `RegionMask` — grid cell region definitions
- `CounterfactualProbe` — probe specification dataclass
- `ProbeResult` — delta metrics storage dataclass
- `ProbeSurface` — aggregated results dataclass
- `CounterfactualComputationError` — error class
- `generate_grid_masks(k)` — k×k uniform grid generation
- `apply_mask(image, mask, fill_value)` — deterministic image occlusion
- `compute_probe_result()` — delta computation
- `compute_probe_surface()` — aggregation with statistics
- `CounterfactualEngine` class with `probe_single()`, `build_probe_surface()`, `generate_masks()`
- `_round8()` — 8-decimal rounding helper
- `to_dict()` methods on all dataclasses with sorted keys

**Tests:**
- `backend/tests/test_counterfactual_engine.py` — 75 comprehensive tests
- Region Mask Generation (11 tests)
- Image Masking (13 tests)
- Basic Delta Correctness (7 tests)
- Determinism (4 tests)
- Region ID Stability (4 tests)
- Error Handling (6 tests)
- Integration (3 tests)
- Serialization (7 tests)
- Dataclasses (5 tests)
- Guardrails AST-based (6 tests)
- Rounding (4 tests)
- Edge Cases (5 tests)

**Governance:**
- `docs/milestones/M08/M08_plan.md` — Detailed plan with locked answers
- `docs/milestones/M08/M08_toolcalls.md` — Tool call log
- `docs/milestones/M08/M08_run1.md` — CI run analysis

### Out of Scope

- Visualization / heatmaps (M10)
- Evidence-map-derived regions (M10+)
- Monte Carlo sampling (M09+)
- BBox mask format (grid-only in M08)
- Actual counterfactual sweep orchestration (M09+)
- Performance optimization (M12)
- GPU parallelization
- UI integration

**Scope did not change during execution.**

---

## 3. Work Executed

### High-Level Actions

| Action | Files | Lines |
|--------|-------|-------|
| Counterfactual engine module creation | 1 | +410 |
| __init__.py exports update | 1 | +16 |
| Test suite | 1 | +750 |
| Governance docs | 4 | +600 |
| **Total** | 7 | +1776 |

### Commits

| SHA | Message | Type |
|-----|---------|------|
| `d3dd928` | feat(M08): implement counterfactual probe engine with grid masking | Feature |

### Mechanical vs Semantic Changes

- **Mechanical:** __init__.py export additions
- **Semantic:** All dataclasses (RegionMask, CounterfactualProbe, ProbeResult, ProbeSurface), grid mask generation, image masking with PIL, delta computation, aggregation statistics, NaN/inf rejection, rounding, to_dict() serialization, guardrail verification

---

## 4. Validation & Evidence

### Tests Run

| Tier | Framework | Count | Status |
|------|-----------|-------|--------|
| Backend Unit | Pytest | 536 | ✅ Pass |
| Frontend Unit | Vitest | 16 | ✅ Pass |
| E2E | Playwright | 5 | ✅ Pass |

### Coverage

| Component | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Backend (overall) | ≥85% | 96%+ | ✅ Pass |
| counterfactual_engine.py | ≥95% | 100% | ✅ Pass |

### Test Categories (New in M08)

| Category | Tests | Enforcement |
|----------|-------|-------------|
| Region Mask Generation | 11 | Grid count, determinism, coverage, boundaries |
| Image Masking | 13 | Dimensions, mode, fill value, determinism |
| Basic Delta Correctness | 7 | Positive/negative/zero deltas, value preservation |
| Determinism | 4 | Double-run equality, engine instances |
| Region ID Stability | 4 | ID format, geometry consistency |
| Error Handling | 6 | Invalid inputs, empty results |
| Integration | 3 | Full pipeline, immutability |
| Serialization | 7 | Sorted keys, JSON compatibility |
| Dataclasses | 5 | Equality, hashability, frozen behavior |
| Guardrails (AST) | 6 | No subprocess/random/datetime/uuid/r2l/numpy |
| Rounding | 4 | 8-decimal precision verified |
| Edge Cases | 5 | Small images, asymmetric, zero metrics |

### Failures Encountered and Resolved

None. CI green on first run.

**Evidence that validation is meaningful:**
- Guardrail tests use AST parsing to verify no forbidden imports
- Determinism tests run compute() twice and compare results
- Masking tests verify actual pixel values after occlusion
- Delta tests use known values with hand-calculated expected deltas

---

## 5. CI / Automation Impact

### Workflows Affected

| Workflow | Status | Change |
|----------|--------|--------|
| `.github/workflows/ci.yml` | Unchanged | No modifications |

### Checks Added

None (existing checks maintained).

### Changes in Enforcement Behavior

| Aspect | Before (M07) | After (M08) |
|--------|--------------|-------------|
| Test count | 461 | 536 (+75) |
| Coverage | 95.74% | 96%+ |
| Guardrail tests | 58 | 64 (+6) |

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
| SCAN-001: No security scanning | Not required for counterfactuals | Yes (M01) | No |
| DEP-001: No dependency lockfile | Version floors sufficient | Yes (M02) | No |
| CF-001: Evidence-map-derived regions | Requires M10 saliency | **New (M08)** | Deferred to M10 |
| CF-002: Actual counterfactual sweeps | Requires orchestrator extension | **New (M08)** | Deferred to M09 |

**CF-001 and CF-002 are intentional scope boundaries, not technical debt.**

**No untracked debt was introduced.**

---

## 8. Governance Outcomes

### What Changed in Governance Posture

| Before M08 | After M08 |
|------------|-----------|
| No region masking capability | Deterministic grid-based masking |
| No causal probe infrastructure | CounterfactualProbe + ProbeResult |
| No delta metric computation | Baseline vs masked delta storage |
| No probe aggregation | ProbeSurface with mean/max statistics |

### What Is Now Provably True

1. **Grid masks are deterministic** — Same k produces identical RegionMask definitions
2. **Image masking is deterministic** — Same image + mask → same result
3. **Region IDs encode position** — `grid_r{row}_c{col}_k{size}` format locked
4. **Fill value is fixed** — 128 (neutral gray), not configurable without code change
5. **Deltas are correctly computed** — masked - baseline, rounded to 8 decimals
6. **Floats are rounded at storage** — 8-decimal precision, deterministic
7. **Ordering is deterministic** — Results sorted by (region_id, axis, value)
8. **Serialization is deterministic** — to_dict() produces sorted keys
9. **No forbidden imports** — AST guardrails verify at CI time

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `counterfactual_engine.py` implemented | ✅ Met | Module complete with all dataclasses and functions |
| ≥50 new tests added | ✅ Met | 75 tests added (exceeds target) |
| ≥95% coverage on new module | ✅ Met | 100% coverage verified |
| Integration test covers full pipeline | ✅ Met | `test_full_probe_pipeline` passes |
| CI green first run | ✅ Met | Run 22240688956 all green |
| No boundary violations | ✅ Met | All 6 guardrail tests pass |
| No HIGH issues introduced | ✅ Met | No HIGH issues in audit |

**7/7 criteria met.**

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed to M09.**

M08 successfully established counterfactual probing infrastructure with:

- ✅ Grid-based region masking (`generate_grid_masks`)
- ✅ Deterministic image occlusion (`apply_mask`)
- ✅ Probe specification (`CounterfactualProbe`)
- ✅ Delta computation (`compute_probe_result`)
- ✅ Aggregation (`compute_probe_surface`, `ProbeSurface`)
- ✅ 75 new tests across 12 categories
- ✅ 100% coverage on new module
- ✅ CI green on first run
- ✅ All guardrails verified

---

## 11. Authorized Next Step

Upon closeout:

1. ⏳ Merge PR #10 to main (requires permission)
2. ⏳ Tag release (`v0.0.9-m08`)
3. ⏳ Update `docs/clarity.md`
4. Proceed to **M09: UI Console Skeleton**

**Constraints for M09:**
- Build on M08 counterfactual infrastructure
- Interactive configuration for probe parameters
- Results display from ProbeSurface
- Maintain determinism constraints

---

## 12. Canonical References

### Commits

| SHA | Description |
|-----|-------------|
| `d3dd928` | feat(M08): implement counterfactual probe engine with grid masking |

### Pull Requests

| PR | Title | Status |
|----|-------|--------|
| #10 | feat(M08): Counterfactual Probe Engine | ⏳ Awaiting merge |

### Tags

| Tag | Description |
|-----|-------------|
| `v0.0.9-m08` | M08: Counterfactual Probe Engine (pending) |

### CI Runs

| Run ID | Commit | Status |
|--------|--------|--------|
| 22240688956 | `d3dd928` | ✅ Success (PR) |

### Documents

| Document | Path |
|----------|------|
| M08 Plan | `docs/milestones/M08/M08_plan.md` |
| M08 Tool Calls | `docs/milestones/M08/M08_toolcalls.md` |
| M08 CI Analysis | `docs/milestones/M08/M08_run1.md` |
| M08 Audit | `docs/milestones/M08/M08_audit.md` |
| M08 Summary | `docs/milestones/M08/M08_summary.md` |
| clarity.md | `docs/clarity.md` |

### Repository

- **GitHub:** https://github.com/m-cahill/clarity
- **Tag:** `v0.0.9-m08` (pending)
- **PR:** https://github.com/m-cahill/clarity/pull/10

---

*End of M08 Summary*

