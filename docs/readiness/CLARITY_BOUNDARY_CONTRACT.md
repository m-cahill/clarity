# CLARITY_BOUNDARY_CONTRACT — Consumer Boundary (Readiness)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M19 — Consumer Boundary Freeze |
| **Authority** | Canonical **readiness-pack** boundary contract for CLARITY↔R2L |
| **Supersedes as readiness authority** | Does **not** silently replace [`CLARITY_ARCHITECHTURE_CONTRACT.MD`](../CLARITY_ARCHITECHTURE_CONTRACT.MD); that document remains an earlier architectural input. For portability and readiness decisions, **this file** and [`docs/clarity.md`](../clarity.md) govern. |
| **Readiness status** | Project readiness remains **`NOT READY`** until M24 verdict (see [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)). |

---

## 1. Purpose

This document freezes the **implemented** CLARITY↔R2L consumer boundary so that a consumer project or external repository can depend on **explicit, test-backed rules**—not informal context. Wording reflects **current code and tests** in this repository unless labeled *deferred*.

---

## 2. Boundary statement

CLARITY is a **deterministic evaluation instrument** layered **above** R2L. It **consumes** R2L run outputs as files and **produces** its own artifacts under a dedicated namespace. CLARITY **does not** modify R2L execution semantics, schemas, or CI behavior **in the R2L substrate**.

---

## 3. Identity: what CLARITY is / is not

### What CLARITY is

- A **consumer** of R2L: it invokes R2L through a **black-box** surface (CLI / subprocess) and reads declared artifacts from an output directory.
- An **orchestration and analysis** layer: perturbation sweeps, metrics, aggregation, visualization, reporting, and UI are CLARITY-owned.

### What CLARITY is not

- **Not** an extension or fork of R2L that alters how R2L runs single questions.
- **Not** an execution substrate for downstream projects; it is an **evaluation / instrumentation** layer.
- **Not** authorized to import **internal** R2L Python modules (see §9 and tests).

---

## 4. Default interaction model (black-box)

**Implemented truth:** R2L is invoked via **subprocess** using a configurable CLI command (e.g. `r2l` or `python -m …`). See `app.clarity.r2l_runner.R2LRunner`.

- **Default sanctioned consumer surface (this repo):** CLI invocation + artifact consumption. No shared in-process coupling with R2L.
- **Future:** A stable **public Python invocation surface** for consumers may be frozen in **M21**; until then, treating deep imports as a supported public API is **out of scope** for readiness.

---

## 5. Allowed inputs consumed from R2L

### 5.1 Invocation inputs

- **Config file path** and **output directory** passed to the R2L CLI (`--config`, `--output`).
- Optional **adapter** and **seed** arguments as supported by the runner (`R2LRunner.run`).

### 5.2 Artifacts CLARITY may read (post-run)

After a successful CLI run, the runner **requires** these paths under the R2L output directory:

| Artifact | Role |
|----------|------|
| `manifest.json` | Run metadata; must satisfy `artifact_loader.load_manifest` required fields (`run_id`, `timestamp`, `seed`, `artifacts`). |
| `trace_pack.jsonl` | Trace records; validated by `load_trace_pack` (each record JSON object; `step` or `step_id` required). |

Additional files (e.g. other filenames listed under `manifest["artifacts"]`) may be consumed by higher-level pipelines **as implemented**; the **minimal** boundary enforced by `R2LRunner` is **`manifest.json` + `trace_pack.jsonl`**.

### 5.3 Optional rich trace content

- Trace lines may include optional fields such as **`adapter_metadata`** when rich inference is enabled.
- CLARITY must **not** require optional fields for core paths: **canonical** traces without rich metadata must remain valid (see tests and [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md)).

---

## 6. CLARITY-owned outputs and namespace rules

### 6.1 Namespace

- CLARITY writes user-facing sweep and analysis outputs under the **`clarity/`** prefix relative to the relevant base directory (`get_clarity_output_namespace()` → `"clarity/"`).
- Output paths must pass **`validate_output_path`** — paths outside `clarity/` are **rejected** (including attempts to overwrite R2L-owned top-level artifacts like `manifest.json`).

### 6.2 Representative outputs

Examples (non-exhaustive; full artifact contract is **M20**): `clarity/sweep_manifest.json`, `clarity/robustness_surface.json`, `clarity/monte_carlo_stats.json`, reports and visualization assets as produced by CLARITY modules.

---

## 7. Canonical mode vs rich mode (boundary)

### 7.1 Canonical (non-rich) path

