"""Sweep Manifest schema for CLARITY.

The SweepManifest records all parameters needed to reproduce a perturbation
sweep. This is the authoritative ledger for CLARITY runs.

This is a minimal schema for M01 guardrail testing. It will be extended
additively in future milestones (M02+) as perturbation logic is added.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SweepManifest(BaseModel):
    """Minimal sweep manifest for CLARITY runs.

    This model captures the essential parameters needed to reproduce a sweep.
    All fields are chosen to ensure deterministic serialization.

    Attributes:
        seeds: List of random seeds used in the sweep. Order is significant.
        perturbation_axes: List of perturbation axis identifiers (e.g., "blur", "noise").
        r2l_version: The R2L git SHA or version string used for this sweep.
        adapter_model_id: The model adapter identifier (e.g., "medgemma-v1").
        rich_mode: Whether rich mode (adapter_metadata) was enabled.
    """

    seeds: list[int] = Field(
        ...,
        description="Ordered list of random seeds for reproducibility",
    )
    perturbation_axes: list[str] = Field(
        ...,
        description="List of perturbation axis identifiers",
    )
    r2l_version: str = Field(
        ...,
        description="R2L git SHA or version string",
    )
    adapter_model_id: str = Field(
        ...,
        description="Model adapter identifier",
    )
    rich_mode: bool = Field(
        default=False,
        description="Whether rich mode (adapter_metadata) is enabled",
    )

    model_config = {
        "frozen": True,  # Immutable after creation
        "extra": "forbid",  # No extra fields allowed
    }

