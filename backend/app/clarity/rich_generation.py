"""Rich Generation Module for CLARITY.

This module provides data structures for representing rich inference outputs
that include token-level probabilities, confidence scores, and entropy metrics.

CRITICAL CONSTRAINTS (M14):
1. All structures must be deterministic given identical input.
2. No randomness, no datetime.now, no uuid.
3. Frozen dataclasses only.
4. All floats rounded to 8 decimal places at storage.
5. Deterministic to_dict() with sorted keys.
6. All fields are OPTIONAL - no breaking changes to existing schemas.
7. Rich mode is opt-in via CLARITY_RICH_MODE environment variable.

Structures defined:
- RichGenerationResult: Extended generation result with logprobs and entropy.
- RichMetricsSummary: Summary metrics for determinism verification.
"""

from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass
from typing import Any


# Environment variable gates
RICH_MODE_ENV_VAR = "CLARITY_RICH_MODE"
RICH_LOGITS_HASH_ENV_VAR = "CLARITY_RICH_LOGITS_HASH"


def is_rich_mode_enabled() -> bool:
    """Check if rich mode is enabled.

    Rich mode requires BOTH CLARITY_REAL_MODEL=true AND CLARITY_RICH_MODE=true.

    Returns:
        True if CLARITY_RICH_MODE environment variable is set to a truthy value.
    """
    value = os.getenv(RICH_MODE_ENV_VAR, "").lower()
    return value in ("true", "1", "yes", "on")


def is_rich_logits_hash_enabled() -> bool:
    """Check if full logits hashing is enabled.

    Full logits hashing requires all three flags:
    - CLARITY_REAL_MODEL=true
    - CLARITY_RICH_MODE=true
    - CLARITY_RICH_LOGITS_HASH=true

    Returns:
        True if CLARITY_RICH_LOGITS_HASH is set to a truthy value.
    """
    value = os.getenv(RICH_LOGITS_HASH_ENV_VAR, "").lower()
    return value in ("true", "1", "yes", "on")


def _round8(value: float) -> float:
    """Round a value to 8 decimal places.

    Args:
        value: The float value to round.

    Returns:
        The value rounded to 8 decimal places.
    """
    return round(value, 8)


def _stable_float_repr(value: float) -> str:
    """Convert float to stable string representation for hashing.

    Uses fixed precision to ensure consistent hashing across runs.
    Handles special values (inf, -inf, nan) explicitly.

    Args:
        value: The float value to convert.

    Returns:
        A stable string representation.
    """
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "inf" if value > 0 else "-inf"
    # Use %.8e format for scientific notation with 8 decimal places
    return f"{value:.8e}"


@dataclass(frozen=True)
class RichMetricsSummary:
    """Summary metrics from rich generation for determinism verification.

    These summary metrics are computed from the full logits and can be
    hashed for determinism verification without storing the full tensor.

    Attributes:
        mean_logprob: Mean log probability across all generated tokens.
                     More negative = less confident. None if not computed.
        output_entropy: Shannon entropy of the output token distribution.
                       Higher = more uncertainty. None if not computed.
        confidence_score: Normalized confidence score in [0, 1].
                         Higher = more confident. None if not computed.
        token_count: Number of tokens generated. None if not computed.
        summary_hash: SHA256 hash of summary metrics for determinism verification.

    Example:
        >>> summary = RichMetricsSummary(
        ...     mean_logprob=-0.5,
        ...     output_entropy=2.3,
        ...     confidence_score=0.85,
        ...     token_count=128,
        ...     summary_hash="abc123...",
        ... )
    """

    mean_logprob: float | None
    output_entropy: float | None
    confidence_score: float | None
    token_count: int | None
    summary_hash: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.
        None values are included explicitly for schema compatibility.

        Returns:
            Dictionary with alphabetically sorted keys.
        """
        return {
            "confidence_score": self.confidence_score,
            "mean_logprob": self.mean_logprob,
            "output_entropy": self.output_entropy,
            "summary_hash": self.summary_hash,
            "token_count": self.token_count,
        }


@dataclass(frozen=True)
class RichGenerationResult:
    """Extended generation result with rich inference signals.

    This dataclass extends the basic MedGemmaResult with additional
    signals extracted from the model's logits, including per-token
    probabilities, confidence scores, and entropy metrics.

    All fields are OPTIONAL to maintain backward compatibility with
    existing artifact schemas.

    Attributes:
        text: The generated text response.
        model_id: The model identifier used.
        seed: The seed used for generation.
        bundle_sha: SHA256 hash of the basic result (text + model_id + seed).
        metadata: Additional metadata about the run.
        token_logprobs: Per-token log probabilities. None if not computed.
        rich_summary: Summary metrics for determinism verification. None if not computed.
        logits_hash: SHA256 hash of full logits tensor. None unless opt-in enabled.

    Example:
        >>> result = RichGenerationResult(
        ...     text="This is a chest X-ray showing...",
        ...     model_id="google/medgemma-4b-it",
        ...     seed=42,
        ...     bundle_sha="abc123...",
        ...     metadata={"device": "cuda"},
        ...     token_logprobs=[-0.1, -0.5, -0.2],
        ...     rich_summary=RichMetricsSummary(...),
        ...     logits_hash="def456...",
        ... )
    """

    # Required fields (same as MedGemmaResult)
    text: str
    model_id: str
    seed: int
    bundle_sha: str
    metadata: dict[str, Any]

    # Optional rich fields (M14)
    token_logprobs: tuple[float, ...] | None = None
    rich_summary: RichMetricsSummary | None = None
    logits_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns a deterministic dictionary with sorted keys.
        Optional fields are included only if not None (schema backward compat).

        Returns:
            Dictionary with alphabetically sorted keys.
        """
        result: dict[str, Any] = {
            "bundle_sha": self.bundle_sha,
            "metadata": self.metadata,
            "model_id": self.model_id,
            "seed": self.seed,
            "text": self.text,
        }

        # Add optional rich fields only if present
        if self.logits_hash is not None:
            result["logits_hash"] = self.logits_hash

        if self.rich_summary is not None:
            result["rich_summary"] = self.rich_summary.to_dict()

        if self.token_logprobs is not None:
            result["token_logprobs"] = list(self.token_logprobs)

        return result


