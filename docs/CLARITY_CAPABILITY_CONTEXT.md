# CLARITY Capability Context

### Built on R2L + RediAI-v3 Governance

---

# 1. Purpose of This Document

This document defines the architectural, contractual, and governance context required for CLARITY to operate as a **pure consumer** of:

* R2L (deterministic micro-lab engine)
* RediAI-v3 governance model

CLARITY must not modify R2L.
CLARITY must not weaken Phase XV invariants.
CLARITY must operate as an external evaluation instrument.

---

# 2. R2L Context (Post-M22 State)

R2L is a deterministic execution engine with the following guarantees:

## 2.1 Core Guarantees (Phase XV Certified)

R2L guarantees:

* Deterministic execution: same `(prompt, seed)` → identical artifact bundle hash
* Schema-validated artifacts
* Provider-agnostic adapter contract
* CI-verified determinism enforcement
* Single certification verdict per run
* Backward compatibility across additive milestones

All of the above are confirmed in M22 audit .

CLARITY must treat these guarantees as immutable.

---

## 2.2 R2L Execution Model

R2L executes:

```
QuestionSpec
   ↓
Runner
   ↓
ModelAdapter.generate() OR generate_rich()
   ↓
Artifact bundle
```

Each run produces:

* `manifest.json`
* `trace_pack.jsonl`
* `evaluation_record`
* `research_card`
* bundle SHA256

CLARITY consumes these artifacts.

---

## 2.3 Adapter Contract (Post-M22)

### Canonical Method (CI Path)

```python
def generate(self, prompt: str, *, seed: int = 0) -> str
```

* Must be deterministic
* Used by CI golden path
* Immutable contract

### Optional Rich Method (M22)

```python
def generate_rich(self, prompt: str, *, seed: int = 0) -> AdapterResponse
```

Where:

```python
class AdapterResponse(TypedDict, total=False):
    text: str
    logits: List[float]
    attention: List[List[float]]
    tokens: List[str]
    metadata: dict[str, Any]
```

Properties:

* Fully optional
* Backward compatible
* Deterministic for same `(prompt, seed)`
* Enabled via `R2L_RICH_MODE=true`

Confirmed in M22 summary .

---

## 2.4 Trace Pack Extension

`trace_pack.jsonl` now supports optional:

```json
"adapter_metadata": { ... }
```

* Optional field
* Additive schema
* Backward compatible
* Deterministically serialized

CLARITY may consume this field if present.

---

## 2.5 What R2L Does NOT Provide

R2L does not provide:

* Perturbation generation
* Monte Carlo orchestration
* Parameter grid sweeps
* Robustness surfaces
* Saliency maps
* ESI computation
* Aggregation logic
* Visualization
* Reporting

Those belong entirely to CLARITY.

---

# 3. CLARITY Responsibility Boundary

CLARITY is responsible for:

* Perturbation taxonomy

* Parameter grid generation

* Monte Carlo loop orchestration

* External looping over R2L runs

* Aggregating artifacts

* Computing:
  
  * ESI
  * Robustness surfaces
  * Justification drift
  * Entropy metrics

* Counterfactual reconstruction

* Visualization layer

* Report generation

* UI console

CLARITY must never:

* Modify R2L execution semantics
* Inject orchestration into R2L runner
* Add perturbation logic into R2L
* Modify CI behavior in R2L

---

# 4. Monte Carlo Semantics

Monte Carlo must be implemented as:

```
for seed in seeds:
    r2l.run_question(spec_with_seed)
```

R2L remains single-execution deterministic.

CLARITY performs statistical aggregation externally.

---

# 5. GPU Responsibilities

R2L is GPU-agnostic.

GPU execution occurs entirely within:

* PhiAdapter
* MedGemmaAdapter
* Any future model adapters

CLARITY may:

* Batch QuestionSpecs externally
* Parallelize R2L invocations
* Schedule GPU usage externally

CLARITY must not modify adapter internals.

---

# 6. Artifact Flow Model

Per-run artifacts:

```
R2L Run Artifacts
├── manifest.json
├── trace_pack.jsonl
├── evaluation_record
└── research_card
```

CLARITY artifacts (external):

```
clarity/
├── sweep_manifest.json
├── robustness_surface.json
├── monte_carlo_stats.json
├── saliency_maps/
├── clarity_report.pdf
└── visualization_assets/
```

CLARITY must never overwrite R2L artifacts.

---

# 7. RediAI-v3 Governance Context

CLARITY should adopt the following RediAI-v3 principles:

## 7.1 Additive Discipline

* No breaking changes
* No invariant weakening
* Explicit milestone closures
* CI-enforced quality gates

## 7.2 Determinism First

* Seed-controlled sampling
* Stable float serialization
* Stable metric computation
* Reproducible sweep manifests

## 7.3 One Capability per Milestone

Avoid multi-feature milestones.

Examples:

* C01 — Perturbation Core
* C02 — Monte Carlo Engine
* C03 — ESI Computation
* C04 — Robustness Surface Estimation
* C05 — Counterfactual Probe
* C06 — UI Console
* C07 — Report Export

---

# 8. Versioning Discipline

CLARITY should record:

* R2L version used
* Git SHA of R2L
* Adapter model ID
* Execution mode (rich_mode true/false)

This ensures full reproducibility.

---

# 9. Invariants That Must Remain True

CLARITY must never:

* Break R2L determinism
* Introduce nondeterministic artifact merging
* Alter R2L schemas
* Couple R2L changes to CLARITY logic
* Require R2L to support perturbations

---

# 10. Architectural Summary

Layering:

```
RediAI-v3 Governance
        ↓
R2L (Deterministic Micro-Lab Engine)
        ↓
CLARITY (Robustness & Integrity Instrument)
        ↓
Model Adapter (GPU-aware)
        ↓
RTX 5090
```

CLARITY is:

* A consumer
* A statistical aggregation engine
* A visualization layer
* A reporting system

R2L remains:

* Deterministic execution substrate
* Artifact certifier
* Adapter boundary enforcer

---

# 11. Strategic Positioning

This separation allows you to state:

> CLARITY is built on a separately certified deterministic micro-lab engine (R2L), extended via additive adapter richness (M22), while preserving all Phase XV invariants.

That is strong — for Kaggle and for Upwork.
