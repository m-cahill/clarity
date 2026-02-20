"""Tests for sweep_models.py.

This test module validates the sweep data structures including:
- SweepAxis immutability and validation
- SweepConfig validation (duplicates, empty axes, empty seeds)
- SweepRunRecord immutability
- Axis value encoding for directory names
- Run directory name generation

Coverage target: ≥95%
"""

from pathlib import Path

import pytest

from app.clarity.sweep_models import (
    SweepAxis,
    SweepConfig,
    SweepConfigValidationError,
    SweepRunRecord,
    build_run_directory_name,
    encode_axis_value,
)


# =============================================================================
# SweepAxis Tests
# =============================================================================


class TestSweepAxis:
    """Tests for SweepAxis dataclass."""

    def test_valid_axis_creation(self) -> None:
        """Test creating a valid SweepAxis."""
        axis = SweepAxis(name="brightness", values=(0.8, 1.0, 1.2))
        assert axis.name == "brightness"
        assert axis.values == (0.8, 1.0, 1.2)

    def test_axis_with_single_value(self) -> None:
        """Test axis with single value is valid."""
        axis = SweepAxis(name="contrast", values=(1.0,))
        assert len(axis.values) == 1

    def test_axis_with_string_values(self) -> None:
        """Test axis with string values."""
        axis = SweepAxis(name="mode", values=("low", "medium", "high"))
        assert axis.values == ("low", "medium", "high")

    def test_axis_with_mixed_types(self) -> None:
        """Test axis with mixed value types."""
        axis = SweepAxis(name="param", values=(1, 2.5, "auto"))
        assert len(axis.values) == 3

    def test_axis_immutability(self) -> None:
        """Test that SweepAxis is frozen (immutable)."""
        axis = SweepAxis(name="brightness", values=(0.8, 1.0))
        with pytest.raises(AttributeError):
            axis.name = "contrast"  # type: ignore

    def test_axis_empty_name_raises(self) -> None:
        """Test that empty axis name raises SweepConfigValidationError."""
        with pytest.raises(SweepConfigValidationError, match="name must not be empty"):
            SweepAxis(name="", values=(1.0,))

    def test_axis_invalid_name_format_raises(self) -> None:
        """Test that invalid axis name format raises error."""
        with pytest.raises(SweepConfigValidationError, match="alphanumeric"):
            SweepAxis(name="123invalid", values=(1.0,))

    def test_axis_name_with_spaces_raises(self) -> None:
        """Test that axis name with spaces raises error."""
        with pytest.raises(SweepConfigValidationError, match="alphanumeric"):
            SweepAxis(name="axis name", values=(1.0,))

    def test_axis_name_with_hyphen_raises(self) -> None:
        """Test that axis name with hyphen raises error."""
        with pytest.raises(SweepConfigValidationError, match="alphanumeric"):
            SweepAxis(name="axis-name", values=(1.0,))

    def test_axis_name_with_underscore_valid(self) -> None:
        """Test that axis name with underscore is valid."""
        axis = SweepAxis(name="axis_name", values=(1.0,))
        assert axis.name == "axis_name"

    def test_axis_empty_values_raises(self) -> None:
        """Test that empty values tuple raises SweepConfigValidationError."""
        with pytest.raises(SweepConfigValidationError, match="at least one value"):
            SweepAxis(name="brightness", values=())

    def test_axis_hashable(self) -> None:
        """Test that SweepAxis is hashable (can be used in sets)."""
        axis1 = SweepAxis(name="brightness", values=(0.8, 1.0))
        axis2 = SweepAxis(name="brightness", values=(0.8, 1.0))
        assert hash(axis1) == hash(axis2)
        assert axis1 == axis2

    def test_axis_equality(self) -> None:
        """Test SweepAxis equality comparison."""
        axis1 = SweepAxis(name="brightness", values=(0.8, 1.0))
        axis2 = SweepAxis(name="brightness", values=(0.8, 1.0))
        axis3 = SweepAxis(name="contrast", values=(0.8, 1.0))
        assert axis1 == axis2
        assert axis1 != axis3


# =============================================================================
# SweepConfig Tests
# =============================================================================


