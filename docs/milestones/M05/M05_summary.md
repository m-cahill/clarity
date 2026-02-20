# 📌 Milestone Summary — M05: Metrics Core (ESI + Justification Drift)

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Phase:** Foundation  
**Milestone:** M05 — Metrics Core (ESI + Justification Drift)  
**Timeframe:** 2026-02-20 → 2026-02-20  
**Status:** Closed

---

## 1. Milestone Objective

Implement deterministic metrics computation for ESI (Evidence Stability Index) and Justification Drift.

M04 established sweep execution topology. Without M05, CLARITY would execute sweeps but have no way to quantify evidence stability or reasoning consistency. This milestone transforms CLARITY from a sweep executor into a **robustness measurement instrument**.

M05 establishes:
- ESI computation: proportion of runs where answer matches baseline
- Justification Drift computation: normalized Levenshtein distance from baseline
- Baseline selection: first run in deterministic order (no heuristics)
- 8-decimal rounding: deterministic float storage
- Answer/justification extraction: explicit contract with graceful degradation

> **What would have been incomplete if this milestone did not exist?**  
> CLARITY would have no mechanism to quantify robustness. The sweep orchestrator would produce directories, but no actionable metrics. M06 (Robustness Surfaces) and all downstream analysis depend on this metrics layer.

---

## 2. Scope Definition

### In Scope

**Backend (Metrics Module):**
- `backend/app/clarity/metrics.py` — ESIMetric, DriftMetric, MetricsResult dataclasses
- `MetricComputationError` exception
- `levenshtein_distance()` — Pure Python DP implementation, Unicode-safe
- `normalized_levenshtein()` — Normalized distance [0,1]
- `round_metric()` — 8-decimal rounding
- `extract_answer()` — Answer extraction with explicit fallback contract
- `extract_justification()` — Justification extraction with empty string fallback

**Backend (Metrics Engine Module):**
- `backend/app/clarity/metrics_engine.py` — MetricsEngine class
- `compute(sweep_dir: Path) -> MetricsResult` method
- Sweep manifest loading
- Run data extraction from trace packs
- Baseline selection (run[0])
- ESI and Drift computation per axis
- Deterministic ordering (alphabetical axes, lexicographic values)

**Tests:**
- `backend/tests/test_metrics_engine.py` — 69 comprehensive tests
- Levenshtein correctness (14 tests including Unicode)
- Answer/justification extraction (13 tests)
- ESI calculation (5 tests)
- Drift calculation (7 tests)
- Determinism verification (3 tests)
- M05 guardrails (12 tests)

**Governance:**
- `docs/milestones/M05/M05_plan.md` — Detailed plan with locked answers
- `docs/milestones/M05/M05_toolcalls.md` — Tool call log
- `docs/milestones/M05/M05_run1.md` — CI run analysis

### Out of Scope

- Metrics persistence (M06+)
- Robustness surface estimation (M06)
- Monte Carlo reasoning stability (M07)
- Gradient estimation
- Plot generation
- UI integration
- Parallelization
- GPU logic
- Real R2L integration (uses artifact_loader boundary)

**Scope did not change during execution.**

---

## 3. Work Executed

### High-Level Actions

| Action | Files | Lines |
|--------|-------|-------|
| Metrics module creation | 1 | +286 |
| Metrics engine module creation | 1 | +335 |
| Test suite | 1 | +1156 |
| __init__.py exports update | 1 | +25/-7 |
| Governance docs | 3 | +533 |
| **Total** | 8 | +2335/-7 |

### Commits

| SHA | Message | Type |
|-----|---------|------|
| `6de78c5` | feat(M05): implement metrics core with ESI and justification drift | Feature |
| `8c736c5` | docs(M05): add CI run analysis M05_run1.md - all green first run | Docs |
| `b0f9413` | Squash merge of PR #7 | Merge |

### Mechanical vs Semantic Changes

