# M12 Tool Calls Log

## Purpose
Track all tool invocations during M12 implementation.

---

| Timestamp | Tool | Purpose | Files/Target | Status |
|-----------|------|---------|--------------|--------|
| 2026-02-21 | read_file | Read clarity.md, M10.5 audit/summary, M11 audit/summary | docs/clarity.md, M10_5, M11 | ✅ Complete |
| 2026-02-21 | list_dir | Explore project structure | backend/app, frontend/src, milestones | ✅ Complete |
| 2026-02-21 | read_file | Read vite.config.ts, requirements.txt, ci.yml | frontend/vite.config.ts, backend/requirements.txt, ci.yml | ✅ Complete |
| 2026-02-21 | write | Populate M12_plan.md with full milestone plan | docs/milestones/M12/M12_plan.md | ✅ Complete |
| 2026-02-21 | — | Received locked answers for Q1-Q7 + additional guardrails | — | ✅ Confirmed |
| 2026-02-21 | git | Create branch m12-operational-hardening | — | ✅ Complete |
| 2026-02-21 | write | Create downloadUtils.ts with DI helper | frontend/src/utils/downloadUtils.ts | ✅ Complete |
| 2026-02-21 | edit | Refactor CounterfactualConsole to use downloadUtils | frontend/src/pages/CounterfactualConsole.tsx | ✅ Complete |
| 2026-02-21 | write | Create downloadUtils unit tests | frontend/tests/downloadUtils.test.ts | ✅ Complete |
| 2026-02-21 | edit | Add api.ts error handling tests | frontend/tests/api.test.ts | ✅ Complete |
| 2026-02-21 | edit | Add delta styling coverage test | frontend/tests/CounterfactualConsole.test.tsx | ✅ Complete |
| 2026-02-21 | edit | Add mock data for zero/positive deltas | frontend/src/mocks/handlers.ts | ✅ Complete |
| 2026-02-21 | edit | Restore branch coverage threshold to 85% | frontend/vite.config.ts | ✅ Complete |
| 2026-02-21 | write | Create E2E report smoke test | frontend/e2e/report.spec.ts | ✅ Complete |
| 2026-02-21 | mkdir | Create cache module directory | backend/app/clarity/cache/ | ✅ Complete |
| 2026-02-21 | write | Create cache module __init__.py | backend/app/clarity/cache/__init__.py | ✅ Complete |
| 2026-02-21 | write | Create cache_key.py | backend/app/clarity/cache/cache_key.py | ✅ Complete |
| 2026-02-21 | write | Create cache_manager.py | backend/app/clarity/cache/cache_manager.py | ✅ Complete |
| 2026-02-21 | write | Create test_cache.py (52 tests) | backend/tests/test_cache.py | ✅ Complete |
| 2026-02-21 | edit | Integrate caching into report_router.py | backend/app/clarity/report/report_router.py | ✅ Complete |
| 2026-02-21 | edit | Add caching and concurrency tests | backend/tests/test_report_router.py | ✅ Complete |
| 2026-02-21 | write | Create requirements.in | backend/requirements.in | ✅ Complete |
| 2026-02-21 | run | Generate requirements.lock with pip-compile | backend/requirements.lock | ✅ Complete |
| 2026-02-21 | edit | Add pip-tools/pip-audit to dev deps | backend/pyproject.toml | ✅ Complete |
| 2026-02-21 | edit | Add .clarity_cache/ to gitignore | .gitignore | ✅ Complete |
| 2026-02-21 | edit | Add security and lockfile CI jobs | .github/workflows/ci.yml | ✅ Complete |
| 2026-02-21 | edit | Implement CORS tightening | backend/app/main.py | ✅ Complete |
| 2026-02-21 | edit | Fix demo_artifacts checksums | demo_artifacts/case_001/checksums.json | ✅ Complete |
| 2026-02-21 | test | Run backend tests (875 pass) | backend/tests/ | ✅ Complete |
| 2026-02-21 | test | Run frontend tests (137 pass, 87.39% branch) | frontend/tests/ | ✅ Complete |
| 2026-02-21 | git | Push branch m12-operational-hardening | — | ✅ Complete |
| 2026-02-21 | gh | Create PR #15 | — | ✅ Complete |
| 2026-02-21 | gh | Watch CI run | — | ⏳ In Progress |
| 2026-02-21 | edit | Fix pip-audit CI to use --disable-pip | .github/workflows/ci.yml | ✅ Complete |
| 2026-02-21 | edit | Fix checksums.json with git blob hashes | demo_artifacts/case_001/checksums.json | ✅ Complete |
| 2026-02-21 | edit | Fix TypeScript: use globalThis instead of global | frontend/tests/api.test.ts | ✅ Complete |
| 2026-02-21 | git | Push all fixes | m12-operational-hardening | ✅ Complete |
| 2026-02-21 | gh | Verify CI green (all 8 jobs passed) | CI run 22251129342 | ✅ Complete |
| 2026-02-21 | write | Create M12_run1.md analysis | docs/milestones/M12/M12_run1.md | ✅ Complete |

