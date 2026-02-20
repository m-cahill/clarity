"""CLARITY Core Module.

Clinical Localization and Reasoning Integrity Testing.

This module contains the core CLARITY logic for boundary enforcement,
deterministic serialization, and R2L artifact consumption.

CLARITY operates as a pure consumer of R2L — it never modifies R2L
execution semantics.
"""

from app.clarity.r2l_interface import (
    R2LInterface,
    R2LInvocationError,
    get_clarity_output_namespace,
    validate_output_path,
)
from app.clarity.serialization import (
    deterministic_json_dumps,
    deterministic_json_dumps_bytes,
)
from app.clarity.sweep_manifest import SweepManifest

__all__ = [
    "R2LInterface",
    "R2LInvocationError",
    "SweepManifest",
    "deterministic_json_dumps",
    "deterministic_json_dumps_bytes",
    "get_clarity_output_namespace",
    "validate_output_path",
]

