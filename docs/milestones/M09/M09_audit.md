# 🧾 M09 DELTA AUDIT — Counterfactual Sweep Orchestration + UI Console Skeleton

---

## 1. Header

* **Milestone:** M09 — Counterfactual Sweep Orchestration + UI Console Skeleton
* **Mode:** DELTA AUDIT
* **Range:** `v0.0.9-m08...v0.0.10-m09`
* **Current SHA:** `33df580`
* **Merge Commit:** `0c0180f`
* **CI Status:** 🟢 Green (final run: 22242936883)
* **Audit Verdict:** 🟢 **PASS** — Full-stack counterfactual orchestration implemented with stubbed R2L runner, interactive UI console, deterministic fixtures, 95 new tests across backend and frontend, CF-002 resolved, first deploy-preview-ready milestone.

CI evidence: PR Run 22242551473 (green), Post-merge Run 22242936883 (green).

---

## 2. Executive Summary (Delta-Focused)

### Concrete Improvements

1. **Counterfactual orchestration pathway complete** — `CounterfactualOrchestrator` coordinates baseline loading, mask generation, inference simulation, and ProbeSurface aggregation.
2. **Interactive UI console** — `/counterfactual` route with baseline selector, grid configuration, and JSON results viewer.
3. **CI-safe stubbed runner** — `StubbedRunner` provides deterministic outputs without real R2L invocation.
4. **First full-stack feature** — Backend endpoint + frontend UI integrated end-to-end with E2E tests passing.
5. **95 new tests** — 73 backend (orchestrator + API) + 22 frontend (console + error handling).

### Concrete Risks

1. **Frontend dependencies increased** — `react-router-dom` (+6 deps) and `msw` (+9 deps) added.
2. **Frontend coverage at lower threshold boundary** — Branch coverage at 86.2% (threshold: 85%).
3. **CF-001 remains deferred** — Evidence-map-derived regions still pending M10.

### Single Most Important Next Action

Document the stubbed vs real R2L runner invocation paths in `clarity.md` to establish clear CLI smoke-test procedure.

---

## 3. Delta Map & Blast Radius

### Files Changed

```
31 files changed, +4053 insertions, -103 deletions

Backend (Core):
  backend/app/clarity/counterfactual_orchestrator.py  (+594 lines, new)
  backend/app/counterfactual_router.py                (+120 lines, new)
  backend/app/clarity/__init__.py                     (+27 lines)
  backend/app/main.py                                 (+5 lines)

Backend (Fixtures):
  backend/tests/fixtures/baselines/*                  (+6 files)

Backend (Tests):
  backend/tests/test_counterfactual_orchestrator.py   (+681 lines, new)
  backend/tests/test_counterfactual_api.py            (+175 lines, new)

Frontend (Core):
  frontend/src/App.tsx                                (refactored for Router)
  frontend/src/pages/CounterfactualConsole.tsx        (+345 lines, new)
  frontend/src/pages/Home.tsx                         (+80 lines, new)
  frontend/src/pages/*.css                            (+460 lines, new)
  frontend/src/mocks/*                                (+121 lines, new)

Frontend (Tests):
  frontend/tests/CounterfactualConsole.test.tsx       (+214 lines, new)
  frontend/tests/CounterfactualConsoleErrors.test.tsx (+206 lines, new)
  frontend/tests/Home.test.tsx                        (+69 lines, new)

Dependencies:
  frontend/package.json                               (+react-router-dom, +msw)
```

### Risk Zones Touched

| Zone          | Touched? | Notes                                      |
| ------------- | -------- | ------------------------------------------ |
| Auth          | ❌        | None                                       |
| Persistence   | ❌        | None (in-memory only)                      |
| CI Glue       | ❌        | No workflow changes                        |
| Contracts     | ✅        | New API endpoints (`/counterfactual/*`)    |
| Migrations    | ❌        | None                                       |
| Concurrency   | ❌        | Sequential execution enforced              |
| Observability | ❌        | None                                       |
| Frontend      | ✅        | First interactive UI routes                |

**Blast radius includes both backend API layer and frontend application layer.**

---

## 4. Architecture & Modularity

### Keep

