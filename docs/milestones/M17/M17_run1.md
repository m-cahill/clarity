# M17 Run 1 — Diagnosis & Validation

## Workflow / Run Context

| Field | Value |
|-------|--------|
| **Milestone** | M17 — Frontend ↔ Backend Connectivity Hardening |
| **Run** | 1 (diagnosis + implementation) |
| **Intent** | Fix Netlify "Failed to fetch"; unify API base URL resolution; verify CORS/env |

---

## Phase 1 — Diagnosis (Pre-Implementation)

### 1. Frontend API base URL

| Finding | Detail |
|--------|--------|
| **Canonical env var** | `VITE_API_BASE_URL` (production). Legacy fallback: `VITE_API_URL`. |
| **Central resolution** | `frontend/src/api.ts` → `getBaseUrl()`: 1) VITE_API_BASE_URL, 2) VITE_API_URL, 3) `/api`. |
| **Pre-M17 bug** | `CounterfactualConsole.tsx` used its own `API_BASE = import.meta.env.VITE_API_URL \|\| "http://localhost:8000"`, so it never used `VITE_API_BASE_URL`. Netlify builds with `VITE_API_BASE_URL` set would still hit the wrong base in the console (legacy fallback or default). |
| **Fix applied** | Console refactored to use `getBaseUrl()` from `api.ts`. Single source of truth. |

### 2. Backend CORS

| Finding | Detail |
|--------|--------|
| **Config** | `backend/app/main.py`: origins from env only. Priority: `CORS_ALLOWED_ORIGINS` → `ALLOWED_ORIGIN` (demo) → demo `["*"]` → localhost only. |
| **Hardcoding** | None. M17 keeps it that way. |
| **Render requirement** | Set `CORS_ALLOWED_ORIGINS=https://majestic-dodol-25e71c.netlify.app` on Render. |

### 3. Failing request (inferred)

- **Likely:** Browser sends OPTIONS preflight for POST to `https://clarity-1sra.onrender.com/counterfactual/run` (or similar). If Render did not have Netlify origin in allowed origins, preflight would fail or response would lack `Access-Control-Allow-Origin`, leading to "Failed to fetch".
- **Also:** If frontend used wrong base URL (e.g. missing or wrong `VITE_API_BASE_URL` on Netlify), requests would go to wrong host or fail.

---

## Implementation Summary

- **M17_plan.md** replaced with full 5-phase plan (VITE_API_BASE_URL, `/health`, no hardcoding, getBaseUrl() refactor).
- **api.ts:** `getBaseUrl()` exported for use by CounterfactualConsole.
- **CounterfactualConsole.tsx:** Removed local `API_BASE`; import `getBaseUrl` from `../api`; all three fetch calls now use `getBaseUrl()`.

---

## Environment Checklist

### Netlify

| Variable | Value | Notes |
|----------|--------|--------|
| `VITE_API_BASE_URL` | `https://clarity-1sra.onrender.com` | No trailing slash. HTTPS. Set for production and deploy-preview. |

### Render

| Variable | Value | Notes |
|----------|--------|--------|
| `CORS_ALLOWED_ORIGINS` | `https://majestic-dodol-25e71c.netlify.app` | Comma-separated if multiple origins. |

---

## Verification (Post-Deploy)

### 1. OPTIONS preflight (terminal)

```bash
curl -s -o /dev/null -w "%{http_code}" -X OPTIONS "https://clarity-1sra.onrender.com/counterfactual/run" \
  -H "Origin: https://majestic-dodol-25e71c.netlify.app" \
  -H "Access-Control-Request-Method: POST"
```

Expected: `200`.

Check headers:

```bash
curl -sI -X OPTIONS "https://clarity-1sra.onrender.com/counterfactual/run" \
  -H "Origin: https://majestic-dodol-25e71c.netlify.app" \
  -H "Access-Control-Request-Method: POST"
```

Expected: `access-control-allow-origin: https://majestic-dodol-25e71c.netlify.app` (or equivalent).

### 2. /health

```bash
curl -s -o /dev/null -w "%{http_code}" "https://clarity-1sra.onrender.com/health"
```

Expected: `200`.

### 3. From Netlify site

- Open https://majestic-dodol-25e71c.netlify.app
- DevTools → Network
- Run counterfactual probe (load baselines, run probe)
- Confirm: no red requests, no CORS errors in console, no "Failed to fetch", POST returns 200 and JSON visible.

---

## CI

To be filled after PR and workflow run (per workflow analysis prompt).
