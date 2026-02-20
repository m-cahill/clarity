# 📌 Milestone Summary — M04: Sweep Orchestrator

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Phase:** Foundation  
**Milestone:** M04 — Sweep Orchestrator  
**Timeframe:** 2026-02-20 → 2026-02-20  
**Status:** Closed

---

## 1. Milestone Objective

Implement a deterministic, multi-axis perturbation sweep engine.

M03 established the R2L invocation boundary. Without M04, CLARITY cannot execute structured experiment grids or produce reproducible sweep artifacts. This milestone is where CLARITY becomes behaviorally interesting — the first time experiment topology is formally expressed.

M04 establishes:
- Cartesian product expansion of perturbation axes × seeds
- Deterministic execution ordering (alphabetical axes, declared values/seeds)
- OS-safe directory naming with value encoding
- Spec injection without mutating original files
- Canonical sweep manifest with byte-identical reproducibility
- Output overwrite protection

> **What would have been incomplete if this milestone did not exist?**  
> CLARITY would have no mechanism to execute structured perturbation sweeps or produce reproducible experiment directories. The metrics core (M05), robustness surfaces (M06), and all downstream analysis depend on this orchestration layer.

---

## 2. Scope Definition

### In Scope

**Backend (Sweep Models Module):**
- `backend/app/clarity/sweep_models.py` — SweepAxis, SweepConfig, SweepRunRecord dataclasses
- `SweepConfigValidationError` exception for fail-fast validation
- `encode_axis_value()` — Deterministic value encoding for directory names
- `build_run_directory_name()` — OS-safe directory naming

**Backend (Sweep Orchestrator Module):**
- `backend/app/clarity/sweep_orchestrator.py` — SweepOrchestrator class
- `SweepResult` frozen dataclass for execution results
- `SweepExecutionError` and `OutputDirectoryExistsError` exceptions
- Cartesian product computation with deterministic ordering
- Spec injection via deep copy
- Atomic directory creation
- Canonical sweep_manifest.json generation

**Tests:**
- `backend/tests/test_sweep_models.py` — 44 model tests
- `backend/tests/test_sweep_orchestrator.py` — 34 orchestrator tests
- `backend/tests/test_m03_guardrails.py` — Extended with 12 M04 guardrails

**Governance:**
- `docs/milestones/M04/M04_plan.md` — Detailed plan with locked answers
- `docs/milestones/M04/M04_toolcalls.md` — Tool call log
- `docs/milestones/M04/M04_run1.md` — CI run analysis

### Out of Scope

- Metrics computation (M05)
- Robustness surface estimation (M06)
- Parallelization (M12)
- Resume/recovery (M12)
- Caching (M12)
- GPU logic
- Persistence to database
- UI integration
- Real R2L integration (uses fake fixture)

**Scope did not change during execution.**

---

## 3. Work Executed

### High-Level Actions

| Action | Files | Lines |
|--------|-------|-------|
| Sweep models module creation | 1 | +242 |
| Sweep orchestrator module creation | 1 | +381 |
| Test suites (2 files) | 2 | +1321 |
| Guardrail test extension | 1 | +167 |
| __init__.py exports update | 1 | +40/-15 |
| Governance docs | 3 | +440 |
| **Total** | 9 | +2576/-15 |

### Commits

| SHA | Message | Type |
|-----|---------|------|
| `666b0c5` | feat(M04): implement sweep orchestrator with deterministic multi-axis perturbation sweeps | Feature |
| `25c226d` | docs(M04): add CI run analysis M04_run1.md - all green first run | Docs |
| `cabffaa` | docs(M04): update toolcalls before merge | Docs |
| `0b79078` | Squash merge of PR #6 | Merge |

### Mechanical vs Semantic Changes

- **Mechanical:** __init__.py export additions
- **Semantic:** All sweep models, orchestration logic, Cartesian expansion, spec injection, directory naming, manifest generation

---

## 4. Validation & Evidence

### Tests Run

| Tier | Framework | Count | Status |
|------|-----------|-------|--------|
| Backend Unit | Pytest | 279 | ✅ Pass |
| Frontend Unit | Vitest | 16 | ✅ Pass |
| E2E | Playwright | 5 | ✅ Pass |

### Coverage

| Component | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Backend (overall) | ≥85% | 95% | ✅ Pass |
| sweep_models.py | ≥95% | 100% | ✅ Pass |
| sweep_orchestrator.py | ≥90% | 94% | ✅ Pass |

### Test Categories (New in M04)

| Category | Tests | Enforcement |
|----------|-------|-------------|
| SweepAxis validation | 13 | Name format, empty values |
| SweepConfig validation | 10 | Duplicates, empty axes/seeds/adapter |
| Cartesian expansion | 5 | Count, ordering, determinism |
| Directory naming | 4 | Encoding, uniqueness, OS-safety |
| Spec injection | 5 | Perturbations, seed, no mutation |
| Manifest generation | 6 | Content, determinism, hashes |
| Error handling | 3 | Output exists, missing spec, invalid JSON |
| M04 guardrails | 12 | No subprocess, no r2l imports |

### Failures Encountered and Resolved

**None.** CI green on first run across all Python versions (3.10-3.12).

**Evidence that validation is meaningful:**
- Determinism tests run sweep twice and compare byte output
- Directory collision test verifies uniqueness across full Cartesian grid
- Spec injection tests verify original file unchanged
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

