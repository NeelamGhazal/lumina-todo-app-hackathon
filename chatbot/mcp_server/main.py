# Task T008: FastAPI Application with MCP Server
# Task T015: Register add_task with MCP server
"""MCP Server for Todo Operations - FastAPI application.

Provides:
- /health endpoint for health checks
- /mcp/tools endpoint to list available tools
- /mcp/call endpoint to execute tools
- CORS middleware for cross-origin requests

References:
- spec.md: FR-001-005 (MCP server core requirements)
- plan.md: ADR-001 (standalone FastAPI on port 8001)
"""

import traceback
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.config import get_settings
from mcp_server.database import init_db, get_db
from mcp_server.logging import configure_logging, get_logger, set_correlation_id
from mcp_server.schemas import ToolCallRequest, ErrorCode
from mcp_server.tools import registry
from mcp_server.tools.base import ToolError, build_error_response

# Import tools to register them (T015, T017, T019, T021, T023)
from mcp_server.tools import add_task  # noqa: F401 - registers tool
from mcp_server.tools import list_tasks  # noqa: F401 - registers tool (T017)

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

    Returns array of registered tools with their JSON schemas.
    """
    return {"tools": registry.list_tools()}


@app.post("/mcp/call")
async def call_mcp_tool(
    request: ToolCallRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Execute an MCP tool.

    Validates parameters against the tool's schema, executes the handler,
    and returns the result or error.

    Args:
        request: Tool call request with tool name and parameters
        db: Database session (injected)

    Returns:
        Tool result or error response
    """
    tool_name = request.tool
    tool = registry.get(tool_name)

    # Check if tool exists
    if tool is None:
        return {
            "status": "error",
            "error": {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": f"Unknown tool: {tool_name}",
                "details": {"available_tools": [t["name"] for t in registry.list_tools()]},
            },
        }

    try:
        # Validate parameters against tool's schema
        params = tool.params_model(**request.parameters)

        # Execute the tool handler
        result = await tool.handler(params=params, db=db)

        return {
            "status": "success",
            "data": result,
        }

    except ValidationError as e:
        # Pydantic validation error
        return {
            "status": "error",
            "error": {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Invalid parameters",
                "details": {"errors": e.errors()},
            },
        }

    except ToolError as e:
        # Tool-specific error
        return {
            "status": "error",
            "error": build_error_response(e),
        }

    except Exception as e:
        # Unexpected error
        logger.error(
            "tool_call_failed",
            tool=tool_name,
            error=str(e),
        )
        return {
            "status": "error",
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "Tool execution failed",
                "details": {"error": str(e)} if settings.is_development else None,
            },
        }


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
