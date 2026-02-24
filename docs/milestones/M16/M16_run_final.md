# M16 Run Final — Competition Submission Freeze

## Canonical Audit Trail

This document records the **submission-freeze state** for the MedGemma Impact Challenge (Kaggle). It is the authoritative reference for what was submitted and how to reproduce it.

---

## Kaggle Submission

| Field | Value |
|-------|--------|
| **Competition** | MedGemma Impact Challenge |
| **Submission confirmation** | Submitted successfully (Kaggle submission accepted) |
| **Submission timestamp** | _[Fill: date/time when submission was made]_ |
| **Repository at submission** | Tag `v0.0.17-m16` (commit _[pending tag]_ ) |

---

## Final Artifact Hashes (Locked)

| Artifact | SHA-256 |
|----------|---------|
| **Bundle** | `26de75db866aafa813cb25ef63ee3c1f34e14eda0d07d7de567957d2d46a58bc` |
| **Summary** | `fba587054c9f63149eba704a703fa8bcb4c5a2d2f96997857fba5c9a8d6166e6` |

Do not regenerate or modify these artifacts. They define the competition submission state.

---

## Repository & Tag

| Item | Value |
|------|--------|
| **Repo** | [m-cahill/clarity](https://github.com/m-cahill/clarity) |
| **Release tag** | `v0.0.17-m16` |
| **Tag message** | M16 — Kaggle Submission Freeze (deterministic MedGemma evaluation verified; canonical artifact hashes locked; submission package finalized; demo deployment issue deferred to M17) |

---

## Links

| Link | URL |
|------|-----|
| **Repository** | https://github.com/m-cahill/clarity |
| **Video / demo** | _[Fill: link to submission video or demo if applicable]_ |

---

## Governance

- **M16** = competition state; deterministic artifact lock; no post-submission mutation.
- **M17** = Deployment & Demo Stabilization (frontend "Failed to fetch" / CORS deferred to M17).

---

## Tag & Push Steps (Run After Commit)

Working tree must be clean (all submission-freeze changes committed) before tagging.

1. **Commit** (if not already done):
   ```bash
   git add -A
   git commit -m "M16 closeout — submission freeze; defer deployment issue to M17"
   git push origin main
   ```

2. **Create and push tag**:
   ```bash
   git tag -a v0.0.17-m16 -m "M16 — Kaggle Submission Freeze

   - Deterministic MedGemma evaluation verified
   - Canonical artifact hashes locked
   - Submission package finalized
   - Demo deployment issue deferred to M17"
   git push origin v0.0.17-m16
   ```

3. **Verify**: `git status` clean, `git tag -l "v0.0.17*"` shows `v0.0.17-m16`, tag visible on GitHub.

---

*Document created at M16 closeout. Update submission timestamp and video link when known.*
