# M03 — R2L Invocation Harness

**Status:** In Progress  
**Baseline:** M02 (`v0.0.3-m02`, Score 4.5)  
**Branch:** `m03-r2l-harness`

---

## Objective

Implement a **black-box R2L runner invocation harness** and deterministic artifact ingestion layer.

M03 must:

* Invoke R2L **via CLI only**
* Never import `r2l.*` (hardened from M01)
* Never depend on R2L implementation details
* Only consume declared artifact outputs
* Preserve M01 boundary contracts
* Preserve M02 determinism guarantees

This milestone enables:

* M04 Sweep Orchestrator
* M05 Metrics Core
* M06 Robustness Surfaces

Without M03, CLARITY cannot execute R2L experiments.

---

## Architectural Constraints (Non-Negotiable)

### 1. Pure Consumer Model

CLARITY must:

* Call R2L as an **external process**
* Consume:
  * `manifest.json`
  * `trace_pack.jsonl`
  * any declared output artifacts

CLARITY must not:

* Import R2L modules (`import r2l` forbidden)
* Share memory with R2L
* Depend on R2L object models
* Mutate R2L artifacts

### 2. Deterministic Execution Envelope

The harness must:

* Accept explicit:
  * config path
  * output directory
  * seed (optional)
  * adapter name (optional)
* Execute via `subprocess.run()`
* Capture:
  * exit code
  * stdout
  * stderr
* Enforce timeout
* Fail loudly on non-zero exit

No background threads.
No async.
No implicit environment mutation.

### 3. Artifact Boundary

The harness must treat R2L output directory as:

```
run_output/
  manifest.json
  trace_pack.jsonl
  adapter_metadata.json (optional)
```

Artifacts must be:

* Parsed
* Schema validated (minimal required fields)
* Hashed for integrity (SHA256 of file bytes)

---

## Locked Answers (Authoritative)

### Q1a — R2L CLI Signature

Use generic passthrough CLI contract with minimal required interface:

* Required inputs: `config_path: Path`, `output_dir: Path`
* Optional: `seed: int | None`, `adapter: str | None`

Arg order:
1. `r2l_executable` (string, split via `shlex.split()`)
2. `--config <config_path>`
3. `--output <output_dir>`
4. `--adapter <adapter>` (only if provided)
5. `--seed <seed>` (only if provided)

### Q1b — r2l_executable Format

Supports both:
* Binary: `/usr/local/bin/r2l`
* Python invocation: `python -m r2l.cli` or `python path/to/r2l_cli.py`

Use `shlex.split(r2l_executable)` to form argv prefix.

### Q2 — Relationship to r2l_interface.py

**Replace the stub.** Remove `r2l_interface.py` if not used elsewhere.
If removal causes churn, use wrapper + deprecation comment.

`backend/app/clarity/r2l_runner.py` becomes canonical implementation.

### Q3 — Manifest Schema Fields

Validate **minimal required set**, allow optional fields:

Required keys:
* `run_id`
* `timestamp`
* `seed`
* `artifacts`

Permit any other keys without failing.

### Q4 — Trace Pack Schema

Accept **either** `step` **or** `step_id`.

Each JSONL record must:
* Be valid JSON object
* Contain one of: `step` (int) or `step_id` (str/int)

### Q5 — AST Guardrail Scope

**No R2L imports at all.** Forbid:
* `import r2l`
* `from r2l import ...`
* any `r2l.*` imports

M03 hardens the M01 boundary.

### Q6 — Coverage Targets

* Overall backend: ≥85% (try for ≥90%)
* `r2l_runner.py`: ≥90%
* `artifact_loader.py`: ≥90%

---

## Additional Locked Constraints

1. Runner must not depend on current working directory — always pass absolute paths
2. Runner must emit structured result even on failure (stderr/stdout captured)
3. Artifact hashing is file-content hashing (SHA256 of bytes), not parsed JSON
4. Fake R2L fixture must be deterministic and Python-only (no bash)

---

## Deliverables

### A. R2L Runner Module

Create: `backend/app/clarity/r2l_runner.py`

