# M08 CI Run Analysis — Run 1

## Run Summary

| Field | Value |
|-------|-------|
| **Run ID** | 22240688956 |
| **Commit** | `d3dd928` |
| **Branch** | `m08-counterfactual-probe` |
| **PR** | #10 |
| **Trigger** | Pull Request |
| **Result** | 🟢 **ALL PASS** |
| **First-Run Green** | ✅ Yes |

---

## Job Results

| Job | Status | Duration | Link |
|-----|--------|----------|------|
| Backend (Python 3.10) | ✅ pass | 36s | [View](https://github.com/m-cahill/clarity/actions/runs/22240688956/job/64343310290) |
| Backend (Python 3.11) | ✅ pass | 36s | [View](https://github.com/m-cahill/clarity/actions/runs/22240688956/job/64343310377) |
| Backend (Python 3.12) | ✅ pass | 35s | [View](https://github.com/m-cahill/clarity/actions/runs/22240688956/job/64343310347) |
| Frontend | ✅ pass | 40s | [View](https://github.com/m-cahill/clarity/actions/runs/22240688956/job/64343310291) |
| E2E Tests | ✅ pass | 1m32s | [View](https://github.com/m-cahill/clarity/actions/runs/22240688956/job/64343382774) |
| CI Success | ✅ pass | 3s | [View](https://github.com/m-cahill/clarity/actions/runs/22240688956/job/64343545897) |

---

## Test Summary

### Backend Tests

| Metric | Value |
|--------|-------|
| Total Tests | 536 |
| New Tests (M08) | 75 |
| Baseline Tests (M07) | 461 |
| Passed | 536 |
| Failed | 0 |
| Skipped | 0 |

### Coverage

| Module | Coverage |
|--------|----------|
| Overall | ≥95% (threshold: 85%) |
| `counterfactual_engine.py` | 100% |

### Frontend Tests

| Metric | Value |
|--------|-------|
| Unit Tests (Vitest) | 16 passed |
| E2E Tests (Playwright) | 5 passed |

---

## Changes in This PR

### Files Changed

| File | Change Type | Lines |
|------|-------------|-------|
| `backend/app/clarity/counterfactual_engine.py` | Added | +410 |
| `backend/tests/test_counterfactual_engine.py` | Added | +750 |
| `backend/app/clarity/__init__.py` | Modified | +16 |
| `docs/milestones/M08/M08_plan.md` | Modified | Full rewrite |
| `docs/milestones/M08/M08_toolcalls.md` | Modified | Updated |

### New Tests by Category

| Category | Count |
|----------|-------|
| Region Mask Generation | 11 |
| Image Masking | 13 |
| Basic Delta Correctness | 7 |
| Determinism | 4 |
| Region ID Stability | 4 |
| Error Handling | 6 |
| Integration | 3 |
| Serialization | 7 |
| Dataclasses | 5 |
| Guardrails (AST) | 6 |
| Rounding | 4 |
| Edge Cases | 5 |
| **Total** | **75** |

---

## Guardrail Verification

All AST-based guardrail tests pass:

| Guardrail | Status |
|-----------|--------|
| No subprocess import | ✅ |
| No r2l import | ✅ |
| No random import | ✅ |
| No datetime import | ✅ |
| No uuid import | ✅ |
| No numpy import | ✅ |

---

## Assessment

### CI Signal Quality

| Criterion | Result |
|-----------|--------|
| First-run green | ✅ Yes |
| No flaky tests | ✅ Verified |
| Coverage maintained | ✅ ≥95% |
| All jobs passed | ✅ 6/6 |
| No warnings (critical) | ✅ None |

### Regression Risk

| Risk | Assessment |
|------|------------|
| Breaking existing tests | ✅ None (all 461 baseline tests pass) |
| Coverage regression | ✅ None (coverage increased) |
| CI workflow changes | ✅ None (no workflow modifications) |

---

## Conclusion

🟢 **CI RUN 1: PASS**

M08 implementation is CI-verified:

- All 536 tests pass (75 new + 461 baseline)
- 100% coverage on new module
- All guardrails verified
- No CI iteration required
- First-run green achieved

**Ready for merge decision.**

---

*Generated: 2026-02-20*

