## M17 — Frontend ↔ Backend Connectivity Hardening

- **Unify API base URL:** CounterfactualConsole now uses `getBaseUrl()` from `api.ts` (single source of truth). Export `getBaseUrl()` from `api.ts`.
- **Netlify:** Set `VITE_API_BASE_URL=https://clarity-1sra.onrender.com` for production.
- **Render:** Set `CORS_ALLOWED_ORIGINS=https://majestic-dodol-25e71c.netlify.app` (no origin hardcoding in code).
- **Tests:** Added `/api/*` MSW handlers so default `getBaseUrl()` in tests (`/api`) is mocked; updated CounterfactualConsoleErrors tests to override `/api/*` URLs.
- **Docs:** M17_plan.md replaced with full 5-phase plan; M17_run1.md (diagnosis + env checklist + verification curl); clarity.md Deploy section documents required env.

No model/schema/metric/UI changes. Backend CORS remains env-driven.

Verification: After deploy, set env on Netlify and Render per `docs/milestones/M17/M17_run1.md`, then confirm no "Failed to fetch" from live Netlify site.

Tag after merge: `v0.0.18-m17`