| Aspect | Before (M03) | After (M04) |
|--------|--------------|-------------|
| Test count | 192 | 279 (+87) |
| Coverage | 96% | 95% (-1%) |
| Guardrail tests | 16 | 28 (+12) |

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

**None.** M04 implemented cleanly without encountering issues.

### New Issues Introduced

None. No HIGH issues introduced.

---

## 7. Deferred Work

| Item | Reason | Pre-existed? | Status Changed? |
|------|--------|--------------|-----------------|
| GOV-001: Branch protection | Requires admin | Yes (M00) | No |
| SEC-001: CORS permissive | Dev-only | Yes (M00) | No |
| SCAN-001: No security scanning | Not required for sweep | Yes (M01) | No |
| DEP-001: No dependency lockfile | Version floors sufficient | Yes (M02) | No |
| Parallelization | Not needed for MVP | New (M04) | Deferred to M12 |
| Resume/recovery | Requires persistence | New (M04) | Deferred to M12 |

**No untracked debt was introduced.**

---

## 8. Governance Outcomes

### What Changed in Governance Posture

| Before M04 | After M04 |
|------------|-----------|
| No sweep execution capability | Deterministic multi-axis sweep orchestration |
| No experiment topology | Cartesian product expansion |
| No reproducible run directories | OS-safe, deterministic directory naming |
| No sweep artifacts | Canonical sweep_manifest.json |
| M03 boundary untested at scale | Boundary exercised via full sweep tests |

### What Is Now Provably True

1. **Execution order is deterministic** — Same config produces identical run sequence
2. **Directory names are unique** — Collision detection test verifies
3. **Manifests are byte-identical** — Same sweep produces identical manifest bytes
4. **Spec files are not mutated** — Deep copy ensures original unchanged
5. **Output directories are protected** — Cannot overwrite previous sweep results
6. **All R2L invocation via R2LRunner** — AST guardrails enforce at CI time
7. **No subprocess in orchestrator** — AST guardrails verify

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Cartesian product executed correctly | ✅ Met | `test_correct_run_count_multi_axis` passes |
| Deterministic output structure verified | ✅ Met | `test_deterministic_ordering` passes |
| sweep_manifest.json deterministic | ✅ Met | `test_manifest_deterministic` byte comparison |
| All runs invoked via R2LRunner | ✅ Met | `test_no_subprocess_import_in_sweep_orchestrator` |
| No boundary violations | ✅ Met | All guardrail tests pass |
| CI green | ✅ Met | Run 22215222193 all green |
| Coverage thresholds met | ✅ Met | 100%/94% on new modules, 95% overall |
| No HIGH issues introduced | ✅ Met | No HIGH issues in audit |

**8/8 criteria met.**

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed to M05.**

M04 successfully established the first behaviorally interesting milestone with:

- ✅ Deterministic multi-axis perturbation sweep orchestration
- ✅ Provably stable execution ordering
- ✅ OS-safe directory naming with collision detection
- ✅ Spec injection without mutation
- ✅ Output overwrite protection
- ✅ Byte-identical sweep manifests
- ✅ All boundary constraints maintained
- ✅ 87 new tests, 95% coverage
- ✅ CI green on first run

---

## 11. Authorized Next Step

Upon closeout:

1. ✅ PR #6 merged (`0b79078`)
2. ✅ M04_audit.md generated
3. ✅ M04_summary.md generated
4. ⏳ Tag release (`v0.0.5-m04`)
5. ⏳ Update `docs/clarity.md`
6. Proceed to **M05: Metrics Core (ESI + Drift)**

**Constraints for M05:**
- Consume sweep output from M04 orchestrator
- Maintain R2LRunner boundary
- No direct R2L imports
- Metrics must be deterministic given identical sweep output

---

## 12. Canonical References

### Commits

| SHA | Description |
|-----|-------------|
| `666b0c5` | feat(M04): implement sweep orchestrator |
| `25c226d` | docs(M04): add CI run analysis |
| `cabffaa` | docs(M04): update toolcalls before merge |
| `0b79078` | Squash merge of PR #6 |

### Pull Requests

| PR | Title | Status |
|----|-------|--------|
| #6 | feat(M04): Sweep Orchestrator - Deterministic Multi-Axis Perturbation Sweeps | ✅ Merged |

### Tags

| Tag | Description |
|-----|-------------|
| `v0.0.5-m04` | M04: Sweep Orchestrator (pending) |

### CI Runs

| Run ID | Commit | Status |
|--------|--------|--------|
| 22215222193 | `666b0c5` | ✅ Success |

### Documents

| Document | Path |
|----------|------|
| M04 Plan | `docs/milestones/M04/M04_plan.md` |
| M04 Tool Calls | `docs/milestones/M04/M04_toolcalls.md` |
| M04 CI Analysis | `docs/milestones/M04/M04_run1.md` |
| M04 Audit | `docs/milestones/M04/M04_audit.md` |
| M04 Summary | `docs/milestones/M04/M04_summary.md` |
| clarity.md | `docs/clarity.md` |

### Repository

- **GitHub:** https://github.com/m-cahill/clarity
- **Tag:** `v0.0.5-m04` (pending)
- **PR:** https://github.com/m-cahill/clarity/pull/6

---

*End of M04 Summary*

