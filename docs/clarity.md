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
| **M02** | Perturbation Core | Implement deterministic image perturbation recipes | 🔄 **In Progress** | — | — |
| **M03** | R2L Invocation Harness | Add black-box R2L runner invocation + artifact ingestion | ⏳ Pending | — | — |
| **M04** | Sweep Orchestrator | Execute multi-axis perturbation sweeps | ⏳ Pending | — | — |
| **M05** | Metrics Core (ESI + Drift) | Compute ESI and justification drift metrics | ⏳ Pending | — | — |
| **M06** | Robustness Surfaces | Estimate and persist robustness surfaces | ⏳ Pending | — | — |
| **M07** | Monte Carlo Reasoning Stability | Implement multi-sample decoding + entropy metrics | ⏳ Pending | — | — |
| **M08** | Counterfactual Probe | Causal grounding probe via region masking | ⏳ Pending | — | — |
| **M09** | UI Console Skeleton | Interactive UI for configuring sweeps + viewing results | ⏳ Pending | — | — |
| **M10** | Visualization Overlays | Evidence map overlays + saliency heatmaps | ⏳ Pending | — | — |
| **M11** | Report Export | Deterministic PDF report generation | ⏳ Pending | — | — |
| **M12** | Operational Hardening | Caching, resumability, concurrency controls | ⏳ Pending | — | — |

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

---

## Key Documents

- [VISION.md](./VISION.md) — Project vision and core question
- [COMPLETE_RULES.md](./COMPLETE_RULES.md) — MedGemma Impact Challenge rules
- [CLARITY_CAPABILITY_CONTEXT.md](./CLARITY_CAPABILITY_CONTEXT.md) — R2L context and boundaries
- [CLARITY_ARCHITECHTURE_CONTRACT.MD](./CLARITY_ARCHITECHTURE_CONTRACT.MD) — Architecture freeze

---

## Current Milestone: M02

**Objective**: Implement deterministic image perturbation recipes.

**Branch**: `m02-perturbation-core`

**Details**: [M02_plan.md](./milestones/M02/M02_plan.md)

### M02 Implementation Summary

**New Files (12):**
- `backend/app/clarity/perturbations/__init__.py`
- `backend/app/clarity/perturbations/base.py` — Perturbation ABC
- `backend/app/clarity/perturbations/brightness.py`
- `backend/app/clarity/perturbations/contrast.py`
- `backend/app/clarity/perturbations/gaussian_noise.py`
- `backend/app/clarity/perturbations/blur.py`
- `backend/app/clarity/perturbations/resize.py`
- `backend/app/clarity/image_utils.py` — Canonical hashing + conversion
- `backend/app/clarity/perturbation_registry.py` — Type registry
- `backend/tests/test_perturbations.py` — 61 tests

**Key Contracts:**
- All perturbations are frozen dataclasses (immutable)
- Input: RGB, RGBA, or L mode PIL Image
- Output: Always RGB mode PIL Image
- Gaussian noise requires explicit seed (no global randomness)
- `image_sha256()` hashes canonical pixel bytes + dimensions

---

## Baseline Reference

| Milestone | Tag | Commit | Score | Date |
|-----------|-----|--------|-------|------|
| M00 | `v0.0.1-m00` | `45c5a30` | 4.2 | 2026-02-20 |
| M01 | `v0.0.2-m01` | `d8192ed` | 4.4 | 2026-02-20 |

---

## Deferred Issues Registry

| ID | Issue | Discovered | Deferred To | Tracking |
|----|-------|------------|-------------|----------|
| GOV-001 | Branch protection | M00 | Manual config | [Issue #3](https://github.com/m-cahill/clarity/issues/3) |
| SEC-001 | CORS permissive | M00 | Pre-production | — |
| SCAN-001 | No security scanning | M01 | M12 | — |

