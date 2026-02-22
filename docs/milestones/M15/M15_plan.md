# M15 — Real Artifact UI Validation & Demo Hardening

## Mode

DELTA AUDIT

## Objective

Validate that CLARITY's **real MedGemma + rich-mode artifacts** render correctly in the UI console without regressions, schema drift, or runtime instability.

This milestone does **not** expand capability.

It validates that the full stack works with:

* Real sweep artifacts
* Real rich-mode metrics (CSI / EDM)
* Real confidence & entropy surfaces
* Real deterministic bundle hashes

---

## Why This Milestone Exists

M13 proved:

> Real inference works.

M14 proved:

> Rich reasoning signals are deterministic.

M15 proves:

> The full system (GPU → backend → artifacts → frontend) works end-to-end with real data.

This is required before Kaggle submission confidence.

---

# Scope

## In Scope

1. Generate real rich-mode sweep artifacts for UI testing
2. Store deterministic baseline artifacts
3. Load artifacts into frontend demo environment
4. Validate rendering of:

   * Robustness surfaces
   * Confidence surfaces
   * Entropy surfaces
   * Counterfactual overlays
5. Verify no UI crashes, null refs, NaNs, or console errors
6. Document verification evidence

---

## Out of Scope

* Attention extraction
* UI redesign
* New metrics
* Multi-image dataset expansion
* Production deployment changes
* Performance optimization

This is validation only.

---

# Guardrails

* No modification of R2L semantics
* No workflow changes
* No new dependencies
* No schema breaking changes
* No refactors beyond what's required for compatibility
* Maintain synthetic path in CI

---

# Execution Phases

---

## Phase 1 — Real Artifact Generation (1–2 hrs)

### Action

Run a slightly expanded sweep:

* 1 image
* 2 seeds
* 2 perturbation axes
* Rich mode enabled

Environment:

```
CLARITY_REAL_MODEL=true
CLARITY_RICH_MODE=true
```

### Store Artifacts In:

```
backend/tests/fixtures/baselines/m15_real_ui/
```

Artifacts required:

* sweep_manifest.json
* robustness_surface.json
* confidence_surface.json
* entropy_surface.json
* monte_carlo_stats.json
* summary_hash.txt

### Determinism Verification

Run sweep twice.

Verify:

* Manifest SHA identical
* Bundle SHA identical
* Confidence surface JSON identical
* Entropy surface JSON identical

Acceptance:

* Hash stable across two runs

---

## Phase 2 — Backend API Validation (1 hr)

### Action

Load new artifact set through backend API routes:

Verify endpoints return:

* Correct schema
* No missing fields
* No 500 errors
* No serialization float drift

Acceptance:

* All endpoints return 200
* No JSON schema mismatches
* No unexpected null values

---

## Phase 3 — Frontend Console Validation (1–2 hrs)

Use the real artifact bundle in:

* Local dev environment

### Validate:

* Surfaces render
* No NaN displayed
* No broken heatmaps
* Counterfactual UI still functions
* Rich metrics visible in JSON export

### Check:

* Browser console errors
* React warnings
* TypeScript runtime warnings

Acceptance:

* Zero console errors
* All UI components render
* No undefined property crashes
* No layout shifts

---

## Phase 4 — SKIPPED (Per Locked Decision)

Stress sanity testing skipped for deadline discipline.

---

## Phase 5 — Governance Close

Deliver:

* M15_run1.md (UI validation log)
* M15_audit.md
* M15_summary.md
* Update clarity.md
* Tag `v0.0.16-m15`

Expected Score: 5.0 maintained

---

# Acceptance Criteria

| Criterion                     | Required |
| ----------------------------- | -------- |
| Real rich artifacts generated | ✅        |
| Determinism re-verified       | ✅        |
| Backend endpoints stable      | ✅        |
| UI renders real surfaces      | ✅        |
| No console errors             | ✅        |
| No schema changes             | ✅        |
| CI green                      | ✅        |

---

# Risks

| Risk                                     | Mitigation                       |
| ---------------------------------------- | -------------------------------- |
| NaN rendering                            | Clamp values backend-side        |
| Float precision display issues           | Format to fixed decimals         |
| UI expecting synthetic shape             | Validate schema before rendering |
| Demo environment caching stale artifacts | Force cache bust                 |

---

# Deliverables

* Real artifact baseline folder
* Determinism verification evidence
* UI screenshot evidence (local only, not committed)
* M15_audit.md
* M15_summary.md
* clarity.md updated
* Tag: `v0.0.16-m15`

---

# Locked Decisions (M15)

| Decision | Answer |
|----------|--------|
| Enable `CLARITY_RICH_LOGITS_HASH`? | NO |
| Update deployed demo with real artifacts? | NO — local validation only |
| Execute Phase 4 stress testing? | NO — skipped |
| Implement UI-001 surface visualization? | NO — verify compatibility only |
| Commit screenshot binaries? | NO — document in audit only |

---

# Strategic Position After M15

After M15:

CLARITY will be:

* Deterministic
* Evidence-aware
* Empirically validated
* UI-validated
* Demo-stable
* Competition-ready

At that point, only Kaggle packaging remains.
