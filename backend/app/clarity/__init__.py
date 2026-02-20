"""CLARITY Core Module.

Clinical Localization and Reasoning Integrity Testing.

This module contains the core CLARITY logic for boundary enforcement,
deterministic serialization, R2L artifact consumption, and image
perturbation primitives.

CLARITY operates as a pure consumer of R2L — it never modifies R2L
execution semantics.
"""

from app.clarity.image_utils import (
    canonicalize_image,
    float32_to_image,
    image_sha256,
    image_to_float32,
)
from app.clarity.perturbation_registry import (
    DuplicateRegistrationError,
    get_perturbation,
    list_perturbations,
    register_perturbation,
)
from app.clarity.perturbations import (
    BrightnessPerturbation,
    ContrastPerturbation,
    GaussianBlurPerturbation,
    GaussianNoisePerturbation,
    InterpolationMode,
    Perturbation,
    ResizePerturbation,
)
from app.clarity.r2l_interface import (
    R2LInterface,
    R2LInvocationError,
    get_clarity_output_namespace,
    validate_output_path,
)
from app.clarity.serialization import (
    deterministic_json_dumps,
    deterministic_json_dumps_bytes,
)
from app.clarity.sweep_manifest import SweepManifest

__all__ = [
    # R2L interface
    "R2LInterface",
    "R2LInvocationError",
    "get_clarity_output_namespace",
    "validate_output_path",
    # Serialization
    "SweepManifest",
    "deterministic_json_dumps",
    "deterministic_json_dumps_bytes",
    # Image utilities
    "canonicalize_image",
    "float32_to_image",
    "image_sha256",
    "image_to_float32",
    # Perturbation base and types
    "Perturbation",
    "BrightnessPerturbation",
    "ContrastPerturbation",
    "GaussianBlurPerturbation",
    "GaussianNoisePerturbation",
    "ResizePerturbation",
    "InterpolationMode",
    # Registry
    "DuplicateRegistrationError",
    "get_perturbation",
    "list_perturbations",
    "register_perturbation",
]

