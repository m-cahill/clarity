# CLARITY_CONSUMER_ASSUMPTIONS — Downstream assumptions (Readiness)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M23 — Consumer assumptions, compatibility matrix & transfer checklist |
| **Authority** | Readiness-pack document: **what a consumer project may treat as proven** after M19–M22, **without** widening the M21 public surface or M21/M20 contracts |
| **Readiness status** | Project readiness remains **`NOT READY`** until M24 verdict (see [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)) |

---

## 1. Purpose

This document lists **explicit assumptions** a downstream repository may make when integrating CLARITY **after** the frozen boundary (M19), artifact (M20), public surface (M21), and operating manual / implementation matrix (M22) delivered.

It is **subordinate** to:

1. [`docs/clarity.md`](../clarity.md) — project ledger  
2. Frozen contracts in `docs/readiness/` — especially [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md), [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md), [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md)  
3. Executable code and tests  

**“Assumption” here means:** CLARITY maintains these behaviors unless a future readiness decision and milestone say otherwise. It does **not** mean “every combination of modes and outputs is supported.” For **combination-level** truth, see [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md).

---

## 2. Interpretation rules

- **Supported combination claims** are **evidence-bound** in the compatibility matrix, not implied by this list alone.
- **Do not** widen **`app.clarity.public_surface`** based on this document.
- **Do not** treat the **HTTP API** as the readiness-canonical invocation surface (see [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §3).
- **Do not** assume **orchestrator-only** runs produce the **full analytical bundle** (`sweep_manifest.json` + `robustness_surface.json` + `monte_carlo_stats.json`) without the additional materialization steps described in the artifact contract and matrix.

---

## 3. Assumptions you may make (after M19–M22)

| ID | Assumption | Grounding |
|----|------------|-----------|
| A-01 | CLARITY **consumes** R2L via **black-box** subprocess invocation and declared artifacts; it does **not** modify R2L execution semantics in the substrate. | [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) §2–4 |
| A-02 | CLARITY-owned writes stay under the **`clarity/`** namespace; path validation rejects writes outside it. | Boundary contract §6; `test_boundary_contract.py` |
| A-03 | The **canonical Python consumer surface** for readiness is **`app.clarity.public_surface`** symbol set aligned with `PUBLIC_SURFACE_SYMBOLS` / `__all__`. | [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md); `test_public_surface_contract.py` |
| A-04 | **R2LRunner** requires **`manifest.json`** and **`trace_pack.jsonl`** after a successful run, per `artifact_loader` validation. | Boundary contract §5; `test_r2l_runner.py` |
| A-05 | **SweepOrchestrator** persists **`clarity/sweep_manifest.json`** under the sweep output tree (orchestrator schema family). | [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) §3, §6.1; `test_sweep_orchestrator.py` |
| A-06 | **Artifact contract** defines required vs optional files, two `sweep_manifest.json` schema families, and deterministic JSON rules where documented. | [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md); `test_artifact_contract.py` |
| A-07 | **Inherited** substrate assumptions (determinism, schema intent, adapter shape) vs **CLARITY-owned** responsibilities are split per [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md). | M19 |
| A-08 | **No semver** is claimed for the public surface; breaking changes require governance + tests. | [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §10 |

---

## 4. What you must still validate locally

| Topic | Why |
|-------|-----|
| **R2L CLI / substrate version** | CLARITY inherits substrate behavior; pin versions and reproduce manifests as your project requires. |
| **GPU / real-model / rich paths** | Environment-specific; not all CI jobs exercise every combination. See matrix for **Supported / Unknown** rows. |
| **Full analytical bundle** end-to-end | Confirm your pipeline runs the **documented** producer path (fixtures + scripts in-repo are evidence), not “orchestrator only.” |
| **Downstream packaging** | Install layout, container, and networking are **consumer** responsibilities unless/until a future milestone freezes them. |

---

## 5. What invalidates or weakens these assumptions

| Change | Effect |
|--------|--------|
| Modifying **frozen** `docs/readiness/*` contracts without a recorded readiness decision | May invalidate adoption claims; re-read pack + [`READINESS_DECISIONS.md`](./READINESS_DECISIONS.md). |
| Depending on **`app.clarity`** modules outside **`public_surface`** | **Unsupported** for portability per M21; assumptions may not apply. |
| Treating **HTTP routes** as a stable external API | **Not** the M21 contract; breaking changes are not governed as readiness. |
| Assuming **one** `sweep_manifest.json` schema everywhere | **Invalid** — two families documented; see artifact contract §6.1. |

---

## 6. Review / re-readiness triggers

Re-run the readiness pack review and [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) when:

- you upgrade R2L, adapters, or CLARITY major integration points;
- you change sweep producers or add new artifact writers;
- you depend on **rich** or **real-model** combinations for production (see matrix **Unknown** rows); or
- readiness documents or `PUBLIC_SURFACE_SYMBOLS` change in a **contract-affecting** way (M24 change control will formalize further).

---

## 7. Related documents

- [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) — **Supported / Unsupported / Unknown** combinations (truth table).  
- [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) — Adoption checklist.  
- [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md) — Operator flow.  
- [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) — Implemented / Planned / Unknown surfaces.
