# 📦 M10.5 Plan — Demo Deployment Layer

**Project:** CLARITY  
**Milestone:** M10.5 — Demo Deployment Layer  
**Phase:** Post-M10 Visualization  
**Baseline Tag:** `v0.0.11-m10`  
**Branch:** `m10.5-demo-deploy`  
**Audit Mode:** DELTA  
**Status:** In Progress

---

## 1️⃣ Milestone Objective

Enable a **live, stable, deterministic demo environment** that:

- Serves precomputed CLARITY artifacts
- Displays visualization overlays via Netlify-hosted frontend
- Uses Render for a thin artifact-serving backend
- Preserves all CLARITY ↔ R2L boundary invariants
- Does not introduce nondeterministic execution

> **Without this milestone:** CLARITY remains local-only and cannot serve as a public credibility artifact for Upwork positioning.

---

## 2️⃣ Architecture (Demo Mode)

```
Browser
   ↓
Netlify (Frontend)
   ↓
Render (Read-Only API)
   ↓
Precomputed Artifact Store (in-repo)
```

### Key Principles

- **No cloud GPU execution**
- **No live sweep generation**
- **No mutation of R2L artifacts**
- **Artifacts are read-only**
- **Single fixed demo case (case_001)**

---

## 3️⃣ Locked Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Demo case count | **One case** (`case_001`) | Lowest scope, highest clarity |
| Frontend UI | **Single fixed demo view** (no selector) | Simplicity |
| Domain | **Default Netlify URL** (`*.netlify.app`) | No DNS dependency |
| Artifact storage | **In-repo** under `demo_artifacts/` | Version-controlled, hash guardrails |
| Artifact generation | **Synthetic/mock** matching schemas | Deployment plumbing, not results |
| Secrets handling | **Auto-skip** if missing + job summary note | CI truthful |
| Workflow structure | **Separate `deploy.yml`** | CI purity, no coupling |
| API URL | **Add `VITE_API_BASE_URL` support** | Portability |
| Backend mode | **Separate `demo_router.py`** | Clean separation |
| Milestone naming | **M10_5 folder**, no tag until closure | Standard discipline |

---

## 4️⃣ Scope Definition

### ✅ In Scope

#### Frontend (Netlify)

- Production deploy on `main`
- Deploy previews on PR
- Environment variable `VITE_API_BASE_URL` support
- Demo mode banner: **"Demo Mode — Precomputed Artifacts (Synthetic)"**
- Basic E2E smoke test against preview URL
- Static asset hosting for overlay images

#### Backend (Render)

- Lightweight FastAPI service with `demo_router.py`
- Endpoints:
  - `GET /health`
  - `GET /demo/cases` → returns `[{id: "case_001", ...}]`
  - `GET /demo/cases/{id}/surface` → returns surface JSON
  - `GET /demo/cases/{id}/overlay` → returns overlay bundle JSON
  - `GET /demo/cases/{id}/metrics` → returns metrics JSON
- Static artifact loading from `demo_artifacts/`
- CORS restricted to Netlify domain
- No authentication (demo-only)
- Read-only enforcement

#### Demo Artifacts

```
demo_artifacts/
└── case_001/
    ├── manifest.json          # Case metadata
    ├── robustness_surface.json
    ├── overlay_bundle.json
    ├── metrics.json
    └── checksums.json         # SHA-256 hashes
```

- Immutable once committed
- Synthetic data matching schemas
- Checksummed
- Explicitly marked as demo/synthetic in metadata

#### CI Additions

- New `.github/workflows/deploy.yml`
- Jobs:
  - `deploy_preview` (PR only)
  - `deploy_production` (main only, after CI passes)
  - `post_deploy_healthcheck`
- Concurrency guard to prevent overlapping deploys
- Auto-skip if secrets missing (with job summary note)

### ❌ Out of Scope

- Live Monte Carlo runs
- On-demand perturbation sweeps
- Multi-user sessions
- Database persistence
- Authentication system
- Artifact generation in cloud
- GPU inference in cloud
- Custom domain configuration
- Case selector UI