def compute_summary_hash(
    mean_logprob: float | None,
    output_entropy: float | None,
    confidence_score: float | None,
    token_count: int | None,
) -> str:
    """Compute deterministic hash of summary metrics.

    This hash is used for determinism verification - same inputs
    must produce identical hash across runs.

    Args:
        mean_logprob: Mean log probability.
        output_entropy: Output entropy.
        confidence_score: Confidence score.
        token_count: Token count.

    Returns:
        SHA256 hex digest of the summary metrics.
    """
    # Build stable string representation
    parts = [
        f"mean_logprob={_stable_float_repr(mean_logprob) if mean_logprob is not None else 'None'}",
        f"output_entropy={_stable_float_repr(output_entropy) if output_entropy is not None else 'None'}",
        f"confidence_score={_stable_float_repr(confidence_score) if confidence_score is not None else 'None'}",
        f"token_count={token_count if token_count is not None else 'None'}",
    ]
    content = "|".join(parts)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_logits_hash_streaming(logits_iterator: Any) -> str:
    """Compute hash of logits tensor without storing it.

    This function streams through the logits and computes a hash
    in constant memory, avoiding storage of the full tensor.

    Args:
        logits_iterator: An iterator yielding logit values.
                        Can be a flattened tensor iterator.

    Returns:
        SHA256 hex digest of the logits.
    """
    hasher = hashlib.sha256()

    for value in logits_iterator:
        # Convert to stable float representation
        repr_str = _stable_float_repr(float(value))
        hasher.update(repr_str.encode("utf-8"))
        hasher.update(b"|")  # Delimiter

    return hasher.hexdigest()


def compute_entropy(probs: list[float]) -> float:
    """Compute Shannon entropy from probability distribution.

    Uses natural log (base e) for entropy calculation.

    Args:
        probs: List of probabilities (must sum to ~1.0).

    Returns:
        Shannon entropy value. Returns 0.0 for empty input.
    """
    if not probs:
        return 0.0

    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * math.log(p)

    return _round8(entropy)


def compute_mean_logprob(logprobs: list[float]) -> float:
    """Compute mean log probability.

    Args:
        logprobs: List of log probabilities.

    Returns:
        Mean log probability. Returns 0.0 for empty input.
    """
    if not logprobs:
        return 0.0

    return _round8(sum(logprobs) / len(logprobs))


def compute_confidence_score(mean_logprob: float) -> float:
    """Compute normalized confidence score from mean logprob.

    Maps mean log probability to [0, 1] range using exponential.
    exp(mean_logprob) gives geometric mean of probabilities.

    Args:
        mean_logprob: Mean log probability (typically negative).

    Returns:
        Confidence score in [0, 1] range.
    """
    # exp(logprob) = probability
    # Clamp to [0, 1] range
    confidence = math.exp(mean_logprob)
    return _round8(min(1.0, max(0.0, confidence)))


def create_rich_metrics_summary(
    token_logprobs: list[float] | None,
    output_probs: list[float] | None = None,
) -> RichMetricsSummary:
    """Create a RichMetricsSummary from raw metrics.

    Args:
        token_logprobs: Per-token log probabilities.
        output_probs: Output probability distribution (for entropy).
                     If None, entropy will be None.

    Returns:
        RichMetricsSummary with computed values.
    """
    if token_logprobs is None:
        return RichMetricsSummary(
            mean_logprob=None,
            output_entropy=None,
            confidence_score=None,
            token_count=None,
            summary_hash=None,
        )

    mean_logprob = compute_mean_logprob(token_logprobs)
    confidence_score = compute_confidence_score(mean_logprob)
    token_count = len(token_logprobs)

    # Compute entropy if output probs provided
    output_entropy = compute_entropy(output_probs) if output_probs else None

    # Compute summary hash
    summary_hash = compute_summary_hash(
        mean_logprob=mean_logprob,
        output_entropy=output_entropy,
        confidence_score=confidence_score,
        token_count=token_count,
    )

    return RichMetricsSummary(
        mean_logprob=mean_logprob,
        output_entropy=output_entropy,
        confidence_score=confidence_score,
        token_count=token_count,
        summary_hash=summary_hash,
    )

