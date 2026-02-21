#!/usr/bin/env python
"""Create deterministic clinical-style fixture image for M13.

This script creates a grayscale clinical-style test image for MedGemma
integration testing. The image is fully deterministic (no randomness).

Provenance:
- Created for M13: MedGemma Integration milestone
- Synthetic image with no external dependencies
- Frozen as baseline fixture for determinism testing

Run from the baselines directory:
    python create_clinical_fixture.py
"""

from PIL import Image


def create_clinical_sample(
    width: int = 224,
    height: int = 224,
    seed: int = 42,
) -> Image.Image:
    """Create a deterministic clinical-style grayscale image.

    Creates a simple pattern that simulates a chest X-ray-like appearance:
    - Gradient background (light in center, darker at edges)
    - Deterministic pattern based on seed
    - Grayscale only

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        seed: Seed value for deterministic pattern variation.

    Returns:
        Grayscale PIL Image in RGB mode (for compatibility).
    """
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    center_x = width // 2
    center_y = height // 2
    max_dist = ((center_x ** 2) + (center_y ** 2)) ** 0.5

    for y in range(height):
        for x in range(width):
            # Distance from center (normalized 0-1)
            dx = x - center_x
            dy = y - center_y
            dist = ((dx ** 2) + (dy ** 2)) ** 0.5
            norm_dist = dist / max_dist

            # Base gradient: lighter in center, darker at edges
            # Simulates chest X-ray lung field appearance
            base_value = int(200 - (norm_dist * 100))

            # Add deterministic texture pattern
            texture = ((x * seed) % 17 + (y * seed) % 13) % 20 - 10

            # Clamp to valid range
            gray = max(0, min(255, base_value + texture))

            # Set RGB (grayscale)
            pixels[x, y] = (gray, gray, gray)

    return img


def main() -> None:
    """Create the clinical sample fixture."""
    # Create 224x224 clinical-style image (standard model input size)
    img = create_clinical_sample(224, 224, seed=42)
    img.save("clinical_sample_01.png")
    print("Created clinical_sample_01.png (224x224 grayscale clinical-style)")

    # Verify determinism by creating again and comparing
    img2 = create_clinical_sample(224, 224, seed=42)
    if list(img.tobytes()) == list(img2.tobytes()):
        print("[OK] Determinism verified: identical pixel data on re-generation")
    else:
        print("[ERROR] Non-deterministic output detected!")
        raise RuntimeError("Image generation is not deterministic")


if __name__ == "__main__":
    main()

