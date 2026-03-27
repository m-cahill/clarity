"""Canonical public consumer surface for CLARITY (M21).

This module is the **only** supported import path for downstream consumers who
depend on the readiness **public invocation contract**. Symbols re-exported here
are frozen; other ``app.clarity`` imports are internal unless listed in
``docs/readiness/CLARITY_PUBLIC_SURFACE.md``.

Import example::

    from app.clarity.public_surface import R2LRunner, SweepOrchestrator, SweepConfig
"""

from __future__ import annotations

from app.clarity.r2l_runner import (
    R2LInvocationError,
    R2LRunner,
    R2LRunResult,
    R2LTimeoutError,
)
from app.clarity.sweep_models import (
    SweepAxis,
    SweepConfig,
    SweepConfigValidationError,
    SweepRunRecord,
    build_run_directory_name,
    encode_axis_value,
)
from app.clarity.sweep_orchestrator import (
    OutputDirectoryExistsError,
    SweepExecutionError,
    SweepOrchestrator,
    SweepResult,
)

__all__ = [
    "OutputDirectoryExistsError",
    "R2LInvocationError",
    "R2LRunner",
    "R2LRunResult",
    "R2LTimeoutError",
    "SweepAxis",
    "SweepConfig",
    "SweepConfigValidationError",
    "SweepExecutionError",
    "SweepOrchestrator",
    "SweepResult",
    "SweepRunRecord",
    "build_run_directory_name",
    "encode_axis_value",
]

# Frozen set of public names for guardrail tests (must match __all__ exactly).
PUBLIC_SURFACE_SYMBOLS: frozenset[str] = frozenset(__all__)
