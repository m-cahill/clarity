# CLARITY_ARTIFACT_CONTRACT — Outputs & deterministic serialization (Readiness)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M20 — Artifact Contract & Deterministic Output Freeze |
| **Authority** | Canonical **readiness-pack** contract for CLARITY-written artifacts (alongside [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) for namespace rules) |
| **Readiness status** | **`CONDITIONALLY READY`** (M24 — see [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md), [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)) |

---

## 1. Purpose

This document freezes the **consumer-meaningful artifact surface** of CLARITY: what files may appear, which are required for which paths, how JSON is serialized, how ordering and numeric stability behave, and what counts as **contract identity** versus **presentation-only** output.

Wording is grounded in **implemented code and tests** in this repository unless labeled *deferred*.

---

## 2. Artifact authority and namespace

### 2.1 CLARITY-owned outputs

- CLARITY writes analysis artifacts only under paths permitted by **`validate_output_path`** — i.e. under the **`clarity/`** prefix relative to the configured output base directory (see [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) §6).
- **Leaf filenames** in this contract (e.g. `sweep_manifest.json`) are stable **contract names**. Their path is **`clarity/<leaf>`** relative to the sweep or case output root when using the enforced namespace.
- **Test and script fixtures** (e.g. under `backend/tests/fixtures/baselines/`) may store the same leaf names in a flat directory for convenience; **contract identity** is defined by the **leaf filenames and JSON semantics**, not by a particular test directory layout.

### 2.2 Substrate (R2L) artifacts

- `manifest.json`, `trace_pack.jsonl`, and other R2L-owned files are **not** CLARITY artifacts. They are consumed per the boundary contract and are out of scope for this document’s “CLARITY output” rules.

---

## 3. Required artifacts (full analytical bundle)

For a **complete CLARITY analytical bundle** as produced by the **rich validation / full-metrics path** (evidenced by `backend/scripts/m15_real_ui_sweep.py` and frozen fixtures under `backend/tests/fixtures/baselines/m15_real_ui/`), the following **three** JSON files are **required** and **contract-relevant**:

| Leaf name | Role |
|-----------|------|
| `sweep_manifest.json` | Sweep ledger: configuration, seeds, per-run results, and metadata (exact top-level keys depend on producer; see §6). |
| `robustness_surface.json` | `RobustnessSurface` JSON: ESI/drift-style surfaces and globals (see §6). |
| `monte_carlo_stats.json` | Monte Carlo sampling summary and related aggregates (see §6). |

**Note:** `SweepOrchestrator` in `app/clarity/sweep_orchestrator.py` **persists** `sweep_manifest.json` only. Surfaces and Monte Carlo JSON are materialized by **metrics/surface pipelines and validation scripts** (e.g. M15 script). A run that only executes the orchestrator **without** a downstream materialization step **does not** produce the two surface files yet. For those runs, the **contract requirement** applies once the consumer runs the **full bundle** path that produces all three files.

---

## 4. Optional artifacts

The following may appear depending on **mode, pipeline, and configuration**. They are **not** guaranteed for every run:

| Leaf name | When it may appear |
|-----------|-------------------|
| `confidence_surface.json` | Rich-mode / CSI-style surfaces (M14+), e.g. M15 rich sweep. |
| `entropy_surface.json` | Rich-mode / EDM-style surfaces (M14+), e.g. M15 rich sweep. |
| `summary_hash.txt` | Optional human-readable summary bundle (M15 script). |
| Report PDFs under `clarity/report/` | Generated report export (see §5). |
| Heatmaps / plots / cache assets | Visualization or presentation outputs (see §5). |

---

## 5. Canonical vs presentation-only artifacts

### 5.1 Contract-relevant (hash / identity / parsing)

- **Required JSON** (`sweep_manifest.json`, `robustness_surface.json`, `monte_carlo_stats.json`) for a full bundle: **contract-relevant**. Consumers may depend on **presence and semantic structure** for that bundle path.
- **`confidence_surface.json` / `entropy_surface.json`** when produced: **contract-relevant** for the same bundle class (rich path), but **optional** in the sense of §4.

### 5.2 Presentation-only / derived

- **PDF reports** (e.g. clarity report PDFs served or exported under report paths): **presentation-only** and **derived**. They **do not** define run identity or contract equivalence for a sweep. They may be regenerated from JSON artifacts.
- **Visualization-only images** (e.g. static plots, demo heatmaps): **presentation-only** unless a future milestone explicitly promotes them to contract artifacts.
- **Demo case bundles** under `demo_artifacts/` are **synthetic/demo** content for the UI; they illustrate shape but are not the canonical **readiness** evidence bundle (fixtures are).

---

## 6. JSON shape expectations (core outputs)

### 6.1 `sweep_manifest.json`

**Two schema families exist in this repository (same filename):**

1. **Orchestrator manifest** (`SweepOrchestrator._write_sweep_manifest`): top-level keys include **`axes`**, **`seeds`**, **`runs`**. Each run entry includes **`axis_values`**, **`seed`**, **`manifest_hash`**. Axis names in `axes` are sorted when written.
2. **Rich aggregate manifest** (e.g. M15 script / `m15_real_ui` fixture): includes keys such as **`sweep_id`**, **`model_id`**, **`axes`**, **`seeds`**, **`results`**, **`rich_mode`**, and optional **`vram_usage`**, **`image_path`**, **`prompt`**. This is a **larger** ledger for validation and UI.

Consumers must **not** assume one fixed schema for every `sweep_manifest.json` without knowing the producer. For **M20**, the **frozen** rule is: **documented producers** above define the allowed shapes; unknown keys should be **additive** unless a breaking change is announced.

### 6.2 `robustness_surface.json`

