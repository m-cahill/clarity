# M16 Tool Calls Log

## Milestone: M16 — Kaggle Submission Packaging & Competition Positioning

---

| # | Timestamp | Tool | Purpose | Files / Target | Status |
|---|-----------|------|---------|----------------|--------|
| 001 | 2026-02-21 21:41 | Shell | Create M16 and kaggle_submission directory scaffold | `docs/milestones/M16/`, `docs/kaggle_submission/screenshots/`, `docs/kaggle_submission/example_bundle/` | ✅ Complete |
| 002 | 2026-02-21 21:41 | Read | Inspect M15 baseline artifacts for bundle content | `backend/tests/fixtures/baselines/m15_real_ui/*` | ✅ Complete |
| 003 | 2026-02-21 21:42 | Write | Create M16_plan.md | `docs/milestones/M16/M16_plan.md` | ✅ Complete |
| 004 | 2026-02-21 21:42 | Write | Create M16_toolcalls.md (this file) | `docs/milestones/M16/M16_toolcalls.md` | ✅ Complete |
| 005 | 2026-02-21 21:42 | Write | Phase 2 — Create README_KAGGLE.md | `docs/kaggle_submission/README_KAGGLE.md` | ✅ Complete |
| 006 | 2026-02-21 21:42 | Write | Phase 5 — Create architecture.md (Mermaid) | `docs/kaggle_submission/architecture.md` | ✅ Complete |
| 007 | 2026-02-21 21:42 | Write | Phase 7 — Create EXECUTIVE_SUMMARY.md | `docs/kaggle_submission/EXECUTIVE_SUMMARY.md` | ✅ Complete |
| 008 | 2026-02-21 21:42 | Shell | Phase 4 — Copy baseline artifacts to example_bundle | `docs/kaggle_submission/example_bundle/` | ✅ Complete |
| 009 | 2026-02-21 21:42 | Write | Phase 4 — Create BUNDLE_README.md | `docs/kaggle_submission/example_bundle/BUNDLE_README.md` | ✅ Complete |
| 010 | 2026-02-21 21:44 | Write | Phase 6 — Create M16_manual_validation.md template | `docs/milestones/M16/M16_manual_validation.md` | ✅ Complete |
| 011 | 2026-02-21 21:44 | Write | Phase 1 — Create M16_reproducibility_report.md | `docs/milestones/M16/M16_reproducibility_report.md` | ✅ Complete |
| 012 | 2026-02-22 | WebFetch | Verify CC0 license on Wikimedia Commons PA chest radiograph | Wikimedia Commons file page | ✅ Complete |
| 013 | 2026-02-22 | Shell | Download CC0 PA chest radiograph (500px thumbnail) from Wikimedia Commons | `backend/tests/fixtures/baselines/clinical_cxr_download.jpg` | ✅ Complete |
| 014 | 2026-02-22 | Shell | Convert JPG to RGB PNG, resize to 447×512 (LANCZOS), replace synthetic fixture | `backend/tests/fixtures/baselines/clinical_sample_01.png` | ✅ Complete |
| 015 | 2026-02-22 | Write | Create image provenance document | `backend/tests/fixtures/baselines/clinical_sample_01.PROVENANCE.md` | ✅ Complete |
| 016 | 2026-02-22 | StrReplace | Fix generate() — replace boi_token prefix with apply_chat_template + add_generation_prompt | `backend/app/clarity/medgemma_runner.py` | ✅ Complete |
| 017 | 2026-02-22 | StrReplace | Fix generate() — remove pad_token_id=eos_token_id, fix input_length decoding | `backend/app/clarity/medgemma_runner.py` | ✅ Complete |
| 018 | 2026-02-22 | StrReplace | Fix generate_rich() — same prompt format + pad_token_id fixes | `backend/app/clarity/medgemma_runner.py` | ✅ Complete |
| 019 | 2026-02-22 | StrReplace | Update registry.json description for clinical-sample-01 | `backend/tests/fixtures/baselines/registry.json` | ✅ Complete |
| 020 | 2026-02-22 | Shell | Run sweep — hit AttributeError: apply_chat_template returns str not tensors | `scripts/m15_real_ui_sweep.py` | ❌ Error |
| 021 | 2026-02-22 | StrReplace | Fix generate() and generate_rich(): two-step approach (apply_chat_template → str, then processor() → tensors) | `backend/app/clarity/medgemma_runner.py` | ✅ Complete |
| 022 | 2026-02-22 | Shell | Run sweep again — still degenerate (confidence 0.0, NaN logits) despite prompt fix | `scripts/m15_real_ui_sweep.py` | ❌ Degenerate |
| 023 | 2026-02-22 | StrReplace | Fix dtype: float16 → bfloat16 (Gemma3/MedGemma requires bfloat16; float16 overflows to NaN in image-conditioned forward pass) | `backend/app/clarity/medgemma_runner.py` | ✅ Complete |
| 024 | 2026-02-22 | Shell | Run sweep with bfloat16 — SUCCESS: confidence 0.80611376, token_count 342, real diagnostic text, deterministic across 2 runs | `scripts/m15_real_ui_sweep.py` | ✅ Complete |
| 025 | 2026-02-22 | Shell | Copy new validated artifacts to example_bundle | `docs/kaggle_submission/example_bundle/*` | ✅ Complete |
| 026 | 2026-02-22 | StrReplace | Update hash tables in README_KAGGLE.md (Section 3.2 + verification script) | `docs/kaggle_submission/README_KAGGLE.md` | ✅ Complete |
| 027 | 2026-02-22 | StrReplace | Update hash tables and signal metrics in M16_reproducibility_report.md | `docs/milestones/M16/M16_reproducibility_report.md` | ✅ Complete |
| 028 | 2026-02-22 | StrReplace | Update hash tables and findings in BUNDLE_README.md | `docs/kaggle_submission/example_bundle/BUNDLE_README.md` | ✅ Complete |
| 029 | 2026-02-22 | StrReplace | Update clarity.md — add M16 corrected artifact evidence section with new hashes | `docs/clarity.md` | ✅ Complete |
