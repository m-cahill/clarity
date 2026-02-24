# M17 Tool Calls Log

## Milestone: M17 — Frontend ↔ Backend Connectivity Hardening

---

| # | Timestamp | Tool | Purpose | Files / Target | Status |
|---|-----------|------|---------|----------------|--------|
| 1 | 2026-02-24 | read_file | Read .cursorrules, clarity.md, VISION.md, M16 audit/summary, M17 plan/toolcalls | docs, .cursorrules | done |
| 2 | 2026-02-24 | grep | Locate /status, /health; API env vars; CORS usage | backend, frontend | done |
| 3 | 2026-02-24 | read_file | api.ts getBaseUrl; main.py CORS; CounterfactualConsole API_BASE usage | frontend/src, backend/app | done |
| 4 | 2026-02-24 | write | Replace M17_plan.md with full 5-phase plan | docs/milestones/M17/M17_plan.md | done |
| 5 | 2026-02-24 | search_replace | Export getBaseUrl from api.ts | frontend/src/api.ts | done |
| 6 | 2026-02-24 | search_replace | CounterfactualConsole: import getBaseUrl, remove API_BASE, use getBaseUrl() in fetches | frontend/src/pages/CounterfactualConsole.tsx | done |
| 7 | 2026-02-24 | write | M17_run1.md — Phase 1 diagnosis, env checklist, verification curl | docs/milestones/M17/M17_run1.md | done |
| 8 | 2026-02-24 | search_replace | Update M17_toolcalls.md header and log entries | docs/milestones/M17/M17_toolcalls.md | done |
| 9 | 2026-02-24 | search_replace | Add /api/* MSW handlers for getBaseUrl() default in tests | frontend/src/mocks/handlers.ts | done |
| 10 | 2026-02-24 | search_replace | CounterfactualConsoleErrors: override /api/* URLs in server.use | frontend/tests/CounterfactualConsoleErrors.test.tsx | done |
| 11 | 2026-02-24 | run | Frontend tests (vitest run) | frontend | 137 passed |
| 12 | 2026-02-24 | run | Backend tests (pytest) | backend | 911 passed |
| 13 | 2026-02-24 | run | git checkout -b m17-connectivity-hardening, commit, push | repo | done |
| 14 | 2026-02-24 | run | gh pr create | PR #19 | done |
