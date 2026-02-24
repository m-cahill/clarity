# CLARITY — Executive Summary

### MedGemma Impact Challenge | February 2026

---

## Core Insight

Clinical AI evaluation is dominated by accuracy metrics — single-number summaries that collapse a model's behavior across all inputs into one scalar. This is inadequate for deployment settings where imaging conditions vary predictably: motion blur, device exposure shifts, monitoring lead occlusion, scanner calibration drift. CLARITY addresses this gap by treating robustness as an empirical, measurable property of model reasoning, not an assumption. Built as a deterministic evaluation instrument on top of R2L micro-labs, CLARITY sweeps MedGemma 4B-IT across parameterized perturbation axes and computes Evidence Sensitivity Index (ESI), Confidence Stability Index (CSI), Entropy Distribution Metric (EDM), and justification drift — producing a robustness surface that reveals whether the model's reasoning degrades gracefully or catastrophically under clinically grounded image distortions.

## Determinism

Every inference run in CLARITY is seed-controlled, hash-verified, and reproducible. Torch, NumPy, Python, and CUDA random states are all fixed before each inference pass. Two seeds (42, 123) are run per perturbation level; identical SHA256 hashes across seeds confirm that stochastic variation does not introduce output drift. The M15 validation sweep — 12 runs across brightness and contrast axes — produced an identical logit summary hash (`c52ead26746d271526b05831f4b34de275fb2c620d69c85bb31a0e4cb5652fa1`) across all runs, and a sealed bundle SHA256 (`fa6fdb5dbe017076fd6cdf01f28f9a7773edef551e977b18bff918e1622d3236`) that serves as a tamper-evident audit artifact. Reproducibility is not claimed — it is proven and hash-verified.

## Validation

M15 validated the full end-to-end system: real MedGemma inference, rich-mode evidence extraction (token logprobs, output entropy, confidence scores), and UI rendering of real artifact surfaces — all with zero console errors, zero NaN values, and CI green across Python 3.10/3.11/3.12. The backend test suite covers 911 tests; the frontend covers 137 tests including branch coverage at 87.39%. The counterfactual probe is implemented and operational: region masking, re-inference, and diagnosis delta computation are all wired end-to-end. The system runs fully offline on an RTX 5090 at 9.71 GB VRAM peak — within the 12 GB budget required for hospital IT environments where external APIs may be restricted.

## Practical Impact

CLARITY establishes that robustness evaluation for clinical AI can be deterministic, reproducible, GPU-accelerated, and instrument-grade. The methodology is model-agnostic — any multimodal model with a thin adapter boundary can be evaluated through the same sweep framework. The output is not a leaderboard score but a robustness landscape: confidence surfaces, entropy surfaces, ESI curves, and counterfactual deltas that allow clinical AI developers to identify failure modes before deployment. A judge who reads this submission will find a complete, runnable, hash-verified scientific instrument — not a demo — with a live deployment, a reproducible artifact bundle, and a clear empirical answer to the question that clinical AI evaluation has been avoiding.

---

*CLARITY — Clinical Localization and Reasoning Integrity Testing*
*Apache-2.0 | https://github.com/m-cahill/clarity*
*Demo: https://majestic-dodol-25e71c.netlify.app*