- **Semantic** structure matches **`RobustnessSurface.to_dict()`** in `app/clarity/surfaces.py`: top-level keys **`axes`**, **`global_mean_drift`**, **`global_mean_esi`**, **`global_variance_drift`**, **`global_variance_esi`**.
- **`axes`**: array of axis objects, each with **`axis`**, **`mean_drift`**, **`mean_esi`**, **`points`**, **`variance_drift`**, **`variance_esi`**.
- **`points`**: point objects with **`axis`**, **`drift`**, **`esi`**, **`value`** (see `SurfacePoint.to_dict()`).
- **Ordering**: axis order is **alphabetical by axis name**; point values are **lexicographic by encoded value string** (see `SurfaceEngine` and `surfaces.py`).

### 6.3 `monte_carlo_stats.json`

- **Fixture / script shape** (e.g. `m15_real_ui`): top-level **`axes`** (list of axis names), **`monte_carlo`** (object with `confidence`, `entropy`, `n_samples`, `seeds`, etc.), **`total_runs`**.
- Exact nested keys may evolve **additively**; tests lock the **presence** of **`monte_carlo`**, **`axes`**, and **`total_runs`** for the canonical fixture bundle.

### 6.4 Schemas

- There is **no** separate JSON Schema file in-repo for these artifacts as of M20. **Shape** is frozen by **documentation here** + **tests** + **`to_dict()`** implementations.

---

## 7. Deterministic ordering rules

| Surface | Rule |
|---------|------|
| **JSON object keys** | **`sort_keys=True`** when using `json.dumps` / `json.dump` for scripted outputs; **`deterministic_json_dumps`** uses `sort_keys=True` (see `app/clarity/serialization.py`). |
| **`RobustnessSurface` / surface structs** | `to_dict()` builds dicts with **alphabetical key order**; axes **alphabetically**; points **lexicographically** by value string. |
| **Sweep orchestrator manifest** | `axes` dict keys sorted by axis name; `runs` list order follows `run_combinations` (deterministic Cartesian product). |
| **Monte Carlo fixture** | `axes` list and `monte_carlo.seeds` use stable ordering from producer (sorted seeds / axis names where applicable). |

---

## 8. Numeric and float serialization rules

### 8.1 `deterministic_json_dumps` (library)

- Uses Python **`json.dumps`** with **`sort_keys=True`**, **`ensure_ascii=False`** (compact or indented), **no** custom `float` encoder — i.e. **Python’s default JSON float representation** for values not pre-rounded.

### 8.2 `SweepOrchestrator` manifest

- Uses **`json.dump(..., sort_keys=True, indent=2)`** — default **`json`** float behavior (shortest round-trippable repr).

### 8.3 Surface engine numeric storage

- **`SurfaceEngine`** and **`surfaces`** document **`_round8`** — **`round(value, 8)`** — for **computed** ESI/drift and related floats stored in **`SurfacePoint`** and axis/global aggregates. This is the **explicit** precision rule for **that** computation path.

### 8.4 What to avoid claiming

- Do **not** assume a **global** “8 decimals everywhere” rule: only surfaces/metrics that **go through** `_round8` are governed by that rule. Other floats (e.g. in manifests) follow **JSON default** unless explicitly rounded elsewhere.

---

## 9. Artifact identity and reproducibility

### 9.1 Contract equivalence (M20)

- **Baseline**: **Semantic equality** of parsed JSON for contract-relevant files **after** normalizing parse (JSON parse round-trip).
- **Byte-identical** output is **optional** and **not** guaranteed across all producers (paths differ: orchestrator `json.dump` vs `deterministic_json_dumps` vs script-local `json.dumps`).
- **Where** a producer uses a **single** deterministic JSON recipe (e.g. fixed `sort_keys=True`, `indent=2`, `ensure_ascii=True` as in `m15_real_ui_sweep.py`), **byte stability** of that recipe is **testable** and used as **evidence** for that bundle.

### 9.2 Golden / checksum workflows

- Scripts may define **bundle** or **per-file** hashes (e.g. M15 `summary_hash.txt`). Those hashes are **evidence** for that workflow; **contract identity** for consumers remains **semantic JSON** unless a future milestone promotes a specific hash algorithm to a **public** guarantee.

---

## 10. Forward / backward compatibility

- **Additive** changes: new **optional** keys or files are acceptable if documented.
- **Breaking** changes: removing required keys, renaming files, changing **numeric** semantics of `RobustnessSurface`, or changing **namespace** rules **without** a version bump / readiness milestone is a **contract break**.
- **M20** does **not** introduce a version field on artifacts; consumers should rely on **commit + docs** until a later milestone adds explicit versioning if needed.

---

## 11. Test evidence / enforcement

| Topic | Location |
|-------|-----------|
| Namespace / `clarity/` paths | `backend/tests/test_boundary_contract.py` |
| Deterministic JSON helpers | `backend/tests/test_boundary_contract.py` (`TestDeterminism`), `app/clarity/serialization.py` |
| **M20 artifact contract** | `backend/tests/test_artifact_contract.py` |
| Sweep manifest structure | `backend/tests/test_sweep_orchestrator.py` |
| Fixtures | `backend/tests/fixtures/baselines/m15_real_ui/` |

---

## 12. Deferred or non-frozen surfaces

| Surface | Status |
|---------|--------|
| Single unified JSON Schema for all manifests | **Deferred** — future milestone if needed |
| Public artifact **version** field | **Deferred** |
| Byte-identical guarantee across **all** CLARITY writers | **Not frozen** — semantic contract is canonical for M20 |

---

## 13. Related documents

- [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) — output namespace and R2L consumer boundary.
- [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md) — inherited vs CLARITY-owned responsibilities.
- [`readinessplan.md`](./readinessplan.md) — Full M18–M24 program.
