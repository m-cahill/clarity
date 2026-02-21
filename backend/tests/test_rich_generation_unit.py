"""Unit Tests for Rich Generation Module (M14).

These tests verify the pure computation functions in rich_generation.py
and metrics.py related to M14 rich mode.

These tests do NOT require GPU or real model - they test pure Python functions.
They SHOULD run in CI as part of the synthetic path.
"""

from __future__ import annotations

import math


class TestComputeEntropy:
    """Unit tests for compute_entropy function."""

    def test_empty_list_returns_zero(self) -> None:
        """Verify compute_entropy handles empty list."""
        from app.clarity.rich_generation import compute_entropy

        assert compute_entropy([]) == 0.0

    def test_uniform_distribution(self) -> None:
        """Verify compute_entropy for uniform distribution."""
        from app.clarity.rich_generation import compute_entropy

        # Uniform distribution over 4 items: entropy = ln(4)
        probs = [0.25, 0.25, 0.25, 0.25]
        expected = math.log(4)  # ~1.386

        result = compute_entropy(probs)
        assert abs(result - expected) < 1e-6, f"Expected ~{expected}, got {result}"

    def test_certain_distribution(self) -> None:
        """Verify compute_entropy for certain (zero entropy) distribution."""
        from app.clarity.rich_generation import compute_entropy

        # All probability on one item: entropy = 0
        probs = [1.0, 0.0, 0.0, 0.0]

        result = compute_entropy(probs)
        assert result == 0.0, f"Expected 0.0, got {result}"

    def test_binary_distribution(self) -> None:
        """Verify compute_entropy for binary distribution."""
        from app.clarity.rich_generation import compute_entropy

        # 50/50: entropy = ln(2)
        probs = [0.5, 0.5]
        expected = math.log(2)

        result = compute_entropy(probs)
        assert abs(result - expected) < 1e-6


class TestComputeMeanLogprob:
    """Unit tests for compute_mean_logprob function."""

    def test_empty_list_returns_zero(self) -> None:
        """Verify compute_mean_logprob handles empty list."""
        from app.clarity.rich_generation import compute_mean_logprob

        assert compute_mean_logprob([]) == 0.0

    def test_basic_mean(self) -> None:
        """Verify compute_mean_logprob computes mean correctly."""
        from app.clarity.rich_generation import compute_mean_logprob

        logprobs = [-1.0, -2.0, -3.0]
        expected = -2.0

        result = compute_mean_logprob(logprobs)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_single_value(self) -> None:
        """Verify compute_mean_logprob with single value."""
        from app.clarity.rich_generation import compute_mean_logprob

        result = compute_mean_logprob([-0.5])
        assert result == -0.5


class TestComputeConfidenceScore:
    """Unit tests for compute_confidence_score function."""

    def test_zero_logprob_gives_one(self) -> None:
        """Verify compute_confidence_score for zero logprob (perfect confidence)."""
        from app.clarity.rich_generation import compute_confidence_score

        # exp(0) = 1.0
        result = compute_confidence_score(0.0)
        assert result == 1.0, f"Expected 1.0, got {result}"

    def test_negative_logprob(self) -> None:
        """Verify compute_confidence_score for negative logprob."""
        from app.clarity.rich_generation import compute_confidence_score

        # exp(-1) ≈ 0.368
        result = compute_confidence_score(-1.0)
        expected = round(math.exp(-1.0), 8)
        assert result == expected, f"Expected {expected}, got {result}"

    def test_very_negative_logprob(self) -> None:
        """Verify compute_confidence_score clamps to [0, 1]."""
        from app.clarity.rich_generation import compute_confidence_score

        # exp(-100) ≈ 0
        result = compute_confidence_score(-100.0)
        assert 0.0 <= result <= 1.0


