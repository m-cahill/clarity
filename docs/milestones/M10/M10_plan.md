# 📌 M10 Plan — Visualization Overlays (Evidence Maps + Saliency Heatmaps)

**Milestone:** M10 — Visualization Overlays  
**Baseline Tag:** `v0.0.10-m09`  
**Branch:** `m10-visualization`  
**Audit Mode:** DELTA  
**Competition Deadline:** Feb 24, 2026 (4 days)

---

## 🎯 M10 Objective

M09 made counterfactual experiments executable.

M10 makes them **interpretable**.

This milestone will:

1. Implement **evidence-map-derived region overlays** (CF-001 closure).
2. Add **saliency heatmap visualization** to the UI.
3. Render overlays on the baseline image in the `/counterfactual` console.
4. Maintain full determinism and CI safety (stubbed runner preserved).

After M10, CLARITY can visually demonstrate:

> "When we remove this region, the model's reasoning shifts — and here's the evidence map showing why."

---

## 🔒 Locked Answers

### 1) Evidence Map Source — Stubbed vs Real

✅ **A — Fixed synthetic pattern (deterministic), not derived from image content.**

* Use a **simple deterministic pattern** (2–3 Gaussian-like bumps computed analytically).
* Store pattern parameters in code constants for stability across runs.
* No edge detection / content-derived transforms.

### 2) Heatmap Rendering Location

✅ **A — Backend returns raw normalized float matrix (2D [0,1])**, frontend applies colormap.

* Backend outputs: `width`, `height`, `values: list[list[float]]` (8-decimal rounded)
* Frontend applies: fixed colormap mapping + opacity scaling

### 3) CF-001 Closure — Threshold Value

✅ **A — Fixed threshold = 0.7 (hard-coded constant).**

* Not configurable in API for M10.
* Single canonical extraction rule for CF-001 closure.

### 4) OverlayBundle in API Response

✅ **A — Always included** in `POST /counterfactual/run` response.

* Keep response deterministic and complete.
* UI decides what to display via toggles.

### 5) Sub-phase Strategy

✅ **B — M10a then M10b within same milestone PR.**

1. **M10a:** Heatmap overlay pipeline (stubbed evidence → API → UI render)
2. **M10b:** Evidence-derived region extraction (threshold + BFS) + UI toggle

### 6) Frontend Rendering Technique

✅ **A — HTML5 Canvas**

* Render heatmap via `ImageData`
* Apply fixed colormap and alpha in pure function
* Use div overlays only for bounding boxes

### 7) Test Count Distribution

✅ **Backend ≥50, Frontend ≥20 (≥70 total)**

* Backend: 55–75 tests
* Frontend: 20–30 tests
* E2E: Keep existing 5, add 1–2 overlay assertions max

### Additional Guardrails

1. **No new dependencies** (backend or frontend).
2. **Region extraction output stable sorted** by `(area desc, x asc, y asc)`.

---

## 🧱 Architectural Scope

### Backend Additions

New module:

```
backend/app/clarity/evidence_overlay.py
```

Responsibilities:

* Parse runner output for evidence maps
* Normalize evidence to 2D heatmap (fixed resolution)
* Generate deterministic `RegionMask` objects from evidence clusters
* Provide overlay-ready structures (no image drawing server-side)

New dataclasses:

* `EvidenceMap` — Raw evidence values from runner
* `Heatmap` — Normalized 2D float matrix [0,1]
* `OverlayRegion` — Bounding box from threshold + BFS
* `OverlayBundle` — Complete overlay data for API response

Update orchestrator:

* Extend `StubbedRunner` to return deterministic evidence maps
* Include `OverlayBundle` in `OrchestratorResult`
* Expose overlay data via API response

### Frontend Additions

Enhance `/counterfactual` route:

* Add image display component
* Overlay heatmap layer (canvas)
* Toggle controls:
  * Show grid masks
  * Show evidence heatmap
  * Show evidence-derived regions

Pure React + CSS + Canvas (no new dependencies).

---

## 🔬 Visualization Model

### Evidence Map (Stubbed in CI)

StubbedRunner returns deterministic evidence arrays:

