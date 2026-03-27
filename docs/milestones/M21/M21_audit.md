# Milestone Audit — M21: Public Surface & Invocation Contract

**Audit mode:** DELTA AUDIT (readiness governance + public surface freeze)  
**Date:** 2026-03-26  
**Scope:** `CLARITY_PUBLIC_SURFACE.md`, `public_surface.py`, ledger/pack/boundary updates, public-surface tests  

---

## 1. Verdict

**M21 scope satisfied.** One **canonical** Python module defines the consumer contract; HTTP API is **explicitly non-canonical**; tests are **separate** from `test_artifact_contract.py`. **Readiness remains `NOT READY`.**

**Regression risk:** Low (additive module + docs + focused tests; `app.clarity.__init__` gains `public_surface` submodule import).

---

## 2. Readiness-plan alignment

| Readiness-plan expectation (M21) | Met? |
|-----------------------------------|------|
| `CLARITY_PUBLIC_SURFACE.md` with required topics | Yes |
| Single official invocation path documented | Yes — `app.clarity.public_surface` |
| Public vs internal explicit | Yes |
| Smoke + consumer + export freeze tests | Yes (no CLI — correctly skipped) |
| `READINESS_LEDGER.md` + `docs/clarity.md` updated | Yes |
| `NOT READY` preserved | Yes |

---

## 3. Boundary with M20

- Artifact contract tests unchanged in purpose; public-surface tests live in **`test_public_surface_contract.py`** only.
- Orchestrator-only output honesty preserved in `CLARITY_PUBLIC_SURFACE.md` §8 (cross-ref to artifact contract).

---

## 4. Issues

| Severity | Finding | Action |
|----------|-----------|--------|
| None blocking | — | — |

---

## 5. Score

**5.0** — Meets exit criteria; no semver overclaim; HTTP correctly excluded from canonical surface.

---

## 6. Audit posture for M22

- Operating manual must **reference** `CLARITY_PUBLIC_SURFACE.md` and not contradict the frozen module list.
- Implementation matrix should list **public surface** as **Implemented** with owner doc `CLARITY_PUBLIC_SURFACE.md`.
