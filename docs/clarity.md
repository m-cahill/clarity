# CLARITY — Source of Truth

## Clinical Localization and Reasoning Integrity Testing

> **CLARITY** is a deterministic, GPU-accelerated evaluation instrument for measuring the robustness and evidence stability of multimodal clinical AI systems under structured perturbation sweeps.

---

## Project Overview

- **Repository**: [m-cahill/clarity](https://github.com/m-cahill/clarity)
- **License**: Apache-2.0
- **Competition**: MedGemma Impact Challenge (Kaggle)
- **Deadline**: February 24, 2026

---

## Architecture

CLARITY is layered:

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

CLARITY operates as a **pure consumer** of R2L — it never modifies R2L execution semantics.

See: [CLARITY_ARCHITECHTURE_CONTRACT.MD](./CLARITY_ARCHITECHTURE_CONTRACT.MD)

---

## Milestone Table

| Milestone | Name | Objective | Status | Tag | Score |
|-----------|------|-----------|--------|-----|-------|
| **M00** | Repo Bootstrap + E2E Proof | Establish runnable CLARITY skeleton with CI and E2E verification | ✅ **Closed** | `v0.0.1-m00` | 4.2 |
| **M01** | Boundary Guardrails | Freeze CLARITY↔R2L boundary with contract + guardrail tests | ✅ **Closed** | `v0.0.2-m01` | 4.4 |
| **M02** | Perturbation Core | Implement deterministic image perturbation recipes | ✅ **Closed** | `v0.0.3-m02` | 4.5 |
| **M03** | R2L Invocation Harness | Add black-box R2L runner invocation + artifact ingestion | ✅ **Closed** | `v0.0.4-m03` | 4.6 |
| **M04** | Sweep Orchestrator | Execute multi-axis perturbation sweeps | ✅ **Closed** | `v0.0.5-m04` | 4.7 |
| **M05** | Metrics Core (ESI + Drift) | Compute ESI and justification drift metrics | ✅ **Closed** | `v0.0.6-m05` | 4.8 |
| **M06** | Robustness Surfaces | Deterministic surface computation from metrics | ✅ **Closed** | `v0.0.7-m06` | 4.85 |
| **M07** | Gradient / Stability Estimation | Gradient estimation and stability analysis | ✅ **Closed** | `v0.0.8-m07` | 4.90 |
| **M08** | Counterfactual Probe | Causal grounding probe via region masking | ✅ **Closed** | `v0.0.9-m08` | 4.92 |
| **M09** | UI Console Skeleton | Interactive UI for counterfactual orchestration + viewing results | ✅ **Closed** | `v0.0.10-m09` | 4.94 |
| **M10** | Visualization Overlays | Evidence map overlays + saliency heatmaps | ✅ **Closed** | `v0.0.11-m10` | 4.96 |
| **M10.5** | Demo Deployment Layer | Netlify frontend + Render backend for read-only demo | ✅ **Closed** | — | 4.97 |
| **M11** | Report Export | Deterministic PDF report generation | ✅ **Closed (Deferred Item)** | `v0.0.12-m11` | 4.98 |
| **M12** | Operational Hardening | Caching, resumability, concurrency controls, security scanning, dependency discipline | ✅ **Closed** | `v0.0.13-m12` | 5.0 |
| **M13** | MedGemma Integration | Real MedGemma inference via R2L, determinism verification, minimal sweep | ⏳ **In Progress** | — | — |

---

## Database Schema

*No database schema defined yet. Will be added when persistence layer is implemented.*

---

## Migrations

*No migrations yet.*

---

## Deploy/CI Notes

- **Netlify**: Use Deploy Previews for PR visibility (frontend)
- **Render**: Use Deploy Hooks for backend deploy triggers
- **Workflow security**: Prefer pinning actions to SHAs (document exceptions)

### Live Demo Environment (M10.5)

| Component | URL |
|-----------|-----|
| Frontend | https://majestic-dodol-25e71c.netlify.app |
| Backend | https://clarity-1sra.onrender.com |

*Demo serves synthetic/precomputed artifacts only. No GPU execution in cloud.*

---

## Key Documents

- [VISION.md](./VISION.md) — Project vision and core question
- [COMPLETE_RULES.md](./COMPLETE_RULES.md) — MedGemma Impact Challenge rules
- [CLARITY_CAPABILITY_CONTEXT.md](./CLARITY_CAPABILITY_CONTEXT.md) — R2L context and boundaries
- [CLARITY_ARCHITECHTURE_CONTRACT.MD](./CLARITY_ARCHITECHTURE_CONTRACT.MD) — Architecture freeze

---

## Current Milestone: M13 ⏳ IN PROGRESS

**Objective**: MedGemma Integration & Empirical Validation — Replace synthetic adapter outputs with real MedGemma inference via R2L.

**Branch**: `m13-medgemma-integration`

**Details**: [M13_plan.md](./milestones/M13/M13_plan.md)

**Scope**:
- Wire `google/medgemma-4b` via HuggingFace Transformers
- Canonical `generate()` only (no rich mode)
- 1 image, 2 seeds, 1 perturbation axis (minimal sweep)
- Determinism regression test gated by `CLARITY_REAL_MODEL=true`
- CI unchanged (synthetic path preserved)

---

## Previous Milestone: M12 ✅ CLOSED

**Objective**: Operational Hardening — Caching, resumability, concurrency controls, security scanning, dependency discipline.

**Status**: ✅ Merged and tagged `v0.0.13-m12`

**Details**: [M12_plan.md](./milestones/M12/M12_plan.md)

**Closed Items**:
- COV-002: Frontend branch coverage restored to 87.39% (≥85% threshold)
- DEP-001: Deterministic lockfile (`requirements.lock` with pip-compile hashes)
- SCAN-001: Security scanning (pip-audit + npm audit) enforced in CI

---

## Baseline Reference

| Milestone | Tag | Commit | Score | Date |
|-----------|-----|--------|-------|------|
| M00 | `v0.0.1-m00` | `45c5a30` | 4.2 | 2026-02-20 |
| M01 | `v0.0.2-m01` | `d8192ed` | 4.4 | 2026-02-20 |
| M02 | `v0.0.3-m02` | `bc87cc5` | 4.5 | 2026-02-20 |
| M03 | `v0.0.4-m03` | `d6fb692` | 4.6 | 2026-02-20 |
| M04 | `v0.0.5-m04` | `0b79078` | 4.7 | 2026-02-20 |
| M05 | `v0.0.6-m05` | `b0f9413` | 4.8 | 2026-02-20 |
| M06 | `v0.0.7-m06` | `0d3ba66` | 4.85 | 2026-02-20 |
| M07 | `v0.0.8-m07` | `976412a` | 4.90 | 2026-02-20 |
| M08 | `v0.0.9-m08` | `f92e1c5` | 4.92 | 2026-02-20 |
| M09 | `v0.0.10-m09` | `0c0180f` | 4.94 | 2026-02-20 |
| M10 | `v0.0.11-m10` | `92b3959` | 4.96 | 2026-02-20 |
| M10.5 | — | `330dac7` | 4.97 | 2026-02-21 |
| M11 | `v0.0.12-m11` | `c5d740a` | 4.98 | 2026-02-21 |
| M12 | `v0.0.13-m12` | `d51f195` | 5.0 | 2026-02-21 |

---

## Deferred Issues Registry

| ID | Issue | Discovered | Deferred To | Tracking |
|----|-------|------------|-------------|----------|
| GOV-001 | Branch protection | M00 | Manual config | [Issue #3](https://github.com/m-cahill/clarity/issues/3) |
| SEC-001 | CORS permissive (partially addressed M12) | M00 | Pre-production | CORS tightened in M12; full lockdown deferred to production |

### Resolved Issues

| ID | Issue | Discovered | Resolved | Evidence |
|----|-------|------------|----------|----------|
| INT-001 | Real sweep → metrics → surface → gradient integration | M05 | M07 | `test_gradient_engine.py::TestINT001RealSweepIntegration` |
| CF-002 | Actual counterfactual sweeps orchestration | M08 | M09 | `CounterfactualOrchestrator` + `POST /counterfactual/run` endpoint |
| CF-001 | Evidence-map-derived regions | M08 | M10 | `evidence_overlay.py::extract_regions_from_heatmap` + BFS region extraction |
| SCAN-001 | No security scanning | M01 | M12 | `pip-audit` + `npm audit` CI jobs in `.github/workflows/ci.yml` |
| DEP-001 | No dependency lockfile | M02 | M12 | `requirements.lock` with pip-compile hashes, lockfile-check CI job |
| COV-002 | Frontend branch coverage reduced 85% → 80% | M11 | M12 | Coverage restored to 87.39%; `downloadUtils.ts` refactor + 27 tests |
