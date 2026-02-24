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
| **M13** | MedGemma Integration | Real MedGemma inference via R2L, determinism verification, minimal sweep | ✅ **Closed** | `v0.0.14-m13` | 5.0 |
| **M14** | Rich Mode Evidence Ingestion | Token-level probabilities, CSI, EDM, confidence/entropy surfaces | ✅ **Closed** | `v0.0.15-m14` | 5.0 |
| **M15** | Real Artifact UI Validation | End-to-end validation with real MedGemma artifacts in UI | ✅ **Closed** | `v0.0.16-m15` | 5.0 |
| **M16** | Kaggle Submission Packaging | Competition-grade packaging: README, architecture, executive summary, artifact bundle, reproducibility protocol | ✅ **Closed** | `v0.0.17-m16` | 5.0 |

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

### M17 — Demo connectivity (required env)

| Where | Variable | Value |
|-------|----------|--------|
| **Netlify** | `VITE_API_BASE_URL` | `https://clarity-1sra.onrender.com` (no trailing slash) |
| **Render** | `CORS_ALLOWED_ORIGINS` | `https://majestic-dodol-25e71c.netlify.app` |

Without these, production frontend may show "Failed to fetch" when calling the backend.

---

## Key Documents

- [VISION.md](./VISION.md) — Project vision and core question
- [COMPLETE_RULES.md](./COMPLETE_RULES.md) — MedGemma Impact Challenge rules
- [CLARITY_CAPABILITY_CONTEXT.md](./CLARITY_CAPABILITY_CONTEXT.md) — R2L context and boundaries
- [CLARITY_ARCHITECHTURE_CONTRACT.MD](./CLARITY_ARCHITECHTURE_CONTRACT.MD) — Architecture freeze

---

## Current Milestone: M16 ✅ CLOSED

**Objective**: Kaggle Submission Packaging & Competition Positioning — Convert validated system into competition-grade artifact.

**Tag**: `v0.0.17-m16`

**Details**: [M16_plan.md](./milestones/M16/M16_plan.md) | [M16_audit.md](./milestones/M16/M16_audit.md)

**Notes**: Competition submission freeze. Frontend deployment issue (CORS/Failed to fetch) deferred to M17.

**Deliverables**:
- ✅ `docs/kaggle_submission/README_KAGGLE.md` — Competition README with full methodology
- ✅ `docs/kaggle_submission/EXECUTIVE_SUMMARY.md` — One-page judge summary
- ✅ `docs/kaggle_submission/architecture.md` — Four Mermaid architecture diagrams
- ✅ `docs/kaggle_submission/example_bundle/` — Canonical M15 artifacts + BUNDLE_README
- ✅ `docs/milestones/M16/M16_reproducibility_report.md` — Non-destructive protocol + hash verification
- ✅ `docs/milestones/M16/M16_manual_validation.md` — 8-check validation template
- ⏳ Screenshots (user action pending)
- ⏳ Manual UI validation (user action pending)

---

## Previous Milestone: M15 ✅ CLOSED

**Objective**: Real Artifact UI Validation & Demo Hardening — Validate end-to-end system with real MedGemma artifacts rendering in UI.

**Tag**: `v0.0.16-m15`

**Details**: [M15_plan.md](./milestones/M15/M15_plan.md) | [M15_audit.md](./milestones/M15/M15_audit.md)

**Deliverables**:
- ✅ Real rich-mode sweep artifacts generated (12 runs, 2 seeds, 2 axes)
- ✅ Bundle SHA256: `fa6fdb5dbe017076fd6cdf01f28f9a7773edef551e977b18bff918e1622d3236`
- ✅ Backend API validation passed (7 tests)
- ✅ Frontend console validation passed (zero console errors, no NaN)
- ✅ Cross-platform checksum verification fixed
- ✅ CI green, demo stable

---

## Previous Milestone: M14 ✅ CLOSED

**Objective**: Rich Mode Evidence Ingestion & Attribution Surfaces — Extract token-level probabilities, entropy, and confidence metrics for reasoning-signal stability analysis.

**Tag**: `v0.0.15-m14`

**Details**: [M14_plan.md](./milestones/M14/M14_plan.md) | [M14_audit.md](./milestones/M14/M14_audit.md)

---

## Previous Milestone: M13 ✅ CLOSED

**Objective**: MedGemma Integration & Empirical Validation — Replace synthetic adapter outputs with real MedGemma inference via R2L.

