# 📌 Milestone Summary — M02: Perturbation Core

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Phase:** Foundation  
**Milestone:** M02 — Perturbation Core  
**Timeframe:** 2026-02-19 → 2026-02-20  
**Status:** Closed

---

## 1. Milestone Objective

Implement deterministic image perturbation primitives — the first domain capability of CLARITY.

M01 froze the CLARITY↔R2L boundary and established determinism contracts. Without M02, the sweep orchestrator (M04) cannot execute, metrics (M05) have no perturbation data, and robustness surfaces (M06) cannot be estimated.

M02 establishes:
- Reproducible perturbation recipes
- Deterministic parameterization
- Stable hashable outputs
- Zero randomness leakage

> **What would have been incomplete if this milestone did not exist?**  
> CLARITY would have no image manipulation capability. The entire perturbation sweep pipeline (M04-M06) depends on the primitives established here.

---

## 2. Scope Definition

### In Scope

**Backend (Perturbation Module):**
- `backend/app/clarity/perturbations/base.py` — Abstract Perturbation class
- `backend/app/clarity/perturbations/brightness.py` — Brightness adjustment
- `backend/app/clarity/perturbations/contrast.py` — Contrast adjustment
- `backend/app/clarity/perturbations/gaussian_noise.py` — Seeded noise addition
- `backend/app/clarity/perturbations/blur.py` — Gaussian blur
- `backend/app/clarity/perturbations/resize.py` — Explicit interpolation resize
- `backend/app/clarity/perturbations/__init__.py` — Module exports

**Backend (Supporting Modules):**
- `backend/app/clarity/image_utils.py` — Canonical hashing and conversion
- `backend/app/clarity/perturbation_registry.py` — Type registry with duplicate prevention

**Tests:**
- `backend/tests/test_perturbations.py` — 61 comprehensive tests

**Dependencies:**
- `numpy>=1.26.0` — Numerical operations
- `pillow>=10.2.0` — Image processing

**Governance:**
- `docs/milestones/M02/M02_plan.md` — Detailed plan with locked answers
- `docs/milestones/M02/M02_toolcalls.md` — Tool call log
- `docs/milestones/M02/M02_run1.md` — CI run analysis
- `docs/milestones/M02/M02_audit.md` — Milestone audit

### Out of Scope

- Sweep execution logic (M04)
- R2L integration (M03)
- Metrics computation (M05)
- Parallelization
- GPU usage
- Persistence
- UI wiring
- Caching
- Async execution

**Scope did not change during execution.**

---

## 3. Work Executed

### High-Level Actions

| Action | Files | Lines |
|--------|-------|-------|
| Perturbation module creation | 7 | +696 |
| Image utilities | 1 | +141 |
| Perturbation registry | 1 | +148 |
| Clarity module __init__ update | 1 | +35/-13 |
| Test suite | 1 | +707 |
| Dependencies | 1 | +2 |
| Governance docs | 4 | +666 |
| **Total** | 16 | +2,317/-23 |

### Commits

| SHA | Message | Type |
|-----|---------|------|
| `379c1ef` | feat(M02): implement deterministic image perturbation core | Feature |
| `7132a15` | fix(M02): add numpy/pillow deps and fix Python 3.10 compatibility | Fix |
| `2ff9fad` | docs(M02): add CI run analysis M02_run1.md | Docs |
| `8d279d8` | docs(M02): add milestone audit M02_audit.md | Docs |

### Mechanical vs Semantic Changes

- **Mechanical:** pyproject.toml dependency addition, module __init__.py exports
- **Semantic:** All perturbation logic, image utilities, registry design, test suite

---

## 4. Validation & Evidence

### Tests Run

| Tier | Framework | Count | Status |
|------|-----------|-------|--------|
| Backend Unit | Pytest | 105 | ✅ Pass |
| Frontend Unit | Vitest | 16 | ✅ Pass |
| E2E | Playwright | 5 | ✅ Pass |

### Coverage

| Component | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Backend | ≥85% | 92% | ✅ Pass |
| Perturbation Module | ≥90% | ~92% | ✅ Pass |

### Test Categories (New in M02)

| Category | Tests | Enforcement |
|----------|-------|-------------|
| Determinism | 10 | Same inputs → same hash |
| No Input Mutation | 5 | Input unchanged after apply |
| Hash Stability | 5 | Stable across calls |
| Parameter Validation | 12 | Fail-fast on invalid params |
| Manifest Serialization | 8 | JSON-serializable output |
| Registry | 6 | Lookup, duplicate prevention |
| AST Guardrails | 4 | No random/datetime/uuid imports |
| Properties | 6 | name, version, repr |

### Failures Encountered and Resolved

**Run 0 Failure:**
- Root cause: Missing `numpy` and `pillow` dependencies in `pyproject.toml`
- Secondary issue: Python 3.12 `type` statement syntax invalid on 3.10/3.11
- Resolution: Added dependencies, changed type alias to `typing.Type` pattern
- Run 1: All tests passed across Python 3.10-3.12 matrix

**Evidence that validation is meaningful:**
- AST tests scan actual source code for forbidden patterns
- Hash tests verify byte-identical output across multiple runs
- Mutation tests capture array state before/after apply()

---

## 5. CI / Automation Impact

### Workflows Affected

| Workflow | Status | Change |
|----------|--------|--------|
| `.github/workflows/ci.yml` | Unchanged | No modifications |

### Checks Added

None (existing checks maintained).

### Changes in Enforcement Behavior

| Aspect | Before (M01) | After (M02) |
|--------|--------------|-------------|
| Dependencies | 4 | 6 (+numpy, +pillow) |
| Test count | 44 | 105 (+61 perturbation tests) |
| Coverage | 95% | 92% (slight decrease, still above threshold) |

