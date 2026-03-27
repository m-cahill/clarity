# Milestone Summary — M21: Public Surface & Invocation Contract

**Project:** CLARITY  
**Phase:** Readiness (M18–M24)  
**Milestone:** M21 — Public Surface & Invocation Contract  
**Timeframe:** 2026-03-26  
**Status:** Closed  

---

## 1. Milestone objective

Freeze a **single official consumer-facing Python surface** (`app.clarity.public_surface`), separate **public vs internal**, document configuration and failure semantics, and add **dedicated** public-surface guardrail tests (distinct from M20 artifact tests).

---

## 2. What was frozen

| Item | Detail |
|------|--------|
| **Canonical surface** | `app.clarity.public_surface` — 14 symbols (`R2LRunner`, `SweepOrchestrator`, sweep models/errors/helpers). |
| **Non-canonical** | HTTP API (demo), broad `app.clarity` package `__all__`, operational scripts. |
| **Versioning** | No semver; breaking changes require readiness decision + milestone + test updates (RD-014). |
| **Rich-mode env** | Documented CLARITY-side names only: `CLARITY_RICH_MODE`, `CLARITY_REAL_MODEL`, `CLARITY_RICH_LOGITS_HASH` (optional). |

---

## 3. Tests

| Deliverable | Evidence |
|-------------|----------|
| New module | `backend/tests/test_public_surface_contract.py` — smoke, export snapshot, sanctioned consumer sweep with `fake_r2l` |
| Pack guardrail | `backend/tests/test_readiness_pack.py` — includes `CLARITY_PUBLIC_SURFACE.md` |

---

## 4. `docs/clarity.md` updates (summary)

- Milestone table: **M21** closed, score 5.0, **not tagged**.
- Pack index: **public surface** link.
- **Current milestone:** M21; **Previous:** M20 (full deliverables listed).

---

## 5. Readiness status

**`NOT READY`** — unchanged. M21 closes the **public invocation** contract layer; operating manual (**M22**), consumer kit (**M23**), and **M24** verdict remain.

---

## 6. Deferred

- HTTP route freeze (explicitly out of M21).
- Semver / artifact version field (still deferred per M20).

---

## 7. Score

**5.0** — Align with `M21_audit.md`.
