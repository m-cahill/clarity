# CLARITY — Readiness ledger

## 1. Readiness objective

Make CLARITY **portable, governable, test-enforced, and legible** so a consumer project can adopt it **without ambiguity, contract drift, or hidden assumptions**—evidenced by frozen contracts, tests, and explicit verdicts—not narrative alone.

---

## 2. Current status

| Field | Value |
|-------|--------|
| **Readiness** | **`NOT READY`** |
| **Phase** | Readiness (M18–M24) |
| **As-of milestone** | M21 |
| **Notes** | Consumer boundary (M19), artifact contract (M20), and canonical Python public surface (M21) frozen. Operating manual, consumer kit, and M24 verdict still open. No final portability claim. |

---

## 3. Milestone roadmap (M18–M24)

| ID | Title | Purpose (summary) | Ledger status |
|----|-------|-------------------|----------------|
| **M18** | Readiness Charter & Authority Freeze | Create `docs/readiness/`, authority hierarchy, ledger + decisions; update `docs/clarity.md` | **Closed** |
| **M19** | Consumer Boundary Freeze | Freeze CLARITY↔R2L consumer boundary and inherited guarantees | **Closed** |
| **M20** | Artifact Contract & Deterministic Output Freeze | Freeze outputs, serialization, reproducibility | **Closed** |
| **M21** | Public Surface & Invocation Contract | Single official invocation path; public vs internal | **Closed** |
| **M22** | Operating Manual & Honest Implementation Matrix | Operable manual + implemented vs planned vs unknown | Planned |
| **M23** | Consumer Assumptions, Compatibility Matrix & Transfer Checklist | Consumer kit: assumptions, matrix, checklist | Planned |
| **M24** | Readiness Audit, Scorecard & Portability Verdict | Final scorecard, verdict, change control | Planned |

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
| `CLARITY_OPERATING_MANUAL.md` | Operator manual | M22 (planned) |
| `CLARITY_IMPLEMENTATION_STATUS.md` | Honest status matrix | M22 (planned) |
| `CLARITY_CONSUMER_ASSUMPTIONS.md` | Consumer assumptions | M23 (planned) |
| `CLARITY_COMPATIBILITY_MATRIX.md` | Compatibility matrix | M23 (planned) |
| `CLARITY_TRANSFER_CHECKLIST.md` | Transfer checklist | M23 (planned) |
| `CLARITY_CHANGE_CONTROL.md` | Post-readiness change rules | M24 (planned) |
| `CLARITY_READINESS_SCORECARD.md` | Final scorecard | M24 (planned) |

---

## 5. Open risks / deferred issues

| ID | Risk / issue | Mitigation / next step | Target |
|----|----------------|------------------------|--------|
| R-001 | Readiness docs could drift from code | Milestone updates to ledger + `docs/clarity.md`; tests per milestone | Ongoing |
| R-002 | Dual location of plan (`docs/readinessplan.md` vs pack) | Canonical pack path documented in README; deprecate root copy only in a later milestone if desired | TBD |
| R-003 | Multiple `sweep_manifest.json` schema families (orchestrator vs rich aggregate) | Documented in `CLARITY_ARTIFACT_CONTRACT.md` §6.1; consumers must not assume one shape | Accepted / monitored |

---

## 6. Evidence map

| Milestone | Evidence type | Location / gate |
|-----------|----------------|-----------------|
| M18 | Pack exists; ledger updated; lightweight test | `docs/readiness/*`, `backend/tests/test_readiness_pack.py`, CI |
| M19 | Frozen boundary + assumed guarantees; boundary tests | `CLARITY_BOUNDARY_CONTRACT.md`, `CLARITY_ASSUMED_GUARANTEES.md`, `backend/tests/test_boundary_contract.py` (incl. M19 section), CI |
| M20 | Frozen artifact contract; semantic + hash guardrails | `CLARITY_ARTIFACT_CONTRACT.md`, `backend/tests/test_artifact_contract.py`, CI |
| M21 | Frozen `app.clarity.public_surface`; smoke + export tests | [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md), `backend/tests/test_public_surface_contract.py`, CI |
| M22–M24 | Per `readinessplan.md` | TBD per milestone |

---

## 7. Final verdict (reserved for M24)

**Verdict:** _Reserved — not evaluated before M24._

Allowed final verdicts (per plan): `READY FOR DOWNSTREAM ADOPTION` | `CONDITIONALLY READY` | `NOT READY`.
