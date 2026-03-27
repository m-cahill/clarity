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
| **M17** | Demo Connectivity Hardening | Netlify ↔ Render connectivity: CORS, VITE_API_BASE_URL, getBaseUrl() single source of truth; live demo fully interactive | ✅ **Closed** | `v0.0.18-m17` | 5.0 |
| **M18** | Readiness Charter & Authority Freeze | Establish `docs/readiness/` pack, authority hierarchy, readiness ledger + decisions; record M18–M24 in ledger (no portability claim) | ✅ **Closed** | not tagged | 5.0 |
| **M19** | Consumer Boundary Freeze | Freeze CLARITY consumer boundary, inherited guarantees, forbidden behaviors | ✅ **Closed** | not tagged | 5.0 |
| **M20** | Artifact Contract & Deterministic Output Freeze | Freeze artifact model, serialization, determinism, reproducibility rules | ✅ **Closed** | not tagged | 5.0 |
| **M21** | Public Surface & Invocation Contract | Single official consumer invocation path; public vs internal | ✅ **Closed** | not tagged | 5.0 |
| **M22** | Operating Manual & Honest Implementation Matrix | Operator manual + implemented vs planned vs unknown matrix | ✅ **Closed** | not tagged | 5.0 |
| **M23** | Consumer Assumptions, Compatibility Matrix & Transfer Checklist | Explicit assumptions, compatibility matrix (Supported / Unsupported / Unknown), transfer checklist | ✅ **Closed** | not tagged | 5.0 |
| **M24** | Readiness Audit, Scorecard & Portability Verdict | Final scorecard, verdict, change control | ✅ **Closed** | not tagged | 5.0 |

---

## Readiness phase (M18–M24)

**Readiness status:** **`CONDITIONALLY READY`**

The **readiness phase** (milestones **M18–M24**) is a governed execution track whose purpose is to make CLARITY **portable, governable, test-enforced, and legible** for safe use by a **consumer project** or **external repository**, with clear contracts and evidence. It does **not** add new model features, redesign the MedGemma evaluation path for capability, or perform downstream-specific integration work.

**M24 verdict:** **`CONDITIONALLY READY`** — authoritative detail, scoring, and adoption **conditions** are in [`readiness/CLARITY_READINESS_SCORECARD.md`](./readiness/CLARITY_READINESS_SCORECARD.md) §8–§9. Post-readiness change rules: [`readiness/CLARITY_CHANGE_CONTROL.md`](./readiness/CLARITY_CHANGE_CONTROL.md). Aggregate guardrail: `backend/tests/test_m24_readiness_verdict.py`.

**Authority (readiness):**

| Artifact | Role |
|----------|------|
| `docs/clarity.md` | Canonical **project ledger** and milestone record |
| `docs/readiness/` | Canonical **readiness pack** (contracts and readiness ledgers as they are frozen) |

**Pack index (M18+):**

- [`readiness/readinessplan.md`](./readiness/readinessplan.md) — Full readiness program (canonical **pack** copy)
- [`readiness/README.md`](./readiness/README.md) — Pack front door, authority order, reading order
- [`readiness/READINESS_LEDGER.md`](./readiness/READINESS_LEDGER.md) — Readiness control ledger
- [`readiness/READINESS_DECISIONS.md`](./readiness/READINESS_DECISIONS.md) — Readiness ADR-style decisions
- [`readiness/CLARITY_BOUNDARY_CONTRACT.md`](./readiness/CLARITY_BOUNDARY_CONTRACT.md) — Frozen CLARITY↔R2L consumer boundary (**M19**)
- [`readiness/CLARITY_ASSUMED_GUARANTEES.md`](./readiness/CLARITY_ASSUMED_GUARANTEES.md) — Inherited vs CLARITY-owned guarantees (**M19**)
- [`readiness/CLARITY_ARTIFACT_CONTRACT.md`](./readiness/CLARITY_ARTIFACT_CONTRACT.md) — Artifact inventory, serialization, contract identity (**M20**)
- [`readiness/CLARITY_PUBLIC_SURFACE.md`](./readiness/CLARITY_PUBLIC_SURFACE.md) — Canonical Python consumer surface (**M21**)
- [`readiness/CLARITY_OPERATING_MANUAL.md`](./readiness/CLARITY_OPERATING_MANUAL.md) — AI-agent / operator manual (**M22**)
- [`readiness/CLARITY_IMPLEMENTATION_STATUS.md`](./readiness/CLARITY_IMPLEMENTATION_STATUS.md) — Implemented / Planned / Unknown matrix (**M22**)
- [`readiness/CLARITY_CONSUMER_ASSUMPTIONS.md`](./readiness/CLARITY_CONSUMER_ASSUMPTIONS.md) — Downstream assumptions (**M23**)
- [`readiness/CLARITY_COMPATIBILITY_MATRIX.md`](./readiness/CLARITY_COMPATIBILITY_MATRIX.md) — Combination truth table (**M23**)
- [`readiness/CLARITY_TRANSFER_CHECKLIST.md`](./readiness/CLARITY_TRANSFER_CHECKLIST.md) — Transfer checklist (**M23**)
- [`readiness/CLARITY_CHANGE_CONTROL.md`](./readiness/CLARITY_CHANGE_CONTROL.md) — Post-readiness change control (**M24**)
- [`readiness/CLARITY_READINESS_SCORECARD.md`](./readiness/CLARITY_READINESS_SCORECARD.md) — Final scorecard and portability verdict (**M24**)

