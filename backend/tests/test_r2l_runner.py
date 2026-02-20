"""Tests for R2L Runner module.

These tests verify the R2LRunner class correctly:
- Invokes external processes via CLI
- Captures stdout/stderr
- Enforces timeout
- Raises appropriate exceptions on failure
- Returns structured results on success

All tests use the fake_r2l.py fixture for self-contained testing.
"""

from __future__ import annotations

import json
import shlex
import sys
import tempfile
from pathlib import Path

import pytest

from app.clarity.r2l_runner import (
    R2LInvocationError,
    R2LRunner,
    R2LRunResult,
    R2LTimeoutError,
)

# Path to fake R2L fixture
FAKE_R2L_PATH = Path(__file__).parent / "fixtures" / "fake_r2l.py"


def get_fake_r2l_command() -> str:
    """Get the command to invoke fake R2L as a command string.

    Returns a properly formatted command string for R2LRunner.
    On Windows, paths with spaces need to be quoted.
    """
    python_path = sys.executable
    script_path = str(FAKE_R2L_PATH.resolve())

    # On Windows, quote paths that contain spaces
    if sys.platform == "win32":
        if " " in python_path:
            python_path = f'"{python_path}"'
        if " " in script_path:
            script_path = f'"{script_path}"'

    return f"{python_path} {script_path}"


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def runner() -> R2LRunner:
    """Create an R2LRunner configured to use the fake R2L CLI."""
    return R2LRunner(get_fake_r2l_command(), timeout_seconds=30)


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Create a basic config file."""
    config = tmp_path / "config.json"
    config.write_text('{"test": true}')
    return config


@pytest.fixture
def fail_config(tmp_path: Path) -> Path:
    """Create a config file that causes fake R2L to fail."""
    config = tmp_path / "fail_config.json"
    config.write_text('{"fail": true}')
    return config


@pytest.fixture
def timeout_config(tmp_path: Path) -> Path:
    """Create a config file that causes fake R2L to timeout."""
    config = tmp_path / "timeout_config.json"
    config.write_text('{"timeout": true}')
    return config


@pytest.fixture
def no_manifest_config(tmp_path: Path) -> Path:
    """Create a config file that skips manifest generation."""
    config = tmp_path / "no_manifest_config.json"
    config.write_text('{"no_manifest": true}')
    return config


@pytest.fixture
def no_trace_config(tmp_path: Path) -> Path:
    """Create a config file that skips trace pack generation."""
    config = tmp_path / "no_trace_config.json"
    config.write_text('{"no_trace": true}')
    return config


# =============================================================================
# RUNNER INITIALIZATION TESTS
# =============================================================================


class TestR2LRunnerInit:
    """Test R2LRunner initialization."""

    def test_init_with_binary_path(self) -> None:
        """Verify runner accepts binary path."""
        runner = R2LRunner("/usr/local/bin/r2l")
        assert runner.r2l_executable == "/usr/local/bin/r2l"
        assert runner.timeout_seconds == 300  # Default

    def test_init_with_python_invocation(self) -> None:
        """Verify runner accepts python invocation string."""
        runner = R2LRunner("python -m r2l.cli")
        assert runner.r2l_executable == "python -m r2l.cli"

    def test_init_with_script_path(self) -> None:
        """Verify runner accepts script invocation."""
        runner = R2LRunner(f"python {FAKE_R2L_PATH}")
        assert "fake_r2l.py" in runner.r2l_executable

    def test_init_with_custom_timeout(self) -> None:
        """Verify custom timeout is accepted."""
        runner = R2LRunner("r2l", timeout_seconds=60)
        assert runner.timeout_seconds == 60

    def test_init_empty_executable_raises(self) -> None:
        """Verify empty executable raises ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            R2LRunner("")

    def test_init_whitespace_executable_raises(self) -> None:
        """Verify whitespace-only executable raises ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            R2LRunner("   ")

    def test_init_zero_timeout_raises(self) -> None:
        """Verify zero timeout raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            R2LRunner("r2l", timeout_seconds=0)

    def test_init_negative_timeout_raises(self) -> None:
        """Verify negative timeout raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            R2LRunner("r2l", timeout_seconds=-1)


# =============================================================================
# SUCCESSFUL INVOCATION TESTS
# =============================================================================


class TestSuccessfulInvocation:
    """Test successful R2L invocations."""

    def test_successful_invocation_returns_result(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify successful run returns R2LRunResult."""
        result = runner.run(config_file, output_dir, seed=42)

        assert isinstance(result, R2LRunResult)
        assert result.exit_code == 0
        assert result.manifest_path.exists()
        assert result.trace_pack_path.exists()

    def test_manifest_path_correct(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify manifest path is correct."""
        result = runner.run(config_file, output_dir, seed=42)

        assert result.manifest_path == output_dir / "manifest.json"

    def test_trace_pack_path_correct(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify trace pack path is correct."""
        result = runner.run(config_file, output_dir, seed=42)

        assert result.trace_pack_path == output_dir / "trace_pack.jsonl"

    def test_stdout_captured(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify stdout is captured."""
        result = runner.run(config_file, output_dir, seed=42)

        assert "FAKE R2L: Run completed successfully" in result.stdout
        assert "Seed: 42" in result.stdout

    def test_stderr_captured(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify stderr is captured (may be empty on success)."""
        result = runner.run(config_file, output_dir, seed=42)

        assert isinstance(result.stderr, str)

    def test_artifacts_have_valid_content(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify generated artifacts have valid JSON content."""
        result = runner.run(config_file, output_dir, seed=42)

        # Check manifest
        with open(result.manifest_path) as f:
            manifest = json.load(f)
        assert manifest["run_id"] == "fake-run-seed-42"
        assert manifest["seed"] == 42

        # Check trace pack
        with open(result.trace_pack_path) as f:
            records = [json.loads(line) for line in f if line.strip()]
        assert len(records) == 3
        assert records[0]["step"] == 1

    def test_adapter_passed_to_cli(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify adapter argument is passed to CLI."""
        result = runner.run(
            config_file, output_dir, adapter="test-adapter", seed=42
        )

        assert "Adapter: test-adapter" in result.stdout

    def test_seed_determinism(
        self, runner: R2LRunner, config_file: Path, tmp_path: Path
    ) -> None:
        """Verify same seed produces identical artifacts."""
        output1 = tmp_path / "output1"
        output1.mkdir()
        output2 = tmp_path / "output2"
        output2.mkdir()

        runner.run(config_file, output1, seed=123)
        runner.run(config_file, output2, seed=123)

        # Compare manifest content
        manifest1 = (output1 / "manifest.json").read_text()
        manifest2 = (output2 / "manifest.json").read_text()
        assert manifest1 == manifest2

        # Compare trace pack content
        trace1 = (output1 / "trace_pack.jsonl").read_text()
        trace2 = (output2 / "trace_pack.jsonl").read_text()
        assert trace1 == trace2

    def test_different_seeds_produce_different_output(
        self, runner: R2LRunner, config_file: Path, tmp_path: Path
    ) -> None:
        """Verify different seeds produce different artifacts."""
        output1 = tmp_path / "output1"
        output1.mkdir()
        output2 = tmp_path / "output2"
        output2.mkdir()

        runner.run(config_file, output1, seed=1)
        runner.run(config_file, output2, seed=2)

        manifest1 = (output1 / "manifest.json").read_text()
        manifest2 = (output2 / "manifest.json").read_text()
        assert manifest1 != manifest2


# =============================================================================
# FAILURE TESTS
# =============================================================================


class TestNonZeroExit:
    """Test handling of non-zero exit codes."""

    def test_nonzero_exit_raises(
        self, runner: R2LRunner, fail_config: Path, output_dir: Path
    ) -> None:
        """Verify non-zero exit raises R2LInvocationError."""
        with pytest.raises(R2LInvocationError) as exc_info:
            runner.run(fail_config, output_dir, seed=42)

        assert exc_info.value.exit_code == 1

    def test_nonzero_exit_captures_stderr(
        self, runner: R2LRunner, fail_config: Path, output_dir: Path
    ) -> None:
        """Verify stderr is captured on failure."""
        with pytest.raises(R2LInvocationError) as exc_info:
            runner.run(fail_config, output_dir, seed=42)

        assert "Simulated failure" in exc_info.value.stderr

    def test_nonzero_exit_has_informative_message(
        self, runner: R2LRunner, fail_config: Path, output_dir: Path
    ) -> None:
        """Verify exception message mentions exit code."""
        with pytest.raises(R2LInvocationError, match="exited with code 1"):
            runner.run(fail_config, output_dir, seed=42)


# =============================================================================
# TIMEOUT TESTS
# =============================================================================


class TestTimeoutEnforcement:
    """Test timeout enforcement."""

    def test_timeout_raises_r2l_timeout_error(
        self, timeout_config: Path, output_dir: Path
    ) -> None:
        """Verify timeout raises R2LTimeoutError."""
        # Use short timeout
        runner = R2LRunner(get_fake_r2l_command(), timeout_seconds=1)

        with pytest.raises(R2LTimeoutError):
            runner.run(timeout_config, output_dir, seed=42)

    def test_timeout_error_has_timeout_value(
        self, timeout_config: Path, output_dir: Path
    ) -> None:
        """Verify R2LTimeoutError includes timeout value."""
        runner = R2LRunner(get_fake_r2l_command(), timeout_seconds=1)

        with pytest.raises(R2LTimeoutError) as exc_info:
            runner.run(timeout_config, output_dir, seed=42)

        assert exc_info.value.timeout_seconds == 1

    def test_timeout_error_is_invocation_error(
        self, timeout_config: Path, output_dir: Path
    ) -> None:
        """Verify R2LTimeoutError is a subclass of R2LInvocationError."""
        runner = R2LRunner(get_fake_r2l_command(), timeout_seconds=1)

        with pytest.raises(R2LInvocationError):
            runner.run(timeout_config, output_dir, seed=42)


# =============================================================================
# MISSING ARTIFACT TESTS
# =============================================================================


class TestMissingArtifacts:
    """Test handling of missing artifacts."""

    def test_missing_manifest_raises(
        self, runner: R2LRunner, no_manifest_config: Path, output_dir: Path
    ) -> None:
        """Verify missing manifest raises R2LInvocationError."""
        with pytest.raises(R2LInvocationError, match="manifest.json"):
            runner.run(no_manifest_config, output_dir, seed=42)

    def test_missing_trace_pack_raises(
        self, runner: R2LRunner, no_trace_config: Path, output_dir: Path
    ) -> None:
        """Verify missing trace pack raises R2LInvocationError."""
        with pytest.raises(R2LInvocationError, match="trace_pack.jsonl"):
            runner.run(no_trace_config, output_dir, seed=42)


# =============================================================================
# OUTPUT DIRECTORY VALIDATION TESTS
# =============================================================================


class TestOutputDirectoryValidation:
    """Test output directory validation."""

    def test_nonexistent_output_dir_raises(
        self, runner: R2LRunner, config_file: Path, tmp_path: Path
    ) -> None:
        """Verify non-existent output directory raises ValueError."""
        nonexistent = tmp_path / "does_not_exist"

        with pytest.raises(ValueError, match="does not exist"):
            runner.run(config_file, nonexistent, seed=42)

    def test_file_as_output_dir_raises(
        self, runner: R2LRunner, config_file: Path, tmp_path: Path
    ) -> None:
        """Verify file path as output directory raises ValueError."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("not a directory")

        with pytest.raises(ValueError, match="not a directory"):
            runner.run(config_file, file_path, seed=42)


# =============================================================================
# RESULT IMMUTABILITY TESTS
# =============================================================================


class TestResultImmutability:
    """Test R2LRunResult immutability."""

    def test_result_is_frozen_dataclass(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify R2LRunResult is immutable."""
        result = runner.run(config_file, output_dir, seed=42)

        with pytest.raises(Exception):  # FrozenInstanceError
            result.exit_code = 99  # type: ignore

    def test_result_fields_accessible(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify all R2LRunResult fields are accessible."""
        result = runner.run(config_file, output_dir, seed=42)

        assert isinstance(result.manifest_path, Path)
        assert isinstance(result.trace_pack_path, Path)
        assert isinstance(result.stdout, str)
        assert isinstance(result.stderr, str)
        assert isinstance(result.exit_code, int)


# =============================================================================
# ABSOLUTE PATH TESTS
# =============================================================================


class TestAbsolutePaths:
    """Test that runner uses absolute paths."""

    def test_relative_paths_resolved(
        self, runner: R2LRunner, config_file: Path, output_dir: Path
    ) -> None:
        """Verify relative paths are resolved to absolute."""
        # Create relative path versions
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(config_file.parent)
            rel_config = Path(config_file.name)
            rel_output = Path(output_dir.relative_to(config_file.parent))

            result = runner.run(rel_config, rel_output, seed=42)

            # Result paths should be absolute
            assert result.manifest_path.is_absolute()
            assert result.trace_pack_path.is_absolute()
        finally:
            os.chdir(original_cwd)


# =============================================================================
# EXCEPTION ATTRIBUTE TESTS
# =============================================================================


class TestExceptionAttributes:
    """Test exception attributes are properly set."""

    def test_invocation_error_attributes(
        self, runner: R2LRunner, fail_config: Path, output_dir: Path
    ) -> None:
        """Verify R2LInvocationError has all attributes."""
        with pytest.raises(R2LInvocationError) as exc_info:
            runner.run(fail_config, output_dir, seed=42)

        err = exc_info.value
        assert hasattr(err, "exit_code")
        assert hasattr(err, "stdout")
        assert hasattr(err, "stderr")
        assert err.exit_code == 1
        assert isinstance(err.stdout, str)
        assert isinstance(err.stderr, str)

    def test_timeout_error_attributes(
        self, timeout_config: Path, output_dir: Path
    ) -> None:
        """Verify R2LTimeoutError has all attributes."""
        runner = R2LRunner(get_fake_r2l_command(), timeout_seconds=1)

        with pytest.raises(R2LTimeoutError) as exc_info:
            runner.run(timeout_config, output_dir, seed=42)

        err = exc_info.value
        assert hasattr(err, "timeout_seconds")
        assert hasattr(err, "stdout")
        assert hasattr(err, "stderr")
        assert err.timeout_seconds == 1

