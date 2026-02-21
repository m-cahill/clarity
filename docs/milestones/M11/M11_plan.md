# 📌 M11_plan — Deterministic Report Export

**Project:** CLARITY
**Milestone:** M11 — Report Export
**Branch:** `m11-report-export`
**Mode:** Standard Feature Milestone (DELTA AUDIT expected at closure)
**Baseline:** `v0.0.11-m10` (post M10) + M10.5 demo layer

---

## 1️⃣ Objective

Implement **deterministic, audit-grade PDF report generation** for CLARITY.

M11 exists because:

* CLARITY now computes:

  * ESI
  * Robustness surfaces
  * Drift metrics
  * Evidence overlays
* M10 introduced visual overlays
* M10.5 introduced demo deployment

However, there is currently **no deterministic, sealed report artifact** suitable for:

* Kaggle submission packaging 
* Clinical audit review
* Offline hospital IT environments
* Reproducibility evidence bundles

> Without M11, CLARITY remains an interactive instrument — not a sealed evaluation artifact.

---

## 2️⃣ Scope Definition

### ✅ In Scope

1. Deterministic PDF report generator
2. Report data model
3. Stable rendering engine
4. Artifact serialization discipline
5. Version + reproducibility metadata inclusion
6. Backend API endpoint for report export
7. Determinism verification tests
8. Minimal frontend trigger button (UI integration only)

---

### ❌ Out of Scope

* Advanced templating engines
* Dynamic CSS theming
* Interactive PDF elements
* Rich R2L mode dependence
* Cloud storage integration
* Batch report pipelines (M12+)
* Performance optimization beyond correctness

---

## 3️⃣ Architectural Requirements (Non-Negotiable)

### A. R2L Boundary Preservation

Per Architecture Contract :

* No modification to R2L schemas
* No artifact overwrites
* Report must consume only CLARITY-level artifacts
* Determinism must remain intact

---

### B. Determinism Constraints

The following must hold true:

| Requirement               | Enforcement                     |
| ------------------------- | ------------------------------- |
| Stable float formatting   | 8 decimal places                |
| Stable section ordering   | Explicit sorted ordering        |
| Stable timestamp behavior | Use run manifest timestamp only |
| No current time usage     | Forbidden in report             |
| Stable font usage         | Explicitly declared             |
| No random UUIDs           | Forbidden                       |
| Re-run PDF hash identical | Required test                   |

---

## 4️⃣ Report Structure (Canonical Sections)

The report must contain:

### 1. Cover Page

* Project: CLARITY
* Run ID
* Sweep manifest hash
* R2L SHA
* Adapter ID
* Rich mode: true/false
* Date (from manifest only)

---

### 2. Core Metrics Summary

* Diagnosis Stability
* Evidence Sensitivity Index (ESI)
* Drift Metrics
* Monte Carlo entropy stats (if present)

---

### 3. Robustness Surfaces

* Surface heatmap snapshot
* Axis labels
* Stability gradient summary

---

### 4. Evidence Overlay Section

* Heatmap image
* Extracted region bounding boxes
* Region area percentages

---

### 5. Counterfactual Results

* Masked region deltas
* Confidence changes
* Drift notes

---

### 6. Reproducibility Block (Critical)

Must include:

```
Sweep Seeds: [...]
R2L SHA: ...
Adapter Model: ...
Rich Mode: true/false
Perturbation Grid: [...]
Serialization Version: M11_v1
```

---

## 5️⃣ Implementation Plan

### Phase A — Backend Core

Create:

```
backend/app/clarity/report/
├── report_model.py
├── report_renderer.py
├── report_router.py
└── __init__.py
```

---

### A1. `report_model.py`

Frozen dataclasses:

* `ReportMetadata`
* `ReportMetrics`
* `ReportSection`
* `ClarityReport`

All fields:

* deterministic ordering
* no optional randomness
* fully serializable

---

### A2. `report_renderer.py`

Use:

* `reportlab` (preferred)
  OR
* Deterministic HTML → PDF via wkhtmltopdf (only if fully stable)

Constraints:

* Explicit font
* Fixed layout
* No layout randomness
* Stable page breaks
* No system-dependent rendering behavior

---

### A3. `report_router.py`

Endpoint:

```
POST /report/generate
```

Input:

* run_id or sweep_manifest reference

Output:

* application/pdf
* deterministic binary

---

## 6️⃣ Determinism Verification Tests

Create:

```
backend/tests/test_report_determinism.py
```

Required tests:

1. Double generation → identical SHA256
2. Changing metric → SHA changes
3. Stable float formatting
4. Stable section order
5. No datetime.now() usage (AST guardrail)
6. No random import (AST guardrail)
7. No UUID usage
8. Report includes reproducibility block