class TestComputeSummaryHash:
    """Unit tests for compute_summary_hash function."""

    def test_determinism(self) -> None:
        """Verify compute_summary_hash is deterministic."""
        from app.clarity.rich_generation import compute_summary_hash

        hash1 = compute_summary_hash(
            mean_logprob=-0.5,
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=100,
        )

        hash2 = compute_summary_hash(
            mean_logprob=-0.5,
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=100,
        )

        assert hash1 == hash2, f"Summary hash not deterministic: {hash1} vs {hash2}"

    def test_different_inputs_produce_different_hashes(self) -> None:
        """Verify compute_summary_hash differs for different inputs."""
        from app.clarity.rich_generation import compute_summary_hash

        hash1 = compute_summary_hash(
            mean_logprob=-0.5,
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=100,
        )

        hash2 = compute_summary_hash(
            mean_logprob=-0.6,  # Different
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=100,
        )

        assert hash1 != hash2, "Summary hash should differ for different inputs"

    def test_handles_none_values(self) -> None:
        """Verify compute_summary_hash handles None values."""
        from app.clarity.rich_generation import compute_summary_hash

        hash1 = compute_summary_hash(
            mean_logprob=None,
            output_entropy=None,
            confidence_score=None,
            token_count=None,
        )

        # Should not raise, and should be deterministic
        hash2 = compute_summary_hash(
            mean_logprob=None,
            output_entropy=None,
            confidence_score=None,
            token_count=None,
        )

        assert hash1 == hash2

    def test_hash_is_sha256(self) -> None:
        """Verify compute_summary_hash returns SHA256 (64 hex chars)."""
        from app.clarity.rich_generation import compute_summary_hash

        hash_value = compute_summary_hash(
            mean_logprob=-0.5,
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=100,
        )

        assert len(hash_value) == 64, f"Expected 64 chars, got {len(hash_value)}"
        assert all(c in "0123456789abcdef" for c in hash_value), "Not valid hex"


class TestComputeLogitsHashStreaming:
    """Unit tests for compute_logits_hash_streaming function."""

    def test_determinism(self) -> None:
        """Verify compute_logits_hash_streaming is deterministic."""
        from app.clarity.rich_generation import compute_logits_hash_streaming

        values = [0.1, 0.2, 0.3, 0.4, 0.5]

        hash1 = compute_logits_hash_streaming(iter(values))
        hash2 = compute_logits_hash_streaming(iter(values))

        assert hash1 == hash2

    def test_different_values_produce_different_hashes(self) -> None:
        """Verify compute_logits_hash_streaming differs for different inputs."""
        from app.clarity.rich_generation import compute_logits_hash_streaming

        hash1 = compute_logits_hash_streaming(iter([0.1, 0.2, 0.3]))
        hash2 = compute_logits_hash_streaming(iter([0.1, 0.2, 0.4]))

        assert hash1 != hash2

    def test_empty_iterator(self) -> None:
        """Verify compute_logits_hash_streaming handles empty iterator."""
        from app.clarity.rich_generation import compute_logits_hash_streaming

        hash_value = compute_logits_hash_streaming(iter([]))

        # Should not raise, and should be deterministic
        hash_value2 = compute_logits_hash_streaming(iter([]))
        assert hash_value == hash_value2


class TestCreateRichMetricsSummary:
    """Unit tests for create_rich_metrics_summary function."""

    def test_none_input_returns_none_fields(self) -> None:
        """Verify create_rich_metrics_summary handles None input."""
        from app.clarity.rich_generation import create_rich_metrics_summary

        summary = create_rich_metrics_summary(token_logprobs=None)

        assert summary.mean_logprob is None
        assert summary.confidence_score is None
        assert summary.token_count is None
        assert summary.summary_hash is None

    def test_creates_summary_from_logprobs(self) -> None:
        """Verify create_rich_metrics_summary computes summary correctly."""
        from app.clarity.rich_generation import create_rich_metrics_summary

        token_logprobs = [-0.1, -0.2, -0.3]

        summary = create_rich_metrics_summary(token_logprobs=token_logprobs)

        assert summary.mean_logprob is not None
        assert summary.confidence_score is not None
        assert summary.token_count == 3
        assert summary.summary_hash is not None

    def test_summary_hash_determinism(self) -> None:
        """Verify create_rich_metrics_summary produces deterministic hash."""
        from app.clarity.rich_generation import create_rich_metrics_summary

        token_logprobs = [-0.5, -0.6, -0.7]

        summary1 = create_rich_metrics_summary(token_logprobs=token_logprobs)
        summary2 = create_rich_metrics_summary(token_logprobs=token_logprobs)

        assert summary1.summary_hash == summary2.summary_hash


