# M16 — Kaggle Submission Packaging & Competition Positioning

## Milestone Mode

**DELTA AUDIT — Packaging Only**

No architectural changes.
No model changes.
No UI changes.
No metric expansion.

This is presentation, reproducibility, and submission hardening.

---

## Objective

Prepare CLARITY for the **MedGemma Impact Challenge submission** by:

1. Packaging reproducibility instructions
2. Producing clean competition documentation
3. Creating submission-ready artifact bundle
4. Capturing visual evidence
5. Hardening demo narrative
6. Verifying full reproducibility from scratch

---

## Non-Negotiable Guardrails

* ❌ No changes to R2L
* ❌ No inference logic modifications
* ❌ No UI feature additions
* ❌ No new metrics
* ❌ No performance tuning
* ❌ No dependency upgrades
* ❌ No schema changes

Only packaging, docs, and verification.

---

## Locked Decisions

| Decision | Resolution |
|----------|------------|
| Cold start | Write protocol + verified hashes only; no destructive cache purge |
| Screenshots | Captured manually by user; compressed and organized by agent |
| Manual UI validation | User runs checklist; agent produces template |
| Artifact bundle source | `backend/tests/fixtures/baselines/m15_real_ui/` (canonical baseline) |
| Execution order | Docs first (Phase 2, 5, 7, 4, 8), then Phase 3, 6, 1 |

---

## Phase 1 — Reproducibility Validation (Non-Destructive Protocol)

**Deliverable**: `docs/milestones/M16/M16_reproducibility_report.md`

Write a documented reproducibility protocol referencing verified M15 hashes.
Include: OS, Python version, CUDA version, VRAM usage, exact commands, expected SHA outputs.
No HF cache purge required — determinism was proven twice in M15.

---

## Phase 2 — Kaggle Competition README

**Deliverable**: `docs/kaggle_submission/README_KAGGLE.md`

Sections:
1. Problem Statement
2. Methodology
3. Determinism Strategy
4. Evidence Stability Concept
5. Reproducibility Instructions
6. Demo Link

---

## Phase 3 — Visual Evidence Capture

**Deliverable**: `docs/kaggle_submission/screenshots/` (max 5 images, ≤1200px wide)

Captures (manual, by user):
1. UI console with real artifact loaded
2. Confidence surface
3. Entropy surface
4. Counterfactual mask interaction
5. JSON metrics view

---

## Phase 4 — Example Artifact Bundle

**Source**: `backend/tests/fixtures/baselines/m15_real_ui/`

**Deliverable**: `docs/kaggle_submission/example_bundle/`

Include:
- `sweep_manifest.json`
- `robustness_surface.json`
- `confidence_surface.json`
- `entropy_surface.json`
- `monte_carlo_stats.json`
- `BUNDLE_README.md`

Exclude: large intermediate tensors, redundant files.

---

## Phase 5 — Architecture Diagram

**Deliverable**: `docs/kaggle_submission/architecture.md`

Mermaid diagram. GitHub-renderable.

---

## Phase 6 — Final Manual UI Validation

**Deliverable**: `docs/milestones/M16/M16_manual_validation.md`

Template produced by agent. User executes and confirms.

Checklist:
- Load real artifact
- Toggle seeds
- Toggle axes
- Run counterfactual
- Export report
- Refresh page
- Load synthetic case
- Resize browser

Pass criteria: no console errors, no NaN, no UI flicker, no hydration mismatch.

---

## Phase 7 — Kaggle Submission Executive Summary

**Deliverable**: `docs/kaggle_submission/EXECUTIVE_SUMMARY.md`

One-page, four-paragraph executive summary. Confident, technical, restrained.

---

## Phase 8 — Governance Close

**Deliverables**:
- `M16_plan.md` ✅
- `M16_toolcalls.md` ✅
- `M16_run1.md`
- `M16_audit.md`
- `M16_summary.md`

**Updates**:
- `docs/clarity.md` — add M16 milestone row, tag `v0.0.17-m16`, score 5.0

---

## Acceptance Criteria

| Requirement | Must Pass |
|-------------|-----------|
| Reproducibility protocol written | ✅ |
| Hash reference complete | ✅ |
| README complete | ✅ |
| Example bundle clean | ✅ |
| Screenshots captured | User action |
| Manual validation clean | User action |
| CI green | ✅ (inherited from M15) |
| No architectural drift | ✅ |

---

## Definition of Done

M16 is complete when a Kaggle judge can:

* Read the README and understand the method
* Reproduce the hashes from the protocol
* Inspect the example artifact bundle
* View the live demo

Without needing to read internal milestone history.