class TestSweepConfig:
    """Tests for SweepConfig dataclass."""

    @pytest.fixture
    def valid_axes(self) -> tuple[SweepAxis, ...]:
        """Fixture providing valid axes."""
        return (
            SweepAxis(name="brightness", values=(0.8, 1.0, 1.2)),
            SweepAxis(name="contrast", values=(0.9, 1.1)),
        )

    def test_valid_config_creation(self, valid_axes: tuple[SweepAxis, ...]) -> None:
        """Test creating a valid SweepConfig."""
        config = SweepConfig(
            base_spec_path=Path("specs/base.json"),
            axes=valid_axes,
            seeds=(42, 43, 44),
            adapter="medgemma",
        )
        assert config.base_spec_path == Path("specs/base.json")
        assert len(config.axes) == 2
        assert config.seeds == (42, 43, 44)
        assert config.adapter == "medgemma"

    def test_config_immutability(self, valid_axes: tuple[SweepAxis, ...]) -> None:
        """Test that SweepConfig is frozen (immutable)."""
        config = SweepConfig(
            base_spec_path=Path("specs/base.json"),
            axes=valid_axes,
            seeds=(42,),
            adapter="medgemma",
        )
        with pytest.raises(AttributeError):
            config.adapter = "other"  # type: ignore

    def test_config_empty_axes_raises(self) -> None:
        """Test that empty axes tuple raises SweepConfigValidationError."""
        with pytest.raises(SweepConfigValidationError, match="axes must not be empty"):
            SweepConfig(
                base_spec_path=Path("specs/base.json"),
                axes=(),
                seeds=(42,),
                adapter="medgemma",
            )

    def test_config_duplicate_axis_names_raises(self) -> None:
        """Test that duplicate axis names raise SweepConfigValidationError."""
        with pytest.raises(SweepConfigValidationError, match="Duplicate axis names"):
            SweepConfig(
                base_spec_path=Path("specs/base.json"),
                axes=(
                    SweepAxis(name="brightness", values=(0.8, 1.0)),
                    SweepAxis(name="brightness", values=(0.9, 1.1)),
                ),
                seeds=(42,),
                adapter="medgemma",
            )

    def test_config_empty_seeds_raises(self) -> None:
        """Test that empty seeds tuple raises SweepConfigValidationError."""
        with pytest.raises(SweepConfigValidationError, match="seeds must not be empty"):
            SweepConfig(
                base_spec_path=Path("specs/base.json"),
                axes=(SweepAxis(name="brightness", values=(0.8, 1.0)),),
                seeds=(),
                adapter="medgemma",
            )

    def test_config_empty_adapter_raises(self) -> None:
        """Test that empty adapter raises SweepConfigValidationError."""
        with pytest.raises(SweepConfigValidationError, match="adapter must not be empty"):
            SweepConfig(
                base_spec_path=Path("specs/base.json"),
                axes=(SweepAxis(name="brightness", values=(0.8, 1.0)),),
                seeds=(42,),
                adapter="",
            )

    def test_config_whitespace_adapter_raises(self) -> None:
        """Test that whitespace-only adapter raises SweepConfigValidationError."""
        with pytest.raises(SweepConfigValidationError, match="adapter must not be empty"):
            SweepConfig(
                base_spec_path=Path("specs/base.json"),
                axes=(SweepAxis(name="brightness", values=(0.8, 1.0)),),
                seeds=(42,),
                adapter="   ",
            )

    def test_config_total_runs_single_axis(self) -> None:
        """Test total_runs calculation with single axis."""
        config = SweepConfig(
            base_spec_path=Path("specs/base.json"),
            axes=(SweepAxis(name="brightness", values=(0.8, 1.0, 1.2)),),
            seeds=(42, 43),
            adapter="medgemma",
        )
        # 3 values × 2 seeds = 6 runs
        assert config.total_runs() == 6

    def test_config_total_runs_multiple_axes(
        self, valid_axes: tuple[SweepAxis, ...]
    ) -> None:
        """Test total_runs calculation with multiple axes."""
        config = SweepConfig(
            base_spec_path=Path("specs/base.json"),
            axes=valid_axes,  # 3 brightness × 2 contrast
            seeds=(42, 43, 44),  # 3 seeds
            adapter="medgemma",
        )
        # 3 × 2 × 3 = 18 runs
        assert config.total_runs() == 18

    def test_config_hashable(self, valid_axes: tuple[SweepAxis, ...]) -> None:
        """Test that SweepConfig is hashable."""
        config = SweepConfig(
            base_spec_path=Path("specs/base.json"),
            axes=valid_axes,
            seeds=(42,),
            adapter="medgemma",
        )
        # Should not raise
        hash(config)


