"""CLARITY Core Module.

Clinical Localization and Reasoning Integrity Testing.

This module contains the core CLARITY logic for boundary enforcement,
deterministic serialization, R2L artifact consumption, image
perturbation primitives, sweep orchestration, and metrics computation.

CLARITY operates as a pure consumer of R2L — it never modifies R2L
execution semantics.

Module Structure:
- r2l_runner: Black-box CLI runner for R2L invocation (M03)
- artifact_loader: R2L artifact loading and validation (M03)
- sweep_orchestrator: Multi-axis perturbation sweep engine (M04)
- sweep_models: Sweep data structures (M04)
- metrics: Metric data structures and helpers (M05)
- metrics_engine: Metrics computation engine (M05)
- surfaces: Robustness surface data structures (M06)
- surface_engine: Surface computation engine (M06)
- gradient_engine: Gradient estimation and stability metrics (M07)
- r2l_interface: Namespace utilities (deprecated R2LInterface)
- serialization: Deterministic JSON serialization
- sweep_manifest: Sweep manifest model (M01, legacy)
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

# Sweep manifest (M01 legacy)
from app.clarity.sweep_manifest import SweepManifest

# Sweep Models (M04)
from app.clarity.sweep_models import (
    SweepAxis,
    SweepConfig,
    SweepConfigValidationError,
    SweepRunRecord,
    build_run_directory_name,
    encode_axis_value,
)

# Sweep Orchestrator (M04)
from app.clarity.sweep_orchestrator import (
    OutputDirectoryExistsError,
    SweepExecutionError,
    SweepOrchestrator,
    SweepResult,
)

# Metrics (M05)
from app.clarity.metrics import (
    DriftMetric,
    ESIMetric,
    MetricComputationError,
    MetricsResult,
    extract_answer,
    extract_justification,
    levenshtein_distance,
    normalized_levenshtein,
    round_metric,
)

# Metrics Engine (M05)
from app.clarity.metrics_engine import MetricsEngine

# Surfaces (M06)
from app.clarity.surfaces import (
    AxisSurface,
    RobustnessSurface,
    SurfaceComputationError,
    SurfacePoint,
)

# Surface Engine (M06)
from app.clarity.surface_engine import SurfaceEngine

# Gradient Engine (M07)
from app.clarity.gradient_engine import (
    AxisGradient,
    GradientComputationError,
    GradientEngine,
    GradientPoint,
    GradientSurface,
)

# Counterfactual Engine (M08)
from app.clarity.counterfactual_engine import (
    CounterfactualComputationError,
    CounterfactualEngine,
    CounterfactualProbe,
    MASK_FILL_VALUE,
    ProbeResult,
    ProbeSurface,
    RegionMask,
    apply_mask,
    compute_probe_result,
    compute_probe_surface,
    generate_grid_masks,
)

# Counterfactual Orchestrator (M09)
from app.clarity.counterfactual_orchestrator import (
    BaselineSpec,
    CounterfactualOrchestrator,
    OrchestratorConfig,
    OrchestratorError,
    OrchestratorResult,
    RunnerProtocol,
    RunnerResult,
    StubbedRunner,
    list_available_baselines,
    load_baseline_registry,
    load_baseline_spec,
)

# Evidence Overlay (M10)
from app.clarity.evidence_overlay import (
    DEFAULT_EVIDENCE_HEIGHT,
    DEFAULT_EVIDENCE_WIDTH,
    EVIDENCE_THRESHOLD,
    EvidenceMap,
    EvidenceOverlayEngine,
    EvidenceOverlayError,
    Heatmap,
    OverlayBundle,
    OverlayRegion,
    create_overlay_bundle,
    extract_regions_from_heatmap,
    generate_stubbed_evidence_map,
    normalize_evidence_to_heatmap,
)

# MedGemma Runner (M13) - Gated behind CLARITY_REAL_MODEL
from app.clarity.medgemma_runner import (
    MedGemmaResult,
    MedGemmaRunner,
    create_medgemma_runner_result,
    is_real_model_enabled,
)

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
    # Sweep Models (M04)
    "SweepAxis",
    "SweepConfig",
    "SweepConfigValidationError",
    "SweepRunRecord",
    "build_run_directory_name",
    "encode_axis_value",
    # Sweep Orchestrator (M04)
    "SweepOrchestrator",
    "SweepResult",
    "SweepExecutionError",
    "OutputDirectoryExistsError",
    # Metrics (M05)
    "ESIMetric",
    "DriftMetric",
    "MetricsResult",
    "MetricComputationError",
    "levenshtein_distance",
    "normalized_levenshtein",
    "round_metric",
    "extract_answer",
    "extract_justification",
    # Metrics Engine (M05)
    "MetricsEngine",
    # Surfaces (M06)
    "SurfacePoint",
    "AxisSurface",
    "RobustnessSurface",
    "SurfaceComputationError",
    # Surface Engine (M06)
    "SurfaceEngine",
    # Gradient Engine (M07)
    "GradientPoint",
    "AxisGradient",
    "GradientSurface",
    "GradientComputationError",
    "GradientEngine",
    # Counterfactual Engine (M08)
    "RegionMask",
    "CounterfactualProbe",
    "ProbeResult",
    "ProbeSurface",
    "CounterfactualComputationError",
    "CounterfactualEngine",
    "MASK_FILL_VALUE",
    "generate_grid_masks",
    "apply_mask",
    "compute_probe_result",
    "compute_probe_surface",
    # Counterfactual Orchestrator (M09)
    "CounterfactualOrchestrator",
    "OrchestratorConfig",
    "OrchestratorError",
    "OrchestratorResult",
    "BaselineSpec",
    "RunnerProtocol",
    "RunnerResult",
    "StubbedRunner",
    "load_baseline_registry",
    "load_baseline_spec",
    "list_available_baselines",
    # Evidence Overlay (M10)
    "EvidenceMap",
    "Heatmap",
    "OverlayRegion",
    "OverlayBundle",
    "EvidenceOverlayError",
    "EvidenceOverlayEngine",
    "EVIDENCE_THRESHOLD",
    "DEFAULT_EVIDENCE_WIDTH",
    "DEFAULT_EVIDENCE_HEIGHT",
    "generate_stubbed_evidence_map",
    "normalize_evidence_to_heatmap",
    "extract_regions_from_heatmap",
    "create_overlay_bundle",
    # MedGemma Runner (M13)
    "MedGemmaRunner",
    "MedGemmaResult",
    "is_real_model_enabled",
    "create_medgemma_runner_result",
]
