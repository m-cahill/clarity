# M23 — Consumer Assumptions, Compatibility Matrix & Transfer Checklist

**Status:** Executing on branch `m23-supported-combination-truth-table` (merge to `main` closes).

**Source of truth:** [`docs/readiness/readinessplan.md`](../../readiness/readinessplan.md) — **M23** section.

## Objective

Deliver the downstream **consumer kit**: explicit assumptions, a **compatibility matrix** authored as a **Supported / Unsupported / Unknown** combination truth table (evidence-bound honesty posture aligned with M22), and a **transfer checklist** derived from those documents.

## Non-goals

- Do not reopen M19–M21 contracts; do not widen `app.clarity.public_surface`.
- Do not treat the HTTP API as readiness-canonical.
- Do not claim orchestrator-only runs satisfy full analytical bundle expectations.
- Do not mint a tag; do not claim final readiness (**M24**).

## Planned deliverables

| Deliverable | Role |
|-------------|------|
| [`CLARITY_CONSUMER_ASSUMPTIONS.md`](../../readiness/CLARITY_CONSUMER_ASSUMPTIONS.md) | Assumptions a consumer may make after M19–M22 |
| [`CLARITY_COMPATIBILITY_MATRIX.md`](../../readiness/CLARITY_COMPATIBILITY_MATRIX.md) | Main table-driven combination truth (Supported / Unsupported / Unknown) |
| [`CLARITY_TRANSFER_CHECKLIST.md`](../../readiness/CLARITY_TRANSFER_CHECKLIST.md) | Operational adoption checklist |
| [`M23_inventory.md`](./M23_inventory.md) | Milestone inventory bridge (repo inspection → classifications) |
| `backend/tests/test_supported_combinations.py` | Lightweight M23 guardrails |
| Pack / ledger / `docs/clarity.md` | Index and status updates |

## Readiness plan

The master [`readinessplan.md`](../../readiness/readinessplan.md) is **not** rewritten in M23; this milestone **implements** the M23 section as written (three documents), with the compatibility matrix using the **supported-combination truth table** as organizing logic.

## Exit criteria

- Three readiness-pack documents exist and are listed in `test_readiness_pack.py`.
- Combination matrix uses **Supported / Unsupported / Unknown** with traceable evidence for **Supported** rows.
- Readiness remains **`NOT READY`**; M24 remains the verdict milestone.
