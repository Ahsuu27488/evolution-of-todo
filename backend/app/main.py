"""FastAPI application entry point for Chronos Todo API.

This is the main entry point for the Todo API backend.
It configures:
- CORS for frontend communication
- Error handling middleware
- Request ID tracking
- Correlation ID propagation (Phase III)
- Rate limiting (Phase III)
- Async database initialization
- Qdrant vector database initialization (Phase III)
- API routes (tasks, auth, notifications, chat)
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db import create_db_and_tables, engine
from app.errors import setup_error_handling
from app.routes import auth, tasks, notifications
from app.routes import chat

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
    - Initialize Qdrant vector database (Phase III)
    - Start scheduler service

    Shutdown:
    - Stop scheduler service
    - Cleanup resources if needed
    """
    logger.info("Starting Todo API...")

    # Validate required environment variables
    required_vars = ["DATABASE_URL", "BETTER_AUTH_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {missing}")
        raise RuntimeError(f"Missing required environment variables: {missing}")

    # Phase III: Warn if optional AI variables are missing
    ai_vars = ["OPENAI_API_KEY", "QDRANT_URL"]
    missing_ai = [var for var in ai_vars if not os.getenv(var)]
    if missing_ai:
        logger.warning(f"Phase III features disabled. Missing: {missing_ai}")

    # Create database tables
    try:
        await create_db_and_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        raise

    # Phase III: Initialize Qdrant vector database
    if os.getenv("QDRANT_URL"):
        try:
            from app.ai.services import initialize_qdrant
            await initialize_qdrant()
            logger.info("Qdrant vector database initialized")
        except Exception as e:
            logger.exception(f"Failed to initialize Qdrant: {e}")
            # Don't fail startup if Qdrant fails

    # Start scheduler service
    try:
        from app.services.scheduler_service import start_scheduler
        await start_scheduler()
        logger.info("Scheduler service started")
    except Exception as e:
        logger.exception(f"Failed to start scheduler: {e}")
        # Don't fail startup if scheduler fails

    logger.info("Todo API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Todo API...")

    # Stop scheduler service
    try:
        from app.services.scheduler_service import stop_scheduler
        await stop_scheduler()
        logger.info("Scheduler service stopped")
    except Exception as e:
        logger.exception(f"Error stopping scheduler: {e}")


# =============================================================================
# Application Instance
# =============================================================================

app = FastAPI(
    title="Chronos Todo API",
    description="RESTful API for Phase II Chronos Todo Full-Stack Web Application with Phase III AI Chatbot",
    version="3.0.0",
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
    expose_headers=["X-Request-ID", "X-Correlation-ID"],
)

# Error handling and request ID middleware
setup_error_handling(app)

# Phase III: Correlation ID middleware for distributed tracing
if os.getenv("PHASE_III_ENABLED", "true").lower() == "true":
    try:
        from app.ai.middleware import CorrelationMiddleware
        app.add_middleware(CorrelationMiddleware)
        logger.info("Correlation ID middleware enabled")
    except ImportError as e:
        logger.warning(f"Could not enable CorrelationMiddleware: {e}")


# =============================================================================
# Routes
# =============================================================================

# Include API routes with /api prefix
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(notifications.router, tags=["Notifications"])

# Phase III: Chat router for AI chatbot (includes transcription endpoint)
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


# =============================================================================
# Health Check
# =============================================================================

async def check_database_health() -> dict:
    """Check database connectivity.

    Returns:
        Dict with database status and latency in milliseconds
    """
    try:
        start = datetime.utcnow()
        async with engine.connect() as conn:
            # Simple query to verify connection
            await conn.execute(text("SELECT 1"))
        latency_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e.__class__.__name__),
        }


async def check_qdrant_health() -> dict:
    """Check Qdrant vector database connectivity (Phase III).

    Returns:
        Dict with Qdrant status and collection info
    """
    if not os.getenv("QDRANT_URL"):
        return {
            "status": "disabled",
            "message": "Qdrant not configured",
        }

    try:
        from app.ai.services import QdrantService

        service = QdrantService()
        collection_exists = await service.collection_exists()

        return {
            "status": "healthy" if collection_exists else "unhealthy",
            "collection_exists": collection_exists,
        }
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e.__class__.__name__),
        }


@app.get("/api/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint.

    Returns server status, database connectivity, Qdrant status, and timestamp.
    Used by monitoring tools and frontend health checks.
    """
    db_health = await check_database_health()
    qdrant_health = await check_qdrant_health()

    # Overall status: degraded if database unhealthy, ok if qdrant disabled
    if db_health["status"] != "healthy":
        overall_status = "degraded"
    elif qdrant_health["status"] == "unhealthy":
        overall_status = "degraded"
    else:
        overall_status = "ok"

    checks = {"database": db_health}
    if qdrant_health["status"] != "disabled":
        checks["qdrant"] = qdrant_health

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "3.0.0",
        "checks": checks,
    }


@app.get("/", tags=["Health"])
def root() -> dict:
    """Root endpoint with API information."""
    return {
        "message": "Chronos Todo API - Phase II with Phase III AI Chatbot",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "phase_iii": os.getenv("PHASE_III_ENABLED", "true").lower() == "true",
    }
