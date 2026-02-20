"""CLARITY Core Module.

Clinical Localization and Reasoning Integrity Testing.

This module contains the core CLARITY logic for boundary enforcement,
deterministic serialization, R2L artifact consumption, and image
perturbation primitives.

CLARITY operates as a pure consumer of R2L — it never modifies R2L
execution semantics.

Module Structure:
- r2l_runner: Black-box CLI runner for R2L invocation (M03)
- artifact_loader: R2L artifact loading and validation (M03)
- r2l_interface: Namespace utilities (deprecated R2LInterface)
- serialization: Deterministic JSON serialization
- sweep_manifest: Sweep manifest model
- image_utils: Image canonicalization and hashing
- perturbations: Deterministic image perturbation primitives
- perturbation_registry: Perturbation type registry
"""

# R2L Runner (M03)
from app.clarity.r2l_runner import (
    R2LInvocationError,
    R2LRunner,
    R2LRunResult,
    R2LTimeoutError,
)

# Artifact Loader (M03)
from app.clarity.artifact_loader import (
    MANIFEST_REQUIRED_FIELDS,
    ManifestValidationError,
    TracePackValidationError,
    hash_artifact,
    load_manifest,
    load_trace_pack,
    validate_manifest_schema,
    validate_trace_record,
)

# R2L Interface utilities (namespace functions)
from app.clarity.r2l_interface import (
    R2LInterface,  # Deprecated, for backward compatibility
    get_clarity_output_namespace,
    validate_output_path,
)

# Image utilities
from app.clarity.image_utils import (
    canonicalize_image,
    float32_to_image,
    image_sha256,
    image_to_float32,
)

# Perturbation registry
from app.clarity.perturbation_registry import (
    DuplicateRegistrationError,
    get_perturbation,
    list_perturbations,
    register_perturbation,
)

# Perturbations
from app.clarity.perturbations import (
    BrightnessPerturbation,
    ContrastPerturbation,
    GaussianBlurPerturbation,
    GaussianNoisePerturbation,
    InterpolationMode,
    Perturbation,
    ResizePerturbation,
)

# Serialization
from app.clarity.serialization import (
    deterministic_json_dumps,
    deterministic_json_dumps_bytes,
)

# Sweep manifest
from app.clarity.sweep_manifest import SweepManifest

__all__ = [
    # R2L Runner (M03)
    "R2LRunner",
    "R2LRunResult",
    "R2LInvocationError",
    "R2LTimeoutError",
    # Artifact Loader (M03)
    "load_manifest",
    "load_trace_pack",
    "hash_artifact",
    "validate_manifest_schema",
    "validate_trace_record",
    "ManifestValidationError",
    "TracePackValidationError",
    "MANIFEST_REQUIRED_FIELDS",
    # R2L interface (backward compatibility + utilities)
    "R2LInterface",  # Deprecated
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
