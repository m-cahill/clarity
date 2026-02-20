"""Gaussian Blur Perturbation.

Applies Gaussian blur with configurable radius.
Uses PIL ImageFilter for deterministic results.
"""

from dataclasses import dataclass
from typing import Any

from PIL import Image, ImageFilter

from app.clarity.image_utils import canonicalize_image
from app.clarity.perturbations.base import Perturbation


@dataclass(frozen=True)
class GaussianBlurPerturbation(Perturbation):
    """Gaussian blur perturbation.

    Applies Gaussian blur using PIL's GaussianBlur filter.

    Attributes:
        radius: Blur radius in pixels. Must be >= 0.
                0 = no blur, higher = more blur.
    """

    radius: float

    def __post_init__(self) -> None:
        """Validate parameters at construction time."""
        if not isinstance(self.radius, (int, float)):
            raise TypeError(f"radius must be a number, got {type(self.radius).__name__}")
        if self.radius < 0:
            raise ValueError(f"radius must be >= 0, got {self.radius}")

    @property
    def name(self) -> str:
        return "gaussian_blur"

    @property
    def version(self) -> str:
        return "1.0.0"

    def apply(self, image: Image.Image) -> Image.Image:
        """Apply Gaussian blur.

        Args:
            image: PIL Image in RGB, RGBA, or L mode.

        Returns:
            PIL Image in RGB mode with Gaussian blur applied.
        """
        # Canonicalize to RGB
        canonical = canonicalize_image(image)

        # Apply Gaussian blur
        # PIL's GaussianBlur is deterministic
        result = canonical.filter(ImageFilter.GaussianBlur(radius=self.radius))

        return result

    def to_manifest_dict(self) -> dict[str, Any]:
        """Serialize to manifest format."""
        return {
            "name": self.name,
            "version": self.version,
            "params": {
                "radius": self.radius,
            },
        }

