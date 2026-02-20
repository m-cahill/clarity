# M02 Tool Calls Log

## Milestone: M02 — Perturbation Core

---

| Timestamp | Tool | Purpose | Files/Target | Status |
|-----------|------|---------|--------------|--------|
| 2026-02-19 23:45 | write | Update M02_plan.md with full plan + locked answers | docs/milestones/M02/M02_plan.md | ✅ Complete |
| 2026-02-19 23:46 | run_terminal_cmd | Create branch m02-perturbation-core | git | ✅ Complete |
| 2026-02-19 23:47 | mkdir | Create perturbations directory | backend/app/clarity/perturbations/ | ✅ Complete |
| 2026-02-19 23:48 | write | Create base.py - Perturbation ABC | backend/app/clarity/perturbations/base.py | ✅ Complete |
| 2026-02-19 23:48 | write | Create image_utils.py - hashing + canonicalization | backend/app/clarity/image_utils.py | ✅ Complete |
| 2026-02-19 23:48 | write | Create brightness.py perturbation | backend/app/clarity/perturbations/brightness.py | ✅ Complete |
| 2026-02-19 23:48 | write | Create contrast.py perturbation | backend/app/clarity/perturbations/contrast.py | ✅ Complete |
| 2026-02-19 23:48 | write | Create gaussian_noise.py perturbation | backend/app/clarity/perturbations/gaussian_noise.py | ✅ Complete |
| 2026-02-19 23:48 | write | Create blur.py perturbation | backend/app/clarity/perturbations/blur.py | ✅ Complete |
| 2026-02-19 23:49 | write | Create resize.py perturbation | backend/app/clarity/perturbations/resize.py | ✅ Complete |
| 2026-02-19 23:49 | write | Create perturbations/__init__.py | backend/app/clarity/perturbations/__init__.py | ✅ Complete |
| 2026-02-19 23:49 | write | Create perturbation_registry.py | backend/app/clarity/perturbation_registry.py | ✅ Complete |
| 2026-02-19 23:50 | search_replace | Update clarity module __init__.py exports | backend/app/clarity/__init__.py | ✅ Complete |
| 2026-02-19 23:51 | write | Create test_perturbations.py (comprehensive suite) | backend/tests/test_perturbations.py | ✅ Complete |
| 2026-02-19 23:52 | read_lints | Check for linter errors | perturbations module + tests | ✅ No errors |
| 2026-02-19 23:53 | run_terminal_cmd | Run pytest locally (first run) | backend/tests/ | ✅ 60/61 pass |
| 2026-02-19 23:54 | search_replace | Fix repr test assertion | backend/tests/test_perturbations.py | ✅ Complete |
| 2026-02-19 23:55 | run_terminal_cmd | Run pytest locally (second run) | backend/tests/ | ✅ 61/61 pass |
| 2026-02-19 23:56 | run_terminal_cmd | Run full suite with coverage | backend/tests/ | ✅ 105 pass, 92% |
| 2026-02-19 23:57 | search_replace | Update clarity.md M02 status | docs/clarity.md | ✅ Complete |
| 2026-02-19 23:58 | run_terminal_cmd | Commit and push branch | git | ✅ Complete |
| 2026-02-20 00:10 | gh run view | Analyze CI failure | CI run 22213492888 | ✅ Complete |
| 2026-02-20 00:11 | search_replace | Add numpy/pillow to pyproject.toml | backend/pyproject.toml | ✅ Complete |
| 2026-02-20 00:11 | search_replace | Fix Python 3.10 type alias compatibility | backend/app/clarity/perturbation_registry.py | ✅ Complete |
| 2026-02-20 00:12 | run_terminal_cmd | Commit and push fix | git | ✅ Complete |
| 2026-02-20 00:14 | gh run view | Verify CI success | CI run 22213527363 | ✅ Complete |
| 2026-02-20 00:15 | write | Create M02_run1.md analysis | docs/milestones/M02/M02_run1.md | ✅ Complete |
| 2026-02-20 00:20 | write | Generate M02_audit.md | docs/milestones/M02/M02_audit.md | ✅ Complete |
| 2026-02-20 00:25 | gh pr merge | Merge PR #4 | PR #4 → main | ✅ Complete |
| 2026-02-20 00:26 | git tag | Create v0.0.3-m02 tag | git | ✅ Complete |
| 2026-02-20 00:27 | write | Update clarity.md milestone table | docs/clarity.md | ✅ Complete |
| 2026-02-20 00:28 | write | Generate M02_summary.md | docs/milestones/M02/M02_summary.md | ✅ Complete |
| 2026-02-20 00:29 | mkdir/write | Seed M03 folder | docs/milestones/M03/ | ✅ Complete |

---

## Summary

**Branch**: `m02-perturbation-core`  
**Baseline**: M01 (`v0.0.2-m01`)  
**Status**: Implementation complete, ready for PR

## Files Created

### New Files (12)
- `backend/app/clarity/perturbations/__init__.py`
- `backend/app/clarity/perturbations/base.py`
- `backend/app/clarity/perturbations/brightness.py`
- `backend/app/clarity/perturbations/contrast.py`
- `backend/app/clarity/perturbations/gaussian_noise.py`
- `backend/app/clarity/perturbations/blur.py`
- `backend/app/clarity/perturbations/resize.py`
- `backend/app/clarity/image_utils.py`
- `backend/app/clarity/perturbation_registry.py`
- `backend/tests/test_perturbations.py`
- `docs/milestones/M02/M02_plan.md`
- `docs/milestones/M02/M02_toolcalls.md`

### Modified Files (2)
- `backend/app/clarity/__init__.py` (added new exports)
- `docs/clarity.md` (M02 in-progress status)

## Test Results

| Metric | Value |
|--------|-------|
| Total Tests | 105 |
| Passed | 105 |
| Failed | 0 |
| Coverage (clarity module) | 92% |
| New Perturbation Tests | 61 |

## Acceptance Criteria Status

| Criterion | Status |
|-----------|--------|
| All perturbations deterministic | ✅ Verified via hash tests |
| Noise requires seed and fails without it | ✅ TypeError on missing seed |
| image_sha256 stable across runs | ✅ 10-run stability test |
| No input image mutation | ✅ Guardrail tests pass |
| Registry prevents duplicate registration | ✅ DuplicateRegistrationError |
| ≥90% coverage on perturbation module | ✅ 92% achieved |
| CI green on first run | ⏳ Pending PR |

