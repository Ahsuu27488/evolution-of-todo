"""FastAPI application entry point for Chronos Todo API.

This is the main entry point for the Todo API backend.
It configures:
- CORS for frontend communication
- Error handling middleware
- Request ID tracking
- Async database initialization
- API routes (tasks, auth, health)
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_db_and_tables
from app.errors import setup_error_handling
from app.routes import auth, tasks

# =============================================================================
# Configuration
# =============================================================================

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Get CORS origins from environment (comma-separated)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]

logger.info(f"Configured CORS origins: {CORS_ORIGINS}")


# =============================================================================
# Application Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Startup:
    - Validate environment variables
    - Create database tables

    Shutdown:
    - Cleanup resources if needed
    """
    logger.info("Starting Todo API...")

    # Validate required environment variables
    required_vars = ["DATABASE_URL", "BETTER_AUTH_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {missing}")
        raise RuntimeError(f"Missing required environment variables: {missing}")

    # Create database tables
    try:
        await create_db_and_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        raise

    logger.info("Todo API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Todo API...")


# =============================================================================
# Application Instance
# =============================================================================

app = FastAPI(
    title="Chronos Todo API",
    description="RESTful API for Phase II Chronos Todo Full-Stack Web Application",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# =============================================================================
# Middleware
# =============================================================================

# CORS middleware - allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Error handling and request ID middleware
setup_error_handling(app)


# =============================================================================
# Routes
# =============================================================================

# Include API routes with /api prefix
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])


# =============================================================================
# Health Check
# =============================================================================

@app.get("/api/health", tags=["Health"])
def health_check() -> dict:
    """Health check endpoint.

    Returns server status and timestamp.
    Used by monitoring tools and frontend health checks.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.0.0",
    }


@app.get("/", tags=["Health"])
def root() -> dict:
    """Root endpoint with API information."""
    return {
        "message": "Chronos Todo API - Phase II",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
