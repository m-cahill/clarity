# 📦 M02_plan.md

## Milestone M02 — Perturbation Core

**Project:** CLARITY
**Milestone:** M02 — Perturbation Core
**Objective:** Implement deterministic image perturbation recipes.
**Mode:** DELTA AUDIT expected
**Precondition:** M01 merged, branch protection configured (GOV-001) 

---

# 1️⃣ Why M02 Exists

CLARITY measures robustness under **structured perturbation sweeps** .

M01 froze the boundary and determinism contract.
M02 introduces the **first domain capability**:

> Deterministic image perturbation primitives.

Without M02:

* Sweep orchestrator (M04) cannot execute.
* Metrics (M05) have no perturbation data.
* Robustness surfaces (M06) cannot be estimated.

This milestone establishes:

* Reproducible perturbation recipes
* Deterministic parameterization
* Stable hashable outputs
* Zero randomness leakage

---

# 2️⃣ Scope

## ✅ In Scope

### A. Perturbation Module

Create:

```
backend/app/clarity/perturbations/
    __init__.py
    base.py
    brightness.py
    contrast.py
    gaussian_noise.py
    blur.py
    resize.py
```

All perturbations must:

* Accept a PIL Image
* Return a PIL Image
* Be pure functions (no hidden randomness)
* Be fully deterministic given explicit parameters
* Avoid global state

---

### B. Base Perturbation Contract

`base.py`

Define abstract base:

```python
class Perturbation(ABC):
    name: str
    version: str

    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        ...

    @abstractmethod
    def to_manifest_dict(self) -> dict:
        ...
```

Requirements:

* Immutable
* Parameters frozen
* Deterministic repr
* No mutation of input image

---

### C. Deterministic Randomness Model

For perturbations requiring noise:

* Require explicit `seed: int`
* Use `np.random.default_rng(seed)`
* No `np.random.seed()` global calls
* No `random` module usage

Add guardrail test:

* Same seed → byte-identical output
* Different seed → different output

---

### D. Deterministic Output Hashing

Add utility:

```
backend/app/clarity/image_utils.py
```

Must provide:

```python
def image_sha256(image: Image.Image) -> str
```

* Convert to canonical format (e.g., PNG)
* Normalize mode
* Strip metadata
* Stable encoding

Used for determinism tests.

---

### E. Minimal Perturbation Set (Locked)

| Perturbation   | Deterministic? | Notes                       |
| -------------- | -------------- | --------------------------- |
| Brightness     | Yes            | Linear scale                |
| Contrast       | Yes            | Linear scale                |
| Gaussian Noise | Yes            | Seed required               |
| Gaussian Blur  | Yes            | Radius param                |
| Resize         | Yes            | Explicit interpolation mode |

No geometric rotation yet.
No cropping.
No compositional perturbations.

Keep blast radius minimal.

---

### F. Perturbation Registry

Create:

```
backend/app/clarity/perturbation_registry.py
```

Must:

* Register perturbation classes
* Prevent duplicate names
* Expose:

```python
def get_perturbation(name: str, **params) -> Perturbation
```

---

### G. Guardrail Test Suite

Create:

```
backend/tests/test_perturbations.py
```

Must include:

1. Determinism test (brightness)
2. Determinism test (noise, same seed)
3. Seed variation test (noise, different seed)
4. No input mutation test
5. Hash stability test
6. Manifest serialization test
7. Registry lookup test
8. Parameter immutability test

Target: 20–30 tests.

Coverage ≥90% for perturbation module.

---

# 3️⃣ Out of Scope

* Sweep execution logic (M04)
* R2L integration (M03)
* Metrics computation (M05)
* Parallelization
* GPU usage
* Persistence
* UI wiring
* Caching
* Async execution

---

# 4️⃣ Determinism Requirements (Non-Negotiable)

### ❌ Forbidden

* datetime.now()
* uuid4()
* global random seeds
* OS entropy
* non-seeded randomness
* metadata-preserving image saves

### ✅ Required

* Explicit seed parameter
* Stable numpy RNG
* Stable image encoding for hashing
* Immutable parameter storage

Add AST guardrail test:

* No `random.` imports inside perturbation module.

---

# 5️⃣ File Changes

## New Files

```
backend/app/clarity/perturbations/*
backend/app/clarity/perturbation_registry.py
backend/app/clarity/image_utils.py
backend/tests/test_perturbations.py
docs/milestones/M02/M02_plan.md
docs/milestones/M02/M02_toolcalls.md
```

## Modified Files

```
docs/clarity.md (mark M02 in-progress)
```

No CI workflow modifications allowed.

---

# 6️⃣ Acceptance Criteria

M02 closes only if:

* [ ] All perturbations deterministic
* [ ] Noise requires seed and fails without it
* [ ] image_sha256 stable across runs
* [ ] No input image mutation
* [ ] Registry prevents duplicate registration
* [ ] ≥90% coverage on perturbation module
* [ ] CI green on first run
* [ ] No new deferred HIGH issues

