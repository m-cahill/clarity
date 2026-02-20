"""Counterfactual API Router for CLARITY.

This module provides the FastAPI router for counterfactual probe execution.

Endpoints:
- POST /counterfactual/run - Execute a counterfactual sweep
- GET /counterfactual/baselines - List available baselines
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.clarity import (
    CounterfactualComputationError,
    CounterfactualOrchestrator,
    OrchestratorError,
    StubbedRunner,
    list_available_baselines,
)


router = APIRouter(prefix="/counterfactual", tags=["counterfactual"])


class CounterfactualRunRequest(BaseModel):
    """Request body for counterfactual run endpoint.

    Attributes:
        baseline_id: The baseline to probe.
        grid_size: Grid size for region masking (k for k×k).
        axis: The perturbation axis.
        value: The encoded axis value.
    """

    baseline_id: str = Field(..., description="The baseline ID to probe")
    grid_size: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Grid size (k for k×k grid)",
    )
    axis: str = Field(..., description="Perturbation axis name")
    value: str = Field(..., description="Encoded axis value")


class CounterfactualRunResponse(BaseModel):
    """Response body for counterfactual run endpoint.

    Contains the full orchestrator result as a nested JSON structure.
    """

    baseline_id: str
    config: dict[str, Any]
    baseline_metrics: dict[str, Any]
    probe_surface: dict[str, Any]
    overlay_bundle: dict[str, Any]


class BaselinesResponse(BaseModel):
    """Response body for baselines list endpoint."""

    baselines: list[str]


@router.post("/run", response_model=CounterfactualRunResponse)
def run_counterfactual(request: CounterfactualRunRequest) -> CounterfactualRunResponse:
    """Execute a counterfactual sweep.

    This endpoint:
    1. Loads the specified baseline
    2. Generates grid masks
    3. Runs probes (stubbed for now)
    4. Returns the probe surface

    Args:
        request: The counterfactual run request.

    Returns:
        CounterfactualRunResponse with probe results.

    Raises:
        HTTPException: If orchestration fails.
    """
    # Use stubbed runner for now (M09 scope)
    runner = StubbedRunner()
    orchestrator = CounterfactualOrchestrator(runner)

    try:
        result = orchestrator.run(
            baseline_id=request.baseline_id,
            grid_size=request.grid_size,
            axis=request.axis,
            value=request.value,
        )
    except OrchestratorError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except CounterfactualComputationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    result_dict = result.to_dict()

    return CounterfactualRunResponse(
        baseline_id=result_dict["baseline_id"],
        config=result_dict["config"],
        baseline_metrics=result_dict["baseline_metrics"],
        probe_surface=result_dict["probe_surface"],
        overlay_bundle=result_dict["overlay_bundle"],
    )


@router.get("/baselines", response_model=BaselinesResponse)
def get_baselines() -> BaselinesResponse:
    """List available baselines.

    Returns:
        BaselinesResponse with list of baseline IDs.
    """
    baselines = list_available_baselines()
    return BaselinesResponse(baselines=baselines)

