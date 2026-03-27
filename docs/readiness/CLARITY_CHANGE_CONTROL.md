# CLARITY_CHANGE_CONTROL — Post-readiness change rules (M24)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M24 — Readiness Audit, Scorecard & Portability Verdict |
| **Authority** | Governs changes **after** the M24 scorecard verdict; subordinate to [`docs/clarity.md`](../clarity.md) and the frozen pack |
| **Applies when** | Any merge to `main` that touches contract surfaces listed below, or any release/adoption claim |

---

## 1. Purpose

Define **what may change freely**, what is **contract-affecting**, and what requires a **new readiness milestone** or **re-readiness review** so that downstream adoption does not silently drift from [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) and the frozen pack.

This document is **CLARITY-specific**. Generic policy boilerplate is intentionally avoided.

---

## 2. Authority and scope

| Layer | Role |
|-------|------|
| **`docs/clarity.md`** | Canonical **project** ledger; milestone and phase record |
| **`docs/readiness/`** | Canonical **readiness** contracts, ledger, scorecard, and this file |
| **Code + tests** | Executable truth; must stay aligned with §4 triggers when those files change |

**In scope:** Changes that affect the CLARITY↔R2L **consumer** posture, **artifact** shapes or determinism, **`app.clarity.public_surface`**, or **consumer-kit** truth (assumptions, compatibility matrix, transfer checklist).

**Out of scope:** Downstream repositories’ own code; R2L execution semantics (CLARITY must remain a consumer — see [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md)).

---

## 3. Frozen contract surfaces (reference)

These documents define **triggers** for §5. A change that contradicts them, narrows guarantees without documentation, or requires consumers to behave differently is **contract-affecting**.

| Surface | Document | What must not drift silently |
|---------|----------|------------------------------|
| **CLARITY↔R2L boundary** | [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) | Consumer-only posture; forbidden imports; output namespace; black-box invocation expectations |
| **Inherited vs owned guarantees** | [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md) | What CLARITY inherits from substrate vs what it must test itself |
| **Artifacts & determinism** | [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) | Required/optional artifacts; JSON semantics; `sweep_manifest.json` **producer-specific** shapes (§6.1); hash-participating vs presentation-only |
| **Public API** | [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) + `app/clarity/public_surface.py` | `PUBLIC_SURFACE_SYMBOLS` / `__all__`; canonical import path; HTTP non-canonical for readiness |
| **Operator truth** | [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md) | Documented pipeline, env gates, debugging discipline |
| **Honest implementation map** | [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) | Implemented / Planned / Unknown — no silent upgrades of Unknown → Supported |
| **Consumer kit** | [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md), [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md), [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) | Assumption set, combination truth table, adoption steps |

---

## 4. What counts as contract-affecting

Unless proven otherwise by inspection, treat the following as **contract-affecting**:

1. **Boundary:** Any change to how CLARITY invokes R2L, what substrate artifacts it consumes, or what it is forbidden to do per [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md).
2. **Artifacts:** Any change to required/optional outputs, JSON key semantics, ordering rules, float serialization, or the **`manifest_schema_family`** values / semantics in [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) §6.1.
3. **Public surface:** Any change to `app.clarity.public_surface` exports, their semantics, or documented failure modes per [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md).
4. **Consumer kit:** Any change that would require a downstream repo to **assume** something new, or that changes a **Supported / Unsupported / Unknown** row in [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) without explicit evidence and ledger/scorecard alignment.
5. **Operating manual / assumptions:** Changes that invalidate procedures or “what may be assumed” in [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md) or [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md).
6. **Verdict-critical assumptions:** Changes to supported combinations, demo vs CI truth, or compatibility matrix evidence that would alter the M24 **conditions** in [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md).

---

## 5. What requires a new readiness milestone or re-readiness review

| Trigger | Minimum response |
|---------|------------------|
| Any **contract-affecting** change in §4 | **Re-readiness review**: update affected docs, [`READINESS_LEDGER.md`](./READINESS_LEDGER.md), `docs/clarity.md`, and **extend or refresh** [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) with a new verdict section **or** a dated addendum that states whether the M24 verdict still holds |
| New **M18–M24-style** freeze cycle (major portability change) | New **readiness milestone** (e.g. M26+) with plan, tests, and ledger entries per [`readinessplan.md`](./readinessplan.md) pattern |
| **Breaking** change to `PUBLIC_SURFACE_SYMBOLS` or artifact contract defaults | Treat as **major**: re-readiness review **and** explicit compatibility note in [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) |

---

## 6. What can change without re-running the full M18–M24 program

| Change class | Allowed when |
|--------------|--------------|
| **Bugfix** restoring documented behavior | Tests + docs unchanged in intent; no consumer-facing semantic change |
| **Internal refactor** with no export/artifact/ boundary change | Guardrail tests still pass; no doc updates needed |
| **Non-canonical surfaces** (e.g. demo HTTP, UI) | [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) remains authoritative; do not imply readiness-canonical stability |
| **Docs typo / link fix** | No semantic change to contracts; optional `READINESS_DECISIONS.md` entry if ambiguity was fixed |
| **Dependency patch** (security/tooling) | No change to frozen semantics; CI remains green |

---

## 7. Versions and tags

- Readiness track milestones **M18–M24** were largely **untagged** unless explicitly authorized (`docs/clarity.md`).
- A **release** that advertises portability to consumers should **record** the commit SHA and the **scorecard verdict** in `docs/clarity.md` and [`READINESS_LEDGER.md`](./READINESS_LEDGER.md).
- **Tagging** (if used) should not replace contract documents; tags are pointers, not contracts.

---

## 8. Recording compatibility-impacting changes

1. Add a row or note to [`READINESS_DECISIONS.md`](./READINESS_DECISIONS.md) for readiness-relevant decisions.
2. Update [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) if **Supported / Unsupported / Unknown** shifts.
3. Update [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) if adoption steps change.
4. Update [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) **open risks** if new deferred issues appear.

**Forbidden:** silently upgrading **Unknown** to **Supported** or downgrading **Unsupported** without evidence (see scorecard audit rules).

---

## 9. Deferred issues and post-readiness regressions

| Situation | Action |
|-----------|--------|
| **Deferred issue** (e.g. R-001–R-003 in ledger) worsens | Update ledger; if consumer impact, amend scorecard addendum or reopen re-readiness |
| **Regression** in guardrail tests (`test_boundary_contract`, `test_artifact_contract`, `test_public_surface_contract`, `test_m22_operating_manual`, `test_supported_combinations`, `test_m24_readiness_verdict`) | **Block release** until fixed or verdict revised |
| **New** ambiguity discovered | Document in ledger; add to [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) **Weaknesses** or **Conditions** |

---

## 10. Relationship to readiness verdict

This file takes effect alongside the verdict in [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md). **M24** conditions **C-M24-001..003** were cleared by **M25** (see [`CLARITY_READINESS_REVIEW_ADDENDUM_M25.md`](./CLARITY_READINESS_REVIEW_ADDENDUM_M25.md)). Future contract-affecting changes require a **re-readiness review** or new milestone per §5.
