# M21 — Public Surface & Invocation Contract

**Status:** Executed — see `M21_summary.md` / `M21_audit.md`.

**Phase:** Readiness (M18–M24)

## Objective

Freeze **one** official consumer-facing invocation path for CLARITY, define **public vs internal**, document required/optional configuration and failure semantics, and back the surface with smoke/freeze tests.

## Canonical outcome (M21)

- **Canonical public surface:** `app.clarity.public_surface` (thin re-exports: `R2LRunner`, `SweepOrchestrator`, sweep config/types, errors).
- **Non-canonical:** HTTP API (demo/operational), broad `app.clarity` root exports, scripts — see `docs/readiness/CLARITY_PUBLIC_SURFACE.md`.
- **CLI:** No CLARITY setuptools CLI added; no CLI help tests (none exists).

## Non-goals

Per readiness plan: no new model features, no MedGemma/UI redesign, no CI weakening, no R2L semantics changes, no downstream-specific integration, no speculative interfaces.

## Deliverables

- `docs/readiness/CLARITY_PUBLIC_SURFACE.md`
- `backend/app/clarity/public_surface.py`
- `backend/tests/test_public_surface_contract.py`
- Updates: `READINESS_LEDGER.md`, `README.md` (pack), `READINESS_DECISIONS.md` (RD-014), `CLARITY_BOUNDARY_CONTRACT.md`, `docs/clarity.md`, `test_readiness_pack.py`

## Source of truth

Full program: `docs/readiness/readinessplan.md` — M21 section.
