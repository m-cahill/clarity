"""Base Perturbation Contract.

Defines the abstract base class for all CLARITY perturbations.
All perturbations must be:
- Immutable (frozen dataclass)
- Deterministic (no hidden randomness)
- Pure functions (no side effects, no input mutation)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from PIL import Image


@dataclass(frozen=True)
class Perturbation(ABC):
    """Abstract base class for all CLARITY perturbations.

    All perturbations must inherit from this class and implement:
    - apply(): Transform an image deterministically
    - to_manifest_dict(): Serialize parameters for reproducibility

    Contract:
    - Accept PIL Image (RGB, RGBA, or L mode)
    - Return PIL Image (always RGB mode)
    - Be fully deterministic given explicit parameters
    - Never mutate the input image
    - Be immutable (frozen dataclass)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Canonical name of this perturbation type."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version of this perturbation implementation."""
        ...

    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """Apply the perturbation to an image.

        Args:
            image: PIL Image in RGB, RGBA, or L mode.
                   MUST NOT be mutated by this method.

        Returns:
            PIL Image in RGB mode (canonical output format).
        """
        ...

    @abstractmethod
    def to_manifest_dict(self) -> dict[str, Any]:
        """Serialize perturbation parameters for manifest storage.

        Returns:
            Dictionary containing:
            - name: str
            - version: str
            - params: dict with all parameter values

        The output must be JSON-serializable and sufficient to
        reproduce the exact same perturbation.
        """
        ...

    def __repr__(self) -> str:
        """Deterministic string representation."""
        manifest = self.to_manifest_dict()
        params_str = ", ".join(f"{k}={v!r}" for k, v in manifest.get("params", {}).items())
        return f"{self.name}(version={self.version!r}, {params_str})"

