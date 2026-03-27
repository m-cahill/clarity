# CLARITY Operating Manual (Readiness)

**Clinical Localization and Reasoning Integrity Testing**

This document is intended to be sufficient for an AI agent (or a human operator) to **run and reason about CLARITY correctly** when used alongside the **frozen readiness contracts** in `docs/readiness/`. When ambiguity exists, prefer **deterministic, contract-aligned** interpretations over repository folklore.

---

## Design philosophy (quick reference)

- Determinism over convenience  
- Contracts over assumptions  
- Frozen readiness docs over loose repo intuition  
- Code and tests over aspirational narrative for **current behavior**  
- Artifacts over undocumented in-memory state  

---

## 0. Purpose and AI-agent instructions

### What this manual is

This is the **runtime and integration operating manual** for CLARITY as a **bounded evaluation instrument** layered above R2L. It covers:

- What CLARITY is and is not  
- The **implemented** consumer path and pipeline  
- **Public** vs **internal** / **demo** surfaces  
- Artifact flow, determinism, and boundary rules  
- Debugging and extension discipline **without** widening the frozen public API  

### Interpretation rules

1. **Determinism over convenience** — prefer interpretations that preserve reproducibility and documented serialization behavior.  
2. **Contracts over assumptions** — do not rely on behavior that is not documented in the readiness pack or demonstrated in code/tests.  
3. **Frozen readiness docs over intuition** — `docs/readiness/` contracts (M19–M21) govern portability claims; older architecture-only docs are **input**, not authority.  
4. **Code/tests win on implementation details** — if this manual conflicts with running code, treat that as **documentation drift** to be fixed (see §0.4).  
5. **Do not widen the public API** — consumers use **`app.clarity.public_surface` only** for the sanctioned Python surface (see [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) and §5).  

### Authority hierarchy (conflict resolution)

| If this manual conflicts with… | Then… |
|--------------------------------|--------|
| [`docs/clarity.md`](../clarity.md) on **milestone status, governance, or ledger facts** | **`docs/clarity.md` wins** |
| **Frozen readiness contracts** (`CLARITY_BOUNDARY_CONTRACT.md`, `CLARITY_ASSUMED_GUARANTEES.md`, `CLARITY_ARTIFACT_CONTRACT.md`, `CLARITY_PUBLIC_SURFACE.md`) on **boundary, artifacts, or public surface** | **The frozen contract wins** |
| **Actual code behavior** on an implementation detail | **Code wins**; the manual must be corrected, not the reverse |

### Honesty markers used in this document

- **Implemented** — present in code and covered by tests and/or frozen contract text.  
- **Planned** — explicitly on the readiness roadmap (e.g. M23–M24) or project ledger, not yet delivered as a governed artifact.  
- **Unknown** — insufficient evidence in-repo; do not guess.  

---

## 1. What CLARITY is

CLARITY is a **deterministic evaluation instrument** that measures robustness and evidence stability of multimodal clinical AI systems under **structured perturbation sweeps**. In this repository it is implemented as:

- A **pure consumer of R2L** — it invokes R2L via a **black-box** subprocess (CLI) and reads **file artifacts** from an output directory.  
- An **orchestration and analysis layer** — sweeps, metrics, robustness surfaces, optional gradient/stability analysis, counterfactual probing, reporting, and UI are **owned by CLARITY** subject to the consumer boundary.  
- **Layered above** R2L in the governance stack described in [`docs/clarity.md`](../clarity.md); it does **not** redefine R2L single-run semantics.  

---

## 2. What CLARITY is not

CLARITY is **not**:

- An **execution substrate** for arbitrary third-party workloads — it is an **evaluation / instrumentation** layer tied to the R2L CLI + artifact model.  
- A **fork or extension** of R2L that modifies how R2L runs a single question inside the substrate.  
- **Portability-complete** merely because this manual exists — final **readiness verdict** is **M24**; status remains **`NOT READY`** until the ledger says otherwise (see [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)).  
- A **stable HTTP product API** for downstream integration — the **canonical readiness invocation surface** is **Python** (`app.clarity.public_surface`). The FastAPI app is **operational / demo**; see §5.  

