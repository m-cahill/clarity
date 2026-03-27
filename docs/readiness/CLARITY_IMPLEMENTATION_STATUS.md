# CLARITY implementation status (Readiness)

**Purpose:** Table-driven **honest** status of major surfaces: **Implemented**, **Planned**, or **Unknown**.  
**Authority:** This document is **not** a substitute for frozen contracts (`CLARITY_*_CONTRACT.md`, `CLARITY_PUBLIC_SURFACE.md`); it summarizes them plus code/test evidence.  
**Readiness:** Project **`NOT READY`** until M24 verdict — see [`READINESS_LEDGER.md`](./READINESS_LEDGER.md).

### Status taxonomy

| Status | Meaning |
|--------|---------|
| **Implemented** | Present in code **and** evidenced by tests and/or an explicit frozen readiness document. |
| **Planned** | Explicitly on the roadmap (`readinessplan.md`, ledger, or `docs/clarity.md`) but **not** delivered as a governed artifact or stable surface. |
| **Unknown** | Insufficient evidence after inspection; **do not** treat as supported. |

---

## Matrix A — Core identity and contracts

| Surface | Status | Owner / source-of-truth | Code evidence | Test evidence | Notes / limitations |
|---------|--------|------------------------|---------------|---------------|---------------------|
| Identity: consumer-only posture | **Implemented** | [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) | `app/clarity/r2l_runner.py`, `validate_output_path` | `test_boundary_contract.py` (namespace, forbidden imports) | CLARITY does not modify R2L execution semantics. |
| Boundary contract (M19) | **Implemented** | `CLARITY_BOUNDARY_CONTRACT.md` | `app/clarity/*` vs R2L CLI | `test_boundary_contract.py` | Frozen; do not reopen without governance. |
| Assumed-guarantees split (M19) | **Implemented** | `CLARITY_ASSUMED_GUARANTEES.md` | N/A (policy doc) | N/A | Distinguishes inherited substrate assumptions from CLARITY-owned tests. |
| Artifact contract (M20) | **Implemented** | `CLARITY_ARTIFACT_CONTRACT.md` | Writers in `sweep_orchestrator`, `surface_engine`, scripts | `test_artifact_contract.py`, `test_boundary_contract.py` | Two `sweep_manifest.json` schema families — see §6.1 of artifact contract. |
| **Public invocation surface (M21)** | **Implemented** | **`CLARITY_PUBLIC_SURFACE.md`** | **`app/clarity/public_surface.py`** (`PUBLIC_SURFACE_SYMBOLS`) | **`test_public_surface_contract.py`** (`test_public_surface_export_snapshot`, `test_sanctioned_consumer_sweep_smoke`) | **Canonical module:** `app.clarity.public_surface`. No semver claim. |

---

## Matrix B — Runtime and analysis surfaces

