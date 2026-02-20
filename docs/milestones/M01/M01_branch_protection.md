# M01 — Branch Protection Configuration

**Issue:** GOV-001: Configure branch protection for main  
**Milestone:** M01 — Boundary Guardrails  
**Status:** Pending manual configuration

---

## Overview

This document provides the exact CLI commands to configure branch protection for the `main` branch. Branch protection ensures:

1. All pushes go through PRs
2. CI must pass before merge
3. Admins are also subject to these rules

---

## Prerequisites

- Repository admin permissions
- GitHub CLI (`gh`) authenticated with appropriate scopes

---

## Configuration Commands

### Option 1: GitHub CLI (`gh api`)

```bash
gh api repos/m-cahill/clarity/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CI Success"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null
```

### Option 2: GitHub Web UI

1. Navigate to: `https://github.com/m-cahill/clarity/settings/branches`
2. Click "Add rule" for branch `main`
3. Configure:
   - ☑️ Require a pull request before merging
     - Required approving reviews: 1
   - ☑️ Require status checks to pass before merging
     - ☑️ Require branches to be up to date before merging
     - Add required check: `CI Success`
   - ☑️ Include administrators
4. Click "Create" / "Save changes"

---

## Verification

After configuration, verify with:

```bash
gh api repos/m-cahill/clarity/branches/main/protection
```

Expected response should include:
- `required_status_checks.contexts` containing `"CI Success"`
- `enforce_admins.enabled` = `true`
- `required_pull_request_reviews.required_approving_review_count` = `1`

---

## GitHub Issue Template

Create an issue with:

**Title:** `GOV-001: Configure branch protection for main (M01 requirement)`

**Body:**

```markdown
## Summary

Configure branch protection rules for the `main` branch as required by M01 governance.

## Requirements

- [ ] Require pull request before merging
- [ ] Require at least 1 approving review
- [ ] Require status checks to pass (`CI Success`)
- [ ] Require branches to be up to date before merging
- [ ] Include administrators

## Commands

See `docs/milestones/M01/M01_branch_protection.md` for exact CLI commands.

## References

- M01 Plan: `docs/milestones/M01/M01_plan.md`
- M00 Audit Issue: CI-002, GOV-001
```

---

## Acceptance Criteria

Branch protection is configured when:

- [ ] Direct pushes to `main` are blocked
- [ ] PRs require `CI Success` check to pass
- [ ] PRs require at least 1 approval
- [ ] Configuration verified via `gh api` command

---

*End of Branch Protection Configuration*

