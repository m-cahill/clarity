# CLARITY Readiness Plan (M18–M24)

## Purpose

This plan defines a seven-milestone readiness program for CLARITY so it can be consumed safely by another repository **without ambiguity, contract drift, or hidden assumptions**.

The goal is **not** to add new reasoning capability, new model functionality, or new demo features. The goal is to make CLARITY **portable, governable, test-enforced, and legible** as a bounded evaluation instrument.

This plan is designed for direct handoff to Cursor for execution inside the CLARITY repo.

---

## Working Goal

By the end of **M24**, CLARITY must be able to answer, with evidence:

1. **What CLARITY is and is not**
2. **What surfaces are stable for consumers**
3. **What artifacts it reads and writes**
4. **What invariants it inherits and what it owns itself**
5. **What is implemented vs planned vs unknown**
6. **How another project should invoke it safely**
7. **Whether readiness is achieved, and what remains deferred**

---

## Readiness Definition

CLARITY is considered **readiness-complete** only when all of the following are true:

- its consumer-only boundary is frozen and CI-enforced
- its artifact contract is explicit, deterministic, and test-backed
- its public invocation surface is documented and snapshot/freeze tested
- its operating manual is sufficient for a new AI agent to operate it correctly
- its implementation status is honest and distinguishes implemented vs planned vs unknown
- its downstream consumer assumptions are explicit and minimal
- a final readiness scorecard gives a clear portable / not-yet-portable verdict with deferred issues recorded

---

## Non-Goals

These milestones must **not** be used to introduce unrelated scope.

Non-goals:

- no new CLARITY model features unless required to freeze a contract
- no redesign of the MedGemma path, demo UI, or Kaggle packaging
- no weakening of current CI gates
- no changes to R2L execution semantics, schemas, or CI behavior
- no downstream-project-specific integration work
- no speculative interfaces that are not implemented or actively frozen

---

## Cross-Milestone Rules

These rules apply to **every** milestone from M18–M24.

### 1. Source of truth

- `docs/clarity.md` remains the canonical project ledger and milestone record.
- `docs/readiness/` becomes the canonical readiness pack.
- If a readiness document is added, `docs/clarity.md` must be updated in the same milestone to reference it.

### 2. Document authority hierarchy

Unless explicitly redefined in M18, use this order:

1. `docs/clarity.md`
2. frozen contracts in `docs/readiness/`
3. current code + tests
4. milestone summaries / audits
5. aspirational documents

### 3. Additive discipline

- No breaking changes without an explicit “Contract Changes” section in the milestone summary.
- Prefer additive docs/tests/guardrails over structural refactors.
- Any unresolved issue must be deferred explicitly with rationale.

### 4. CI posture

- Green CI is required by default for milestone closure.
- Any new CI check must answer a new question.
- Do not add duplicate or redundant checks.
- Do not push post-closeout fixes onto a closed milestone branch; carry them into the next milestone branch.

### 5. Downstream-neutral language

All readiness docs must use generic language such as:

- “consumer project”
- “downstream repository”
- “external project”

Do **not** name a downstream consumer unless strictly necessary.

### 6. Evidence over narrative

Every milestone must end with:

- updated `docs/clarity.md`
- `MNN_summary.md`
- `MNN_audit.md`
- clear exit criteria evidence
- explicit deferred items if any remain

---

## Required `docs/readiness/` Structure by End of M24

At minimum, the readiness pack should contain:

```text
docs/readiness/
├── readinessplan.md
├── README.md
├── READINESS_LEDGER.md
├── READINESS_DECISIONS.md
├── CLARITY_BOUNDARY_CONTRACT.md
├── CLARITY_ASSUMED_GUARANTEES.md
├── CLARITY_ARTIFACT_CONTRACT.md
├── CLARITY_PUBLIC_SURFACE.md
├── CLARITY_OPERATING_MANUAL.md
├── CLARITY_IMPLEMENTATION_STATUS.md
├── CLARITY_CONSUMER_ASSUMPTIONS.md
├── CLARITY_COMPATIBILITY_MATRIX.md
├── CLARITY_TRANSFER_CHECKLIST.md
├── CLARITY_CHANGE_CONTROL.md
└── CLARITY_READINESS_SCORECARD.md
```

Notes:

- Some of these may be introduced earlier and refined later.
- Do not create placeholder documents that remain empty. Each document must be meaningful in the milestone where it is introduced.

---

