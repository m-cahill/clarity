# M22 — Repo truth inventory (working note)

**Purpose:** Bridge from code inspection to `CLARITY_OPERATING_MANUAL.md` and `CLARITY_IMPLEMENTATION_STATUS.md`.  
**Status:** Milestone-local; not part of the readiness-pack authority set.  
**As-of:** M22 branch (see git for exact commit).

---

## 1. Canonical consumer surface (readiness)

| Item | Code / contract | Tests |
|------|-----------------|-------|
| Frozen module | `app.clarity.public_surface` — re-exports `R2LRunner`, `SweepOrchestrator`, sweep models/errors, helpers; `PUBLIC_SURFACE_SYMBOLS` | `test_public_surface_contract.py::test_public_surface_smoke_import`, `test_public_surface_export_snapshot`, `test_sanctioned_consumer_sweep_smoke` |
| Contract doc | `docs/readiness/CLARITY_PUBLIC_SURFACE.md` | `test_readiness_pack.py` (file exists) |

**Not canonical for readiness:** `app.clarity` package root breadth; HTTP API under FastAPI (`app.main`); no CLARITY `console_scripts` in `pyproject.toml`.

---

## 2. R2L black-box invocation

| Item | Code | Tests |
|------|------|-------|
| Subprocess CLI runner | `app/clarity/r2l_runner.py` — `R2LRunner`, `R2LRunResult`, `R2LInvocationError`, `R2LTimeoutError` | `test_r2l_runner.py` (e.g. `TestR2LRunner::test_successful_invocation_returns_result`, `test_nonzero_exit_raises`, `test_missing_manifest_raises`, `test_timeout_raises_r2l_timeout_error`) |

**Reads after success:** `manifest.json`, `trace_pack.jsonl` (boundary contract).

---

## 3. Sweep orchestration

| Item | Code | Tests |
|------|------|-------|
| Multi-axis / multi-seed sweeps | `app/clarity/sweep_orchestrator.py` — `SweepOrchestrator`, `SweepResult`, `SweepExecutionError`, `OutputDirectoryExistsError` | `test_sweep_orchestrator.py` (e.g. `test_execute_single_axis_single_seed`, `test_manifest_created`, `test_full_sweep_with_fake_r2l`) |
| Config models | `app/clarity/sweep_models.py` — `SweepConfig`, `SweepAxis`, etc. (exported via `public_surface`) | Covered via public-surface sweep smoke + sweep orchestrator tests |

**Orchestrator-only output:** persists `clarity/sweep_manifest.json` (orchestrator schema family). Does **not** alone guarantee `robustness_surface.json` + `monte_carlo_stats.json` (artifact contract).

---

## 4. Metrics, surfaces, gradients, counterfactual probe

| Area | Code | Tests (representative) |
|------|------|-------------------------|
| ESI / drift metrics | `app/clarity/metrics_engine.py` | `test_metrics_engine.py::TestMetricsEngineComprehensive::test_full_sweep_computation`, boundary-style guards in same file |
| Robustness surfaces | `app/clarity/surface_engine.py`, `app/clarity/surfaces.py` | `test_surface_engine.py::TestSurfaceEngineComprehensive::test_full_surface_computation` |
| Gradient / stability | `app/clarity/gradient_engine.py` | `test_gradient_engine.py::TestGradientEngineIntegration::test_metrics_to_surface_to_gradient`, `test_real_sweep_to_gradient_determinism` |
| Counterfactual probe | `app/clarity/counterfactual_engine.py` | `test_counterfactual_engine.py::TestCounterfactualEngineIntegration::test_full_probe_pipeline` |

---

## 5. Rich-mode ingestion (CLARITY-side)

| Item | Code | Tests |
|------|------|-------|
| Env gating | `CLARITY_RICH_MODE`, `CLARITY_REAL_MODEL`, `CLARITY_RICH_LOGITS_HASH` (see boundary + public surface docs) | `test_boundary_contract.py::TestM19BoundaryContract::test_rich_mode_env_var_name_is_clarity_rich_mode`, `test_rich_mode_sweep_flag_does_not_relax_namespace_rules` |
| Rich generation / logits | `app/clarity/rich_generation.py`, MedGemma paths | `test_rich_generation_unit.py`, `test_rich_mode_determinism.py`, `test_real_adapter_determinism.py` |

Rich paths are **not** interchangeable with canonical sweep-only guarantees without evidence (manual must say so).

---

## 6. Report export

| Item | Code | Tests |
|------|------|-------|
| PDF / image determinism | Report pipeline modules used by `test_report_determinism.py` | `test_report_determinism.py::TestReportPdfDeterminism::test_identical_input_produces_identical_pdf`, `TestPngDeterminism::*` |

PDFs / PNGs: presentation-oriented; artifact contract marks PDFs as presentation-only where applicable.

---

## 7. UI console & demo HTTP (non-canonical)

| Item | Role | Tests |
|------|------|-------|
| Frontend | `frontend/` — console UI | Frontend test suite (out of scope for this inventory’s Python list) |
| Demo API | FastAPI routers (e.g. demo routes) | `test_demo_router.py::TestDemoEndpoints::*` |

Operational/demo surfaces; **not** the M21 readiness invocation contract.

---

## 8. Artifact contract enforcement

| Item | Tests |
|------|-------|
| Bundle shapes, ordering, optional PDF exclusion | `test_artifact_contract.py` (`test_m15_fixture_dir_has_required_bundle_artifacts`, `test_robustness_surface_axis_ordering_alphabetical`, `test_presentation_pdf_not_in_required_bundle`, etc.) |
| Namespace / JSON determinism | `test_boundary_contract.py` (`TestArtifactLoader::*`, `TestDeterminism::*`, `TestOutputPathValidation::*`) |

---

## 9. Readiness pack guardrails

| Item | Tests |
|------|-------|
| Pack files on disk | `test_readiness_pack.py` |
| M22 manual/matrix consistency | `test_m22_operating_manual.py` (this milestone) |

---

## 10. Gaps / explicit non-inference

- **Portability verdict:** M24 only; ledger remains `NOT READY` after M22.
- **Semver:** Not claimed (M21 public surface).
- **Single `sweep_manifest.json` schema:** Two families documented in `CLARITY_ARTIFACT_CONTRACT.md` §6.1 — do not assume one shape.
