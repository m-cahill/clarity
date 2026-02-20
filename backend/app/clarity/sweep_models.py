"""Sweep Models for CLARITY.

This module defines the core data structures for the sweep orchestrator.
All models are frozen dataclasses to ensure immutability and determinism.

CRITICAL CONSTRAINTS (M04):
1. All models must be immutable (frozen=True).
2. No randomness, no datetime.now, no uuid.
3. Validation fails fast at construction time.
4. Axis value encoding must be deterministic and OS-safe.

These models are isolated from the M01 SweepManifest.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SweepConfigValidationError(ValueError):
    """Raised when SweepConfig validation fails.

    This error indicates invalid configuration such as:
    - Duplicate axis names
    - Empty axes tuple
    - Empty axis values
    - Empty seeds tuple
    """

    pass


@dataclass(frozen=True)
class SweepAxis:
    """A single perturbation axis for a sweep.

    Each axis defines a named dimension with a tuple of values to sweep over.
    The axis is immutable after creation.

    Attributes:
        name: The canonical name of the axis (e.g., "brightness", "contrast").
              Must be non-empty and contain only alphanumeric characters and underscores.
        values: Tuple of values to sweep over. Must be non-empty.
                Values can be any type that is JSON-serializable.

    Example:
        >>> brightness = SweepAxis(name="brightness", values=(0.8, 1.0, 1.2))
        >>> contrast = SweepAxis(name="contrast", values=(0.9, 1.0, 1.1))
    """

    name: str
    values: tuple[Any, ...]

    def __post_init__(self) -> None:
        """Validate axis constraints at construction time."""
        if not self.name:
            raise SweepConfigValidationError("Axis name must not be empty")

        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", self.name):
            raise SweepConfigValidationError(
                f"Axis name must be alphanumeric with underscores, "
                f"starting with a letter: '{self.name}'"
            )

        if not self.values:
            raise SweepConfigValidationError(
                f"Axis '{self.name}' must have at least one value"
            )


@dataclass(frozen=True)
class SweepConfig:
    """Configuration for a perturbation sweep.

    Defines the complete specification for a sweep run, including:
    - Base spec file path
    - Perturbation axes to sweep
    - Seeds for reproducibility
    - Model adapter to use

    All validation occurs at construction time (fail fast).

    Attributes:
        base_spec_path: Path to the base spec JSON file. Will be loaded,
                        modified, and written to each run directory.
        axes: Tuple of SweepAxis objects defining perturbation dimensions.
              Must be non-empty. No duplicate axis names allowed.
        seeds: Tuple of integer seeds for reproducibility. Must be non-empty.
        adapter: Name of the model adapter to use for R2L invocation.

    Example:
        >>> config = SweepConfig(
        ...     base_spec_path=Path("specs/base.json"),
        ...     axes=(
        ...         SweepAxis(name="brightness", values=(0.8, 1.0, 1.2)),
        ...         SweepAxis(name="contrast", values=(0.9, 1.1)),
        ...     ),
        ...     seeds=(42, 43, 44),
        ...     adapter="medgemma",
        ... )
    """

    base_spec_path: Path
    axes: tuple[SweepAxis, ...]
    seeds: tuple[int, ...]
    adapter: str

    def __post_init__(self) -> None:
        """Validate configuration constraints at construction time."""
        # Validate axes not empty
        if not self.axes:
            raise SweepConfigValidationError("axes must not be empty")

        # Validate no duplicate axis names
        axis_names = [axis.name for axis in self.axes]
        if len(axis_names) != len(set(axis_names)):
            duplicates = [name for name in axis_names if axis_names.count(name) > 1]
            raise SweepConfigValidationError(
                f"Duplicate axis names not allowed: {sorted(set(duplicates))}"
            )

        # Validate seeds not empty
        if not self.seeds:
            raise SweepConfigValidationError("seeds must not be empty")

        # Validate adapter not empty
        if not self.adapter or not self.adapter.strip():
            raise SweepConfigValidationError("adapter must not be empty")

    def total_runs(self) -> int:
        """Calculate total number of runs in this sweep.

        Returns:
            Product of all axis value counts times number of seeds.
        """
        axis_product = 1
        for axis in self.axes:
            axis_product *= len(axis.values)
        return axis_product * len(self.seeds)


@dataclass(frozen=True)
class SweepRunRecord:
    """Record of a single run within a sweep.

    Immutable metadata record for one R2L invocation within a sweep.
    Contains the axis values used, seed, output location, and manifest hash.

    Attributes:
        axis_values: Dictionary mapping axis names to their values for this run.
        seed: The seed used for this run.
        output_dir: Path to the directory containing run artifacts.
        manifest_hash: SHA256 hash of the manifest.json file.

    Example:
        >>> record = SweepRunRecord(
        ...     axis_values={"brightness": 0.8, "contrast": 1.0},
        ...     seed=42,
        ...     output_dir=Path("sweep_output/runs/brightness=0p8_contrast=1p0_seed=42"),
        ...     manifest_hash="abc123...",
        ... )
    """

    axis_values: dict[str, Any]
    seed: int
    output_dir: Path
    manifest_hash: str


def encode_axis_value(value: Any) -> str:
    """Encode an axis value for use in directory names.

    Applies deterministic encoding rules:
    1. Convert to string via str(value)
    2. Replace "." with "p"
    3. Replace "-" with "m"
    4. Remove spaces
    5. Keep only [a-zA-Z0-9_]

    Args:
        value: The axis value to encode.

    Returns:
        OS-safe, deterministic string representation.

    Examples:
        >>> encode_axis_value(0.8)
        '0p8'
        >>> encode_axis_value(-0.25)
        'm0p25'
        >>> encode_axis_value("high")
        'high'
        >>> encode_axis_value(42)
        '42'
    """
    # Convert to string
    s = str(value)

    # Apply replacements
    s = s.replace(".", "p")
    s = s.replace("-", "m")
    s = s.replace(" ", "")

    # Filter to allowed characters only
    s = re.sub(r"[^a-zA-Z0-9_]", "", s)

    return s


def build_run_directory_name(axis_values: dict[str, Any], seed: int) -> str:
    """Build a deterministic directory name for a sweep run.

    Creates a directory name from axis values and seed in a deterministic,
    OS-safe format. Axis names are sorted alphabetically for consistent ordering.

    Format: axis1=value1_axis2=value2_..._seed=N

    Args:
        axis_values: Dictionary mapping axis names to values.
        seed: The seed for this run.

    Returns:
        Deterministic directory name string.

    Example:
        >>> build_run_directory_name({"brightness": 0.8, "contrast": 1.0}, 42)
        'brightness=0p8_contrast=1p0_seed=42'
    """
    # Sort axis names alphabetically for deterministic ordering
    segments = []
    for name in sorted(axis_values.keys()):
        encoded_value = encode_axis_value(axis_values[name])
        segments.append(f"{name}={encoded_value}")

    # Append seed
    segments.append(f"seed={seed}")

    return "_".join(segments)