# M18 — Readiness Charter & Authority Freeze

## Objective

Create the readiness program itself, freeze the purpose of `docs/readiness/`, and define what “portable” means for CLARITY.

## Why this milestone exists

CLARITY already has strong technical milestones through M17, but readiness for external consumption needs its own governed document set. This milestone creates the authority structure so later readiness docs do not drift or contradict each other.

## Scope

- create `docs/readiness/`
- place this plan in `docs/readiness/readinessplan.md`
- define readiness scope, terminology, and document ownership
- define authority hierarchy for readiness docs
- define readiness success criteria and non-goals
- extend `docs/clarity.md` with M18–M24 roadmap entries

## Documents to create/update

### Create

- `docs/readiness/README.md`
- `docs/readiness/READINESS_LEDGER.md`
- `docs/readiness/READINESS_DECISIONS.md`
- `docs/readiness/readinessplan.md` (copy of this plan)

### Update

- `docs/clarity.md`

## Required contents

### `README.md`

Must explain:

- what the readiness pack is for
- which docs are canonical
- what downstream-neutral language rules apply
- how to read the pack in the right order

### `READINESS_LEDGER.md`

Must include:

- readiness objective
- milestone table for M18–M24
- document inventory
- open risks / deferred issues table
- current readiness status: `NOT READY` at M18

### `READINESS_DECISIONS.md`

Must be a concise ADR-style running log for readiness-only decisions, including:

- why readiness docs live under `docs/readiness/`
- why downstream-specific naming is avoided
- why readiness is a separate track from feature development

## Code / tests / CI

Add only lightweight guardrails in M18:

- docs link check or equivalent existing-docs validation if practical
- test or script ensuring all readiness docs referenced in `README.md` actually exist
- no new heavy workflow unless clearly justified

## Exit criteria

- `docs/readiness/` exists with the core scaffolding docs
- `docs/clarity.md` references the readiness program and M18–M24 milestones
- authority hierarchy is documented
- readiness status is explicitly `NOT READY`
- CI remains green

## Milestone closeout requirements

- close with summary + audit
- record any naming or authority issues deferred to M19
- seed M19 folder after merge

---

# M19 — Consumer Boundary Freeze

## Objective

Turn the current CLARITY↔R2L boundary from draft context into a frozen consumer contract with explicit inherited guarantees and forbidden behaviors.

## Why this milestone exists

Portability fails first at the boundary. Before another repository can depend on CLARITY, it must know exactly what CLARITY is allowed to consume, what it must never change, and what guarantees it inherits rather than re-proves.

## Scope

- freeze the CLARITY consumer-only posture
- convert draft boundary material into canonical readiness docs
- define inherited guarantees from R2L / governance context
- define allowed vs forbidden integration patterns
- introduce boundary guardrail tests if missing or incomplete

## Documents to create/update

### Create

- `docs/readiness/CLARITY_BOUNDARY_CONTRACT.md`
- `docs/readiness/CLARITY_ASSUMED_GUARANTEES.md`

### Update

- `docs/readiness/READINESS_LEDGER.md`
- `docs/clarity.md`

## Required contents

### `CLARITY_BOUNDARY_CONTRACT.md`

Must freeze:

- consumer-only posture
- black-box invocation as the default allowed surface unless a public/stable Python surface is explicitly frozen later
- allowed R2L inputs consumed by CLARITY
- CLARITY-owned outputs and required namespace separation
- canonical vs rich-mode behavior
- deterministic seed-enumeration semantics
- forbidden behaviors

### `CLARITY_ASSUMED_GUARANTEES.md`

Modeled after an assumption contract. It must state what CLARITY inherits and therefore does **not** re-test at the substrate level, such as:

- deterministic single-run execution
- schema-validated substrate artifacts
- provider-agnostic adapter contract
- CI truthfulness of the substrate

It must also state what CLARITY **still must test**, such as:

- its own perturbation logic
- its aggregation logic
- its serialization stability
- its own output namespace and contracts

## Code / tests / CI

Required guardrails:

1. consumer contract test for parsing expected substrate artifacts
2. no-overwrite / namespace isolation test
3. compatibility test covering canonical mode and optional rich mode behavior

If a guardrail already exists, harden or document it rather than duplicating it.

## Exit criteria

- boundary contract is present and referenced by `docs/clarity.md`
- inherited guarantees vs CLARITY-owned responsibilities are explicit
- forbidden behaviors are listed and test-backed where appropriate
- boundary guardrails pass in CI

