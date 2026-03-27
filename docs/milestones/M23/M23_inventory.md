# M23 — Combination inventory (milestone artifact)

**Purpose:** Auditable bridge from repo inspection to **Supported / Unsupported / Unknown** claims in [`CLARITY_COMPATIBILITY_MATRIX.md`](../../readiness/CLARITY_COMPATIBILITY_MATRIX.md).  
**Status:** Milestone-local working note; not a substitute for frozen contracts.  
**As-of:** M23 branch (`m23-supported-combination-truth-table`).

**Posture:** Same honesty taxonomy as M22: **Supported** only with strong evidence; default thin evidence → **Unknown**.

---

## 1. Invocation surfaces

| Candidate combination | Code / contract | Tests / evidence | Preliminary classification |
|----------------------|-----------------|------------------|----------------------------|
| Canonical **`app.clarity.public_surface`** + `R2LRunner` + `SweepOrchestrator` | `app/clarity/public_surface.py`, `r2l_runner.py`, `sweep_orchestrator.py` | `test_public_surface_contract.py`, `test_sweep_orchestrator.py` | **Supported** (readiness consumer path) |
| **`app.clarity` package root** imports (non–`public_surface`) | Broad `__all__` | M21 contract explicitly **not** canonical | **Unsupported** for portability |
| **HTTP / FastAPI** demo and product routes | `app/main.py`, routers | `test_demo_router.py`; `CLARITY_PUBLIC_SURFACE.md` §3 **non-canonical** | **Unsupported** as readiness contract; operational only |

---

## 2. Execution modes

| Candidate | Code / notes | Tests | Preliminary classification |
|-----------|--------------|-------|----------------------------|
| Canonical **non-rich** sweep / fake R2L (CI-style) | Default sweep paths | `test_sweep_orchestrator.py`, synthetic adapters | **Supported** where sweep + public surface tests cover |
| **Rich mode** (`CLARITY_RICH_MODE` + real paths) | Boundary §7, `medgemma_runner`, `rich_generation` | `test_rich_generation_unit.py`, `test_rich_mode_determinism.py`, `test_boundary_contract.py` (env) | **Unknown** for arbitrary consumer combos unless evidence row in matrix |
| **Real model** (`CLARITY_REAL_MODEL`) | GPU / env gated | `test_real_adapter_determinism.py` | **Unknown** as default portability claim; **Supported** only where tests + docs scope |

---

## 3. Output expectations

| Candidate | Contract | Evidence | Preliminary classification |
|-----------|----------|----------|----------------------------|
| **Orchestrator-only:** `clarity/sweep_manifest.json` (orchestrator family) | `CLARITY_ARTIFACT_CONTRACT.md` §3, §6.1 | `test_sweep_orchestrator.py::test_manifest_created` | **Supported** for orchestrator execute path |
| **Full analytical bundle** (three JSON files) | `CLARITY_ARTIFACT_CONTRACT.md` §3 | M15 script + `backend/tests/fixtures/baselines/m15_real_ui/`, `test_artifact_contract.py` | **Supported** only for documented full-bundle producer path; **not** from orchestrator alone |
| **Presentation-only** (PDF, plots) | Artifact contract §5 | `test_report_determinism.py` | **Supported** as presentation outputs; not bundle identity |

---

## 4. Operating context

| Context | Role | Preliminary classification |
|---------|------|----------------------------|
| **Local tests / CI** with fakes | Primary guardrail evidence | **Supported** for documented test paths |
| **Readiness-contract path** | `docs/readiness/*` + `app.clarity.public_surface` | **Supported** as documented |
| **Demo / cloud deployment** | `docs/clarity.md` deploy notes; no GPU in cloud | **Unknown** for full analytical guarantees in production demo |

---

## 5. Matrix row mapping

Inventory rows above feed **combination IDs** C-001–C-012 in [`CLARITY_COMPATIBILITY_MATRIX.md`](../../readiness/CLARITY_COMPATIBILITY_MATRIX.md). Classification and evidence strings are authoritative in that document.
