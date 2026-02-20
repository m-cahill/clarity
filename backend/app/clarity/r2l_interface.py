"""R2L Interface for CLARITY (Deprecated).

This module is DEPRECATED as of M03. The functionality has been moved to:
- `r2l_runner.py` — R2LRunner class for CLI invocation
- `artifact_loader.py` — Artifact loading and validation

This module now provides:
1. Backward-compatible aliases for R2LInvocationError
2. Namespace utilities (get_clarity_output_namespace, validate_output_path)

The R2LInterface class is DEPRECATED and will be removed in a future milestone.
Use R2LRunner from r2l_runner.py instead.

CRITICAL CONSTRAINTS (unchanged):
1. CLARITY must NOT import internal R2L modules.
2. CLARITY must NOT modify R2L execution semantics.
3. All R2L invocation must be through CLI or stable public interface.
"""

from __future__ import annotations

import warnings
from pathlib import Path

# Re-export exceptions from the new location for backward compatibility
from app.clarity.r2l_runner import R2LInvocationError, R2LRunner, R2LTimeoutError

__all__ = [
    "R2LInvocationError",
    "R2LTimeoutError",
    "R2LRunner",
    "get_clarity_output_namespace",
    "validate_output_path",
    # Deprecated
    "R2LInterface",
]


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


class R2LInterface:
    """DEPRECATED: Thin CLI-based interface to R2L.

    .. deprecated::
        This class is deprecated as of M03. Use `R2LRunner` from
        `app.clarity.r2l_runner` instead.

    This class provided a minimal interface for invoking R2L runs via CLI.
    It has been replaced by `R2LRunner` which provides:
    - Proper subprocess management with timeout
    - Structured result objects
    - Better error handling

    Example migration::

        # Old (deprecated):
        from app.clarity.r2l_interface import R2LInterface
        interface = R2LInterface(r2l_bin="r2l")
        result = interface.invoke(spec_path=..., output_dir=...)

        # New (recommended):
        from app.clarity.r2l_runner import R2LRunner
        runner = R2LRunner("r2l", timeout_seconds=300)
        result = runner.run(config_path=..., output_dir=...)
    """

    # Forbidden import patterns - enforced by AST test
    FORBIDDEN_IMPORT_PATTERNS: list[str] = [
        "r2l.internal",
        "r2l.runner",
        "r2l._private",
    ]

    def __init__(self, r2l_bin: str | Path = "r2l") -> None:
        """Initialize the R2L interface.

        .. deprecated::
            Use R2LRunner instead.

        Args:
            r2l_bin: Path to the R2L CLI binary. Defaults to "r2l" (assumes on PATH).
        """
        warnings.warn(
            "R2LInterface is deprecated since M03. Use R2LRunner instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.r2l_bin = Path(r2l_bin) if isinstance(r2l_bin, str) else r2l_bin

    def invoke(
        self,
        *,
        spec_path: Path,
        output_dir: Path,
        seed: int | None = None,
        timeout: int = 300,
    ) -> dict:
        """Invoke an R2L run via CLI.

        .. deprecated::
            Use R2LRunner.run() instead.

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
            This method returns a stub response. For real functionality,
            use R2LRunner.run() instead.
        """
        warnings.warn(
            "R2LInterface.invoke() is deprecated. Use R2LRunner.run() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Return stub response for backward compatibility
        _ = spec_path, output_dir, seed, timeout  # Mark as intentionally unused

        return {
            "returncode": 0,
            "stdout": "[DEPRECATED] R2LInterface.invoke() - use R2LRunner instead",
            "stderr": "",
            "stub": True,
        }

    def check_version(self) -> str:
        """Check the R2L version.

        .. deprecated::
            This method is deprecated.

        Returns:
            The R2L version string.

        Note:
            This returns a placeholder. For real functionality,
            invoke R2L CLI directly.
        """
        warnings.warn(
            "R2LInterface.check_version() is deprecated.",
            DeprecationWarning,
            stacklevel=2,
        )
        return "r2l-deprecated-use-R2LRunner"
