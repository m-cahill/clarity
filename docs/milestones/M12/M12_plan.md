# 📌 M12_plan — Operational Hardening

**Project:** CLARITY
**Milestone:** M12 — Operational Hardening
**Branch:** `m12-operational-hardening`
**Mode:** DELTA AUDIT expected
**Baseline:** `v0.0.12-m11`

---

# 1️⃣ Objective

M12 strengthens CLARITY's **runtime reliability, governance posture, and operational correctness** without expanding scope.

Per Source of Truth :

> "M12 — Caching, resumability, concurrency controls."

Additionally, M11 introduced:

* COV-002 (coverage regression) 
* New reportlab dependency
* Larger artifact generation footprint

M12 must:

1. Close COV-002
2. Add deterministic caching
3. Add resumability guards
4. Add concurrency protection
5. Introduce basic security scanning
6. Add dependency lock discipline

No new product features.

---

# 2️⃣ Strict Scope

## ✅ In Scope

### A. Coverage Restoration (COV-002 Exit)

* Restore frontend branch coverage ≥85%
* Remove threshold exception in `vite.config.ts`
* Prefer E2E coverage over jsdom hacks
* No lowering gates

---

### B. Deterministic Artifact Caching (Server-Side)

Add optional caching layer for:

* Report generation (`/report/generate`)
* Demo artifact reads

Requirements:

* Cache key = SHA256(case manifest + metrics + overlay bundle)
* Deterministic file naming
* Cache directory: `clarity/cache/`
* No cross-request mutation
* Cache safe under concurrency

Must not cache:

* Anything R2L-owned
* Mutable artifacts

---

### C. Idempotent Resumability Guards

Prevent:

* Duplicate report writes
* Duplicate sweep runs (future-safe)
* Concurrent regeneration race conditions

Implement:

* Atomic file writes (temp file → rename)
* Lock file mechanism OR file-level mutex
* Explicit 409 if concurrent identical request detected

---

### D. Concurrency Controls (Backend)

For report generation:

* Thread-safe rendering
* No shared global state
* Explicit max worker setting if needed

Add tests simulating:

* Parallel requests
* Identical case_id simultaneous POST

---

### E. Dependency Discipline (DEP-001 Exit)

Per Deferred Registry :

> DEP-001 — No dependency lockfile — Deferred to M12

Implement:

* `requirements.lock` (pip-compile or equivalent)
* Deterministic install in CI
* Hash-verified lock

No version floating allowed.

---

### F. Security Scanning (SCAN-001 Exit)

Per registry :

> SCAN-001 — No security scanning — Deferred to M12

Implement:

* `pip-audit` in CI
* `npm audit` in CI
* Fail on HIGH/CRITICAL
* Report in PR

Pinned versions only.

---

### G. CORS Tightening (SEC-001 Progress)

Not full production lock, but:

* Restrict CORS in non-demo mode
* Explicit allowed origins
* Document demo exception

---

# 3️⃣ Out of Scope

* Persistent database
* Multi-user job queue
* Cloud object storage
* Auth system
* Rate limiting
* Performance benchmarking
* UI redesign

M12 is not architecture expansion.

---

# 4️⃣ Implementation Breakdown

---

## Phase A — Coverage Restoration (COV-002)

1. Remove branch threshold reduction
2. Add:

   * Playwright test covering real file download path
   * Mock URL.createObjectURL coverage branch
3. Achieve:

   * ≥85% branch coverage
4. Remove exception comment

Exit Criteria:

* CI fails if branch <85%
* COV-002 removed from Deferred Registry

---

## Phase B — Cache Layer

Create:

```
backend/app/clarity/cache/
    cache_manager.py
    cache_key.py
```

### cache_key.py

```
def compute_case_hash(case_dir: Path) -> str
```

* Sort JSON keys
* Canonical serialization
* SHA256 output

---

### cache_manager.py

Responsibilities:

* get_or_create(cache_key, generator_func)
* Atomic write
* Lock file enforcement
* Deterministic path structure

---

### Integrate into:

`report_router.py`

If cache hit:
→ return cached bytes

Else:
→ generate → write → return

Add tests:

* First request generates
* Second identical request reads cache
* Hash matches

---

## Phase C — Concurrency Guard

Simulate parallel POST:

* Use pytest + threading
* Ensure:

  * Only one generation
  * No partial file
  * No corruption

---

## Phase D — Lockfile

Backend:

```
pip-compile requirements.in → requirements.lock
```

CI must install from lockfile.

Frontend:

Ensure package-lock.json committed.

---

## Phase E — Security Scan Workflow

Update `.github/workflows/ci.yml`:

Add jobs:

* pip-audit
* npm audit --production

Fail if severity ≥ HIGH.

Pin audit tool version.

---

# 5️⃣ Test Requirements

M12 must add:

* ≥ 40 backend tests
* ≥ 5 frontend tests
* Concurrency stress tests
* Cache hit/miss tests
* Lockfile verification test
* CI security job test (dry run allowed)

Coverage:

* Backend ≥95%
* Frontend branch ≥85% restored

---

# 6️⃣ CI Requirements

Must:

* Remain green
* Add security job
* Add lockfile enforcement
* No action unpinned
* No new threshold reductions

---

# 7️⃣ Governance Changes Required

Update:

* Deferred Registry (remove COV-002, DEP-001, SCAN-001 if closed)
* Milestone table in clarity.md 
* Add M12 entry on close

---

# 8️⃣ Exit Criteria

M12 closes only if:

| Criterion                 | Required |
| ------------------------- | -------- |
| COV-002 resolved          | ✅        |
| DEP-001 resolved          | ✅        |
| SCAN-001 resolved         | ✅        |
| Cache layer deterministic | ✅        |
| Concurrency safe          | ✅        |
| CI green                  | ✅        |
| No new deferrals          | ✅        |
| clarity.md updated        | ✅        |
| Tag `v0.0.13-m12` created | ✅        |

---

# 9️⃣ Risk Assessment

| Risk                   | Mitigation                   |
| ---------------------- | ---------------------------- |
| Cache nondeterministic | Canonical JSON + sorted keys |
| File corruption        | Atomic rename                |
| Deadlocks              | Timeout on lock              |
| Audit job flakiness    | Pin versions                 |
| CI slowdown            | Parallelize jobs             |

---

# 🔟 Score Target

If executed cleanly:

M12 should move overall from **4.98 → 5.0**
By:

* Closing 3 deferred items
* Restoring full coverage discipline
* Adding security scanning
* Adding lock determinism

---

# 11️⃣ Hand-Off Instructions to Cursor

1. Create branch `m12-operational-hardening`
2. Create `docs/milestones/M12/M12_plan.md`
3. Copy this plan verbatim
4. Ask clarifying questions
5. Do NOT implement until answers locked

---
