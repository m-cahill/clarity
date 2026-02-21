"""CLARITY Backend FastAPI Application.

Main entry point for the CLARITY evaluation instrument backend.
Provides health and version endpoints for service verification.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.counterfactual_router import router as counterfactual_router
from app.demo_router import router as demo_router
from app.health import (
    HealthResponse,
    VersionResponse,
    get_health,
    get_version,
)
from app.logging_config import configure_logging

logger = logging.getLogger(__name__)

# Environment configuration
APP_ENV = os.environ.get("APP_ENV", "development")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup/shutdown."""
    configure_logging()
    logger.info("CLARITY backend starting", extra={"event": "startup"})
    yield
    logger.info("CLARITY backend shutting down", extra={"event": "shutdown"})


app = FastAPI(
    title="CLARITY Backend",
    description="Clinical Localization and Reasoning Integrity Testing",
    version="0.0.1",
    lifespan=lifespan,
)

# CORS configuration for frontend access
# In demo mode, restrict to ALLOWED_ORIGIN if set
if APP_ENV == "demo" and ALLOWED_ORIGIN:
    cors_origins = [ALLOWED_ORIGIN]
else:
    cors_origins = ["*"]  # Permissive for dev

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint.

    Returns service status, name, and version for E2E verification.
    """
    return get_health()


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    """Version endpoint.

    Returns service version and git SHA (if available).
    """
    return get_version()


# Include counterfactual router (M09)
app.include_router(counterfactual_router)

# Include demo router (M10.5) - always available for artifact serving
app.include_router(demo_router)