```json
{
  "width": 224,
  "height": 224,
  "values": [[0.0, 0.01, ...], ...]
}
```

Pattern: 2–3 Gaussian bumps at fixed positions, analytically computed.

### Heatmap Normalization

Rules:

* Min-max normalize
* Clip to [0,1]
* Round to 8 decimals
* Fixed resolution matching image

### Region Extraction (CF-001 Closure)

Algorithm:

1. Threshold evidence map (> 0.7)
2. Connected component grouping (deterministic BFS, row-major order)
3. Generate bounding boxes
4. Sort by `(area desc, x asc, y asc)`
5. Convert to `OverlayRegion`

Pure deterministic BFS. No sklearn, no numpy randomness.

---

## 🧪 Test Plan

### Backend (≥50 new tests)

Categories:

1. Evidence normalization correctness
2. Threshold behavior edge cases
3. Connected component grouping (BFS)
4. Bounding box extraction
5. Determinism double-run equality
6. Stubbed evidence reproducibility
7. OverlayBundle serialization
8. No forbidden imports (AST test)
9. No random usage
10. No R2L import
11. Gaussian bump pattern correctness
12. Empty evidence handling
13. All-above-threshold handling
14. Region sorting verification

### Frontend (≥20 new tests)

1. Image renders
2. Heatmap layer renders
3. Toggle on/off works
4. Overlay opacity control
5. Canvas colormap application
6. API integration with overlay_bundle
7. Region bounding box display
8. Multiple toggle combinations

---

## 🔒 Determinism Requirements

Must preserve:

* 8-decimal rounding
* Fixed threshold value (0.7)
* Stable BFS traversal order (row-major)
* Sorted region list by (area desc, x asc, y asc)
* Fixed colormap mapping
* No GPU involvement in CI

---

## 📊 API Changes

Extend `POST /counterfactual/run` response:

```json
{
  "baseline_id": "...",
  "baseline_metrics": {...},
  "config": {...},
  "probe_surface": {...},
  "overlay_bundle": {
    "evidence_map": {
      "width": 224,
      "height": 224,
      "values": [[...], ...]
    },
    "heatmap": {
      "width": 224,
      "height": 224,
      "values": [[...], ...]
    },
    "regions": [
      {
        "region_id": "evidence_r0",
        "x_min": 0.2,
        "y_min": 0.3,
        "x_max": 0.5,
        "y_max": 0.6,
        "area": 0.09
      }
    ]
  }
}
```

No breaking changes.

---

## 🏁 Definition of Done

- [ ] `evidence_overlay.py` implemented
- [ ] CF-001 removed from deferred registry
- [ ] UI heatmap overlay renders
- [ ] UI region overlay renders
- [ ] ≥70 total new tests
- [ ] ≥95% coverage backend module
- [ ] No workflow changes
- [ ] CI green first run
- [ ] clarity.md updated
- [ ] Tag: `v0.0.11-m10`

---

## ⚠️ Risk Assessment

| Risk | Mitigation |
|------|------------|
| Visual bug breaks E2E | Keep overlay isolated component |
| Threshold produces no regions | Add fallback empty state |
| Performance regression | Use small fixed-size heatmaps |
| CI slowdown | Avoid heavy libs |
| Over-scope | No charts, no D3, no fancy animation |

---

## 📌 Execution Steps

### Phase M10a (Heatmap Pipeline)

1. Create branch `m10-visualization`
2. Implement `evidence_overlay.py` with EvidenceMap, Heatmap, OverlayBundle
3. Extend StubbedRunner to return evidence maps
4. Extend orchestrator to include OverlayBundle
5. Update API response schema
6. Implement frontend canvas heatmap rendering
7. Add toggle controls
8. Write M10a tests

### Phase M10b (Region Extraction)

9. Implement threshold + BFS region extraction
10. Add OverlayRegion dataclass
11. Implement region sorting
12. Add UI region bounding box display
13. Write M10b tests
14. Close CF-001

### Finalization

15. Run full CI matrix
16. Generate M10_run1.md
17. Await merge permission

---

*Plan locked. Ready for implementation.*
