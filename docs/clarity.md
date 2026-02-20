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

| Milestone | Name | Objective | Status |
|-----------|------|-----------|--------|
| **M00** | Repo Bootstrap + E2E Proof | Establish runnable CLARITY skeleton with CI and E2E verification | 🔄 In Progress |
| **M01** | Boundary Guardrails | Freeze CLARITY↔R2L boundary with contract + guardrail tests | ⏳ Pending |
| **M02** | Perturbation Core | Implement deterministic image perturbation recipes | ⏳ Pending |
| **M03** | R2L Invocation Harness | Add black-box R2L runner invocation + artifact ingestion | ⏳ Pending |
| **M04** | Sweep Orchestrator | Execute multi-axis perturbation sweeps | ⏳ Pending |
| **M05** | Metrics Core (ESI + Drift) | Compute ESI and justification drift metrics | ⏳ Pending |
| **M06** | Robustness Surfaces | Estimate and persist robustness surfaces | ⏳ Pending |
| **M07** | Monte Carlo Reasoning Stability | Implement multi-sample decoding + entropy metrics | ⏳ Pending |
| **M08** | Counterfactual Probe | Causal grounding probe via region masking | ⏳ Pending |
| **M09** | UI Console Skeleton | Interactive UI for configuring sweeps + viewing results | ⏳ Pending |
| **M10** | Visualization Overlays | Evidence map overlays + saliency heatmaps | ⏳ Pending |
| **M11** | Report Export | Deterministic PDF report generation | ⏳ Pending |
| **M12** | Operational Hardening | Caching, resumability, concurrency controls | ⏳ Pending |

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

## Current Milestone: M00

**Objective**: Establish a full-stack CLARITY skeleton with backend, frontend, CI, and verified E2E path.

**Success Criteria**: Frontend request successfully reaches backend `/health` in CI and passes E2E tests.

**Branch**: `m00-bootstrap`

**Details**: [M00_plan.md](./milestones/M00/M00_plan.md)

