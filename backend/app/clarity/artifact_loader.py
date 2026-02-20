"""Artifact Loader for CLARITY.

This module provides functions for loading, validating, and hashing R2L
artifacts. CLARITY consumes R2L output as declared artifacts without
importing R2L internals.

CRITICAL CONSTRAINTS (M03):
1. All artifact loading is file-based (no R2L imports).
2. Validation is minimal (required fields only).
3. Hashing is file-content based (SHA256 of bytes).
4. No dependency on R2L object models.

Artifacts consumed:
- manifest.json: Run metadata with required fields
- trace_pack.jsonl: Inference trace records
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ManifestValidationError(ValueError):
    """Raised when manifest.json validation fails.

    This error indicates that the manifest is missing required fields
    or has an invalid structure.
    """

    pass


class TracePackValidationError(ValueError):
    """Raised when trace_pack.jsonl validation fails.

    This error indicates that a trace record is invalid JSON or
    missing required fields.
    """

    pass


# Required fields in manifest.json (per M03 locked answers)
MANIFEST_REQUIRED_FIELDS: frozenset[str] = frozenset({
    "run_id",
    "timestamp",
    "seed",
    "artifacts",
})


def load_manifest(path: Path) -> dict[str, Any]:
    """Load and validate a manifest.json file.

    This function loads the manifest JSON and validates that all required
    fields are present. Additional fields are permitted without error.

    Required fields (per M03 specification):
    - run_id: Unique identifier for the run
    - timestamp: ISO timestamp of the run
    - seed: Seed used for reproducibility
    - artifacts: List of artifact filenames

    Args:
        path: Path to the manifest.json file.

    Returns:
        The parsed manifest as a dictionary.

    Raises:
        FileNotFoundError: If the manifest file does not exist.
        ManifestValidationError: If the file is not valid JSON or
            required fields are missing.

    Example:
        >>> manifest = load_manifest(Path("output/manifest.json"))
        >>> print(manifest["run_id"])
    """
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ManifestValidationError(
            f"Invalid JSON in manifest: {path}: {e}"
        ) from e

    if not isinstance(data, dict):
        raise ManifestValidationError(
            f"Manifest must be a JSON object, got {type(data).__name__}: {path}"
        )

    # Validate required fields
    missing_fields = MANIFEST_REQUIRED_FIELDS - set(data.keys())
    if missing_fields:
        raise ManifestValidationError(
            f"Manifest missing required fields {sorted(missing_fields)}: {path}"
        )

    return data


def load_trace_pack(path: Path) -> list[dict[str, Any]]:
    """Load and validate a trace_pack.jsonl file.

    This function loads the JSONL file and validates that:
    - Each line is valid JSON
    - Each record is a JSON object
    - Each record contains either 'step' or 'step_id' field

    Args:
        path: Path to the trace_pack.jsonl file.

    Returns:
        A list of trace records (dictionaries).

    Raises:
        FileNotFoundError: If the trace pack file does not exist.
        TracePackValidationError: If any line is invalid JSON or
            missing required fields.

    Example:
        >>> traces = load_trace_pack(Path("output/trace_pack.jsonl"))
        >>> for trace in traces:
        ...     print(trace.get("step") or trace.get("step_id"))
    """
    if not path.exists():
        raise FileNotFoundError(f"Trace pack not found: {path}")

    records: list[dict[str, Any]] = []

    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                # Skip empty lines
                continue

            # Parse JSON
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                raise TracePackValidationError(
                    f"Invalid JSON on line {line_num}: {path}: {e}"
                ) from e

            # Validate record is an object
            if not isinstance(record, dict):
                raise TracePackValidationError(
                    f"Trace record must be a JSON object on line {line_num}, "
                    f"got {type(record).__name__}: {path}"
                )

            # Validate step field (either 'step' or 'step_id')
            has_step = "step" in record
            has_step_id = "step_id" in record
            if not has_step and not has_step_id:
                raise TracePackValidationError(
                    f"Trace record missing 'step' or 'step_id' on line {line_num}: {path}"
                )

            records.append(record)

    return records


def hash_artifact(path: Path) -> str:
    """Compute SHA256 hash of an artifact file.

    This function computes a deterministic hash of the file contents.
    The hash is computed from raw bytes, not parsed content, ensuring
    byte-identical files produce identical hashes.

    Args:
        path: Path to the artifact file.

    Returns:
        The SHA256 hex digest of the file contents.

    Raises:
        FileNotFoundError: If the file does not exist.

    Example:
        >>> hash1 = hash_artifact(Path("output/manifest.json"))
        >>> hash2 = hash_artifact(Path("output/manifest.json"))
        >>> assert hash1 == hash2  # Deterministic
    """
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    hasher = hashlib.sha256()

    # Read file in chunks for memory efficiency
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def validate_manifest_schema(manifest: dict[str, Any]) -> bool:
    """Check if a manifest dictionary has all required fields.

    This is a convenience function for validating pre-loaded manifests.

    Args:
        manifest: The manifest dictionary to validate.

    Returns:
        True if all required fields are present, False otherwise.
    """
    return MANIFEST_REQUIRED_FIELDS.issubset(manifest.keys())


def validate_trace_record(record: dict[str, Any]) -> bool:
    """Check if a trace record has required fields.

    This is a convenience function for validating individual records.

    Args:
        record: The trace record dictionary to validate.

    Returns:
        True if the record has 'step' or 'step_id', False otherwise.
    """
    return "step" in record or "step_id" in record

