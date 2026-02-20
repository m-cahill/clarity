# M04 — Sweep Orchestrator

**Status:** In Progress  
**Baseline:** M03 (`v0.0.4-m03`)  
**Branch:** `m04-sweep-orchestrator`

---

## Objective

Implement a deterministic, multi-axis perturbation sweep engine that:

- Uses M02 perturbations (via spec injection, not direct application)
- Uses M03 R2LRunner for all R2L invocation
- Executes structured sweep grids (Cartesian product)
- Produces reproducible run directories
- Emits a canonical sweep manifest
- Does **not** compute metrics (M05)
- Does **not** estimate surfaces (M06)

M04 is the first milestone where CLARITY becomes *behaviorally interesting*.

---

## 🔒 Core Constraints (Non-Negotiable)

From M03:
- All R2L invocation must go through `R2LRunner`
- All artifact ingestion must go through `artifact_loader`
- No direct subprocess calls
- No r2l imports
- No randomness without explicit seed
- No datetime.now / uuid / OS entropy

From M02:
- All perturbations are deterministic
- Seeded noise required
- Image hashing stable

---

## 🔒 Locked Decisions

### Spec File Format
- Spec is **opaque** to CLARITY
- Must be valid JSON, writable
- CLARITY injects `"perturbations"` field
- CLARITY injects/overrides `"seed"` field
- No schema validation beyond JSON parsing

### Axis Value Serialization
Deterministic encoding for directory naming:
1. Convert value to string via `str(value)`
2. Replace `"."` → `"p"`, `"-"` → `"m"`
3. Remove spaces
4. Allow only `[a-zA-Z0-9_=]`

Examples:
| Value | Encoded |
|-------|---------|
| 0.8 | `0p8` |
| -0.25 | `m0p25` |
| "high" | `high` |

### Perturbation Application
- Orchestrator does NOT apply perturbations
- Only injects perturbation parameters into spec
- R2L is responsible for actual perturbation execution
- M04 is control-plane, not data-plane

### Existing sweep_manifest.py
- Do NOT modify M01 SweepManifest
- Create new models in `sweep_models.py`
- Write sweep_manifest.json manually (no Pydantic)
- Keep M04 models isolated

### Adapter Parameter
- `SweepConfig.adapter` maps directly to `R2LRunner.run(..., adapter=...)`
- No transformation required

### Fake R2L Fixture
- No extension required
- Current behavior sufficient for M04

### Additional Constraints
1. Axis name collision detection is mandatory (fail fast)
2. Sweep must fail if `output_root` already exists (no overwriting)
3. Spec injection must NOT mutate original file on disk (deep copy)
4. Seed injection: override if `"seed"` already exists in base spec
5. Run directory creation must be atomic: `mkdir(parents=True, exist_ok=False)`
6. No parallelization — sequential execution only

---

## Scope

### In Scope

**A. Sweep Models** (`backend/app/clarity/sweep_models.py`):

1. `SweepAxis` — frozen dataclass
   ```python
   @dataclass(frozen=True)
   class SweepAxis:
       name: str
       values: tuple[Any, ...]
   ```

2. `SweepConfig` — frozen dataclass
   ```python
   @dataclass(frozen=True)
   class SweepConfig:
       base_spec_path: Path
       axes: tuple[SweepAxis, ...]
       seeds: tuple[int, ...]
       adapter: str
   ```
   - Validation: no duplicate axis names, no empty axes, no empty seeds
   - Fail fast at construction

3. `SweepRunRecord` — frozen dataclass
   ```python
   @dataclass(frozen=True)
   class SweepRunRecord:
       axis_values: dict[str, Any]
       seed: int
       output_dir: Path
       manifest_hash: str
   ```

**B. Sweep Orchestrator** (`backend/app/clarity/sweep_orchestrator.py`):

1. `SweepResult` — frozen dataclass
   ```python
   @dataclass(frozen=True)
   class SweepResult:
       runs: tuple[SweepRunRecord, ...]
       sweep_manifest_path: Path
   ```

2. `SweepOrchestrator` class
   ```python
   class SweepOrchestrator:
       def __init__(self, runner: R2LRunner, output_root: Path): ...
       def execute(self, config: SweepConfig) -> SweepResult: ...
   ```

**C. Tests**:
- `backend/tests/test_sweep_models.py`
- `backend/tests/test_sweep_orchestrator.py`
- AST guardrail tests in `test_m03_guardrails.py` or new file

### Out of Scope
- Metrics computation (M05)
- Robustness surface estimation (M06)
- Parallelization
- Cache/resume
- Persistence to DB
- GPU logic
- Frontend integration

---

## Execution Semantics

### Cartesian Expansion
- Compute full Cartesian product of all axis values × all seeds
- Deterministic ordering:
  1. Axis names sorted alphabetically
  2. Axis values in declared order
  3. Seeds in declared order

### Output Directory Structure
```
output_root/
    sweep_manifest.json
    runs/
        brightness=0p8_contrast=1p0_seed=42/
            manifest.json
            trace_pack.jsonl
        brightness=0p8_contrast=1p0_seed=43/
            ...
```

### Per-Run Execution
1. Create deterministic subdirectory (atomic)
2. Build modified spec file (deep copy, inject perturbations + seed)
3. Write modified spec to run directory
4. Invoke R2LRunner
5. Load artifacts via artifact_loader
6. Hash manifest
7. Record SweepRunRecord

### Sweep Manifest
```json
{
  "axes": {
    "brightness": [0.8, 1.0, 1.2],
    "contrast": [0.8, 1.0, 1.2]
  },
  "seeds": [42, 43],
  "runs": [
    {
      "axis_values": {...},
      "seed": 42,
      "manifest_hash": "..."
    }
  ]
}
```
Written with `sort_keys=True`, `indent=2`.

---

## Test Categories

### A. Model Tests (`test_sweep_models.py`)
- SweepAxis immutability
- SweepConfig validation (duplicates, empty axes, empty seeds)
- SweepRunRecord immutability

### B. Orchestrator Tests (`test_sweep_orchestrator.py`)
- Cartesian expansion (correct count, ordering, determinism)
- Directory naming (encoding, no collisions, OS-safe)
- Spec injection (original unmutated, perturbations injected, seed injected)
- Integration with fake_r2l
- Sweep manifest content and determinism
- Error handling (output_root exists, invalid config)

### C. Guardrail Tests
- No direct subprocess calls outside R2LRunner
- No r2l imports
- No datetime.now
- No random

---

## Coverage Targets

| Component | Threshold |
|-----------|-----------|
| sweep_orchestrator.py | ≥90% |
| sweep_models.py | ≥95% |
| Backend overall | ≥90% (target ≥94%) |

---

## Exit Criteria

M04 is complete when:
- [ ] Cartesian product executed correctly
- [ ] Deterministic output structure verified
- [ ] sweep_manifest.json deterministic (byte-identical across runs)
- [ ] All runs invoked via R2LRunner
- [ ] No boundary violations (AST guardrails pass)
- [ ] CI green on first run (or subsequent with fixes)
- [ ] Coverage thresholds met
- [ ] No HIGH issues introduced

---

## Implementation Order

1. Create branch `m04-sweep-orchestrator`
2. Implement `sweep_models.py`
3. Implement `sweep_orchestrator.py`
4. Update `__init__.py` exports
5. Create `test_sweep_models.py`
6. Create `test_sweep_orchestrator.py`
7. Add AST guardrails for new modules
8. Verify coverage
9. Create PR
10. Monitor CI

---

## Notes

This file was populated with locked answers from stakeholder review.
Clarifying questions asked and answered: Q1-Q7.

