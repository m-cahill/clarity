"""Tests for CLARITY Report Image Renderer.

This module tests the deterministic PNG generation functions.

Test coverage:
- Heatmap rendering
- Surface rendering
- Probe grid rendering
- PNG format validity
- Determinism across calls
- Edge cases
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

import pytest

from app.clarity.report.image_renderer import (
    DEFAULT_HEATMAP_HEIGHT,
    DEFAULT_HEATMAP_WIDTH,
    generate_synthetic_heatmap_values,
    render_heatmap_png,
    render_probe_grid_png,
    render_surface_png,
)

if TYPE_CHECKING:
    pass


# PNG magic bytes
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class TestRenderHeatmapPng:
    """Tests for render_heatmap_png function."""

    def test_basic_render(self) -> None:
        """Test basic heatmap rendering."""
        values = [[0.5] * 10 for _ in range(10)]
        png = render_heatmap_png(values)

        assert png[:8] == PNG_MAGIC
        assert len(png) > 100  # Should have content

    def test_deterministic_output(self) -> None:
        """Test that same input produces identical output."""
        values = [[0.1 * (x + y) / 18 for x in range(10)] for y in range(10)]

        png1 = render_heatmap_png(values)
        png2 = render_heatmap_png(values)

        assert png1 == png2

    def test_different_values_different_output(self) -> None:
        """Test that different values produce different output."""
        values1 = [[0.0] * 10 for _ in range(10)]
        values2 = [[1.0] * 10 for _ in range(10)]

        png1 = render_heatmap_png(values1)
        png2 = render_heatmap_png(values2)

        assert png1 != png2

    def test_custom_dimensions(self) -> None:
        """Test rendering with custom dimensions."""
        values = [[0.5] * 5 for _ in range(5)]
        png = render_heatmap_png(values, width=100, height=100)

        assert png[:8] == PNG_MAGIC

    def test_empty_values_raises(self) -> None:
        """Test that empty values raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            render_heatmap_png([])

        with pytest.raises(ValueError, match="empty"):
            render_heatmap_png([[]])

    def test_mismatched_row_widths_raises(self) -> None:
        """Test that inconsistent row widths raises ValueError."""
        values = [
            [0.5, 0.5, 0.5],
            [0.5, 0.5],  # Different width
        ]

        with pytest.raises(ValueError, match="width"):
            render_heatmap_png(values)

    def test_values_clamped_to_range(self) -> None:
        """Test that values outside [0, 1] are clamped."""
        values = [[-0.5, 1.5]]

        # Should not raise, values should be clamped
        png = render_heatmap_png(values)
        assert png[:8] == PNG_MAGIC

    def test_single_pixel(self) -> None:
        """Test rendering a 1x1 heatmap."""
        values = [[0.5]]
        png = render_heatmap_png(values, width=10, height=10)

        assert png[:8] == PNG_MAGIC

    def test_default_dimensions(self) -> None:
        """Test default dimensions are used."""
        values = [[0.5] * 10 for _ in range(10)]
        png = render_heatmap_png(values)

        # Just verify it renders without explicit dimensions
        assert png[:8] == PNG_MAGIC