| Surface | Status | Owner / source-of-truth | Code evidence | Test evidence | Notes / limitations |
|---------|--------|------------------------|---------------|---------------|---------------------|
| Sweep orchestration | **Implemented** | `CLARITY_BOUNDARY_CONTRACT.md` §4 + `CLARITY_ARTIFACT_CONTRACT.md` §3 | `app/clarity/sweep_orchestrator.py` | `test_sweep_orchestrator.py` (e.g. `test_full_sweep_with_fake_r2l`, `test_manifest_created`) | Orchestrator writes **orchestrator** `sweep_manifest.json` only. |
| Metrics (ESI, drift, etc.) | **Implemented** | Code + tests (contract-adjacent) | `app/clarity/metrics_engine.py` | `test_metrics_engine.py` (e.g. `test_full_sweep_computation`) | Consumer relevance: full bundle paths, not single-run demo. |
| Robustness surfaces | **Implemented** | `CLARITY_ARTIFACT_CONTRACT.md` §6.2 | `app/clarity/surface_engine.py`, `app/clarity/surfaces.py` | `test_surface_engine.py` (e.g. `test_full_surface_computation`) | Output `robustness_surface.json` when pipeline run. |
| Gradient / stability analysis | **Implemented** | Code + tests | `app/clarity/gradient_engine.py` | `test_gradient_engine.py` (e.g. `test_metrics_to_surface_to_gradient`, `test_real_sweep_to_gradient_determinism`) | Depends on surface inputs. |
| Counterfactual probe | **Implemented** | Code + tests | `app/clarity/counterfactual_engine.py` | `test_counterfactual_engine.py` (e.g. `test_full_probe_pipeline`) | Not part of minimal public surface re-exports. |
| **Report export** (PDF / assets) | **Implemented** | `CLARITY_ARTIFACT_CONTRACT.md` §5 (presentation-only) | Report pipeline modules | `test_report_determinism.py` | PDFs are **presentation-oriented**; not bundle identity. |
| **UI console** | **Implemented** | `docs/clarity.md` (feature milestone); **not** readiness contract | `frontend/` | Frontend test suite | **Not** canonical for portability; product UI. |
| **Rich-mode ingestion** | **Implemented** (with gates) | `CLARITY_BOUNDARY_CONTRACT.md` §7, `CLARITY_PUBLIC_SURFACE.md` §7 | `medgemma_runner`, `rich_generation`, etc. | `test_rich_generation_unit.py`, `test_rich_mode_determinism.py`, `test_real_adapter_determinism.py`, `test_boundary_contract.py` (rich env) | **Not** equivalent to canonical paths unless tests cover the combination. |
| **Real-model path** (MedGemma via R2L) | **Implemented** | `docs/clarity.md` (M13); env-gated | `medgemma_runner`, adapter | `test_real_adapter_determinism.py` | GPU / env; not CI-default on all jobs. |

---

## Matrix C — Integration surfaces and governance

| Surface | Status | Owner / source-of-truth | Code evidence | Test evidence | Notes / limitations |
|---------|--------|------------------------|---------------|---------------|---------------------|
| **Demo HTTP / API** | **Implemented** (operationally) | **Not** canonical for readiness — `CLARITY_PUBLIC_SURFACE.md` §3 | `app/main.py`, demo routers | `test_demo_router.py` | **Do not** treat as stable external API for adoption. |
| **Compatibility guarantees** (semver, cross-repo version matrix) | **Planned** | **M23** — `readinessplan.md` (compatibility matrix) | N/A | N/A | No semver on public surface (M21). |
| **Consumer assumptions pack** | **Planned** | **M23** — `CLARITY_CONSUMER_ASSUMPTIONS.md` | N/A | N/A | See `docs/readiness/READINESS_LEDGER.md`. |
| **Transfer checklist** | **Planned** | **M23** — `CLARITY_TRANSFER_CHECKLIST.md` | N/A | N/A | — |
| **Portability verdict** | **Planned** | **M24** — `CLARITY_READINESS_SCORECARD.md` | N/A | N/A | Ledger verdict reserved until M24. |
| **Readiness scorecard / change control** | **Planned** | **M24** | N/A | N/A | — |

---

## Matrix D — Explicit Unknown / low-evidence

| Surface | Status | Owner / source-of-truth | Notes |
|---------|--------|------------------------|-------|
| **Single unified JSON Schema** for all `sweep_manifest.json` producers | **Unknown** / **Deferred** | `CLARITY_ARTIFACT_CONTRACT.md` §6.4, §12 | Two families documented; unification **deferred**. |
| **Byte-identical JSON** across all writers | **Unknown** | `CLARITY_ARTIFACT_CONTRACT.md` §9 | Semantic equality is the M20 baseline; byte match not global. |

---

## Consumer relevance summary

- **Adopt via:** `app.clarity.public_surface` + `docs/readiness/` contracts + this matrix + operating manual.  
- **Do not adopt via:** HTTP route shapes, broad `app.clarity` imports, or undocumented scripts — unless you accept **unsupported** risk.  

---

*Introduced: M22 — Operating Manual & Honest Implementation Matrix.*
