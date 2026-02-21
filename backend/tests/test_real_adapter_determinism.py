"""Real Adapter Determinism Tests for M13.

These tests verify that the MedGemma adapter produces deterministic
output for identical inputs (same image, prompt, seed).

CRITICAL: These tests are GATED behind CLARITY_REAL_MODEL=true.
They require a GPU and the MedGemma model to be available.

In CI:
- Tests are SKIPPED (not trivially passed)
- CI uses StubbedRunner for synthetic path
- No GPU requirement in CI

Locally (with CLARITY_REAL_MODEL=true):
- Tests run with real MedGemma inference
- Verify deterministic bundle SHA
- Track VRAM usage

Contract Guardrail (M13):
    Given:
        same image
        same prompt
        same seed
    Then:
        artifact bundle SHA is identical

Failing this blocks merge.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Skip all tests in this module if CLARITY_REAL_MODEL is not set
pytestmark = pytest.mark.skipif(
    not os.getenv("CLARITY_REAL_MODEL", "").lower() in ("true", "1", "yes", "on"),
    reason="Real model tests require CLARITY_REAL_MODEL=true",
)


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "baselines"


class TestRealAdapterDeterminism:
    """Test deterministic behavior of real MedGemma adapter."""

    def test_same_seed_produces_identical_hash(self) -> None:
        """Verify same (prompt, seed) produces identical bundle SHA.

        This is the core M13 guardrail test.

        Given:
            same prompt
            same seed

        Then:
            artifact bundle SHA is identical
        """
        from app.clarity.medgemma_runner import MedGemmaRunner

        runner = MedGemmaRunner()

        prompt = "Analyze this chest X-ray for any abnormalities."
        seed = 42

        # Run 1
        result1 = runner.generate(prompt, seed=seed)

        # Run 2 (same inputs)
        result2 = runner.generate(prompt, seed=seed)

        # Assert determinism
        assert result1.bundle_sha == result2.bundle_sha, (
            f"Determinism violation: same inputs produced different hashes.\n"
            f"Run 1 SHA: {result1.bundle_sha}\n"
            f"Run 2 SHA: {result2.bundle_sha}\n"
            f"Run 1 text: {result1.text[:100]}...\n"
            f"Run 2 text: {result2.text[:100]}..."
        )

    def test_different_seeds_produce_different_hashes(self) -> None:
        """Verify different seeds produce different bundle SHAs.

        This confirms that seed actually affects output (or at minimum,
        the hash includes the seed).
        """
        from app.clarity.medgemma_runner import MedGemmaRunner

        runner = MedGemmaRunner()

        prompt = "Analyze this chest X-ray for any abnormalities."

        # Run with seed 42
        result1 = runner.generate(prompt, seed=42)

        # Run with seed 123
        result2 = runner.generate(prompt, seed=123)

        # Hashes should differ (at minimum due to seed in hash)
        assert result1.bundle_sha != result2.bundle_sha, (
            "Different seeds should produce different hashes"
        )

    def test_multimodal_determinism_with_image(self) -> None:
        """Verify determinism with image input.

        Uses the clinical_sample_01.png fixture.
        """
        from PIL import Image

        from app.clarity.medgemma_runner import MedGemmaRunner

        # Load fixture image
        image_path = FIXTURES_DIR / "clinical_sample_01.png"
        if not image_path.exists():
            pytest.skip(f"Fixture not found: {image_path}")

        image = Image.open(image_path)
        runner = MedGemmaRunner()

        prompt = "Describe any findings in this chest X-ray image."
        seed = 42

        # Run 1
        result1 = runner.generate(prompt, seed=seed, image=image)

        # Run 2 (same inputs)
        result2 = runner.generate(prompt, seed=seed, image=image)

        # Assert determinism
        assert result1.bundle_sha == result2.bundle_sha, (
            f"Multimodal determinism violation.\n"
            f"Run 1 SHA: {result1.bundle_sha}\n"
            f"Run 2 SHA: {result2.bundle_sha}"
        )

    def test_vram_budget_respected(self) -> None:
        """Verify VRAM usage stays within budget (≤12GB).

        This is a soft check - we log usage but don't fail if exceeded.
        """
        from app.clarity.medgemma_runner import MedGemmaRunner

        runner = MedGemmaRunner()

        # Run inference to load model
        prompt = "Test prompt"
        runner.generate(prompt, seed=42)

        # Check VRAM
        vram = runner.get_vram_usage()
        max_allocated = vram.get("max_allocated_gb", 0)

        # Log VRAM usage
        print(f"\nVRAM Usage:")
        print(f"  Allocated: {vram.get('allocated_gb', 0):.2f} GB")
        print(f"  Reserved: {vram.get('reserved_gb', 0):.2f} GB")
        print(f"  Max Allocated: {max_allocated:.2f} GB")

        # Soft assertion - warn if over budget but don't fail
        if max_allocated > 12.0:
            import warnings
            warnings.warn(
                f"VRAM usage ({max_allocated:.2f} GB) exceeds 12GB budget",
                UserWarning,
            )


class TestRealAdapterMetadata:
    """Test metadata recording for real adapter runs."""

    def test_metadata_includes_required_fields(self) -> None:
        """Verify metadata includes all required fields for sweep_manifest.json."""
        from app.clarity.medgemma_runner import MedGemmaRunner

        runner = MedGemmaRunner()
        result = runner.generate("Test prompt", seed=42)

        # Check required metadata fields
        assert result.model_id == "google/medgemma-4b"
        assert result.seed == 42
        assert result.bundle_sha is not None
        assert len(result.bundle_sha) == 64  # SHA256 hex

        # Check metadata dict
        metadata = result.metadata
        assert "device" in metadata
        assert "torch_version" in metadata
        assert "transformers_version" in metadata
        assert "temperature" in metadata
        assert metadata["temperature"] == 0.0
        assert metadata["do_sample"] is False


class TestRealAdapterGating:
    """Test environment variable gating behavior."""

    def test_runner_raises_when_disabled(self) -> None:
        """Verify runner raises RuntimeError when CLARITY_REAL_MODEL is not set.

        Note: This test actually runs because we're in the real model context.
        We need to temporarily unset the env var to test this behavior.
        """
        import os

        from app.clarity.medgemma_runner import MedGemmaRunner

        # Save current value
        original = os.environ.get("CLARITY_REAL_MODEL")

        try:
            # Unset the env var
            if "CLARITY_REAL_MODEL" in os.environ:
                del os.environ["CLARITY_REAL_MODEL"]

            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match="Real model execution is disabled"):
                MedGemmaRunner()
        finally:
            # Restore original value
            if original is not None:
                os.environ["CLARITY_REAL_MODEL"] = original
            elif "CLARITY_REAL_MODEL" in os.environ:
                del os.environ["CLARITY_REAL_MODEL"]


class TestMinimalSweepDeterminism:
    """Test determinism across a minimal sweep (M13 acceptance criteria)."""

    def test_minimal_sweep_2_seeds_deterministic(self) -> None:
        """Verify minimal sweep with 2 seeds produces deterministic results.

        This matches M13 scope: 1 image, 2 seeds, 1 perturbation axis.
        """
        from PIL import Image

        from app.clarity.medgemma_runner import MedGemmaRunner

        # Load fixture image
        image_path = FIXTURES_DIR / "clinical_sample_01.png"
        if not image_path.exists():
            pytest.skip(f"Fixture not found: {image_path}")

        image = Image.open(image_path)
        runner = MedGemmaRunner()

        prompt = "Analyze this chest X-ray. Describe any findings."
        seeds = [42, 123]

        # First pass
        results_pass1 = {}
        for seed in seeds:
            result = runner.generate(prompt, seed=seed, image=image)
            results_pass1[seed] = result.bundle_sha

        # Second pass (re-run with same inputs)
        results_pass2 = {}
        for seed in seeds:
            result = runner.generate(prompt, seed=seed, image=image)
            results_pass2[seed] = result.bundle_sha

        # Verify determinism across both passes
        for seed in seeds:
            assert results_pass1[seed] == results_pass2[seed], (
                f"Determinism violation at seed={seed}\n"
                f"Pass 1: {results_pass1[seed]}\n"
                f"Pass 2: {results_pass2[seed]}"
            )

        print(f"\n✓ Minimal sweep determinism verified for seeds: {seeds}")
        print(f"  Seed 42 SHA: {results_pass1[42][:16]}...")
        print(f"  Seed 123 SHA: {results_pass1[123][:16]}...")

