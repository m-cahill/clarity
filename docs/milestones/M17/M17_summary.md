# M17 Summary — Frontend ↔ Backend Connectivity Hardening

## Milestone Overview

| Field | Value |
|-------|-------|
| **Milestone** | M17 |
| **Tag** | `v0.0.18-m17` |
| **Mode** | DELTA — Deployment Integrity Only |
| **Date** | 2026-02-24 |
| **Status** | ✅ Closed |

---

## What M17 Did

M17 fixed the Netlify production "Failed to fetch" issue so the live demo is fully interactive.

- **No model, metric, or schema changes.** Only deployment-layer and frontend API base URL resolution.
- **Single source of truth:** All API calls use `getBaseUrl()` from `api.ts`; CounterfactualConsole no longer uses a local `API_BASE` or `VITE_API_URL`-only path.
- **Canonical env:** `VITE_API_BASE_URL` is the production variable; `VITE_API_URL` is legacy/E2E only and documented as such.
- **CORS:** Backend already env-driven; Render `CORS_ALLOWED_ORIGINS` for Netlify origin verified; OPTIONS and POST return 200 from live Netlify → Render.

---

## Deliverables

| Deliverable | Status |
|-------------|--------|
| getBaseUrl() preferred; no localhost in app code | ✅ |
| CounterfactualConsole uses getBaseUrl() only | ✅ |
| netlify.toml / clarity.md env documented | ✅ |
| Backend CORS env-only; OPTIONS 200 | ✅ |
| Live validation: request URL, OPTIONS, POST, probe, console | ✅ |
| M17_plan.md, M17_run1.md, M17_audit.md, M17_summary.md | ✅ |

---

## Post-M17 State

- **Kaggle submission:** Unchanged; M16 artifacts frozen.
- **Demo:** Netlify frontend → Render backend; no "Failed to fetch"; counterfactual probe runs end-to-end.
- **Optional later:** Remove `VITE_API_URL` from Netlify and rely only on `VITE_API_BASE_URL` after confirming stability.

---

## Governance Alignment

Single capability (deployment connectivity); end-to-end verified; audit defensible; no opportunistic expansion.
