# M17 Delta Audit — Frontend ↔ Backend Connectivity Hardening

## Audit Metadata

| Field | Value |
|-------|-------|
| **Milestone** | M17 |
| **Mode** | DELTA AUDIT — Deployment Integrity Only |
| **Auditor** | Cursor Agent |
| **Date** | 2026-02-24 |
| **Branch** | `m17-connectivity-hardening` |
| **Tag** | `v0.0.18-m17` |

---

## Objective Verification

### Goal
> Resolve Netlify production "Failed to fetch"; unify API base URL resolution; verify CORS and env so live demo is fully interactive.

### Status: ✅ ACHIEVED

---

## Verification Criteria (Merge Gate)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `/health` returns 200 | ✅ | Live validation confirmed |
| OPTIONS preflight returns 200 for Netlify origin | ✅ | Live validation confirmed |
| POST `/counterfactual/run` returns 200 from Netlify | ✅ | Live validation confirmed |
| Netlify production works (no "Failed to fetch") | ✅ | Live demo validated |
| No browser console CORS errors | ✅ | Live validation confirmed |
| API calls hit `https://clarity-1sra.onrender.com` | ✅ | Request URL confirmed |
| Counterfactual probe completes and renders results | ✅ | Live validation confirmed |

---

## Phase Verification

### Phase 1 — Diagnosis

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Frontend base URL centralized | ✅ | `getBaseUrl()` in `api.ts`; CounterfactualConsole uses it |
| Canonical env: `VITE_API_BASE_URL` | ✅ | Documented in plan, run1, netlify.toml, api.ts |
| Legacy `VITE_API_URL` marked non-production | ✅ | api.ts comment; optional for E2E/Playwright only |
| No localhost fallback in app code | ✅ | getBaseUrl() returns `/api` when no env set (dev proxy) |

### Phase 2 — Backend CORS

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Origins from env only (no hardcoding) | ✅ | main.py uses CORS_ALLOWED_ORIGINS / ALLOWED_ORIGIN |
| Render: Netlify origin allowed | ✅ | `CORS_ALLOWED_ORIGINS` documented; live OPTIONS 200 |
| OPTIONS preflight returns 200 | ✅ | Live validation confirmed |

### Phase 3 — Environment Normalization

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Netlify: `VITE_API_BASE_URL` set | ✅ | netlify.toml; production build uses Render URL |
| Render: `CORS_ALLOWED_ORIGINS` set | ✅ | clarity.md; live CORS success |
| Single source of truth for base URL | ✅ | getBaseUrl() only; no duplicate API_BASE in console |

### Phase 4 — Live Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Request URL = Render | ✅ | User confirmed all API calls hit clarity-1sra.onrender.com |
| OPTIONS 200 + Access-Control-Allow-Origin | ✅ | User confirmed |
| POST 200 | ✅ | User confirmed |
| Probe execution and results rendered | ✅ | User confirmed |
| No CORS / connection refused / red failures | ✅ | User confirmed |

### Phase 5 — Regression Guardrail

| Requirement | Status | Evidence |
|-------------|--------|----------|
| CORS / env documented | ✅ | M17_run1.md curl examples; clarity.md env table |
| No frontend test regression | ✅ | Existing tests use getBaseUrl() / proxy |

---

## Guardrails Compliance

| Guardrail | Compliant | Notes |
|-----------|-----------|-------|
| No R2L changes | ✅ | Zero R2L files modified |
| No inference logic changes | ✅ | Backend CORS/config only; no app logic |
| No metric changes | ✅ | Not applicable |
| No schema changes | ✅ | Not applicable |
| No dependency upgrades | ✅ | Not applicable |
| No UI redesign | ✅ | Console only uses getBaseUrl(); no UX change |
| M16 Kaggle artifacts frozen | ✅ | No changes to submission docs or bundle |

---

## Artifact Inventory

### Modified Files

| File | Change |
|------|--------|
| `frontend/src/api.ts` | getBaseUrl() comments: canonical vs legacy env |
| `frontend/src/pages/CounterfactualConsole.tsx` | Use getBaseUrl() from api.ts (single source of truth) |
| `netlify.toml` | VITE_API_BASE_URL comment; branch-deploy context |
| `backend/README.md` | Port 8000 + frontend proxy note for local dev |
| `docs/clarity.md` | M17 row; current milestone; env table (if updated) |
| `docs/milestones/M17/M17_plan.md` | Plan and verification criteria |
| `docs/milestones/M17/M17_run1.md` | Diagnosis, env checklist, curl verification |

### New Files

| File | Purpose |
|------|---------|
| `docs/milestones/M17/M17_audit.md` | This document |
| `docs/milestones/M17/M17_summary.md` | Closure summary |
| `docs/milestones/M17/M17_toolcalls.md` | Tool call log |
| `docs/milestones/M17/pr_body.md` | PR description |

---

## Root Cause Summary

Production "Failed to fetch" was attributable to deployment/config rather than application design:

- **Frontend:** Console previously used `VITE_API_URL` (or localhost fallback) instead of `getBaseUrl()`; Netlify may have had wrong env scope, cached build, or typo in `VITE_API_BASE_URL`.
- **Fix:** Single source of truth (`getBaseUrl()`), canonical env `VITE_API_BASE_URL` documented, optional `VITE_API_URL` for E2E only.
- **Backend:** CORS already env-driven; ensuring Render has `CORS_ALLOWED_ORIGINS` for Netlify origin completed the fix.

---

## Final Verdict

**M17 connectivity hardening: COMPLETE**

All verification criteria and live validation checks passed. Demo is fully interactive; no CORS or connection errors. Architecture is correct; issue was deployment/env, not design flaw.
