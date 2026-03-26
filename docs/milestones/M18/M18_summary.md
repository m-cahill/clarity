# Milestone Summary — M18: Readiness Charter & Authority Freeze

**Project:** CLARITY  
**Phase:** Readiness (M18–M24)  
**Milestone:** M18 — Readiness Charter & Authority Freeze  
**Timeframe:** 2026-03-26 (single tranche)  
**Status:** Closed  

---

## 1. Milestone objective

Establish the **readiness phase** as a governed program inside the repository: create the canonical **`docs/readiness/`** pack, freeze document authority and terminology, seed a readiness ledger and ADR-style decisions log, record milestones **M18–M24** in **`docs/clarity.md`**, and add a **lightweight** automated check that core pack files exist and that local markdown links in the pack README resolve. Explicitly leave CLARITY in a **`NOT READY`** state for downstream adoption.

---

## 2. Scope boundaries

**In scope**

- `docs/readiness/readinessplan.md` (canonical pack copy of the approved plan)
- `docs/readiness/README.md`, `READINESS_LEDGER.md`, `READINESS_DECISIONS.md`
- Updates to `docs/clarity.md` (milestone table M18–M24, readiness phase section, current milestone, baseline row, key-doc links)
- `backend/tests/test_readiness_pack.py` (existence + README link resolution)
- Milestone artifacts: `M18_plan.md`, `M18_toolcalls.md`, this summary, `M18_audit.md`
- Seed: `docs/milestones/M19/M19_plan.md`, `M19_toolcalls.md`

**Out of scope**

- Consumer boundary contract, artifact contract, public surface, operating manual, compatibility matrix (later milestones)
- Git tag for M18 (**not tagged** unless explicitly authorized later)
- Removal of legacy `docs/readinessplan.md` at repo root (retained; pack copy is canonical)
- Changes to unrelated in-progress work (other modified files left to the contributor)

---

## 3. Deliverables completed

| Deliverable | Evidence |
|-------------|----------|
| Readiness pack | `docs/readiness/*` (four core files) |
| Canonical ledger | `docs/clarity.md` — readiness phase, M18–M24 rows, `NOT READY`, authority note |
| Lightweight guardrail | `backend/tests/test_readiness_pack.py`; 5 tests passing |
| M19 seed | `docs/milestones/M19/M19_plan.md`, `M19_toolcalls.md` |

---

## 4. Authority structure frozen

- **`docs/clarity.md`** remains the **canonical project ledger**.
- **`docs/readiness/`** is the **canonical readiness pack**; **`docs/readiness/readinessplan.md`** is the authoritative pack copy of the program (root `docs/readinessplan.md` documented as legacy/convenience where applicable).
- Readiness decisions **RD-001–RD-007** recorded in `READINESS_DECISIONS.md` (downstream-neutral language, evidence-backed claims, separate execution track).

---

## 5. `docs/clarity.md` updates (summary)

- Milestone table extended through **M24**; **M18** closed with tag **`not tagged`** and score **5.0** (per audit).
- New **Readiness phase (M18–M24)** section: purpose, **`NOT READY`**, authority table, pack index, legacy plan note.
- **Current milestone** set to **M18**; **M17** moved to previous milestone section.
- **Baseline reference** row added for M18 with **`not tagged`** and commit **`_[pending]_`** until merge commit is recorded.

---

## 6. Lightweight guardrails

- **`test_readiness_pack.py`**: asserts four required files exist under `docs/readiness/`; parses `README.md` for local `*.md` links and asserts targets exist. No new GitHub Actions workflow.

---

## 7. Verification

- `pytest tests/test_readiness_pack.py` — pass  
- Full backend `pytest` with coverage ≥85% — pass (local, after `pip install -e ".[dev]"`)  
- Frontend `npm run test:coverage` — pass  

CI is expected to match (same install paths as `.github/workflows/ci.yml`).

---

## 8. Readiness status

**`NOT READY`** — unchanged by design. M18 is charter and scaffolding only.

---

## 9. Deferred / next (M19)

Per **`docs/readiness/readinessplan.md`**, **M19 — Consumer Boundary Freeze**: introduce `CLARITY_BOUNDARY_CONTRACT.md`, `CLARITY_ASSUMED_GUARANTEES.md`, boundary tests, and ledger updates. **No M19 implementation** was done in M18.

---

## 10. Score

**Target:** 5.0  
**Recorded:** Align with **`M18_audit.md`** (honest; governance quality is first-class).
