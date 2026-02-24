# M17 — Frontend ↔ Backend Connectivity Hardening

**Mode:** DELTA — Deployment Integrity  
**No model changes. No metric changes. No schema changes.**

---

## Objective

Resolve the Netlify production frontend error:

> "Failed to fetch"

while:

- Preserving `/health` green state
- Maintaining deterministic backend behavior
- Keeping M16 Kaggle artifacts frozen
- Avoiding any inference or R2L modification

This is a deployment-layer milestone only.

---

## Root Scope

We already know:

- `/health` works
- Backend is alive
- Render is responding
- Only POST or JSON endpoints fail (or cross-origin requests from Netlify)

Root cause is narrowed to:

1. CORS misconfiguration
2. OPTIONS preflight rejection
3. Incorrect API base URL (frontend env)
4. Environment variable mismatch
5. Missing allowed headers
6. Netlify → Render origin mismatch

---

## Deliverables

### Code

- CORS middleware verified and corrected (env-based; no origin hardcoding)
- Explicit allowed origins via `CORS_ALLOWED_ORIGINS` on Render
- Explicit allowed methods and headers (already present; verify)
- Environment-based API URL resolution: **`VITE_API_BASE_URL`** (or project API base env var) on Netlify
- Frontend: single source of truth for base URL — **refactor console to use `getBaseUrl()` from `api.ts`**
- Preflight OPTIONS verified

### Validation

- Local frontend → local backend works
- Netlify frontend → Render backend works
- No CORS errors in browser console
- No "Failed to fetch"

### Documentation

- `docs/milestones/M17/M17_plan.md` (this file)
- `docs/milestones/M17/M17_toolcalls.md`
- `docs/milestones/M17/M17_run1.md`
- `docs/milestones/M17/M17_audit.md`
- `docs/milestones/M17/M17_summary.md`
- `clarity.md` updated with M17 row (per milestone map)

---

## Implementation Plan

---

### Phase 1 — Diagnose Precisely (No Code Yet)

1. **Confirm frontend base URL**
   - Locate where frontend defines API base: **`VITE_API_BASE_URL`** (canonical) or **`VITE_API_URL`** (legacy fallback).
   - Verify: Netlify env exists, matches exact Render URL, no trailing slash mismatch, HTTPS enforced.
   - Document finding: `CounterfactualConsole.tsx` previously used `VITE_API_URL` only; `api.ts` uses `getBaseUrl()` with `VITE_API_BASE_URL` then `VITE_API_URL`. Unify on `getBaseUrl()`.

2. **Inspect failing request (browser DevTools)**
   - Record: full URL, method (POST?), OPTIONS status, response headers, exact CORS error.
   - Log in `M17_run1.md`.

---

### Phase 2 — Backend CORS Hardening

- **Middleware position:** CORS already added before route definitions in `main.py`. Keep as-is.
- **No hardcoding:** Origins come only from env:
  - **Render:** set `CORS_ALLOWED_ORIGINS=https://majestic-dodol-25e71c.netlify.app` (comma-separated if multiple).
  - If not set → backend defaults to localhost-only (safe).
- **OPTIONS:** Verify from terminal:
  ```bash
  curl -X OPTIONS https://<render-url>/counterfactual/run \
    -H "Origin: https://majestic-dodol-25e71c.netlify.app" \
    -H "Access-Control-Request-Method: POST"
  ```
  Expect HTTP 200 and `access-control-allow-origin` in response.

---

### Phase 3 — Environment Normalization

**Netlify**

- `VITE_API_BASE_URL` set to `https://clarity-1sra.onrender.com` (or actual Render backend URL).
- Production and deploy-preview both configured.

**Render**

- `CORS_ALLOWED_ORIGINS=https://majestic-dodol-25e71c.netlify.app`
- No hardcoded localhost or Netlify URLs in code.

---

### Phase 4 — Strict Validation Checklist

After deploy:

- From Netlify site: DevTools → Network; run counterfactual probe.
- Confirm: no red requests, no CORS block, POST returns 200, JSON visible.
- Capture screenshot of Network tab success (optional; document in run doc).

---

### Phase 5 — Regression Guardrail

- Backend: add or extend test that CORS allows configured origin when `CORS_ALLOWED_ORIGINS` is set (or documented curl reproduction in M17_run1).
- No frontend test required beyond existing.

---

## Guardrails (Inherited from M16)

- No model changes
- No inference changes
- No schema changes
- No metrics changes
- No dependency upgrades
- No UI redesign

M17 touches only:

- FastAPI middleware (config remains env-driven)
- Environment config and documentation
- Frontend: single change — use `getBaseUrl()` from `api.ts` in CounterfactualConsole
- Deployment wiring docs

---

## Verification Criteria (Merge Gate)

All must pass:

- `/health` returns 200
- `/counterfactual/run` (POST) returns 200 when called from Netlify
- OPTIONS preflight returns 200 for Netlify origin
- Netlify production works (no "Failed to fetch")
- No browser console CORS errors
- CI green
- No Python tests broken
- No frontend tests broken

---

## Tag

`v0.0.18-m17`

---

## Post-M17 State

- Kaggle submission remains frozen
- Demo link fully interactive
- No "Failed to fetch"
- End-to-end integrity restored

---

## Governance Alignment

Single capability (deployment connectivity); end-to-end verified; audit defensible; no opportunistic expansion.