---

## 3. Key concepts

| Concept | Meaning |
|---------|---------|
| **R2L** | Deterministic micro-lab engine; produces `manifest.json`, `trace_pack.jsonl`, etc., under a run output directory. |
| **Black-box invocation** | `R2LRunner` runs the configured R2L CLI as a subprocess; no R2L Python imports in CLARITY (`CLARITY_BOUNDARY_CONTRACT.md` §9). |
| **Sweep** | Cartesian (or enumerated) combination of perturbation **axes**, **values**, and **seeds**, orchestrated by `SweepOrchestrator`. |
| **`clarity/` namespace** | CLARITY-owned outputs live under the **`clarity/`** prefix relative to the configured output base (`validate_output_path`). |
| **Orchestrator manifest** | `SweepOrchestrator` writes `clarity/sweep_manifest.json` with a **specific** schema family (axes, seeds, runs). |
| **Full analytical bundle** | Three JSON files — `sweep_manifest.json`, `robustness_surface.json`, `monte_carlo_stats.json` — required for the **full** analytical path described in `CLARITY_ARTIFACT_CONTRACT.md` §3. **Orchestrator-only** runs do **not** produce the full bundle by themselves. |
| **Schema families for `sweep_manifest.json`** | **Two** documented families (orchestrator vs rich aggregate). **Do not** assume one global shape — see `CLARITY_ARTIFACT_CONTRACT.md` §6.1. |
| **Canonical vs rich mode** | Canonical paths work without rich trace fields. Rich paths use **`CLARITY_RICH_MODE`** / **`CLARITY_REAL_MODEL`** (and optional **`CLARITY_RICH_LOGITS_HASH`**) per [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §7 and §7 of the boundary contract. |

---

## 4. Current implemented pipeline

High-level **implemented** path for sanctioned consumers:

```text
SweepConfig + base spec JSON
  → SweepOrchestrator
       → for each (axis values, seed): build run config, optionally run perturbations
       → R2LRunner.run(...)  [subprocess → R2L CLI]
       → read manifest.json + trace_pack.jsonl in R2L output dir
       → aggregate into sweep manifest
  → write clarity/sweep_manifest.json (under output tree)
  → SweepResult (paths, run records)
```

**Downstream** (not all invoked by `SweepOrchestrator` alone):

- **Metrics** (`metrics_engine`) — ESI, drift, etc., from traces.  
- **Surfaces** (`surface_engine`, `surfaces`) — `robustness_surface.json`.  
- **Monte Carlo stats** — `monte_carlo_stats.json` in full bundle contexts.  
- **Gradients** (`gradient_engine`) — derived from surfaces.  
- **Counterfactual probe** (`counterfactual_engine`) — region masks and probe surfaces.  
- **Report export** — PDF/PNG pipelines (presentation-oriented; see artifact contract).  
- **Rich-mode** — optional token/logprob paths; gated by env vars.  

**Honesty:** Treating “I ran `SweepOrchestrator`” as “I have the full three-file analytical bundle” is **not** valid — see `CLARITY_ARTIFACT_CONTRACT.md` §3 and `CLARITY_PUBLIC_SURFACE.md` §8.2.

---

## 5. Public invocation flow (frozen — M21)

**Canonical module:** **`app.clarity.public_surface`**

- Import **only** symbols from this module for downstream readiness (see [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §4 for the frozen name list).  
- **`PUBLIC_SURFACE_SYMBOLS`** in code must match **`__all__`** — enforced by tests.  
- **`app.clarity`** package root re-exports many names for **tests and legacy code** — it is **not** the portability contract.  
- **HTTP API** (FastAPI): **non-canonical** for readiness — do **not** treat route shapes as stable external APIs unless a future milestone freezes them.  
- **No CLARITY console script** is shipped for consumers — see `CLARITY_PUBLIC_SURFACE.md` §3.  
- **Breaking changes** to the frozen public surface require readiness governance (decision + milestone + test updates) — see `CLARITY_PUBLIC_SURFACE.md` §10. **No semver** is claimed.  

---

## 6. Artifact flow

### 6.1 What CLARITY reads (from R2L)

After a successful CLI run, the runner **requires** at minimum:

- `manifest.json` — parsed by `artifact_loader.load_manifest`  
- `trace_pack.jsonl` — parsed by `load_trace_pack`  

Optional trace fields (e.g. rich `adapter_metadata`) may be present; canonical paths must **not** require them (`CLARITY_BOUNDARY_CONTRACT.md` §5.3).

### 6.2 What CLARITY writes

- Under **`clarity/`** only — enforced by `validate_output_path`.  
- **Contract-relevant** JSON for full bundles per `CLARITY_ARTIFACT_CONTRACT.md` (required vs optional; presentation-only vs hash-participating).  
- **PDFs / images** — generally **presentation-only** / derived; **do not** treat them as contract identity unless a milestone says otherwise.  

### 6.3 Where truth lives

1. **Frozen contracts** in `docs/readiness/`  
2. **Code** (`app/clarity/…`)  
3. **Tests** (`backend/tests/…`)  
4. **Milestone evidence** under `docs/milestones/`  

Vision docs and competition packaging are **context**, not substitutes for contracts.

---

## 7. Determinism rules

- **CLARITY** documents deterministic behavior at **contract surfaces** — JSON ordering rules, `sort_keys` where specified, surface `_round8` semantics for computed floats in specific engines, sweep manifest ordering — see `CLARITY_ARTIFACT_CONTRACT.md` §§7–8.  
- **R2L single-run determinism** is an **assumed** substrate property (`CLARITY_ASSUMED_GUARANTEES.md`).  
- **Byte-identical** JSON across **all** writers is **not** globally guaranteed — **semantic** equality after parse is the M20 baseline for many comparisons.  
- **Rich / GPU** paths may exhibit **non-determinism** outside what CLARITY tests lock — do not equate rich and canonical paths without evidence.  

---

## 8. Boundary rules (summary)

Full text: [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md).

**Rules of thumb:**

1. **Do not** write or overwrite R2L-owned top-level artifacts (`manifest.json`, `trace_pack.jsonl`, …).  
2. **Do not** import R2L internal Python modules from `app/clarity` (AST guardrails in tests).  
3. **Do** write CLARITY outputs only under **`clarity/`**.  
4. **Rich mode** does not relax namespace or import rules.  

---

## 9. Debugging guide

| Symptom | Likely cause | What to check |
|---------|--------------|----------------|
| `R2LInvocationError` / `R2LTimeoutError` | R2L CLI failure, missing artifacts | `R2LRunner` tests in `test_r2l_runner.py`; stderr from subprocess; timeout value. |
| Missing `manifest.json` or `trace_pack.jsonl` | Incomplete R2L run | Output directory contents; R2L exit code. |
| `OutputDirectoryExistsError` | Sweep output already exists | Use a fresh `output_root` (orchestrator rejects overwrites). |
| `SweepConfigValidationError` | Invalid sweep config | `SweepConfig` + base spec path; see `SweepOrchestrator` validation. |
| Missing `robustness_surface.json` / `monte_carlo_stats.json` after orchestrator | Expected — orchestrator-only | Run metrics/surface pipelines or full bundle scripts; see `CLARITY_ARTIFACT_CONTRACT.md` §3. |
| Wrong `sweep_manifest.json` shape | **Two schema families** | Identify producer (orchestrator vs rich aggregate) — §6.1 artifact contract. |
| “Import worked but downstream broke” | Importing **internal** modules | Use **`app.clarity.public_surface` only** for supported consumer imports. |
| Confusion about demo vs canonical | **HTTP vs Python** | Demo is **non-canonical** for readiness; see §5. |
| Rich path not activating | Env not set | `CLARITY_RICH_MODE`, `CLARITY_REAL_MODEL` per public surface doc. |

---

## 10. Extension guide

- **Respect frozen contracts** — boundary, artifact, public surface.  
- **Additive** changes are acceptable only when they do **not** silently change consumer meaning of existing artifacts or symbols.  
- **Contract-affecting** changes (boundary, artifact names/semantics, public surface symbols) require **readiness governance** (milestones, decisions, tests).  
- **Do not** “extend” CLARITY by importing unsupported internals just because they are importable — that bypasses `CLARITY_PUBLIC_SURFACE.md`.  
- New **features** belong in normal feature milestones with tests; **readiness** milestones (M18–M24) are **not** for unrelated capability work (`readinessplan.md` non-goals).  

---

## 11. Frozen surfaces and versioning discipline

| Surface | Authority |
|---------|-----------|
| Consumer boundary | `CLARITY_BOUNDARY_CONTRACT.md` (M19) |
| Assumed vs owned guarantees | `CLARITY_ASSUMED_GUARANTEES.md` (M19) |
| Artifacts & serialization | `CLARITY_ARTIFACT_CONTRACT.md` (M20) |
| Public Python invocation | `CLARITY_PUBLIC_SURFACE.md` (M21) + `app/clarity/public_surface.py` |
| Project ledger | [`docs/clarity.md`](../clarity.md) |

**No semver** on the public surface for M21; breaking changes require explicit governance (`CLARITY_PUBLIC_SURFACE.md` §10).

---

## 12. Repository structure (quick reference)

```text
backend/
  app/
    clarity/
      public_surface.py   ← Canonical consumer imports (M21)
      r2l_runner.py       ← Black-box R2L invocation
      sweep_orchestrator.py
      metrics_engine.py, surface_engine.py, gradient_engine.py, …
    main.py               ← FastAPI app (demo / operational; not readiness-canonical)
  tests/                  ← Contract + unit tests (see §13)
docs/
  clarity.md              ← Project ledger
  readiness/              ← Readiness pack (this file, contracts, ledger)
frontend/                 ← UI console (demo)
```

---

## 13. Quick reference — key documents and tests

| Document | Role |
|----------|------|
| [`docs/clarity.md`](../clarity.md) | Project ledger, milestones |
| [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) | **Canonical** Python surface |
| [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) | R2L consumer boundary |
| [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) | Artifact inventory & schemas |
| [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md) | Inherited vs CLARITY-owned |
| [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) | Readiness status (**`CONDITIONALLY READY`** — see [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md)) |

| Topic | Tests (examples) |
|-------|------------------|
| Public surface | `backend/tests/test_public_surface_contract.py` |
| Boundary | `backend/tests/test_boundary_contract.py` |
| Artifacts | `backend/tests/test_artifact_contract.py` |
| R2L runner | `backend/tests/test_r2l_runner.py` |
| Sweep | `backend/tests/test_sweep_orchestrator.py` |
| Metrics / surfaces / gradients / counterfactual | `test_metrics_engine.py`, `test_surface_engine.py`, `test_gradient_engine.py`, `test_counterfactual_engine.py` |
| Report | `backend/tests/test_report_determinism.py` |

### Environment variables (CLARITY-side, rich / real paths)

| Variable | Role |
|----------|------|
| `CLARITY_RICH_MODE` | Enable rich-mode handling when truthy |
| `CLARITY_REAL_MODEL` | Required with rich for real inference paths |
| `CLARITY_RICH_LOGITS_HASH` | Optional logits hashing |

---

## 14. Related documents

| Document | Role |
|----------|------|
| [`docs/clarity.md`](../clarity.md) | Governance ledger |
| [`readinessplan.md`](./readinessplan.md) | Full M18–M24 program |
| [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) | **Must** be read alongside this manual for invocation |
| [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) | Implemented vs planned vs unknown matrix |

---

*Introduced: M22 — Operating Manual & Honest Implementation Matrix. Readiness status: **`CONDITIONALLY READY`** (M24 — see [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md), [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)).*
