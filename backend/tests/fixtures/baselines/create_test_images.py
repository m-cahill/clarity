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


def create_clinical_sample_image(width: int, height: int) -> Image.Image:
    """Create a deterministic clinical sample image for testing.
    
    Creates a 224x224 image that simulates a chest X-ray-like appearance
    with a dark center gradient and lighter edges.
    
    Args:
        width: Image width.
        height: Image height.
        
    Returns:
        RGB PIL Image suitable for medical image model input.
    """
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    
    center_x, center_y = width // 2, height // 2
    max_dist = ((width // 2) ** 2 + (height // 2) ** 2) ** 0.5
    
    for y in range(height):
        for x in range(width):
            # Create radial gradient (lighter at edges, darker at center)
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            normalized_dist = dist / max_dist
            
            # Base grayscale with some structure
            base = int(80 + normalized_dist * 100)
            
            # Add some deterministic structure (ribcage-like horizontal bands)
            if 0.3 < abs(y - center_y) / height < 0.45:
                band_intensity = 20 if (y % 15) < 5 else 0
                base = min(255, base + band_intensity)
            
            # Add central darker region (heart silhouette area)
            if dist < max_dist * 0.25:
                base = int(base * 0.7)
            
            pixels[x, y] = (base, base, base)
    
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
    
    # Clinical sample: 224x224 medical image simulation
    clinical = create_clinical_sample_image(224, 224)
    clinical.save("clinical_sample_01.png")
    print("Created clinical_sample_01.png (224x224)")


if __name__ == "__main__":
    main()