**Tag**: `v0.0.14-m13`

**Details**: [M13_plan.md](./milestones/M13/M13_plan.md) | [M13_audit.md](./milestones/M13/M13_audit.md)

**Deliverables**:
- ✅ Real MedGemma inference via `google/medgemma-4b-it` (HuggingFace)
- ✅ Determinism verified: manifest hash `01e9c46d1c18bc86...` stable across runs
- ✅ VRAM: 8.17 GB max (within 12 GB budget)
- ✅ Competition HAI-DEF requirement satisfied
- ✅ CI unchanged (synthetic path preserved)

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
| M13 | `v0.0.14-m13` | `1fe3da9` | 5.0 | 2026-02-21 |
| M14 | `v0.0.15-m14` | `c4e61c6` | 5.0 | 2026-02-22 |
| M15 | `v0.0.16-m15` | `0cb6e4e` | 5.0 | 2026-02-22 |
| M16 | `v0.0.17-m16` | _[pending]_ | 5.0 | 2026-02-22 |

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
| ARCH-001 | Rich mode evidence ingestion | M13 | M14 | `generate_rich()` + CSI/EDM metrics + confidence/entropy surfaces |

---

## M16 Corrected Artifact Evidence

*Canonical hashes supersede M15 values after M16 pre-close correction: (1) synthetic→real image fixture (CC0 PA chest X-ray), (2) chat-template prompt format, (3) bfloat16 dtype.*

| Metric | Value |
|--------|-------|
| **Bundle SHA256** | `26de75db866aafa813cb25ef63ee3c1f34e14eda0d07d7de567957d2d46a58bc` |
| **Summary Hash** | `fba587054c9f63149eba704a703fa8bcb4c5a2d2f96997857fba5c9a8d6166e6` |
| **Inference Runs** | 12 (2 axes × 3 values × 2 seeds) |
| **VRAM Max** | 9.14 GB |
| **Mean Logprob** | -0.2155304 |
| **Output Entropy** | 4.99646272 |
| **Confidence Score** | 0.80611376 |
| **Token Count** | 342 |
| **Determinism** | ✅ Verified (identical bundle SHA across 2 independent runs) |

---

## M15 Real Artifact UI Validation Evidence

| Metric | Value |
|--------|-------|
| **Bundle SHA256** | `fa6fdb5dbe017076fd6cdf01f28f9a7773edef551e977b18bff918e1622d3236` |
| **Summary Hash** | `c52ead26746d271526b05831f4b34de275fb2c620d69c85bb31a0e4cb5652fa1` |
| **Inference Runs** | 12 (2 axes × 3 values × 2 seeds) |
| **VRAM Max** | 9.71 GB |
| **Backend Tests** | 911 passed |
| **Frontend Tests** | 137 passed |
| **Console Errors** | 0 |
| **NaN Values** | 0 |
| **Cross-Platform Fix** | CRLF→LF normalization for checksum verification |

---

## M14 Rich Mode Validation Evidence

| Metric | Value |
|--------|-------|
| **Summary Hash** | `c52ead26746d271526b05831f4b34de275fb2c620d69c85bb31a0e4cb5652fa1` |
| **Bundle SHA** | `0cb6551750922165cf7391f7c75c7ccfe77ea918478f3bb24e4172d0efa44026` |
| **Mean Logprob** | -100.0 |
| **Output Entropy** | 0.0 |
| **Confidence Score** | 0.0 |
| **Token Count** | 512 |
| **Determinism** | ✅ Verified (identical hash across runs) |
| **New Unit Tests** | 36 |
| **GPU Determinism Tests** | 5 |
| **Environment Flags** | `CLARITY_REAL_MODEL`, `CLARITY_RICH_MODE`, `CLARITY_RICH_LOGITS_HASH` |

---

## M13 Empirical Validation Evidence

| Metric | Value |
|--------|-------|
| **Model ID** | `google/medgemma-4b-it` |
| **Manifest Hash** | `01e9c46d1c18bc86d007abb7308b878aa704940cd79e091faec4959788455826` |
| **VRAM Max** | 8.17 GB |
| **VRAM Budget** | 12 GB |
| **Seeds Tested** | 42, 123 |
| **Determinism** | ✅ Verified (identical hash across runs) |
| **Competition HAI-DEF** | ✅ Satisfied |
