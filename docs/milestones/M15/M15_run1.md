# M15 Run 1 — UI Validation Analysis

## Run Metadata

| Field | Value |
|-------|-------|
| **Run** | 1 |
| **Type** | Local Validation (not CI) |
| **Date** | 2026-02-21 |
| **Branch** | `m15-ui-validation` |
| **Commit** | Pending (artifacts generated) |

---

## Phase 1: Real Artifact Generation

### Configuration

| Parameter | Value |
|-----------|-------|
| Image | `clinical_sample_01.png` (224x224) |
| Seeds | 42, 123 |
| Axes | brightness (0.8, 1.0, 1.2), contrast (0.9, 1.0, 1.1) |
| Total Runs | 12 |
| Rich Mode | Enabled |
| Model | `google/medgemma-4b-it` |

### Generated Artifacts

| Artifact | SHA256 (first 16 chars) |
|----------|-------------------------|
| sweep_manifest.json | `71c78d84cc0a67ed` |
| robustness_surface.json | `d3114c3d731f6953` |
| confidence_surface.json | `75d4c53c0e953252` |
| entropy_surface.json | `384f87de19801f89` |
| monte_carlo_stats.json | (included) |
| **Bundle SHA256** | `fa6fdb5dbe017076fd6cdf01f28f9a7773edef551e977b18bff918e1622d3236` |

### Determinism Verification

| Metric | Run 1 | Run 2 | Match |
|--------|-------|-------|-------|
| Summary Hash | `c52ead26746d2715...` | `c52ead26746d2715...` | ✅ |
| Bundle SHA | `fa6fdb5dbe017076...` | `fa6fdb5dbe017076...` | ✅ |

### VRAM Usage

| Metric | Value |
|--------|-------|
| Allocated | 8.02 GB |
| Max Allocated | 9.71 GB |
| Reserved | 9.86 GB |
| Budget | 12 GB |
| Status | ✅ PASS |

---

## Phase 2: Backend API Validation

### Test Results

| Test | Status |
|------|--------|
| Case listing | ✅ PASS (2 cases found) |
| Manifest loading | ✅ PASS (synthetic=False, rich_mode=True) |
| Robustness surface | ✅ PASS (2 axes, 6 points) |
| Metrics loading | ✅ PASS (CSI=1.0, 12 samples) |
| Overlay bundle | ✅ PASS |
| Checksum verification | ✅ PASS (4/4 files) |
| NaN value check | ✅ PASS (none found) |

### API Endpoints Tested

| Endpoint | Response |
|----------|----------|
| `GET /demo/cases` | 200 OK |
| `GET /demo/cases/case_m15_real/manifest` | 200 OK |
| `GET /demo/cases/case_m15_real/surface` | 200 OK |
| `GET /demo/cases/case_m15_real/metrics` | 200 OK |
| `GET /demo/cases/case_m15_real/overlay` | 200 OK |
| `GET /demo/cases/case_m15_real/verify` | 200 OK (valid=true) |

---

## Phase 3: Frontend Console Validation

### TypeScript/Lint

| Check | Result |
|-------|--------|
| `npm run typecheck` | ✅ PASS |
| `npm run lint` | ✅ PASS |
| `npm run test` | ✅ 137 passed |

### Backend Tests

| Result | Count |
|--------|-------|
| Passed | 910 |
| Skipped | 31 |
| Failed | 0 |

### Browser UI Validation

| Check | Status |
|-------|--------|
| Page loads | ✅ PASS |
| Console errors | ✅ None |
| React warnings | ✅ None |
| NaN values | ✅ None displayed |
| Undefined values | ✅ None displayed |
| Backend health | ✅ OK |
| API requests | ✅ All 200 |

### Pages Validated

- Homepage: ✅ Loads correctly
- Counterfactual Console: ✅ Loads correctly
- Baseline selector: 3 options available
- Axis selector: 4 options available
- Value selector: 5 options available

---

## Issues Fixed During Run

| Issue | Resolution |
|-------|------------|
| `case_001/checksums.json` outdated | Updated SHA256 hashes |

---

## Summary

All validation phases passed:

1. **Phase 1**: Real artifacts generated with deterministic hashes
2. **Phase 2**: Backend API loads all artifacts without errors
3. **Phase 3**: Frontend renders without console errors or NaN values
4. **Phase 4**: Skipped (per locked decision)

**Verdict**: ✅ PASS — Ready for governance close
