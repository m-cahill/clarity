# 📌 Milestone Summary — M13: MedGemma Integration & Empirical Validation

**Project:** CLARITY (Clinical Localization and Reasoning Integrity Testing)  
**Phase:** Empirical Transition  
**Milestone:** M13 — MedGemma Integration & Empirical Validation  
**Timeframe:** 2026-02-21  
**Status:** ✅ Closed  

---

## 1. Milestone Objective

M13 existed to transition CLARITY from **synthetic-only evaluation** to **empirical validation with real MedGemma inference**.

Prior to M13, all CLARITY evaluation used synthetic/stubbed model outputs. This satisfied architectural correctness but did not prove the system works with actual HAI-DEF (Health AI Developer Foundations) models required by the MedGemma Impact Challenge.

The objective was to:

1. Integrate real MedGemma inference via HuggingFace Transformers
2. Verify deterministic behavior (same seed → identical output)
3. Run a minimal empirical sweep (1 image, 2 seeds, 1 perturbation axis)
4. Preserve all CI invariants (synthetic path unchanged)

> **What would have been incomplete if this milestone did not exist?**
> CLARITY would remain a hardened instrument with synthetic signals only, failing to satisfy the competition's HAI-DEF model requirement.

---

## 2. Scope Definition

### In Scope

| Component | Description |
|-----------|-------------|
| `MedGemmaRunner` | New module for real MedGemma inference (`google/medgemma-4b-it`) |
| Determinism controls | Explicit seeding (`torch`, `numpy`, `random`), deterministic algorithms |
| Test fixtures | `clinical_sample_01.png`, `clinical_spec_01.json`, sweep artifacts |
| Real adapter tests | `test_real_adapter_determinism.py` (7 tests, gated by `CLARITY_REAL_MODEL`) |
| Sweep script | `m13_real_sweep.py` for empirical validation |
| Documentation | `M13_plan.md`, `M13_toolcalls.md`, `M13_run1.md`, `M13_audit.md` |

### Out of Scope

| Item | Reason |
|------|--------|
| Rich mode (`generate_rich()`) | Scope discipline; deferred to M14+ |
| Multi-axis high-resolution sweeps | Minimal sweep sufficient for validation |
| Performance benchmarking | Not required for competition |
| Fine-tuning | Not permitted by competition rules |
| Cloud GPU execution | Local GPU only for M13 |
| CI GPU requirements | CI remains synthetic; no workflow changes |

No scope changes occurred during execution.

---

## 3. Work Executed

### High-Level Actions

1. **Created `MedGemmaRunner` module** (424 lines)
   - HuggingFace model loading with `AutoModelForImageTextToText`
   - Deterministic seed control (torch, numpy, random)
   - VRAM monitoring via `get_vram_usage()`
   - Environment gate (`CLARITY_REAL_MODEL=true`)

2. **Implemented multimodal image handling**
   - Automatic `<start_of_image>` token insertion (Gemma3 format)
   - Fixed model ID from `medgemma-4b` to `medgemma-4b-it` (instruction-tuned)
   - Fixed Auto class from `Vision2Seq` to `ImageTextToText`

3. **Created test fixtures**
   - `clinical_sample_01.png` (224x224 synthetic clinical image)
   - `clinical_spec_01.json` (baseline specification)
   - Updated `registry.json` with new baseline

4. **Added determinism test suite**
   - 7 tests covering: same-seed hash, different-seed divergence, multimodal, VRAM, metadata, gating, sweep
   - All tests skip in CI (synthetic path preserved)

5. **Ran empirical validation**
   - 2 runs with identical manifest hash
   - VRAM: 8.17 GB max (within 12 GB budget)

### Files Changed

| Category | Count |
|----------|-------|
| Files changed | 17 |
| Lines added | 2,251 |
| Lines removed | 10 |
| New modules | 1 (`medgemma_runner.py`) |
| New tests | 1 (`test_real_adapter_determinism.py`) |

---

## 4. Validation & Evidence

### Tests Executed

| Environment | Result | Duration |
|-------------|--------|----------|
| CI (synthetic path) | 7 skipped (expected) | — |
| Local (CLARITY_REAL_MODEL=true) | 7 passed | 382.76s |

### Determinism Verification

| Run | Manifest Hash |
|-----|---------------|
| Run 1 | `01e9c46d1c18bc86d007abb7308b878aa704940cd79e091faec4959788455826` |
| Run 2 | `01e9c46d1c18bc86d007abb7308b878aa704940cd79e091faec4959788455826` |
| **Match** | ✅ Identical |

### Seed-Level Verification

| Seed | bundle_sha (Run 1) | bundle_sha (Run 2) | Match |
|------|--------------------|--------------------|-------|
| 42 | `194f1642b238fa84...` | `194f1642b238fa84...` | ✅ |
| 123 | `8f280dc3e69f5a70...` | `8f280dc3e69f5a70...` | ✅ |

### VRAM Verification

| Metric | Value | Budget | Status |
|--------|-------|--------|--------|
| Allocated | 8.02 GB | 12 GB | ✅ PASS |
| Max Allocated | 8.17 GB | 12 GB | ✅ PASS |

---

## 5. CI / Automation Impact

### Workflows Affected

**None.** CI workflows unchanged.

### Enforcement Behavior

