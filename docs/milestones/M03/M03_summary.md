# 📌 Milestone Summary — M03: R2L Invocation Harness

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Phase:** Foundation  
**Milestone:** M03 — R2L Invocation Harness  
**Timeframe:** 2026-02-20 → 2026-02-20  
**Status:** Closed

---

## 1. Milestone Objective

Implement a black-box R2L runner invocation harness and deterministic artifact ingestion layer.

M02 established image perturbation determinism. Without M03, CLARITY cannot execute R2L experiments or consume R2L artifacts. This milestone is the first cross-system integration point — the place CLARITY touches an external execution substrate.

M03 establishes:
- CLI-only invocation boundary (no R2L imports)
- Subprocess-based execution envelope with timeout enforcement
- Deterministic artifact loading and hashing
- Structured result objects for error handling
- Hardened AST guardrails (no `r2l.*` imports anywhere)

> **What would have been incomplete if this milestone did not exist?**  
> CLARITY would have no mechanism to invoke R2L runs or consume R2L output artifacts. The sweep orchestrator (M04), metrics core (M05), and robustness surfaces (M06) all depend on this harness.

---

## 2. Scope Definition

### In Scope

**Backend (R2L Runner Module):**
- `backend/app/clarity/r2l_runner.py` — R2LRunner class, subprocess invocation
- `R2LRunResult` frozen dataclass for structured results
- `R2LInvocationError` and `R2LTimeoutError` exceptions
- Timeout enforcement via subprocess timeout parameter
- Cross-platform path handling (Windows/POSIX)

**Backend (Artifact Loader Module):**
- `backend/app/clarity/artifact_loader.py` — Artifact loading and validation
- `load_manifest()` — Parse and validate manifest.json
- `load_trace_pack()` — Parse and validate trace_pack.jsonl
- `hash_artifact()` — SHA256 file hashing
- Minimal schema validation (required fields only)

**Backend (Deprecations):**
- `backend/app/clarity/r2l_interface.py` — R2LInterface deprecated with warnings

**Tests:**
- `backend/tests/fixtures/fake_r2l.py` — Deterministic test fixture
- `backend/tests/test_r2l_runner.py` — 32 runner tests
- `backend/tests/test_artifact_loader.py` — 39 loader tests
- `backend/tests/test_m03_guardrails.py` — 16 AST guardrail tests
- `backend/tests/test_boundary_contract.py` — Updated for deprecation warnings

**Governance:**
- `docs/milestones/M03/M03_plan.md` — Detailed plan with locked answers
- `docs/milestones/M03/M03_toolcalls.md` — Tool call log
- `docs/milestones/M03/M03_run1.md` — CI run analysis

### Out of Scope

- Sweep execution logic (M04)
- Metrics computation (M05)
- Robustness surface estimation (M06)
- Parallelization
- GPU usage
- Persistence
- UI integration
- Caching
- Async execution
- Real R2L integration (uses fake fixture)

**Scope did not change during execution.**

---

## 3. Work Executed

### High-Level Actions

| Action | Files | Lines |
|--------|-------|-------|
| R2L Runner module creation | 1 | +324 |
| Artifact Loader module creation | 1 | +232 |
| Fake R2L fixture | 1 | +154 |
| Test suites (3 files) | 3 | +1462 |
| r2l_interface.py deprecation | 1 | +74/-108 |
| __init__.py exports update | 1 | +61/-9 |
| test_boundary_contract.py update | 1 | +44/-29 |
| Governance docs | 3 | +574 |
| **Total** | 12 | +2850/-108 |

### Commits

| SHA | Message | Type |
|-----|---------|------|
| `2c3a2be` | feat(M03): implement R2L invocation harness and artifact loader | Feature |
| `dc4b18a` | docs(M03): add CI run analysis M03_run1.md | Docs |
| `d6fb692` | Squash merge of PR #5 | Merge |