## Milestone closeout requirements

- explicitly document any boundary surfaces still draft and why
- no unresolved ambiguity about whether CLARITY is a consumer or extension layer

---

# M20 — Artifact Contract & Deterministic Output Freeze

## Objective

Freeze CLARITY’s output artifact model, serialization expectations, required/optional files, and reproducibility rules.

## Why this milestone exists

A downstream repository cannot safely parse, cache, compare, or trust CLARITY outputs without a stable artifact contract. This is the core portability layer.

## Scope

- document CLARITY artifact inventory
- define required vs optional outputs
- define stable naming and path rules
- define deterministic ordering and float serialization expectations
- define how artifact identity is determined
- back the contract with golden or snapshot-style tests

## Documents to create/update

### Create

- `docs/readiness/CLARITY_ARTIFACT_CONTRACT.md`

### Update

- `docs/readiness/READINESS_LEDGER.md`
- `docs/clarity.md`

## Required contents

`CLARITY_ARTIFACT_CONTRACT.md` must define:

- authoritative output namespace
- required artifacts
- optional artifacts
- JSON shape expectations for core outputs
- deterministic ordering rules
- stable float / numeric serialization rules
- whether PDFs/images are canonical outputs or derived presentation artifacts
- hash-participating vs presentation-only artifacts
- forward/backward compatibility rules

The contract must cover at minimum:

- `clarity/sweep_manifest.json`
- `clarity/robustness_surface.json`
- `clarity/monte_carlo_stats.json`
- report assets, if present
- visualization assets, if present

## Code / tests / CI

Required tests:

1. tiny sweep golden-output or stable-hash test
2. deterministic ledger ordering test
3. stable float serialization test
4. artifact completeness test for required outputs
5. presentation-only artifact exclusion test, if applicable

If schemas already exist, reference and validate them. If they do not exist, create only the minimal schemas needed to freeze the contract.

## Exit criteria

- artifact contract is explicit and test-backed
- required vs optional files are clear
- tiny sweep reruns produce stable contract-compliant output
- CI remains green with no weakening of existing checks

## Milestone closeout requirements

- record any intentionally non-canonical assets as such
- defer only truly optional surfaces, not core artifact ambiguity

---

# M21 — Public Surface & Invocation Contract

## Objective

Freeze the **one official consumer-facing way** to invoke CLARITY and define what parts of the codebase are public vs internal.

## Why this milestone exists

Readiness is not only about artifacts; it is also about how another repository starts CLARITY, passes configuration, and receives results without importing unstable internals.

## Scope

- define the stable invocation surface
- define public vs internal modules or commands
- define configuration expectations and environment variables
- define exit codes / failure semantics for the official surface
- add snapshot or freeze tests for the public surface

## Documents to create/update

### Create

- `docs/readiness/CLARITY_PUBLIC_SURFACE.md`

### Update

- `docs/readiness/READINESS_LEDGER.md`
- `docs/clarity.md`

## Required contents

`CLARITY_PUBLIC_SURFACE.md` must answer:

- what is the official public surface: CLI, Python facade, or both
- what is explicitly stable
- what is explicitly internal and unsupported for consumers
- what config is required
- what config is optional
- what exit conditions / failure modes the consumer should expect
- what versioning promises apply to the public surface

If both CLI and Python usage are retained, the document must define which is canonical and which is secondary.

## Code / tests / CI

Required tests:

1. public surface smoke test
2. help / usage / invocation contract test if CLI exists
3. consumer example test that uses only the sanctioned surface
4. snapshot or freeze test for exported public symbols if Python API exists

Prefer a thin stable facade over exposing deep internals.

## Exit criteria

- one official invocation surface is defined and documented
- public vs internal boundaries are explicit
- consumer smoke test passes using only the sanctioned surface
- no undocumented consumer dependency on internal modules remains

## Milestone closeout requirements

- any internal surfaces still used by tests must be justified or migrated
- public-surface versioning rules must be recorded

---

# M22 — Operating Manual & Honest Implementation Matrix

## Objective

Produce a manual that lets a new AI agent operate CLARITY correctly, and a status matrix that clearly distinguishes implemented vs planned vs unknown.

## Why this milestone exists

Portability fails when a new consumer or agent must read the entire repository to understand current truth. This milestone turns CLARITY into an operable system with a single readable guide.

## Scope