### CI Assessment

| Criterion | Result |
|-----------|--------|
| Blocked incorrect changes | ✅ Yes (Run 0 caught missing deps) |
| Validated correct changes | ✅ Yes (Run 1 green) |
| Failed to observe relevant risk | ❌ No (all gates functional) |

### Signal Drift

None detected. CI remains truthful.

---

## 6. Issues & Exceptions

### Issues Encountered

**CI-RUN0: Missing Dependencies**
- Description: numpy and pillow not in pyproject.toml; Python 3.12 type syntax
- Root cause: Local environment had deps installed; syntax used Python 3.12 feature
- Resolution: Fixed in commit `7132a15`
- Status: Resolved

### New Issues Introduced

**DEP-001: No Dependency Lockfile**
- Description: pyproject.toml uses `>=` constraints; no lockfile
- Severity: LOW
- Status: Deferred to M12

---

## 7. Deferred Work

| Item | Reason | Pre-existed? | Status Changed? |
|------|--------|--------------|-----------------|
| GOV-001: Branch protection | Requires admin | Yes (M00) | No |
| SEC-001: CORS permissive | Dev-only | Yes (M00) | No |
| SCAN-001: No security scanning | Not required for perturbations | Yes (M01) | No |
| DEP-001: No dependency lockfile | Version floors sufficient | No (new discovery) | Added to registry |

**No untracked debt was introduced.**

---

## 8. Governance Outcomes

### What Changed in Governance Posture

| Before M02 | After M02 |
|------------|-----------|
| No image manipulation capability | 5 deterministic perturbation types |
| No hashing infrastructure | `image_sha256()` for verification |
| No perturbation contract | Frozen dataclass pattern established |
| No registry system | Extensible registry with duplicate prevention |
| No randomness guardrails | AST tests enforce no global random state |

### What Is Now Provably True

1. **All perturbations are deterministic** — Hash tests verify byte-identical output
2. **Gaussian noise requires explicit seed** — TypeError raised without seed parameter
3. **Input images are never mutated** — Parametrized mutation tests across all perturbations
4. **No forbidden imports in perturbation module** — AST scan enforces at CI time
5. **Registry prevents duplicate names** — DuplicateRegistrationError on collision
6. **Cross-version compatibility** — All tests pass on Python 3.10, 3.11, 3.12

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| All perturbations deterministic | ✅ Met | Hash tests pass on all Python versions |
| Noise requires seed and fails without | ✅ Met | `test_seed_required` passes |
| image_sha256 stable across runs | ✅ Met | `test_hash_stability_across_calls` (10 runs) |
| No input image mutation | ✅ Met | 5 parametrized mutation tests pass |
| Registry prevents duplicate registration | ✅ Met | `test_duplicate_registration_raises` passes |
| ≥90% coverage on perturbation module | ✅ Met | 92% actual |
| CI green on first run | ❌ Not Met | Run 0 failed (deps); Run 1 green |
| No new deferred HIGH issues | ✅ Met | DEP-001 is LOW severity |

**7/8 criteria met. Run 0 failure was legitimate missing dependency, not test weakness.**

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed to M03.**

M02 successfully established the first domain capability (deterministic image perturbation primitives) with:
- Strict determinism guarantees via frozen dataclasses and seeded RNG
- Comprehensive test coverage (61 new tests, 92% coverage)
- AST-based guardrails preventing forbidden patterns
- No boundary violations (M01 contracts preserved)
- Clean supply chain additions (numpy, pillow)
- CI green across Python 3.10-3.12 matrix

---

## 11. Authorized Next Step

Upon closeout:

1. ✅ PR #4 merged (`bc87cc5`)
2. ✅ Tag released (`v0.0.3-m02`)
3. ✅ `docs/clarity.md` updated
4. Proceed to **M03: R2L Invocation Harness**

**Constraints for M03:**
- Preserve black-box R2L invocation
- No semantic bleed from R2L internals
- No direct internal imports
- Artifact ingestion only
- Zero perturbation logic drift

---

## 12. Canonical References

### Commits

| SHA | Description |
|-----|-------------|
| `379c1ef` | feat(M02): implement deterministic image perturbation core |
| `7132a15` | fix(M02): add numpy/pillow deps and fix Python 3.10 compatibility |
| `2ff9fad` | docs(M02): add CI run analysis M02_run1.md |
| `8d279d8` | docs(M02): add milestone audit M02_audit.md |
| `bc87cc5` | Squash merge of PR #4 |

### Pull Requests

| PR | Title | Status |
|----|-------|--------|
| #4 | feat(M02): Perturbation Core - Deterministic Image Perturbation Recipes | ✅ Merged |

### Tags

| Tag | Description |
|-----|-------------|
| `v0.0.3-m02` | M02: Perturbation Core |

### CI Runs

| Run ID | Commit | Status |
|--------|--------|--------|
| 22213492888 | `379c1ef` | ❌ Failure (missing deps) |
| 22213527363 | `7132a15` | ✅ Success |

### Documents

| Document | Path |
|----------|------|
| M02 Plan | `docs/milestones/M02/M02_plan.md` |
| M02 Tool Calls | `docs/milestones/M02/M02_toolcalls.md` |
| M02 CI Analysis | `docs/milestones/M02/M02_run1.md` |
| M02 Audit | `docs/milestones/M02/M02_audit.md` |
| M02 Summary | `docs/milestones/M02/M02_summary.md` |
| clarity.md | `docs/clarity.md` |

### Repository

- **GitHub:** https://github.com/m-cahill/clarity
- **Tag:** `v0.0.3-m02`
- **PR:** https://github.com/m-cahill/clarity/pull/4

---

*End of M02 Summary*