### Mechanical vs Semantic Changes

- **Mechanical:** __init__.py export additions, deprecation warnings wiring
- **Semantic:** All runner logic, artifact loading, validation, hashing, subprocess management

---

## 4. Validation & Evidence

### Tests Run

| Tier | Framework | Count | Status |
|------|-----------|-------|--------|
| Backend Unit | Pytest | 192 | ✅ Pass |
| Frontend Unit | Vitest | 16 | ✅ Pass |
| E2E | Playwright | 5 | ✅ Pass |

### Coverage

| Component | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Backend (overall) | ≥85% | 96% | ✅ Pass |
| r2l_runner.py | ≥90% | 97% | ✅ Pass |
| artifact_loader.py | ≥90% | 100% | ✅ Pass |

### Test Categories (New in M03)

| Category | Tests | Enforcement |
|----------|-------|-------------|
| Runner Init | 8 | Parameter validation |
| Successful Invocation | 9 | Happy path + determinism |
| Non-Zero Exit | 3 | Error handling |
| Timeout Enforcement | 3 | Timeout → R2LTimeoutError |
| Missing Artifacts | 2 | Artifact validation |
| Result Immutability | 2 | Frozen dataclass |
| Manifest Loading | 11 | Parse + validation |
| Trace Pack Loading | 11 | JSONL parse + step validation |
| Hash Artifact | 9 | SHA256 determinism |
| AST Guardrails | 16 | No r2l/random/datetime/uuid imports |

### Failures Encountered and Resolved

**Local Testing Issue:**
- Root cause: Windows path handling with `shlex.split()` using POSIX mode
- Resolution: Use `posix=False` on Windows, proper path quoting
- CI Run: All tests passed across Python 3.10-3.12 matrix on first run

**Evidence that validation is meaningful:**
- AST tests scan actual source code for forbidden patterns
- Hash tests verify byte-identical output across multiple runs
- Timeout tests actually invoke subprocess with short timeout
- Fake R2L fixture produces deterministic, verifiable output

---

## 5. CI / Automation Impact

### Workflows Affected

| Workflow | Status | Change |
|----------|--------|--------|
| `.github/workflows/ci.yml` | Unchanged | No modifications |

### Checks Added

None (existing checks maintained).

### Changes in Enforcement Behavior

| Aspect | Before (M02) | After (M03) |
|--------|--------------|-------------|
| Test count | 105 | 192 (+87) |
| Coverage | 92% | 96% (+4%) |
| Boundary guardrails | M01 patterns | Hardened (no r2l.* at all) |

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

**WIN-PATH: Windows Path Handling**
- Description: `shlex.split()` uses POSIX quoting by default, breaking Windows paths
- Root cause: Cross-platform subprocess invocation
- Resolution: Use `posix=False` on Windows, quote paths with spaces
- Status: Resolved in initial implementation

### New Issues Introduced

None. No HIGH issues introduced.

---

## 7. Deferred Work

| Item | Reason | Pre-existed? | Status Changed? |
|------|--------|--------------|-----------------|
| GOV-001: Branch protection | Requires admin | Yes (M00) | No |
| SEC-001: CORS permissive | Dev-only | Yes (M00) | No |
| SCAN-001: No security scanning | Not required for harness | Yes (M01) | No |
| DEP-001: No dependency lockfile | Version floors sufficient | Yes (M02) | No |
| pythonjsonlogger deprecation | External dependency | Yes (pre-M00) | No |

**No untracked debt was introduced.**

---

## 8. Governance Outcomes

### What Changed in Governance Posture

| Before M03 | After M03 |
|------------|-----------|
| No R2L invocation capability | CLI-based subprocess invocation |
| No artifact consumption | Load, validate, hash R2L artifacts |
| M01 boundary allowed r2l.internal | All r2l.* imports forbidden |
| No timeout enforcement | subprocess timeout → R2LTimeoutError |
| No structured error handling | R2LInvocationError with exit_code/stdout/stderr |

