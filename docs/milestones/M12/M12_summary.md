# 📌 Milestone Summary — M12: Operational Hardening

**Project:** CLARITY  
**Phase:** Operational Hardening  
**Milestone:** M12 — Operational Hardening  
**Timeframe:** 2026-02-21 → 2026-02-21  
**Status:** ✅ Closed  

---

## 1. Milestone Objective

M12 existed to **strengthen CLARITY's runtime reliability, governance posture, and operational correctness** without expanding feature scope.

This milestone addressed:

- **COV-002**: Frontend branch coverage regression introduced in M11 (80% threshold exception)
- **DEP-001**: Absence of deterministic dependency lockfile (floating versions in CI)
- **SCAN-001**: No security vulnerability scanning in CI pipeline
- **Operational gaps**: Missing caching, resumability guards, and concurrency controls

Per Source of Truth:
> "M12 — Caching, resumability, concurrency controls."

Without M12, the project would have:
- Unreliable dependency resolution in CI
- No security scanning for vulnerabilities
- Reduced test coverage discipline
- No caching or concurrency safety for report generation

---

## 2. Scope Definition

### In Scope

| Area | Components |
|------|------------|
| Coverage Restoration | `downloadUtils.ts` refactor, 27 unit tests, E2E smoke test |
| Caching Layer | `cache_key.py`, `cache_manager.py`, atomic writes, file locking |
| Report Integration | `report_router.py` cache integration, 409 conflict handling |
| Dependency Discipline | `requirements.in`, `requirements.lock`, pip-tools |
| Security Scanning | pip-audit CI job, npm audit CI job |
| CI Hardening | `lockfile-check` job, `security` job |
| CORS Tightening | Environment variable-driven CORS configuration |

### Out of Scope

| Area | Rationale |
|------|-----------|
| Persistent database | M12 is hardening, not feature expansion |
| Multi-user job queue | Deferred to post-competition |
| Cloud object storage | Not needed for demo/MVP |
| Auth system | Deferred to pre-production |
| Rate limiting | Deferred to production |
| Performance benchmarking | Not required for M12 |
| UI redesign | Not in scope |

---

## 3. Work Executed

### Summary Statistics

| Metric | Value |
|--------|-------|
| Files changed | 27 |
| Lines added | +4,174 |
| Lines removed | -30 |
| New test files | 3 |
| New tests | ~92 |
| New CI jobs | 2 |

### Key Actions

1. **Frontend Download Refactor**
   - Extracted `downloadReportBlob()` helper with dependency injection
   - Created `frontend/src/utils/downloadUtils.ts` (74 lines)
   - Added 27 unit tests in `frontend/tests/downloadUtils.test.ts`
   - Added Playwright E2E smoke test in `frontend/e2e/report.spec.ts`
   - Restored branch coverage threshold to 85%

2. **Backend Cache Module**
   - Created `backend/app/clarity/cache/` module
   - Implemented `cache_key.py`: canonical JSON, SHA256 hashing
   - Implemented `cache_manager.py`: atomic writes, file locking, get_or_create
   - Added 52 tests in `backend/tests/test_cache.py`

3. **Report Router Integration**
   - Integrated `CacheManager` into `/report/generate` endpoint
   - Added `X-Cache-Hit` and `X-Cache-Key` response headers
   - Implemented HTTP 409 response for concurrent identical requests
   - Added 5 new tests for cache behavior

4. **Dependency Lockfile**
   - Created `requirements.in` with top-level dependencies
   - Generated `requirements.lock` with pip-compile (818 lines, SHA256 hashes)
   - Updated CI to install from lockfile

5. **Security Scanning CI**
   - Added `security` job to CI workflow
   - Integrated `pip-audit -r requirements.lock --strict --disable-pip`
   - Integrated `npm audit --production`

6. **Lockfile Verification CI**
   - Added `lockfile-check` job to CI workflow
   - Verifies `requirements.lock` and `package-lock.json` exist
   - Verifies pip-compile header in lockfile

7. **CORS Tightening**
   - Added `CORS_ALLOWED_ORIGINS` environment variable
   - Default to localhost in non-demo mode
   - Permissive in demo mode (documented)

---

## 4. Validation & Evidence

### Test Execution

| Suite | Tests | Result |
|-------|-------|--------|
| Backend (Python 3.10) | 875 | ✅ PASS |
| Backend (Python 3.11) | 875 | ✅ PASS |
| Backend (Python 3.12) | 875 | ✅ PASS |
| Frontend | 137 | ✅ PASS |
| E2E (Playwright) | 5+ | ✅ PASS |

### Coverage

| Module | Before | After | Delta |
|--------|--------|-------|-------|
| Backend (line) | ~95% | 94.61% | -0.4% |
| Frontend (branch) | 80% | 87.39% | **+7.39%** |

### Security Scanning

| Scanner | Result |
|---------|--------|
| pip-audit | No vulnerabilities |
| npm audit | No HIGH/CRITICAL |

### Failures Encountered and Resolved

| Failure | Root Cause | Resolution |
|---------|------------|------------|
| pip-audit hash mode error | `--no-deps` insufficient | Changed to `--disable-pip` |
| checksums.json mismatch | CRLF/LF line ending inconsistency | Recomputed hashes from git blob |
| TypeScript `global` undefined | ESM context doesn't have `global` | Changed to `globalThis` |

---

## 5. CI / Automation Impact

### Workflows Affected

