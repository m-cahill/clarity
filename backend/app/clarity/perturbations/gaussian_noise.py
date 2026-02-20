"""Gaussian Noise Perturbation.

Adds Gaussian noise to images with explicit seed control.
Determinism is guaranteed via np.random.default_rng(seed).
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from PIL import Image

from app.clarity.image_utils import (
    canonicalize_image,
    float32_to_image,
    image_to_float32,
)
from app.clarity.perturbations.base import Perturbation


@dataclass(frozen=True)
class GaussianNoisePerturbation(Perturbation):
    """Gaussian noise perturbation with mandatory seed.

    Adds zero-mean Gaussian noise to each pixel channel.
    Deterministic: same seed + same image = same output.

    Attributes:
        std_dev: Standard deviation of noise, normalized to [0.0, 1.0].
                 0.0 = no noise, 1.0 = maximum noise.
        seed: Random seed for deterministic noise generation. REQUIRED.
    """

    std_dev: float
    seed: int

    def __post_init__(self) -> None:
        """Validate parameters at construction time."""
        # Validate std_dev type
        if not isinstance(self.std_dev, (int, float)):
            raise TypeError(
                f"std_dev must be a number, got {type(self.std_dev).__name__}"
            )

        # Validate std_dev range
        if not 0.0 <= self.std_dev <= 1.0:
            raise ValueError(
                f"std_dev must be in [0.0, 1.0], got {self.std_dev}"
            )

        # Validate seed type
        if not isinstance(self.seed, int):
            raise TypeError(f"seed must be an int, got {type(self.seed).__name__}")

    @property
    def name(self) -> str:
        return "gaussian_noise"

    @property
    def version(self) -> str:
        return "1.0.0"

    def apply(self, image: Image.Image) -> Image.Image:
        """Apply Gaussian noise to image.

        Args:
            image: PIL Image in RGB, RGBA, or L mode.

        Returns:
            PIL Image in RGB mode with added noise.
        """
        # Canonicalize to RGB
        canonical = canonicalize_image(image)

        # Convert to float32 normalized [0, 1]
        arr = image_to_float32(canonical)

        # Generate deterministic noise using explicit RNG
        rng = np.random.default_rng(self.seed)
        noise = rng.normal(loc=0.0, scale=self.std_dev, size=arr.shape).astype(
            np.float32
        )

        # Add noise
        noisy = arr + noise

        # Convert back to image (includes clipping)
        return float32_to_image(noisy)

    def to_manifest_dict(self) -> dict[str, Any]:
        """Serialize to manifest format."""
        return {
            "name": self.name,
            "version": self.version,
            "params": {
                "std_dev": self.std_dev,
                "seed": self.seed,
            },
        }