### What Is Now Provably True

1. **CLARITY can invoke R2L via CLI** — R2LRunner executes subprocess with captured output
2. **No R2L imports exist in CLARITY** — AST tests enforce at CI time
3. **Artifact hashing is deterministic** — SHA256 of file bytes, verified across runs
4. **Timeout is enforced** — subprocess.TimeoutExpired → R2LTimeoutError
5. **Non-zero exit raises exception** — R2LInvocationError with full context
6. **Result objects are immutable** — Frozen dataclass pattern
7. **Cross-platform compatibility** — Tests pass on Windows (local) and Linux (CI)

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| R2LRunner executes fake CLI | ✅ Met | `test_successful_invocation_returns_result` passes |
| Artifacts load and hash deterministically | ✅ Met | `test_hash_stability`, `test_seed_determinism` pass |
| Timeout enforced (R2LTimeoutError) | ✅ Met | `test_timeout_raises_r2l_timeout_error` passes |
| Non-zero exit raises R2LInvocationError | ✅ Met | `test_nonzero_exit_raises` passes |
| No R2L imports in CLARITY | ✅ Met | `test_no_r2l_imports_in_clarity_module` passes |
| CI green on first run | ✅ Met | Run 22214441510 all green |
| Coverage thresholds met | ✅ Met | 97%/100% on new modules, 96% overall |
| No HIGH issues introduced | ✅ Met | No HIGH issues in audit |

**8/8 criteria met.**

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed to M04.**

M03 successfully established the first cross-system integration point with:

- ✅ Pure CLI invocation boundary (no R2L imports)
- ✅ Subprocess-based execution with timeout enforcement
- ✅ Deterministic artifact loading and hashing
- ✅ Structured error handling with full context
- ✅ Hardened AST guardrails (all r2l.* forbidden)
- ✅ 87 new tests, 96% coverage
- ✅ CI green on first run across Python 3.10-3.12

---

## 11. Authorized Next Step

Upon closeout:

1. ✅ PR #5 merged (`d6fb692`)
2. ✅ Tag released (`v0.0.4-m03`)
3. ✅ `docs/clarity.md` updated
4. Proceed to **M04: Sweep Orchestrator**

**Constraints for M04:**
- Preserve M03 invocation boundary
- Use R2LRunner for all R2L invocations
- No direct subprocess calls outside runner
- Maintain artifact loading through artifact_loader
- No new R2L imports

---

## 12. Canonical References

### Commits

| SHA | Description |
|-----|-------------|
| `2c3a2be` | feat(M03): implement R2L invocation harness and artifact loader |
| `dc4b18a` | docs(M03): add CI run analysis M03_run1.md |
| `d6fb692` | Squash merge of PR #5 |

### Pull Requests

| PR | Title | Status |
|----|-------|--------|
| #5 | feat(M03): R2L Invocation Harness - Black-box Runner and Artifact Ingestion | ✅ Merged |

### Tags

| Tag | Description |
|-----|-------------|
| `v0.0.4-m03` | M03: R2L Invocation Harness |

### CI Runs

| Run ID | Commit | Status |
|--------|--------|--------|
| 22214441510 | `2c3a2be` | ✅ Success |

### Documents

| Document | Path |
|----------|------|
| M03 Plan | `docs/milestones/M03/M03_plan.md` |
| M03 Tool Calls | `docs/milestones/M03/M03_toolcalls.md` |
| M03 CI Analysis | `docs/milestones/M03/M03_run1.md` |
| M03 Summary | `docs/milestones/M03/M03_summary.md` |
| clarity.md | `docs/clarity.md` |

### Repository

- **GitHub:** https://github.com/m-cahill/clarity
- **Tag:** `v0.0.4-m03`
- **PR:** https://github.com/m-cahill/clarity/pull/5

---

*End of M03 Summary*

