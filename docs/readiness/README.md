# CLARITY readiness pack

## 1. Purpose

This directory holds the **canonical readiness pack** for CLARITY: governed documents that define how an external project or consumer repository may safely depend on CLARITY **without** relying on undocumented behavior, implied contracts, or tribal knowledge.

The readiness program (M18–M24) and **M25** re-readiness upgrade are **separate execution tracks** from feature development. They do not add model capability; they freeze and evidence boundaries, artifacts, invocation, consumer assumptions, and the final portability verdict.

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
15. [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) — Scorecard and portability verdict (M24; M25 supersession).
16. [`CLARITY_READINESS_REVIEW_ADDENDUM_M25.md`](./CLARITY_READINESS_REVIEW_ADDENDUM_M25.md) — M25 re-readiness evidence (supersedes M24 conditional elements).

For overall project context, always read **`docs/clarity.md`** first or in parallel. Program arc closeout: [`../milestones/M25/M25_project_closeout.md`](../milestones/M25/M25_project_closeout.md).

---

## 5. Language and naming rules

Readiness documents use **downstream-neutral** wording only, for example:

- “consumer project”
- “downstream repository”
- “external project”

Do **not** name specific downstream repositories unless strictly necessary and approved out-of-band.

---

## 6. Legacy path for the readiness plan

**`docs/readinessplan.md`** (under `docs/`) is a **redirect stub** only. The **canonical** program text is **`docs/readiness/readinessplan.md`**. Do not duplicate substantive plan content at the root path.

---

## 7. Current readiness status

**`READY FOR DOWNSTREAM ADOPTION`** (M25; M24’s **`CONDITIONALLY READY`** and conditions **C-M24-001..003** superseded — see [`CLARITY_READINESS_REVIEW_ADDENDUM_M25.md`](./CLARITY_READINESS_REVIEW_ADDENDUM_M25.md) and [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) §8–§9).

M18–**M23** delivered the frozen pack (boundary, artifacts, public surface, manual, consumer kit). **M24** recorded the scorecard and [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md). **M25** re-readiness cleared the remaining M24 adoption conditions and aligned the recorded verdict. See [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) §7. Future contract-affecting changes follow [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md).

---

## 8. Relationship to the milestone ledger

Every readiness milestone (M18–M24) must update **`docs/clarity.md`** (canonical ledger) and this pack **where appropriate**. Closeout artifacts live under `docs/milestones/MNN/`.
