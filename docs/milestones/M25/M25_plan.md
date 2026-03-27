# M25 Plan — Re-readiness upgrade to `READY FOR DOWNSTREAM ADOPTION`

**Milestone:** M25 — Re-readiness upgrade: clear M24 conditions  
**Phase:** Post-readiness / re-readiness review  
**Status:** Implemented on branch `m25-re-readiness-upgrade`

## Objective

Upgrade the recorded portability verdict from **`CONDITIONALLY READY`** (M24) to **`READY FOR DOWNSTREAM ADOPTION`** only if evidence clears **C-M24-001**, **C-M24-002**, and **C-M24-003**.

## Work phases (summary)

1. **Inventory** — [`M25_inventory.md`](./M25_inventory.md)
2. **C-M24-001** — `manifest_schema_family` on all CLARITY `sweep_manifest.json` writers + `manifest_schema_family.py` + contract/tests
3. **C-M24-002** — `test_m25_readiness_upgrade.py` verdict/pack sync
4. **C-M24-003** — `docs/readinessplan.md` redirect stub; canonical `docs/readiness/readinessplan.md`
5. **Verdict** — scorecard, ledger, [`CLARITY_READINESS_REVIEW_ADDENDUM_M25.md`](../../readiness/CLARITY_READINESS_REVIEW_ADDENDUM_M25.md), `docs/clarity.md`, `READINESS_DECISIONS.md` (RD-016)

## Non-goals

No new model features, no public-surface widening, no CI weakening, no downstream-specific integration.

## Acceptance

All three M24 conditions cleared with tests green; verdict honest and consistent across canonical docs.
