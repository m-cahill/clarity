# Milestone summary — M25: Re-readiness upgrade

**Project:** CLARITY  
**Milestone:** M25 — Clear M24 conditions; upgrade portability verdict where evidence supports  
**Status:** Closed on branch `m25-re-readiness-upgrade` (merge to `main` via PR)

## Objective

Remove standing consumer adoption conditions **C-M24-001..003** and, with evidence, advance the recorded verdict from **`CONDITIONALLY READY`** to **`READY FOR DOWNSTREAM ADOPTION`**.

## Delivered

| Item | Detail |
|------|--------|
| **Manifest self-ID** | `manifest_schema_family` + `backend/app/clarity/manifest_schema_family.py`; `SweepOrchestrator`, M13/M15 scripts; fixtures; artifact/sweep tests |
| **Doc sync** | `backend/tests/test_m25_readiness_upgrade.py` |
| **Plan authority** | `docs/readinessplan.md` redirect stub |
| **Governance** | Addendum, scorecard §8–§10, ledger, RD-016, `docs/clarity.md`, contract headers |
| **M24** | Unchanged as historical milestone; **M24** summary/audit still describe **`CONDITIONALLY READY`** at M24 close |

## Readiness verdict

**`READY FOR DOWNSTREAM ADOPTION`** — see [`CLARITY_READINESS_SCORECARD.md`](../../readiness/CLARITY_READINESS_SCORECARD.md) §8.

## Scores

| Metric | Value |
|--------|--------|
| **Scorecard overall (M25)** | **5.0 / 5.0** (M25 re-score in scorecard §3) |
| **Milestone closure** | Governance exit criteria met; guardrail suite green |
