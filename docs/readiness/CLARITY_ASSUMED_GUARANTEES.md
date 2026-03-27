# CLARITY_ASSUMED_GUARANTEES — Inherited vs owned

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M19 — Consumer Boundary Freeze |
| **Purpose** | Assumption contract: what CLARITY **inherits** from the substrate vs what it **must still prove** locally |
| **Readiness status** | **`NOT READY`** until M24 (see [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)) |

---

## 1. Purpose

Downstream projects need to know what CLARITY **does not re-validate** at the R2L layer and what remains **CLARITY’s obligation**. This document separates:

1. **Inherited guarantees** — treated as **substrate / governance** responsibility; CLARITY does not reproduce full substrate certification in this repo.
2. **CLARITY-owned responsibilities** — implemented, tested, and versioned here.
3. **Non-inherited** — must remain covered by CLARITY tests, contracts (later milestones), or explicit deferral.

---

## 2. Inherited guarantees (assumptions)

CLARITY **assumes** the following about R2L and its governance context, based on project context and upstream certification **as referenced** in [`CLARITY_CAPABILITY_CONTEXT.md`](../CLARITY_CAPABILITY_CONTEXT.md). This repository **does not** re-prove the substrate’s internal CI or Phase XV certification.

| Assumption | Meaning for CLARITY |
|------------|---------------------|
| **Deterministic single-run behavior** | For a fixed question spec and seed, a single R2L run produces a **consistent** artifact set suitable for hashing and replay **as consumed from disk**. |
| **Schema-validated substrate artifacts** | R2L outputs are **intended** to conform to declared schemas; CLARITY performs **minimal** validation (`artifact_loader`) sufficient for its ingestion—not a full duplicate of substrate schema CI. |
| **Provider-agnostic adapter contract** | Model adapters implement a stable **`generate()`** surface; optional **`generate_rich()`** is additive. CLARITY does not fork adapter internals. |
| **Substrate CI truthfulness** | CLARITY **relies** on upstream R2L/RediAI governance for substrate regressions; CLARITY’s CI enforces **CLARITY** invariants (boundary, serialization, pack docs, etc.). |

**If violated:** CLARITY’s metrics and reports may be wrong or non-reproducible even when CLARITY logic is correct. Recovery is **substrate fix + version pin**, not a CLARITY-only patch to execution semantics.

---

## 3. CLARITY-owned responsibilities (must hold here)

These are **not** inherited; CLARITY must implement, test, and maintain them:

| Area | Responsibility |
|------|------------------|
| **Perturbation recipes** | Deterministic image / input perturbations per CLARITY taxonomy. |
| **Sweep orchestration** | Multi-axis sweeps, seed loops **outside** R2L. |
| **Metrics & aggregation** | ESI, drift, entropy-related summaries, robustness surfaces, Monte Carlo stats—computed in CLARITY. |
| **Serialization stability** | Deterministic JSON (`deterministic_json_dumps`, etc.) for CLARITY outputs. |
| **Output namespace** | Writes only under **`clarity/`**; no overwriting R2L artifacts (`validate_output_path`). |
| **Boundary enforcement** | No forbidden R2L imports; CLI-based runner; artifact loading without R2L object models. |
| **Rich-mode ingestion (when enabled)** | Parsing optional trace fields; **no** hard dependency on rich fields on canonical paths. |
| **Compatibility across modes** | Canonical and rich paths both respect the same **ownership** and **parsing** rules (see boundary contract §7). |

---

## 4. Non-inherited / still-to-be-validated (explicit)

| Item | Where addressed |
|------|-----------------|
| Full **artifact contract** (required vs optional files, float rules, hash participation) | **M20** — [`readinessplan.md`](./readinessplan.md) |
| **Official public invocation surface** (CLI vs Python API for consumers) | **M21** |
| **Operating manual + honest implementation matrix** | **M22** — [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md), [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) |
| **Consumer assumptions pack, compatibility matrix, transfer checklist** | **M23** — [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md), [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md), [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) |
| **Final readiness scorecard and verdict** | **M24** |

---

## 5. Failure consequences if assumptions are violated

| Failure | Symptom | Typical response |
|---------|---------|------------------|
| Substrate non-determinism | Unstable hashes / manifests across runs | Fix upstream; record adapter + R2L version in sweep manifest |
| Invalid substrate artifacts | Loader or downstream metrics fail | Treat as **substrate** bug; may add defensive errors in CLARITY |
| CLARITY serialization drift | Golden tests / hash checks fail | Fix CLARITY serialization or document intentional change (M20+ change control) |
| Boundary violation (imports / overwrite) | AST or path tests fail | **Block release**; fix CLARITY code |

---

## 6. Review / update rules

1. Any change to **inherited** assumptions must be coordinated with **substrate** releases and recorded in [`READINESS_DECISIONS.md`](./READINESS_DECISIONS.md) when it affects readiness.
2. **CLARITY-owned** behaviors must gain or retain **tests** when modified.
3. This document must stay aligned with [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) and [`docs/clarity.md`](../clarity.md).

---

## 7. Related documents

- [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) — allowed/forbidden boundary.
- [`readinessplan.md`](./readinessplan.md) — milestone M20–M24 expectations.