| Check | Status |
|-------|--------|
| Real model tests in CI | Correctly skipped |
| Synthetic path preserved | ✅ |
| Coverage gates | No regression |
| Security scans | Clean |

### Signal Observation

- CI **validated correct changes** (all 8 jobs green)
- CI **correctly skipped** GPU-dependent tests
- No signal drift observed

---

## 6. Issues & Exceptions

### Issues Encountered

| Issue | Root Cause | Resolution |
|-------|------------|------------|
| HuggingFace authentication required | Gated model | Token saved via `HfFolder.save_token()` |
| `AutoModelForVision2Seq` incompatible | Gemma3 architecture | Changed to `AutoModelForImageTextToText` |
| Image token format incorrect | Processor expects `<start_of_image>` | Fixed prompt formatting |
| `accelerate` package missing | Required for `device_map="auto"` | Installed |

All issues were resolved during milestone execution.

### New Issues Introduced

> No new blocking issues were introduced during this milestone.

---

## 7. Deferred Work

| ID | Item | Status | Rationale |
|----|------|--------|-----------|
| ARCH-001 | Rich mode evidence ingestion | New deferral | Scope discipline; M14+ |
| PERF-001 | Model loading time (~4s) | New deferral | Acceptable for batch workflows |
| DX-001 | Windows symlink warning | New deferral | Cosmetic only |

No existing deferrals were closed in M13.

---

## 8. Governance Outcomes

### What Changed

| Before M13 | After M13 |
|------------|-----------|
| Synthetic-only evaluation | Real MedGemma inference validated |
| Competition HAI-DEF requirement unmet | ✅ Competition requirement satisfied |
| No empirical determinism proof | ✅ Determinism verified with hash evidence |
| Unknown VRAM requirements | ✅ VRAM budget confirmed (8.17 GB < 12 GB) |

### What Is Now Provably True

1. **CLARITY works with real MedGemma** — `google/medgemma-4b-it` integrated and functional
2. **Determinism is preserved** — Same (prompt, seed, image) → identical bundle hash
3. **VRAM is within budget** — 8.17 GB peak on RTX 5090, no OOM risk
4. **CI integrity is maintained** — Synthetic path unchanged, no workflow weakening
5. **Competition requirement is satisfied** — HAI-DEF model integrated per rules

---

## 9. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Real adapter invocation path implemented | ✅ Met | `MedGemmaRunner` module |
| Determinism regression test passing | ✅ Met | 7/7 tests pass locally |
| Minimal real sweep artifacts generated | ✅ Met | `sweep_manifest.json` created |
| sweep_manifest ledger entries recorded | ✅ Met | Hash: `01e9c46d...` |
| clarity.md updated | ✅ Met | M13 row marked closed |
| Tag `v0.0.14-m13` | ✅ Met | Tag pushed to remote |
| CI green | ✅ Met | 8/8 jobs passing |

All exit criteria met.

---

## 10. Final Verdict

**Milestone objectives met. Safe to proceed.**

M13 successfully transitions CLARITY from synthetic-only evaluation to empirical validation with real MedGemma inference. All governance invariants preserved. Competition HAI-DEF requirement satisfied. Determinism verified with cryptographic evidence.

**Score: 5.0** (no regression from M12)

---

## 11. Authorized Next Step

The following options are authorized for M14:

1. **Kaggle Packaging** — Prepare competition submission bundle
2. **Freeze for Submission** — Lock codebase, focus on documentation
3. **Rich Mode** — Enable `generate_rich()` path (higher risk)
4. **Multi-Axis Sweeps** — Expand robustness coverage (higher risk)

Given the competition deadline of **February 24, 2026** (3 days), low-risk options (1, 2) are recommended.

---

## 12. Canonical References

### Commits

| SHA | Message |
|-----|---------|
| `b42a29f` | M13: MedGemma integration scaffolding |
| `5e92e1f` | M13: Add CI run analysis (M13_run1.md) |
| `33eac3c` | Merge pull request #16 from m-cahill/m13-medgemma-integration |
| `1fe3da9` | M13: Fix MedGemma multimodal inference and verify determinism |
| `ad16a4e` | M13: Audit and governance close |

### Pull Requests

| PR | Title | Status |
|----|-------|--------|
| [#16](https://github.com/m-cahill/clarity/pull/16) | M13: MedGemma Integration | ✅ Merged |

### Tags

| Tag | Commit |
|-----|--------|
| `v0.0.14-m13` | `1fe3da9` |

### Documents

| Document | Purpose |
|----------|---------|
| [M13_plan.md](./M13_plan.md) | Milestone planning and scope |
| [M13_toolcalls.md](./M13_toolcalls.md) | Tool call log and recovery context |
| [M13_run1.md](./M13_run1.md) | CI run analysis |
| [M13_audit.md](./M13_audit.md) | Formal audit |
| [clarity.md](../../clarity.md) | Source of truth |

### CI Runs

| Run ID | Status |
|--------|--------|
| [22253280967](https://github.com/m-cahill/clarity/actions/runs/22253280967) | ✅ Green |

### Artifacts

| Artifact | Location |
|----------|----------|
| `sweep_manifest.json` | `backend/tests/fixtures/baselines/m13_real_sweep/` |
| `manifest_hash.txt` | `backend/tests/fixtures/baselines/m13_real_sweep/` |
| `clinical_sample_01.png` | `backend/tests/fixtures/baselines/` |

---

*Summary generated: 2026-02-21*

