# M18 — Readiness Charter & Authority Freeze

**Mode:** GOVERNANCE — Readiness program scaffolding (no feature work)

---

## Milestone title

**M18 — Readiness Charter & Authority Freeze**

---

## Purpose

Establish the **readiness phase** (M18–M24) as a governed program inside this repository: freeze document authority, create `docs/readiness/` as the canonical readiness pack, seed ledger and ADR-style decisions, and record the roadmap in `docs/clarity.md`.

**Explicit state:** CLARITY remains **`NOT READY`** for downstream adoption after M18. This milestone only sets up governance and scaffolding for later evidence-backed verdicts.

---

## Scope

- Create `docs/readiness/` and install the approved readiness plan as `docs/readiness/readinessplan.md` (copy from `docs/readinessplan.md`; **keep** root copy per repo policy).
- Add `README.md`, `READINESS_LEDGER.md`, `READINESS_DECISIONS.md`.
- Update `docs/clarity.md`: readiness phase purpose, M18–M24 planned milestones, `NOT READY`, artifact references, authority note.
- Add **one** lightweight guardrail (readiness file existence + README link resolution test in backend pytest).
- Authoritative execution plan for this branch: this file.

---

## Non-goals

- No CLARITY↔R2L boundary freeze beyond what already exists (M19).
- No artifact contract, public surface freeze, operating manual, compatibility matrix, or portability verdict.
- No new model features, demo redesign, or downstream-specific integration.
- No weakening of CI; no heavy new workflows.
- **Do not** create git tag for M18 unless explicitly authorized later (`not tagged` in ledger).

---

## Deliverables

### Create

| Path | Role |
|------|------|
| `docs/readiness/readinessplan.md` | Canonical copy of approved readiness plan (pack) |
| `docs/readiness/README.md` | Front door: authority, reading order, language rules |
| `docs/readiness/READINESS_LEDGER.md` | Control ledger: status, roadmap, inventory, risks |
| `docs/readiness/READINESS_DECISIONS.md` | ADR-style readiness decisions |
| `docs/milestones/M18/M18_plan.md` | This file |
| `docs/milestones/M18/M18_toolcalls.md` | Tool / recovery log |
| `backend/tests/test_readiness_pack.py` | Lightweight existence + link check |

### Update

| Path | Role |
|------|------|
| `docs/clarity.md` | Ledger: readiness phase, table rows M18–M24, current milestone, references |

### After green CI (closeout)

| Path | Role |
|------|------|
| `docs/milestones/M18/M18_summary.md` | Summary per `docs/prompts/summaryprompt.md` |
| `docs/milestones/M18/M18_audit.md` | Audit per `docs/prompts/unifiedmilestoneauditpromptV2.md` |

### Seed next milestone

| Path | Role |
|------|------|
| `docs/milestones/M19/M19_plan.md` | Stub / pointer only |
| `docs/milestones/M19/M19_toolcalls.md` | Header only |

---

## Verification plan

- All paths under `docs/readiness/` listed in README exist; pytest `test_readiness_pack.py` passes.
- `docs/clarity.md` references readiness phase, M18–M24, `NOT READY`, and pack paths.
- Full `pytest` in `backend/` (existing CI matrix) passes locally.
- No tag created unless authorized.

---

## Exit criteria

- `docs/readiness/` exists with core scaffolding docs.
- `docs/clarity.md` updated as canonical ledger with readiness phase and M18–M24.
- Authority hierarchy documented; readiness status **`NOT READY`**.
- Lightweight guardrail green; overall CI green.
- Summary + audit complete; M19 seeded.

---

## Rollback posture

Revert readiness docs and `docs/clarity.md` changes; remove `test_readiness_pack.py` if needed. Low risk — documentation-first.

---

## Instructions for `docs/clarity.md` updates

1. Add milestone table rows **M18–M24** (M18 closed; M19–M24 planned).
2. Add **Readiness phase** section: purpose (portable, governable, test-enforced, legible; no new model features; no downstream-specific integration).
3. Record **readiness status:** `NOT READY`.
4. Reference: `docs/readiness/readinessplan.md`, `README.md`, `READINESS_LEDGER.md`, `READINESS_DECISIONS.md`.
5. Authority: `docs/clarity.md` = project ledger; `docs/readiness/` = readiness pack; note legacy `docs/readinessplan.md` vs canonical pack copy.
6. Tag column for M18: **`not tagged`** (no tag minted without approval).
7. **Current milestone** section: M18; **Previous:** M17.

---

## Deferred-issues handling

- Any repo-truth mismatch or ambiguity → `READINESS_LEDGER.md` open risks / deferred table, not silent edits.
- Unresolved items must have rationale and target milestone.