---

# 7️⃣ Risk Analysis

| Risk                       | Mitigation                  |
| -------------------------- | --------------------------- |
| Floating point instability | Use consistent dtype        |
| PIL metadata drift         | Canonicalize before hashing |
| Accidental nondeterminism  | Seed required + tests       |
| Silent mutation            | Explicit copy before apply  |

---

# 8️⃣ Definition of Done

M02 is complete only if:

* Perturbation primitives exist
* Determinism provable via hash tests
* No global randomness
* Registry works
* CI green
* Audit verdict 🟢 or 🟡 (no red)

---

# 9️⃣ Deliverables After CI Green

* `M02_run1.md`
* `M02_audit.md`
* `M02_summary.md`
* Update `clarity.md`
* Tag `v0.0.3-m02`

---

# 🔟 Milestone Discipline

This is the first domain milestone.

It must:

* Remain small
* Introduce no orchestration
* Introduce no external coupling
* Preserve M01 guarantees

---

# Cursor Execution Instructions

1. Create `docs/milestones/M02/`
2. Copy this plan to `M02_plan.md`
3. Generate clarifying questions
4. Implement only after clarification lock
5. Push branch `m02-perturbation-core`
6. Monitor CI
7. Provide CI run summary

---

# ✅ Locked Answers — M02 Clarifications

## 1) PIL Image Mode Handling

**Locked:** Accept `RGB`, `RGBA`, `L`; internally convert as needed; **return `RGB`**.

* Rationale: deterministic canonicalization beats "preserve mode" complexity.
* Rule: `L` → `RGB` via repeat channels; `RGBA` → composite onto **solid black** then `RGB` (deterministic).

---

## 2) NumPy dtype for operations

**Locked:** `float32`, normalized to `[0.0, 1.0]`, then convert back to `uint8`.

* Clip to `[0.0, 1.0]` before conversion.

---

## 3) Brightness / Contrast semantics

**Locked:** Follow **PIL ImageEnhance conventions**.

* `factor=1.0` = no change
* `factor=0.0` = min effect
* `factor>1.0` = increased effect
  Implementation may use `ImageEnhance` directly *if deterministic in practice* (guarded by hashing tests). If any flake appears, re-implement via numpy math.

---

## 4) Gaussian Noise parameters

**Locked:** Normalized `std_dev` in `[0.0, 1.0]`, mean fixed at `0.0`.

* Also require `seed: int` (mandatory).
* Validation: `0.0 <= std_dev <= 1.0`.

---

## 5) Resize interpolation default

**Locked:** **BILINEAR** default, with explicit override allowed.

* Allowed: `NEAREST`, `BILINEAR`, `BICUBIC`, `LANCZOS`
* Encode interpolation in manifest as a string enum.

---

## 6) Hashing canonical format

**Locked:** Hash **raw canonical pixel bytes**, not PNG.
Implementation contract for `image_sha256()`:

* Convert to canonical `RGB`
* Use `np.asarray(img, dtype=np.uint8)` (after canonicalization)
* Hash `arr.tobytes()` plus **width/height** (to avoid ambiguous byte streams across shapes)
* No metadata, no encoder, no compression variability.

---

## 7) Input mutation prevention

**Locked:** Guardrail test only, **NOT** "always defensive copy."

* Rationale: copying every time is easy but hides bugs and costs perf. We prove non-mutation in tests and keep implementations clean.
* Test must verify input unchanged after `apply()`.

(May still copy internally for transformations that require it, but not mandated as blanket policy.)

---

## 8) Parameter validation timing

**Locked:** Validate at construction time.

* Use Pydantic model(s) or `@dataclass(frozen=True)` + explicit checks in `__post_init__`.

---

## 9) Perturbation version scheme

**Locked:** Semver.

* Start all perturbations at `1.0.0`.
* Bump patch for internal bugfixes that don't change semantics.
* Bump minor for additive params.
* Bump major for breaking changes.

---

## 10) Test fixture images

**Locked:** Synthetic-only.
Required synthetic generators:

* solid color
* gradient
* checkerboard (high frequency)
  These catch subtle issues across blur/noise/resize.

---

# Additional Locked Constraints (M02)

## A) Canonical "image contract"

All perturbations operate on canonical RGB internally and output RGB.

* This is now part of the perturbation-core contract.

## B) No PIL internal nondeterminism leakage

If any operation produces non-stable hashes across runs/platforms:

* Replace with numpy implementation within M02 (don't defer).

## C) Registry API

`get_perturbation(name: str, **params)` must:

* raise `KeyError` for unknown names
* raise `ValueError` for invalid params
* return an **immutable** perturbation instance

## D) CI / gates

No CI workflow changes in M02.

