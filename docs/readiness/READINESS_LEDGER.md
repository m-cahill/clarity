# CLARITY — Readiness ledger

## 1. Readiness objective

Make CLARITY **portable, governable, test-enforced, and legible** so a consumer project can adopt it **without ambiguity, contract drift, or hidden assumptions**—evidenced by frozen contracts, tests, and explicit verdicts—not narrative alone.

---

## 2. Current status

| Field | Value |
|-------|--------|
| **Readiness** | **`CONDITIONALLY READY`** |
| **Phase** | Readiness (M18–M24) — **program complete** |
| **As-of milestone** | **M24** — **closed** (final audit, scorecard, change control) |
| **Notes** | Consumer boundary (M19), artifact contract (M20), canonical Python public surface (M21), operating manual + implementation matrix (M22), consumer kit (M23) merged previously. **M24** delivers [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) and [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md); aggregate test `test_m24_readiness_verdict.py`. **Verdict:** **`CONDITIONALLY READY`** — see scorecard §8–§9 for conditions. |

---

## 3. Milestone roadmap (M18–M24)

| ID | Title | Purpose (summary) | Ledger status |
|----|-------|-------------------|----------------|
| **M18** | Readiness Charter & Authority Freeze | Create `docs/readiness/`, authority hierarchy, ledger + decisions; update `docs/clarity.md` | **Closed** |
| **M19** | Consumer Boundary Freeze | Freeze CLARITY↔R2L consumer boundary and inherited guarantees | **Closed** |
| **M20** | Artifact Contract & Deterministic Output Freeze | Freeze outputs, serialization, reproducibility | **Closed** |
| **M21** | Public Surface & Invocation Contract | Single official invocation path; public vs internal | **Closed** |
| **M22** | Operating Manual & Honest Implementation Matrix | Operable manual + implemented vs planned vs unknown | **Closed** |
| **M23** | Consumer Assumptions, Compatibility Matrix & Transfer Checklist | Consumer kit: assumptions, matrix (truth table), checklist | **Closed** ([PR #24](https://github.com/m-cahill/clarity/pull/24) → `main` `4469b2c`) |
| **M24** | Readiness Audit, Scorecard & Portability Verdict | Final scorecard, verdict, change control | **Closed** |

Detailed scope: [`readinessplan.md`](./readinessplan.md).

---

## 4. Document inventory (readiness pack)

| Document | Role | Introduced |
|----------|------|------------|
| [`readinessplan.md`](./readinessplan.md) | Full readiness program (M18–M24) | M18 |
| [`README.md`](./README.md) | Pack front door, authority, reading order | M18 |
| [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) | This ledger | M18 |
| [`READINESS_DECISIONS.md`](./READINESS_DECISIONS.md) | ADR-style readiness decisions | M18 |
| [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) | Frozen consumer boundary | **M19** |
| [`CLARITY_ASSUMED_GUARANTEES.md`](./CLARITY_ASSUMED_GUARANTEES.md) | Inherited vs CLARITY-owned guarantees | **M19** |
| [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) | Artifact inventory, serialization, contract identity | **M20** |
| [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) | Canonical Python consumer surface | **M21** |
| [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md) | Operator / AI-agent manual | **M22** |
| [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) | Honest status matrix | **M22** |
| [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md) | Explicit downstream assumptions (M19–M22) | **M23** |
| [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) | Combination truth table: Supported / Unsupported / Unknown | **M23** |
| [`CLARITY_TRANSFER_CHECKLIST.md`](./CLARITY_TRANSFER_CHECKLIST.md) | Adoption transfer checklist | **M23** |
| [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md) | Post-readiness change rules | **M24** |
| [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) | Final scorecard and verdict | **M24** |

---

## 5. Open risks / deferred issues

| ID | Risk / issue | Mitigation / next step | Target |
|----|----------------|------------------------|--------|
| R-001 | Readiness docs could drift from code | Milestone updates to ledger + `docs/clarity.md`; tests per milestone; **C-M24-002** in scorecard | Ongoing |
| R-002 | Dual location of plan (`docs/readinessplan.md` vs pack) | Canonical pack path documented in README; **C-M24-003** in scorecard | TBD |
| R-003 | Multiple `sweep_manifest.json` schema families (orchestrator vs rich aggregate) | Documented in `CLARITY_ARTIFACT_CONTRACT.md` §6.1; **C-M24-001** in scorecard | Accepted / monitored |

**M24 evaluation:** R-001–R-003 are **non-blockers** for an unconditional **`READY FOR DOWNSTREAM ADOPTION`** claim; they **are** conditions of the **`CONDITIONALLY READY`** verdict (see [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md)).

---

## 6. Evidence map

| Milestone | Evidence type | Location / gate |
|-----------|----------------|-----------------|
| M18 | Pack exists; ledger updated; lightweight test | `docs/readiness/*`, `backend/tests/test_readiness_pack.py`, CI |
| M19 | Frozen boundary + assumed guarantees; boundary tests | `CLARITY_BOUNDARY_CONTRACT.md`, `CLARITY_ASSUMED_GUARANTEES.md`, `backend/tests/test_boundary_contract.py` (incl. M19 section), CI |
| M20 | Frozen artifact contract; semantic + hash guardrails | `CLARITY_ARTIFACT_CONTRACT.md`, `backend/tests/test_artifact_contract.py`, CI |
| M21 | Frozen `app.clarity.public_surface`; smoke + export tests | [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md), `backend/tests/test_public_surface_contract.py`, CI |
| M22 | Operating manual + matrix; doc consistency tests | [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md), [`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md), `backend/tests/test_m22_operating_manual.py`, CI |
| M23 | Consumer assumptions + compatibility matrix + transfer checklist + `test_supported_combinations.py` | `CLARITY_CONSUMER_ASSUMPTIONS.md`, `CLARITY_COMPATIBILITY_MATRIX.md`, `CLARITY_TRANSFER_CHECKLIST.md`, `backend/tests/test_supported_combinations.py`, CI |
| M24 | Scorecard + change control + aggregate verdict test | `CLARITY_READINESS_SCORECARD.md`, `CLARITY_CHANGE_CONTROL.md`, `backend/tests/test_m24_readiness_verdict.py`, CI |

---

## 7. Final verdict

**Verdict:** **`CONDITIONALLY READY`**

**Allowed verdicts (per plan):** `READY FOR DOWNSTREAM ADOPTION` | `CONDITIONALLY READY` | `NOT READY`

**Authoritative detail:** [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) §8–§9 (explicit verdict and conditions).

**Post-readiness governance:** [`CLARITY_CHANGE_CONTROL.md`](./CLARITY_CHANGE_CONTROL.md).
