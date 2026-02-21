# M13 — MedGemma Integration & Empirical Validation

**Mode:** DELTA AUDIT milestone  
**Baseline:** `v0.0.13-m12`  
**Target Tag:** `v0.0.14-m13`  
**Score Target:** ≥ 5.0 (no regression)

---

## 1. Milestone Objective

Replace synthetic adapter outputs with real MedGemma inference via R2L, generating:

- Real artifact bundles
- Real evidence overlays
- Real ESI + drift metrics
- Real robustness surfaces

**Without:**

- Modifying R2L semantics
- Introducing nondeterminism
- Weakening CI determinism gates
- Breaking demo deployment

This is a **consumer integration milestone**, not an architectural one.

If this milestone did not exist, CLARITY would remain a hardened instrument with synthetic signals only. M13 satisfies the competition requirement: **must use at least one HAI-DEF model**.

---

## 2. Locked Decisions

### 2.1 Model Source

| Field | Value |
|-------|-------|
| Model ID | `google/medgemma-4b` |
| Source | HuggingFace Transformers |
| Execution | Local GPU inference (RTX 5090) |
| Caching | Downloaded once, cached locally |

### 2.2 Adapter Mode

| Field | Value |
|-------|-------|
| Mode | Canonical `generate()` only |
| Rich Mode | Disabled (deferred to M14+) |
| Output | Text only |

### 2.3 Test Scope

| Field | Value |
|-------|-------|
| Images | 1 (fixture image) |
| Seeds | 2 |
| Perturbation Axes | 1 (minimal grid) |
| Total Runs | 2–4 |

### 2.4 CI Policy

| Field | Value |
|-------|-------|
| CI Path | Synthetic (unchanged) |
| Real Model Gate | `CLARITY_REAL_MODEL=true` |
| GPU Required | No (CI remains CPU-only) |

---

## 3. Strict Scope

### 3.1 In Scope

1. **Adapter Wiring**
   - Implement `MedGemmaAdapter` in R2L environment (if not present)
   - Wire to `google/medgemma-4b` via HuggingFace Transformers
   - Implement canonical `generate(prompt, seed)` method

2. **Determinism Enforcement**
   - Explicit seed control for all random sources
   - Deterministic CUDA operations
   - Fixed decoding parameters (temperature=0, no sampling)

3. **Minimal Real Sweep**
   - 1 fixture image
   - 2 seeds
   - 1 perturbation axis (e.g., blur radius small/medium)
   - Generate full artifact chain

4. **Artifact Production**
   - `sweep_manifest.json` with real hashes
   - `robustness_surface.json`
   - `monte_carlo_stats.json`
   - Evidence overlays

5. **Metadata Recording**
   - `model_id: "google/medgemma-4b"`
   - `execution_device: "cuda"`
   - `transformers_version`
   - `torch_version`
   - `r2l_git_sha`
   - `seed_list`

6. **Determinism Regression Test**
   - `test_real_adapter_determinism.py`
   - Assert identical bundle SHA for same `(image, prompt, seed)`
   - Skip in CI unless `CLARITY_REAL_MODEL=true`

### 3.2 Out of Scope

| Item | Rationale |
|------|-----------|
| Fine-tuning | Not M13 objective |
| Performance benchmarking | Not M13 objective |
| Hyperparameter optimization | Not M13 objective |
| UI redesign | Not M13 objective |
| Cloud GPU execution | Local only |
| Multi-axis high-resolution sweeps | Minimal scope |
| Competition packaging narrative | Post-M13 |
| `generate_rich()` / attention ingestion | Deferred to M14+ |
| R2L modifications | Contract violation |

---

## 4. Contract Guardrails (Non-Negotiable)

From `CLARITY_ARCHITECHTURE_CONTRACT.MD`:

1. **CLARITY must not modify R2L execution semantics**
2. **Monte Carlo = external seed enumeration**
3. **No overwrite of R2L artifacts**
4. **Rich mode remains optional**

### 4.1 New Guardrail Test (M13)

File: `backend/tests/test_real_adapter_determinism.py`

```python
@pytest.mark.skipif(
    not os.getenv("CLARITY_REAL_MODEL"),
    reason="Real model tests require CLARITY_REAL_MODEL=true"
)
def test_real_adapter_determinism():
    """
    Given:
      same image
      same prompt
      same seed

    Then:
      artifact bundle SHA is identical
    """
    # Run 1
    result1 = run_medgemma_adapter(image, prompt, seed=42)
    
    # Run 2
    result2 = run_medgemma_adapter(image, prompt, seed=42)
    
    assert result1.bundle_sha == result2.bundle_sha
```

**Failing this blocks merge.**

---

## 5. Determinism Strategy

### 5.1 Random Source Control

```python
import random
import numpy as np
import torch

def set_deterministic_seed(seed: int) -> None:
    """Set all random sources to deterministic state."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def enable_deterministic_mode() -> None:
    """Enable PyTorch deterministic operations."""
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

### 5.2 Decoding Parameters

```python
generation_config = {
    "temperature": 0.0,
    "top_p": 1.0,
    "do_sample": False,
    "max_new_tokens": 512,
}
```

No sampling. No beam randomness. Fully deterministic.

### 5.3 Inference Mode

```python
with torch.no_grad():
    output = model.generate(**inputs, **generation_config)
