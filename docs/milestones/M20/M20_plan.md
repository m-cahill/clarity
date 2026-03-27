# M20 — Artifact Contract & Deterministic Output Freeze

**Status:** Closed (see `M20_summary.md`, `M20_audit.md`).

**Source of truth:** [`docs/readiness/readinessplan.md`](../../readiness/readinessplan.md) — M20 section.

---

## Milestone objective

Freeze CLARITY’s **output artifact model**, **serialization expectations**, **required vs optional files**, **deterministic ordering**, **numeric handling**, and **contract identity / reproducibility rules** as a canonical readiness contract, and back that contract with **test evidence**.

---

## Scope

- Authoritative **`docs/readiness/CLARITY_ARTIFACT_CONTRACT.md`** (namespace, required/optional artifacts, canonical vs presentation-only, shapes, ordering, floats, identity, compatibility).
- Updates to **`READINESS_LEDGER.md`**, **`docs/clarity.md`**, pack **`README.md`** (reading order if needed), **`READINESS_DECISIONS.md`** (durable ADRs only).
- New tests: **`backend/tests/test_artifact_contract.py`** (semantic + stable-hash + ordering + float rule spot-check + presentation exclusion).
- Extend **`test_readiness_pack.py`** required file list.

---

## Non-goals

- Public invocation surface, CLI/Python API freeze (**M21**).
- Operating manual, implementation matrix (**M22**).
- Consumer assumptions pack, compatibility matrix (**M23**).
- Final readiness verdict (**M24**).
- R2L semantics, schemas, or CI behavior changes.
- Tags unless explicitly authorized.

---

## Repo-truth inspection obligations (completed)

- Readiness docs: `docs/clarity.md`, `readinessplan.md`, `README.md`, `READINESS_LEDGER.md`, `READINESS_DECISIONS.md`, `CLARITY_BOUNDARY_CONTRACT.md`, `CLARITY_ASSUMED_GUARANTEES.md`.
- Writers: `sweep_orchestrator.py` (sweep manifest), `serialization.py`, `surfaces.py` / `surface_engine.py`, `scripts/m15_real_ui_sweep.py`.
- Fixtures: `backend/tests/fixtures/baselines/m15_real_ui/`.
- Existing boundary/determinism tests: `test_boundary_contract.py` (not duplicated).

---

## Verification plan

- `CLARITY_ARTIFACT_CONTRACT.md` exists; README links resolve; readiness pack test passes.
- `pytest backend/tests/test_artifact_contract.py backend/tests/test_readiness_pack.py` passes.
- Full backend test suite green in CI.

---

## Exit criteria

- Artifact contract doc is explicit: required vs optional, canonical vs presentation-only, ordering, numeric rules, identity, compatibility.
- Guardrail tests pass; fixture SHA256 + semantic structure locked.
- `docs/clarity.md` and `READINESS_LEDGER.md` updated; readiness **`NOT READY`** preserved.
- Summary + audit complete; **M21** seeded only.

---

## Rollback posture

Revert artifact contract doc, new tests, and ledger/clarity updates together if a partial freeze would contradict repo truth.

---

## Required `docs/clarity.md` updates

- Milestone table: M20 closed.
- Pack index: `CLARITY_ARTIFACT_CONTRACT.md`.
- Current/previous milestone sections; readiness notes; deliverables; baseline row.

---

## Deferred-issue handling

- Document **multiple `sweep_manifest.json` schema families** (orchestrator vs rich aggregate) explicitly; do not hide ambiguity.
- Byte-identical JSON across **all** writers: **not** claimed unless separately frozen.
