# M25 — Re-readiness inventory

Evidence-first mapping of M24 conditions to resolution (see scorecard §9 history).

| Condition | Ambiguity source (pre-M25) | Fix | Contract-affecting? | Proof |
|-----------|-----------------------------|-----|----------------------|--------|
| **C-M24-001** | Two `sweep_manifest.json` shapes without machine-readable producer ID | Top-level **`manifest_schema_family`** (`clarity_sweep_orchestrator_v1` / `clarity_rich_aggregate_v1`); `app/clarity/manifest_schema_family.py`; writers + fixtures | Yes (additive JSON field) | `test_artifact_contract.py`, `test_sweep_orchestrator.py`, `test_m25_readiness_upgrade.py` |
| **C-M24-002** | Doc/ledger/scorecard drift as adoption caveat | `test_m25_readiness_upgrade.py` + existing `test_m24_readiness_verdict.py` pack list includes addendum | No | Same + manual review |
| **C-M24-003** | Root vs pack `readinessplan.md` | Root file = **redirect stub** only | No (docs path hygiene) | Stub length & content test in `test_m25_readiness_upgrade.py` |

## Repository notes

- **M24 on `main`:** merge baseline `e1a6b54` (fast-forward from M23 merge `4469b2c`).
- **Legacy manifests:** `classify_sweep_manifest_json` retains heuristic for pre-M25 artifacts; new outputs must emit **`manifest_schema_family`**.
