# M16 Manual UI Validation

## Validation Metadata

| Field | Value |
|-------|-------|
| **Milestone** | M16 |
| **Date** | _[Fill in: YYYY-MM-DD]_ |
| **Validator** | _[Fill in: name]_ |
| **Frontend URL** | http://localhost:5173 (local) or https://majestic-dodol-25e71c.netlify.app (demo) |
| **Backend URL** | http://localhost:8000 (local) or https://clarity-1sra.onrender.com (demo) |
| **Browser** | _[Fill in: Chrome / Firefox / Edge + version]_ |
| **Resolution** | _[Fill in: e.g., 1920×1080]_ |

---

## Pre-Validation Setup

Before beginning:

- [ ] Backend is running (`uvicorn app.main:app --reload`)
- [ ] Frontend is running (`npm run dev`)
- [ ] Browser devtools console is open (F12)
- [ ] Console is cleared

---

## Validation Checklist

### 1. Real Artifact Load

- [ ] Navigate to UI console
- [ ] Load case `case_m15_real` (real MedGemma artifacts)
- [ ] Artifact loads without errors
- [ ] Sweep manifest visible
- [ ] No loading spinners stuck

**Console errors at this step**: _[None / list any]_

---

### 2. Seed Toggle

- [ ] Toggle seed from 42 → 123
- [ ] Surface updates without full page reload
- [ ] No NaN displayed in any surface value
- [ ] No JavaScript error in console

**Console errors at this step**: _[None / list any]_

---

### 3. Axis Toggle

- [ ] Toggle perturbation axis from brightness → contrast
- [ ] Surface re-renders correctly
- [ ] Axis label updates
- [ ] No broken heatmap tiles

**Console errors at this step**: _[None / list any]_

---

### 4. Counterfactual Run

- [ ] Navigate to counterfactual panel
- [ ] Initiate counterfactual probe (region masking)
- [ ] Request completes without 500 error
- [ ] Diagnosis delta is displayed
- [ ] No NaN in counterfactual output

**Console errors at this step**: _[None / list any]_

---

### 5. Report Export

- [ ] Click export report
- [ ] Report downloads (PDF or JSON)
- [ ] File is non-empty and opens correctly
- [ ] Exported metrics match UI values

**Console errors at this step**: _[None / list any]_

---

### 6. Page Refresh

- [ ] Hard refresh (Ctrl+Shift+R)
- [ ] Page reloads without error
- [ ] No hydration mismatch warning in console
- [ ] State resets cleanly (no stale artifact loaded)

**Console errors at this step**: _[None / list any]_

---

### 7. Synthetic Case Load

- [ ] Load case `case_001` (synthetic artifact)
- [ ] Surfaces render correctly
- [ ] No schema mismatch errors
- [ ] Values are non-NaN

**Console errors at this step**: _[None / list any]_

---

### 8. Browser Resize

- [ ] Resize browser to narrow viewport (~768px wide)
- [ ] UI layout adjusts without overflow
- [ ] Heatmaps remain visible and proportional
- [ ] Resize back to full width
- [ ] No layout regression

**Console errors at this step**: _[None / list any]_

---

## Pass/Fail Summary

| Check | Result |
|-------|--------|
| Real artifact load | ⬜ Pass / ⬜ Fail |
| Seed toggle | ⬜ Pass / ⬜ Fail |
| Axis toggle | ⬜ Pass / ⬜ Fail |
| Counterfactual run | ⬜ Pass / ⬜ Fail |
| Report export | ⬜ Pass / ⬜ Fail |
| Page refresh | ⬜ Pass / ⬜ Fail |
| Synthetic case load | ⬜ Pass / ⬜ Fail |
| Browser resize | ⬜ Pass / ⬜ Fail |

---

## Console Summary

| Category | Count |
|----------|-------|
| Errors | _[Fill in]_ |
| Warnings | _[Fill in]_ |
| NaN values observed | _[Fill in]_ |
| React warnings | _[Fill in]_ |
| TypeScript runtime warnings | _[Fill in]_ |

---

## Issues Found

_[List any issues. If none: "No issues found."]_

---

## Final Verdict

- [ ] **PASS** — All checks green, zero console errors, zero NaN
- [ ] **FAIL** — Issues listed above

**Validator signature**: _[Fill in]_

**Date**: _[Fill in]_
