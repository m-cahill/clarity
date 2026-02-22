# M15 Tool Calls Log

## Purpose

This file logs all tool invocations for M15 milestone execution. Each entry is recorded BEFORE the tool is run.

---

## Log

### Entry 1

- **Timestamp**: 2026-02-21T20:11:00Z
- **Tool**: Shell (mkdir)
- **Purpose**: Create M15 milestone folder
- **Files**: `docs/milestones/M15/`
- **Status**: ✅ Complete

### Entry 2

- **Timestamp**: 2026-02-21T20:11:30Z
- **Tool**: Write
- **Purpose**: Initialize M15_plan.md with locked scope
- **Files**: `docs/milestones/M15/M15_plan.md`
- **Status**: ✅ Complete

### Entry 3

- **Timestamp**: 2026-02-21T20:11:30Z
- **Tool**: Write
- **Purpose**: Initialize M15_toolcalls.md
- **Files**: `docs/milestones/M15/M15_toolcalls.md`
- **Status**: ✅ Complete

### Entry 4

- **Timestamp**: 2026-02-21T20:12:00Z
- **Tool**: Shell (git checkout)
- **Purpose**: Create m15-ui-validation branch
- **Files**: N/A
- **Status**: ✅ Complete

### Entry 5

- **Timestamp**: 2026-02-21T20:12:30Z
- **Tool**: Task (explore)
- **Purpose**: Explore sweep artifact generation, backend API, frontend rendering
- **Files**: Codebase analysis
- **Status**: ✅ Complete

### Entry 6

- **Timestamp**: 2026-02-21T20:15:00Z
- **Tool**: Read
- **Purpose**: Analyze existing artifact structures and M14 rich generation code
- **Files**: `demo_artifacts/case_001/*`, `backend/app/clarity/surfaces.py`, `rich_generation.py`, `medgemma_runner.py`
- **Status**: ✅ Complete

### Entry 7

- **Timestamp**: 2026-02-21T20:20:00Z
- **Tool**: Write
- **Purpose**: Create M15 artifact generation script
- **Files**: `backend/scripts/m15_real_ui_sweep.py`
- **Status**: ✅ Complete

### Entry 8

- **Timestamp**: 2026-02-21T20:25:00Z
- **Tool**: Glob, Shell
- **Purpose**: Verify clinical sample image exists; create if missing
- **Files**: `backend/tests/fixtures/baselines/clinical_sample_01.png`
- **Status**: ✅ Complete (created 224x224 clinical sample image)

---

## Phase 1 Checkpoint — Ready for GPU Execution

**Status**: Script prepared, awaiting GPU execution.

**Next Step**: Run the M15 artifact generation script locally with GPU:

```powershell
cd c:\coding\clarity\backend
$env:CLARITY_REAL_MODEL="true"
$env:CLARITY_RICH_MODE="true"
python -m scripts.m15_real_ui_sweep
```

**Expected Output**:
- `backend/tests/fixtures/baselines/m15_real_ui/sweep_manifest.json`
- `backend/tests/fixtures/baselines/m15_real_ui/robustness_surface.json`
- `backend/tests/fixtures/baselines/m15_real_ui/confidence_surface.json`
- `backend/tests/fixtures/baselines/m15_real_ui/entropy_surface.json`
- `backend/tests/fixtures/baselines/m15_real_ui/monte_carlo_stats.json`
- `backend/tests/fixtures/baselines/m15_real_ui/summary_hash.txt`

**Determinism Verification**: Run twice; compare `summary_hash.txt` bundle SHA256.

### Entry 9

- **Timestamp**: 2026-02-21T20:35:00Z
- **Tool**: GPU Execution (user)
- **Purpose**: Run M15 artifact generation script
- **Files**: `backend/tests/fixtures/baselines/m15_real_ui/*`
- **Status**: ✅ Complete

**Phase 1 Results**:
- Bundle SHA256: `fa6fdb5dbe017076fd6cdf01f28f9a7773edef551e977b18bff918e1622d3236`
- Summary hash: `c52ead26746d271526b05831f4b34de275fb2c620d69c85bb31a0e4cb5652fa1` (stable)
- VRAM: 9.71 GB max
- Runs: 12 (2 axes × 3 values × 2 seeds)
- Artifacts: 6 files generated

---

## Phase 2 — Backend API Validation

### Entry 10

- **Timestamp**: 2026-02-21T20:40:00Z
- **Tool**: Shell, Read, Write
- **Purpose**: Validate backend API loads real artifacts correctly
- **Files**: `demo_artifacts/case_m15_real/*`, `backend/scripts/m15_api_validation.py`
- **Status**: ✅ Complete

**Phase 2 Results**:
- Created `demo_artifacts/case_m15_real/` with manifest, surfaces, metrics, overlay, checksums
- 7 validation tests passed:
  - Case listing: case_m15_real found
  - Manifest loading: synthetic=False, rich_mode=True
  - Robustness surface: 2 axes, 3 points each, no missing fields
  - Metrics: global_mean_csi=1.0, 12 monte_carlo samples
  - Overlay bundle: loads without error
  - Checksums: all 4 files verified
  - NaN check: no NaN values in surfaces

---

## Phase 3 — Frontend Console Validation

### Entry 11

- **Timestamp**: 2026-02-21T20:50:00Z
- **Tool**: Shell, npm, browser-use
- **Purpose**: Validate frontend loads and renders real artifacts
- **Files**: Frontend components
- **Status**: ✅ Complete

**Phase 3 Results**:
- TypeScript typecheck: PASS
- Frontend tests: 137 passed (9 test files)
- Frontend lint: PASS
- Backend tests: 910 passed, 31 skipped (fixed checksum.json in case_001)
- Browser UI validation:
  - Zero JavaScript errors
  - Zero React warnings
  - No NaN values displayed
  - No undefined values displayed
  - Backend health: OK
  - Demo cases API: 2 cases (case_001, case_m15_real)
  - Counterfactual console: renders correctly
  - All API requests: 200 OK

---

## Phase 4 — SKIPPED (Per Locked Decision)

Stress testing skipped for deadline discipline.

---

## Phase 5 — Governance Close

### Entry 12

- **Timestamp**: 2026-02-21T21:00:00Z
- **Tool**: Write, Shell
- **Purpose**: Create governance documents and prepare for close
- **Files**: `M15_run1.md`, `M15_audit.md`, `M15_summary.md`
- **Status**: 🔄 In Progress