* **Stubbed runner pattern** — `RunnerProtocol` + `StubbedRunner` allows CI-safe testing while preserving real R2L invocation path.
* **Baseline fixture registry** — `registry.json` + committed test images provide deterministic, reproducible test data.
* **Frozen dataclasses** — `BaselineSpec`, `RunnerResult`, `OrchestratorConfig`, `OrchestratorResult`.
* **Router pattern** — FastAPI router cleanly separates counterfactual endpoints from health/version.
* **React Router integration** — Clean SPA routing with `/` (Home) and `/counterfactual` (Console).
* **MSW for API mocking** — Realistic frontend tests without backend dependency.
* **8-decimal rounding preserved** — Consistent with M05–M08 pattern.
* **AST guardrails** — No subprocess, no random, no datetime.now, no uuid, no r2l imports.

### Fix Now (≤ 90 min)

None identified.

### Defer

| Item                           | Reason                                       | Target |
| ------------------------------ | -------------------------------------------- | ------ |
| Evidence-map-derived regions   | Requires M10 saliency overlays               | M10    |
| Real R2L integration           | Local smoke-test only; CI stays stubbed      | M12+   |
| Database persistence           | Not blocking; in-memory sufficient           | M11    |
| Visualization overlays         | M10 scope                                    | M10    |

---

## 5. CI/CD & Workflow Integrity

Post-merge CI Run 22242936883: 🟢 Success

### Evaluation

| Check                       | Status     |
| --------------------------- | ---------- |
| Required checks enforced    | ✅          |
| No skipped gates            | ✅          |
| No continue-on-error misuse | ✅          |
| Matrix stable (3.10–3.12)   | ✅          |
| Coverage gate ≥85%          | ✅          |
| No workflow edits           | ✅          |
| Dependency delta documented | ✅          |

CI remains a truthful signal.

---

## 6. Tests & Coverage (Delta-Only)

### Coverage Delta

| Metric                         | M08    | M09    | Δ       |
| ------------------------------ | ------ | ------ | ------- |
| Backend Overall                | 96%+   | 96%+   | Stable  |
| counterfactual_orchestrator.py | —      | 95%+   | New     |
| counterfactual_router.py       | —      | 95%+   | New     |
| Frontend Lines                 | 97.5%  | 97.6%  | +0.1%   |
| Frontend Branches              | 85%    | 86.2%  | +1.2%   |
| Frontend Functions             | 95%+   | 100%   | +5%     |

### New Tests

**Backend (73 tests):**
- Orchestrator happy path (8)
- Deterministic double-run equality (4)
- Baseline loading (12)
- Stubbed runner behavior (8)
- Delta computation (6)
- Error handling (9)
- Serialization (6)
- Guardrails AST-based (6)
- API endpoints (12)
- Schema validation (2)

**Frontend (22 tests):**
- Home page rendering (5)
- CounterfactualConsole rendering (6)
- Form interaction (4)
- API integration (4)
- Error handling (3)

### Flaky Tests

None detected.

### Missing Tests

None required for current scope.

---

## 7. Security & Supply Chain

| Aspect                    | Status         |
| ------------------------- | -------------- |
| New dependencies (backend)| None           |
| New dependencies (frontend)| react-router-dom, msw |
| Dependency audit          | No vulnerabilities |
| Secrets risk              | None           |
| Workflow boundary changes | None           |
| SBOM continuity           | Unchanged      |
| Provenance continuity     | Unchanged      |

### Frontend Dependency Analysis

* **react-router-dom** (v7.2.0) — Well-maintained, widely used routing library.
* **msw** (v2.7.0) — Test-only dependency for API mocking.

Both dependencies are development-grade appropriate and introduce no production security concerns.

---

## 8. Top Issues (Max 7)

No HIGH or MEDIUM issues identified.

### LOW Issues (Informational)

| ID | Category | Issue | Status |
|----|----------|-------|--------|
| M09-LOW-001 | Coverage | Frontend branch coverage at 86.2% (threshold: 85%) | ACCEPTABLE |
| M09-LOW-002 | Docs | R2L smoke-test procedure not documented | DEFER to M10 |

---

## 9. PR-Sized Action Plan

None required before proceeding to M10.

---

# Cumulative Trackers

---

## 10. Deferred Issues Registry (Updated)