class TestRenderSurfacePng:
    """Tests for render_surface_png function."""

    def test_basic_render(self) -> None:
        """Test basic surface rendering."""
        axes = [
            {
                "axis": "brightness",
                "points": [
                    {"value": "0p8", "esi": 0.9},
                    {"value": "1p0", "esi": 0.95},
                ],
            },
        ]

        png = render_surface_png(axes)
        assert png[:8] == PNG_MAGIC

    def test_deterministic_output(self) -> None:
        """Test that same input produces identical output."""
        axes = [
            {
                "axis": "brightness",
                "points": [
                    {"value": "0p8", "esi": 0.9},
                    {"value": "1p0", "esi": 0.95},
                ],
            },
            {
                "axis": "contrast",
                "points": [
                    {"value": "0p8", "esi": 0.92},
                    {"value": "1p0", "esi": 0.96},
                ],
            },
        ]

        png1 = render_surface_png(axes)
        png2 = render_surface_png(axes)

        assert png1 == png2

    def test_axes_sorted_for_determinism(self) -> None:
        """Test that axes are sorted alphabetically."""
        axes1 = [
            {"axis": "brightness", "points": [{"value": "1", "esi": 0.9}]},
            {"axis": "contrast", "points": [{"value": "1", "esi": 0.9}]},
        ]
        axes2 = [
            {"axis": "contrast", "points": [{"value": "1", "esi": 0.9}]},
            {"axis": "brightness", "points": [{"value": "1", "esi": 0.9}]},
        ]

        png1 = render_surface_png(axes1)
        png2 = render_surface_png(axes2)

        # Should produce identical output regardless of input order
        assert png1 == png2

    def test_empty_axes_raises(self) -> None:
        """Test that empty axes list raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            render_surface_png([])

    def test_no_points_raises(self) -> None:
        """Test that axis with no points raises ValueError."""
        axes = [{"axis": "brightness", "points": []}]

        with pytest.raises(ValueError, match="points"):
            render_surface_png(axes)

    def test_multiple_axes(self) -> None:
        """Test rendering with multiple axes."""
        axes = [
            {"axis": f"axis_{i}", "points": [{"value": "v", "esi": 0.5}]}
            for i in range(5)
        ]

        png = render_surface_png(axes)
        assert png[:8] == PNG_MAGIC

    def test_custom_dimensions(self) -> None:
        """Test rendering with custom dimensions."""
        axes = [
            {"axis": "test", "points": [{"value": "v", "esi": 0.8}]},
        ]

        png = render_surface_png(axes, width=600, height=300)
        assert png[:8] == PNG_MAGIC


class TestRenderProbeGridPng:
    """Tests for render_probe_grid_png function."""

    def test_basic_render(self) -> None:
        """Test basic probe grid rendering."""
        probes = [
            {"row": 0, "col": 0, "delta_esi": -0.05},
            {"row": 0, "col": 1, "delta_esi": -0.08},
            {"row": 1, "col": 0, "delta_esi": -0.07},
            {"row": 1, "col": 1, "delta_esi": -0.15},
        ]

        png = render_probe_grid_png(probes, grid_size=2)
        assert png[:8] == PNG_MAGIC

    def test_deterministic_output(self) -> None:
        """Test that same input produces identical output."""
        probes = [
            {"row": r, "col": c, "delta_esi": -0.01 * (r + c + 1)}
            for r in range(3) for c in range(3)
        ]

        png1 = render_probe_grid_png(probes, grid_size=3)
        png2 = render_probe_grid_png(probes, grid_size=3)

        assert png1 == png2

    def test_negative_positive_colors(self) -> None:
        """Test that negative and positive deltas produce different colors."""
        probes_neg = [{"row": 0, "col": 0, "delta_esi": -0.5}]
        probes_pos = [{"row": 0, "col": 0, "delta_esi": 0.5}]

        png_neg = render_probe_grid_png(probes_neg, grid_size=1)
        png_pos = render_probe_grid_png(probes_pos, grid_size=1)

        assert png_neg != png_pos

    def test_invalid_grid_size_raises(self) -> None:
        """Test that invalid grid size raises ValueError."""
        probes = [{"row": 0, "col": 0, "delta_esi": 0.0}]

        with pytest.raises(ValueError, match="grid"):
            render_probe_grid_png(probes, grid_size=0)

        with pytest.raises(ValueError, match="grid"):
            render_probe_grid_png(probes, grid_size=-1)

    def test_empty_probes_raises(self) -> None:
        """Test that empty probes list raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            render_probe_grid_png([], grid_size=2)

    def test_4x4_grid(self) -> None:
        """Test rendering a 4x4 probe grid."""
        probes = [
            {"row": r, "col": c, "delta_esi": -0.05 - (r * 0.02 + c * 0.01)}
            for r in range(4) for c in range(4)
        ]

        png = render_probe_grid_png(probes, grid_size=4)
        assert png[:8] == PNG_MAGIC

    def test_sparse_probes(self) -> None:
        """Test rendering with sparse probes (not all cells filled)."""
        probes = [
            {"row": 0, "col": 0, "delta_esi": -0.1},
            {"row": 2, "col": 2, "delta_esi": -0.2},
        ]

        png = render_probe_grid_png(probes, grid_size=3)
        assert png[:8] == PNG_MAGIC


class TestGenerateSyntheticHeatmapValues:
    """Tests for generate_synthetic_heatmap_values function."""

    def test_basic_generation(self) -> None:
        """Test basic value generation."""
        values = generate_synthetic_heatmap_values(10, 10)

        assert len(values) == 10
        assert all(len(row) == 10 for row in values)

    def test_deterministic_with_same_seed(self) -> None:
        """Test that same seed produces identical values."""
        values1 = generate_synthetic_heatmap_values(50, 50, seed=42)
        values2 = generate_synthetic_heatmap_values(50, 50, seed=42)

        assert values1 == values2

    def test_different_seeds_different_values(self) -> None:
        """Test that different seeds produce different values."""
        values1 = generate_synthetic_heatmap_values(50, 50, seed=42)
        values2 = generate_synthetic_heatmap_values(50, 50, seed=123)

        assert values1 != values2

    def test_values_in_range(self) -> None:
        """Test that all values are in [0, 1] range."""
        values = generate_synthetic_heatmap_values(100, 100, seed=42)

        for row in values:
            for v in row:
                assert 0.0 <= v <= 1.0

    def test_values_rounded_to_8_decimals(self) -> None:
        """Test that values are rounded to 8 decimal places."""
        values = generate_synthetic_heatmap_values(10, 10, seed=42)

        for row in values:
            for v in row:
                # Check that value has at most 8 decimal places
                rounded = round(v, 8)
                assert v == rounded

    def test_custom_dimensions(self) -> None:
        """Test generation with custom dimensions."""
        values = generate_synthetic_heatmap_values(width=200, height=100, seed=42)

        assert len(values) == 100
        assert all(len(row) == 200 for row in values)

    def test_minimal_dimensions(self) -> None:
        """Test generation with minimal 1x1 dimensions."""
        values = generate_synthetic_heatmap_values(width=1, height=1, seed=42)

        assert len(values) == 1
        assert len(values[0]) == 1


class TestImageRenderingIntegration:
    """Integration tests for image rendering."""

    def test_synthetic_values_to_heatmap(self) -> None:
        """Test full pipeline: synthetic values → heatmap PNG."""
        values = generate_synthetic_heatmap_values(100, 100, seed=42)
        png = render_heatmap_png(values)

        assert png[:8] == PNG_MAGIC
        assert len(png) > 1000  # Should have meaningful content

    def test_multiple_renders_identical(self) -> None:
        """Test that multiple renders produce identical bytes."""
        values = generate_synthetic_heatmap_values(50, 50, seed=42)
        hashes = set()

        for _ in range(5):
            png = render_heatmap_png(values)
            hashes.add(hashlib.sha256(png).hexdigest())

        assert len(hashes) == 1, "All renders should produce identical PNG"

    def test_png_no_variable_metadata(self) -> None:
        """Test that PNG has no variable metadata (timestamps, etc.)."""
        values = generate_synthetic_heatmap_values(10, 10, seed=42)

        png1 = render_heatmap_png(values)
        png2 = render_heatmap_png(values)

        # Byte-identical means no variable metadata
        assert png1 == png2

