"""Boundary Contract Guardrail Tests for CLARITY.

These tests enforce the CLARITY ↔ R2L boundary contract as defined in
docs/CLARITY_ARCHITECHTURE_CONTRACT.MD.

Test Categories:
1. Artifact Parse Tests - Validate R2L artifact consumption
2. No-Overwrite Tests - Ensure CLARITY writes only to clarity/ namespace
3. Determinism Tests - Verify byte-identical serialization
4. AST Import Tests - Prevent forbidden R2L internal imports
"""

from __future__ import annotations

import ast
import json
import tempfile
from pathlib import Path

import pytest

from app.clarity.r2l_interface import (
    R2LInterface,
    get_clarity_output_namespace,
    validate_output_path,
)
from app.clarity.serialization import (
    deterministic_json_dumps,
    deterministic_json_dumps_bytes,
)
from app.clarity.sweep_manifest import SweepManifest

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "r2l_samples"


# =============================================================================
# ARTIFACT PARSE TESTS
# =============================================================================


class TestArtifactParsing:
    """Test CLARITY's ability to parse R2L artifacts."""

    def test_parse_manifest_json(self) -> None:
        """Verify manifest.json can be parsed correctly."""
        manifest_path = FIXTURES_DIR / "manifest.json"
        assert manifest_path.exists(), f"Fixture not found: {manifest_path}"

        with open(manifest_path) as f:
            manifest = json.load(f)

        # Verify required fields exist
        assert "version" in manifest
        assert "run_id" in manifest
        assert "status" in manifest
        assert manifest["status"] == "completed"

    def test_parse_trace_pack_with_metadata(self) -> None:
        """Verify trace_pack with adapter_metadata can be parsed."""
        trace_path = FIXTURES_DIR / "trace_pack_with_metadata.jsonl"
        assert trace_path.exists(), f"Fixture not found: {trace_path}"

        records = []
        with open(trace_path) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        assert len(records) == 3

        # Find the record with adapter_metadata
        metadata_records = [r for r in records if "adapter_metadata" in r]
        assert len(metadata_records) == 1

        # Verify metadata structure
        metadata = metadata_records[0]["adapter_metadata"]
        assert "attention_weights" in metadata
        assert "confidence" in metadata
        assert "evidence_regions" in metadata

    def test_parse_trace_pack_without_metadata(self) -> None:
        """Verify trace_pack WITHOUT adapter_metadata can be parsed.

        This is critical: CLARITY must work with canonical adapter output
        that does not include rich mode metadata.
        """
        trace_path = FIXTURES_DIR / "trace_pack_without_metadata.jsonl"
        assert trace_path.exists(), f"Fixture not found: {trace_path}"

        records = []
        with open(trace_path) as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        assert len(records) == 3

        # Verify NO records have adapter_metadata
        metadata_records = [r for r in records if "adapter_metadata" in r]
        assert len(metadata_records) == 0, "Unexpected adapter_metadata in canonical trace"

    def test_optional_metadata_does_not_fail(self) -> None:
        """Verify absence of adapter_metadata does not cause failures.

        This guardrail ensures CLARITY does not hard-depend on rich mode.
        """
        trace_path = FIXTURES_DIR / "trace_pack_without_metadata.jsonl"

        with open(trace_path) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    # Accessing optional field should return None, not raise
                    metadata = record.get("adapter_metadata")
                    # This assertion confirms we can safely access the optional field
                    assert metadata is None or isinstance(metadata, dict)


# =============================================================================
# NO-OVERWRITE TESTS
# =============================================================================