# =============================================================================
# SweepRunRecord Tests
# =============================================================================


class TestSweepRunRecord:
    """Tests for SweepRunRecord dataclass."""

    def test_valid_record_creation(self) -> None:
        """Test creating a valid SweepRunRecord."""
        record = SweepRunRecord(
            axis_values={"brightness": 0.8, "contrast": 1.0},
            seed=42,
            output_dir=Path("sweep_output/runs/brightness=0p8_contrast=1p0_seed=42"),
            manifest_hash="abc123def456",
        )
        assert record.axis_values == {"brightness": 0.8, "contrast": 1.0}
        assert record.seed == 42
        assert record.manifest_hash == "abc123def456"

    def test_record_immutability(self) -> None:
        """Test that SweepRunRecord is frozen (immutable)."""
        record = SweepRunRecord(
            axis_values={"brightness": 0.8},
            seed=42,
            output_dir=Path("output"),
            manifest_hash="abc123",
        )
        with pytest.raises(AttributeError):
            record.seed = 43  # type: ignore

    def test_record_equality(self) -> None:
        """Test SweepRunRecord equality comparison."""
        record1 = SweepRunRecord(
            axis_values={"brightness": 0.8},
            seed=42,
            output_dir=Path("output"),
            manifest_hash="abc123",
        )
        record2 = SweepRunRecord(
            axis_values={"brightness": 0.8},
            seed=42,
            output_dir=Path("output"),
            manifest_hash="abc123",
        )
        assert record1 == record2


# =============================================================================
# encode_axis_value Tests
# =============================================================================


class TestEncodeAxisValue:
    """Tests for encode_axis_value function."""

    def test_encode_positive_float(self) -> None:
        """Test encoding positive float."""
        assert encode_axis_value(0.8) == "0p8"
        assert encode_axis_value(1.0) == "1p0"
        assert encode_axis_value(1.25) == "1p25"

    def test_encode_negative_float(self) -> None:
        """Test encoding negative float."""
        assert encode_axis_value(-0.25) == "m0p25"
        assert encode_axis_value(-1.0) == "m1p0"

    def test_encode_integer(self) -> None:
        """Test encoding integer."""
        assert encode_axis_value(42) == "42"
        assert encode_axis_value(0) == "0"
        assert encode_axis_value(-1) == "m1"

    def test_encode_string_simple(self) -> None:
        """Test encoding simple string."""
        assert encode_axis_value("high") == "high"
        assert encode_axis_value("low") == "low"

    def test_encode_string_with_spaces(self) -> None:
        """Test encoding string with spaces (spaces removed)."""
        assert encode_axis_value("high quality") == "highquality"

    def test_encode_string_with_underscore(self) -> None:
        """Test encoding string with underscore (preserved)."""
        assert encode_axis_value("high_quality") == "high_quality"

    def test_encode_removes_special_characters(self) -> None:
        """Test that special characters are removed."""
        assert encode_axis_value("test@value") == "testvalue"
        assert encode_axis_value("test!value") == "testvalue"
        assert encode_axis_value("test/value") == "testvalue"

    def test_encode_deterministic(self) -> None:
        """Test that encoding is deterministic."""
        value = 0.8
        result1 = encode_axis_value(value)
        result2 = encode_axis_value(value)
        result3 = encode_axis_value(value)
        assert result1 == result2 == result3 == "0p8"


# =============================================================================
# build_run_directory_name Tests
# =============================================================================


