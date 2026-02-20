"""Image Utilities for CLARITY.

Provides deterministic image operations:
- Canonical image format conversion
- Stable hash computation for determinism verification
"""

import hashlib
from typing import Literal

import numpy as np
from PIL import Image

# Supported input modes
SUPPORTED_MODES = frozenset({"RGB", "RGBA", "L"})

# Canonical output mode
CANONICAL_MODE: Literal["RGB"] = "RGB"


def canonicalize_image(image: Image.Image) -> Image.Image:
    """Convert an image to canonical RGB format.

    Conversion rules (locked M02 decisions):
    - RGB: returned as-is (but copied to avoid mutation)
    - L (grayscale): converted to RGB via channel repeat
    - RGBA: composited onto solid black background, then RGB

    Args:
        image: PIL Image in RGB, RGBA, or L mode.

    Returns:
        PIL Image in RGB mode.

    Raises:
        ValueError: If image mode is not supported.
    """
    if image.mode not in SUPPORTED_MODES:
        raise ValueError(
            f"Unsupported image mode: {image.mode}. "
            f"Supported modes: {sorted(SUPPORTED_MODES)}"
        )

    if image.mode == "RGB":
        # Copy to ensure we don't share data with input
        return image.copy()

    if image.mode == "L":
        # Grayscale to RGB: repeat channel 3 times
        return image.convert("RGB")

    if image.mode == "RGBA":
        # RGBA to RGB: composite onto solid black (deterministic)
        # Create black background
        background = Image.new("RGB", image.size, (0, 0, 0))
        # Paste using alpha channel as mask
        background.paste(image, mask=image.split()[3])
        return background

    # Should never reach here due to mode check above
    raise ValueError(f"Unexpected image mode: {image.mode}")  # pragma: no cover


def image_sha256(image: Image.Image) -> str:
    """Compute deterministic SHA-256 hash of an image.

    The hash is computed from:
    1. Canonical RGB pixel bytes
    2. Image dimensions (width, height)

    This ensures:
    - Same visual content → same hash
    - Different dimensions → different hash (even if bytes match)
    - No metadata/encoder variability

    Locked M02 contract:
    - Convert to canonical RGB
    - Use np.asarray(img, dtype=np.uint8)
    - Hash arr.tobytes() + width/height

    Args:
        image: PIL Image in RGB, RGBA, or L mode.

    Returns:
        Lowercase hex SHA-256 hash string (64 characters).

    Raises:
        ValueError: If image mode is not supported.
    """
    # Canonicalize to RGB
    canonical = canonicalize_image(image)

    # Convert to numpy array
    arr = np.asarray(canonical, dtype=np.uint8)

    # Get dimensions
    width, height = canonical.size

    # Create hash
    hasher = hashlib.sha256()

    # Include dimensions in hash to disambiguate byte streams
    hasher.update(f"{width}x{height}:".encode("utf-8"))

    # Hash pixel bytes
    hasher.update(arr.tobytes())

    return hasher.hexdigest()


def image_to_float32(image: Image.Image) -> np.ndarray:
    """Convert PIL Image to float32 numpy array normalized to [0, 1].

    Args:
        image: PIL Image (any supported mode).

    Returns:
        numpy array with dtype float32, values in [0.0, 1.0].
    """
    arr = np.asarray(image, dtype=np.float32)
    return arr / 255.0


def float32_to_image(arr: np.ndarray) -> Image.Image:
    """Convert float32 numpy array back to PIL Image.

    Args:
        arr: numpy array with values nominally in [0.0, 1.0].
             Values are clipped before conversion.

    Returns:
        PIL Image in RGB mode.
    """
    # Clip to valid range
    clipped = np.clip(arr, 0.0, 1.0)

    # Convert to uint8
    uint8_arr = (clipped * 255.0).astype(np.uint8)

    return Image.fromarray(uint8_arr, mode="RGB")

