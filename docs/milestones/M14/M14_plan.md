# M14 — Rich Mode Evidence Ingestion & Attribution Surfaces

## Mode

DELTA AUDIT

## Status

**Status:** 🔄 In Progress (CI Green)  
**Baseline:** `v0.0.14-m13` (Score: 5.0)  
**Competition Deadline:** February 24, 2026
**PR:** [#17](https://github.com/m-cahill/clarity/pull/17)

---

## Objective

Enable optional ingestion of `generate_rich()` signals from MedGemma and extend CLARITY's robustness instrumentation to incorporate:

* Token-level probabilities (logprobs)
* Logits-based confidence
* Justification entropy metrics

**Without:**

* Breaking canonical `generate()` path
* Modifying R2L semantics
* Introducing nondeterminism
* Weakening CI

---

## Locked Decisions

| Question | Answer |
|----------|--------|
| Milestone choice | ✅ Option A: Rich Mode Evidence Ingestion |
| Attention proxy scope | ✅ Deferred entirely — logprobs/confidence/entropy only |
| Surface visualization | ✅ Artifacts only (JSON) — no UI integration |
| Determinism verification | ✅ Option (c): Summary metrics hash default, full logits hash opt-in |
| Environment gating | ✅ Both flags required: `CLARITY_REAL_MODEL=true` + `CLARITY_RICH_MODE=true` |

---

## Scope

### In Scope

1. **Extend `MedGemmaRunner`:**
   * Add `generate_rich()` method (optional)
   * Extract: logits, per-token logprobs, mean confidence, output entropy
   * Return structured `RichGenerationResult` dataclass

2. **New dataclass module:**
   * `rich_generation.py` with `RichGenerationResult`
   * Optional fields: `token_logprobs`, `mean_logprob`, `output_entropy`, `confidence_score`
   * Full logits hash (opt-in via `CLARITY_RICH_LOGITS_HASH=true`)

3. **Extend Metrics Core:**
   * CSI (Confidence Stability Index)
   * EDM (Entropy Drift Metric)

4. **Extend Robustness Surfaces:**
   * Confidence Surface (JSON artifact)
   * Entropy Surface (JSON artifact)
   * Deterministic serialization (canonically ordered, float-stable)

5. **Determinism Tests:**
   * Same seed → identical summary metrics hash
   * Same seed → identical full logits hash (when enabled)
   * Surfaces serialize deterministically

6. **Environment Gating:**
   * `CLARITY_REAL_MODEL=true` — required for real model
   * `CLARITY_RICH_MODE=true` — required for rich output
   * `CLARITY_RICH_LOGITS_HASH=true` — optional full logits hash

### Out of Scope

| Item | Reason |
|------|--------|
| Attention weights extraction | Scope discipline; deferred |
| Attention visualization | Scope discipline; deferred |
| UI console changes | Artifacts-only approach locked |
| Fine-tuning | Not permitted by competition rules |
| Beam-search / stochastic decoding | Determinism constraint |
| Multi-axis sweep expansion | Separate milestone |
| Cloud GPU execution | Local GPU only |
| CI GPU requirements | CI remains synthetic |

---

## Guardrails

### Contract

Per architecture contract:

* Rich mode must remain **optional**
* Canonical `generate()` must remain **default**
* No hard dependency on rich outputs
* CLARITY must not modify R2L

### CI Discipline

* CI synthetic path **unchanged**
* Rich tests gated behind:
  ```
  CLARITY_REAL_MODEL=true
  CLARITY_RICH_MODE=true
  ```

### Determinism Enforcement

* Summary metrics hash must match across runs (default)
* Full logits tensor SHA must match (opt-in with `CLARITY_RICH_LOGITS_HASH=true`)
* Entropy values must match to 1e-8 precision
* Surfaces must serialize deterministically

### Schema Compatibility

* All new fields are **optional**
* No breaking changes to existing artifact schemas
* Canonically ordered JSON serialization
* Float-stable representation

---

## Execution Phases

### Phase 1 — Rich Result Dataclass ✅

* Created `rich_generation.py` module
* Defined `RichGenerationResult` and `RichMetricsSummary` dataclasses
* Implemented computation functions: `compute_entropy`, `compute_mean_logprob`, etc.
* Ensured canonical serialization

### Phase 2 — Rich Runner Extension ✅

* Added `generate_rich()` to `MedGemmaRunner`
* Extracts logits from model output
* Computes per-token logprobs, mean logprob, output entropy, confidence score
* Optional full logits hash (stream/hash in-memory)

### Phase 3 — Metric Extension ✅

* Added `CSIMetric` (Confidence Stability Index)
* Added `EDMMetric` (Entropy Drift Metric)
* Added helper functions for extraction and computation

### Phase 4 — Surface Extension ✅

* Added `ConfidenceSurface` and `ConfidenceSurfacePoint`
* Added `EntropySurface` and `EntropySurfacePoint`
* Added `RichSurfaces` aggregate structure
* Deterministic JSON serialization

### Phase 5 — Tests & Validation ✅

* Created `test_rich_mode_determinism.py` (GPU-gated tests)
* Created `test_rich_generation_unit.py` (36 CI-runnable unit tests)
* All tests passing

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Canonical `generate()` path unchanged | ✅ |
| CI green | ✅ (Run 22266143038) |
| Determinism verified (summary metrics) | ✅ (via unit tests) |
| No schema breaking change | ✅ |
| Rich path fully optional | ✅ |
| All new fields optional | ✅ |
| Float-stable serialization | ✅ |

---

## Deliverables

| Deliverable | Status |
|-------------|--------|
| `rich_generation.py` (new dataclass module) | ✅ |
| `medgemma_runner.py` extended with `generate_rich()` | ✅ |
| `metrics.py` extended with CSI/EDM | ✅ |
| `surfaces.py` extended with confidence/entropy surfaces | ✅ |
| `test_rich_generation_unit.py` (36 tests) | ✅ |
| `test_rich_mode_determinism.py` (GPU-gated) | ✅ |
| PR #17 created | ✅ |
| CI green | ✅ |
| `M14_audit.md` | ⏳ Pending |
| `M14_summary.md` | ⏳ Pending |
| Tag: `v0.0.15-m14` | ⏳ Awaiting merge |

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLARITY_REAL_MODEL` | Enable real MedGemma model | `false` |
| `CLARITY_RICH_MODE` | Enable rich output extraction | `false` |
| `CLARITY_RICH_LOGITS_HASH` | Enable full logits tensor hashing | `false` |

Rich mode requires: `CLARITY_REAL_MODEL=true` AND `CLARITY_RICH_MODE=true`

Full logits hash requires all three flags set to `true`.

---

## Files Changed

| Category | Count |
|----------|-------|
| New modules | 3 (`rich_generation.py`, `test_rich_generation_unit.py`, `test_rich_mode_determinism.py`) |
| Modified modules | 4 (`medgemma_runner.py`, `metrics.py`, `surfaces.py`, `__init__.py`) |
| Lines added | ~2494 |
| Lines removed | ~7 |

---

## Notes

M13 proved: "The system works."

M14 proves: "The system understands *why* it works."

This strengthens the Kaggle narrative by showing CLARITY can measure not just output stability, but confidence stability and entropy drift.