```

No gradient tracking. VRAM budget: ≤ 12GB for batch=1.

---

## 6. Test Image Fixture

Use or create:

```
backend/tests/fixtures/clinical_sample_01.png
```

Requirements:
- Deterministic (frozen in repo)
- Grayscale clinical-style (synthetic acceptable)
- 224×224 or 512×512
- No external dataset pulls

If fixture does not exist, create minimal synthetic image and commit.

---

## 7. Verification Plan

### Step 1 — Local GPU Verification

- [ ] Confirm model loads on RTX 5090
- [ ] Confirm memory fits with batch=1
- [ ] Record peak VRAM

### Step 2 — Determinism Check

Run same spec twice. Assert identical:

- [ ] `manifest.json`
- [ ] `trace_pack.jsonl`
- [ ] `evaluation_record`
- [ ] Bundle SHA256

### Step 3 — Minimal Sweep

- [ ] 1 image
- [ ] 2 seeds
- [ ] 1 perturbation axis
- [ ] Generate ESI, drift metrics, robustness surface
- [ ] Verify `sweep_manifest.json` stable ordering
- [ ] Verify float serialization stable

### Step 4 — CI Strategy

- [ ] CI continues synthetic path
- [ ] Real model gated: `CLARITY_REAL_MODEL=true`
- [ ] Determinism test skipped in CI (no GPU)
- [ ] No CI weakening

---

## 8. Deliverables

| Artifact | Status Required |
|----------|-----------------|
| `MedGemmaAdapter` implementation | Implemented |
| Determinism regression test | Passing (locally) |
| Minimal real sweep artifacts | Generated |
| `sweep_manifest.json` ledger entries | Recorded |
| `docs/clarity.md` updated | Yes |
| Tag `v0.0.14-m13` | Created |
| CI green | Required |

---

## 9. Execution Phases

### Phase 1 — Adapter Wiring (1–2 hours)

- Confirm MedGemma adapter loads via R2L
- Implement `MedGemmaAdapter.generate(prompt, seed)` 
- Confirm canonical generate() path works
- Record model loading time and VRAM

### Phase 2 — Determinism Validation (1 hour)

- Add `test_real_adapter_determinism.py`
- Run twice with same inputs
- Verify stable hash
- Document any platform-specific considerations

### Phase 3 — Minimal Real Sweep (2–3 hours)

- Create/verify fixture image
- Configure minimal sweep: 1 image, 2 seeds, 1 axis
- Execute sweep
- Generate full artifact chain:
  - `sweep_manifest.json`
  - `robustness_surface.json`
  - `monte_carlo_stats.json`
  - Evidence overlays
- Verify determinism across runs

### Phase 4 — Governance Close (1 hour)

- Update `docs/clarity.md` (add M13 row)
- Commit all artifacts
- Run CI (verify green)
- Tag release `v0.0.14-m13`

---

## 10. Acceptance Criteria

| Criterion | Verification |
|-----------|--------------|
| MedGemma adapter invocable | Local test passes |
| Determinism verified | Same seed → identical hash |
| Minimal sweep completed | Artifacts exist |
| sweep_manifest.json valid | Schema validated |
| No R2L modifications | Code review |
| CI green | GitHub Actions |
| No new deferrals | Audit confirms |
| Score ≥ 5.0 | Audit confirms |

---

## 11. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Model download fails | Pre-download and cache locally |
| VRAM exceeds budget | Use `torch.float16` if needed |
| Nondeterminism detected | Investigate CUDA ops; use CPU fallback if blocked |
| CI regression | Real tests skip in CI; synthetic path unchanged |
| Adapter interface mismatch | Verify R2L adapter contract first |

---

## 12. What We Will NOT Do

We will NOT:

- Increase sweep dimensionality
- Tune decoding parameters beyond determinism needs
- Add new metrics
- Modify R2L internals
- Add GPU requirement to CI
- Enable `generate_rich()`
- Pull external datasets
- Expand scope for competition narrative

This is an integration milestone only.

---

## 13. Close Conditions

M13 closes when:

1. ✅ MedGemma adapter invocable with real model
2. ✅ Determinism test passes locally
3. ✅ Minimal real sweep artifacts generated
4. ✅ CI green (synthetic path)
5. ✅ `clarity.md` updated
6. ✅ Tag `v0.0.14-m13` created
7. ✅ No new deferrals introduced
8. ✅ Audit verdict: PASS

---

## 14. References

| Document | Purpose |
|----------|---------|
| `CLARITY_ARCHITECHTURE_CONTRACT.MD` | Boundary contract |
| `CLARITY_CAPABILITY_CONTEXT.md` | R2L context |
| `COMPLETE_RULES.md` | Competition rules |
| `M12_summary.md` | Baseline state |
| `M12_audit.md` | Governance posture |

---

*Plan generated following milestone workflow process.*

