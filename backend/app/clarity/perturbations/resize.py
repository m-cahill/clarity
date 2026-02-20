"""Resize Perturbation.

Resizes images with configurable dimensions and interpolation.
Uses PIL's resize with explicit interpolation mode for determinism.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from PIL import Image

from app.clarity.image_utils import canonicalize_image
from app.clarity.perturbations.base import Perturbation


class InterpolationMode(str, Enum):
    """Supported interpolation modes for resize.

    String enum for easy serialization to manifest.
    """

    NEAREST = "nearest"
    BILINEAR = "bilinear"
    BICUBIC = "bicubic"
    LANCZOS = "lanczos"


# Map enum values to PIL resampling constants
_INTERPOLATION_MAP = {
    InterpolationMode.NEAREST: Image.Resampling.NEAREST,
    InterpolationMode.BILINEAR: Image.Resampling.BILINEAR,
    InterpolationMode.BICUBIC: Image.Resampling.BICUBIC,
    InterpolationMode.LANCZOS: Image.Resampling.LANCZOS,
}


@dataclass(frozen=True)
class ResizePerturbation(Perturbation):
    """Resize perturbation with explicit interpolation.

    Resizes image to specified dimensions using deterministic interpolation.

    Attributes:
        width: Target width in pixels. Must be > 0.
        height: Target height in pixels. Must be > 0.
        interpolation: Interpolation mode. Default is BILINEAR.
    """

    width: int
    height: int
    interpolation: InterpolationMode = InterpolationMode.BILINEAR

    def __post_init__(self) -> None:
        """Validate parameters at construction time."""
        # Validate width
        if not isinstance(self.width, int):
            raise TypeError(f"width must be an int, got {type(self.width).__name__}")
        if self.width <= 0:
            raise ValueError(f"width must be > 0, got {self.width}")

        # Validate height
        if not isinstance(self.height, int):
            raise TypeError(f"height must be an int, got {type(self.height).__name__}")
        if self.height <= 0:
            raise ValueError(f"height must be > 0, got {self.height}")

        # Validate interpolation
        if not isinstance(self.interpolation, InterpolationMode):
            # Try to convert string to enum
            if isinstance(self.interpolation, str):
                try:
                    # Use object.__setattr__ since we're in a frozen dataclass
                    object.__setattr__(
                        self, "interpolation", InterpolationMode(self.interpolation)
                    )
                except ValueError:
                    valid = [m.value for m in InterpolationMode]
                    raise ValueError(
                        f"Invalid interpolation mode: {self.interpolation}. "
                        f"Valid modes: {valid}"
                    )
            else:
                raise TypeError(
                    f"interpolation must be InterpolationMode or str, "
                    f"got {type(self.interpolation).__name__}"
                )

    @property
    def name(self) -> str:
        return "resize"

    @property
    def version(self) -> str:
        return "1.0.0"

    def apply(self, image: Image.Image) -> Image.Image:
        """Apply resize transformation.

        Args:
            image: PIL Image in RGB, RGBA, or L mode.

        Returns:
            PIL Image in RGB mode with new dimensions.
        """
        # Canonicalize to RGB
        canonical = canonicalize_image(image)

        # Get PIL resampling constant
        resampling = _INTERPOLATION_MAP[self.interpolation]

        # Resize
        result = canonical.resize((self.width, self.height), resample=resampling)

        return result

    def to_manifest_dict(self) -> dict[str, Any]:
        """Serialize to manifest format."""
        return {
            "name": self.name,
            "version": self.version,
            "params": {
                "width": self.width,
                "height": self.height,
                "interpolation": self.interpolation.value,
            },
        }

