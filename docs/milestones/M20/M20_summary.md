# Milestone Summary — M20: Artifact Contract & Deterministic Output Freeze

**Project:** CLARITY  
**Phase:** Readiness (M18–M24)  
**Milestone:** M20 — Artifact Contract & Deterministic Output Freeze  
**Timeframe:** 2026-03-26  
**Status:** Closed  

---

## 1. Milestone objective

Freeze CLARITY’s **consumer-meaningful output surface**: artifact inventory, required vs optional files, canonical vs presentation-only outputs, deterministic ordering, numeric serialization rules, and contract identity — **grounded in implemented code and fixtures**, with **test-backed** evidence — without claiming final downstream portability.

---

## 2. What artifact truth was frozen

### Required core JSON (full analytical bundle)

For the **rich validation / full-metrics bundle** class (evidenced by `m15_real_ui` fixtures and `m15_real_ui_sweep.py`):

- `sweep_manifest.json`
- `robustness_surface.json`
- `monte_carlo_stats.json`

### Optional / mode-dependent

- `confidence_surface.json`, `entropy_surface.json` (rich path)
- `summary_hash.txt` (M15 workflow)
- Report PDFs, visualization assets — **not** required for core contract identity

### Canonical vs presentation-only

- **Contract-relevant:** the three required JSON files (and optional rich surface JSON when produced).
- **Presentation-only / derived:** report PDFs and similar visualization exports — **do not** define run identity (RD-011).

### Deterministic rules frozen

- **Ordering:** `RobustnessSurface` axis alphabetical; point values lexicographic; JSON `sort_keys` where documented; Monte Carlo `seeds` sorted in fixture checks.
- **Floats:** `_round8` / `round(..., 8)` for **surface-engine** storage path; other JSON floats follow **Python `json` default** unless explicitly rounded (RD-013).
- **Identity:** **Semantic JSON equality** as baseline contract; **committed SHA256** + **round-trip** serialization for `m15_real_ui` JSON as **evidence**, not a claim that every writer is byte-identical (RD-012).

### Multiple `sweep_manifest.json` shapes

- **Orchestrator** manifest (`axes` / `seeds` / `runs`) vs **rich aggregate** manifest (e.g. M15) — both documented; consumers must not assume one schema for all files (ledger risk R-003).

---

## 3. Tests added or hardened

| Deliverable | Evidence |
|-------------|----------|
| New module | `backend/tests/test_artifact_contract.py` — completeness, SHA256, round-trip JSON, ordering, structure keys, `_round8` rule, PDF exclusion from required bundle |
| Pack guardrail | `backend/tests/test_readiness_pack.py` — includes `CLARITY_ARTIFACT_CONTRACT.md` |

---

## 4. `docs/clarity.md` updates (summary)

- Milestone table: **M20** closed, score 5.0, **not tagged**.
- Readiness pack index: **artifact contract** link.
- **M20 note:** artifact contract frozen; **M21** still owns public invocation surface.
- **Current milestone:** M20; **Previous:** M19 (full deliverables listed).
- **Baseline table:** M20 row added (commit pending merge policy).

---

## 5. Readiness status

**`NOT READY`** — unchanged by design. M20 freezes artifact truth; **M21+** still required for public surface, manual, consumer kit, and **M24** verdict.

---

## 6. Deferred to M21

- **`CLARITY_PUBLIC_SURFACE.md`** — official consumer invocation path; public vs internal modules.
- Snapshot/freeze tests for public API per readiness plan.

---

## 7. Score

**5.0** — Align with `M20_audit.md`.
