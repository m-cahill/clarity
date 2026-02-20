# M09 — Counterfactual Sweep Orchestration + UI Console Skeleton

**Status:** In Progress  
**Baseline:** M08 (`v0.0.9-m08`)  
**Branch:** `m09-ui-console`  
**Tag:** `v0.0.10-m09`  
**Audit Mode:** DELTA

---

## Objective

M08 created the *probe engine*. M09 makes it usable.

This milestone:

1. Implements **actual counterfactual sweep orchestration** (CF-002 closure).
2. Adds a **minimal interactive console** for:
   - Selecting a baseline run
   - Generating grid masks
   - Executing probes
   - Viewing structured ProbeSurface results

M09 is the first milestone that justifies **preview deployment**.

---

## Locked Answers

### 1) R2L Invocation Strategy

**M09 should NOT invoke real R2L in CI.**

- The orchestrator must be built so it *can* invoke R2L via the existing runner interface, but:
  - **Unit + integration tests must use a stubbed runner** (in-process fake) with deterministic outputs.
  - **No subprocess R2L calls in CI** (too risky for time, environment, GPU availability).
- Add a **single "manual smoke" CLI path** (documented) that can be used locally to run with real R2L, but it must be excluded from CI tests.

This closes CF-002 in the sense of "orchestration pathway exists and is executable," while keeping CI truthful and deterministic.

### 2) Baseline Run Spec / Baseline ID

**Baseline source = repo fixture.**

- Use a small deterministic fixture set committed to the repo:
  - `backend/tests/fixtures/baselines/…`
  - include: image file + minimal spec json (prompt + axis/value metadata)
- `baseline_id` maps to these fixtures via an in-repo lookup table (dict) in the orchestrator or a small registry module.

**Do not depend on an external artifact directory existing.**
The UI baseline selector can list these fixture IDs (hardcoded for now).

### 3) Frontend Routing

**Add React Router.**
- `react-router-dom`
- One route: `/counterfactual`
- Keep existing landing/health at `/`

### 4) API Mocking for Frontend Tests

**Use MSW.**
- MSW keeps tests realistic and avoids brittle component-level mocking.
- Frontend tests should verify request payload shape and response rendering.
- Keep the handler responses deterministic.

### 5) Branch Name

**`m09-ui-console`** (per clarity.md source of truth)

### 6) Tag

**`v0.0.10-m09`**

---

## Architectural Split

### Layer 1 — Backend Orchestrator (Core)

New module:

```
backend/app/clarity/counterfactual_orchestrator.py
```

Responsibilities:

- Accept baseline run spec
- Generate masked image variants
- Invoke R2L harness (stubbed for CI)
- Run:
  - MetricsEngine
  - SurfaceEngine
  - GradientEngine
  - CounterfactualEngine
- Persist temporary results (in-memory only)
- Return structured ProbeSurface

No DB yet.

### Layer 2 — UI Console Skeleton

Frontend:

```
frontend/src/pages/CounterfactualConsole.tsx
```

Minimal components:

- Baseline selector (fixture list)
- Grid size input (k)
- Axis/value dropdown
- "Run Probe" button
- JSON results viewer
- Simple delta table

No charts yet.

---

## Scope Definition

### ✅ In Scope

#### Backend

- CounterfactualOrchestrator class
- Deterministic execution path
- Stubbed R2L runner for CI
- Baseline fixture registry
- FastAPI endpoint: `POST /counterfactual/run`
- Request schema:
  - baseline_id
  - grid_size
  - axis
  - value
- Response schema:
  - ProbeSurface JSON

#### Frontend

- React Router integration
- Single route: `/counterfactual`
- Form + results viewer
- API integration
- MSW handlers

#### Tests

- ≥45 new backend tests
- ≥10 frontend tests
- Integration test: end-to-end probe via API
- Orchestrator determinism test
- Guardrail AST test

### ❌ Out of Scope

- Heatmaps (M10)
- Saliency overlays (M10)
- Persistence layer (M11)
- Concurrency optimization (M12)
- GPU parallel orchestration
- User authentication
- Real R2L invocation in CI

---

## Orchestrator Flow

```
baseline_id
   ↓
Load baseline image + spec from fixtures
   ↓
Generate grid masks (k×k)
   ↓
For each region:
    apply_mask()
    invoke R2L runner (stubbed)
    compute metrics → surface → gradient
    compute delta vs baseline
   ↓
Aggregate ProbeSurface
   ↓
Return JSON
```

---

## Determinism Constraints

Must preserve:

- Seed list unchanged
- Mask fill value = 128
- Mask ordering stable
- Region ID stable
- No random sampling
- No async race conditions
- No multiprocessing

All execution sequential for M09.

---

## Test Plan

### Backend Categories

1. Orchestrator happy path
2. Deterministic double-run equality
3. API contract validation
4. Error handling (invalid baseline)
5. R2L harness invocation correctness (stubbed)
6. Delta integrity verification
7. No forbidden imports
8. Response schema stability
9. Baseline registry lookups
10. Fixture loading

### Frontend Categories

1. Form renders
2. API call executed
3. JSON displayed
4. Error state handled
5. Deterministic rerender
6. Routing works
7. MSW integration

---

## Definition of Done

- [ ] Orchestrator implemented
- [ ] FastAPI endpoint added
- [ ] Stubbed runner for CI
- [ ] Baseline fixtures committed
- [ ] UI route created
- [ ] ≥45 new backend tests
- [ ] ≥10 new frontend tests
- [ ] ≥95% coverage backend module
- [ ] No workflow changes
- [ ] CI green first run
- [ ] CF-002 removed from deferred registry
- [ ] clarity.md updated
- [ ] Tag: `v0.0.10-m09`

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| R2L invocation side effects | Stubbed runner for CI |
| Determinism drift | Double-run equality tests |
| API schema drift | pydantic models frozen |
| UI breaking CI | Keep minimal React surface |
| Performance | Small grid sizes default (k=3) |

---

## Notes

Earlier assistant plan suggested branch name `m09-counterfactual-orchestrator-ui`, but `clarity.md` is the source of truth, so using `m09-ui-console`.

---

*Plan locked with stakeholder answers on 2026-02-20.*
