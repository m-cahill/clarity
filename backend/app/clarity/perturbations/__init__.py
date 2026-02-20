"""CLARITY Perturbations Module.

Provides deterministic image perturbation primitives for robustness testing.

All perturbations:
- Accept PIL Image (RGB, RGBA, or L mode)
- Return PIL Image (always RGB mode)
- Are fully deterministic given explicit parameters
- Never mutate the input image
- Are immutable (frozen dataclass)
"""

from app.clarity.perturbations.base import Perturbation
from app.clarity.perturbations.blur import GaussianBlurPerturbation
from app.clarity.perturbations.brightness import BrightnessPerturbation
from app.clarity.perturbations.contrast import ContrastPerturbation
from app.clarity.perturbations.gaussian_noise import GaussianNoisePerturbation
from app.clarity.perturbations.resize import InterpolationMode, ResizePerturbation

__all__ = [
    # Base
    "Perturbation",
    # Perturbation types
    "BrightnessPerturbation",
    "ContrastPerturbation",
    "GaussianBlurPerturbation",
    "GaussianNoisePerturbation",
    "ResizePerturbation",
    # Enums
    "InterpolationMode",
]