| Workflow | Changes |
|----------|---------|
| `ci.yml` | +83 lines; 2 new jobs added |

### Checks Added

| Job | Purpose | Required |
|-----|---------|----------|
| `lockfile-check` | Verify lockfile existence and validity | ✅ Yes |
| `security` | Run pip-audit and npm audit | ✅ Yes |

### Enforcement Behavior

- CI now **blocks** changes with missing lockfiles
- CI now **blocks** changes with detected vulnerabilities
- CI now **blocks** changes with frontend branch coverage <85%

### Signal Assessment

| Behavior | Status |
|----------|--------|
| Blocked incorrect changes | ✅ Yes (3 corrective runs) |
| Validated correct changes | ✅ Yes (final run green) |
| Failed to observe risk | ❌ No failures |

---

## 6. Issues & Exceptions

### Issues Encountered

| Issue | Root Cause | Resolution | Tracking |
|-------|------------|------------|----------|
| pip-audit CI failure | Hash mode requires `--disable-pip` | Fixed in CI workflow | Resolved in M12 |
| checksums.json CI failure | Windows CRLF vs Linux LF | Recomputed from git blob | Resolved in M12 |
| TypeScript compilation failure | `global` not in ESM | Changed to `globalThis` | Resolved in M12 |

### Issues Resolved from Prior Milestones

| Issue | Origin | Resolution |
|-------|--------|------------|
| COV-002 | M11 | Frontend coverage restored to 87.39% |
| DEP-001 | M02 | requirements.lock with hashes |
| SCAN-001 | M01 | Security scanning CI jobs |

> No new issues were introduced during this milestone that remain unresolved.

---

## 7. Deferred Work

### Resolved This Milestone

| ID | Issue | Status |
|----|-------|--------|
| COV-002 | Frontend branch coverage 80% | ✅ Resolved |
| DEP-001 | No dependency lockfile | ✅ Resolved |
| SCAN-001 | No security scanning | ✅ Resolved |

### Still Deferred

| ID | Issue | Reason | Status Change |
|----|-------|--------|---------------|
| GOV-001 | Branch protection | Requires GitHub admin | No change |
| SEC-001 | CORS full lockdown | Demo needs permissive | Partially addressed (localhost defaults added) |

---

## 8. Governance Outcomes

### What Is Now Provably True

1. **Dependency Determinism**
   - All Python dependencies pinned with SHA256 hashes
   - CI installs from lockfile only
   - Lockfile existence verified in CI

2. **Security Scanning Institutionalized**
   - Every PR runs pip-audit and npm audit
   - CI fails on detected vulnerabilities
   - No manual intervention required

3. **Coverage Discipline Restored**
   - Frontend branch coverage ≥85% enforced
   - No exceptions or threshold reductions
   - Download logic now testable via DI

4. **Cache Determinism**
   - Cache keys computed via canonical JSON + SHA256
   - Atomic file writes prevent corruption
   - File locking prevents concurrent regeneration

5. **Concurrency Safety**
   - HTTP 409 returned for concurrent identical requests
   - Lock timeout prevents deadlocks
   - No shared global state in report generation

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| COV-002 resolved | ✅ Met | 87.39% branch coverage |
| DEP-001 resolved | ✅ Met | requirements.lock with hashes |
| SCAN-001 resolved | ✅ Met | security CI job |
| Cache layer deterministic | ✅ Met | 52 cache tests pass |
| Concurrency safe | ✅ Met | File locking + 409 response |
| CI green | ✅ Met | 8/8 jobs pass |
| No new deferrals | ✅ Met | None created |
| clarity.md updated | ✅ Met | M12 row added |
| Tag v0.0.13-m12 created | ✅ Met | Tag pushed |

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed.**

M12 is a clean operational hardening close:
- Three deferred governance items resolved
- No new deferrals created
- CI signal strengthened
- Security posture improved
- Overall score: 5.0

---

## 11. Authorized Next Step

M12 closes the operational hardening phase.

**Next milestone:** To be determined based on competition timeline and priorities.

Potential directions (not authorized, for reference only):
- M13: Real model integration (post-MedGemma release)
- M13: Full production hardening (if deploying beyond demo)

---

## 12. Canonical References

### Commits

| SHA | Description |
|-----|-------------|
| `d51f195` | M12: Operational Hardening (#15) — Merge commit |
| `v0.0.13-m12` | M12 release tag |

### Pull Requests

| PR | Title |
|----|-------|
| [#15](https://github.com/m-cahill/clarity/pull/15) | M12: Operational Hardening |

### CI Runs

| Run ID | Status |
|--------|--------|
| [22251129342](https://github.com/m-cahill/clarity/actions/runs/22251129342) | ✅ Green |

### Documents

| Document | Purpose |
|----------|---------|
| `docs/milestones/M12/M12_plan.md` | Milestone plan |
| `docs/milestones/M12/M12_run1.md` | CI run analysis |
| `docs/milestones/M12/M12_audit.md` | Milestone audit |
| `docs/milestones/M12/M12_toolcalls.md` | Tool call log |
| `docs/clarity.md` | Source of truth (updated) |

### Files Changed

| Category | Count |
|----------|-------|
| Backend source | 5 |
| Backend tests | 2 |
| Frontend source | 3 |
| Frontend tests | 4 |
| CI/CD | 1 |
| Documentation | 8 |
| Configuration | 4 |
| **Total** | **27** |

---

*Summary generated following `docs/prompts/summaryprompt.md` guidelines.*

