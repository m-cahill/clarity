"""Tests for Artifact Loader module.

These tests verify the artifact loading, validation, and hashing functions:
- load_manifest: Parse and validate manifest.json
- load_trace_pack: Parse and validate trace_pack.jsonl
- hash_artifact: Compute SHA256 of file contents

All validation tests verify minimal required fields per M03 specification.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from app.clarity.artifact_loader import (
    MANIFEST_REQUIRED_FIELDS,
    ManifestValidationError,
    TracePackValidationError,
    hash_artifact,
    load_manifest,
    load_trace_pack,
    validate_manifest_schema,
    validate_trace_record,
)

# Path to existing test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "r2l_samples"


# =============================================================================
# MANIFEST LOADING TESTS
# =============================================================================


class TestLoadManifest:
    """Test manifest loading and validation."""

    def test_load_valid_manifest(self, tmp_path: Path) -> None:
        """Verify valid manifest loads correctly."""
        manifest_data = {
            "run_id": "test-run-001",
            "timestamp": "2026-01-01T00:00:00Z",
            "seed": 42,
            "artifacts": ["manifest.json", "trace_pack.jsonl"],
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_manifest(manifest_path)

        assert result == manifest_data

    def test_load_manifest_with_extra_fields(self, tmp_path: Path) -> None:
        """Verify manifest with extra fields loads without error."""
        manifest_data = {
            "run_id": "test-run-001",
            "timestamp": "2026-01-01T00:00:00Z",
            "seed": 42,
            "artifacts": ["manifest.json"],
            # Extra fields allowed
            "version": "1.0.0",
            "r2l_version": "0.1.0",
            "model_id": "test-model",
            "status": "completed",
            "extra_field": "allowed",
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        result = load_manifest(manifest_path)

        assert result["extra_field"] == "allowed"
        assert result["version"] == "1.0.0"

    def test_load_existing_fixture_manifest(self) -> None:
        """Verify existing fixture manifest can be loaded."""
        manifest_path = FIXTURES_DIR / "manifest.json"
        if not manifest_path.exists():
            pytest.skip("Fixture not available")

        result = load_manifest(manifest_path)

        assert "run_id" in result
        assert "seed" in result

    def test_load_manifest_file_not_found(self, tmp_path: Path) -> None:
        """Verify FileNotFoundError for missing file."""
        nonexistent = tmp_path / "does_not_exist.json"

        with pytest.raises(FileNotFoundError, match="Manifest not found"):
            load_manifest(nonexistent)

    def test_load_manifest_invalid_json(self, tmp_path: Path) -> None:
        """Verify ManifestValidationError for invalid JSON."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text("{ not valid json }")

        with pytest.raises(ManifestValidationError, match="Invalid JSON"):
            load_manifest(manifest_path)

    def test_load_manifest_not_object(self, tmp_path: Path) -> None:
        """Verify ManifestValidationError for non-object JSON."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text('["array", "not", "object"]')

        with pytest.raises(ManifestValidationError, match="must be a JSON object"):
            load_manifest(manifest_path)

    def test_load_manifest_missing_run_id(self, tmp_path: Path) -> None:
        """Verify ManifestValidationError for missing run_id."""
        manifest_data = {
            # Missing: "run_id"
            "timestamp": "2026-01-01T00:00:00Z",
            "seed": 42,
            "artifacts": [],
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        with pytest.raises(ManifestValidationError, match="run_id"):
            load_manifest(manifest_path)

    def test_load_manifest_missing_timestamp(self, tmp_path: Path) -> None:
        """Verify ManifestValidationError for missing timestamp."""
        manifest_data = {
            "run_id": "test",
            # Missing: "timestamp"
            "seed": 42,
            "artifacts": [],
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        with pytest.raises(ManifestValidationError, match="timestamp"):
            load_manifest(manifest_path)

    def test_load_manifest_missing_seed(self, tmp_path: Path) -> None:
        """Verify ManifestValidationError for missing seed."""
        manifest_data = {
            "run_id": "test",
            "timestamp": "2026-01-01T00:00:00Z",
            # Missing: "seed"
            "artifacts": [],
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        with pytest.raises(ManifestValidationError, match="seed"):
            load_manifest(manifest_path)

    def test_load_manifest_missing_artifacts(self, tmp_path: Path) -> None:
        """Verify ManifestValidationError for missing artifacts."""
        manifest_data = {
            "run_id": "test",
            "timestamp": "2026-01-01T00:00:00Z",
            "seed": 42,
            # Missing: "artifacts"
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        with pytest.raises(ManifestValidationError, match="artifacts"):
            load_manifest(manifest_path)

    def test_load_manifest_missing_multiple_fields(self, tmp_path: Path) -> None:
        """Verify error mentions all missing fields."""
        manifest_data = {"extra": "only"}  # Missing all required fields
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data))

        with pytest.raises(ManifestValidationError) as exc_info:
            load_manifest(manifest_path)

        # Error should mention missing fields
        assert "missing required fields" in str(exc_info.value)


# =============================================================================
# TRACE PACK LOADING TESTS
# =============================================================================


class TestLoadTracePack:
    """Test trace pack loading and validation."""

    def test_load_valid_trace_pack_with_step(self, tmp_path: Path) -> None:
        """Verify valid trace pack with 'step' field loads correctly."""
        records = [
            {"step": 1, "event": "start"},
            {"step": 2, "event": "process"},
            {"step": 3, "event": "end"},
        ]
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text("\n".join(json.dumps(r) for r in records))

        result = load_trace_pack(trace_path)

        assert len(result) == 3
        assert result[0]["step"] == 1
        assert result[2]["step"] == 3

    def test_load_valid_trace_pack_with_step_id(self, tmp_path: Path) -> None:
        """Verify valid trace pack with 'step_id' field loads correctly."""
        records = [
            {"step_id": "step-1", "event": "start"},
            {"step_id": "step-2", "event": "end"},
        ]
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text("\n".join(json.dumps(r) for r in records))

        result = load_trace_pack(trace_path)

        assert len(result) == 2
        assert result[0]["step_id"] == "step-1"

    def test_load_trace_pack_mixed_step_fields(self, tmp_path: Path) -> None:
        """Verify trace pack with mixed step/step_id loads correctly."""
        records = [
            {"step": 1, "event": "start"},
            {"step_id": "mid", "event": "process"},
            {"step": 3, "event": "end"},
        ]
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text("\n".join(json.dumps(r) for r in records))

        result = load_trace_pack(trace_path)

        assert len(result) == 3

    def test_load_trace_pack_with_extra_fields(self, tmp_path: Path) -> None:
        """Verify trace records with extra fields load correctly."""
        records = [
            {
                "step": 1,
                "event": "test",
                "extra": "allowed",
                "nested": {"data": True},
            },
        ]
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text(json.dumps(records[0]))

        result = load_trace_pack(trace_path)

        assert result[0]["extra"] == "allowed"
        assert result[0]["nested"]["data"] is True

    def test_load_trace_pack_skips_empty_lines(self, tmp_path: Path) -> None:
        """Verify empty lines are skipped."""
        content = '{"step": 1}\n\n{"step": 2}\n   \n{"step": 3}'
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text(content)

        result = load_trace_pack(trace_path)

        assert len(result) == 3

    def test_load_existing_fixture_trace_pack(self) -> None:
        """Verify existing fixture trace pack can be loaded."""
        trace_path = FIXTURES_DIR / "trace_pack_with_metadata.jsonl"
        if not trace_path.exists():
            pytest.skip("Fixture not available")

        result = load_trace_pack(trace_path)

        assert len(result) > 0

    def test_load_trace_pack_file_not_found(self, tmp_path: Path) -> None:
        """Verify FileNotFoundError for missing file."""
        nonexistent = tmp_path / "does_not_exist.jsonl"

        with pytest.raises(FileNotFoundError, match="Trace pack not found"):
            load_trace_pack(nonexistent)

    def test_load_trace_pack_invalid_json(self, tmp_path: Path) -> None:
        """Verify TracePackValidationError for invalid JSON."""
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text('{"step": 1}\n{invalid json}\n{"step": 3}')

        with pytest.raises(TracePackValidationError, match="Invalid JSON on line 2"):
            load_trace_pack(trace_path)

    def test_load_trace_pack_not_object(self, tmp_path: Path) -> None:
        """Verify TracePackValidationError for non-object record."""
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text('{"step": 1}\n["array"]\n{"step": 3}')

        with pytest.raises(TracePackValidationError, match="must be a JSON object"):
            load_trace_pack(trace_path)

    def test_load_trace_pack_missing_step(self, tmp_path: Path) -> None:
        """Verify TracePackValidationError for missing step/step_id."""
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text('{"step": 1}\n{"event": "no_step"}\n{"step": 3}')

        with pytest.raises(TracePackValidationError, match="step.*step_id.*line 2"):
            load_trace_pack(trace_path)

    def test_load_trace_pack_empty_file(self, tmp_path: Path) -> None:
        """Verify empty file returns empty list."""
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text("")

        result = load_trace_pack(trace_path)

        assert result == []


# =============================================================================
# HASH ARTIFACT TESTS
# =============================================================================


class TestHashArtifact:
    """Test artifact hashing."""

    def test_hash_artifact_returns_sha256(self, tmp_path: Path) -> None:
        """Verify hash is SHA256 hex digest."""
        artifact = tmp_path / "test.txt"
        artifact.write_text("test content")

        result = hash_artifact(artifact)

        assert len(result) == 64  # SHA256 hex is 64 chars
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_artifact_deterministic(self, tmp_path: Path) -> None:
        """Verify same content produces same hash."""
        artifact = tmp_path / "test.txt"
        artifact.write_text("deterministic content")

        hash1 = hash_artifact(artifact)
        hash2 = hash_artifact(artifact)
        hash3 = hash_artifact(artifact)

        assert hash1 == hash2 == hash3

    def test_hash_artifact_different_content(self, tmp_path: Path) -> None:
        """Verify different content produces different hash."""
        artifact1 = tmp_path / "test1.txt"
        artifact1.write_text("content one")

        artifact2 = tmp_path / "test2.txt"
        artifact2.write_text("content two")

        hash1 = hash_artifact(artifact1)
        hash2 = hash_artifact(artifact2)

        assert hash1 != hash2

    def test_hash_artifact_file_not_found(self, tmp_path: Path) -> None:
        """Verify FileNotFoundError for missing file."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with pytest.raises(FileNotFoundError, match="Artifact not found"):
            hash_artifact(nonexistent)

    def test_hash_artifact_binary_file(self, tmp_path: Path) -> None:
        """Verify binary files can be hashed."""
        artifact = tmp_path / "binary.bin"
        artifact.write_bytes(bytes(range(256)))

        result = hash_artifact(artifact)

        assert len(result) == 64

    def test_hash_artifact_empty_file(self, tmp_path: Path) -> None:
        """Verify empty files can be hashed."""
        artifact = tmp_path / "empty.txt"
        artifact.write_text("")

        result = hash_artifact(artifact)

        # SHA256 of empty string is known
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result == expected

    def test_hash_artifact_json_file(self, tmp_path: Path) -> None:
        """Verify JSON files can be hashed correctly."""
        artifact = tmp_path / "manifest.json"
        artifact.write_text('{"key": "value"}')

        result = hash_artifact(artifact)

        assert len(result) == 64

    def test_hash_artifact_stability_across_runs(self, tmp_path: Path) -> None:
        """Verify hash stability across multiple reads."""
        artifact = tmp_path / "stable.txt"
        content = "This content should hash consistently"
        artifact.write_text(content)

        hashes = [hash_artifact(artifact) for _ in range(10)]

        assert all(h == hashes[0] for h in hashes)

    def test_hash_artifact_unicode_content(self, tmp_path: Path) -> None:
        """Verify Unicode content hashes correctly."""
        artifact = tmp_path / "unicode.txt"
        artifact.write_text("日本語 🎉 émoji", encoding="utf-8")

        result = hash_artifact(artifact)

        assert len(result) == 64


