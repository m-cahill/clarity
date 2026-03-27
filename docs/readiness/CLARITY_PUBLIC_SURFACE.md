# CLARITY_PUBLIC_SURFACE — Consumer invocation contract (Readiness)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M21 — Public Surface & Invocation Contract |
| **Authority** | Canonical readiness-pack document for **how** a consumer project may invoke CLARITY safely |
| **Readiness status** | **`CONDITIONALLY READY`** (M24 — see [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md), [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)) |

---

## 1. Purpose and scope

This document freezes the **single official consumer-facing invocation surface** for CLARITY: a **thin Python module** that re-exports only the symbols required for the sanctioned black-box R2L + sweep flow.

**In scope:** Which Python imports are supported for downstream adoption; what is internal; required and optional configuration for documented paths; failure semantics; versioning discipline for this surface.

**Out of scope for M21:** HTTP API routes (demo/operational), setuptools console scripts (none shipped), MedGemma or UI redesign, R2L substrate semantics, and full analytical bundle guarantees beyond what the chosen path produces (see §8 and [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md)).

---

## 2. Canonical public surface

**Module:** `app.clarity.public_surface`

Consumers should import **only** from this module when depending on the readiness contract:

```python
from app.clarity.public_surface import (
    R2LRunner,
    SweepOrchestrator,
    SweepConfig,
    # … see §4 for the full frozen list
)
```

The submodule is also reachable as `from app.clarity import public_surface` for discoverability; **symbol-level** support is defined by `public_surface.__all__` and `PUBLIC_SURFACE_SYMBOLS` in that module.

---

## 3. Secondary surfaces

| Surface | Role in M21 |
|---------|-------------|
| **`app.clarity` package root** | **Not** the canonical contract. Re-exports a large set for tests and legacy code. Treat as **internal / unsupported** for portability unless a future milestone narrows it. |
| **HTTP API** (`FastAPI` app under `app.main`) | **Non-canonical** for readiness. Used by the demo and internal tooling; **not** versioned or frozen as the M21 public contract. Do not build downstream integrations against route shapes as a stability guarantee. |
| **CLI entrypoint for CLARITY** | **None** is shipped (`pyproject.toml` has no `console_scripts` for CLARITY). R2L is still invoked **by** `R2LRunner` via a **substrate CLI string** you configure (see §7). |

---

## 4. Explicitly stable elements (frozen names)

These names are re-exported from `app.clarity.public_surface` and are covered by guardrail tests:

| Symbol | Kind |
|--------|------|
| `R2LRunner` | Class |
| `R2LRunResult` | Dataclass |
| `R2LInvocationError` | Exception |
| `R2LTimeoutError` | Exception |
| `SweepOrchestrator` | Class |
| `SweepResult` | Dataclass |
| `SweepExecutionError` | Exception |
| `OutputDirectoryExistsError` | Exception |
| `SweepConfig` | Dataclass |
| `SweepAxis` | Dataclass |
| `SweepRunRecord` | Dataclass |
| `SweepConfigValidationError` | Exception |
| `build_run_directory_name` | Function |
| `encode_axis_value` | Function |

The authoritative set is **`PUBLIC_SURFACE_SYMBOLS`** in `app/clarity/public_surface.py` (must match `__all__`).

---

## 5. Explicitly internal / unsupported (for consumers)

Unless a future readiness milestone says otherwise:

- Imports from **`app.clarity`** submodules **other than** `public_surface` (e.g. `metrics_engine`, `surface_engine`, `medgemma_runner`, `artifact_loader` directly) are **not** part of the M21 contract.
- **`app.clarity.__all__`** breadth does **not** imply that every listed name is a supported downstream API.
- **Demo routers**, **report routers**, and **counterfactual HTTP** paths are **operational / product** surfaces, not the M21 portability contract.
- **Scripts** under `backend/scripts/` are validation or packaging utilities, not a frozen CLI for consumers.

---

## 6. Required configuration

