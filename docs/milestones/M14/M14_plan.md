# M14 — Rich Mode Evidence Ingestion & Attribution Surfaces

## Mode

DELTA AUDIT

**CI Trigger Note**: Testing workflow activation.

## Status

**Status:** 🔄 In Progress  
**Baseline:** `v0.0.14-m13` (Score: 5.0)  
**Competition Deadline:** February 24, 2026

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

### Phase 1 — Rich Result Dataclass (~1 hr)

* Create `rich_generation.py` module
* Define `RichGenerationResult` dataclass with:
  * `token_logprobs: list[float] | None`
  * `mean_logprob: float | None`
  * `output_entropy: float | None`
  * `confidence_score: float | None`
  * `logits_hash: str | None` (opt-in)
* Ensure canonical serialization

**Acceptance:**
* Dataclass serializes deterministically
* All fields are optional

---

### Phase 2 — Rich Runner Extension (~2-3 hrs)

* Add `generate_rich()` to `MedGemmaRunner`
* Extract logits from model output
* Compute:
  * Per-token logprobs (from logits via softmax)
  * Mean logprob
  * Output entropy
  * Confidence score
* Optional full logits hash (stream/hash in-memory)

**Acceptance:**
* Determinism test passes locally
* Same seed → identical rich result hash
* No changes to canonical `generate()` path

---

### Phase 3 — Metric Extension (~2 hrs)

* Add CSI (Confidence Stability Index) to metrics engine
* Add EDM (Entropy Drift Metric) to metrics engine
* Integrate with existing metrics computation

**Acceptance:**
* Metrics deterministic across runs
* No regression in existing ESI/drift metrics

---

### Phase 4 — Surface Extension (~2 hrs)

* Add Confidence Surface computation
* Add Entropy Surface computation
* Deterministic JSON serialization

**Acceptance:**
* Surface serialization stable
* Hash identical across repeated sweeps
* Schema backward compatible

---

### Phase 5 — Tests & Validation (~2 hrs)

* Add rich mode determinism tests
* Add surface serialization tests
* Run minimal rich sweep (2 seeds)
* Verify all hashes stable

**Acceptance:**
* All tests pass locally
* CI continues to skip rich tests (synthetic path preserved)

---

## Acceptance Criteria

| Criterion | Required |
|-----------|----------|
| Canonical `generate()` path unchanged | ✅ |
| CI green | ✅ |
| Determinism verified (summary metrics) | ✅ |
| Determinism verified (full logits, opt-in) | ✅ |
| No schema breaking change | ✅ |
| Rich path fully optional | ✅ |
| All new fields optional | ✅ |
| Float-stable serialization | ✅ |
| Score ≥ 5.0 | ✅ |

---

## Deliverables

* `rich_generation.py` (new dataclass module)
* `medgemma_runner.py` extended with `generate_rich()`
* `metrics_engine.py` extended with CSI/EDM
* `surface_engine.py` extended with confidence/entropy surfaces
* `test_rich_mode_determinism.py` (new test file)
* `M14_audit.md`
* `M14_summary.md`
* Tag: `v0.0.15-m14`

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

## Dependencies from M13

| Item | Status |
|------|--------|
| Real MedGemma inference | ✅ Integrated |
| Determinism | ✅ Verified |
| Competition HAI-DEF | ✅ Satisfied |
| CI integrity | ✅ Preserved |
| `MedGemmaRunner` module | ✅ Available |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Logits extraction breaks determinism | Test with multiple seeds, verify hash stability |
| VRAM increase from logits | Stream/hash in-memory, don't store full tensors |
| Float precision drift | Use canonical float representation (round to 1e-8) |
| Schema breaking change | All new fields optional, test backward compat |
| CI regression | Rich tests gated, synthetic path unchanged |

---

## Notes

M13 proved: "The system works."

M14 proves: "The system understands *why* it works."

This strengthens the Kaggle narrative by showing CLARITY can measure not just output stability, but confidence stability and entropy drift.
