"""Tests for Counterfactual Engine (M08).

This test module provides comprehensive coverage for counterfactual probing
capabilities including:

1. RegionMask Generation (grid masks, determinism, boundaries)
2. Image Masking (apply_mask, fill values, coordinate conversion)
3. Basic Delta Correctness (probe results, delta computation)
4. Determinism (double-run, different engines, ordering)
5. Region ID Stability (same ID same result, different ID different result)
6. Error Handling (invalid inputs, empty results)
7. Integration (full probe pipeline)
8. Serialization (to_dict, sorted keys, determinism)
9. Dataclasses (equality, hashability, frozen)
10. Guardrails (no subprocess, no r2l, no random, no datetime, no uuid)

Target: 50-65 tests minimum.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from app.clarity.counterfactual_engine import (
    CounterfactualComputationError,
    CounterfactualEngine,
    CounterfactualProbe,
    MASK_FILL_VALUE,
    ProbeResult,
    ProbeSurface,
    RegionMask,
    _round8,
    apply_mask,
    compute_probe_result,
    compute_probe_surface,
    generate_grid_masks,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def engine() -> CounterfactualEngine:
    """Create a CounterfactualEngine instance."""
    return CounterfactualEngine()


@pytest.fixture
def sample_image() -> Image.Image:
    """Create a sample RGB image for testing."""
    # Create a 100x100 white image
    return Image.new("RGB", (100, 100), (255, 255, 255))


@pytest.fixture
def colored_image() -> Image.Image:
    """Create a colored image with distinct regions."""
    img = Image.new("RGB", (90, 90), (255, 0, 0))  # Red background
    # Add some variety
    for x in range(30, 60):
        for y in range(30, 60):
            img.putpixel((x, y), (0, 255, 0))  # Green center
    return img


@pytest.fixture
def sample_mask() -> RegionMask:
    """Create a sample RegionMask."""
    return RegionMask(
        region_id="grid_r0_c0_k3",
        row=0,
        col=0,
        grid_size=3,
        x_min=0.0,
        y_min=0.0,
        x_max=0.33333333,
        y_max=0.33333333,
    )


@pytest.fixture
def sample_probe() -> CounterfactualProbe:
    """Create a sample CounterfactualProbe."""
    return CounterfactualProbe(
        region_id="grid_r0_c0_k3",
        axis="brightness",
        value="1p0",
    )


@pytest.fixture
def sample_result(sample_probe: CounterfactualProbe) -> ProbeResult:
    """Create a sample ProbeResult."""
    return ProbeResult(
        probe=sample_probe,
        baseline_esi=0.8,
        masked_esi=0.5,
        delta_esi=-0.3,
        baseline_drift=0.1,
        masked_drift=0.25,
        delta_drift=0.15,
    )


# =============================================================================
# 1. RegionMask Generation Tests
# =============================================================================


class TestRegionMaskGeneration:
    """Tests for grid mask generation."""

    def test_generate_3x3_grid_produces_9_masks(self) -> None:
        """3×3 grid produces exactly 9 region masks."""
        masks = generate_grid_masks(3)
        assert len(masks) == 9

    def test_generate_4x4_grid_produces_16_masks(self) -> None:
        """4×4 grid produces exactly 16 region masks."""
        masks = generate_grid_masks(4)
        assert len(masks) == 16

    def test_generate_1x1_grid_produces_1_mask(self) -> None:
        """1×1 grid produces exactly 1 region mask covering entire image."""
        masks = generate_grid_masks(1)
        assert len(masks) == 1
        assert masks[0].x_min == 0.0
        assert masks[0].y_min == 0.0
        assert masks[0].x_max == 1.0
        assert masks[0].y_max == 1.0

    def test_generate_2x2_grid_produces_4_masks(self) -> None:
        """2×2 grid produces exactly 4 region masks."""
        masks = generate_grid_masks(2)
        assert len(masks) == 4

    def test_region_ids_are_deterministic(self) -> None:
        """Region IDs follow deterministic naming pattern."""
        masks = generate_grid_masks(3)
        expected_ids = [
            "grid_r0_c0_k3", "grid_r0_c1_k3", "grid_r0_c2_k3",
            "grid_r1_c0_k3", "grid_r1_c1_k3", "grid_r1_c2_k3",
            "grid_r2_c0_k3", "grid_r2_c1_k3", "grid_r2_c2_k3",
        ]
        assert [m.region_id for m in masks] == expected_ids

    def test_region_ids_are_unique(self) -> None:
        """All region IDs within a grid are unique."""
        masks = generate_grid_masks(4)
        ids = [m.region_id for m in masks]
        assert len(ids) == len(set(ids))

    def test_masks_cover_full_image(self) -> None:
        """Grid masks collectively cover [0,1] × [0,1]."""
        masks = generate_grid_masks(3)

        # Check corners
        x_mins = [m.x_min for m in masks]
        y_mins = [m.y_min for m in masks]
        x_maxs = [m.x_max for m in masks]
        y_maxs = [m.y_max for m in masks]

        assert min(x_mins) == 0.0
        assert min(y_mins) == 0.0
        assert max(x_maxs) == 1.0
        assert max(y_maxs) == 1.0

    def test_masks_do_not_overlap(self) -> None:
        """Grid masks do not overlap (boundaries are shared but interior is disjoint)."""
        masks = generate_grid_masks(3)

        # Each cell should have unique (row, col)
        positions = [(m.row, m.col) for m in masks]
        assert len(positions) == len(set(positions))

    def test_invalid_grid_size_zero_raises_error(self) -> None:
        """Grid size of 0 raises CounterfactualComputationError."""
        with pytest.raises(CounterfactualComputationError, match="grid_size must be >= 1"):
            generate_grid_masks(0)

    def test_invalid_grid_size_negative_raises_error(self) -> None:
        """Negative grid size raises CounterfactualComputationError."""
        with pytest.raises(CounterfactualComputationError, match="grid_size must be >= 1"):
            generate_grid_masks(-1)

    def test_double_generation_produces_identical_masks(self) -> None:
        """Generating masks twice produces identical results."""
        masks1 = generate_grid_masks(3)
        masks2 = generate_grid_masks(3)
        assert masks1 == masks2


# =============================================================================
# 2. Image Masking Tests
# =============================================================================


class TestImageMasking:
    """Tests for image mask application."""

    def test_apply_mask_returns_new_image(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """apply_mask returns a new image, not the original."""
        result = apply_mask(sample_image, sample_mask)
        assert result is not sample_image

    def test_apply_mask_preserves_dimensions(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Masked image has same dimensions as original."""
        result = apply_mask(sample_image, sample_mask)
        assert result.size == sample_image.size

    def test_apply_mask_preserves_mode(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Masked image has same mode as original."""
        result = apply_mask(sample_image, sample_mask)
        assert result.mode == sample_image.mode

    def test_apply_mask_fills_with_default_value(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Mask region is filled with MASK_FILL_VALUE (128) by default."""
        result = apply_mask(sample_image, sample_mask)

        # Sample a pixel in the masked region
        # For 100x100 image with mask x_max=0.33, y_max=0.33
        # Region covers (0,0) to (33,33) pixels
        pixel = result.getpixel((10, 10))
        assert pixel == (MASK_FILL_VALUE, MASK_FILL_VALUE, MASK_FILL_VALUE)

    def test_apply_mask_with_custom_fill_value(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Mask region can be filled with custom value."""
        result = apply_mask(sample_image, sample_mask, fill_value=0)

        pixel = result.getpixel((10, 10))
        assert pixel == (0, 0, 0)

    def test_apply_mask_preserves_unmasked_regions(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Pixels outside the mask region are unchanged."""
        result = apply_mask(sample_image, sample_mask)

        # Sample a pixel outside the masked region
        pixel_original = sample_image.getpixel((50, 50))
        pixel_result = result.getpixel((50, 50))
        assert pixel_original == pixel_result

    def test_apply_mask_is_deterministic(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Applying same mask twice produces identical results."""
        result1 = apply_mask(sample_image, sample_mask)
        result2 = apply_mask(sample_image, sample_mask)

        # Compare pixel by pixel
        for x in range(result1.width):
            for y in range(result1.height):
                assert result1.getpixel((x, y)) == result2.getpixel((x, y))

    def test_apply_mask_to_colored_image(
        self, colored_image: Image.Image
    ) -> None:
        """Mask correctly applied to colored image."""
        mask = RegionMask(
            region_id="grid_r1_c1_k3",
            row=1,
            col=1,
            grid_size=3,
            x_min=0.33333333,
            y_min=0.33333333,
            x_max=0.66666667,
            y_max=0.66666667,
        )
        result = apply_mask(colored_image, mask)

        # Center region should be masked
        # Image is 90x90, center cell covers roughly (30,30) to (60,60)
        pixel = result.getpixel((45, 45))
        assert pixel == (MASK_FILL_VALUE, MASK_FILL_VALUE, MASK_FILL_VALUE)

    def test_apply_mask_none_image_raises_error(self, sample_mask: RegionMask) -> None:
        """apply_mask with None image raises CounterfactualComputationError."""
        with pytest.raises(CounterfactualComputationError, match="Image cannot be None"):
            apply_mask(None, sample_mask)  # type: ignore

    def test_apply_mask_non_rgb_image_raises_error(self, sample_mask: RegionMask) -> None:
        """apply_mask with non-RGB image raises CounterfactualComputationError."""
        grayscale = Image.new("L", (100, 100), 128)
        with pytest.raises(CounterfactualComputationError, match="must be RGB mode"):
            apply_mask(grayscale, sample_mask)

    def test_apply_mask_invalid_fill_value_raises_error(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Invalid fill_value raises CounterfactualComputationError."""
        with pytest.raises(CounterfactualComputationError, match="fill_value must be 0-255"):
            apply_mask(sample_image, sample_mask, fill_value=300)

    def test_apply_mask_invalid_fill_value_negative_raises_error(
        self, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """Negative fill_value raises CounterfactualComputationError."""
        with pytest.raises(CounterfactualComputationError, match="fill_value must be 0-255"):
            apply_mask(sample_image, sample_mask, fill_value=-1)


# =============================================================================
# 3. Basic Delta Correctness Tests
# =============================================================================


class TestBasicDeltaCorrectness:
    """Tests for probe result delta computation."""

    def test_compute_probe_result_positive_delta(self) -> None:
        """Positive delta when masked ESI > baseline."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        result = compute_probe_result(
            probe=probe,
            baseline_esi=0.5,
            baseline_drift=0.1,
            masked_esi=0.8,
            masked_drift=0.3,
        )

        assert result.delta_esi == 0.3
        assert result.delta_drift == 0.2

    def test_compute_probe_result_negative_delta(self) -> None:
        """Negative delta when masked ESI < baseline."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        result = compute_probe_result(
            probe=probe,
            baseline_esi=0.8,
            baseline_drift=0.3,
            masked_esi=0.5,
            masked_drift=0.1,
        )

        assert result.delta_esi == -0.3
        assert result.delta_drift == -0.2

    def test_compute_probe_result_zero_delta(self) -> None:
        """Zero delta when masked equals baseline."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        result = compute_probe_result(
            probe=probe,
            baseline_esi=0.5,
            baseline_drift=0.1,
            masked_esi=0.5,
            masked_drift=0.1,
        )

        assert result.delta_esi == 0.0
        assert result.delta_drift == 0.0

    def test_compute_probe_result_preserves_baseline_values(self) -> None:
        """ProbeResult stores baseline values correctly."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        result = compute_probe_result(
            probe=probe,
            baseline_esi=0.12345678,
            baseline_drift=0.87654321,
            masked_esi=0.5,
            masked_drift=0.3,
        )

        assert result.baseline_esi == 0.12345678
        assert result.baseline_drift == 0.87654321

    def test_compute_probe_result_preserves_masked_values(self) -> None:
        """ProbeResult stores masked values correctly."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        result = compute_probe_result(
            probe=probe,
            baseline_esi=0.5,
            baseline_drift=0.3,
            masked_esi=0.12345678,
            masked_drift=0.87654321,
        )

        assert result.masked_esi == 0.12345678
        assert result.masked_drift == 0.87654321

    def test_compute_probe_result_nan_esi_raises_error(self) -> None:
        """NaN baseline_esi raises CounterfactualComputationError."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        with pytest.raises(CounterfactualComputationError, match="Invalid baseline_esi"):
            compute_probe_result(
                probe=probe,
                baseline_esi=float("nan"),
                baseline_drift=0.1,
                masked_esi=0.5,
                masked_drift=0.1,
            )

    def test_compute_probe_result_inf_drift_raises_error(self) -> None:
        """Infinite masked_drift raises CounterfactualComputationError."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        with pytest.raises(CounterfactualComputationError, match="Invalid masked_drift"):
            compute_probe_result(
                probe=probe,
                baseline_esi=0.5,
                baseline_drift=0.1,
                masked_esi=0.5,
                masked_drift=float("inf"),
            )


# =============================================================================
# 4. Determinism Tests
# =============================================================================


class TestDeterminism:
    """Tests for deterministic computation."""

    def test_generate_masks_deterministic(self) -> None:
        """Generating masks produces identical results."""
        masks1 = generate_grid_masks(3)
        masks2 = generate_grid_masks(3)
        assert masks1 == masks2

    def test_compute_probe_result_deterministic(self) -> None:
        """Computing probe result twice produces identical results."""
        probe = CounterfactualProbe(
            region_id="grid_r0_c0_k3",
            axis="brightness",
            value="1p0",
        )
        result1 = compute_probe_result(
            probe=probe,
            baseline_esi=0.8,
            baseline_drift=0.1,
            masked_esi=0.5,
            masked_drift=0.3,
        )
        result2 = compute_probe_result(
            probe=probe,
            baseline_esi=0.8,
            baseline_drift=0.1,
            masked_esi=0.5,
            masked_drift=0.3,
        )
        assert result1 == result2

    def test_different_engine_instances_produce_same_results(self) -> None:
        """Different CounterfactualEngine instances produce identical results."""
        engine1 = CounterfactualEngine()
        engine2 = CounterfactualEngine()

        masks1 = engine1.generate_masks(3)
        masks2 = engine2.generate_masks(3)

        assert masks1 == masks2

    def test_probe_surface_ordering_is_deterministic(self) -> None:
        """ProbeSurface results are sorted by (region_id, axis, value)."""
        results = [
            ProbeResult(
                probe=CounterfactualProbe("grid_r1_c0_k3", "contrast", "1p0"),
                baseline_esi=0.5, masked_esi=0.4, delta_esi=-0.1,
                baseline_drift=0.1, masked_drift=0.15, delta_drift=0.05,
            ),
            ProbeResult(
                probe=CounterfactualProbe("grid_r0_c0_k3", "brightness", "1p0"),
                baseline_esi=0.6, masked_esi=0.5, delta_esi=-0.1,
                baseline_drift=0.2, masked_drift=0.25, delta_drift=0.05,
            ),
            ProbeResult(
                probe=CounterfactualProbe("grid_r0_c0_k3", "contrast", "1p0"),
                baseline_esi=0.7, masked_esi=0.6, delta_esi=-0.1,
                baseline_drift=0.1, masked_drift=0.15, delta_drift=0.05,
            ),
        ]

        surface = compute_probe_surface(results)

        # Check sorting: grid_r0 before grid_r1, then by axis
        assert surface.results[0].probe.region_id == "grid_r0_c0_k3"
        assert surface.results[0].probe.axis == "brightness"
        assert surface.results[1].probe.region_id == "grid_r0_c0_k3"
        assert surface.results[1].probe.axis == "contrast"
        assert surface.results[2].probe.region_id == "grid_r1_c0_k3"


# =============================================================================
# 5. Region ID Stability Tests
# =============================================================================


class TestRegionIDStability:
    """Tests for region ID consistency."""

    def test_same_region_id_same_mask_geometry(self) -> None:
        """Same region_id always has same geometry."""
        masks1 = generate_grid_masks(3)
        masks2 = generate_grid_masks(3)

        for m1, m2 in zip(masks1, masks2):
            if m1.region_id == m2.region_id:
                assert m1.x_min == m2.x_min
                assert m1.y_min == m2.y_min
                assert m1.x_max == m2.x_max
                assert m1.y_max == m2.y_max

    def test_different_region_ids_different_geometry(self) -> None:
        """Different region_ids have different geometries."""
        masks = generate_grid_masks(3)

        # Get two different masks
        mask1 = masks[0]  # grid_r0_c0_k3
        mask2 = masks[1]  # grid_r0_c1_k3

        assert mask1.region_id != mask2.region_id
        assert mask1.x_min != mask2.x_min or mask1.y_min != mask2.y_min

    def test_region_id_format_validation(self) -> None:
        """Region IDs follow expected format."""
        masks = generate_grid_masks(3)

        for mask in masks:
            assert mask.region_id.startswith("grid_r")
            assert "_c" in mask.region_id
            assert "_k3" in mask.region_id

    def test_region_id_encodes_position(self) -> None:
        """Region ID correctly encodes row, col, grid_size."""
        masks = generate_grid_masks(4)

        for mask in masks:
            expected_id = f"grid_r{mask.row}_c{mask.col}_k{mask.grid_size}"
            assert mask.region_id == expected_id


# =============================================================================
# 6. Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error conditions."""

    def test_empty_results_raises_error(self) -> None:
        """compute_probe_surface with empty list raises error."""
        with pytest.raises(CounterfactualComputationError, match="empty results"):
            compute_probe_surface([])

    def test_engine_probe_single_none_image_raises_error(
        self, engine: CounterfactualEngine, sample_mask: RegionMask
    ) -> None:
        """probe_single with None image raises error."""
        with pytest.raises(CounterfactualComputationError, match="Image cannot be None"):
            engine.probe_single(
                image=None,  # type: ignore
                mask=sample_mask,
                axis="brightness",
                value="1p0",
                baseline_esi=0.5,
                baseline_drift=0.1,
                masked_esi=0.5,
                masked_drift=0.1,
            )

    def test_engine_probe_single_empty_axis_raises_error(
        self, engine: CounterfactualEngine, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """probe_single with empty axis raises error."""
        with pytest.raises(CounterfactualComputationError, match="Axis cannot be empty"):
            engine.probe_single(
                image=sample_image,
                mask=sample_mask,
                axis="",
                value="1p0",
                baseline_esi=0.5,
                baseline_drift=0.1,
                masked_esi=0.5,
                masked_drift=0.1,
            )

    def test_engine_probe_single_empty_value_raises_error(
        self, engine: CounterfactualEngine, sample_image: Image.Image, sample_mask: RegionMask
    ) -> None:
        """probe_single with empty value raises error."""
        with pytest.raises(CounterfactualComputationError, match="Value cannot be empty"):
            engine.probe_single(
                image=sample_image,
                mask=sample_mask,
                axis="brightness",
                value="",
                baseline_esi=0.5,
                baseline_drift=0.1,
                masked_esi=0.5,
                masked_drift=0.1,
            )

    def test_invalid_mask_coordinates_x_raises_error(
        self, sample_image: Image.Image
    ) -> None:
        """Invalid x coordinates raise error."""
        bad_mask = RegionMask(
            region_id="bad",
            row=0,
            col=0,
            grid_size=3,
            x_min=0.5,
            y_min=0.0,
            x_max=0.3,  # x_max < x_min
            y_max=0.5,
        )
        with pytest.raises(CounterfactualComputationError, match="Invalid mask x coordinates"):
            apply_mask(sample_image, bad_mask)

    def test_invalid_mask_coordinates_y_raises_error(
        self, sample_image: Image.Image
    ) -> None:
        """Invalid y coordinates raise error."""
        bad_mask = RegionMask(
            region_id="bad",
            row=0,
            col=0,
            grid_size=3,
            x_min=0.0,
            y_min=0.8,
            x_max=0.5,
            y_max=0.3,  # y_max < y_min
        )
        with pytest.raises(CounterfactualComputationError, match="Invalid mask y coordinates"):
            apply_mask(sample_image, bad_mask)


# =============================================================================
# 7. Integration Tests
# =============================================================================


class TestIntegration:
    """Tests for full probe pipeline integration."""

    def test_full_probe_pipeline(
        self, engine: CounterfactualEngine, sample_image: Image.Image
    ) -> None:
        """Full pipeline: generate masks → apply → compute results → aggregate."""
        # Generate masks
        masks = engine.generate_masks(3)
        assert len(masks) == 9

        # Apply masks and collect results
        results = []
        for mask in masks[:3]:  # Test first 3 masks
            masked_img = apply_mask(sample_image, mask)
            assert masked_img is not None

            # Simulate metrics (in real use, would run inference)
            result = engine.probe_single(
                image=sample_image,
                mask=mask,
                axis="brightness",
                value="1p0",
                baseline_esi=0.8,
                baseline_drift=0.1,
                masked_esi=0.6,  # Simulated masked value
                masked_drift=0.15,
            )
            results.append(result)

        # Aggregate
        surface = engine.build_probe_surface(results)

        assert len(surface.results) == 3
        assert surface.mean_abs_delta_esi > 0
        assert surface.max_abs_delta_esi > 0

    def test_probe_surface_immutability(
        self, engine: CounterfactualEngine, sample_image: Image.Image
    ) -> None:
        """ProbeSurface is immutable (frozen dataclass)."""
        masks = engine.generate_masks(2)

        results = []
        for mask in masks:
            result = engine.probe_single(
                image=sample_image,
                mask=mask,
                axis="brightness",
                value="1p0",
                baseline_esi=0.8,
                baseline_drift=0.1,
                masked_esi=0.6,
                masked_drift=0.15,
            )
            results.append(result)

        surface = engine.build_probe_surface(results)

        # Attempting to modify should raise
        with pytest.raises(AttributeError):
            surface.mean_abs_delta_esi = 999.0  # type: ignore

    def test_multiple_axes_probe(
        self, engine: CounterfactualEngine, sample_image: Image.Image
    ) -> None:
        """Probes can span multiple axes."""
        mask = generate_grid_masks(2)[0]

        results = []
        for axis in ["brightness", "contrast", "blur"]:
            result = engine.probe_single(
                image=sample_image,
                mask=mask,
                axis=axis,
                value="1p0",
                baseline_esi=0.8,
                baseline_drift=0.1,
                masked_esi=0.6,
                masked_drift=0.15,
            )
            results.append(result)

        surface = engine.build_probe_surface(results)
        assert len(surface.results) == 3

        # Results should be sorted by axis
        axes = [r.probe.axis for r in surface.results]
        assert axes == sorted(axes)


# =============================================================================
# 8. Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for to_dict() serialization."""

    def test_region_mask_to_dict_sorted_keys(self, sample_mask: RegionMask) -> None:
        """RegionMask.to_dict() has sorted keys."""
        d = sample_mask.to_dict()
        keys = list(d.keys())
        assert keys == sorted(keys)

    def test_counterfactual_probe_to_dict_sorted_keys(
        self, sample_probe: CounterfactualProbe
    ) -> None:
        """CounterfactualProbe.to_dict() has sorted keys."""
        d = sample_probe.to_dict()
        keys = list(d.keys())
        assert keys == sorted(keys)

    def test_probe_result_to_dict_sorted_keys(self, sample_result: ProbeResult) -> None:
        """ProbeResult.to_dict() has sorted keys."""
        d = sample_result.to_dict()
        keys = list(d.keys())
        assert keys == sorted(keys)

    def test_probe_surface_to_dict_sorted_keys(self, sample_result: ProbeResult) -> None:
        """ProbeSurface.to_dict() has sorted keys."""
        surface = compute_probe_surface([sample_result])
        d = surface.to_dict()
        keys = list(d.keys())
        assert keys == sorted(keys)

    def test_to_dict_is_json_serializable(self, sample_result: ProbeResult) -> None:
        """to_dict() output can be serialized to JSON."""
        surface = compute_probe_surface([sample_result])
        json_str = json.dumps(surface.to_dict())
        assert isinstance(json_str, str)

    def test_to_dict_deterministic(self, sample_result: ProbeResult) -> None:
        """to_dict() produces identical output on repeated calls."""
        d1 = sample_result.to_dict()
        d2 = sample_result.to_dict()
        assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)

    def test_region_mask_to_dict_contains_all_fields(
        self, sample_mask: RegionMask
    ) -> None:
        """RegionMask.to_dict() contains all expected fields."""
        d = sample_mask.to_dict()
        expected_fields = {
            "col", "grid_size", "region_id", "row",
            "x_max", "x_min", "y_max", "y_min",
        }
        assert set(d.keys()) == expected_fields


# =============================================================================
# 9. Dataclass Tests
# =============================================================================


class TestDataclasses:
    """Tests for dataclass behavior."""

    def test_region_mask_equality(self) -> None:
        """Two RegionMasks with same values are equal."""
        m1 = RegionMask(
            region_id="grid_r0_c0_k3",
            row=0, col=0, grid_size=3,
            x_min=0.0, y_min=0.0, x_max=0.33, y_max=0.33,
        )
        m2 = RegionMask(
            region_id="grid_r0_c0_k3",
            row=0, col=0, grid_size=3,
            x_min=0.0, y_min=0.0, x_max=0.33, y_max=0.33,
        )
        assert m1 == m2

    def test_region_mask_inequality(self) -> None:
        """Two RegionMasks with different values are not equal."""
        m1 = RegionMask(
            region_id="grid_r0_c0_k3",
            row=0, col=0, grid_size=3,
            x_min=0.0, y_min=0.0, x_max=0.33, y_max=0.33,
        )
        m2 = RegionMask(
            region_id="grid_r0_c1_k3",
            row=0, col=1, grid_size=3,
            x_min=0.33, y_min=0.0, x_max=0.66, y_max=0.33,
        )
        assert m1 != m2

    def test_region_mask_hashable(self) -> None:
        """RegionMask is hashable (can be used in sets/dicts)."""
        m = RegionMask(
            region_id="grid_r0_c0_k3",
            row=0, col=0, grid_size=3,
            x_min=0.0, y_min=0.0, x_max=0.33, y_max=0.33,
        )
        s = {m}
        assert m in s

    def test_counterfactual_probe_hashable(self, sample_probe: CounterfactualProbe) -> None:
        """CounterfactualProbe is hashable."""
        s = {sample_probe}
        assert sample_probe in s

    def test_probe_result_frozen(self, sample_result: ProbeResult) -> None:
        """ProbeResult is frozen (immutable)."""
        with pytest.raises(AttributeError):
            sample_result.delta_esi = 999.0  # type: ignore


# =============================================================================
# 10. Guardrail Tests (AST-based)
# =============================================================================


class TestGuardrails:
    """AST-based tests to verify no forbidden imports."""

    @pytest.fixture
    def module_ast(self) -> ast.Module:
        """Parse counterfactual_engine.py into AST."""
        module_path = (
            Path(__file__).parent.parent
            / "app"
            / "clarity"
            / "counterfactual_engine.py"
        )
        with open(module_path, encoding="utf-8") as f:
            source = f.read()
        return ast.parse(source)

    def _get_imported_names(self, tree: ast.Module) -> set[str]:
        """Extract all imported module names from AST."""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return imports

    def test_no_subprocess_import(self, module_ast: ast.Module) -> None:
        """counterfactual_engine.py does not import subprocess."""
        imports = self._get_imported_names(module_ast)
        assert "subprocess" not in imports

    def test_no_r2l_import(self, module_ast: ast.Module) -> None:
        """counterfactual_engine.py does not import r2l modules."""
        imports = self._get_imported_names(module_ast)
        assert "r2l" not in imports
        assert "r2l_runner" not in imports
        assert "r2l_interface" not in imports

    def test_no_random_import(self, module_ast: ast.Module) -> None:
        """counterfactual_engine.py does not import random."""
        imports = self._get_imported_names(module_ast)
        assert "random" not in imports

    def test_no_datetime_import(self, module_ast: ast.Module) -> None:
        """counterfactual_engine.py does not import datetime."""
        imports = self._get_imported_names(module_ast)
        assert "datetime" not in imports

    def test_no_uuid_import(self, module_ast: ast.Module) -> None:
        """counterfactual_engine.py does not import uuid."""
        imports = self._get_imported_names(module_ast)
        assert "uuid" not in imports

    def test_no_numpy_import(self, module_ast: ast.Module) -> None:
        """counterfactual_engine.py does not import numpy."""
        imports = self._get_imported_names(module_ast)
        assert "numpy" not in imports
        assert "np" not in imports


# =============================================================================
# 11. Rounding Tests
# =============================================================================


class TestRounding:
    """Tests for 8-decimal rounding enforcement."""

    def test_round8_basic(self) -> None:
        """_round8 rounds to 8 decimal places."""
        assert _round8(0.123456789012) == 0.12345679

    def test_round8_preserves_exact_values(self) -> None:
        """_round8 preserves values with <= 8 decimals."""
        assert _round8(0.12345678) == 0.12345678

    def test_delta_esi_is_rounded(self) -> None:
        """Delta ESI values are rounded to 8 decimals."""
        probe = CounterfactualProbe(
            region_id="test",
            axis="brightness",
            value="1p0",
        )
        result = compute_probe_result(
            probe=probe,
            baseline_esi=0.1111111111111,
            baseline_drift=0.0,
            masked_esi=0.2222222222222,
            masked_drift=0.0,
        )
        # 0.2222... - 0.1111... should round to 8 decimals
        assert len(str(result.delta_esi).split(".")[-1]) <= 8

    def test_probe_surface_statistics_are_rounded(self) -> None:
        """ProbeSurface statistics are rounded to 8 decimals."""
        results = [
            ProbeResult(
                probe=CounterfactualProbe("r1", "a", "v"),
                baseline_esi=0.0, masked_esi=0.333333333333,
                delta_esi=0.333333333333,
                baseline_drift=0.0, masked_drift=0.0, delta_drift=0.0,
            ),
            ProbeResult(
                probe=CounterfactualProbe("r2", "a", "v"),
                baseline_esi=0.0, masked_esi=0.666666666666,
                delta_esi=0.666666666666,
                baseline_drift=0.0, masked_drift=0.0, delta_drift=0.0,
            ),
        ]
        surface = compute_probe_surface(results)

        # Mean should be rounded
        mean_str = str(surface.mean_abs_delta_esi)
        if "." in mean_str:
            assert len(mean_str.split(".")[-1]) <= 8


# =============================================================================
# 12. Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_small_image(self) -> None:
        """Masking works on small images (1x1)."""
        tiny_img = Image.new("RGB", (1, 1), (255, 255, 255))
        mask = generate_grid_masks(1)[0]

        result = apply_mask(tiny_img, mask)
        assert result.size == (1, 1)

    def test_single_result_probe_surface(self) -> None:
        """ProbeSurface can be computed from single result."""
        result = ProbeResult(
            probe=CounterfactualProbe("r1", "a", "v"),
            baseline_esi=0.5, masked_esi=0.3, delta_esi=-0.2,
            baseline_drift=0.1, masked_drift=0.2, delta_drift=0.1,
        )
        surface = compute_probe_surface([result])

        assert len(surface.results) == 1
        assert surface.mean_abs_delta_esi == 0.2
        assert surface.max_abs_delta_esi == 0.2

    def test_large_grid_size(self) -> None:
        """Large grid sizes work correctly."""
        masks = generate_grid_masks(10)
        assert len(masks) == 100

        # Check first and last masks
        assert masks[0].region_id == "grid_r0_c0_k10"
        assert masks[-1].region_id == "grid_r9_c9_k10"

    def test_asymmetric_image(self) -> None:
        """Masking works on non-square images."""
        wide_img = Image.new("RGB", (200, 50), (255, 255, 255))
        mask = generate_grid_masks(2)[0]  # Top-left quarter

        result = apply_mask(wide_img, mask)
        assert result.size == (200, 50)

        # Check masked region
        pixel = result.getpixel((25, 10))  # In top-left quarter
        assert pixel == (MASK_FILL_VALUE, MASK_FILL_VALUE, MASK_FILL_VALUE)

    def test_all_zeros_metrics(self) -> None:
        """Handling of all-zero metrics."""
        result = ProbeResult(
            probe=CounterfactualProbe("r1", "a", "v"),
            baseline_esi=0.0, masked_esi=0.0, delta_esi=0.0,
            baseline_drift=0.0, masked_drift=0.0, delta_drift=0.0,
        )
        surface = compute_probe_surface([result])

        assert surface.mean_abs_delta_esi == 0.0
        assert surface.max_abs_delta_esi == 0.0

    def test_empty_region_after_rounding(self) -> None:
        """Mask with region too small to render returns original image."""
        # Create a small image where a tiny mask region rounds to empty
        img = Image.new("RGB", (10, 10), (255, 255, 255))

        # Create a mask with very small coordinates that will round to empty
        # When x_min=0.01 and x_max=0.02 on a 10px image:
        # x1 = int(0.01 * 10) = 0, x2 = int(0.02 * 10) = 0
        # This creates an empty region (x2 <= x1)
        tiny_mask = RegionMask(
            region_id="tiny",
            row=0,
            col=0,
            grid_size=100,
            x_min=0.001,
            y_min=0.001,
            x_max=0.009,  # Will round to same pixel as x_min
            y_max=0.009,
        )

        result = apply_mask(img, tiny_mask)

        # Image should be unchanged (white)
        assert result.getpixel((0, 0)) == (255, 255, 255)
        assert result.getpixel((5, 5)) == (255, 255, 255)