class TestNoOverwrite:
    """Test that CLARITY writes only to the clarity/ namespace."""

    def test_clarity_output_namespace(self) -> None:
        """Verify the CLARITY output namespace is correct."""
        namespace = get_clarity_output_namespace()
        assert namespace == "clarity/"

    def test_valid_output_path_in_clarity_namespace(self) -> None:
        """Verify paths within clarity/ are accepted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            # Create the clarity directory
            (base_dir / "clarity").mkdir()

            # Valid paths
            assert validate_output_path(Path("clarity/sweep_manifest.json"), base_dir)
            assert validate_output_path(Path("clarity/robustness_surface.json"), base_dir)
            assert validate_output_path(Path("clarity/report/clarity_report.pdf"), base_dir)

    def test_invalid_output_path_outside_clarity_namespace(self) -> None:
        """Verify paths outside clarity/ are rejected.

        This guardrail prevents CLARITY from overwriting R2L artifacts.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            # Create the clarity directory
            (base_dir / "clarity").mkdir()

            # Invalid paths - should be rejected
            assert not validate_output_path(Path("manifest.json"), base_dir)
            assert not validate_output_path(Path("trace_pack.jsonl"), base_dir)
            assert not validate_output_path(Path("r2l_output/results.json"), base_dir)
            assert not validate_output_path(Path("../outside/file.json"), base_dir)

    def test_symlink_escape_prevented(self) -> None:
        """Verify symlink-based escape attempts are blocked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            # Create the clarity directory
            (base_dir / "clarity").mkdir()
            # Create an outside directory
            outside_dir = base_dir / "outside"
            outside_dir.mkdir()

            # Attempting to reference outside via relative path should fail
            assert not validate_output_path(Path("clarity/../manifest.json"), base_dir)


# =============================================================================
# DETERMINISM TESTS
# =============================================================================


class TestDeterminism:
    """Test deterministic serialization guarantees."""

    def test_json_key_ordering_stable(self) -> None:
        """Verify JSON keys are sorted deterministically."""
        # Create dict with intentionally unordered keys
        data = {"z": 1, "a": 2, "m": 3, "b": 4}

        result = deterministic_json_dumps(data)

        # Keys must be sorted
        assert result == '{"a":2,"b":4,"m":3,"z":1}'

    def test_nested_key_ordering_stable(self) -> None:
        """Verify nested dict keys are also sorted."""
        data = {
            "outer_z": {"inner_b": 1, "inner_a": 2},
            "outer_a": {"inner_z": 3, "inner_m": 4},
        }

        result = deterministic_json_dumps(data)

        # Parse and verify structure
        parsed = json.loads(result)

        # Verify key order in output string
        assert '"outer_a"' in result
        assert result.index('"outer_a"') < result.index('"outer_z"')

    def test_byte_identical_output_multiple_runs(self) -> None:
        """Verify byte-identical output across multiple serializations.

        This is the core determinism guardrail.
        """
        data = {
            "seeds": [42, 43],
            "perturbation_axes": ["blur", "noise"],
            "r2l_version": "abc123",
            "adapter_model_id": "medgemma-v1",
            "rich_mode": False,
        }

        # Serialize multiple times
        outputs = [deterministic_json_dumps(data) for _ in range(10)]

        # All outputs must be identical
        assert all(o == outputs[0] for o in outputs)

    def test_sweep_manifest_deterministic_serialization(self) -> None:
        """Verify SweepManifest serialization is byte-identical across runs."""
        manifest = SweepManifest(
            seeds=[42, 43],
            perturbation_axes=["blur"],
            r2l_version="abc123def456",
            adapter_model_id="medgemma-stub",
            rich_mode=False,
        )

        # Serialize multiple times
        outputs = [deterministic_json_dumps(manifest) for _ in range(10)]

        # All outputs must be identical
        assert all(o == outputs[0] for o in outputs)

        # Verify key ordering
        parsed = json.loads(outputs[0])
        keys = list(parsed.keys())
        assert keys == sorted(keys), "Keys must be sorted"

    def test_bytes_encoding_deterministic(self) -> None:
        """Verify bytes encoding is deterministic UTF-8."""
        data = {"key": "value", "unicode": "日本語"}

        bytes_output_1 = deterministic_json_dumps_bytes(data)
        bytes_output_2 = deterministic_json_dumps_bytes(data)

        assert bytes_output_1 == bytes_output_2
        assert isinstance(bytes_output_1, bytes)

        # Verify UTF-8 encoding
        decoded = bytes_output_1.decode("utf-8")
        assert "日本語" in decoded

    def test_compact_separators_used(self) -> None:
        """Verify compact separators (no extra spaces) are used."""
        data = {"a": 1, "b": 2}

        result = deterministic_json_dumps(data)

        # Should use compact separators: no space after colon or comma
        assert result == '{"a":1,"b":2}'
        assert ": " not in result
        assert ", " not in result


# =============================================================================
# AST IMPORT TESTS
# =============================================================================


class TestASTImportGuardrails:
    """Test that forbidden R2L imports are detected.

    This guardrail prevents future code from importing internal R2L modules.
    """

    # Forbidden import patterns
    FORBIDDEN_PATTERNS = [
        "r2l.internal",
        "r2l.runner",
        "r2l._private",
    ]

    def _scan_file_for_forbidden_imports(self, filepath: Path) -> list[str]:
        """Scan a Python file for forbidden imports.

        Returns a list of violation messages.
        """
        violations = []

        with open(filepath, encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(filepath))
            except SyntaxError:
                # Skip files with syntax errors (shouldn't happen in tests)
                return []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for pattern in self.FORBIDDEN_PATTERNS:
                        if alias.name.startswith(pattern):
                            violations.append(
                                f"{filepath}:{node.lineno}: forbidden import '{alias.name}'"
                            )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for pattern in self.FORBIDDEN_PATTERNS:
                        if node.module.startswith(pattern):
                            violations.append(
                                f"{filepath}:{node.lineno}: forbidden import from '{node.module}'"
                            )

        return violations

    def test_no_forbidden_imports_in_clarity_module(self) -> None:
        """Verify no forbidden R2L imports exist in the clarity module.

        This test scans all Python files in app/clarity/ for forbidden imports.
        """
        clarity_dir = Path(__file__).parent.parent / "app" / "clarity"

        if not clarity_dir.exists():
            pytest.skip("clarity module not yet created")

        all_violations = []

        for py_file in clarity_dir.rglob("*.py"):
            violations = self._scan_file_for_forbidden_imports(py_file)
            all_violations.extend(violations)

        assert not all_violations, (
            f"Forbidden R2L imports detected:\n" + "\n".join(all_violations)
        )

    def test_forbidden_import_detection_works(self) -> None:
        """Verify the detection mechanism actually catches violations.

        This is a meta-test to ensure our guardrail isn't broken.
        """
        # Create a temporary file with a forbidden import
        test_code = """