- **R2L substrate:** A working **R2L-compatible CLI** (or test double) and valid **config** / **output** paths as required by `R2LRunner.run()` (see code and [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) §5).
- **Sweep:** A **`SweepConfig`** with valid `base_spec_path`, `axes`, `seeds`, and `adapter` per `SweepOrchestrator.execute()` — see `SweepConfig` validation in implementation.

No separate CLARITY package install step is required beyond installing this repository’s backend package as you already do for development.

---

## 7. Optional configuration (environment)

For **rich / real-model paths** referenced elsewhere in the codebase, the **CLARITY-side** names frozen in readiness are (see RD-010):

| Variable | Role |
|----------|------|
| `CLARITY_RICH_MODE` | Enables rich-mode handling in CLARITY when truthy (`true`, `1`, `yes`, `on`). |
| `CLARITY_REAL_MODEL` | Required together with rich real paths where the implementation gates real inference. |
| `CLARITY_RICH_LOGITS_HASH` | Optional; enables logits hashing when set. |

Do **not** treat upstream-only names (e.g. substrate flags not wired in CLARITY) as part of this contract. Deployment-only variables (Netlify, CORS, etc.) are **not** required for the canonical **Python** consumer path.

---

## 8. Invocation examples

### 8.1 Minimal pattern (conceptual)

1. Construct `R2LRunner(r2l_executable="...", timeout_seconds=...)`.
2. Construct `SweepOrchestrator(runner, output_root=Path("..."))` with a **non-existing** `output_root` (orchestrator rejects overwrites).
3. Call `orchestrator.execute(SweepConfig(...))`.
4. On success, obtain `SweepResult` with `sweep_manifest_path` under the CLARITY output namespace rules (see boundary + artifact contracts).

### 8.2 Outputs expected from this path

- **`SweepOrchestrator`** persists **`clarity/sweep_manifest.json`** under the sweep output tree (see [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) §3 and §6.1 — orchestrator manifest schema).
- The **full** three-file analytical bundle (`sweep_manifest.json`, `robustness_surface.json`, `monte_carlo_stats.json`) requires **additional** materialization steps (e.g. metrics/surface pipelines or validation scripts). **Do not** assume those files appear from orchestrator execution alone.

---

## 9. Failure semantics / exit conditions

| Situation | Behavior |
|-----------|----------|
| R2L non-zero exit or missing `manifest.json` / `trace_pack.jsonl` | `R2LInvocationError` (or `R2LTimeoutError` on timeout) from `R2LRunner.run()`. |
| Output directory already exists for a sweep | `OutputDirectoryExistsError` (subclass of `SweepExecutionError`). |
| Invalid sweep configuration | `SweepConfigValidationError` or `SweepExecutionError` per implementation. |

There is **no** separate CLARITY process exit code: consumers integrate via **Python exceptions** on the canonical path.

---

## 10. Versioning promise

**No semver** is claimed for M21.

**Promise:** The canonical public surface is frozen **as of M21** as a readiness contract. **Breaking changes** to `app.clarity.public_surface` (removing or renaming listed symbols, or changing documented semantics) require:

1. An explicit readiness **decision** record,
2. A **milestone** that authorizes the change, and
3. **Guardrail test** updates.

Final **downstream readiness** and portability verdict remain **M24**; this milestone does **not** claim full adoption readiness.

---

## 11. Unsupported shortcuts / forbidden consumer patterns

- Importing **internal** `app.clarity` modules for convenience when `public_surface` exposes the needed entrypoints.
- Treating **HTTP routes** as a stable external API without a future milestone that freezes them.
- Assuming **full** artifact bundle files from **orchestrator-only** runs (see §8.2 and [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md)).
- Depending on **undefined** environment variables or substrate flags not listed in §7 for the paths you run.

---

## 12. Related documents

- [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) — R2L consumer boundary, namespace, black-box invocation.
- [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) — Artifact inventory and producer-specific shapes.
- [`READINESS_DECISIONS.md`](./READINESS_DECISIONS.md) — RD-014 (canonical public surface).
