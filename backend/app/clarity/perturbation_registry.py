"""Perturbation Registry.

Provides centralized registration and lookup of perturbation types.
Prevents duplicate registration and ensures type safety.
"""

from typing import Any, Type

from app.clarity.perturbations.base import Perturbation
from app.clarity.perturbations.blur import GaussianBlurPerturbation
from app.clarity.perturbations.brightness import BrightnessPerturbation
from app.clarity.perturbations.contrast import ContrastPerturbation
from app.clarity.perturbations.gaussian_noise import GaussianNoisePerturbation
from app.clarity.perturbations.resize import ResizePerturbation

# Type alias for perturbation factory (compatible with Python 3.10+)
PerturbationClass = Type[Perturbation]

# Registry mapping name -> perturbation class
_REGISTRY: dict[str, PerturbationClass] = {}


class DuplicateRegistrationError(ValueError):
    """Raised when attempting to register a duplicate perturbation name."""

    pass


def register_perturbation(cls: PerturbationClass) -> PerturbationClass:
    """Register a perturbation class in the registry.

    Args:
        cls: Perturbation subclass to register.

    Returns:
        The registered class (for use as decorator).

    Raises:
        DuplicateRegistrationError: If name is already registered.
        TypeError: If cls is not a Perturbation subclass.
    """
    if not isinstance(cls, type) or not issubclass(cls, Perturbation):
        raise TypeError(f"Expected Perturbation subclass, got {cls}")

    # Create a dummy instance to get the name
    # This requires perturbations to have sensible defaults or we inspect differently
    # For now, we'll use the class attribute pattern
    name = _get_perturbation_name(cls)

    if name in _REGISTRY:
        existing = _REGISTRY[name]
        raise DuplicateRegistrationError(
            f"Perturbation name '{name}' already registered by {existing.__name__}"
        )

    _REGISTRY[name] = cls
    return cls


def _get_perturbation_name(cls: PerturbationClass) -> str:
    """Get the canonical name for a perturbation class.

    Creates a minimal instance to read the name property.
    """
    # Each perturbation class needs different minimal params
    # We use a lookup table for known classes
    minimal_params: dict[PerturbationClass, dict[str, Any]] = {
        BrightnessPerturbation: {"factor": 1.0},
        ContrastPerturbation: {"factor": 1.0},
        GaussianNoisePerturbation: {"std_dev": 0.0, "seed": 0},
        GaussianBlurPerturbation: {"radius": 0.0},
        ResizePerturbation: {"width": 1, "height": 1},
    }

    params = minimal_params.get(cls, {})
    try:
        instance = cls(**params)
        return instance.name
    except Exception as e:
        raise TypeError(f"Cannot instantiate {cls.__name__} to get name: {e}")


def get_perturbation(name: str, **params: Any) -> Perturbation:
    """Get a perturbation instance by name.

    Args:
        name: Canonical perturbation name (e.g., "brightness", "gaussian_noise").
        **params: Parameters to pass to the perturbation constructor.

    Returns:
        Immutable Perturbation instance.

    Raises:
        KeyError: If name is not registered.
        ValueError: If params are invalid for the perturbation type.
        TypeError: If param types are invalid.
    """
    if name not in _REGISTRY:
        available = sorted(_REGISTRY.keys())
        raise KeyError(
            f"Unknown perturbation: '{name}'. Available: {available}"
        )

    cls = _REGISTRY[name]

    try:
        return cls(**params)
    except TypeError as e:
        raise ValueError(f"Invalid parameters for '{name}': {e}")
    except ValueError as e:
        raise ValueError(f"Invalid parameters for '{name}': {e}")


def list_perturbations() -> list[str]:
    """List all registered perturbation names.

    Returns:
        Sorted list of registered perturbation names.
    """
    return sorted(_REGISTRY.keys())


def clear_registry() -> None:
    """Clear all registered perturbations.

    WARNING: Only for testing. Do not use in production code.
    """
    _REGISTRY.clear()


def _initialize_default_registry() -> None:
    """Register all built-in perturbation types."""
    default_perturbations: list[PerturbationClass] = [
        BrightnessPerturbation,
        ContrastPerturbation,
        GaussianNoisePerturbation,
        GaussianBlurPerturbation,
        ResizePerturbation,
    ]

    for cls in default_perturbations:
        if _get_perturbation_name(cls) not in _REGISTRY:
            register_perturbation(cls)


# Initialize registry with built-in perturbations on module load
_initialize_default_registry()