# =============================================================================
# VALIDATION HELPER TESTS
# =============================================================================


class TestValidationHelpers:
    """Test validation helper functions."""

    def test_validate_manifest_schema_valid(self) -> None:
        """Verify valid manifest passes schema check."""
        manifest = {
            "run_id": "test",
            "timestamp": "2026-01-01",
            "seed": 42,
            "artifacts": [],
        }

        assert validate_manifest_schema(manifest) is True

    def test_validate_manifest_schema_missing_field(self) -> None:
        """Verify missing field fails schema check."""
        manifest = {
            "run_id": "test",
            "timestamp": "2026-01-01",
            # Missing seed and artifacts
        }

        assert validate_manifest_schema(manifest) is False

    def test_validate_trace_record_with_step(self) -> None:
        """Verify record with step passes validation."""
        record = {"step": 1, "event": "test"}

        assert validate_trace_record(record) is True

    def test_validate_trace_record_with_step_id(self) -> None:
        """Verify record with step_id passes validation."""
        record = {"step_id": "step-1", "event": "test"}

        assert validate_trace_record(record) is True

    def test_validate_trace_record_with_both(self) -> None:
        """Verify record with both step and step_id passes validation."""
        record = {"step": 1, "step_id": "step-1", "event": "test"}

        assert validate_trace_record(record) is True

    def test_validate_trace_record_missing_step(self) -> None:
        """Verify record without step/step_id fails validation."""
        record = {"event": "test", "data": "no step field"}

        assert validate_trace_record(record) is False