- **Sweep / ledger:** `SweepManifest.rich_mode` may be **false** (default).
- **Traces:** `trace_pack.jsonl` without `adapter_metadata` remains valid.
- **CI:** Default pipelines rely on **non-GPU** / synthetic paths as configured; rich GPU tests are gated by environment (see tests).

### 7.2 Rich mode (optional)

**Implemented gating in this repository** (implementation beats historical doc naming):

| Concern | Canonical in this repo |
|---------|-------------------------|
| Enable rich **CLARITY** inference features | **`CLARITY_RICH_MODE`** (truthy: `true`, `1`, `yes`, `on`) together with **`CLARITY_REAL_MODEL`** for real MedGemma-rich paths (see `medgemma_runner`, `rich_generation`). |
| Optional logits hashing | **`CLARITY_RICH_LOGITS_HASH`** |

**Legacy / upstream wording:** Some non-readiness docs refer to substrate-side names such as **`R2L_RICH_MODE`**. That is **not** the environment switch implemented in this repository’s CLARITY code paths. Where upstream R2L uses its own flags, those belong to the **substrate** configuration; CLARITY’s **readiness** contract for “did we enable rich handling in CLARITY?” is anchored on **`CLARITY_RICH_MODE`** (+ **`CLARITY_REAL_MODEL`** where applicable).

### 7.3 Boundary invariant across modes

- **Rich mode does not** relax namespace rules: CLARITY still writes only under **`clarity/`** for CLARITY-owned outputs.
- **Rich mode does not** authorize importing R2L internals.

---

## 8. Determinism and seed semantics

### 8.1 R2L single run

- CLARITY assumes each R2L invocation is **deterministic for a given config and seed** as provided to the CLI (substrate responsibility; see assumed guarantees).

### 8.2 Monte Carlo / multi-seed sweeps

- CLARITY implements multi-seed workflows as **external enumeration**: e.g. `for seed in seeds: run R2L with that seed`.
- **`SweepManifest`** records ordered seeds, adapter model id, R2L version string, perturbation axes, and **`rich_mode`** for reproducibility of the **CLARITY** side of the ledger.

---

## 9. Forbidden behaviors

1. **Mutate or overwrite substrate-owned artifacts** in the R2L output directory (e.g. writing over `manifest.json` / `trace_pack.jsonl` from CLARITY logic). Use **`clarity/`** for CLARITY outputs.
2. **Import internal R2L modules** (patterns such as `r2l.internal`, `r2l.runner`, `r2l._private` are forbidden in `app/clarity/` per AST guardrails).
3. **Depend on undocumented R2L internals** as a substitute for file-based contracts.
4. **Silently redefine** the consumer boundary by mode: rich vs canonical must remain **explicit** in manifests and tests (no hidden requirement for optional trace fields on canonical paths).
5. **Treat CLARITY as the execution substrate** for third-party “runs” without going through the documented consumer model (black-box R2L + explicit artifacts).

---

## 10. Test evidence / enforcement notes

| Topic | Location |
|-------|-----------|
| Parse manifest / trace fixtures; optional `adapter_metadata` | `backend/tests/test_boundary_contract.py`, `backend/tests/fixtures/r2l_samples/` |
| Namespace / no overwrite | `validate_output_path`, tests in `test_boundary_contract.py` |
| Deterministic JSON / sweep manifest | `app.clarity.serialization`, `SweepManifest`, tests |
| Forbidden imports | AST tests in `test_boundary_contract.py` |
| Readiness pack file presence + README links | `backend/tests/test_readiness_pack.py` |
| M19 cumulative boundary tests | `test_boundary_contract.py` (M19 section) |

---

## 11. Deferred or explicitly non-frozen surfaces

| Surface | Status |
|---------|--------|
| Full **artifact contract** (all files, hashes, presentation vs canonical) | **M20** |
| **Single official public API** for downstream Python consumers | **M21** |
| **Compatibility matrix / transfer checklist** | **M23** |
| Portable **readiness verdict** | **M24** |

---

## 12. Related documents

- [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md) — inherited vs CLARITY-owned responsibilities.
- [`readinessplan.md`](./readinessplan.md) — full M18–M24 program.
- [`../CLARITY_CAPABILITY_CONTEXT.md`](../CLARITY_CAPABILITY_CONTEXT.md) — architectural context (input; not readiness authority on its own).
- [`../CLARITY_ARCHITECHTURE_CONTRACT.MD`](../CLARITY_ARCHITECHTURE_CONTRACT.MD) — earlier boundary notes (M01); **readiness authority** is this pack + `docs/clarity.md`.
