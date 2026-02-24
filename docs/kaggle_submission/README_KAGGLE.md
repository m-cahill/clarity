# CLARITY — Clinical Localization and Reasoning Integrity Testing

### A Deterministic Robustness Evaluation Instrument for Multimodal Clinical AI

**MedGemma Impact Challenge — Kaggle Submission**

---

## 1. Problem Statement

### What CLARITY Measures

Standard clinical AI evaluation answers one question: *is the model accurate?* CLARITY asks a harder and more clinically relevant question:

> **Can a multimodal clinical AI localize, justify, and maintain region-level evidence stability for diagnostic statements under structured perturbation sweeps?**

Real-world clinical images are rarely ideal. Emergency chest X-rays contain monitoring leads. Motion blur degrades edge definition. Scanner artifacts shift pixel statistics. A model that is accurate on clean images but whose reasoning collapses under predictable distortions is not a reliable instrument for clinical use.

CLARITY measures **reasoning robustness** — not just output accuracy. It quantifies whether a model's evidence localization, justification coherence, and confidence signals remain stable as image quality degrades along clinically grounded perturbation axes.

### Why Robustness Matters in Clinical AI

Accuracy is a point estimate. Robustness is a surface. A model that achieves 90% accuracy but whose reasoning drifts catastrophically under mild occlusion or brightness shifts has a hidden failure mode that accuracy alone cannot detect. CLARITY makes that failure mode visible, measurable, and reproducible.

This is the critical gap CLARITY addresses: **the absence of structured, deterministic robustness characterization** in clinical AI evaluation workflows.

---

## 2. Methodology

### 2.1 Perturbation Sweeps

CLARITY sweeps across parameterized perturbation axes:

| Axis | Range | Clinical Analog |
|------|-------|----------------|
| Brightness | 0.8 – 1.2 | Scanner exposure variation |
| Contrast | 0.9 – 1.1 | Device calibration drift |
| Occlusion | Configurable | Monitoring leads, artifacts |
| Blur | Configurable | Motion, focus degradation |

For each axis, CLARITY runs inference at N perturbation levels across K random seeds, producing a structured grid of outputs that can be analyzed as a continuous robustness surface.

The M15 validated sweep covers:
- **2 perturbation axes** (brightness, contrast)
- **3 intensity levels per axis**
- **2 random seeds** (42, 123)
- **12 total inference runs**
- **Model**: `google/medgemma-4b-it`

### 2.2 Evidence Sensitivity Index (ESI)

The Evidence Sensitivity Index quantifies diagnostic slope sensitivity:

$$\text{ESI} = \frac{\Delta D}{\Delta P}$$

Where:
- $\Delta D$ = change in diagnosis confidence or probability
- $\Delta P$ = perturbation magnitude

Low ESI → stable reasoning. High ESI → fragile reasoning. A diagnostic cliff is a region of the perturbation surface where ESI spikes — indicating a sudden, non-linear collapse in reasoning quality.

### 2.3 Drift Metrics

Justification drift measures semantic coherence of the model's reasoning across perturbation levels. CLARITY tracks:

- **Token-level probability shifts** across perturbation variants
- **Output entropy** as a function of perturbation magnitude
- **Summary hash stability** — identical reasoning outputs across seeds produce identical SHA256 hashes

### 2.4 Confidence Stability Index (CSI)

CSI measures the variance of model confidence across a perturbation axis:

$$\text{CSI} = 1 - \frac{\sigma^2(\text{confidence})}{\max(\sigma^2)}$$

CSI = 1.0 indicates perfect confidence stability. CSI < 1.0 quantifies confidence surface roughness.

In the M15 sweep, CSI = **1.0** across both axes — indicating that MedGemma's confidence signal did not vary under the tested brightness and contrast perturbations.

### 2.5 Entropy Distribution Metric (EDM)

EDM tracks how model output entropy changes across perturbation levels. A flat entropy surface indicates the model's uncertainty distribution is invariant to the perturbation. A rising entropy surface indicates increasing output instability.

### 2.6 Counterfactual Probe

To test causal grounding:

1. Identify the model's claimed evidence region
2. Mask that region (deterministic inpainting)
3. Re-run inference
4. Measure diagnosis delta

This tests whether the model's diagnostic conclusion causally depends on its stated evidence. A model that cites region R but whose diagnosis is unchanged when R is masked is not causally grounded — it is producing post-hoc rationalization.

---

## 3. Determinism Strategy

Reproducibility is a first-class requirement of CLARITY, not an afterthought. Every inference run, perturbation, and artifact is seed-controlled and hash-verified.

### 3.1 Seed Enumeration

All stochastic elements are controlled:

```python
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
numpy.random.seed(seed)
random.seed(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

Two seeds (42 and 123) are run for every perturbation level. Identical SHA256 hashes across seeds confirm that seed variation does not introduce output drift.

### 3.2 Hash Verification

Every artifact bundle is SHA256-sealed at generation time. The bundle hash is computed over the concatenated content of all JSON artifacts (manifest + surfaces + metrics), normalized for cross-platform line endings (CRLF → LF).

**Canonical Hashes (bfloat16, real PA chest X-ray, chat-template prompt):**

| Artifact | SHA256 |
|----------|--------|
| `sweep_manifest.json` | `e3f355b60133587868494d553bdac3e787202550e3b4b1ebe9421f20b8a42e71` |
| `robustness_surface.json` | `5b6b2e7f4ba49c16963187318682950814b50995db8a465b4c01a26b438ee62e` |
| `confidence_surface.json` | `cc33deca4dbf408068623c5c8f026da65aa5841bc8dc6c1e3065ce1caa8c585e` |
| `entropy_surface.json` | `5c23324ff401c360ac22688c6bb8f61b82abfe30ed09efe18e3de99a84fd8451` |
| **Bundle SHA256** | `26de75db866aafa813cb25ef63ee3c1f34e14eda0d07d7de567957d2d46a58bc` |

### 3.3 Logits Summary Stability

The model's output logit distribution is summarized at inference time. The summary hash:

```
fba587054c9f63149eba704a703fa8bcb4c5a2d2f96997857fba5c9a8d6166e6
```

was **identical across all 12 inference runs** — 2 axes × 3 levels × 2 seeds. This is the strongest possible evidence of deterministic inference.

Key signal metrics from the validated sweep:

| Metric | Value |
|--------|-------|
| Mean logprob | -0.2155304 |
| Output entropy | 4.99646272 |
| Confidence score | 0.80611376 |
| Token count | 342 |
| VRAM peak | 9.14 GB |

---

## 4. Evidence Stability Concepts

### 4.1 The Confidence Surface

A confidence surface maps model confidence as a function of perturbation parameters. In a robust model, this surface is flat — confidence does not depend on minor image quality variations. In a fragile model, the surface has cliffs and valleys where small perturbation changes cause large confidence drops.

CLARITY renders the confidence surface in its UI console as an interactive heatmap, allowing visual inspection of stability topology.

### 4.2 The Entropy Surface

The entropy surface maps output token distribution entropy across perturbation levels. High entropy indicates the model is uncertain about its output vocabulary — it is "hedging." Low, stable entropy indicates consistent, confident generation regardless of perturbation.

### 4.3 Stability vs. Accuracy

This is the central conceptual distinction of CLARITY:

> **Stability is not accuracy. A model can be stable and wrong, or accurate and unstable.**

Accuracy measures the relationship between model output and ground truth. Stability measures the internal consistency of the model's reasoning across a perturbation family. A model that is stable but wrong has systematic bias. A model that is accurate but unstable has learned brittle features that happen to be correct on the test distribution.

Clinical AI requires both. CLARITY measures the stability dimension — the dimension that standard benchmarks ignore.

---

## 5. Reproducibility Instructions

### Prerequisites

```
GPU:     NVIDIA RTX 5090 (or equivalent with ≥12 GB VRAM)
OS:      Windows 11 / Ubuntu 22.04+
Python:  3.10 / 3.11 / 3.12
CUDA:    12.x
```

### Step 1 — Clone Repository

```bash
git clone https://github.com/m-cahill/clarity.git
cd clarity
```

### Step 2 — Install Dependencies (Deterministic Lockfile)

```bash
pip install -r requirements.lock
```

The lockfile (`requirements.lock`) contains pip-compiled, hash-verified pinned dependencies. This is the only approved installation path for reproducibility.

### Step 3 — Set Environment Variables

```bash
export CLARITY_REAL_MODEL=true
export CLARITY_RICH_MODE=true
```

On Windows PowerShell:

```powershell
$env:CLARITY_REAL_MODEL = "true"
$env:CLARITY_RICH_MODE = "true"
```

### Step 4 — Run the M15 Validation Sweep

```bash
python backend/scripts/m15_real_ui_sweep.py
```

This executes 12 inference runs (2 axes × 3 levels × 2 seeds) against `google/medgemma-4b-it`.

Expected runtime: ~10–15 minutes on RTX 5090.

Expected VRAM: max 9.71 GB allocated.

### Step 5 — Verify Hashes

After completion, verify:

```bash
python -c "
import hashlib, json, pathlib

base = pathlib.Path('backend/tests/fixtures/baselines/m15_real_ui')
files = ['sweep_manifest.json', 'robustness_surface.json',
         'confidence_surface.json', 'entropy_surface.json']

combined = b''
for f in files:
    content = (base / f).read_text(encoding='utf-8').replace('\r\n', '\n')
    combined += content.encode('utf-8')

bundle_sha = hashlib.sha256(combined).hexdigest()
print(f'Bundle SHA256: {bundle_sha}')
assert bundle_sha == '26de75db866aafa813cb25ef63ee3c1f34e14eda0d07d7de567957d2d46a58bc', 'HASH MISMATCH'
print('VERIFIED')
"
```

### Step 6 — Start Backend and Frontend

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173`. Load the `m15_real_ui` case to inspect real artifact surfaces.

---

## 6. Demo Links

| Component | URL |
|-----------|-----|
| Frontend (Netlify) | https://majestic-dodol-25e71c.netlify.app |
| Backend API (Render) | https://clarity-1sra.onrender.com |

The live demo serves precomputed synthetic and real artifacts. No GPU execution in cloud. Demo is read-only.

To inspect real MedGemma artifacts in the demo, load case `case_m15_real`.

---

## Repository

**GitHub**: https://github.com/m-cahill/clarity

**License**: Apache-2.0

**Competition**: MedGemma Impact Challenge (Kaggle) — February 2026