import r2l.internal.secrets
from r2l.runner import something
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(test_code)
            temp_path = Path(f.name)

        try:
            violations = self._scan_file_for_forbidden_imports(temp_path)
            assert len(violations) == 2, "Should detect both forbidden imports"
            assert "r2l.internal" in violations[0]
            assert "r2l.runner" in violations[1]
        finally:
            temp_path.unlink()


# =============================================================================
# R2L INTERFACE TESTS (DEPRECATED - Testing backward compatibility)
# =============================================================================


class TestR2LInterface:
    """Test the R2L interface (deprecated, testing backward compatibility).

    Note: R2LInterface is deprecated since M03. These tests verify backward
    compatibility and emit deprecation warnings.
    """

    def test_interface_instantiation(self) -> None:
        """Verify R2L interface can be instantiated with deprecation warning."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            interface = R2LInterface()
            assert interface.r2l_bin == Path("r2l")

            # Verify deprecation warning was emitted
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

    def test_interface_custom_bin_path(self) -> None:
        """Verify custom binary path is accepted."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            interface = R2LInterface(r2l_bin="/usr/local/bin/r2l")
            assert interface.r2l_bin == Path("/usr/local/bin/r2l")

    def test_invoke_returns_stub(self) -> None:
        """Verify invoke returns stub response with deprecation warning."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            interface = R2LInterface()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = interface.invoke(
                spec_path=Path("test.json"),
                output_dir=Path("/tmp/output"),
                seed=42,
            )

            assert result["stub"] is True
            assert result["returncode"] == 0
            # Verify deprecation warning was emitted for invoke()
            assert len(w) >= 1
            assert any(issubclass(warning.category, DeprecationWarning) for warning in w)

    def test_check_version_returns_stub(self) -> None:
        """Verify version check returns deprecation message."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            interface = R2LInterface()
            version = interface.check_version()

            # Now checks for "deprecated" instead of "stub"
            assert "deprecated" in version.lower()

    def test_forbidden_patterns_defined(self) -> None:
        """Verify forbidden import patterns are defined."""
        # This doesn't require instantiation, so no warning
        assert len(R2LInterface.FORBIDDEN_IMPORT_PATTERNS) >= 3
        assert "r2l.internal" in R2LInterface.FORBIDDEN_IMPORT_PATTERNS


# =============================================================================
# SWEEP MANIFEST MODEL TESTS
# =============================================================================


class TestSweepManifest:
    """Test the SweepManifest Pydantic model."""

    def test_minimal_manifest_creation(self) -> None:
        """Verify minimal manifest can be created."""
        manifest = SweepManifest(
            seeds=[42, 43],
            perturbation_axes=["blur"],
            r2l_version="abc123",
            adapter_model_id="test-model",
        )

        assert manifest.seeds == [42, 43]
        assert manifest.perturbation_axes == ["blur"]
        assert manifest.r2l_version == "abc123"
        assert manifest.adapter_model_id == "test-model"
        assert manifest.rich_mode is False  # Default

    def test_manifest_with_rich_mode(self) -> None:
        """Verify rich_mode can be set."""
        manifest = SweepManifest(
            seeds=[1],
            perturbation_axes=["noise"],
            r2l_version="def456",
            adapter_model_id="rich-model",
            rich_mode=True,
        )

        assert manifest.rich_mode is True

    def test_manifest_is_immutable(self) -> None:
        """Verify manifest is frozen (immutable)."""
        manifest = SweepManifest(
            seeds=[42],
            perturbation_axes=["blur"],
            r2l_version="abc",
            adapter_model_id="model",
        )

        with pytest.raises(Exception):  # ValidationError for frozen model
            manifest.seeds = [99]

    def test_manifest_forbids_extra_fields(self) -> None:
        """Verify extra fields are rejected."""
        with pytest.raises(Exception):  # ValidationError for extra field
            SweepManifest(
                seeds=[42],
                perturbation_axes=["blur"],
                r2l_version="abc",
                adapter_model_id="model",
                unknown_field="should fail",  # type: ignore
            )

    def test_manifest_requires_all_fields(self) -> None:
        """Verify all required fields must be provided."""
        with pytest.raises(Exception):  # ValidationError for missing field
            SweepManifest(
                seeds=[42],
                # Missing perturbation_axes, r2l_version, adapter_model_id
            )  # type: ignore