- write a full operating manual based on current implemented truth
- write an implementation-status matrix with honesty markers
- define runtime pipeline, debugging, extension rules, and frozen surfaces
- ensure the manual does not overstate aspirational features

## Documents to create/update

### Create

- `docs/readiness/CLARITY_OPERATING_MANUAL.md`
- `docs/readiness/CLARITY_IMPLEMENTATION_STATUS.md`

### Update

- `docs/readiness/README.md`
- `docs/readiness/READINESS_LEDGER.md`
- `docs/clarity.md`

## Required contents

### `CLARITY_OPERATING_MANUAL.md`

Should follow the proven operating-manual pattern used in other governed projects:

- what CLARITY is
- what CLARITY is not
- current implemented pipeline
- key concepts
- public invocation flow
- artifact flow
- determinism rules
- boundary rules
- debugging guide
- extension guide
- frozen surfaces / versioning discipline
- repo structure / quick reference

### `CLARITY_IMPLEMENTATION_STATUS.md`

Must be a table-driven status document with fields such as:

- surface
- status (`Implemented`, `Planned`, `Unknown`)
- owner / source-of-truth doc
- notes / limitations

Must cover at least:

- sweep orchestration
- metrics
- robustness surfaces
- report export
- UI console
- rich-mode ingestion
- public invocation surface
- compatibility guarantees

## Code / tests / CI

Required guardrails:

1. docs consistency test (manual surface names must match actual public surface names)
2. version / doc reference consistency check if feasible
3. no stale placeholder sections left labeled as current behavior

## Exit criteria

- a new AI agent could operate CLARITY from the manual plus public surface docs alone
- implementation status is explicit and honest
- no major “aspirational but undocumented as such” sections remain

## Milestone closeout requirements

- defer any manual sections that require future code only if clearly labeled
- update `docs/clarity.md` to reference the operating manual as a readiness artifact

---

# M23 — Consumer Assumptions, Compatibility Matrix & Transfer Checklist

## Objective

Create the downstream-consumer pack: what a consuming repository may safely assume, what compatibility matrix applies, and what checklist must be completed before adoption.

## Why this milestone exists

Even with good contracts and manuals, consumers still need a concise integration pack that answers: what do we inherit, what do we still need to validate, and what combinations are supported?

## Scope

- define consumer assumptions explicitly
- define supported compatibility combinations
- define the exact adoption checklist for a downstream repo
- add a minimal simulated-consumer smoke path if not already present

## Documents to create/update

### Create

- `docs/readiness/CLARITY_CONSUMER_ASSUMPTIONS.md`
- `docs/readiness/CLARITY_COMPATIBILITY_MATRIX.md`
- `docs/readiness/CLARITY_TRANSFER_CHECKLIST.md`

### Update

- `docs/readiness/READINESS_LEDGER.md`
- `docs/clarity.md`

## Required contents

### `CLARITY_CONSUMER_ASSUMPTIONS.md`

Must clearly state:

- what a consumer may assume is already proven
- what a consumer must still validate locally
- what changes would invalidate the assumption set
- what triggers a re-readiness review

### `CLARITY_COMPATIBILITY_MATRIX.md`

Must at minimum define support expectations for:

- canonical vs rich mode
- minimal artifact-only consumption vs full invocation
- optional report/UI assets
- required versions / SHAs recorded for the substrate and adapter context

### `CLARITY_TRANSFER_CHECKLIST.md`

Must be a practical checklist for another repo, including:

- dependency / version capture
- required environment/config
- public invocation path
- artifact locations consumed
- non-goals / forbidden shortcuts
- validation steps to confirm successful adoption

## Code / tests / CI

Required tests:

1. minimal consumer smoke test in a temp directory or fixture
2. compatibility-path test for the officially supported mode combinations
3. transfer checklist validation script if practical (even a lightweight one)

## Exit criteria

- consumer assumptions are explicit and minimal
- compatibility matrix exists and is grounded in real supported paths
- transfer checklist is actionable, not aspirational
- minimal consumer smoke path passes in CI

## Milestone closeout requirements

- record any unsupported combinations explicitly rather than leaving them ambiguous
- do not claim support for modes that have no test evidence

---

# M24 — Readiness Audit, Scorecard & Portability Verdict

## Objective

Perform the final readiness closeout: score the system, record the portability verdict, and lock change-control rules for future modifications.

## Why this milestone exists

A readiness program is incomplete without an explicit verdict. This milestone answers, with evidence, whether CLARITY is ready to move into another repository and what future changes must do to preserve that status.

