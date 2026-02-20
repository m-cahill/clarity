# 📌 M00 — Repository Bootstrap + Full-Stack E2E Verification

**Project:** CLARITY
**Phase:** Foundation
**Milestone:** M00 — Bootstrap + E2E Health Path
**Status Target:** Closed (Green CI)
**Baseline:** Public empty repo `m-cahill/clarity`

---

# 1. Milestone Objective

Establish a full-stack CLARITY skeleton with:

* Backend service
* Frontend React app
* Local integration wiring
* Deterministic CI
* Verified E2E path

The milestone is successful only if:

> A frontend request successfully reaches backend `/health` in CI and passes E2E tests.

No perturbations.
No R2L integration.
No deployment complexity.

Just wiring, determinism, and verifiable correctness.

---

# 2. Scope Definition

## In Scope

### Backend

* FastAPI service
* `/health` endpoint
* `/version` endpoint (static version + git SHA placeholder)
* JSON structured logging
* Deterministic configuration
* Dockerfile
* Pytest + coverage baseline (≥85%)

### Frontend

* React + Vite + TypeScript
* `/health` call via fetch
* Basic UI indicator (Healthy / Unhealthy)
* Display service name/version from backend response
* Vitest baseline (v8 coverage)
* Playwright E2E

### Integration

* Docker Compose (backend + frontend + optional postgres placeholder)
* CI workflow (GitHub Actions)
* Python 3.10-3.12 matrix
* Node 20 LTS
* Artifact uploads (JUnit + coverage)

### Governance

* `clarity.md` created with milestone table
* `docs/ARCHITECTURE_CONTRACT.md` (existing)
* LICENSE Apache-2.0
* `.editorconfig`
* `.gitignore`
* Pre-commit config (minimal, non-blocking, local only)

---

## Out of Scope

* R2L integration
* Perturbations
* Monte Carlo
* Robustness metrics
* Netlify deploy
* Render deploy
* Dataset ingestion
* GPU execution

Deployment explicitly deferred to M01+.

---

# 3. Repository Layout

```
clarity/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── health.py
│   │   └── logging_config.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── HealthIndicator.tsx
│   │   └── main.tsx
│   ├── tests/
│   │   └── HealthIndicator.test.tsx
│   ├── e2e/
│   │   └── health.spec.ts
│   ├── vite.config.ts
│   ├── playwright.config.ts
│   └── Dockerfile
│
├── ops/
│   └── docker-compose.dev.yml
│
├── .github/workflows/ci.yml
├── docs/clarity.md
├── LICENSE
├── .editorconfig
├── .gitignore
├── .pre-commit-config.yaml
└── docs/ARCHITECTURE_CONTRACT.md
```

---

# 4. Backend Implementation

### FastAPI App

`GET /health`

Returns:

```json
{
  "status": "ok",
  "service": "clarity-backend",
  "version": "0.0.1"
}
```

`GET /version`

Returns:

```json
{
  "version": "0.0.1",
  "git_sha": null
}
```

### Logging

* JSON logging (python-json-logger)
* Stable key ordering
* No timestamps required for determinism
* Request ID middleware stub (trace integration later)

### Tests

* Unit test `/health`
* Unit test `/version`
* Coverage ≥ 85% (line)
* Deterministic test ordering

---

# 5. Frontend Implementation

### React App

* On load, call `/health`
* Display:

```
Backend Status: OK
Service: clarity-backend
Version: 0.0.1
```

or

```
Backend Status: ERROR
```

### Tests

* Vitest unit test: mock API call
* Playwright E2E:
  * Start backend
  * Start frontend
  * Visit page
  * Assert visible text includes "clarity-backend" and "0.0.1"

---

# 6. CI Workflow

`.github/workflows/ci.yml`

Jobs:

## 1️⃣ Backend

* Python 3.10, 3.11, 3.12 matrix
* Install deps
* Run pytest
* Enforce coverage ≥85%
* Upload coverage.xml

## 2️⃣ Frontend

* Node 20
* Install deps
* Run vitest
* Upload coverage summary

## 3️⃣ E2E

* Spin backend in background (with readiness wait)
* Spin frontend
* Run Playwright headless
* Upload Playwright report
* Assert real backend values in UI

## Required Checks

* backend
* frontend
* e2e

No silent skips.
No continue-on-error.

---

# 7. Determinism Guardrails

M00 must prove:

* Running CI twice produces identical backend `/health` JSON
* Frontend display is deterministic
* No randomness in tests
* Docker builds reproducible (pinned version tags, not `latest`)

---

# 8. Dataset Posture (M00 Decision)

For M00:

**Do not include any real medical images.**

Use:

* Static placeholder image
* Or synthetic test asset

Dataset selection deferred to M02.

---

# 9. Exit Criteria

M00 is closed when:

* Repo pushed to GitHub on branch `m00-bootstrap`
* PR created to main
* CI fully green
* Frontend calls backend `/health` in Playwright
* E2E asserts real backend response values (service name, version)
* Coverage ≥85%
* `clarity.md` updated with milestone table
* Architecture contract committed

No deploys required.

---

# 10. Locked Decisions

| Decision | Answer |
|----------|--------|
| Branch strategy | Option B — `m00-bootstrap` branch, PR to main |
| Python version | Option B — 3.10-3.12 matrix |
| Node version | Option A — Node 20 LTS only |
| Frontend coverage | Option A — Vitest built-in v8 |
| Pre-commit | Option A — configured, not enforced in CI |
| Milestone folder | Yes — create docs/milestones/M00/ structure |
| Docker base images | Option B — version tags (e.g., python:3.11-slim-bookworm) |
| Backend API prefix | Option A — root paths (/health, /version) |