---

## 5️⃣ Environment Variables

### GitHub Secrets (to be configured by user)

| Secret | Purpose |
|--------|---------|
| `NETLIFY_AUTH_TOKEN` | Netlify CLI authentication |
| `NETLIFY_SITE_ID` | Target Netlify site |
| `RENDER_DEPLOY_HOOK_URL` | Trigger Render deploy |

### Netlify Environment Variables

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | Render service base URL |
| `VITE_APP_MODE` | `demo` |

### Render Environment Variables

| Variable | Value |
|----------|-------|
| `APP_ENV` | `demo` |
| `ALLOWED_ORIGIN` | Netlify URL (exact origin) |
| `ARTIFACT_ROOT` | `demo_artifacts` |
| `LOG_LEVEL` | `INFO` |

---

## 6️⃣ Guardrails

| Guardrail | Implementation |
|-----------|----------------|
| Determinism | CI asserts artifact hashes match `checksums.json` |
| No-Overwrite | Backend mounts artifacts read-only; test verifies no write access |
| Contract | AST test ensures demo_router.py has no R2L imports |
| Deploy Gating | Production deploy requires all CI checks green |
| Secrets Skip | Deploy jobs skip gracefully with summary note if secrets absent |

---

## 7️⃣ Test Plan

### Backend (15–20 tests)

1. Schema load/parse correctness
2. Endpoint determinism (response hash stable)
3. CORS allowlist behavior
4. Path traversal protection (no `../` escapes)
5. Read-only enforcement (no write operations)
6. 404 for nonexistent case
7. Health endpoint returns expected structure
8. No R2L imports (AST guardrail)

### Frontend (8–12 tests)

1. API base URL resolution from environment
2. Demo mode banner renders when `VITE_APP_MODE=demo`
3. Happy-path fetch + render overlay
4. Error state on API failure
5. Version display (if present)

### E2E (3 smoke tests)

1. Homepage loads successfully
2. Overlay asset loads and renders
3. Surface JSON endpoint returns valid data

---

## 8️⃣ CI Workflow Structure

### `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true

jobs:
  deploy_preview:
    if: github.event_name == 'pull_request'
    # ... Netlify preview deploy
    
  deploy_production:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: [verify_ci_passed]
    # ... Netlify + Render production deploy
    
  post_deploy_healthcheck:
    needs: [deploy_production]
    # ... Verify /health returns 200
```

---

## 9️⃣ Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Artifact corruption | Hash validation in CI |
| CORS misconfig | Explicit `ALLOWED_ORIGIN` |
| Accidental GPU compute | No adapter invocation in demo_router |
| Drift from local version | Version variables in artifacts |
| CI churn | Concurrency guard |
| Secrets not configured | Auto-skip with job summary |

---

## 🔟 Exit Criteria

- [ ] Netlify preview deploy works on PR (or skips gracefully)
- [ ] Render demo API endpoints implemented
- [ ] Production deploy gated and working (or skips gracefully)
- [ ] E2E smoke passes (local mode)
- [ ] Artifact immutability verified via checksums
- [ ] Demo mode banner visible in UI
- [ ] `docs/clarity.md` updated with demo endpoint placeholder
- [ ] Audit score ≥ 4.95

---

## 1️⃣1️⃣ Execution Steps

1. Create branch: `git checkout -b m10.5-demo-deploy`
2. Create `demo_artifacts/case_001/` with synthetic data
3. Implement `backend/app/demo_router.py`
4. Add `VITE_API_BASE_URL` support to frontend
5. Add demo mode banner component
6. Create `.github/workflows/deploy.yml`
7. Write backend tests
8. Write frontend tests
9. Write E2E smoke tests
10. Run full CI matrix
11. Generate `M10_5_run1.md`
12. Await merge permission

---

## 1️⃣2️⃣ Authorized Next Step After Closure

Proceed to:
- **M11** — Report Export Hardening

---

*Plan locked with answers from 2026-02-20.*