## Scope

- perform final readiness audit
- produce scorecard and verdict
- define post-readiness change control
- update `docs/clarity.md` to mark readiness outcome
- explicitly defer unresolved non-blockers

## Documents to create/update

### Create

- `docs/readiness/CLARITY_CHANGE_CONTROL.md`
- `docs/readiness/CLARITY_READINESS_SCORECARD.md`

### Update

- `docs/readiness/READINESS_LEDGER.md`
- `docs/clarity.md`

## Required contents

### `CLARITY_CHANGE_CONTROL.md`

Must define:

- what changes are considered contract-affecting
- what requires a new readiness milestone
- what can change without re-running the full readiness program
- when to bump versions / tags
- how to record compatibility-impacting changes

### `CLARITY_READINESS_SCORECARD.md`

Must include a scored review of at least:

- identity clarity
- boundary freeze completeness
- artifact contract completeness
- public surface stability
- manual operability
- compatibility / consumer kit completeness
- CI guardrail sufficiency
- deferred issue posture

It must end with one of these explicit verdicts:

- `READY FOR DOWNSTREAM ADOPTION`
- `CONDITIONALLY READY`
- `NOT READY`

If the verdict is conditional, all conditions must be listed and linked to deferred issues.

## Code / tests / CI

Required final evidence:

- full readiness guardrail suite green
- manual / public surface / artifact contract / consumer smoke evidence all passing
- no unresolved blocker-class issue left undocumented

## Exit criteria

- final readiness verdict recorded
- change-control rules recorded
- readiness ledger updated to closed state
- `docs/clarity.md` updated with M24 closeout and document index
- next milestone folder seeded only after readiness closeout is complete

## Milestone closeout requirements

- final summary and audit must explicitly state whether portability was achieved
- if portability is not achieved, list exact remaining blockers and the next milestone(s) required

---

## Recommended CI / Guardrail Map Across M18–M24

This is the intended progression. Reuse existing workflows where possible.

### M18
- readiness-doc inventory / link validation

### M19
- consumer boundary parsing test
- namespace isolation test
- canonical vs rich compatibility test

### M20
- tiny sweep stable-hash or stable-ledger test
- artifact completeness test
- numeric serialization stability test

### M21
- public surface smoke test
- sanctioned-consumer-only test
- export snapshot/freeze test

### M22
- docs/manual consistency test
- version/reference sanity check

### M23
- temp-consumer integration smoke test
- supported-mode compatibility test

### M24
- aggregate readiness verification job or script

---

## Required Updates to `docs/clarity.md` at Every Milestone

For **every** milestone M18–M24, Cursor must update `docs/clarity.md` with:

- current milestone status
- milestone table row
- key deliverables added in that milestone
- readiness-specific document references
- deferred issue changes, if any

`docs/clarity.md` must continue to act as the canonical project ledger.

---

## Standard Milestone Workflow for Cursor

For each milestone M18–M24, Cursor should follow this exact pattern:

1. create or update `milestones/MNN/MNN_plan.md` from the relevant section of this readiness plan
2. implement only that milestone’s scoped work
3. run the smallest meaningful end-to-end verification for that milestone
4. push and observe CI
5. if CI fails, fix within the same open milestone branch when appropriate
6. after green CI, generate:
   - `MNN_summary.md`
   - `MNN_audit.md`
7. update `docs/clarity.md`
8. seed the next milestone folder with a stub `MNN+1_plan.md` and `toolcalls.md`

Avoid post-closeout commits on a closed milestone whenever possible.

---

## Suggested Tags

Assuming the existing tag sequence continues from `v0.0.18-m17`, the suggested tags are:

- `v0.0.19-m18`
- `v0.0.20-m19`
- `v0.0.21-m20`
- `v0.0.22-m21`
- `v0.0.23-m22`
- `v0.0.24-m23`
- `v0.0.25-m24`

Use only if consistent with the repo’s current tagging practice.

---

## Final Expected Outcome After M24

By the end of M24, CLARITY should have:

- a readiness pack under `docs/readiness/`
- a frozen consumer boundary
- a frozen artifact contract
- a documented public surface
- an honest operating manual
- a consumer assumptions contract
- a compatibility matrix and transfer checklist
- a final readiness scorecard with an explicit verdict

That is the minimum evidence needed to say CLARITY is ready to be consumed by another repository without relying on tribal knowledge.
