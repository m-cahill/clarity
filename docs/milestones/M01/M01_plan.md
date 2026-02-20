# 📦 M01_plan.md

## Milestone M01 — Boundary Guardrails

**Project:** CLARITY
**Milestone:** M01 — Boundary Guardrails
**Objective:** Freeze the CLARITY ↔ R2L boundary via executable guardrails, contract enforcement, and workflow hardening.
**Baseline:** M00 tag `v0.0.1-m00`
**Mode:** DELTA AUDIT expected

---

# 1️⃣ Why M01 Exists

M00 established a full-stack skeleton with truthful CI and E2E verification.

However:

* The CLARITY ↔ R2L boundary is **documented**, not yet **enforced**
* Workflow security (SHA pinning, permissions) is deferred
* No executable guardrails prevent:

  * Artifact overwrite
  * Schema drift
  * Determinism leakage
  * Rich-mode coupling

M01 converts the architecture contract from prose into **CI-enforced invariants**.

Without M01:

* Later milestones (M02–M08) could silently weaken determinism
* R2L contract assumptions could drift
* CI trust posture would degrade

---

# 2️⃣ Scope

## ✅ In Scope

### A. Contract Formalization

* Freeze and commit:

  * `docs/CLARITY_ARCHITECHTURE_CONTRACT.MD`
* Add explicit version header:

  * `Boundary Contract v0.1`
* Reference in `clarity.md`

### B. Guardrail Tests (Backend)

Create `backend/tests/test_boundary_contract.py` with:

1. **Artifact Parse Test**

   * Load sample `manifest.json`
   * Load sample `trace_pack.jsonl`
   * Assert:

     * Optional `adapter_metadata` is allowed
     * Absence does not fail
     * Deterministic serialization preserved

2. **No-Overwrite Test**

   * Simulate CLARITY output write
   * Assert:

     * Writes only under `clarity/`
     * Never overwrites R2L artifacts

3. **Sweep Manifest Determinism Test**

   * Create minimal sweep (2 seeds, 1 perturb axis stub)
   * Serialize sweep manifest
   * Re-run
   * Assert:

     * Byte-identical output
     * Stable key ordering

These are stubs — NOT full perturbation implementation.

---

### C. R2L Invocation Posture Freeze

Add:

* `backend/app/clarity/r2l_interface.py` with:

  * A thin CLI-based invocation stub
  * Explicit prohibition of direct internal imports

Add test:

* Assert no imports from `r2l.internal.*`
* Enforced via AST inspection

---

### D. CI Hardening (Deferred from M00)

From M00 audit deferred registry:

#### 1. Pin GitHub Actions to SHAs

* Replace `@v4` etc. with commit SHAs

#### 2. Add Explicit Permissions Block

```yaml
permissions:
  contents: read
```

#### 3. Add Branch Protection Checklist Issue

If not configurable via API, open issue with exact CLI commands.

---

### E. Deterministic Serialization Utility

Add:

`backend/app/clarity/serialization.py`

Must enforce:

* sort_keys=True
* stable float formatting
* no datetime.now()
* explicit encoding

Used by sweep manifest test.

---

# 3️⃣ Out of Scope

* Perturbation logic (M02)
* Monte Carlo loops (M07)
* Metrics computation (M05)
* UI changes
* R2L internal changes
* GPU execution logic
* Database
* Deployment infra

No scope expansion allowed.

---

# 4️⃣ File Changes

## New Files

```
backend/app/clarity/__init__.py
backend/app/clarity/serialization.py
backend/app/clarity/sweep_manifest.py
backend/app/clarity/r2l_interface.py
backend/tests/test_boundary_contract.py
backend/tests/fixtures/r2l_samples/manifest.json
backend/tests/fixtures/r2l_samples/trace_pack_with_metadata.jsonl
backend/tests/fixtures/r2l_samples/trace_pack_without_metadata.jsonl
docs/milestones/M01/M01_branch_protection.md
```

## Modified Files

```
.github/workflows/ci.yml   (pin SHAs + permissions)
docs/clarity.md            (update milestone table)
docs/CLARITY_ARCHITECHTURE_CONTRACT.MD (freeze header)
```

---

# 5️⃣ Acceptance Criteria (Hard Gates)

M01 is complete only if:

### Contract Guardrails

* [ ] Parsing test passes with and without `adapter_metadata`
* [ ] No-overwrite test fails if writing outside `clarity/`
* [ ] Sweep manifest serialization is byte-identical across runs

### CI Hardening

* [ ] All actions pinned to immutable SHAs
* [ ] Workflow contains explicit `permissions:` block
* [ ] No CI regressions introduced

### Governance

* [ ] `clarity.md` milestone table updated
* [ ] Contract version declared
* [ ] All new logic ≥85% coverage

---

# 6️⃣ Guardrails Added

This milestone must introduce at least:

* One schema guardrail
* One determinism guardrail
* One boundary enforcement guardrail
* One workflow hardening guardrail

---

# 7️⃣ Expected CI Behavior

CI should:

* Stay green
* Show increased backend test count
* Maintain ≥85% coverage
* Show no matrix instability

If CI fails:

* Must root cause
* No coverage lowering allowed
* No gate weakening allowed

---

# 8️⃣ Risk Analysis

| Risk                           | Mitigation                            |
| ------------------------------ | ------------------------------------- |
| Over-coupling to R2L           | CLI-only invocation                   |
| Future schema drift            | Parse test + optional field allowance |
| Nondeterministic serialization | Stable JSON utility                   |
| Workflow drift                 | SHA pinning                           |

---

# 9️⃣ Definition of Done

M01 closes only if:

* Contract is executable
* CI hardened
* Determinism guardrails verifiable
* No new deferred HIGH items
* Audit verdict 🟢 or 🟡 with explicit deferrals

---

# 🔟 Deliverables to Produce After CI Green

* `M01_run1.md`
* `M01_audit.md`
* `M01_summary.md`
* Updated `clarity.md`
* Tag: `v0.0.2-m01`

---

# 1️⃣1️⃣ Milestone Discipline

* One capability: boundary enforcement
* No perturbation logic
* No metrics
* No UI
* No GPU features

---

# 1️⃣2️⃣ Locked Decisions

## Directory Structure

CLARITY module lives at `backend/app/clarity/` (not repo root).

## Sample Artifacts

Create compliant stub fixtures under `backend/tests/fixtures/r2l_samples/`.

## Sweep Manifest

Define minimal Pydantic `SweepManifest` model in `backend/app/clarity/sweep_manifest.py`.

## AST Import Test

Static AST scan guardrail that fails on `r2l.internal.*` imports.

## Branch Protection

Create GitHub issue with exact CLI commands (no programmatic configuration).

## SHA Pinning

Pin current latest SHAs for all actions in use.

## Serialization Rules

* `json.dumps(..., sort_keys=True, separators=(",", ":"))`
* Forbid: `datetime.now()`, `uuid4()`, unseeded `random`
* Test for byte-identical output

---

*End of M01 Plan*
