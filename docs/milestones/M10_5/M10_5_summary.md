# M10.5 Summary — Demo Deployment Layer

## Mission

Deploy a **read-only, deterministic demo instance** of CLARITY for external viewing without introducing GPU execution into cloud infrastructure.

---

## What Was Built

### Backend Demo Service

- **New module**: `backend/app/demo_router.py` (394 lines)
  - Read-only artifact serving endpoints
  - Path traversal protection (regex + resolve validation)
  - Checksum verification endpoint
  - No R2L dependencies, no subprocess, no write operations

- **Endpoints**:
  - `GET /demo/health` — Demo health status
  - `GET /demo/cases` — List available demo cases
  - `GET /demo/cases/{id}/manifest` — Case manifest
  - `GET /demo/cases/{id}/surface` — Robustness surface
  - `GET /demo/cases/{id}/overlay` — Overlay bundle
  - `GET /demo/cases/{id}/metrics` — Case metrics
  - `GET /demo/cases/{id}/verify` — Integrity verification

### Demo Artifacts

- **Location**: `demo_artifacts/case_001/`
- **Files**: manifest.json, robustness_surface.json, overlay_bundle.json, metrics.json, checksums.json
- **Properties**: Synthetic data, clearly labeled, checksummed, version-controlled

### Frontend Demo Support

- **API URL switching**: `VITE_API_BASE_URL` environment variable support
- **Demo banner**: `DemoBanner.tsx` component displaying "Demo Mode — Precomputed Artifacts (Synthetic)"
- **Mode detection**: `VITE_APP_MODE=demo` environment variable

### Deployment Infrastructure

- **Netlify**: 
  - `netlify.toml` — Build configuration, SPA redirects, security headers
  - `frontend/public/_redirects` — Fallback SPA routing

- **Render**:
  - `render.yaml` — Blueprint with rootDir, build/start commands, env vars
  - `backend/requirements.txt` — Render-compatible dependency file

- **GitHub Actions**:
  - `deploy.yml` — Separate deploy workflow
  - Preview deploys on PR
  - Production deploys on main
  - Auto-skip if secrets missing
  - Post-deploy health checks

---

## Test Coverage

| Component | Tests Added |
|-----------|-------------|
| Backend (test_demo_router.py) | 33 |
| Frontend (DemoBanner.test.tsx) | 10 |
| E2E (demo.spec.ts) | 4 |
| **Total** | **47** |

---

## Guardrails Enforced

1. **No R2L imports** — AST-verified in demo_router.py
2. **No subprocess** — AST-verified
3. **No write operations** — AST-verified
4. **Path traversal protection** — 6 dedicated tests
5. **Checksum integrity** — SHA256 verification
6. **Line ending consistency** — `.gitattributes` enforces LF for JSON

---

## Architecture Preserved

- Demo router activates conditionally (`APP_ENV=demo`)
- Full CLARITY system unaffected
- No coupling between demo and production code paths
- Synthetic artifacts clearly labeled

---

## Files Changed

| Type | Count |
|------|-------|
| New files | 20 |
| Modified files | 6 |
| Lines added | ~2,165 |
| Lines removed | ~63 |

---

## CI Status

| Run | Status |
|-----|--------|
| Pre-merge | ✅ GREEN |
| Post-merge | ✅ GREEN (Run 22248667956) |

---

## Deployment Status

| Platform | Status |
|----------|--------|
| Netlify | ✅ Configured via netlify.toml |
| Render | ⚙️ Configured via render.yaml (manual service creation needed) |

---

## Next Steps

1. **Render manual setup**: Create service from render.yaml blueprint
2. **M11**: Report Export Hardening
3. **M12**: Operational Hardening

---

*Summary generated per `docs/prompts/summaryprompt.md` guidelines.*

