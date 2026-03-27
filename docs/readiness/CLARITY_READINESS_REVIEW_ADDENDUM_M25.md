# CLARITY — Readiness review addendum (M25)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M25 — Re-readiness upgrade |
| **Authority** | Supersedes the **conditional** elements of the M24 portability verdict where stated below; subordinate to [`docs/clarity.md`](../clarity.md) and [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) |
| **Evidence** | Repository state on branch `m25-re-readiness-upgrade` merged to `main` |

---

## 1. Purpose

This addendum records the **M25 re-readiness review** required by [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md) when clearing **M24** adoption conditions **C-M24-001** through **C-M24-003**.

It does **not** erase M24 history. M24 remains the milestone that first recorded an explicit scorecard verdict on `main` @ `e1a6b54`.

---

## 2. What changed since M24

| Area | Change |
|------|--------|
| **C-M24-001** (`sweep_manifest.json`) | Introduced mandatory top-level **`manifest_schema_family`** for CLARITY writers (`clarity_sweep_orchestrator_v1`, `clarity_rich_aggregate_v1`), implementation in `app/clarity/manifest_schema_family.py`, producers updated (`SweepOrchestrator`, M13/M15 scripts), fixtures refreshed, tests in `test_artifact_contract.py`. |
| **C-M24-002** (doc/ledger/test sync) | Added **`test_m25_readiness_upgrade.py`** to enforce verdict tokens and readiness-pack consistency across `docs/clarity.md`, ledger, scorecard, and addendum. |
| **C-M24-003** (dual readiness plan) | Replaced `docs/readinessplan.md` body with a **redirect stub**; canonical program text remains only in **`docs/readiness/readinessplan.md`**. |

---

## 3. M24 verdict supersession

| Item | Status |
|------|--------|
| **M24 recorded verdict** | **`CONDITIONALLY READY`** (historical — see [`../milestones/M24/M24_summary.md`](../milestones/M24/M24_summary.md)) |
| **M25 recorded verdict** | **`READY FOR DOWNSTREAM ADOPTION`** |
| **Conditions C-M24-001..003** | **Cleared** — no longer binding consumer adoption caveats |

---

## 4. Non-goals (honored)

- No new CLARITY model features, no MedGemma capability redesign, no public-surface widening beyond `app.clarity.public_surface`, no CI weakening, no downstream-specific integration work.

---

## 5. Related

- [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) — §8–§10  
- [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) — §2, §7  
- [`READINESS_DECISIONS.md`](./READINESS_DECISIONS.md) — RD-016
