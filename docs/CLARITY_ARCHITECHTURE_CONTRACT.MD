## 1-Page Architecture Contract — CLARITY ↔ R2L Boundary Freeze

---

**Boundary Contract Version:** `v0.1`  
**Frozen At:** M01  
**Date:** 2026-02-20  
**Status:** ACCEPTED ✅

---

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Consumer Substrate:** R2L (deterministic micro-lab engine)  
**Contract Status:** FROZEN — immutably versioned. Changes require milestone ID + explicit diff section.

### A. Non-Negotiable Invariants (Must Remain True)

1. **Consumer-only posture:** CLARITY must not modify R2L execution semantics, schemas, or CI behavior. 
2. **Determinism preservation:** CLARITnondeterminism into the artifact pipeline; all randomness is **seed-enumerated** and **recorded**. 
3. **Additive discipline:** changes areg changes without explicit migration/rollback. (RediAI-v3 governance posture) 
4. **No artifact overwrite:** CLARITY ntates R2L output bundles. 

### B. Invocation Model (How CLARITY CM00–M02): “Black-box” invocation only**

* CLARITY triggers R2L runs via a CLI entrypoint or stable runner command.
* CLARITY does **not** import internal R2L modules beyond a documented public interface.

**Allowed in later milestones (explicitly gated):**

* Direct Python import *only* if the imported surface is declared “public/stable” and covered by a consumer contract test.

### C. Data & Artifact Contract (What CLARITY Consumes)

**Per-run R2L artifacts (input to CLARITY):**

* `manifest.json`
* `trace_pack.jsonl` (optionally includes `adapter_metadata`)
* `evaluation_record`
* `research_card`

**CLARITY outputs (must be separate name`clarity/sweep_manifest.json` (authoritative run ledger)

* `clarity/robustness_surface.json`
* `clarity/monte_carlo_stats.json`
* `clarity/report/clarity_report.pdf` (optional early)

### D. Rich Mode Policy (Adapter Optionality)

* CLARITY must work with **canonical** adapter method `generate()` (CI golden path). 
* If `generate_rich()` is available andODE=true`), CLARITY may ingest optional fields (e.g., `adapter_metadata`) **without requiring them**. 
* **No milestone may introduce a hard dode unless explicitly declared and covered by compatibility tests.

### E. Seed & Sweep Semantics (Deterministic Monte Carlo)

* Monte Carlo is implemented as **external seed enumeration**:
  `for seed in seeds: r2l.run_question(spec_with_seed)` 

* CLARITY must record in `sweep_manifest (ordered)
  
  * R2L git SHA / version
  * adapter model ID
  * rich_mode on/off
  * perturbation recipe IDs + parameter grids

### F. Security & Supply Chain Minimums ub Actions: pin third-party actions to immutable SHAs where feasible (or document exceptions). ([GitHub Docs][1])

* Secrets: Netlify/Render tokens and hooks must be stored only in GitHub Secrets; never in repo.

* Deploys: use first-party deployment mechanisms:
  
  * Netlify Deploy Previews / deploy contexts as applicable ([Netlify Docs][2])
  * Render Deploy Hooks for CI-triggered deploys ([Render][3])

### G. Boundary Guardrails (Tests/Checks that Freeze the Contract)

**Required guardrails to add by/within M00–M01:**

1. **Consumer contract test:** validate CLARITY can parse R2L `manifest.json` + `trace_pack.jsonl` schema (including absence/presence of optional fields). 
2. **No-overwrite test:** ensure CLARITY writes outputs only under `clarity/` (or configured CLARITY namespace). 
3. **Deterministic ledger test:** re-run a tiny sweep (2 seeds, 1 perturb axis) and assert stable `sweep_mg + stable metric serialization.

### H. Acceptance & Versioning

* This contract is accepted when:
  
  * checked into CTURE_CONTRACT.md`
  * referenced by `clarity.md`
  * enforced by CI checks listed above

* Any change requires:
  
  * a milestone ID
  * a diff section “Contract Changes”
  * updated guardrail(s)
