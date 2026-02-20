"""R2L Runner for CLARITY.

This module provides a black-box invocation harness for R2L. CLARITY operates
as a pure consumer of R2L — it invokes R2L via CLI only and consumes its
declared artifacts.

CRITICAL CONSTRAINTS (M03):
1. CLARITY must NOT import any r2l modules.
2. CLARITY must NOT share memory with R2L.
3. All R2L invocation must be through subprocess (CLI).
4. Runner must not depend on current working directory.
5. Runner must emit structured result even on failure.

This module replaces the M01 stub `r2l_interface.py`.
"""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence


class R2LInvocationError(Exception):
    """Raised when R2L CLI invocation fails.

    This exception is raised when:
    - R2L process exits with non-zero code
    - Required artifacts are missing after run
    - CLI invocation itself fails

    Attributes:
        exit_code: The exit code from the R2L process (if available).
        stdout: Standard output from the process (if available).
        stderr: Standard error from the process (if available).
    """

    def __init__(
        self,
        message: str,
        *,
        exit_code: int | None = None,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        """Initialize the invocation error.

        Args:
            message: Human-readable error description.
            exit_code: The exit code from the R2L process.
            stdout: Standard output captured from the process.
            stderr: Standard error captured from the process.
        """
        super().__init__(message)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class R2LTimeoutError(R2LInvocationError):
    """Raised when R2L CLI invocation times out.

    This is a specific case of R2LInvocationError that occurs when the
    subprocess exceeds the configured timeout.
    """

    def __init__(
        self,
        message: str,
        *,
        timeout_seconds: int,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        """Initialize the timeout error.

        Args:
            message: Human-readable error description.
            timeout_seconds: The timeout that was exceeded.
            stdout: Partial stdout captured before timeout.
            stderr: Partial stderr captured before timeout.
        """
        super().__init__(message, exit_code=None, stdout=stdout, stderr=stderr)
        self.timeout_seconds = timeout_seconds


@dataclass(frozen=True)
class R2LRunResult:
    """Result of a successful R2L invocation.

    This is an immutable dataclass containing paths to artifacts and
    captured output from the R2L process.

    Attributes:
        manifest_path: Path to the manifest.json artifact.
        trace_pack_path: Path to the trace_pack.jsonl artifact.
        stdout: Standard output from the R2L process.
        stderr: Standard error from the R2L process.
        exit_code: Exit code from the R2L process (always 0 for success).
    """

    manifest_path: Path
    trace_pack_path: Path
    stdout: str
    stderr: str
    exit_code: int


class R2LRunner:
    """Black-box CLI runner for R2L.

    This class provides a subprocess-based interface for invoking R2L runs.
    It enforces the CLARITY↔R2L boundary by using only CLI invocation and
    consuming declared artifacts.

    The runner:
    - Uses subprocess.run() for execution
    - Captures stdout/stderr
    - Enforces timeout
    - Fails loudly on non-zero exit
    - Always uses absolute paths

    Attributes:
        r2l_executable: The R2L CLI command (may be multi-part, e.g., "python -m r2l.cli").
        timeout_seconds: Maximum seconds to wait for R2L process.

    Example:
        >>> runner = R2LRunner("python -m r2l.cli", timeout_seconds=300)
        >>> result = runner.run(
        ...     config_path=Path("/path/to/config.json"),
        ...     output_dir=Path("/path/to/output"),
        ...     adapter="medgemma",
        ...     seed=42,
        ... )
        >>> print(result.manifest_path)
    """

    def __init__(self, r2l_executable: str, timeout_seconds: int = 300) -> None:
        """Initialize the R2L runner.

        Args:
            r2l_executable: The R2L CLI command. Can be:
                - A binary path: "/usr/local/bin/r2l"
                - A Python invocation: "python -m r2l.cli"
                - A script invocation: "python /path/to/r2l_cli.py"
                Will be split using shlex.split() for safe argument handling.
                On Windows, uses posix=False for proper path handling.
            timeout_seconds: Maximum seconds to wait for the R2L process.
                Default is 300 (5 minutes).

        Raises:
            ValueError: If r2l_executable is empty or timeout_seconds <= 0.
        """
        if not r2l_executable or not r2l_executable.strip():
            raise ValueError("r2l_executable must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        # Use posix=False on Windows for proper path handling
        import sys
        posix = sys.platform != "win32"
        self._executable_parts: list[str] = shlex.split(r2l_executable, posix=posix)
        self._timeout_seconds = timeout_seconds

    @property
    def r2l_executable(self) -> str:
        """The R2L executable command as a string."""
        return shlex.join(self._executable_parts)

    @property
    def timeout_seconds(self) -> int:
        """The timeout in seconds for R2L invocations."""
        return self._timeout_seconds

    def _build_command(
        self,
        config_path: Path,
        output_dir: Path,
        *,
        adapter: str | None = None,
        seed: int | None = None,
    ) -> list[str]:
        """Build the command line arguments for R2L invocation.

        Args:
            config_path: Path to the R2L configuration file.
            output_dir: Directory for R2L output artifacts.
            adapter: Optional adapter name.
            seed: Optional seed for reproducibility.

        Returns:
            List of command line arguments.
        """
        # Start with executable parts
        cmd: list[str] = list(self._executable_parts)

        # Add required arguments (always absolute paths)
        cmd.extend(["--config", str(config_path.resolve())])
        cmd.extend(["--output", str(output_dir.resolve())])

        # Add optional arguments
        if adapter is not None:
            cmd.extend(["--adapter", adapter])
        if seed is not None:
            cmd.extend(["--seed", str(seed)])

        return cmd

    def run(
        self,
        config_path: Path,
        output_dir: Path,
        *,
        adapter: str | None = None,
        seed: int | None = None,
    ) -> R2LRunResult:
        """Run an R2L invocation via CLI.

        This method:
        1. Builds the command line arguments
        2. Executes R2L via subprocess.run()
        3. Captures stdout/stderr
        4. Validates exit code
        5. Verifies required artifacts exist
        6. Returns structured result

        Args:
            config_path: Path to the R2L configuration file. Will be resolved
                to absolute path before invocation.
            output_dir: Directory for R2L output artifacts. Will be resolved
                to absolute path before invocation. Directory must exist.
            adapter: Optional adapter name to pass to R2L.
            seed: Optional seed for reproducibility.

        Returns:
            R2LRunResult containing artifact paths and captured output.

        Raises:
            R2LInvocationError: If R2L exits with non-zero code or required
                artifacts are missing.
            R2LTimeoutError: If R2L process exceeds timeout_seconds.
            ValueError: If output_dir does not exist.
        """
        # Validate output directory exists
        output_dir_resolved = output_dir.resolve()
        if not output_dir_resolved.exists():
            raise ValueError(f"output_dir does not exist: {output_dir_resolved}")
        if not output_dir_resolved.is_dir():
            raise ValueError(f"output_dir is not a directory: {output_dir_resolved}")

        # Build command
        cmd = self._build_command(
            config_path, output_dir, adapter=adapter, seed=seed
        )

        # Execute subprocess
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,  # We handle exit code ourselves
            )
        except subprocess.TimeoutExpired as e:
            # Extract partial output if available
            stdout = e.stdout.decode("utf-8", errors="replace") if e.stdout else ""
            stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
            raise R2LTimeoutError(
                f"R2L process timed out after {self._timeout_seconds} seconds",
                timeout_seconds=self._timeout_seconds,
                stdout=stdout,
                stderr=stderr,
            ) from e
        except OSError as e:
            raise R2LInvocationError(
                f"Failed to execute R2L command: {e}",
                exit_code=None,
                stdout="",
                stderr=str(e),
            ) from e

        # Check exit code
        if result.returncode != 0:
            raise R2LInvocationError(
                f"R2L exited with code {result.returncode}",
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        # Verify required artifacts exist
        manifest_path = output_dir_resolved / "manifest.json"
        trace_pack_path = output_dir_resolved / "trace_pack.jsonl"

        if not manifest_path.exists():
            raise R2LInvocationError(
                f"Required artifact missing: {manifest_path}",
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        if not trace_pack_path.exists():
            raise R2LInvocationError(
                f"Required artifact missing: {trace_pack_path}",
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        return R2LRunResult(
            manifest_path=manifest_path,
            trace_pack_path=trace_pack_path,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

