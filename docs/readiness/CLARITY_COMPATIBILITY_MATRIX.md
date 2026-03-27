# CLARITY_COMPATIBILITY_MATRIX — Supported combination truth table (Readiness)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M23 — Consumer assumptions, compatibility matrix & transfer checklist |
| **Authority** | Canonical **combination-level** truth for this repository: which **invocation × mode × output × context** combinations are **Supported**, **Unsupported**, or **Unknown** under the evidence rules below |
| **Readiness status** | **`READY FOR DOWNSTREAM ADOPTION`** (M25 — see [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md), [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)) |

---

## 1. Purpose

This document answers:

> For a given CLARITY **invocation surface**, **execution mode**, **output expectation**, and **operating context**, is the combination **Supported**, **Unsupported**, or **Unknown** today?

It uses the same honesty taxonomy as [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) but with **combination-level** status:

| Status | Meaning |
|--------|--------|
| **Supported** | Strong evidence from **frozen contracts**, **code**, and **tests** for this specific combination. |
| **Unsupported** | Contradicted by the readiness posture or explicitly out of scope for the contract (e.g. HTTP as adoption API). |
| **Unknown** | Insufficient evidence to claim **Supported**; **do not** treat as safe by default. |

**Subordinate to:** `docs/clarity.md`, frozen contracts in `docs/readiness/`, and current code/tests. This matrix **does not** widen [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) or the M20 artifact contract.

---

## 2. Interpretation rules

