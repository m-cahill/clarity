# Readiness decisions (ADR-style)

Running log of **readiness-phase** decisions only. Broader project decisions remain recorded in `docs/clarity.md` and milestone audits unless duplicated here for clarity.

---

## RD-001 — Canonical location for readiness documents

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M18 |
| **Context** | Readiness work spans multiple milestones and must not compete with ad hoc docs scattered across `docs/`. |
| **Decision** | Readiness pack lives under **`docs/readiness/`**. |
| **Rationale** | Single discoverable tree; aligns with `readinessplan.md` structure; keeps governance boundaries clear. |
| **Consequences** | New readiness contracts and ledgers are added here; `docs/clarity.md` must reference them when introduced. |

---

## RD-002 — Readiness is a separate execution track

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M18 |
| **Context** | Feature milestones (M00–M17) delivered instrument capability; portability requires different controls. |
| **Decision** | M18–M24 readiness work is a **governed program** with its own ledger and decisions, not ad hoc documentation. |
| **Rationale** | Prevents “paper readiness” without evidence; separates contract freeze from feature velocity. |
| **Consequences** | Milestone closeouts must update both `docs/clarity.md` and this pack where applicable. |

---

## RD-003 — Downstream-neutral naming

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M18 |
| **Context** | Readiness docs must remain reusable and must not embed assumptions about a specific external repository. |
| **Decision** | Use generic terms (**consumer project**, **downstream repository**, **external project**). Do not name specific downstream consumers unless strictly necessary. |
| **Rationale** | Avoids implied partnerships, scope creep, and stale names in long-lived contracts. |
| **Consequences** | Reviews should flag named downstream references in readiness docs unless explicitly exempted. |

---

## RD-004 — `docs/clarity.md` remains the canonical project ledger

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M18 |
| **Context** | The repository already uses `docs/clarity.md` as the milestone and evidence ledger. |
| **Decision** | **`docs/clarity.md`** stays the **canonical project ledger**; readiness milestones update it every time they change readiness status or add pack artifacts. |
| **Rationale** | One place for “where is the project?” truth; readiness pack details do not replace the ledger. |
| **Consequences** | Omission of ledger updates is a process failure for a milestone closeout. |

---

## RD-005 — `docs/readiness/` is the canonical readiness pack

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M18 |
| **Context** | Contracts and checklists must be locatable without hunting through unrelated `docs/` files. |
| **Decision** | **`docs/readiness/`** is the **canonical readiness pack** for frozen readiness artifacts (as they are introduced M18–M24). |
| **Rationale** | Matches the approved program structure; enables clear authority ordering (see pack `README.md`). |
| **Consequences** | Frozen contracts should not live only in milestone folders without a pack pointer; prefer pack + ledger reference. |

---

## RD-006 — Readiness status at M18

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M18 |
| **Context** | M18 creates scaffolding; no boundary/artifact/public-surface freeze is complete yet. |
| **Decision** | Readiness is explicitly **`NOT READY`** at end of M18. |
| **Rationale** | Avoids implying portability or adoption safety before evidence exists. |
| **Consequences** | Marketing, demos, and external messaging must not cite M18 as “ready to integrate.” |

---

## RD-007 — Readiness claims require evidence and explicit verdict

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M18 |
| **Context** | Narrative-only “readiness” undermines trust and complicates audits. |
| **Decision** | Readiness **claims** must be **evidence-backed** (tests, contracts, audits). A final **portability verdict** is issued only at **M24** (or superseding decision), not by implication. |
| **Rationale** | Aligns with readiness definition in `readinessplan.md` and keeps the program honest. |
| **Consequences** | Interim milestones record progress and deferrals; they do not replace M24. |
