"""Metrics Module for CLARITY.

This module provides core metric data structures and computation helpers for
measuring evidence stability and justification drift across perturbation sweeps.

CRITICAL CONSTRAINTS (M05+M14):
1. All metrics must be deterministic given identical input.
2. No randomness, no datetime.now, no uuid.
3. No numpy — pure Python only.
4. No r2l imports.
5. All floats rounded to 8 decimal places at storage.
6. Unicode-safe string operations.

Metrics defined:
- ESI (Evidence Stability Index): Measures answer consistency under perturbation.
- Justification Drift: Measures justification change via normalized Levenshtein distance.
- (M14) CSI (Confidence Stability Index): Measures confidence consistency under perturbation.
- (M14) EDM (Entropy Drift Metric): Measures entropy change under perturbation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class MetricComputationError(Exception):
    """Raised when metric computation fails.

    This error indicates a failure during metric computation, such as:
    - Empty sweep (zero runs)
    - Missing required fields in trace records
    - Invalid sweep manifest structure
    """

    pass


@dataclass(frozen=True)
class ESIMetric:
    """Evidence Stability Index for a single perturbation axis.

    ESI measures the proportion of runs where the final answer matches
    the baseline answer, aggregated per axis value.

    Attributes:
        axis: The name of the perturbation axis.
        value_scores: Dictionary mapping axis value (encoded) to ESI score.
                     Each score is the proportion of seeds where answer matches baseline.
        overall_score: Mean ESI across all axis values.

    Example:
        >>> esi = ESIMetric(
        ...     axis="brightness",
        ...     value_scores={"0p8": 0.66666667, "1p0": 1.0, "1p2": 0.33333333},
        ...     overall_score=0.66666667,
        ... )
    """

    axis: str
    value_scores: dict[str, float]
    overall_score: float


@dataclass(frozen=True)
class DriftMetric:
    """Justification Drift metric for a single perturbation axis.

    Drift measures the normalized Levenshtein distance between baseline
    justification and each run's justification, aggregated per axis value.

    Attributes:
        axis: The name of the perturbation axis.
        value_scores: Dictionary mapping axis value (encoded) to drift score.
                     Each score is the mean normalized Levenshtein distance.
        overall_score: Mean drift across all axis values.

    Example:
        >>> drift = DriftMetric(
        ...     axis="brightness",
        ...     value_scores={"0p8": 0.15, "1p0": 0.0, "1p2": 0.25},
        ...     overall_score=0.13333333,
        ... )
    """

    axis: str
    value_scores: dict[str, float]
    overall_score: float


@dataclass(frozen=True)
class CSIMetric:
    """Confidence Stability Index for a single perturbation axis (M14).

    CSI measures the stability of confidence scores under perturbation.
    A high CSI indicates consistent confidence regardless of perturbation.

    Computed as 1 - normalized variance of confidence scores across seeds/values.

    Attributes:
        axis: The name of the perturbation axis.
        value_scores: Dictionary mapping axis value (encoded) to CSI score.
                     Each score measures confidence stability for that value.
        overall_score: Mean CSI across all axis values.
        mean_confidence: Mean confidence score across all runs.

    Example:
        >>> csi = CSIMetric(
        ...     axis="brightness",
        ...     value_scores={"0p8": 0.95, "1p0": 1.0, "1p2": 0.92},
        ...     overall_score=0.95666667,
        ...     mean_confidence=0.85,
        ... )
    """

    axis: str
    value_scores: dict[str, float]
    overall_score: float
    mean_confidence: float | None = None


@dataclass(frozen=True)
class EDMMetric:
    """Entropy Drift Metric for a single perturbation axis (M14).

    EDM measures the change in output entropy under perturbation.
    A low EDM indicates consistent uncertainty regardless of perturbation.

    Computed as mean absolute difference from baseline entropy.

    Attributes:
        axis: The name of the perturbation axis.
        value_scores: Dictionary mapping axis value (encoded) to EDM score.
                     Each score measures entropy drift for that value.
        overall_score: Mean EDM across all axis values.
        baseline_entropy: Entropy of the baseline run.

    Example:
        >>> edm = EDMMetric(
        ...     axis="brightness",
        ...     value_scores={"0p8": 0.05, "1p0": 0.0, "1p2": 0.08},
        ...     overall_score=0.04333333,
        ...     baseline_entropy=2.3,
        ... )
    """

    axis: str
    value_scores: dict[str, float]
    overall_score: float
    baseline_entropy: float | None = None


@dataclass(frozen=True)
class MetricsResult:
    """Complete metrics result from a sweep analysis.

    Contains ESI and drift metrics for all perturbation axes.
    Optionally contains CSI and EDM metrics (M14 rich mode).
    Metrics are sorted alphabetically by axis name.

    Attributes:
        esi: Tuple of ESIMetric objects, one per axis, sorted by axis name.
        drift: Tuple of DriftMetric objects, one per axis, sorted by axis name.
        csi: Optional tuple of CSIMetric objects (M14 rich mode only).
        edm: Optional tuple of EDMMetric objects (M14 rich mode only).

    Example:
        >>> result = MetricsResult(
        ...     esi=(ESIMetric(axis="brightness", ...), ESIMetric(axis="contrast", ...)),
        ...     drift=(DriftMetric(axis="brightness", ...), DriftMetric(axis="contrast", ...)),
        ...     csi=(CSIMetric(axis="brightness", ...), CSIMetric(axis="contrast", ...)),
        ...     edm=(EDMMetric(axis="brightness", ...), EDMMetric(axis="contrast", ...)),
        ... )
    """

    esi: tuple[ESIMetric, ...]
    drift: tuple[DriftMetric, ...]
    # M14 rich mode metrics (optional)
    csi: tuple[CSIMetric, ...] | None = None
    edm: tuple[EDMMetric, ...] | None = None


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between two strings.

    Uses dynamic programming to compute the minimum number of single-character
    edits (insertions, deletions, substitutions) required to transform s1 into s2.

    This implementation is character-based (not byte-based), making it Unicode-safe.

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        The Levenshtein distance as a non-negative integer.

    Examples:
        >>> levenshtein_distance("kitten", "sitting")
        3
        >>> levenshtein_distance("", "abc")
        3
        >>> levenshtein_distance("abc", "abc")
        0
        >>> levenshtein_distance("café", "cafe")
        1
    """
    # Edge cases
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    # Create matrix with dimensions (len(s1)+1) x (len(s2)+1)
    # Use single row optimization for memory efficiency
    previous_row = list(range(len(s2) + 1))
    current_row = [0] * (len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row[0] = i + 1

        for j, c2 in enumerate(s2):
            # Cost is 0 if characters match, 1 otherwise
            cost = 0 if c1 == c2 else 1

            current_row[j + 1] = min(
                previous_row[j + 1] + 1,  # Deletion
                current_row[j] + 1,  # Insertion
                previous_row[j] + cost,  # Substitution
            )

        # Swap rows
        previous_row, current_row = current_row, previous_row

    return previous_row[len(s2)]


def normalized_levenshtein(s1: str, s2: str) -> float:
    """Compute normalized Levenshtein distance between two strings.

    The normalized distance is the Levenshtein distance divided by the
    maximum length of the two strings. Returns 0.0 if both strings are empty.

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        Normalized distance in range [0.0, 1.0].
        Returns 0.0 if both strings are empty.

    Examples:
        >>> normalized_levenshtein("abc", "abc")
        0.0
        >>> normalized_levenshtein("", "")
        0.0
        >>> normalized_levenshtein("ab", "cd")
        1.0
    """
    if len(s1) == 0 and len(s2) == 0:
        return 0.0

    max_len = max(len(s1), len(s2))
    distance = levenshtein_distance(s1, s2)

    return distance / max_len


def round_metric(value: float) -> float:
    """Round a metric value to 8 decimal places.

    All stored metric values must be rounded to ensure deterministic output.

    Args:
        value: The float value to round.

    Returns:
        The value rounded to 8 decimal places.

    Example:
        >>> round_metric(0.333333333333)
        0.33333333
    """
    return round(value, 8)


def extract_answer(trace_records: list[dict[str, Any]]) -> str:
    """Extract the answer from a list of trace records.

    Uses the last record and extracts the answer according to M05 rules:
    1. If "output" exists and is a non-empty string → use it
    2. Else if "answer" exists and is a non-empty string → use it
    3. Else → raise MetricComputationError

    Args:
        trace_records: List of trace record dictionaries.

    Returns:
        The extracted answer string.

    Raises:
        MetricComputationError: If no trace records, or no valid answer found.
    """
    if not trace_records:
        raise MetricComputationError("No trace records found")

    last_record = trace_records[-1]

    # Try "output" first
    output = last_record.get("output")
    if isinstance(output, str) and output:
        return output

    # Try "answer" second
    answer = last_record.get("answer")
    if isinstance(answer, str) and answer:
        return answer

    raise MetricComputationError(
        "No valid 'output' or 'answer' field in last trace record"
    )


def extract_justification(trace_records: list[dict[str, Any]]) -> str:
    """Extract the justification from a list of trace records.

    Uses the last record and extracts justification according to M05 rules:
    - If "justification" missing → return ""
    - If present but non-string → coerce with str(...)
    - Do NOT fall back to "output"

    Args:
        trace_records: List of trace record dictionaries.

    Returns:
        The extracted justification string (may be empty).

    Raises:
        MetricComputationError: If no trace records.
    """
    if not trace_records:
        raise MetricComputationError("No trace records found")

    last_record = trace_records[-1]

    justification = last_record.get("justification")

    if justification is None:
        return ""

    if isinstance(justification, str):
        return justification

    # Coerce non-string to string
    return str(justification)


# M14 Rich Metrics Functions


def extract_confidence_score(trace_records: list[dict[str, Any]]) -> float | None:
    """Extract the confidence score from trace records (M14).

    Looks for rich_summary.confidence_score in the last trace record.

    Args:
        trace_records: List of trace record dictionaries.

    Returns:
        Confidence score if present, None otherwise.
    """
    if not trace_records:
        return None

    last_record = trace_records[-1]

    # Try rich_summary.confidence_score
    rich_summary = last_record.get("rich_summary")
    if rich_summary and isinstance(rich_summary, dict):
        confidence = rich_summary.get("confidence_score")
        if isinstance(confidence, (int, float)):
            return round_metric(float(confidence))

    # Try top-level confidence_score
    confidence = last_record.get("confidence_score")
    if isinstance(confidence, (int, float)):
        return round_metric(float(confidence))

    return None


def extract_output_entropy(trace_records: list[dict[str, Any]]) -> float | None:
    """Extract the output entropy from trace records (M14).

    Looks for rich_summary.output_entropy in the last trace record.

    Args:
        trace_records: List of trace record dictionaries.

    Returns:
        Output entropy if present, None otherwise.
    """
    if not trace_records:
        return None

    last_record = trace_records[-1]

    # Try rich_summary.output_entropy
    rich_summary = last_record.get("rich_summary")
    if rich_summary and isinstance(rich_summary, dict):
        entropy = rich_summary.get("output_entropy")
        if isinstance(entropy, (int, float)):
            return round_metric(float(entropy))

    # Try top-level output_entropy
    entropy = last_record.get("output_entropy")
    if isinstance(entropy, (int, float)):
        return round_metric(float(entropy))

    return None


def compute_csi_from_confidences(confidences: list[float]) -> float:
    """Compute Confidence Stability Index from a list of confidence scores.

    CSI = 1 - normalized_variance
    Where normalized_variance = variance / max_possible_variance

    For values in [0, 1], max variance is 0.25 (when half are 0 and half are 1).

    Args:
        confidences: List of confidence scores in [0, 1] range.

    Returns:
        CSI score in [0, 1] range. Higher = more stable.
        Returns 1.0 if variance is 0 or list has < 2 elements.
    """
    if len(confidences) < 2:
        return 1.0  # Perfect stability with single point

    mean_conf = sum(confidences) / len(confidences)
    variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)

    # Normalize by max possible variance for [0, 1] range
    max_variance = 0.25
    normalized_variance = variance / max_variance

    # CSI = 1 - normalized variance
    csi = 1.0 - min(1.0, normalized_variance)
    return round_metric(csi)


def compute_edm_from_entropies(
    baseline_entropy: float | None,
    entropies: list[float | None],
) -> float:
    """Compute Entropy Drift Metric from baseline and list of entropies.

    EDM = mean absolute difference from baseline entropy.

    Args:
        baseline_entropy: Entropy of the baseline run.
        entropies: List of entropies from perturbed runs.

    Returns:
        EDM score (lower = more stable).
        Returns 0.0 if baseline is None or all entropies are None.
    """
    if baseline_entropy is None:
        return 0.0

    valid_entropies = [e for e in entropies if e is not None]
    if not valid_entropies:
        return 0.0

    total_drift = sum(abs(e - baseline_entropy) for e in valid_entropies)
    mean_drift = total_drift / len(valid_entropies)

    return round_metric(mean_drift)

