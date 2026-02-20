# 📌 Milestone Summary — M09: Counterfactual Sweep Orchestration + UI Console Skeleton

**Project:** CLARITY  
**Phase:** Phase 2 — Interactive Orchestration  
**Milestone:** M09 — Counterfactual Sweep Orchestration + UI Console Skeleton  
**Timeframe:** 2026-02-20 → 2026-02-20  
**Status:** ✅ Closed

---

## 1. Milestone Objective

M08 established the counterfactual probe engine infrastructure (region masking, delta computation, ProbeSurface aggregation). However, this infrastructure was not executable end-to-end — there was no orchestration layer to coordinate baseline loading, mask generation, inference runs, and result aggregation.

M09 exists to:

1. **Close CF-002** — Implement actual counterfactual sweep orchestration
2. **Provide first interactive UI** — Allow users to configure and execute probes
3. **Enable deploy preview** — First milestone suitable for external demonstration

Without M09, CLARITY would remain a collection of analytical components without user-facing execution capability.

---

## 2. Scope Definition

### In Scope

**Backend:**
- `CounterfactualOrchestrator` class with full orchestration flow
- `StubbedRunner` implementing `RunnerProtocol` for CI-safe testing
- Baseline fixture registry (`registry.json` + committed images)
- `POST /counterfactual/run` API endpoint
- `GET /counterfactual/baselines` API endpoint
- 73 new backend tests

**Frontend:**
- React Router integration (`react-router-dom`)
- `/` route (Home page with navigation)
- `/counterfactual` route (Console page)
- Baseline selector dropdown
- Grid size input
- Axis/value configuration
- JSON results viewer
- MSW handlers for test mocking
- 22 new frontend tests

**Documentation:**
- M09_plan.md with locked answers
- M09_toolcalls.md
- M09_run1.md (CI analysis)

### Out of Scope

- Real R2L invocation in CI (stubbed per locked answer)
- Heatmap/visualization overlays (M10)
- Database persistence (M11)
- GPU parallel orchestration (M12+)
- User authentication
- Charts or graphical results display

Scope remained stable throughout execution.

---

## 3. Work Executed

### Backend Implementation

1. Created `counterfactual_orchestrator.py` (594 lines):
   - `BaselineSpec` dataclass for baseline specifications
   - `RunnerResult` dataclass for inference outputs
   - `RunnerProtocol` interface for runner abstraction
   - `StubbedRunner` implementing deterministic CI-safe runner
   - `OrchestratorConfig` for execution configuration
   - `OrchestratorResult` for aggregated results
   - `CounterfactualOrchestrator.run()` method for full orchestration

2. Created `counterfactual_router.py` (120 lines):
   - `GET /counterfactual/baselines` — list available baselines
   - `POST /counterfactual/run` — execute probe with parameters

3. Created baseline fixtures:
   - `registry.json` mapping baseline IDs to files
   - `test_spec_001.json`, `test_spec_002.json` — baseline specifications
   - `test_image_001.png`, `test_image_002.png` — test images
   - `create_test_images.py` — fixture generation script

4. Wrote 73 backend tests covering:
   - Orchestrator happy path
   - Deterministic double-run equality
   - Baseline loading and validation
   - Stubbed runner behavior
   - Delta computation
   - Error handling
   - Serialization
   - AST guardrails

### Frontend Implementation

1. Added React Router (`react-router-dom` v7.2.0)

2. Created `Home.tsx` (80 lines):
   - Navigation cards for CLARITY features
   - Health indicator
   - Milestone table display

3. Created `CounterfactualConsole.tsx` (345 lines):
   - Baseline selector (populated from API)
   - Grid size input (1-10, default 3)
   - Axis dropdown (brightness, contrast, noise)
   - Value dropdown (0p8, 0p9, 1p0, 1p1, 1p2)
   - Run Probe button with loading state
   - JSON results viewer with formatting
   - Error handling and display

4. Created MSW handlers for API mocking:
   - `GET /api/health`
   - `GET /api/counterfactual/baselines`
   - `POST /api/counterfactual/run`

5. Wrote 22 frontend tests covering:
   - Component rendering
   - Form interaction
   - API integration
   - Error handling

### File Counts

- **31 files changed**
- **+4,053 lines added**
- **-103 lines removed**

---

## 4. Validation & Evidence

### CI Runs

| Run ID | Type | Status | Tests |
|--------|------|--------|-------|
| 22242331052 | PR | 🔴 Failed | Coverage thresholds not met |
| 22242422760 | PR | 🔴 Failed | TypeScript unused imports |
| 22242461145 | PR | 🔴 Failed | E2E heading ambiguity |
| 22242551473 | PR | 🟢 Pass | All 6 jobs green |
| 22242936883 | Post-merge | 🟢 Pass | All 6 jobs green |

### Test Results (Final)

| Suite | Count | Status |
|-------|-------|--------|
| Backend | 609 | ✅ Pass |
| Frontend | 53 | ✅ Pass |
| E2E | 5 | ✅ Pass |

### Coverage

| Target | Threshold | Actual |
|--------|-----------|--------|
| Backend | 85% | 96%+ |
| Frontend Lines | 85% | 97.6% |
| Frontend Branches | 85% | 86.2% |
| Frontend Functions | 85% | 100% |

### Guardrails Verified

- No subprocess imports (AST test)
- No random/uuid imports (AST test)
- No datetime.now usage (AST test)
- No R2L direct imports (AST test)
- Deterministic double-run equality (test)
- 8-decimal rounding consistency (test)

