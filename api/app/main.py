"""FastAPI application entry point."""

import logging
import traceback
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db
from app.jobs.scheduler import shutdown_scheduler, start_scheduler
from app.routers import auth_router, chat_router, notifications_router, tasks_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup: initialize database
    try:
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.error(traceback.format_exc())
        # Continue anyway to allow diagnostic endpoints to work

    # Startup: initialize scheduler
    try:
        logger.info("Starting notification scheduler...")
        start_scheduler()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Scheduler initialization failed: {e}")
        logger.error(traceback.format_exc())

    yield

    # Shutdown: stop scheduler
    try:
        logger.info("Stopping scheduler...")
        shutdown_scheduler()
        logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Scheduler shutdown failed: {e}")


app = FastAPI(
    title="Evolution Todo API",
    description="FastAPI backend for Evolution Todo application",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware - allow multiple origins for Vercel integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


@app.get("/")
async def root() -> dict:
    """Root endpoint for HF Spaces health monitoring."""
    return {"status": "ok", "service": "Lumina Todo API", "version": "0.1.0"}


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/debug/db")
async def debug_db() -> dict:
    """Debug endpoint to test database connectivity."""
    from app.core.database import engine
    import os

    result = {
        "database_url": settings.database_url,
        "environment": settings.environment,
        "cwd": os.getcwd(),
        "data_dir_exists": os.path.exists("./data"),
        "data_dir_writable": os.access("./data", os.W_OK) if os.path.exists("./data") else False,
    }

    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        result["db_connection"] = "success"
    except Exception as e:
        result["db_connection"] = "failed"
        result["db_error"] = str(e)
        result["db_traceback"] = traceback.format_exc()

    return result


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to return actual error details."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc() if settings.is_development else None,
        },
    )
