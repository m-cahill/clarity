# M19 — Consumer Boundary Freeze

**Status:** Authoritative plan for M19 execution.

---

## Milestone objective

Freeze the CLARITY↔R2L **consumer boundary** as a canonical readiness contract: what CLARITY may consume from R2L, what it owns, what it must not do, and how **canonical** vs **optional rich** modes relate at the boundary—grounded in **implemented** code and tests, not aspirational architecture.

---

## Scope

### In scope

- Authoritative readiness documents:
  - `docs/readiness/CLARITY_BOUNDARY_CONTRACT.md`
  - `docs/readiness/CLARITY_ASSUMED_GUARANTEES.md`
- Updates: `docs/readiness/READINESS_LEDGER.md`, `docs/readiness/README.md` (reading order / factual status), `docs/readiness/READINESS_DECISIONS.md` (durable ADRs only), `docs/clarity.md`
- Boundary guardrail tests: extend `backend/tests/test_readiness_pack.py` for new pack files; extend `backend/tests/test_boundary_contract.py` with M19-focused cases (artifact loader contract, canonical vs rich boundary invariants)
- Closeout: `M19_summary.md`, `M19_audit.md`; seed **M20 only** (`M20_plan.md`, `M20_toolcalls.md`)

### Non-goals

- Full artifact contract freeze (**M20**)
- Public Python surface / official consumer API (**M21**)
- Operating manual, compatibility matrix, transfer checklist (**M22–M23**)
- Changes to R2L semantics, schemas, or substrate CI
- Downstream-project-specific integration
- Repairing [`CLARITY_ARCHITECHTURE_CONTRACT.MD`](../../CLARITY_ARCHITECHTURE_CONTRACT.MD) unless required for truthful cross-reference (not required for M19)
- Opportunistic fixes to unrelated ledger items (e.g. M16 baseline commit placeholder) unless they block truthful M19 updates

---

## Repo-truth inspection obligations (pre-write)

Completed grounding:

- `docs/clarity.md`, `docs/readiness/readinessplan.md`, `READINESS_LEDGER.md`, `READINESS_DECISIONS.md`
- `CLARITY_CAPABILITY_CONTEXT.md`, `CLARITY_ARCHITECHTURE_CONTRACT.MD` (context only)
- `app.clarity.r2l_runner`, `r2l_interface` (namespace), `artifact_loader`, `rich_generation` / `medgemma_runner` for env switches
- `backend/tests/test_boundary_contract.py`, fixtures under `backend/tests/fixtures/r2l_samples/`

---

## Required deliverables

| Deliverable | Location |
|-------------|----------|
| Boundary contract | `docs/readiness/CLARITY_BOUNDARY_CONTRACT.md` |
| Assumed guarantees | `docs/readiness/CLARITY_ASSUMED_GUARANTEES.md` |
| Ledger / pack updates | `READINESS_LEDGER.md`, `README.md`, `READINESS_DECISIONS.md` as needed |
| Canonical ledger | `docs/clarity.md` |
| Tests | `test_boundary_contract.py`, `test_readiness_pack.py` |
| Milestone artifacts | `M19_plan.md`, `M19_toolcalls.md`, `M19_summary.md`, `M19_audit.md` |

---

## Verification plan

- `pytest backend/tests/test_readiness_pack.py backend/tests/test_boundary_contract.py` — pass
- Full backend test suite per CI parity
- Confirm new markdown links from `docs/readiness/README.md` resolve

---

## Exit criteria

- Both new readiness documents exist and are meaningful
- Inherited vs CLARITY-owned split is explicit; forbidden behaviors listed
- Guardrails pass; ledger and `docs/clarity.md` updated; readiness **`NOT READY`**
- M20 seeded; M20 not implemented

---

## Rollback posture

Revert boundary docs, tests, and ledger/`docs/clarity.md` together if rollback is needed; do not leave contradictory boundary claims.

---

## Required `docs/clarity.md` updates

- Milestone table: M19 closed
- Readiness pack index: link boundary + assumed-guarantees docs
- Current / previous milestone sections per convention
- Baseline row for M19 (commit recorded at merge if policy requires)

---

## Deferred-issue handling

Record deferred surfaces (M20–M24) in the boundary contract and ledger; do not imply final portability.

---

## Source

Program definition: [`docs/readiness/readinessplan.md`](../../readiness/readinessplan.md) — section **M19 — Consumer Boundary Freeze**.
