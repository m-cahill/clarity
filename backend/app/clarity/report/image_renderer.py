"""Deterministic Image Renderer for CLARITY Reports.

This module provides deterministic PNG generation for heatmaps and surfaces.

CRITICAL CONSTRAINTS (M11):
1. All rendering must be deterministic (same input → identical bytes).
2. No randomness, no datetime.now, no uuid.
3. No subprocess, no r2l imports.
4. Fixed dimensions, colormap, scaling.
5. No antialiasing.
6. Stable PNG encoding (no variable metadata).
7. Use Pillow only.

The renderer produces:
- Heatmap images with fixed colormap
- Surface plots as simple grid visualizations
- All images are PNG with no metadata variability
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

from PIL import Image, PngImagePlugin

if TYPE_CHECKING:
    pass


# Fixed rendering constants
DEFAULT_HEATMAP_WIDTH = 200
DEFAULT_HEATMAP_HEIGHT = 200
DEFAULT_SURFACE_WIDTH = 400
DEFAULT_SURFACE_HEIGHT = 200
CELL_SIZE = 40  # Size of each cell in surface grid


def _round8(value: float) -> float:
    """Round a value to 8 decimal places.

    Args:
        value: The float value to round.

    Returns:
        The value rounded to 8 decimal places.
    """
    return round(value, 8)


def _value_to_color(value: float) -> tuple[int, int, int]:
    """Convert a normalized value [0, 1] to an RGB color.

    Uses a fixed red-scale colormap:
    - 0.0 → light gray (240, 240, 240)
    - 1.0 → dark red (180, 0, 0)

    The colormap is designed for deterministic rendering with
    good visibility across the value range.

    Args:
        value: Normalized value in [0, 1].

    Returns:
        RGB tuple (r, g, b) with values in [0, 255].
    """
    # Clamp value to [0, 1]
    value = max(0.0, min(1.0, value))

    # Linear interpolation from light gray to dark red
    # Low values: (240, 240, 240) - light gray
    # High values: (180, 0, 0) - dark red
    r = int(240 - (60 * value))  # 240 → 180
    g = int(240 * (1 - value))   # 240 → 0
    b = int(240 * (1 - value))   # 240 → 0

    return (r, g, b)


def _value_to_blue_red(value: float) -> tuple[int, int, int]:
    """Convert a normalized value [-1, 1] to an RGB color.

    Uses a diverging blue-white-red colormap:
    - -1.0 → blue (0, 100, 200)
    - 0.0 → white (255, 255, 255)
    - +1.0 → red (200, 50, 50)

    Args:
        value: Normalized value in [-1, 1].

    Returns:
        RGB tuple (r, g, b) with values in [0, 255].
    """
    # Clamp value to [-1, 1]
    value = max(-1.0, min(1.0, value))

    if value < 0:
        # Interpolate from blue to white
        t = -value  # 0 to 1
        r = int(255 - (255 - 0) * t)     # 255 → 0
        g = int(255 - (255 - 100) * t)   # 255 → 100
        b = int(255 - (255 - 200) * t)   # 255 → 200
    else:
        # Interpolate from white to red
        t = value  # 0 to 1
        r = int(255 - (255 - 200) * t)   # 255 → 200
        g = int(255 - (255 - 50) * t)    # 255 → 50
        b = int(255 - (255 - 50) * t)    # 255 → 50

    return (r, g, b)


def render_heatmap_png(
    values: list[list[float]],
    width: int = DEFAULT_HEATMAP_WIDTH,
    height: int = DEFAULT_HEATMAP_HEIGHT,
) -> bytes:
    """Render a heatmap as a deterministic PNG.

    Creates a fixed-size image from a 2D array of normalized values.
    Uses nearest-neighbor scaling (no antialiasing) for determinism.

    Args:
        values: 2D array of values in [0, 1].
        width: Output image width in pixels.
        height: Output image height in pixels.

    Returns:
        PNG image bytes.

    Raises:
        ValueError: If values array is empty or malformed.
    """
    if not values or not values[0]:
        raise ValueError("Values array cannot be empty")

    input_height = len(values)
    input_width = len(values[0])

    # Validate all rows have same width
    for i, row in enumerate(values):
        if len(row) != input_width:
            raise ValueError(f"Row {i} has width {len(row)}, expected {input_width}")

    # Create image
    img = Image.new("RGB", (width, height), (255, 255, 255))
    pixels = img.load()

    # Scale factors
    x_scale = input_width / width
    y_scale = input_height / height

    # Fill pixels using nearest-neighbor sampling
    for py in range(height):
        # Map pixel y to source row
        src_y = int(py * y_scale)
        src_y = min(src_y, input_height - 1)

        for px in range(width):
            # Map pixel x to source column
            src_x = int(px * x_scale)
            src_x = min(src_x, input_width - 1)

            # Get value and convert to color
            value = _round8(values[src_y][src_x])
            color = _value_to_color(value)
            pixels[px, py] = color

    # Save to bytes with deterministic settings
    return _save_png_deterministic(img)


def render_surface_png(
    axes: list[dict],
    width: int = DEFAULT_SURFACE_WIDTH,
    height: int = DEFAULT_SURFACE_HEIGHT,
) -> bytes:
    """Render a robustness surface as a deterministic PNG.

    Creates a simple grid visualization of ESI values across axes and values.
    Uses fixed cell sizes and colors for determinism.

    Args:
        axes: List of axis dictionaries with 'axis', 'points' fields.
              Each point has 'value' and 'esi' fields.
        width: Output image width in pixels.
        height: Output image height in pixels.

    Returns:
        PNG image bytes.

    Raises:
        ValueError: If axes data is malformed.
    """
    if not axes:
        raise ValueError("Axes list cannot be empty")

    # Sort axes alphabetically for determinism
    sorted_axes = sorted(axes, key=lambda a: a.get("axis", ""))

    # Find maximum number of points across all axes
    max_points = max(len(a.get("points", [])) for a in sorted_axes)
    if max_points == 0:
        raise ValueError("No points in any axis")

    num_axes = len(sorted_axes)

    # Calculate cell dimensions to fit within image
    cell_width = width // max_points
    cell_height = height // num_axes

    # Create image with white background
    img = Image.new("RGB", (width, height), (255, 255, 255))
    pixels = img.load()

    # Draw cells for each axis
    for axis_idx, axis_data in enumerate(sorted_axes):
        points = sorted(axis_data.get("points", []), key=lambda p: p.get("value", ""))

        for point_idx, point in enumerate(points):
            esi = point.get("esi", 0.0)
            esi = _round8(float(esi))
            color = _value_to_color(esi)

            # Calculate cell bounds
            x_start = point_idx * cell_width
            x_end = min(x_start + cell_width, width)
            y_start = axis_idx * cell_height
            y_end = min(y_start + cell_height, height)

            # Fill cell
            for py in range(y_start, y_end):
                for px in range(x_start, x_end):
                    pixels[px, py] = color

    # Add grid lines (dark gray)
    grid_color = (100, 100, 100)

    # Vertical lines
    for i in range(max_points + 1):
        x = min(i * cell_width, width - 1)
        for py in range(height):
            pixels[x, py] = grid_color

    # Horizontal lines
    for i in range(num_axes + 1):
        y = min(i * cell_height, height - 1)
        for px in range(width):
            pixels[px, y] = grid_color

    return _save_png_deterministic(img)


def render_probe_grid_png(
    probes: list[dict],
    grid_size: int,
    width: int = DEFAULT_HEATMAP_WIDTH,
    height: int = DEFAULT_HEATMAP_HEIGHT,
) -> bytes:
    """Render a probe grid as a deterministic PNG.

    Creates a grid visualization of delta ESI values from counterfactual probes.
    Uses a diverging colormap (blue-white-red) for negative/positive deltas.

    Args:
        probes: List of probe dictionaries with 'row', 'col', 'delta_esi' fields.
        grid_size: Size of the grid (k for k×k).
        width: Output image width in pixels.
        height: Output image height in pixels.

    Returns:
        PNG image bytes.

    Raises:
        ValueError: If probes data is malformed or grid_size is invalid.
    """
    if grid_size < 1:
        raise ValueError(f"Invalid grid size: {grid_size}")

    if not probes:
        raise ValueError("Probes list cannot be empty")

    # Create 2D array for delta values
    grid: list[list[float]] = [[0.0] * grid_size for _ in range(grid_size)]

    # Fill grid from probes
    for probe in probes:
        row = probe.get("row", 0)
        col = probe.get("col", 0)
        delta_esi = probe.get("delta_esi", 0.0)

        if 0 <= row < grid_size and 0 <= col < grid_size:
            grid[row][col] = _round8(float(delta_esi))

    # Calculate cell dimensions
    cell_width = width // grid_size
    cell_height = height // grid_size

    # Create image with white background
    img = Image.new("RGB", (width, height), (255, 255, 255))
    pixels = img.load()

    # Find max absolute value for normalization
    max_abs = 0.0
    for row in grid:
        for val in row:
            if abs(val) > max_abs:
                max_abs = abs(val)

    # Avoid division by zero
    if max_abs < 1e-10:
        max_abs = 1.0

    # Draw cells
    for row_idx in range(grid_size):
        for col_idx in range(grid_size):
            value = grid[row_idx][col_idx]
            normalized = value / max_abs  # Range [-1, 1]
            color = _value_to_blue_red(normalized)

            # Calculate cell bounds
            x_start = col_idx * cell_width
            x_end = min(x_start + cell_width, width)
            y_start = row_idx * cell_height
            y_end = min(y_start + cell_height, height)

            # Fill cell
            for py in range(y_start, y_end):
                for px in range(x_start, x_end):
                    pixels[px, py] = color

    # Add grid lines (dark gray)
    grid_color = (100, 100, 100)

    # Vertical lines
    for i in range(grid_size + 1):
        x = min(i * cell_width, width - 1)
        for py in range(height):
            pixels[x, py] = grid_color

    # Horizontal lines
    for i in range(grid_size + 1):
        y = min(i * cell_height, height - 1)
        for px in range(width):
            pixels[px, y] = grid_color

    return _save_png_deterministic(img)


def _save_png_deterministic(img: Image.Image) -> bytes:
    """Save a PIL Image to PNG bytes with deterministic settings.

    Removes all variable metadata from the PNG to ensure identical bytes
    for identical image content.

    Args:
        img: PIL Image to save.

    Returns:
        PNG image bytes.
    """
    # Create a PngInfo object with no metadata
    pnginfo = PngImagePlugin.PngInfo()

    # Save to buffer with fixed settings
    buffer = io.BytesIO()
    img.save(
        buffer,
        format="PNG",
        pnginfo=pnginfo,
        compress_level=6,  # Fixed compression level
    )

    return buffer.getvalue()


def generate_synthetic_heatmap_values(
    width: int,
    height: int,
    seed: int = 42,
) -> list[list[float]]:
    """Generate synthetic heatmap values for testing.

    Creates a deterministic pattern based on the seed.
    This is for testing only — real reports use actual data.

    Args:
        width: Width of the value grid.
        height: Height of the value grid.
        seed: Seed for deterministic pattern generation.

    Returns:
        2D array of normalized values [0, 1].
    """
    import math

    values: list[list[float]] = []

    # Use seed to vary bump positions
    bump_count = 2 + (seed % 2)
    bumps: list[tuple[float, float, float]] = []

    for i in range(bump_count):
        cx = 0.3 + 0.2 * i + 0.1 * ((seed + i) % 3)
        cy = 0.3 + 0.15 * i + 0.1 * ((seed + i * 2) % 4)
        sigma = 0.08 + 0.02 * (i % 2)
        cx = max(0.1, min(0.9, cx))
        cy = max(0.1, min(0.9, cy))
        bumps.append((cx, cy, sigma))

    for y in range(height):
        row: list[float] = []
        ny = y / (height - 1) if height > 1 else 0.5

        for x in range(width):
            nx = x / (width - 1) if width > 1 else 0.5

            value = 0.0
            for cx, cy, sigma in bumps:
                dx = nx - cx
                dy = ny - cy
                dist_sq = dx * dx + dy * dy
                value += math.exp(-dist_sq / (2 * sigma * sigma))

            value = _round8(max(0.0, min(1.0, value)))
            row.append(value)

        values.append(row)

    return values