- **Mechanical:** __init__.py export additions
- **Semantic:** All metrics dataclasses, Levenshtein implementation, extraction functions, MetricsEngine computation logic, baseline selection, rounding, ordering

---

## 4. Validation & Evidence

### Tests Run

| Tier | Framework | Count | Status |
|------|-----------|-------|--------|
| Backend Unit | Pytest | 348 | ✅ Pass |
| Frontend Unit | Vitest | 16 | ✅ Pass |
| E2E | Playwright | 5 | ✅ Pass |

### Coverage

| Component | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Backend (overall) | ≥85% | 94.61% | ✅ Pass |
| metrics.py | ≥95% | 100% | ✅ Pass |
| metrics_engine.py | ≥90% | 91% | ✅ Pass |

### Test Categories (New in M05)

| Category | Tests | Enforcement |
|----------|-------|-------------|
| Levenshtein distance | 14 | Known pairs, edge cases, Unicode (emoji, CJK) |
| Normalized Levenshtein | 4 | Empty strings, normalization |
| Round metric | 3 | 8-decimal precision |
| Extract answer | 7 | `output` → `answer` → error |
| Extract justification | 6 | Missing → empty, coercion |
| Baseline selection | 2 | First run, determinism |
| ESI calculation | 5 | Matching, partial, multi-axis |
| Drift calculation | 7 | Identical, different, Unicode |
| Determinism | 3 | Run twice, compare results |
| Error handling | 4 | Empty sweep, missing files |
| M05 guardrails | 12 | AST checks for forbidden imports |
| Integration | 2 | Full sweep, immutability |

### Failures Encountered and Resolved

**One minor test fix:** Guardrail test for `datetime.now` was triggering on docstring comment. Fixed by converting to AST-based detection.

**Evidence that validation is meaningful:**
- Determinism tests run compute() twice and compare MetricsResult objects
- Unicode tests include emoji (😀) and CJK (日本語) characters
- Rounding tests verify exact 8-decimal output
- AST guardrail tests scan actual source code

---

## 5. CI / Automation Impact

### Workflows Affected

| Workflow | Status | Change |
|----------|--------|--------|
| `.github/workflows/ci.yml` | Unchanged | No modifications |

### Checks Added

None (existing checks maintained).

### Changes in Enforcement Behavior

| Aspect | Before (M04) | After (M05) |
|--------|--------------|-------------|
| Test count | 279 | 348 (+69) |
| Coverage | 95% | 94.61% (-0.39%) |
| Guardrail tests | 28 | 40 (+12) |

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

**Minor:** Guardrail test detected "datetime.now" in docstring comment. Fixed by converting to AST-based detection that only checks actual code.

### New Issues Introduced

None. No HIGH issues introduced.

---

## 7. Deferred Work

| Item | Reason | Pre-existed? | Status Changed? |
|------|--------|--------------|-----------------|
| GOV-001: Branch protection | Requires admin | Yes (M00) | No |
| SEC-001: CORS permissive | Dev-only | Yes (M00) | No |
| SCAN-001: No security scanning | Not required for metrics | Yes (M01) | No |
| DEP-001: No dependency lockfile | Version floors sufficient | Yes (M02) | No |
| INT-001: Real sweep integration | Requires M04 output | New (M05) | Deferred to M06 |

**No untracked debt was introduced.**

---

## 8. Governance Outcomes

### What Changed in Governance Posture

| Before M05 | After M05 |
|------------|-----------|
| No metrics computation capability | Deterministic ESI + Drift computation |
| No quantifiable robustness measure | Evidence stability quantified per axis |
| No baseline selection contract | Baseline = run[0] (deterministic, no heuristics) |
| No answer extraction contract | `output` → `answer` → error (explicit) |
| No justification handling | Missing → empty string (graceful degradation) |
| No rounding contract | 8-decimal rounding at storage |

### What Is Now Provably True

