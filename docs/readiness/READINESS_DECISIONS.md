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

---

## RD-008 — Canonical readiness-pack boundary contract (M19)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M19 |
| **Context** | Boundary rules for consumers must live under the readiness pack per `readinessplan.md`; older one-page architecture notes must not remain the sole authority for readiness. |
| **Decision** | **`docs/readiness/CLARITY_BOUNDARY_CONTRACT.md`** is the **canonical readiness-pack** CLARITY↔R2L boundary contract. [`CLARITY_ARCHITECHTURE_CONTRACT.MD`](../CLARITY_ARCHITECHTURE_CONTRACT.MD) remains prior architectural context, not the top readiness authority. |
| **Rationale** | Matches authority order (`docs/clarity.md` → frozen `docs/readiness/` → code/tests); avoids silent drift between M01 notes and M18+ governance. |
| **Consequences** | Readiness reviews cite the pack contract; legacy doc may be referenced but does not override the pack. |

---

## RD-009 — Black-box invocation as default sanctioned surface (until M21)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M19 |
| **Context** | Consumers need a clear default integration pattern before a public Python surface is frozen. |
| **Decision** | **CLI / subprocess** invocation of R2L with artifact consumption (`R2LRunner`) is the **default sanctioned** boundary in this repository until **M21** defines an official public consumer surface. |
| **Rationale** | Implemented in `r2l_runner.py`; preserves “no internal R2L imports” invariant. |
| **Consequences** | Direct import of deep modules as a supported API remains **out of scope** for readiness until M21 explicitly freezes a surface. |

**M21 note:** The **“until M21”** default for **which Python module** is the official consumer surface is **superseded** by **RD-014**. RD-009 remains valid for **substrate** behavior: R2L is still invoked **only** via subprocess / `R2LRunner` from CLARITY’s perspective.

---

## RD-010 — Rich-mode environment switch (CLARITY repo)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M19 |
| **Context** | Historical and upstream docs may name substrate-side flags differently from this repo’s implementation. |
| **Decision** | For **this repository’s** CLARITY rich-path gating, **`CLARITY_RICH_MODE`** (with **`CLARITY_REAL_MODEL`** where required by code) is **canonical**. Optional **`CLARITY_RICH_LOGITS_HASH`** for full logits hashing. Upstream-only names (e.g. **`R2L_RICH_MODE`** in non-readiness context docs) are **not** treated as the CLARITY-side switch unless explicitly wired in code. |
| **Rationale** | Implementation truth beats historical wording; avoids double-canonical env confusion in readiness artifacts. |
| **Consequences** | Readiness docs and tests anchor on `app.clarity.rich_generation` / `medgemma_runner` behavior. |

---

## RD-011 — Report PDFs are presentation-only (M20)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M20 |
| **Context** | Consumers need to know whether exported PDFs are canonical evidence of a run or regenerable views. |
| **Decision** | **PDF report outputs** (e.g. under report paths) are **derived / presentation-only**. They **do not** participate in **contract identity** for a sweep unless a future milestone explicitly promotes them. |
| **Rationale** | Aligns with optional early PDF in architecture notes; JSON artifacts remain the analyzable source of truth. |
| **Consequences** | Hashing or diffing PDFs is **not** required for portability proof; semantic JSON contract remains primary. |

---

## RD-012 — Contract identity: semantic first, selective byte stability (M20)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M20 |
| **Context** | Multiple JSON writers exist (`json.dump`, `deterministic_json_dumps`, script-local `json.dumps`). |
| **Decision** | **Contract equivalence** for artifact comparison is **semantic JSON equality** (parse + structure) as the baseline. **Per-file SHA256** of **committed fixtures** and **round-trip** serialization tests are **evidence** where a single recipe is used, not a claim that every producer emits byte-identical JSON. |
| **Rationale** | Avoids false guarantees across writers while still freezing real determinism where tested. |
| **Consequences** | Changes to serialization helpers or producers may require updating fixture hashes and tests deliberately. |

---

## RD-013 — Surface-engine floats use `_round8` (M20)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M20 |
| **Context** | Readiness plan asks for stable numeric rules; fixtures show many decimal places. |
| **Decision** | For **`SurfaceEngine` / `surfaces`** metrics storage, numeric values use **`round(value, 8)`** (`_round8`). Other floats in manifests follow **Python `json` default float encoding** unless explicitly rounded elsewhere. |
| **Rationale** | Matches implemented `surfaces.py` / `surface_engine.py`; avoids inventing a global decimal width for all JSON. |
| **Consequences** | Contract docs and tests reference `_round8` for that path only. |

---

## RD-014 — Canonical Python public surface (M21)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M21 |
| **Context** | Readiness requires a **single** official consumer invocation path; the broad `app.clarity` package root is not a minimal contract. |
| **Decision** | The canonical **readiness** public surface is **`app.clarity.public_surface`**, re-exporting only the symbols listed in that module’s `__all__` / `PUBLIC_SURFACE_SYMBOLS`. **HTTP API** routes are **not** part of the M21 contract (demo/operational). **No** CLARITY setuptools CLI is introduced for M21. |
| **Rationale** | Thin, test-freezable surface; preserves black-box R2L invocation via `R2LRunner` + `SweepOrchestrator`; avoids freezing demo HTTP routes or the entire legacy export list. |
| **Consequences** | Breaking changes to listed symbols require a readiness decision, milestone, and test updates. Root `from app.clarity import ...` remains **not** the portability contract. Final portability verdict remains **M24**. |

---

## RD-015 — M24 portability verdict (CONDITIONALLY READY)

| Field | Value |
|-------|--------|
| **Status** | Accepted |
| **Date / milestone** | M24 |
| **Context** | The readiness program requires a single explicit verdict backed by evidence. |
| **Decision** | M24 records **`CONDITIONALLY READY`** in [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md): adoption is safe **if** consumers follow the frozen pack and **conditions** C-M24-001..003 (manifest producer classification, doc/ledger sync, canonical plan path). |
| **Rationale** | R-001–R-003 are non-blockers for documentation but impose residual obligations; two `sweep_manifest.json` schema families are explicit in the artifact contract but require consumer discipline. |
| **Consequences** | **`READY FOR DOWNSTREAM ADOPTION`** is **not** claimed without qualification. Re-readiness and [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md) apply to contract-affecting changes. |
