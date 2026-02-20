"""Deterministic JSON serialization for CLARITY.

This module provides stable, reproducible JSON serialization that guarantees
byte-identical output across runs. This is critical for:
- Sweep manifest determinism
- Artifact reproducibility
- CI guardrail verification

Rules enforced:
- sort_keys=True for stable key ordering
- Compact separators (",", ":") for minimal output
- No datetime.now(), uuid4(), or unseeded random
- Explicit UTF-8 encoding
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel


def deterministic_json_dumps(obj: Any, *, indent: int | None = None) -> str:
    """Serialize an object to deterministic JSON string.

    This function guarantees byte-identical output for the same input,
    which is essential for CLARITY's reproducibility guarantees.

    Args:
        obj: The object to serialize. Can be a dict, list, Pydantic model,
            or any JSON-serializable object.
        indent: Optional indentation level. If None, produces compact output.
            When specified, still maintains sort_keys=True for determinism.

    Returns:
        A JSON string with stable key ordering and consistent formatting.

    Example:
        >>> data = {"b": 2, "a": 1}
        >>> deterministic_json_dumps(data)
        '{"a":1,"b":2}'
    """
    # Handle Pydantic models
    if isinstance(obj, BaseModel):
        # Use model_dump() for Pydantic v2
        obj = obj.model_dump()

    # Serialize with deterministic settings
    if indent is not None:
        return json.dumps(
            obj,
            sort_keys=True,
            separators=(",", ": "),  # Standard indent separators
            indent=indent,
            ensure_ascii=False,
        )
    else:
        return json.dumps(
            obj,
            sort_keys=True,
            separators=(",", ":"),  # Compact separators
            ensure_ascii=False,
        )


def deterministic_json_dumps_bytes(obj: Any, *, indent: int | None = None) -> bytes:
    """Serialize an object to deterministic JSON bytes (UTF-8).

    Same as deterministic_json_dumps but returns bytes for file writing.

    Args:
        obj: The object to serialize.
        indent: Optional indentation level.

    Returns:
        UTF-8 encoded bytes of the deterministic JSON.
    """
    return deterministic_json_dumps(obj, indent=indent).encode("utf-8")

