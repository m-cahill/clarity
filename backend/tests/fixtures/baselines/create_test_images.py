#!/usr/bin/env python
"""Create deterministic test images for baseline fixtures.

This script creates small RGB images for testing purposes.
Images are deterministic given the same parameters.

Run from the baselines directory:
    python create_test_images.py
"""

from PIL import Image


def create_test_image(width: int, height: int, base_color: tuple[int, int, int], seed: int) -> Image.Image:
    """Create a deterministic test image.

    Creates a simple gradient pattern that is deterministic given the same parameters.
    No random values used.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        base_color: Base RGB color tuple.
        seed: Seed value (used to modify pattern).

    Returns:
        RGB PIL Image.
    """
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            # Create a simple deterministic pattern
            r = (base_color[0] + (x * seed) % 50) % 256
            g = (base_color[1] + (y * seed) % 50) % 256
            b = (base_color[2] + ((x + y) * seed) % 50) % 256
            pixels[x, y] = (r, g, b)

    return img


def main() -> None:
    """Create test images for baselines."""
    # Test image 001: 64x64 grayscale-ish pattern
    img1 = create_test_image(64, 64, (128, 128, 128), 42)
    img1.save("test_image_001.png")
    print("Created test_image_001.png (64x64)")

    # Test image 002: 64x64 different pattern
    img2 = create_test_image(64, 64, (100, 120, 140), 123)
    img2.save("test_image_002.png")
    print("Created test_image_002.png (64x64)")


if __name__ == "__main__":
    main()

