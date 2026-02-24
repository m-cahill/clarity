# M17 — Deployment & Demo Stabilization

## Milestone Mode

**DELTA AUDIT — Deployment Hardening**

No new features. No schema changes. No model or inference changes.

Scope: resolve deployed-demo failures and validate production readiness.

---

## Objective

1. Resolve frontend "Failed to fetch" issue in deployed demo.
2. Audit CORS configuration (backend and hosting).
3. Validate deployed endpoints (Netlify frontend ↔ Render backend).
4. Preserve deterministic inference path; no changes to artifact generation or hashes.

---

## Out of Scope (This Milestone)

- New UI features
- Backend API changes beyond CORS/config
- Regenerating or modifying submission artifacts
- Model or runner changes

---

## Success Criteria (To Be Refined in M17 Kickoff)

- Deployed demo loads data without "Failed to fetch".
- CORS and network path documented and verified.
- Deterministic inference and artifact hashes unchanged.

---

*No implementation in this milestone yet. Plan will be expanded at M17 kickoff.*