class TestCSIFromConfidences:
    """Unit tests for compute_csi_from_confidences function."""

    def test_single_value_returns_one(self) -> None:
        """Verify CSI returns 1.0 for single value (perfect stability)."""
        from app.clarity.metrics import compute_csi_from_confidences

        result = compute_csi_from_confidences([0.85])
        assert result == 1.0

    def test_identical_values_returns_one(self) -> None:
        """Verify CSI returns 1.0 for identical values."""
        from app.clarity.metrics import compute_csi_from_confidences

        result = compute_csi_from_confidences([0.8, 0.8, 0.8])
        assert result == 1.0

    def test_max_variance_returns_zero(self) -> None:
        """Verify CSI returns 0.0 for maximum variance."""
        from app.clarity.metrics import compute_csi_from_confidences

        # Half 0, half 1 gives variance = 0.25 (max for [0,1] range)
        result = compute_csi_from_confidences([0.0, 1.0])
        assert result == 0.0

    def test_partial_variance(self) -> None:
        """Verify CSI handles partial variance correctly."""
        from app.clarity.metrics import compute_csi_from_confidences

        # Values with some variance
        result = compute_csi_from_confidences([0.7, 0.8, 0.9])
        assert 0.0 < result < 1.0


class TestEDMFromEntropies:
    """Unit tests for compute_edm_from_entropies function."""

    def test_no_drift_returns_zero(self) -> None:
        """Verify EDM returns 0.0 when all entropies match baseline."""
        from app.clarity.metrics import compute_edm_from_entropies

        result = compute_edm_from_entropies(2.3, [2.3, 2.3, 2.3])
        assert result == 0.0

    def test_with_drift(self) -> None:
        """Verify EDM computes mean absolute difference correctly."""
        from app.clarity.metrics import compute_edm_from_entropies

        # Baseline = 2.0, entropies = [2.5, 1.5, 2.0]
        # Diffs = [0.5, 0.5, 0.0], mean = 0.333...
        result = compute_edm_from_entropies(2.0, [2.5, 1.5, 2.0])
        expected = round((0.5 + 0.5 + 0.0) / 3, 8)
        assert result == expected

    def test_none_baseline_returns_zero(self) -> None:
        """Verify EDM returns 0.0 when baseline is None."""
        from app.clarity.metrics import compute_edm_from_entropies

        result = compute_edm_from_entropies(None, [2.3, 2.4])
        assert result == 0.0

    def test_none_entropies_returns_zero(self) -> None:
        """Verify EDM returns 0.0 when all entropies are None."""
        from app.clarity.metrics import compute_edm_from_entropies

        result = compute_edm_from_entropies(2.0, [None, None])
        assert result == 0.0


class TestRichGenerationResultDataclass:
    """Unit tests for RichGenerationResult dataclass."""

    def test_to_dict_includes_required_fields(self) -> None:
        """Verify to_dict includes all required fields."""
        from app.clarity.rich_generation import RichGenerationResult

        result = RichGenerationResult(
            text="test output",
            model_id="test-model",
            seed=42,
            bundle_sha="abc123",
            metadata={"key": "value"},
        )

        result_dict = result.to_dict()

        assert "text" in result_dict
        assert "model_id" in result_dict
        assert "seed" in result_dict
        assert "bundle_sha" in result_dict
        assert "metadata" in result_dict

    def test_to_dict_excludes_none_rich_fields(self) -> None:
        """Verify to_dict excludes None optional fields."""
        from app.clarity.rich_generation import RichGenerationResult

        result = RichGenerationResult(
            text="test",
            model_id="test-model",
            seed=42,
            bundle_sha="abc123",
            metadata={},
            # All optional fields default to None
        )

        result_dict = result.to_dict()

        assert "logits_hash" not in result_dict
        assert "rich_summary" not in result_dict
        assert "token_logprobs" not in result_dict

    def test_to_dict_includes_rich_fields_when_present(self) -> None:
        """Verify to_dict includes optional fields when present."""
        from app.clarity.rich_generation import (
            RichGenerationResult,
            RichMetricsSummary,
        )

        summary = RichMetricsSummary(
            mean_logprob=-0.5,
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=10,
            summary_hash="def456",
        )

        result = RichGenerationResult(
            text="test",
            model_id="test-model",
            seed=42,
            bundle_sha="abc123",
            metadata={},
            token_logprobs=(-0.1, -0.2),
            rich_summary=summary,
            logits_hash="ghi789",
        )

        result_dict = result.to_dict()

        assert "logits_hash" in result_dict
        assert "rich_summary" in result_dict
        assert "token_logprobs" in result_dict