1. **ESI is deterministic** — Same sweep produces identical ESI values
2. **Drift is deterministic** — Same sweep produces identical drift values
3. **Baseline is invariant** — run[0] in manifest order, no heuristics
4. **Answer extraction is explicit** — Contract: `output` → `answer` → error
5. **Justification missing is graceful** — Returns empty string, not error
6. **Floats are rounded at storage** — 8-decimal precision, deterministic
7. **Unicode is supported** — Levenshtein handles emoji, CJK, accented characters
8. **No forbidden imports** — AST guardrails verify at CI time

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| ESI computed correctly on synthetic sweep | ✅ Met | `test_all_matching_answers`, `test_partial_matching` pass |
| Drift computed correctly | ✅ Met | `test_partial_drift`, `test_unicode_justifications` pass |
| Baseline selection deterministic | ✅ Met | `test_baseline_is_first_run`, `test_baseline_deterministic` pass |
| All numeric outputs deterministic | ✅ Met | `test_compute_twice_identical_results` passes |
| CI green first run | ✅ Met | Run 22216071598 all green |
| Coverage targets met | ✅ Met | 100%/91% on new modules, 94.61% overall |
| No HIGH issues introduced | ✅ Met | No HIGH issues in audit |
| No boundary violations | ✅ Met | All guardrail tests pass |

**8/8 criteria met.**

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed to M06.**

M05 successfully established the first analytic milestone with:

- ✅ Deterministic ESI computation (Evidence Stability Index)
- ✅ Deterministic Drift computation (Justification Drift)
- ✅ Baseline selection invariance (run[0], no heuristics)
- ✅ Answer extraction contract (`output` → `answer` → error)
- ✅ Justification handling (missing → empty string)
- ✅ 8-decimal rounding at storage
- ✅ Unicode-safe Levenshtein implementation
- ✅ 69 new tests, 100%/91% coverage
- ✅ CI green on first run

---

## 11. Authorized Next Step

Upon closeout:

1. ✅ PR #7 merged (`b0f9413`)
2. ✅ M05_audit.md generated
3. ✅ M05_summary.md generated
4. ⏳ Tag release (`v0.0.6-m05`)
5. ⏳ Update `docs/clarity.md`
6. Proceed to **M06: Robustness Surfaces**

**Constraints for M06:**
- Consume metrics output from M05 MetricsEngine
- Maintain R2LRunner boundary
- No direct R2L imports
- Surface estimation must be deterministic

---

## 12. Canonical References

### Commits

| SHA | Description |
|-----|-------------|
| `6de78c5` | feat(M05): implement metrics core with ESI and justification drift |
| `8c736c5` | docs(M05): add CI run analysis |
| `b0f9413` | Squash merge of PR #7 |

### Pull Requests

| PR | Title | Status |
|----|-------|--------|
| #7 | feat(M05): Metrics Core - ESI and Justification Drift | ✅ Merged |

### Tags

| Tag | Description |
|-----|-------------|
| `v0.0.6-m05` | M05: Metrics Core (pending) |

### CI Runs

| Run ID | Commit | Status |
|--------|--------|--------|
| 22216071598 | `6de78c5` | ✅ Success |

### Documents

| Document | Path |
|----------|------|
| M05 Plan | `docs/milestones/M05/M05_plan.md` |
| M05 Tool Calls | `docs/milestones/M05/M05_toolcalls.md` |
| M05 CI Analysis | `docs/milestones/M05/M05_run1.md` |
| M05 Audit | `docs/milestones/M05/M05_audit.md` |
| M05 Summary | `docs/milestones/M05/M05_summary.md` |
| clarity.md | `docs/clarity.md` |

### Repository

- **GitHub:** https://github.com/m-cahill/clarity
- **Tag:** `v0.0.6-m05` (pending)
- **PR:** https://github.com/m-cahill/clarity/pull/7

---

*End of M05 Summary*

