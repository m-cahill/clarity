# CLARITY_TRANSFER_CHECKLIST — Adoption handoff (Readiness)

## Document control

| Field | Value |
|-------|--------|
| **Introduced** | M23 — Consumer assumptions, compatibility matrix & transfer checklist |
| **Authority** | Operational checklist for a **consumer project** adopting CLARITY; subordinate to frozen contracts and [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) |
| **Readiness status** | **`READY FOR DOWNSTREAM ADOPTION`** (M25 — see [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md), [`READINESS_LEDGER.md`](./READINESS_LEDGER.md)) |

---

## 1. Purpose

This checklist turns [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md) and the **Supported / Unsupported / Unknown** table in [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) into an actionable **transfer** sequence. Complete items in order unless your project has a documented exception.

---

## 2. Before you integrate

### 2.1 Read and align

- [ ] Read **`docs/clarity.md`** (project ledger) and the readiness pack in the order given in [`README.md`](./README.md).
- [ ] Confirm **combination intent** against [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) (orchestrator-only vs full bundle; canonical vs rich vs HTTP).
- [ ] Understand **HTTP API is **not** readiness-canonical** for adoption ([`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §3).

### 2.2 Substrate and versions

- [ ] Record **R2L substrate** CLI / version / config you will use (see [`CLARITY_BOUNDARY_CONTRACT.md`](./CLARITY_BOUNDARY_CONTRACT.md) §4–5).
- [ ] Pin **adapter / model** identifiers if using real inference paths.
- [ ] Capture **Python** and **dependency** versions consistent with this repo’s backend (`requirements` / lockfiles as applicable).

### 2.3 Public surface only

- [ ] Import only from **`app.clarity.public_surface`** for governed adoption ([`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md)).
- [ ] Avoid importing other **`app.clarity`** submodules for portability (unless you accept **Unsupported** risk per matrix **C-006**).

---

## 3. Configuration and environment

- [ ] Set **`R2LRunner`** + **`SweepOrchestrator`** parameters per [`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §6–8 and operating manual.
- [ ] If using **rich / real-model** paths, set **`CLARITY_RICH_MODE`**, **`CLARITY_REAL_MODEL`**, and optional **`CLARITY_RICH_LOGITS_HASH`** only as documented ([`CLARITY_PUBLIC_SURFACE.md`](./CLARITY_PUBLIC_SURFACE.md) §7).
- [ ] Do **not** assume undeclared environment variables are part of the contract.

---

## 4. Artifact expectations

- [ ] **Orchestrator-only:** expect **`clarity/sweep_manifest.json`** (orchestrator schema family) after `SweepOrchestrator.execute` — see matrix **C-001 / C-002**.
- [ ] **Full analytical bundle:** plan for **three** JSON files per [`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) §3 and matrix **C-003 / C-004**; do **not** assume they appear without the **documented** downstream materialization steps.
- [ ] **Two schema families** for `sweep_manifest.json` — confirm producer before parsing ([`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) §6.1).
- [ ] Treat **PDFs / plots** as **presentation-oriented** unless your workflow promotes them ([`CLARITY_ARTIFACT_CONTRACT.md`](./CLARITY_ARTIFACT_CONTRACT.md) §5).

---

## 5. Validation steps (before you claim success)

- [ ] Run **local** tests or a **smoke** path using **`app.clarity.public_surface`** only (see `test_public_surface_contract.py` patterns).
- [ ] Verify **namespace:** outputs under **`clarity/`** for CLARITY-owned artifacts; no writes to R2L-owned top-level files.
- [ ] If using **rich / real** paths, record evidence (logs, manifests) and treat **Unknown** matrix rows as **not** proven until you replicate documented script/fixture behavior.
- [ ] Re-read [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md) — **Supported** rows only with evidence.

---

## 6. Non-goals / forbidden shortcuts

- [ ] Do **not** treat **demo HTTP** routes as your stable integration surface (matrix **C-007**).
- [ ] Do **not** widen **`app.clarity.public_surface`** exports without a governance milestone.
- [ ] Do **not** assume **orchestrator-only** runs satisfy **full-bundle** expectations.
- [ ] Do **not** redefine or overstate the **recorded** readiness verdict; authoritative verdict and conditions are in [`CLARITY_READINESS_SCORECARD.md`](./CLARITY_READINESS_SCORECARD.md) and [`READINESS_LEDGER.md`](./READINESS_LEDGER.md) §7.

---

## 7. Optional: demo / UI

- [ ] If using the **demo UI** for exploration, treat it as **product** surface, **not** the M21 contract ([`CLARITY_IMPLEMENTATION_STATUS.md`](./CLARITY_IMPLEMENTATION_STATUS.md) Matrix B/C).

---

## 8. Related documents

- [`CLARITY_CONSUMER_ASSUMPTIONS.md`](./CLARITY_CONSUMER_ASSUMPTIONS.md)  
- [`CLARITY_COMPATIBILITY_MATRIX.md`](./CLARITY_COMPATIBILITY_MATRIX.md)  
- [`CLARITY_OPERATING_MANUAL.md`](./CLARITY_OPERATING_MANUAL.md)  
