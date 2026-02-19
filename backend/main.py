"""
MedGuardian Edge - FastAPI Application Entry Point
"""

import os
import time
import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes import risk, lab, prescription, documentation, analyze
from backend.services.ollama_client import health_check, OLLAMA_MODEL, OLLAMA_BASE_URL

# ─────────────────────────────────────────────
# Logging Configuration
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("medguardian")


# ─────────────────────────────────────────────
# Lifespan: Startup / Shutdown Events
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("  MedGuardian Edge — Starting Up")
    logger.info("=" * 60)
    logger.info("  Ollama URL  : %s", OLLAMA_BASE_URL)
    logger.info("  Model       : %s", OLLAMA_MODEL)

    health = await health_check()
    if health["ollama_status"] == "online" and health["model_loaded"]:
        logger.info("  Ollama      : ✓ Connected — model '%s' available", OLLAMA_MODEL)
    elif health["ollama_status"] == "online":
        logger.warning("  Ollama      : ✓ Connected — but model '%s' NOT found in ollama list", OLLAMA_MODEL)
    else:
        logger.warning(
            "  Ollama      : ✗ Not reachable. Start with: ollama serve"
        )

    logger.info("=" * 60)
    yield
    logger.info("MedGuardian Edge — Shutting down.")


# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────
app = FastAPI(
    title="MedGuardian Edge API",
    description=(
        "Offline Clinical Safety and Documentation Assistant. "
        "Powered by MedGemma via Ollama."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────
# Request Logging Middleware
# ─────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - t0
    logger.info(
        "%s %s → %d (%.3fs)",
        request.method, request.url.path, response.status_code, elapsed,
    )
    return response


# ─────────────────────────────────────────────
# CORS — allow React dev server
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────
app.include_router(risk.router,          prefix="/api/risk",          tags=["Patient Risk Assessment"])
app.include_router(lab.router,           prefix="/api/lab",           tags=["Lab Report Analysis"])
app.include_router(prescription.router,  prefix="/api/prescription",  tags=["Prescription Safety"])
app.include_router(documentation.router, prefix="/api/documentation",  tags=["Clinical Documentation"])
app.include_router(analyze.router,       prefix="/api/v4/analyze",    tags=["V4 Analysis Protocol"])


# ─────────────────────────────────────────────
# Root & Health Endpoints
# ─────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "application": "MedGuardian Edge",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
async def health():
    """
    Full health check endpoint.
    Pings Ollama, checks model availability.
    Returns 200 if healthy, 503 if Ollama is unreachable.
    """
    result = await health_check()
    status_code = 200 if result["ollama_status"] == "online" else 503
    return JSONResponse(status_code=status_code, content=result)