class TestBuildRunDirectoryName:
    """Tests for build_run_directory_name function."""

    def test_single_axis(self) -> None:
        """Test directory name with single axis."""
        name = build_run_directory_name({"brightness": 0.8}, seed=42)
        assert name == "brightness=0p8_seed=42"

    def test_multiple_axes_alphabetical_order(self) -> None:
        """Test that axes are sorted alphabetically."""
        name = build_run_directory_name(
            {"contrast": 1.0, "brightness": 0.8}, seed=42
        )
        # brightness comes before contrast alphabetically
        assert name == "brightness=0p8_contrast=1p0_seed=42"

    def test_three_axes(self) -> None:
        """Test directory name with three axes."""
        name = build_run_directory_name(
            {"zoom": 1.5, "brightness": 0.8, "contrast": 1.0}, seed=42
        )
        assert name == "brightness=0p8_contrast=1p0_zoom=1p5_seed=42"

    def test_negative_values(self) -> None:
        """Test directory name with negative values."""
        name = build_run_directory_name({"offset": -0.25}, seed=42)
        assert name == "offset=m0p25_seed=42"

    def test_string_values(self) -> None:
        """Test directory name with string values."""
        name = build_run_directory_name({"mode": "high"}, seed=42)
        assert name == "mode=high_seed=42"

    def test_deterministic(self) -> None:
        """Test that directory naming is deterministic."""
        axis_values = {"brightness": 0.8, "contrast": 1.0}
        seed = 42
        name1 = build_run_directory_name(axis_values, seed)
        name2 = build_run_directory_name(axis_values, seed)
        name3 = build_run_directory_name(axis_values, seed)
        assert name1 == name2 == name3

    def test_different_seeds_different_names(self) -> None:
        """Test that different seeds produce different directory names."""
        axis_values = {"brightness": 0.8}
        name1 = build_run_directory_name(axis_values, seed=42)
        name2 = build_run_directory_name(axis_values, seed=43)
        assert name1 != name2
        assert "seed=42" in name1
        assert "seed=43" in name2

    def test_no_os_unsafe_characters(self) -> None:
        """Test that directory names contain no OS-unsafe characters."""
        name = build_run_directory_name(
            {"brightness": 0.8, "contrast": -0.25}, seed=42
        )
        # Should only contain alphanumeric, underscore, equals
        import re
        assert re.match(r"^[a-zA-Z0-9_=]+$", name)
        # No dots, hyphens, spaces, slashes
        assert "." not in name
        assert "-" not in name
        assert " " not in name
        assert "/" not in name
        assert "\\" not in name


# =============================================================================
# Integration Tests
# =============================================================================


class TestSweepModelsIntegration:
    """Integration tests for sweep models working together."""

    def test_config_with_directory_naming(self) -> None:
        """Test that config axes work with directory naming."""
        config = SweepConfig(
            base_spec_path=Path("specs/base.json"),
            axes=(
                SweepAxis(name="brightness", values=(0.8, 1.0)),
                SweepAxis(name="contrast", values=(0.9, 1.1)),
            ),
            seeds=(42, 43),
            adapter="medgemma",
        )

        # Generate directory names for all combinations
        names = set()
        for brightness in config.axes[0].values:
            for contrast in config.axes[1].values:
                for seed in config.seeds:
                    name = build_run_directory_name(
                        {"brightness": brightness, "contrast": contrast},
                        seed=seed,
                    )
                    names.add(name)

        # Should have no collisions
        assert len(names) == config.total_runs()

    def test_record_creation_from_config(self) -> None:
        """Test creating records from config values."""
        config = SweepConfig(
            base_spec_path=Path("specs/base.json"),
            axes=(SweepAxis(name="brightness", values=(0.8,)),),
            seeds=(42,),
            adapter="medgemma",
        )

        axis_values = {"brightness": 0.8}
        seed = 42
        dir_name = build_run_directory_name(axis_values, seed)

        record = SweepRunRecord(
            axis_values=axis_values,
            seed=seed,
            output_dir=Path(f"output/runs/{dir_name}"),
            manifest_hash="abc123",
        )

        assert record.axis_values["brightness"] == 0.8
        assert str(record.output_dir).endswith(dir_name)

