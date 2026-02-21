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

from app.clarity.report import report_router
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
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "")

# M12: Default localhost origins for non-demo mode
DEFAULT_LOCALHOST_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def get_cors_origins() -> list[str]:
    """Get CORS allowed origins based on environment.

    M12: CORS tightening (SEC-001 progress).

    Priority:
    1. CORS_ALLOWED_ORIGINS env var (comma-separated)
    2. ALLOWED_ORIGIN env var (demo mode, comma-separated)
    3. In demo mode without explicit origins: ["*"] (permissive for demo)
    4. In non-demo mode: localhost only

    Returns:
        List of allowed origins.
    """
    # Explicit CORS_ALLOWED_ORIGINS takes highest priority
    if CORS_ALLOWED_ORIGINS:
        origins = [o.strip() for o in CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
        logger.info(f"CORS: Using explicit CORS_ALLOWED_ORIGINS: {origins}")
        return origins

    # Demo mode with ALLOWED_ORIGIN
    if APP_ENV == "demo" and ALLOWED_ORIGIN:
        origins = [o.strip() for o in ALLOWED_ORIGIN.split(",") if o.strip()]
        logger.info(f"CORS: Demo mode with ALLOWED_ORIGIN: {origins}")
        return origins

    # Demo mode without explicit origins - permissive (documented exception)
    if APP_ENV == "demo":
        logger.warning("CORS: Demo mode without explicit origins - using permissive ['*']")
        return ["*"]

    # Non-demo mode: restrict to localhost by default (M12)
    logger.info(f"CORS: Non-demo mode - localhost only: {DEFAULT_LOCALHOST_ORIGINS}")
    return DEFAULT_LOCALHOST_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler for startup/shutdown."""
    configure_logging()
    logger.info("CLARITY backend starting", extra={"event": "startup", "env": APP_ENV})
    yield
    logger.info("CLARITY backend shutting down", extra={"event": "shutdown"})


app = FastAPI(
    title="CLARITY Backend",
    description="Clinical Localization and Reasoning Integrity Testing",
    version="0.0.1",
    lifespan=lifespan,
)

# CORS configuration (M12: tightened for non-demo mode)
cors_origins = get_cors_origins()

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

# Include report router (M11) - PDF report generation
app.include_router(report_router)

