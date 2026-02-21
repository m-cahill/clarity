"""Cache Key Generation for CLARITY.

M12: Deterministic cache key computation for artifact caching.

CRITICAL CONSTRAINTS:
1. Keys must be deterministic - identical inputs produce identical keys.
2. JSON serialization must use sorted keys.
3. Float values must be quantized to 8 decimal places.
4. The same hash algorithm (SHA256) as the report module.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _quantize_floats(obj: Any, decimals: int = 8) -> Any:
    """Recursively quantize float values in a data structure.

    Args:
        obj: The data structure to quantize.
        decimals: Number of decimal places to round to.

    Returns:
        The data structure with quantized floats.
    """
    if isinstance(obj, float):
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return {k: _quantize_floats(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_quantize_floats(item, decimals) for item in obj]
    return obj


def _canonical_json(data: dict[str, Any]) -> str:
    """Convert a dictionary to canonical JSON string.

    Ensures deterministic serialization:
    - Keys are sorted
    - No extra whitespace
    - Floats are quantized to 8 decimals

    Args:
        data: The dictionary to serialize.

    Returns:
        Canonical JSON string.
    """
    quantized = _quantize_floats(data)
    return json.dumps(quantized, sort_keys=True, separators=(",", ":"))


def compute_hash(data: str | bytes) -> str:
    """Compute SHA256 hash of data.

    Args:
        data: String or bytes to hash.

    Returns:
        Hex-encoded SHA256 hash.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def compute_case_hash(case_dir: Path) -> str:
    """Compute a deterministic hash for a case directory.

    The hash is computed from:
    - manifest.json
    - metrics.json
    - overlay_bundle.json

    This matches the cache key specification in M12_plan.md:
    "Cache key = SHA256(case manifest + metrics + overlay bundle)"

    Args:
        case_dir: Path to the case directory.

    Returns:
        SHA256 hash string.

    Raises:
        FileNotFoundError: If required files are missing.
        json.JSONDecodeError: If files contain invalid JSON.
    """
    # Load and canonicalize each artifact
    artifacts: list[str] = []

    for filename in ["manifest.json", "metrics.json", "overlay_bundle.json"]:
        filepath = case_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Required file not found: {filepath}")

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        # Convert to canonical JSON
        artifacts.append(_canonical_json(data))

    # Concatenate all artifacts and compute hash
    combined = "\n".join(artifacts)
    return compute_hash(combined)


def compute_dict_hash(data: dict[str, Any]) -> str:
    """Compute a deterministic hash for a dictionary.

    Useful for hashing request data or other structured data.

    Args:
        data: Dictionary to hash.

    Returns:
        SHA256 hash string.
    """
    return compute_hash(_canonical_json(data))

