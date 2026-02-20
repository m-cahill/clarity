"""Brightness Perturbation.

Adjusts image brightness using PIL ImageEnhance conventions:
- factor=1.0: no change
- factor=0.0: minimum (black)
- factor>1.0: increased brightness
"""

from dataclasses import dataclass
from typing import Any

from PIL import Image, ImageEnhance

from app.clarity.image_utils import canonicalize_image
from app.clarity.perturbations.base import Perturbation


@dataclass(frozen=True)
class BrightnessPerturbation(Perturbation):
    """Brightness adjustment perturbation.

    Uses PIL ImageEnhance.Brightness which is deterministic.

    Attributes:
        factor: Brightness multiplier. 1.0 = no change, 0.0 = black,
                >1.0 = brighter. Must be >= 0.0.
    """

    factor: float

    def __post_init__(self) -> None:
        """Validate parameters at construction time."""
        if not isinstance(self.factor, (int, float)):
            raise TypeError(f"factor must be a number, got {type(self.factor).__name__}")
        if self.factor < 0.0:
            raise ValueError(f"factor must be >= 0.0, got {self.factor}")

    @property
    def name(self) -> str:
        return "brightness"

    @property
    def version(self) -> str:
        return "1.0.0"

    def apply(self, image: Image.Image) -> Image.Image:
        """Apply brightness adjustment.

        Args:
            image: PIL Image in RGB, RGBA, or L mode.

        Returns:
            PIL Image in RGB mode with adjusted brightness.
        """
        # Canonicalize to RGB
        canonical = canonicalize_image(image)

        # Apply brightness enhancement
        enhancer = ImageEnhance.Brightness(canonical)
        result = enhancer.enhance(self.factor)

        return result

    def to_manifest_dict(self) -> dict[str, Any]:
        """Serialize to manifest format."""
        return {
            "name": self.name,
            "version": self.version,
            "params": {
                "factor": self.factor,
            },
        }