```python
class R2LInvocationError(Exception):
    pass

class R2LTimeoutError(R2LInvocationError):
    pass

@dataclass(frozen=True)
class R2LRunResult:
    manifest_path: Path
    trace_pack_path: Path
    stdout: str
    stderr: str
    exit_code: int

class R2LRunner:
    def __init__(self, r2l_executable: str, timeout_seconds: int = 300):
        ...

    def run(
        self,
        config_path: Path,
        output_dir: Path,
        *,
        adapter: str | None = None,
        seed: int | None = None,
    ) -> R2LRunResult:
        ...
```

### B. Artifact Loader Module

Create: `backend/app/clarity/artifact_loader.py`

Functions:
* `load_manifest(path: Path) -> dict` — load and validate manifest.json
* `load_trace_pack(path: Path) -> list[dict]` — load and validate JSONL
* `hash_artifact(path: Path) -> str` — SHA256 of file bytes

### C. Fake R2L CLI Fixture

Create: `backend/tests/fixtures/fake_r2l.py`

Deterministic Python script that:
* Writes deterministic `manifest.json`
* Writes deterministic `trace_pack.jsonl`
* Exits 0

### D. Test Suite

Create:
* `backend/tests/test_r2l_runner.py`
* `backend/tests/test_artifact_loader.py`

Runner tests:
| Test | Purpose |
|------|---------|
| test_successful_invocation | Exit 0, artifacts exist |
| test_nonzero_exit_raises | Simulate failure |
| test_timeout_raises | Sleep > timeout |
| test_stdout_stderr_captured | Validate capture |
| test_output_dir_required | Missing dir fails |

Loader tests:
| Test | Purpose |
|------|---------|
| test_load_manifest_valid | Parses correctly |
| test_load_manifest_invalid_json | Raises |
| test_load_manifest_missing_required | Raises |
| test_trace_pack_valid | Parses list |
| test_trace_pack_invalid_line | Raises |
| test_trace_pack_missing_step | Raises |
| test_hash_stability | Hash identical across calls |

Guardrail tests:
| Test | Enforcement |
|------|-------------|
| test_no_r2l_imports | AST scan for any r2l import |
| test_no_random_imports | AST scan |
| test_no_datetime_now_usage | AST scan |
| test_no_uuid4_usage | AST scan |

---

## Scope

### In Scope

* `backend/app/clarity/r2l_runner.py` — Runner implementation
* `backend/app/clarity/artifact_loader.py` — Artifact loading/validation
* `backend/tests/fixtures/fake_r2l.py` — Test fixture
* `backend/tests/test_r2l_runner.py` — Runner tests
* `backend/tests/test_artifact_loader.py` — Loader tests
* Remove/deprecate `backend/app/clarity/r2l_interface.py`
* Update `backend/app/clarity/__init__.py` exports
* Governance docs

### Out of Scope

* Sweep logic (M04)
* Metrics computation (M05)
* Perturbation execution
* Parallelization
* GPU logic
* Persistence
* Frontend integration
* Caching
* Async execution

---

## Exit Criteria

M03 is complete when:

1. ✅ R2LRunner executes fake CLI successfully
2. ✅ Artifacts load and hash deterministically
3. ✅ Timeout enforced (raises R2LTimeoutError)
4. ✅ Non-zero exit raises R2LInvocationError
5. ✅ No R2L imports anywhere in CLARITY
6. ✅ CI green on first run
7. ✅ No HIGH issues introduced
8. ✅ Coverage thresholds met (≥90% on new modules, ≥85% overall)

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| R2L interface drift | CLI-only boundary |
| Artifact schema changes | Minimal validation only |
| Hidden randomness | AST guardrails |
| Subprocess deadlock | Timeout enforcement |

---

## Estimated Scope

* ~600–900 LOC
* ~40–60 tests
* Medium complexity
* High architectural importance

---

## Notes

M02 gave CLARITY **image determinism**.
M03 gives CLARITY **execution determinism**.

> CLARITY must never "know" how R2L works — only what it outputs.

If that contract holds, M04–M08 become safe to build.

---

*End of M03 Plan*
