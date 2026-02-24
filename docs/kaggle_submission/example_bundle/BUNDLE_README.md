# CLARITY — Example Artifact Bundle

## Source

This bundle contains the canonical baseline artifacts from the **M15 Real Artifact UI Validation** sweep.

These are the authoritative, hash-verified outputs of CLARITY's evaluation of `google/medgemma-4b-it` under structured perturbation sweeps.

**Bundle SHA256**: `26de75db866aafa813cb25ef63ee3c1f34e14eda0d07d7de567957d2d46a58bc`

---

## Bundle Contents

| File | Description |
|------|-------------|
| `sweep_manifest.json` | Full sweep configuration and per-run results |
| `robustness_surface.json` | ESI and drift metrics per perturbation axis |
| `confidence_surface.json` | CSI and confidence statistics per perturbation axis |
| `entropy_surface.json` | EDM and entropy statistics per perturbation axis |
| `monte_carlo_stats.json` | Monte Carlo sampling statistics |
| `BUNDLE_README.md` | This file |

---

## Sweep Configuration

| Parameter | Value |
|-----------|-------|
| Model | `google/medgemma-4b-it` |
| Perturbation axes | brightness, contrast |
| Levels per axis | 3 |
| Seeds | 42, 123 |
| Total inference runs | 12 |
| Rich mode | Enabled |
| VRAM peak | 9.71 GB |

---

## Artifact Hashes

| Artifact | SHA256 |
|----------|--------|
| `sweep_manifest.json` | `e3f355b60133587868494d553bdac3e787202550e3b4b1ebe9421f20b8a42e71` |
| `robustness_surface.json` | `5b6b2e7f4ba49c16963187318682950814b50995db8a465b4c01a26b438ee62e` |
| `confidence_surface.json` | `cc33deca4dbf408068623c5c8f026da65aa5841bc8dc6c1e3065ce1caa8c585e` |
| `entropy_surface.json` | `5c23324ff401c360ac22688c6bb8f61b82abfe30ed09efe18e3de99a84fd8451` |
| **Bundle SHA256** | `26de75db866aafa813cb25ef63ee3c1f34e14eda0d07d7de567957d2d46a58bc` |

**Logit summary hash** (identical across all 12 runs):
`fba587054c9f63149eba704a703fa8bcb4c5a2d2f96997857fba5c9a8d6166e6`

---

## Key Findings

### Model Output (Validated Non-Degenerate)

| Metric | Value |
|--------|-------|
| **Mean logprob** | -0.2155304 |
| **Output entropy** | 4.99646272 |
| **Confidence score** | 0.80611376 |
| **Token count** | 342 |
| **Text** | `"Based on the chest X-ray image provided, here's an analysis:..."` |

### Robustness Surface (`robustness_surface.json`)

- **Global mean ESI**: 0.80611376 (confidence-derived)
- **Global mean drift**: 0.0
- **Variance ESI**: 0.0

MedGemma's reasoning was invariant under tested brightness and contrast variations — the model produced identical text output across all perturbation levels. The flat ESI surface and zero drift establish a stable operating envelope for this perturbation family.

### Confidence Surface (`confidence_surface.json`)

- **Global mean CSI**: 1.0
- **Global mean confidence**: 0.80611376

CSI = 1.0 with a real confidence of 0.806 indicates perfect confidence stability — the model's certainty in its output does not shift under mild image-quality perturbations.

### Entropy Surface (`entropy_surface.json`)

- **Output entropy**: 4.99646272 (real, non-degenerate)

The model's output distribution entropy is consistent at ~5.0 nats across all perturbation levels and seeds, indicating stable but not overconfident generation.

---

## Interpretation

These results establish a quantitative robustness baseline for MedGemma under mild brightness and contrast perturbations. The model produces real diagnostic language (`confidence = 0.806`, `entropy = 4.997`, `token_count = 342`) and that output is completely invariant across the tested perturbation range — the logit summary hash is identical across all 12 inference runs. This is a meaningful scientific finding: MedGemma's reasoning about this normal chest radiograph is robust to the brightness/contrast perturbation family within the tested parameter range.

---

## Reproducibility

To reproduce this bundle from scratch:

```bash
git clone https://github.com/m-cahill/clarity.git
cd clarity
pip install -r requirements.lock
$env:CLARITY_REAL_MODEL = "true"
$env:CLARITY_RICH_MODE = "true"
python backend/scripts/m15_real_ui_sweep.py
```

See `docs/kaggle_submission/README_KAGGLE.md` for full reproducibility instructions and hash verification steps.
