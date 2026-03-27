# M24 — Readiness evidence inventory

**Purpose:** Audit-chain map from readiness criteria → governing docs → tests/CI → preliminary impact on verdict.  
**Authority:** Working note for **M24**; subordinate to [`CLARITY_READINESS_SCORECARD.md`](../../readiness/CLARITY_READINESS_SCORECARD.md).

---

## Scoring categories (locked)

| Category | Governing docs | Code / test evidence | Confidence | Blocker? | Verdict impact |
|----------|----------------|----------------------|------------|----------|----------------|
| **Identity clarity** | `docs/clarity.md`, `README.md`, `readinessplan.md` | `test_readiness_pack.py` | High | No | R-002 reduces score; pack authority clear |
| **Boundary contract** | `CLARITY_BOUNDARY_CONTRACT.md`, `CLARITY_ASSUMED_GUARANTEES.md` | `test_boundary_contract.py` | High | No | Strong |
| **Artifact contract** | `CLARITY_ARTIFACT_CONTRACT.md` | `test_artifact_contract.py`, fixtures | High | No (borderline) | R-003: two `sweep_manifest.json` families documented §6.1; consumer must classify producer — **conditional** posture |
| **Public surface** | `CLARITY_PUBLIC_SURFACE.md`, `public_surface.py` | `test_public_surface_contract.py` | High | No | Strong |
| **Operating manual** | `CLARITY_OPERATING_MANUAL.md` | `test_m22_operating_manual.py` | High | No | R-001 ongoing drift risk — score impact |
| **Compatibility / consumer kit** | `CLARITY_CONSUMER_ASSUMPTIONS.md`, `CLARITY_COMPATIBILITY_MATRIX.md`, `CLARITY_TRANSFER_CHECKLIST.md` | `test_supported_combinations.py` | High | No | Matrix + §6.1 cross-reference contain R-003 |
| **CI & guardrails** | Pack + `READINESS_LEDGER.md` evidence map | M18–M23 test modules + `test_m24_readiness_verdict.py` | High | No | Aggregate M24 check added |
| **Deferred issue posture** | `READINESS_LEDGER.md` §5, this repo’s deferred tables | Ledger + scorecard | Medium | No | R-001–R-003 evaluated; none block **READY** in isolation per M24 decision |

---

## Risk IDs (ledger §5)

| ID | Evaluation | Classification |
|----|------------|----------------|
| **R-001** | Docs vs code drift | Non-blocker; governance durability / manual operability score impact |
| **R-002** | Dual `readinessplan.md` location | Non-blocker; identity / coherence score impact; canonical path documented |
| **R-003** | Two `sweep_manifest.json` schema families | Borderline → **non-blocker** for verdict because artifact contract §6.1 + compatibility matrix + transfer checklist make the rule explicit; residual **conditional** obligation on consumers to know producer context |

---

## Non-readiness (contextual)

| ID | Role in M24 |
|----|-------------|
| **GOV-001** | Branch protection — infra; scorecard **Non-readiness risks** only |
| **SEC-001** | CORS posture — security hygiene; not a consumer-contract blocker for portability |

---

## Question for audit

> Can a new repository safely use CLARITY using **only** the readiness pack?

**Answer:** Yes **if** the consumer follows the frozen contracts, compatibility matrix, transfer checklist, and **explicitly** applies [`CLARITY_ARTIFACT_CONTRACT.md`](../../readiness/CLARITY_ARTIFACT_CONTRACT.md) §6.1 when parsing `sweep_manifest.json`. Residual governance and schema-classification obligations prevent a clean **`READY FOR DOWNSTREAM ADOPTION`** without conditions — see scorecard **§8 (Explicit verdict)** and **§9 (Conditions)**.