---

## 5. CI / Automation Impact

### Workflows Affected

No workflow files were modified.

### Checks Status

| Check | Status | Notes |
|-------|--------|-------|
| Backend (3.10/3.11/3.12) | ✅ | Matrix stable |
| Frontend | ✅ | Coverage thresholds met |
| E2E Tests | ✅ | Full stack verified |
| CI Success | ✅ | Aggregate gate |

### Signal Quality

CI correctly:
- **Blocked** insufficient coverage (Run 1)
- **Blocked** unused imports (Run 2)
- **Blocked** ambiguous E2E selector (Run 3)
- **Validated** corrected implementation (Run 4)

No false positives or signal drift observed.

---

## 6. Issues & Exceptions

### Issues Encountered

| Issue | Root Cause | Resolution |
|-------|------------|------------|
| Frontend coverage < 85% | Error handling paths untested | Added CounterfactualConsoleErrors.test.tsx |
| TypeScript unused imports | Copy-paste from template | Removed unused beforeEach/afterEach |
| E2E heading ambiguity | Multiple elements matching "CLARITY" | Used `exact: true` matcher |

All issues were resolved within the milestone.

### New Issues

No new issues were introduced.

---

## 7. Deferred Work

### Pre-existing Deferrals (Unchanged)

| ID | Issue | Status |
|----|-------|--------|
| GOV-001 | Branch protection | Deferred to manual config |
| SEC-001 | CORS permissive | Deferred to pre-production |
| SCAN-001 | No security scanning | Deferred to M12 |
| DEP-001 | No dependency lockfile | Deferred to M12 |
| CF-001 | Evidence-map-derived regions | Deferred to M10 |

### Resolved Deferrals

| ID | Issue | Evidence |
|----|-------|----------|
| CF-002 | Actual counterfactual sweeps | `CounterfactualOrchestrator` + API endpoint |

---

## 8. Governance Outcomes

### What Is Now Provably True

1. **Counterfactual orchestration is executable** — The full pipeline from baseline to ProbeSurface works end-to-end.

2. **CI remains deterministic** — Stubbed runner ensures no environmental dependencies in automated testing.

3. **Real R2L path exists but is isolated** — `RunnerProtocol` allows plugging in real runner for local smoke tests.

4. **Frontend architecture is established** — React Router integration sets foundation for additional routes.

5. **Full-stack integration is verified** — E2E tests confirm backend API works with frontend UI.

6. **First deploy-preview-ready state** — The system can be meaningfully demonstrated externally.

---

## 9. Exit Criteria Evaluation

| Criterion | Met? | Evidence |
|-----------|------|----------|
| Orchestrator implemented | ✅ Met | `counterfactual_orchestrator.py` |
| FastAPI endpoint added | ✅ Met | `POST /counterfactual/run` |
| Stubbed runner for CI | ✅ Met | `StubbedRunner` class |
| Baseline fixtures committed | ✅ Met | `fixtures/baselines/*` |
| UI route created | ✅ Met | `/counterfactual` route |
| ≥45 new backend tests | ✅ Met | 73 tests |
| ≥10 new frontend tests | ✅ Met | 22 tests |
| ≥95% coverage backend module | ✅ Met | 96%+ |
| CI green | ✅ Met | Runs 22242551473, 22242936883 |
| CF-002 closed | ✅ Met | Resolved in registry |
| clarity.md updated | ✅ Met | M09 row updated |
| Tag created | ✅ Met | `v0.0.10-m09` |

All exit criteria met without adjustment.

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed.**

M09 successfully delivers:
- First executable counterfactual orchestration pathway
- First interactive UI console
- First full-stack integration
- First deploy-preview-ready milestone

The CLARITY system is now capable of:
1. Loading a baseline specification from committed fixtures
2. Generating grid masks for the baseline image
3. Simulating inference on masked variants (via stubbed runner)
4. Computing deltas relative to baseline
5. Aggregating results into a ProbeSurface
6. Exposing all of this via REST API
7. Providing a web UI for configuration and result viewing

---

## 11. Authorized Next Step

**Proceed to M10: Visualization Overlays**

M10 scope (pending planning):
- Evidence map overlays
- Saliency heatmaps
- CF-001 closure (evidence-map-derived regions)

Constraints:
- Maintain CI-safe stubbed runner pattern
- No database persistence until M11
- No GPU optimization until M12

---

## 12. Canonical References

### Commits

| SHA | Message |
|-----|---------|
| f68017d | feat(M09): counterfactual sweep orchestration + UI console skeleton |
| 93a8a6c | fix(M09): improve frontend test coverage to meet thresholds |
| 913c31d | fix: remove unused imports in tests |
| 64a95fc | fix: use exact matching in E2E test for CLARITY heading |
| 0c0180f | Merge pull request #11 from m-cahill/m09-ui-console |
| 33df580 | docs: close M09 milestone, resolve CF-002 |

### Pull Requests

- **PR #11**: m09-ui-console → main (merged)

### Tags

- **v0.0.10-m09**: M09 release tag

### CI Runs

- **22242551473**: PR final green run
- **22242936883**: Post-merge green run

### Documents

- `docs/milestones/M09/M09_plan.md` — Detailed plan with locked answers
- `docs/milestones/M09/M09_toolcalls.md` — Tool execution log
- `docs/milestones/M09/M09_run1.md` — CI analysis report
- `docs/milestones/M09/M09_audit.md` — Delta audit
- `docs/clarity.md` — Updated milestone table

---

*End of M09 Summary*

