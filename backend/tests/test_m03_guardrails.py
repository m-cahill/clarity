"""AST Guardrail Tests for M03.

These tests enforce the M03 hardened boundary:
1. No R2L imports at all (not even `import r2l`)
2. No random module usage in harness
3. No datetime.now() usage
4. No uuid4() usage

This tightens the M01 guardrails per M03 locked answers:
"No R2L imports at all" — CLI invocation only.
"""

from __future__ import annotations

import ast
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Callable

# Path to clarity module
CLARITY_DIR = Path(__file__).parent.parent / "app" / "clarity"

# Modules specifically created/modified in M03
M03_MODULES = [
    "r2l_runner.py",
    "artifact_loader.py",
]


# =============================================================================
# AST SCANNING UTILITIES
# =============================================================================


def scan_file_for_imports(filepath: Path, patterns: list[str]) -> list[str]:
    """Scan a Python file for import statements matching patterns.

    Args:
        filepath: Path to the Python file to scan.
        patterns: List of import patterns to detect. Each pattern is checked
            against the imported module name.

    Returns:
        List of violation messages, empty if no violations found.
    """
    violations = []

    with open(filepath, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError:
            return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for pattern in patterns:
                    if alias.name == pattern or alias.name.startswith(f"{pattern}."):
                        violations.append(
                            f"{filepath}:{node.lineno}: forbidden import '{alias.name}'"
                        )

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for pattern in patterns:
                    if node.module == pattern or node.module.startswith(f"{pattern}."):
                        violations.append(
                            f"{filepath}:{node.lineno}: forbidden import from '{node.module}'"
                        )

    return violations


def scan_file_for_function_calls(
    filepath: Path, func_names: list[str]
) -> list[str]:
    """Scan a Python file for specific function calls.

    Args:
        filepath: Path to the Python file to scan.
        func_names: List of function names to detect (e.g., ["datetime.now", "uuid4"]).

    Returns:
        List of violation messages, empty if no violations found.
    """
    violations = []

    with open(filepath, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError:
            return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = _get_call_name(node)
            if func_name in func_names:
                violations.append(
                    f"{filepath}:{node.lineno}: forbidden call to '{func_name}'"
                )

    return violations


def _get_call_name(node: ast.Call) -> str:
    """Extract the full function name from a Call node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        parts = []
        current = node.func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    return ""


def scan_directory_for_violations(
    directory: Path,
    check_func: Callable[[Path], list[str]],
    include_subdirs: bool = True,
) -> list[str]:
    """Scan all Python files in a directory for violations.

    Args:
        directory: Directory to scan.
        check_func: Function that takes a file path and returns violations.
        include_subdirs: Whether to scan subdirectories.

    Returns:
        Combined list of all violations found.
    """
    all_violations = []

    if include_subdirs:
        py_files = directory.rglob("*.py")
    else:
        py_files = directory.glob("*.py")

    for py_file in py_files:
        violations = check_func(py_file)
        all_violations.extend(violations)

    return all_violations


# =============================================================================
# NO R2L IMPORTS TESTS (HARDENED FROM M01)
# =============================================================================


class TestNoR2LImports:
    """Test that no R2L imports exist in CLARITY module.

    M03 hardens the boundary: "No R2L imports at all."
    This means even `import r2l` is forbidden.
    """

    # Forbidden patterns - any r2l import
    FORBIDDEN_R2L_PATTERNS = ["r2l"]

    def test_no_r2l_imports_in_clarity_module(self) -> None:
        """Verify no R2L imports exist in the clarity module."""
        if not CLARITY_DIR.exists():
            pytest.skip("clarity module not found")

        violations = scan_directory_for_violations(
            CLARITY_DIR,
            lambda f: scan_file_for_imports(f, self.FORBIDDEN_R2L_PATTERNS),
        )

        assert not violations, (
            f"Forbidden R2L imports detected (M03 boundary violation):\n"
            + "\n".join(violations)
        )

    def test_no_r2l_imports_in_r2l_runner(self) -> None:
        """Verify r2l_runner.py has no R2L imports."""
        runner_path = CLARITY_DIR / "r2l_runner.py"
        if not runner_path.exists():
            pytest.skip("r2l_runner.py not found")

        violations = scan_file_for_imports(runner_path, self.FORBIDDEN_R2L_PATTERNS)

        assert not violations, (
            f"r2l_runner.py has forbidden R2L imports:\n" + "\n".join(violations)
        )

    def test_no_r2l_imports_in_artifact_loader(self) -> None:
        """Verify artifact_loader.py has no R2L imports."""
        loader_path = CLARITY_DIR / "artifact_loader.py"
        if not loader_path.exists():
            pytest.skip("artifact_loader.py not found")

        violations = scan_file_for_imports(loader_path, self.FORBIDDEN_R2L_PATTERNS)

        assert not violations, (
            f"artifact_loader.py has forbidden R2L imports:\n" + "\n".join(violations)
        )

    def test_detection_mechanism_works(self) -> None:
        """Verify the detection mechanism catches R2L imports."""
        test_code = """
import r2l
from r2l import something
from r2l.internal import secrets
import r2l.runner
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            violations = scan_file_for_imports(temp_path, self.FORBIDDEN_R2L_PATTERNS)
            assert len(violations) == 4, f"Expected 4 violations, got {len(violations)}"
        finally:
            temp_path.unlink()


# =============================================================================
# NO RANDOM MODULE TESTS
# =============================================================================


class TestNoRandomImports:
    """Test that random module is not imported in M03 modules."""

    FORBIDDEN_PATTERNS = ["random"]

    def test_no_random_imports_in_r2l_runner(self) -> None:
        """Verify r2l_runner.py has no random imports."""
        runner_path = CLARITY_DIR / "r2l_runner.py"
        if not runner_path.exists():
            pytest.skip("r2l_runner.py not found")

        violations = scan_file_for_imports(runner_path, self.FORBIDDEN_PATTERNS)

        assert not violations, (
            f"r2l_runner.py has forbidden random imports:\n" + "\n".join(violations)
        )

    def test_no_random_imports_in_artifact_loader(self) -> None:
        """Verify artifact_loader.py has no random imports."""
        loader_path = CLARITY_DIR / "artifact_loader.py"
        if not loader_path.exists():
            pytest.skip("artifact_loader.py not found")

        violations = scan_file_for_imports(loader_path, self.FORBIDDEN_PATTERNS)

        assert not violations, (
            f"artifact_loader.py has forbidden random imports:\n" + "\n".join(violations)
        )


# =============================================================================
# NO DATETIME.NOW() TESTS
# =============================================================================


class TestNoDatetimeNow:
    """Test that datetime.now() is not called in M03 modules."""

    FORBIDDEN_CALLS = ["datetime.now", "datetime.datetime.now"]

    def test_no_datetime_now_in_r2l_runner(self) -> None:
        """Verify r2l_runner.py has no datetime.now() calls."""
        runner_path = CLARITY_DIR / "r2l_runner.py"
        if not runner_path.exists():
            pytest.skip("r2l_runner.py not found")

        violations = scan_file_for_function_calls(runner_path, self.FORBIDDEN_CALLS)

        assert not violations, (
            f"r2l_runner.py has forbidden datetime.now() calls:\n"
            + "\n".join(violations)
        )

    def test_no_datetime_now_in_artifact_loader(self) -> None:
        """Verify artifact_loader.py has no datetime.now() calls."""
        loader_path = CLARITY_DIR / "artifact_loader.py"
        if not loader_path.exists():
            pytest.skip("artifact_loader.py not found")

        violations = scan_file_for_function_calls(loader_path, self.FORBIDDEN_CALLS)

        assert not violations, (
            f"artifact_loader.py has forbidden datetime.now() calls:\n"
            + "\n".join(violations)
        )

    def test_detection_mechanism_works(self) -> None:
        """Verify the detection mechanism catches datetime.now()."""
        test_code = """
from datetime import datetime
now = datetime.now()
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            violations = scan_file_for_function_calls(temp_path, self.FORBIDDEN_CALLS)
            assert len(violations) == 1, f"Expected 1 violation, got {len(violations)}"
        finally:
            temp_path.unlink()


# =============================================================================
# NO UUID4() TESTS
# =============================================================================


class TestNoUuid4:
    """Test that uuid4() is not called in M03 modules."""

    FORBIDDEN_CALLS = ["uuid4", "uuid.uuid4"]

    def test_no_uuid4_in_r2l_runner(self) -> None:
        """Verify r2l_runner.py has no uuid4() calls."""
        runner_path = CLARITY_DIR / "r2l_runner.py"
        if not runner_path.exists():
            pytest.skip("r2l_runner.py not found")

        violations = scan_file_for_function_calls(runner_path, self.FORBIDDEN_CALLS)

        assert not violations, (
            f"r2l_runner.py has forbidden uuid4() calls:\n" + "\n".join(violations)
        )

    def test_no_uuid4_in_artifact_loader(self) -> None:
        """Verify artifact_loader.py has no uuid4() calls."""
        loader_path = CLARITY_DIR / "artifact_loader.py"
        if not loader_path.exists():
            pytest.skip("artifact_loader.py not found")

        violations = scan_file_for_function_calls(loader_path, self.FORBIDDEN_CALLS)

        assert not violations, (
            f"artifact_loader.py has forbidden uuid4() calls:\n" + "\n".join(violations)
        )


# =============================================================================
# COMPREHENSIVE M03 MODULE SCAN
# =============================================================================


class TestM03ModuleIntegrity:
    """Comprehensive integrity tests for M03 modules."""

    ALL_FORBIDDEN_IMPORTS = ["r2l", "random"]
    ALL_FORBIDDEN_CALLS = ["datetime.now", "datetime.datetime.now", "uuid4", "uuid.uuid4"]

    def test_m03_modules_clean(self) -> None:
        """Verify all M03 modules pass all guardrail checks."""
        if not CLARITY_DIR.exists():
            pytest.skip("clarity module not found")

        all_violations = []

        for module_name in M03_MODULES:
            module_path = CLARITY_DIR / module_name
            if not module_path.exists():
                continue

            # Check imports
            import_violations = scan_file_for_imports(
                module_path, self.ALL_FORBIDDEN_IMPORTS
            )
            all_violations.extend(import_violations)

            # Check function calls
            call_violations = scan_file_for_function_calls(
                module_path, self.ALL_FORBIDDEN_CALLS
            )
            all_violations.extend(call_violations)

        assert not all_violations, (
            f"M03 module guardrail violations:\n" + "\n".join(all_violations)
        )

    def test_clarity_module_no_r2l_anywhere(self) -> None:
        """Verify no R2L imports exist anywhere in clarity module."""
        if not CLARITY_DIR.exists():
            pytest.skip("clarity module not found")

        violations = scan_directory_for_violations(
            CLARITY_DIR,
            lambda f: scan_file_for_imports(f, ["r2l"]),
        )

        assert not violations, (
            f"R2L imports found in clarity module (violates M03 boundary):\n"
            + "\n".join(violations)
        )


# =============================================================================
# BACKWARDS COMPATIBILITY WITH M01 TESTS
# =============================================================================


class TestBackwardsCompatibility:
    """Verify M03 guardrails are compatible with M01 tests."""

    def test_forbidden_patterns_include_m01_patterns(self) -> None:
        """Verify M03 patterns are a superset of M01 patterns."""
        # M01 patterns (from r2l_interface.py)
        m01_patterns = ["r2l.internal", "r2l.runner", "r2l._private"]

        # M03 pattern catches all r2l imports
        m03_pattern = "r2l"

        # Any string starting with an M01 pattern also starts with M03 pattern
        for m01 in m01_patterns:
            assert m01.startswith(m03_pattern) or m01 == m03_pattern, (
                f"M01 pattern '{m01}' not covered by M03 pattern '{m03_pattern}'"
            )