- **Supported** is **not** aspirational: it requires traceable evidence (see §4).
- **Unsupported** includes **non-canonical** surfaces that may still exist operationally (e.g. demo HTTP).
- **Unknown** is the **default** when evidence is thin or environment-dependent without a governed CI path for every combination.
- The **HTTP API** is **not** readiness-canonical for adoption (see [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §3).
- **Orchestrator-only** output does **not** satisfy **full analytical bundle** expectations (see [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) §3 and [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §8.2).

---

## 3. Axes of combination

| Axis | Values used in §4 |
|------|-------------------|
| **Invocation surface** | **A** — `app.clarity.public_surface` (canonical). **B** — `app.clarity` package root (non–`public_surface`). **C** — HTTP API / FastAPI routes. |
| **Execution mode** | **Canonical** — documented sweep + fake/synthetic R2L as in CI tests. **Rich** — `CLARITY_RICH_MODE` truthy. **Real model** — `CLARITY_REAL_MODEL` where applicable. |
| **Output expectation** | **Orchestrator-only** — `clarity/sweep_manifest.json` with `manifest_schema_family: clarity_sweep_orchestrator_v1`. **Full bundle** — three required JSON files per artifact contract §3 (rich aggregate uses `clarity_rich_aggregate_v1`). **Presentation** — PDFs / plots (presentation-only). |
| **Operating context** | **Local dev / CI** — tests and scripts in-repo. **Readiness contract** — consumer path via `public_surface` + contracts. **Demo / cloud** — deployment described in `docs/clarity.md`; no GPU in cloud demo. |

---

## 4. Supported combinations table

| ID | Invocation surface | Mode | Output expectation | Context | Status | Evidence | Limitations / notes | Owner doc(s) |
|----|------------------|------|-------------------|---------|--------|----------|----------------------|--------------|
| C-001 | A (`app.clarity.public_surface`) | Canonical | Orchestrator-only | Local dev / CI | **Supported** | `test_public_surface_contract.py::test_sanctioned_consumer_sweep_smoke`; `test_sweep_orchestrator.py` (e.g. `test_manifest_created`, `test_full_sweep_with_fake_r2l`) | Produces orchestrator `sweep_manifest.json` only; not full bundle. | `CLARITY_PUBLIC_SURFACE.md` §8; `CLARITY_ARTIFACT_CONTRACT.md` §3 |
| C-002 | A | Canonical | Orchestrator-only | Readiness contract | **Supported** | Same as C-001; frozen symbols in `public_surface.py` | Consumer must not import non-`public_surface` modules for contract. | `CLARITY_PUBLIC_SURFACE.md` |
| C-003 | A | Canonical | Full bundle (three JSON files) | Local dev / CI (documented producer path) | **Supported** | `backend/tests/fixtures/baselines/m15_real_ui/`; `test_artifact_contract.py`; `CLARITY_ARTIFACT_CONTRACT.md` §3 | Requires **materialization** beyond orchestrator alone (e.g. metrics/surface pipelines or validation scripts per artifact contract). | `CLARITY_ARTIFACT_CONTRACT.md` | 
| C-004 | A | Canonical | Full bundle | Readiness contract | **Supported** | Same evidence as C-003 for **shape**; consumer must run a producer path that emits all three artifacts | Do not assume full bundle from sweep execute alone. | `CLARITY_PUBLIC_SURFACE.md` §8.2 |
| C-005 | A | Rich + real model (env-gated) | Rich artifacts optional | Local / GPU evidence paths | **Unknown** | `test_rich_generation_unit.py`, `test_rich_mode_determinism.py`, `test_real_adapter_determinism.py` prove **pieces**; not every cross-product is CI-governed | Treat as **Unknown** unless you replicate a documented script path and validate artifacts. | `CLARITY_BOUNDARY_CONTRACT.md` §7 |
| C-006 | B (`app.clarity` import not via `public_surface`) | Any | Any | Any | **Unsupported** | `CLARITY_PUBLIC_SURFACE.md` §3–5; M21 freeze | Package root breadth is **not** the portability contract. | `CLARITY_PUBLIC_SURFACE.md` |
| C-007 | C (HTTP / FastAPI) | Any | Any | Demo / operational | **Unsupported** | `CLARITY_PUBLIC_SURFACE.md` §3 (HTTP **non-canonical** for readiness); `test_demo_router.py` (operational tests only) | **Do not** adopt route shapes as stable external API. | `CLARITY_PUBLIC_SURFACE.md` |
| C-008 | A | Canonical | Presentation-only (PDF/PNG) | CI / report pipeline | **Supported** | `test_report_determinism.py`; `CLARITY_ARTIFACT_CONTRACT.md` §5 | Presentation-only; not bundle identity. | `CLARITY_ARTIFACT_CONTRACT.md` §5 |
| C-009 | A | Canonical | Orchestrator-only | Demo / cloud | **Unknown** | No readiness evidence that cloud demo runs full `R2LRunner` + `SweepOrchestrator` with consumer config | Demo uses synthetic/precomputed artifacts per `docs/clarity.md`; not a substitute for local validation. | `docs/clarity.md` — M10.5 / demo notes |
| C-010 | A | Rich | Orchestrator-only | Local dev / CI | **Unknown** | Rich mode affects downstream pipelines; manifests are self-identifying via `manifest_schema_family` (see artifact contract §6.1) | **Unknown** reflects mode/product interaction, not manual producer-family guessing. | `CLARITY_ARTIFACT_CONTRACT.md` §6.1 |
| C-011 | A | Canonical | Full bundle | Demo / cloud | **Unknown** | No governed CI path for full bundle in cloud | Same as C-009. | `docs/clarity.md` |
| C-012 | Internal modules (not `public_surface`) | Canonical | Full bundle | Local dev | **Unknown** | `CLARITY_IMPLEMENTATION_STATUS.md` — metrics/surface **implemented** in code, but **not** a sanctioned consumer import path | Use **public_surface** entrypoints for adoption; internal imports are **Unsupported** for portability. | `CLARITY_PUBLIC_SURFACE.md` §5 |

---

## 5. Narrative summary

**What a downstream consumer should do**

- Integrate via **`app.clarity.public_surface`**, read [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) and [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md), and treat **C-001 / C-002** as the **Supported** minimal orchestrator path.
- If you need the **full analytical bundle**, plan for **C-003 / C-004** and the **explicit** producer steps (not orchestrator alone).

**What they must not rely on**

- **HTTP** as the readiness-stable adoption surface (**C-007**).
- **Package-root** imports as portability (**C-006**).
- **Orchestrator-only** runs as automatically satisfying **full-bundle** semantics (**C-001** vs **C-003**).

**What remains unresolved (post–M25)**

- **Rich / real-model / GPU** combinations without a single CI-governed matrix for every consumer environment (**C-005**, **C-010**).
- **Demo / cloud** vs **local** full-bundle evidence (**C-009**, **C-011**).

---

## 6. Known gaps

| Gap | Why it matters |
|-----|----------------|
| Cross-product **rich × real × full bundle** not fully enumerated in CI | **Unknown** rows remain. |
| Single JSON Schema file for all `sweep_manifest.json` shapes | **Deferred** per artifact contract §6.4; `manifest_schema_family` disambiguates producers. |
| Semver / cross-repo version matrix | **Planned** for governance; not claimed in M23. |

---

## 7. Related documents

- [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md) — Assumption list.  
- [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) — Adoption checklist.  
- [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md) — Operator flow.  
- [`docs/milestones/M23/M23_inventory.md`](../milestones/M23/M23_inventory.md) — Milestone inventory bridge.