| ID       | Issue                             | Discovered | Deferred To | Reason           | Blocker? | Exit Criteria               |
| -------- | --------------------------------- | ---------- | ----------- | ---------------- | -------- | --------------------------- |
| GOV-001  | Branch protection                 | M00        | Manual      | Admin required   | No       | Protection visible via API  |
| SEC-001  | CORS permissive                   | M00        | Pre-prod    | Dev-only         | No       | Env-based CORS config       |
| SCAN-001 | No security scanning              | M01        | M12         | Hardening phase  | No       | Dependabot + scan jobs      |
| DEP-001  | No dependency lockfile            | M02        | M12         | Non-blocking     | No       | Locked pip deps             |
| CF-001   | Evidence-map-derived regions      | M08        | M10         | Requires saliency| No       | RegionMask from evidence maps |

### Resolved This Milestone

| ID     | Issue                          | Resolved | Evidence                                   |
| ------ | ------------------------------ | -------- | ------------------------------------------ |
| CF-002 | Actual counterfactual sweeps   | M09      | `CounterfactualOrchestrator` + API endpoint |

---

## 11. Score Trend

| Milestone | Arch | Mod | Health | CI  | Sec | Perf | DX  | Docs | Overall  |
| --------- | ---- | --- | ------ | --- | --- | ---- | --- | ---- | -------- |
| M07       | 5.0  | 5.0 | 5.0    | 5.0 | 4.3 | 3.2  | 4.6 | 5.0  | 4.90     |
| M08       | 5.0  | 5.0 | 5.0    | 5.0 | 4.3 | 3.2  | 4.7 | 5.0  | 4.92     |
| **M09**   | 5.0  | 5.0 | 5.0    | 5.0 | 4.3 | 3.2  | 4.8 | 5.0  | **4.94** |

### Weighting

* Arch: 15%
* Mod: 15%
* Health: 15%
* CI: 15%
* Sec: 10%
* Perf: 5%
* DX: 15%
* Docs: 10%

### Score Movement

* DX +0.1 (first interactive UI, full-stack integration)
* Overall +0.02 (meaningful improvement in user-facing capability)

---

## 12. Flake & Regression Log

| Item | Type | First Seen | Current Status | Last Evidence | Fix/Defer |
| ---- | ---- | ---------- | -------------- | ------------- | --------- |
| —    | —    | —          | —              | —             | —         |

No flakes or regressions detected.

---

# Machine-Readable Appendix

```json
{
  "milestone": "M09",
  "mode": "DELTA_AUDIT",
  "commit": "33df580",
  "merge_commit": "0c0180f",
  "range": "v0.0.9-m08...v0.0.10-m09",
  "verdict": "green",
  "quality_gates": {
    "ci": "PASS",
    "tests": "PASS",
    "coverage": "PASS",
    "security": "PASS",
    "workflows": "PASS",
    "contracts": "PASS"
  },
  "issues": [],
  "resolved_issues": [
    {
      "id": "CF-002",
      "issue": "Actual counterfactual sweeps",
      "resolved": "M09",
      "evidence": "CounterfactualOrchestrator + POST /counterfactual/run endpoint"
    }
  ],
  "deferred_registry_updates": [],
  "score_trend_update": {
    "milestone": "M09",
    "overall": 4.94,
    "dx": 4.8
  },
  "new_tests": {
    "backend": 73,
    "frontend": 22,
    "total": 95
  },
  "files_changed": 31,
  "lines_added": 4053,
  "lines_removed": 103
}
```

---

# Final Verdict

🟢 **Milestone objectives met. Safe to proceed to M10.**

M09 successfully establishes counterfactual sweep orchestration with interactive UI:

- ✅ `CounterfactualOrchestrator` implemented with stubbed runner
- ✅ `POST /counterfactual/run` API endpoint
- ✅ `GET /counterfactual/baselines` endpoint
- ✅ Baseline fixture registry with committed test images
- ✅ React Router integration (`/` and `/counterfactual`)
- ✅ `CounterfactualConsole.tsx` with form and results viewer
- ✅ MSW handlers for frontend testing
- ✅ 95 new tests (73 backend + 22 frontend)
- ✅ CI green across all runs (no iteration required after coverage fix)
- ✅ CF-002 resolved
- ✅ First deploy-preview-ready milestone

---

## Audit Certification

**Audit Lead:** AI Agent (Cursor)  
**Audit Date:** 2026-02-20  
**Audit Mode:** DELTA AUDIT  
**Verdict:** 🟢 **PASS**

---

*End of M09 Audit*