# =============================================================================
# CONSTANTS TESTS
# =============================================================================


class TestConstants:
    """Test module constants."""

    def test_manifest_required_fields_immutable(self) -> None:
        """Verify MANIFEST_REQUIRED_FIELDS is a frozenset."""
        assert isinstance(MANIFEST_REQUIRED_FIELDS, frozenset)

    def test_manifest_required_fields_contents(self) -> None:
        """Verify required fields per M03 specification."""
        assert "run_id" in MANIFEST_REQUIRED_FIELDS
        assert "timestamp" in MANIFEST_REQUIRED_FIELDS
        assert "seed" in MANIFEST_REQUIRED_FIELDS
        assert "artifacts" in MANIFEST_REQUIRED_FIELDS
        assert len(MANIFEST_REQUIRED_FIELDS) == 4


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests combining loading and hashing."""

    def test_load_and_hash_manifest(self, tmp_path: Path) -> None:
        """Verify manifest can be loaded and hashed."""
        manifest_data = {
            "run_id": "test",
            "timestamp": "2026-01-01",
            "seed": 42,
            "artifacts": [],
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data, sort_keys=True))

        # Load and validate
        loaded = load_manifest(manifest_path)
        assert loaded["run_id"] == "test"

        # Hash the file
        file_hash = hash_artifact(manifest_path)
        assert len(file_hash) == 64

    def test_load_and_hash_trace_pack(self, tmp_path: Path) -> None:
        """Verify trace pack can be loaded and hashed."""
        records = [
            {"step": 1, "event": "start"},
            {"step": 2, "event": "end"},
        ]
        trace_path = tmp_path / "trace_pack.jsonl"
        trace_path.write_text("\n".join(json.dumps(r) for r in records))

        # Load and validate
        loaded = load_trace_pack(trace_path)
        assert len(loaded) == 2

        # Hash the file
        file_hash = hash_artifact(trace_path)
        assert len(file_hash) == 64

