"""Metrics Module for CLARITY.

This module provides core metric data structures and computation helpers for
measuring evidence stability and justification drift across perturbation sweeps.

CRITICAL CONSTRAINTS (M05):
1. All metrics must be deterministic given identical input.
2. No randomness, no datetime.now, no uuid.
3. No numpy — pure Python only.
4. No r2l imports.
5. All floats rounded to 8 decimal places at storage.
6. Unicode-safe string operations.

Metrics defined:
- ESI (Evidence Stability Index): Measures answer consistency under perturbation.
- Justification Drift: Measures justification change via normalized Levenshtein distance.
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
class MetricsResult:
    """Complete metrics result from a sweep analysis.

    Contains ESI and drift metrics for all perturbation axes.
    Metrics are sorted alphabetically by axis name.

    Attributes:
        esi: Tuple of ESIMetric objects, one per axis, sorted by axis name.
        drift: Tuple of DriftMetric objects, one per axis, sorted by axis name.

    Example:
        >>> result = MetricsResult(
        ...     esi=(ESIMetric(axis="brightness", ...), ESIMetric(axis="contrast", ...)),
        ...     drift=(DriftMetric(axis="brightness", ...), DriftMetric(axis="contrast", ...)),
        ... )
    """

    esi: tuple[ESIMetric, ...]
    drift: tuple[DriftMetric, ...]


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

