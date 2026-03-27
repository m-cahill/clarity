# CLARITY readiness pack

## 1. Purpose

This directory holds the **canonical readiness pack** for CLARITY: governed documents that define how an external project or consumer repository may safely depend on CLARITY **without** relying on undocumented behavior, implied contracts, or tribal knowledge.

The readiness phase (M18–M24) is a **separate execution track** from feature development. It does not add model capability; it freezes and evidences boundaries, artifacts, invocation, and consumer assumptions.

---

## 2. Scope of this pack

**In scope:** Portability, governance, test-backed contracts, and honest documentation of what is implemented vs unknown.

**Out of scope for the pack itself:** Downstream-specific integration code, naming of external repositories, and one-off hacks that bypass published contracts.

---

## 3. Canonical sources (authority order)

1. **`docs/clarity.md`** — Canonical **project ledger** and milestone record for the repository.
2. **Frozen contracts and ledgers under `docs/readiness/`** — Readiness authority (this pack).
3. **Current code and tests** — Executable truth.
4. **Milestone summaries and audits** — Milestone-scoped evidence.
5. **Aspirational or draft notes** — Lowest authority; must be labeled as such.

Within this pack, the **roadmap and definitions** in `readinessplan.md` set expectations for what will appear by M24. Individual documents gain authority when explicitly frozen in their milestone (see `READINESS_LEDGER.md`).

---

## 4. Reading order

1. This file (`README.md`).
2. [`readinessplan.md`](./readinessplan.md) — Full M18–M24 program (milestones, non-goals, exit criteria).
3. [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) — Status, roadmap, inventory, risks, evidence map.
4. [`READINESS_DECISIONS.md`](./READINESS_DECISIONS.md) — Readiness-only architecture and policy decisions (ADR-style).
5. [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) — Frozen CLARITY↔R2L consumer boundary (M19).
6. [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md) — Inherited substrate assumptions vs CLARITY-owned responsibilities (M19).
7. [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) — Frozen artifact inventory, serialization, and contract identity (M20).
8. [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) — Canonical consumer Python invocation surface (M21).
9. [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md) — AI-agent / operator manual; implemented pipeline and debugging (M22).
10. [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) — Honest Implemented / Planned / Unknown matrix (M22).
11. [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md) — Explicit downstream assumptions after M19–M22 (M23).
12. [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) — Supported / Unsupported / Unknown combination truth table (M23).
13. [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) — Adoption transfer checklist (M23).
14. [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md) — Post-readiness change rules (M24).
15. [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) — Final scorecard and portability verdict (M24).

For overall project context, always read **`docs/clarity.md`** first or in parallel.

---

## 5. Language and naming rules

Readiness documents use **downstream-neutral** wording only, for example:

- “consumer project”
- “downstream repository”
- “external project”

Do **not** name specific downstream repositories unless strictly necessary and approved out-of-band.

---

## 6. Legacy copy of the readiness plan

**`docs/readinessplan.md`** (repository root under `docs/`) may remain as a **convenience / legacy** copy of the plan. The **canonical readiness-pack** copy of the same content is:

- **`docs/readiness/readinessplan.md`**

If both exist, treat **`docs/readiness/readinessplan.md`** as authoritative for the readiness pack; resolve conflicts in favor of the pack copy and record intentional changes in `READINESS_DECISIONS.md`.

---

## 7. Current readiness status

**`READY FOR DOWNSTREAM ADOPTION`** (M25; M24 `CONDITIONALLY READY` superseded — see [`CLARITY_READINESS_REVIEW_ADDENDUM_M25.md`](./CLARITY_READINESS_REVIEW_ADDENDUM_M25.md))

M18–**M23** delivered the frozen pack (boundary, artifacts, public surface, manual, consumer kit). **M24** records the final scorecard ([`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md)), post-readiness [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md), and aggregate test `test_m24_readiness_verdict.py`. Adoption is **subject to conditions** in the scorecard §9 (C-M24-001..003). See [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) §7.

---

## 8. Relationship to the milestone ledger

Every readiness milestone (M18–M24) must update **`docs/clarity.md`** (canonical ledger) and this pack **where appropriate**. Closeout artifacts live under `docs/milestones/MNN/`.
