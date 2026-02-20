# M02 CI Run Analysis — Run 1 (Fix Run)

## Summary

| Field | Value |
|-------|-------|
| **Run ID** | 22213527363 |
| **Branch** | `m02-perturbation-core` |
| **Commit** | `7132a15` |
| **Triggered** | 2026-02-20T06:10:41Z |
| **Completed** | 2026-02-20T06:12:30Z |
| **Duration** | ~1 min 49 sec |
| **Result** | ✅ **SUCCESS** |

---

## Run History

| Run | Run ID | Commit | Result | Notes |
|-----|--------|--------|--------|-------|
| 0 (initial) | 22213492888 | `379c1ef` | ❌ Failure | Missing numpy/pillow deps, Python 3.12 type syntax |
| 1 (fix) | 22213527363 | `7132a15` | ✅ Success | Added deps, fixed type alias |

---

## Initial Failure Analysis (Run 0)

### Root Cause

```
ModuleNotFoundError: No module named 'numpy'
```

The perturbation module introduced dependencies on `numpy` and `pillow` that were not in `pyproject.toml`. Additionally, Python 3.12's `type` statement syntax was used:

```python
# Python 3.12+ only
type PerturbationClass = type[Perturbation]
```

This syntax is not valid in Python 3.10 or 3.11.

### Fix Applied

1. Added dependencies to `pyproject.toml`:
   ```toml
   "numpy>=1.26.0",
   "pillow>=10.2.0",
   ```

2. Fixed type alias syntax for Python 3.10+ compatibility:
   ```python
   # Before (Python 3.12 only)
   type PerturbationClass = type[Perturbation]
   
   # After (Python 3.10+)
   from typing import Type
   PerturbationClass = Type[Perturbation]
   ```

---

## Run 1 Results

### Jobs Summary

| Job | Python/Node | Duration | Result |
|-----|-------------|----------|--------|
| Frontend | Node.js | 21s | ✅ Success |
| Backend (3.10) | Python 3.10 | 29s | ✅ Success |
| Backend (3.11) | Python 3.11 | 22s | ✅ Success |
| Backend (3.12) | Python 3.12 | 30s | ✅ Success |
| E2E Tests | — | 69s | ✅ Success |
| CI Success | — | 2s | ✅ Success |

### All Steps Passed

All jobs completed successfully:
- ✅ Backend tests pass on all Python versions (3.10, 3.11, 3.12)
- ✅ Frontend type check, lint, and tests pass
- ✅ E2E Playwright tests pass
- ✅ Coverage thresholds met (≥85%)

---

## Test Results

### Backend Tests

| Version | Tests | Passed | Failed | Coverage |
|---------|-------|--------|--------|----------|
| Python 3.10 | 105 | 105 | 0 | ≥85% |
| Python 3.11 | 105 | 105 | 0 | ≥85% |
| Python 3.12 | 105 | 105 | 0 | ≥85% |

### Frontend Tests

| Tests | Passed | Failed | Coverage |
|-------|--------|--------|----------|
| 16 | 16 | 0 | ≥85% |

### E2E Tests

| Tests | Passed | Failed |
|-------|--------|--------|
| 5 | 5 | 0 |

---

## Perturbation Module Tests (New in M02)

| Category | Tests | Status |
|----------|-------|--------|
| Image Canonicalization | 5 | ✅ Pass |
| Image SHA-256 Hashing | 5 | ✅ Pass |
| Image Type Conversion | 3 | ✅ Pass |
| Brightness Perturbation | 8 | ✅ Pass |
| Contrast Perturbation | 3 | ✅ Pass |
| Gaussian Noise Perturbation | 7 | ✅ Pass |
| Gaussian Blur Perturbation | 4 | ✅ Pass |
| Resize Perturbation | 8 | ✅ Pass |
| No Input Mutation | 5 | ✅ Pass |
| Registry | 6 | ✅ Pass |
| AST Guardrails | 4 | ✅ Pass |
| Repr/Properties | 3 | ✅ Pass |
| **Total New** | **61** | ✅ Pass |

---

## Acceptance Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All perturbations deterministic | ✅ Met | Hash tests pass on all Python versions |
| Noise requires seed and fails without | ✅ Met | `test_seed_required` passes |
| image_sha256 stable across runs | ✅ Met | `test_hash_stability_across_calls` passes |
| No input image mutation | ✅ Met | 5 parametrized mutation tests pass |
| Registry prevents duplicate registration | ✅ Met | `test_duplicate_registration_raises` passes |
| ≥90% coverage on perturbation module | ✅ Met | 92% locally verified |
| CI green | ✅ Met | Run 22213527363 success |
| No new deferred HIGH issues | ✅ Met | No issues introduced |

---

## CI Health Assessment

| Metric | Status |
|--------|--------|
| Flaky tests | ❌ None detected |
| Performance regression | ❌ None (tests run in ~2s) |
| Dependency issues | ✅ Resolved (numpy/pillow added) |
| Python version compatibility | ✅ All versions pass |
| Action pinning | ✅ All actions SHA-pinned |

---

## Commits in This PR

| SHA | Message |
|-----|---------|
| `379c1ef` | feat(M02): implement deterministic image perturbation core |
| `7132a15` | fix(M02): add numpy/pillow deps and fix Python 3.10 compatibility |

---

## Next Steps

1. ⏳ Await merge permission
2. Create `M02_audit.md` using audit prompt
3. Create `M02_summary.md` using summary prompt
4. Update `clarity.md` milestone table
5. Tag `v0.0.3-m02`

---

## Links

- **PR:** https://github.com/m-cahill/clarity/pull/4
- **Run 0 (failed):** https://github.com/m-cahill/clarity/actions/runs/22213492888
- **Run 1 (success):** https://github.com/m-cahill/clarity/actions/runs/22213527363

---

*Generated: 2026-02-20*