**Legacy note:** [`readinessplan.md`](./readinessplan.md) at `docs/` root may remain as a convenience copy; the **canonical readiness-pack** copy of the plan is **`docs/readiness/readinessplan.md`**. If both differ, resolve in favor of the pack copy and record the change in `READINESS_DECISIONS.md`.

Later readiness milestones must update **`docs/clarity.md`** and the readiness pack **whenever** readiness status or frozen documents change.

**M19 note:** The consumer boundary and assumed-guarantee split are **frozen** in the boundary contract and assumed-guarantees documents.

**M20 note:** The artifact contract and deterministic output expectations are **frozen** in `CLARITY_ARTIFACT_CONTRACT.md`.

**M21 note:** The public invocation surface is **frozen** in `CLARITY_PUBLIC_SURFACE.md` (`app.clarity.public_surface`).

**M22 note:** The operating manual and implementation-status matrix are **delivered** (`CLARITY_OPERATING_MANUAL.md`, `CLARITY_IMPLEMENTATION_STATUS.md`).

**M23 note:** Consumer assumptions, compatibility matrix (combination-level **Supported / Unsupported / Unknown**), and transfer checklist are delivered as `CLARITY_CONSUMER_ASSUMPTIONS.md`, `CLARITY_COMPATIBILITY_MATRIX.md`, and `CLARITY_TRANSFER_CHECKLIST.md`, with `test_supported_combinations.py` guardrails. Merged to `main` as [PR #24](https://github.com/m-cahill/clarity/pull/24) (merge commit `4469b2c`). Post-merge CI on `main` green (workflows `23631336064`, `23631336105`).

**M24 note:** Final scorecard ([`CLARITY_READINESS_SCORECARD.md`](./readiness/CLARITY_READINESS_SCORECARD.md)), change control ([`CLARITY_CHANGE_CONTROL.md`](./readiness/CLARITY_CHANGE_CONTROL.md)), evidence inventory ([`milestones/M24/M24_inventory.md`](./milestones/M24/M24_inventory.md)), and `test_m24_readiness_verdict.py`. **Verdict:** **`CONDITIONALLY READY`** (see scorecard §8–§9).

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
- [readiness/README.md](./readiness/README.md) — Readiness pack (canonical); see also [readiness/readinessplan.md](./readiness/readinessplan.md)
- [readiness/CLARITY_BOUNDARY_CONTRACT.md](./readiness/CLARITY_BOUNDARY_CONTRACT.md) — Frozen consumer boundary (M19)
- [readiness/CLARITY_ASSUMED_GUARANTEES.md](./readiness/CLARITY_ASSUMED_GUARANTEES.md) — Inherited vs CLARITY-owned guarantees (M19)
- [readiness/CLARITY_ARTIFACT_CONTRACT.md](./readiness/CLARITY_ARTIFACT_CONTRACT.md) — Artifact contract (M20)
- [readiness/CLARITY_PUBLIC_SURFACE.md](./readiness/CLARITY_PUBLIC_SURFACE.md) — Public surface (M21)
- [readiness/CLARITY_OPERATING_MANUAL.md](./readiness/CLARITY_OPERATING_MANUAL.md) — Operating manual (M22)
- [readiness/CLARITY_IMPLEMENTATION_STATUS.md](./readiness/CLARITY_IMPLEMENTATION_STATUS.md) — Implementation status matrix (M22)
- [readiness/CLARITY_CONSUMER_ASSUMPTIONS.md](./readiness/CLARITY_CONSUMER_ASSUMPTIONS.md) — Consumer assumptions (M23)
- [readiness/CLARITY_COMPATIBILITY_MATRIX.md](./readiness/CLARITY_COMPATIBILITY_MATRIX.md) — Compatibility / combination matrix (M23)
- [readiness/CLARITY_TRANSFER_CHECKLIST.md](./readiness/CLARITY_TRANSFER_CHECKLIST.md) — Transfer checklist (M23)
- [readiness/CLARITY_CHANGE_CONTROL.md](./readiness/CLARITY_CHANGE_CONTROL.md) — Post-readiness change control (M24)
- [readiness/CLARITY_READINESS_SCORECARD.md](./readiness/CLARITY_READINESS_SCORECARD.md) — Final readiness scorecard and verdict (M24)

---

## Readiness program: M18–M24 **complete**

**Final portability verdict:** **`CONDITIONALLY READY`** — see [`readiness/CLARITY_READINESS_SCORECARD.md`](./readiness/CLARITY_READINESS_SCORECARD.md). Adoption is **subject to conditions** C-M24-001..003 in that document. **Tag:** not tagged by default (readiness track pattern unless explicitly authorized).

**Working branch (historical):** `m24-readiness-scorecard-verdict`

**Details**: [M24_plan.md](./milestones/M24/M24_plan.md) | [M24_summary.md](./milestones/M24/M24_summary.md) | [M24_audit.md](./milestones/M24/M24_audit.md)

---

## Previous Milestone: M23 ✅ CLOSED

**Objective**: Consumer Assumptions, Compatibility Matrix & Transfer Checklist — explicit downstream assumptions; compatibility matrix as **Supported / Unsupported / Unknown** truth table; transfer checklist. *(At M23 close, M24 verdict was still pending.)*

**Merge**: [PR #24](https://github.com/m-cahill/clarity/pull/24) merged to `main` as merge commit `4469b2c7715d67387d08c21956acc73206bb53f0` (`4469b2c`). PR head implementing M23: `b138d51`.

**Tag**: not tagged

**Post-merge CI (`main` @ `4469b2c`):** CI workflow run `23631336064`, Deploy workflow run `23631336105` — **success**.

**Details**: [M23_plan.md](./milestones/M23/M23_plan.md) | [M23_audit.md](./milestones/M23/M23_audit.md) | [M23_summary.md](./milestones/M23/M23_summary.md)

**Deliverables** (summary): `CLARITY_CONSUMER_ASSUMPTIONS.md`, `CLARITY_COMPATIBILITY_MATRIX.md`, `CLARITY_TRANSFER_CHECKLIST.md`, `M23_inventory.md`, `test_supported_combinations.py`, pack/ledger updates, M24 stubs.

---

## Previous Milestone: M22 ✅ CLOSED

**Objective**: Operating Manual & Honest Implementation Matrix — AI-agent-oriented operating manual plus **Implemented / Planned / Unknown** matrix; M22 guardrail tests; pack and ledger updates. **Readiness remains `NOT READY`.**

**Merge**: [PR #23](https://github.com/m-cahill/clarity/pull/23) merged to `main` as merge commit `7f50bfca66b45c4667c8eb347ac2286406be0578` (`7f50bfc`).

**Tag**: not tagged

**Details**: [M22_plan.md](./milestones/M22/M22_plan.md) | [M22_audit.md](./milestones/M22/M22_audit.md) | [M22_summary.md](./milestones/M22/M22_summary.md)

**Deliverables** (summary): `CLARITY_OPERATING_MANUAL.md`, `CLARITY_IMPLEMENTATION_STATUS.md`, `M22_inventory.md`, `test_m22_operating_manual.py`, pack/ledger updates, M23 stubs.

---

## Previous Milestone: M21 ✅ CLOSED

**Objective**: Public Surface & Invocation Contract — Freeze **one** official consumer-facing Python surface (`app.clarity.public_surface`), explicit public vs internal policy, configuration and failure semantics, and guardrail tests; HTTP API remains non-canonical for readiness. **Readiness remains `NOT READY`.**

**Tag**: not tagged

**Details**: [M21_plan.md](./milestones/M21/M21_plan.md) | [M21_audit.md](./milestones/M21/M21_audit.md)

**Deliverables** (summary): `CLARITY_PUBLIC_SURFACE.md`, `public_surface.py`, public-surface tests, pack updates (RD-014).

---

## Previous Milestone: M20 ✅ CLOSED

**Objective**: Artifact Contract & Deterministic Output Freeze — Freeze CLARITY artifact inventory, required vs optional outputs, canonical vs presentation-only artifacts, serialization and ordering rules, and contract identity; back with guardrail tests. **Readiness remains `NOT READY`.**

**Tag**: not tagged (no git tag minted for M20 unless explicitly authorized later)

**Details**: [M20_plan.md](./milestones/M20/M20_plan.md) | [M20_audit.md](./milestones/M20/M20_audit.md)

**Deliverables**:
- ✅ `docs/readiness/CLARITY_ARTIFACT_CONTRACT.md`
- ✅ `docs/readiness/READINESS_LEDGER.md`, `docs/readiness/README.md`, `docs/readiness/READINESS_DECISIONS.md` (RD-011–RD-013)
- ✅ `docs/clarity.md` updated
- ✅ `backend/tests/test_artifact_contract.py`; `backend/tests/test_readiness_pack.py` (pack file list includes artifact contract)
- ✅ M20_summary.md, M20_audit.md; M21 seeded

---

## Previous Milestone: M19 ✅ CLOSED

**Objective**: Consumer Boundary Freeze — Freeze the CLARITY↔R2L consumer boundary, inherited guarantees vs CLARITY-owned responsibilities, and forbidden behaviors as readiness contracts; extend boundary guardrail tests. **Readiness remains `NOT READY`.**

**Tag**: not tagged (no git tag minted for M19 unless explicitly authorized later)

**Details**: [M19_plan.md](./milestones/M19/M19_plan.md) | [M19_audit.md](./milestones/M19/M19_audit.md)

**Deliverables**:
- ✅ `docs/readiness/CLARITY_BOUNDARY_CONTRACT.md`, `docs/readiness/CLARITY_ASSUMED_GUARANTEES.md`
- ✅ `docs/readiness/READINESS_LEDGER.md`, `docs/readiness/README.md`, `docs/readiness/READINESS_DECISIONS.md` (RD-008–RD-010)
- ✅ `docs/clarity.md` updated
- ✅ Boundary tests extended: `backend/tests/test_boundary_contract.py` (M19 section); `backend/tests/test_readiness_pack.py` (pack file list)
- ✅ M19_summary.md, M19_audit.md; M20 seeded

---

## Previous Milestone: M18 ✅ CLOSED

**Objective**: Readiness Charter & Authority Freeze — Establish the readiness program, canonical `docs/readiness/` pack, authority hierarchy, initial ledger and decisions, and M18–M24 roadmap in this ledger. **Readiness remains `NOT READY`.**

**Tag**: not tagged (no git tag minted for M18 unless explicitly authorized later)

**Details**: [M18_plan.md](./milestones/M18/M18_plan.md) | [M18_audit.md](./milestones/M18/M18_audit.md)

**Deliverables**:
- ✅ `docs/readiness/readinessplan.md`, `README.md`, `READINESS_LEDGER.md`, `READINESS_DECISIONS.md`
- ✅ `docs/clarity.md` updated with readiness phase and M18–M24 rows
- ✅ Lightweight guardrail: `backend/tests/test_readiness_pack.py`
- ✅ M18_summary.md, M18_audit.md; M19 seeded

---

## Previous Milestone: M17 ✅ CLOSED

**Objective**: Frontend ↔ Backend Connectivity Hardening — Resolve Netlify "Failed to fetch"; live demo fully interactive.

**Tag**: `v0.0.18-m17`

**Details**: [M17_plan.md](./milestones/M17/M17_plan.md) | [M17_audit.md](./milestones/M17/M17_audit.md)

**Notes**: getBaseUrl() single source of truth; VITE_API_BASE_URL canonical; CORS env-driven. Live validation confirmed.

---

## Previous Milestone: M16 ✅ CLOSED

**Objective**: Kaggle Submission Packaging & Competition Positioning — Convert validated system into competition-grade artifact.

**Tag**: `v0.0.17-m16`

**Details**: [M16_plan.md](./milestones/M16/M16_plan.md) | [M16_audit.md](./milestones/M16/M16_audit.md)

**Deliverables**:
- ✅ README_KAGGLE.md, EXECUTIVE_SUMMARY.md, architecture.md
- ✅ example_bundle/, M16_reproducibility_report.md, M16_manual_validation.md
- ⏳ Screenshots (user action pending)

---

## Previous Milestone: M15 ✅ CLOSED

**Objective**: Real Artifact UI Validation & Demo Hardening — Validate end-to-end system with real MedGemma artifacts rendering in UI.

**Tag**: `v0.0.16-m15`

**Details**: [M15_plan.md](./milestones/M15/M15_plan.md) | [M15_audit.md](./milestones/M15/M15_audit.md)

**Deliverables**:
- ✅ Real rich-mode sweep artifacts generated (12 runs, 2 seeds, 2 axes)
- ✅ Bundle SHA256: `fa6fdb5dbe017076fd6cdf01f28f9a7773edef551e977b18bff918e1622d3236`
- ✅ Backend API validation passed; frontend console validation (zero errors, no NaN)
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
| M17 | `v0.0.18-m17` | `cdac548` | 5.0 | 2026-02-24 |
| M18 | not tagged | `0e674fd` | 5.0 | 2026-03-26 |
| M19 | not tagged | `8187d62` | 5.0 | 2026-03-26 |
| M20 | not tagged | `975165e` | 5.0 | 2026-03-27 |
| M21 | not tagged | `975165e` | 5.0 | 2026-03-27 |
| M22 | not tagged | `7f50bfc` | 5.0 | 2026-03-27 |
| M23 | not tagged | `4469b2c` | 5.0 | 2026-03-27 |
| M24 | not tagged | _[set to `main` merge commit at PR merge]_ | 5.0 | 2026-03-26 |

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