---

## 7️⃣ Frontend Integration (Minimal)

In CounterfactualConsole:

* Add "Export Report" button
* Calls `/report/generate`
* Triggers file download
* No client-side PDF generation
* No dynamic rendering in browser

---

## 8️⃣ CI Requirements

M11 must:

* Add ≥ 20 new backend tests
* Maintain ≥95% coverage for report module
* No workflow modifications
* No new dependency beyond report library
* Pass all matrix Python versions (3.10–3.12)

---

## 9️⃣ Guardrails to Add

### AST Guardrails

Enforce in report module:

* No random
* No uuid
* No datetime.now
* No subprocess
* No R2L import

---

### Serialization Guardrail

Add test ensuring:

* JSON intermediate representation stable
* Sorting enforced

---

## 🔟 Exit Criteria

M11 closes only if:

| Criterion                 | Required |
| ------------------------- | -------- |
| PDF generation works      | ✅        |
| SHA stable across runs    | ✅        |
| CI green                  | ✅        |
| No new deferrals          | ✅        |
| clarity.md updated        | ✅        |
| Tag `v0.0.12-m11` created | ✅        |

---

## 11️⃣ Deliverables

* `M11_plan.md`
* `M11_toolcalls.md`
* `M11_run1.md`
* `M11_audit.md`
* `M11_summary.md`
* clarity.md updated
* Version tag

---

## 12️⃣ Risk Assessment

| Risk                              | Mitigation             |
| --------------------------------- | ---------------------- |
| PDF rendering nondeterministic    | Fixed layout + font    |
| Hidden timestamps in metadata     | Strip metadata         |
| Environment-based rendering drift | Avoid HTML engines     |
| Floating point drift              | Round before rendering |

---

## 13️⃣ Governance Posture

This milestone:

* Strengthens audit posture
* Moves CLARITY toward submission readiness 
* Preserves boundary discipline 
* Completes visualization → sealed artifact pipeline

---

## 14️⃣ Locked Answers (User Decisions)

### 1) Report Input Source
**Pick: (B) baseline_id used by the existing CounterfactualConsole / Orchestrator flow.**

**Contract:** `POST /report/generate` accepts JSON:
```json
{ "case_id": "case_001" }
```

Where `case_id` maps to the same artifact shape as demo cases (`/demo/cases/{id}/...`).

* Demo mode: pull from `demo_artifacts/<case_id>/...`
* Non-demo mode: return 404/NotImplemented (M12+)

---

### 2) Data Availability
**Pick: (A) Consume synthetic/demo data from `demo_artifacts/` (primary path).**

M11 supports deterministic report generation for demo cases only.

---

### 3) Robustness Surface Snapshot
**Pick: (A) Render an image and embed it.**

Deterministic rendering with:
* fixed dimensions
* fixed colormap
* fixed scaling
* no antialiasing
* stable pixel encoding (PNG)

---

### 4) Evidence Overlay Heatmap Image
**Pick: (A) Dynamically render PNG from heatmap values (deterministic).**

Same deterministic renderer rules. Include top-N regions + area % table.

---

### 5) Font Selection
**Pick: (A) reportlab built-in fonts — Helvetica (primary) + Courier for monospace blocks.**

---

### 6) PDF Metadata Stripping
**Pick: (B) Set metadata to fixed values derived from the sweep manifest.**

* Title/Author/Subject: fixed constants (e.g., "CLARITY Report")
* CreationDate/ModDate: set to manifest timestamp
* Producer: fixed constant

---

### 7) Run Manifest Timestamp Field
Precedence:
1. `manifest["created_at"]`
2. `manifest["timestamp"]`
3. fallback: `"1970-01-01T00:00:00Z"`

---

### 8) Monte Carlo Stats
**Conditionally omit.**

If not present: `Monte Carlo: not present in artifact bundle`.

---

### 9) Serialization Version
**Hardcode `M11_v1`.**

---

### 10) Frontend Integration Scope
**Pick: (A) single "Export Report" button.**

* Show only after case is loaded
* "Generating…" disabled state while in flight
* On success: trigger download
* On error: show single-line error banner

---

## 15️⃣ Additional Determinism Constraints

* PDF must be byte-identical for same case_id
* Ensure deterministic ordering of all lists
* Quantize all floats (8 decimals) before rendering
* Ensure PNG bytes are stable (no timestamps/chunks that vary)
* Stream bytes (preferred) — tests hash bytes directly

---

# ✅ Hand-Off Complete

Implementation may proceed.

