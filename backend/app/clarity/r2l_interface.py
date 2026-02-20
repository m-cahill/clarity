"""R2L Interface for CLARITY.

This module defines the boundary between CLARITY and R2L. CLARITY operates
as a pure consumer of R2L — it invokes R2L via CLI and consumes its artifacts.

CRITICAL CONSTRAINTS:
1. CLARITY must NOT import internal R2L modules.
2. CLARITY must NOT modify R2L execution semantics.
3. All R2L invocation must be through CLI or stable public interface.

This is a stub implementation for M01 boundary guardrails.
Full implementation will be added in M03 (R2L Invocation Harness).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class R2LInvocationError(Exception):
    """Raised when R2L CLI invocation fails."""

    pass


class R2LInterface:
    """Thin CLI-based interface to R2L.

    This class provides a minimal interface for invoking R2L runs via CLI.
    It explicitly prohibits direct internal imports to maintain the
    consumer-only posture.

    Attributes:
        r2l_bin: Path to the R2L CLI binary or script.
    """

    # Forbidden import patterns - enforced by AST test
    FORBIDDEN_IMPORT_PATTERNS: list[str] = [
        "r2l.internal",
        "r2l.runner",
        "r2l._private",
    ]

    def __init__(self, r2l_bin: str | Path = "r2l") -> None:
        """Initialize the R2L interface.

        Args:
            r2l_bin: Path to the R2L CLI binary. Defaults to "r2l" (assumes on PATH).
        """
        self.r2l_bin = Path(r2l_bin) if isinstance(r2l_bin, str) else r2l_bin

    def invoke(
        self,
        *,
        spec_path: Path,
        output_dir: Path,
        seed: int | None = None,
        timeout: int = 300,
    ) -> dict[str, Any]:
        """Invoke an R2L run via CLI.

        This is a stub implementation. Full implementation in M03.

        Args:
            spec_path: Path to the R2L specification file.
            output_dir: Directory for R2L output artifacts.
            seed: Optional seed for reproducibility.
            timeout: Timeout in seconds for the R2L process.

        Returns:
            A dict containing:
                - returncode: The process exit code
                - stdout: Standard output (stub)
                - stderr: Standard error (stub)

        Raises:
            R2LInvocationError: If the R2L invocation fails.

        Note:
            This is a stub. It does NOT actually invoke R2L.
            Full implementation will be added in M03.
        """
        # Stub implementation - does not actually invoke R2L
        # This exists to establish the interface contract
        _ = spec_path, output_dir, seed, timeout  # Mark as intentionally unused

        # Return stub response
        return {
            "returncode": 0,
            "stdout": "[STUB] R2L invocation not implemented",
            "stderr": "",
            "stub": True,
        }

    def check_version(self) -> str:
        """Check the R2L version.

        Returns:
            The R2L version string.

        Raises:
            R2LInvocationError: If version check fails.

        Note:
            This is a stub. Returns a placeholder version.
        """
        # Stub implementation
        return "r2l-stub-0.0.0"


def get_clarity_output_namespace() -> str:
    """Get the CLARITY output namespace.

    CLARITY must write outputs only under this namespace to prevent
    overwriting R2L artifacts.

    Returns:
        The CLARITY output namespace (always "clarity/").
    """
    return "clarity/"


def validate_output_path(path: Path, base_dir: Path) -> bool:
    """Validate that an output path is within the CLARITY namespace.

    This guardrail prevents CLARITY from accidentally overwriting R2L
    artifacts or writing outside its designated namespace.

    Args:
        path: The proposed output path.
        base_dir: The base directory for outputs.

    Returns:
        True if the path is valid (within clarity/ namespace), False otherwise.
    """
    # Resolve paths to handle relative paths and symlinks
    resolved_path = (base_dir / path).resolve()
    clarity_dir = (base_dir / "clarity").resolve()

    # Check that the path is within the clarity namespace
    try:
        resolved_path.relative_to(clarity_dir)
        return True
    except ValueError:
        return False

