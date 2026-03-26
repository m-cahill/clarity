# Milestone Summary — M19: Consumer Boundary Freeze

**Project:** CLARITY  
**Phase:** Readiness (M18–M24)  
**Milestone:** M19 — Consumer Boundary Freeze  
**Timeframe:** 2026-03-26  
**Status:** Closed  

---

## 1. Milestone objective

Freeze the CLARITY↔R2L relationship as a **readiness contract**: consumer-only identity, black-box invocation as the default sanctioned surface, allowed substrate inputs, CLARITY-owned outputs and `clarity/` namespace rules, canonical vs optional rich-mode behavior at the boundary, seed-enumeration semantics, and forbidden behaviors—**grounded in implemented code and tests**, without claiming final downstream portability.

---

## 2. Scope boundaries

### In scope

- `docs/readiness/CLARITY_BOUNDARY_CONTRACT.md` — canonical readiness-pack boundary contract (supersedes **readiness authority** over legacy one-page architecture notes; does not silently erase `CLARITY_ARCHITECHTURE_CONTRACT.MD` as historical input).
- `docs/readiness/CLARITY_ASSUMED_GUARANTEES.md` — inherited substrate assumptions vs CLARITY-owned responsibilities.
- Updates to `READINESS_LEDGER.md`, `README.md`, `READINESS_DECISIONS.md` (RD-008–RD-010), `docs/clarity.md`.
- Tests: extended `backend/tests/test_boundary_contract.py` (M19 section); `backend/tests/test_readiness_pack.py` (required file list).
- `M20_plan.md` / `M20_toolcalls.md` seeded only.

### Out of scope

- Full artifact contract (M20), public surface (M21), operating manual / matrix / checklist (M22–M23), final verdict (M24).
- R2L semantic or schema changes; repairing `CLARITY_ARCHITECHTURE_CONTRACT.MD` unless required for truthful citation.
- Opportunistic M16 baseline commit cleanup in `docs/clarity.md`.

---

## 3. Deliverables completed

| Deliverable | Evidence |
|-------------|----------|
| Boundary contract | `docs/readiness/CLARITY_BOUNDARY_CONTRACT.md` |
| Assumed guarantees | `docs/readiness/CLARITY_ASSUMED_GUARANTEES.md` |
| Ledger / pack | `READINESS_LEDGER.md` (as-of M19, M19 closed, evidence map), `README.md` reading order |
| ADRs | RD-008 (pack canonical boundary), RD-009 (black-box default until M21), RD-010 (`CLARITY_RICH_MODE` canonical in this repo) |
| Canonical ledger | `docs/clarity.md` — M19 closed, pack index, current/previous milestone sections, baseline row M19 |
| Tests | `test_boundary_contract.py` (loader + canonical/rich invariants + env constant); `test_readiness_pack.py` |
| M20 seed | `docs/milestones/M20/M20_plan.md`, `M20_toolcalls.md` |

---

## 4. What was frozen

### Boundary contract

- CLARITY remains a **consumer**; R2L invoked via **CLI/subprocess** (`R2LRunner`); no internal R2L imports (existing AST guardrails).
- **Minimal** consumed artifacts after a run: `manifest.json` + `trace_pack.jsonl` (aligned with runner checks); loader validates required manifest fields; trace lines may omit rich optional fields.
- **Outputs** under `clarity/` only (`validate_output_path`).
- **Rich mode:** `CLARITY_RICH_MODE` is the CLARITY-side canonical switch name; real rich paths also require `CLARITY_REAL_MODEL` per code; `R2L_RICH_MODE` in older context docs is **not** the implemented CLARITY switch.
- **Deferred:** full artifact contract, public API, M24 verdict—explicitly listed in the contract.

### Assumed guarantees

- **Inherited:** high-level substrate assumptions (determinism, schema posture, adapter contract, reliance on upstream CI) as **assumptions**, not re-proven here.
- **Owned:** perturbation, sweep orchestration, metrics, serialization, namespace, boundary tests, rich ingestion when enabled without hard dependency on optional fields on canonical paths.

### Guardrails added or hardened

- New **M19** test class: `load_manifest` / `load_trace_pack` on fixtures; canonical vs rich trace fixtures; `SweepManifest.rich_mode` does not relax namespace rules; `RICH_MODE_ENV_VAR == "CLARITY_RICH_MODE"`.
- Readiness pack **required files** extended to include the two new markdown documents.

---

## 5. `docs/clarity.md` updates (summary)

- Milestone table: **M19** closed, score 5.0, **not tagged**.
- Readiness pack index: boundary + assumed-guarantees links; M19 note under readiness phase.
- **Current milestone:** M19; **Previous:** M18 (with deliverables listed).
- **Key documents:** links to new readiness contracts.
- **Baseline table:** M19 row added (commit to be recorded at merge if policy requires).

---

## 6. Verification

- `pytest backend/tests/test_readiness_pack.py backend/tests/test_boundary_contract.py` — pass  
- Full backend suite — **922 passed**, 31 skipped (GPU/env-gated), local run  

---

## 7. Readiness status

**`NOT READY`** — unchanged by design. M19 freezes boundary truth and assumptions; it does **not** establish final portability.

---

## 8. Deferred to M20

- `CLARITY_ARTIFACT_CONTRACT.md` and deterministic output / golden tests per readiness plan.

---

## 9. Score

**5.0** — Align with `M19_audit.md`.
