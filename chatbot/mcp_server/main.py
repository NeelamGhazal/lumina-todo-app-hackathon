# Task T008: FastAPI Application with MCP Server
"""MCP Server for Todo Operations - FastAPI application.

Provides:
- /health endpoint for health checks
- /mcp endpoint for MCP protocol communication
- CORS middleware for cross-origin requests

References:
- spec.md: FR-001-005 (MCP server core requirements)
- plan.md: ADR-001 (standalone FastAPI on port 8001)
"""

import logging
import traceback
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mcp_server.config import get_settings
from mcp_server.database import init_db
from mcp_server.logging import configure_logging, get_logger, set_correlation_id

settings = get_settings()

# Configure structured logging on module load
configure_logging()
logger = get_logger("mcp_server")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Startup:
    - Initialize database tables
    - Log startup message

    Shutdown:
    - Log shutdown message
    """
    # Startup
    try:
        logger.info("mcp_server_starting", port=settings.mcp_server_port)
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("startup_failed", error=str(e))
        # Continue anyway to allow diagnostic endpoints

    yield

    # Shutdown
    logger.info("mcp_server_stopping")


app = FastAPI(
    title="MCP Todo Server",
    description="MCP Server exposing todo CRUD operations for AI agents",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to each request."""
    import uuid

    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
    set_correlation_id(correlation_id)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.get("/")
async def root() -> dict:
    """Root endpoint for basic health check."""
    return {
        "service": "MCP Todo Server",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns server status for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment,
    }


@app.get("/mcp/tools")
async def list_mcp_tools() -> dict:
    """List available MCP tools.

    Returns empty array until tools are registered in Phase 1C.
    """
    # TODO: Populate with registered tools in T015, T017, T019, T021, T023
    return {"tools": []}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler with structured logging.

    Logs errors with correlation ID for debugging (FR-067).
    Returns sanitized error response.
    """
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=str(request.url.path),
        method=request.method,
    )

    # Return detailed errors only in development
    content = {"error": "Internal server error", "code": "INTERNAL_ERROR"}
    if settings.is_development:
        content["detail"] = str(exc)
        content["traceback"] = traceback.format_exc()

    return JSONResponse(status_code=500, content=content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mcp_server.main:app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=settings.is_development,
    )