class TestRichMetricsSummaryDataclass:
    """Unit tests for RichMetricsSummary dataclass."""

    def test_to_dict_has_sorted_keys(self) -> None:
        """Verify to_dict returns keys in alphabetical order."""
        from app.clarity.rich_generation import RichMetricsSummary

        summary = RichMetricsSummary(
            mean_logprob=-0.5,
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=10,
            summary_hash="abc123",
        )

        result_dict = summary.to_dict()
        keys = list(result_dict.keys())
        sorted_keys = sorted(keys)

        assert keys == sorted_keys, f"Keys not sorted: {keys}"

    def test_frozen_dataclass(self) -> None:
        """Verify RichMetricsSummary is frozen (immutable)."""
        from app.clarity.rich_generation import RichMetricsSummary

        summary = RichMetricsSummary(
            mean_logprob=-0.5,
            output_entropy=2.3,
            confidence_score=0.85,
            token_count=10,
            summary_hash="abc123",
        )

        # Should raise FrozenInstanceError
        import pytest
        with pytest.raises(Exception):  # FrozenInstanceError
            summary.mean_logprob = -0.6  # type: ignore


class TestSurfaceDataclasses:
    """Unit tests for M14 surface dataclasses."""

    def test_confidence_surface_point_to_dict(self) -> None:
        """Verify ConfidenceSurfacePoint.to_dict() has sorted keys."""
        from app.clarity.surfaces import ConfidenceSurfacePoint

        point = ConfidenceSurfacePoint(
            axis="brightness",
            value="0p8",
            mean_confidence=0.85,
            csi=0.95,
            confidence_variance=0.0025,
        )

        result = point.to_dict()
        keys = list(result.keys())
        sorted_keys = sorted(keys)

        assert keys == sorted_keys

    def test_entropy_surface_point_to_dict(self) -> None:
        """Verify EntropySurfacePoint.to_dict() has sorted keys."""
        from app.clarity.surfaces import EntropySurfacePoint

        point = EntropySurfacePoint(
            axis="brightness",
            value="0p8",
            mean_entropy=2.3,
            edm=0.05,
            entropy_variance=0.01,
        )

        result = point.to_dict()
        keys = list(result.keys())
        sorted_keys = sorted(keys)

        assert keys == sorted_keys

    def test_rich_surfaces_to_dict(self) -> None:
        """Verify RichSurfaces.to_dict() has sorted keys."""
        from app.clarity.surfaces import (
            ConfidenceSurface,
            ConfidenceSurfacePoint,
            EntropySurface,
            EntropySurfacePoint,
            RichSurfaces,
        )

        conf_point = ConfidenceSurfacePoint(
            axis="brightness",
            value="1p0",
            mean_confidence=0.9,
            csi=0.98,
            confidence_variance=0.001,
        )

        ent_point = EntropySurfacePoint(
            axis="brightness",
            value="1p0",
            mean_entropy=2.0,
            edm=0.02,
            entropy_variance=0.005,
        )

        conf_surface = ConfidenceSurface(
            axis="brightness",
            points=(conf_point,),
            mean_csi=0.98,
            overall_mean_confidence=0.9,
            overall_variance=0.001,
        )

        ent_surface = EntropySurface(
            axis="brightness",
            points=(ent_point,),
            mean_edm=0.02,
            overall_mean_entropy=2.0,
            overall_variance=0.005,
        )

        rich = RichSurfaces(
            confidence_surfaces=(conf_surface,),
            entropy_surfaces=(ent_surface,),
            global_mean_csi=0.98,
            global_mean_edm=0.02,
        )

        result = rich.to_dict()
        keys = list(result.keys())
        sorted_keys = sorted(keys)

        assert keys == sorted_keys

