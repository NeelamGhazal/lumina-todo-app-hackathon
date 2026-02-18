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

from fastapi import FastAPI, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.config import get_settings

# Task T007: Import agent settings for health check
# Task T013: Import agent initialization (now uses OpenAI Agents SDK)
# Task T020-T022: Import agent chat and conversation functions
try:
    from agent.config import get_agent_settings
    from agent.agent_sdk import initialize_agents_sdk, is_agent_ready
    from agent.chat import process_chat
    from agent.schemas import ChatRequest
    from agent.conversation import get_user_conversations, get_conversation_messages
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    initialize_agents_sdk = None  # type: ignore
    is_agent_ready = None  # type: ignore
    process_chat = None  # type: ignore
    ChatRequest = None  # type: ignore
    get_user_conversations = None  # type: ignore
    get_conversation_messages = None  # type: ignore
from mcp_server.database import init_db, get_db
from mcp_server.logging import configure_logging, get_logger, set_correlation_id
from mcp_server.schemas import ToolCallRequest, ErrorCode
from mcp_server.tools import registry
from mcp_server.tools.base import ToolError, build_error_response

# Import tools to register them (T015, T017, T019, T021, T023)
from mcp_server.tools import add_task  # noqa: F401 - registers tool
from mcp_server.tools import list_tasks  # noqa: F401 - registers tool (T017)
from mcp_server.tools import complete_task  # noqa: F401 - registers tool (T019)
from mcp_server.tools import delete_task  # noqa: F401 - registers tool (T021)
from mcp_server.tools import update_task  # noqa: F401 - registers tool (T023)

settings = get_settings()

# Configure structured logging on module load
configure_logging()
logger = get_logger("mcp_server")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Startup:
    - Initialize database tables
    - Initialize agent with MCP tools (Task T013)
    - Log startup message

    Shutdown:
    - Log shutdown message
    """
    # Startup
    try:
        logger.info("mcp_server_starting", port=settings.mcp_server_port)
        await init_db()
        logger.info("database_initialized")

        # Task T013: Initialize OpenAI Agents SDK with OpenRouter at startup
        if AGENT_AVAILABLE and initialize_agents_sdk is not None:
            agent_ready = await initialize_agents_sdk()
            if agent_ready:
                logger.info("agents_sdk_ready")
            else:
                logger.warning("agents_sdk_not_ready")
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
    Task T007: Includes agent status when agent module is available.
    """
    response = {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment,
    }

    # Task T007: Add agent status if agent module is available
    if AGENT_AVAILABLE:
        try:
            agent_settings = get_agent_settings()
            response["agent_status"] = "ready" if agent_settings.is_configured else "not_configured"
            response["agent_model"] = agent_settings.agent_model
        except Exception:
            response["agent_status"] = "error"

    return response


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
        # Pydantic validation error - convert to serializable format
        errors = []
        for err in e.errors():
            error_info = {
                "loc": err.get("loc", []),
                "msg": err.get("msg", "Unknown error"),
                "type": err.get("type", "unknown"),
            }
            errors.append(error_info)

        return {
            "status": "error",
            "error": {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Invalid parameters",
                "details": {"errors": errors},
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


# =============================================================================
# Task T020-T022: Chat and Conversation Endpoints
# =============================================================================


@app.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    """Send message to agent and get response.

    Task T020: Main chat endpoint per hackathon spec.
    Hackathon compliance: POST /api/{user_id}/chat with user_id in URL path.
    Task T001-T002: Robust error handling - never returns 500.

    Args:
        user_id: User's unique identifier (UUID string) from URL path
        request: Chat request with message and optional conversation_id
        db: Database session (injected)

    Returns:
        ChatResponse with message, conversation_id, and optional tool_calls.
        On error: Returns 200 with error flag (never 500).
    """
    from uuid import UUID

    # Validate user_id is a valid UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "code": "INVALID_USER_ID",
                "message": "user_id must be a valid UUID",
            },
        )

    # T003: Debug log - request received
    logger.debug(
        "chat_request_received",
        user_id=user_id,
        conversation_id=str(request.conversation_id) if request.conversation_id else None,
        message_length=len(request.message),
    )

    if not AGENT_AVAILABLE or process_chat is None:
        logger.warning("chat_agent_unavailable")
        return JSONResponse(
            status_code=503,
            content={
                "error": True,
                "code": "AGENT_UNAVAILABLE",
                "message": "AI assistant is temporarily unavailable. Please try again later.",
            },
        )

    try:
        # T003: Debug log - calling process_chat
        logger.debug(
            "chat_processing_start",
            user_id=user_id,
        )

        response = await process_chat(
            message=request.message,
            user_id=user_uuid,
            db=db,
            conversation_id=request.conversation_id,
            auth_token=authorization,
        )

        # T003: Debug log - response built
        logger.debug(
            "chat_processing_complete",
            user_id=user_id,
            conversation_id=str(response.conversation_id),
            has_tool_calls=bool(response.tool_calls),
        )

        return response.model_dump(mode="json")

    except Exception as e:
        # T001: Log full error with traceback
        error_traceback = traceback.format_exc()
        logger.error(
            "chat_endpoint_failed",
            error=str(e),
            error_type=type(e).__name__,
            user_id=user_id,
            conversation_id=str(request.conversation_id) if request.conversation_id else None,
            traceback=error_traceback,
        )

        # T002: Return graceful error response (200 with error flag, never 500)
        error_message = f"AI failed: {str(e)}" if settings.is_development else "AI assistant encountered an error. Please try again."
        return {
            "error": True,
            "code": "CHAT_FAILED",
            "message": error_message,
            "conversation_id": str(request.conversation_id) if request.conversation_id else None,
            "details": {"error": str(e), "type": type(e).__name__} if settings.is_development else None,
        }


@app.get("/conversations")
async def list_conversations(
    user_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List user's conversations.

    Task T021: List conversations endpoint per contracts/agent-api.yaml.

    Args:
        user_id: User's unique identifier (UUID string)
        limit: Maximum conversations to return (1-100, default 20)
        db: Database session (injected)

    Returns:
        List of conversation summaries
    """
    if not AGENT_AVAILABLE or get_user_conversations is None:
        return JSONResponse(
            status_code=503,
            content={
                "error": "AGENT_UNAVAILABLE",
                "message": "Agent module is not available",
            },
        )

    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
        limit = max(1, min(100, limit))

        conversations = await get_user_conversations(db, user_uuid, limit)

        # Convert UUIDs and datetimes to strings for JSON serialization
        result = []
        for conv in conversations:
            result.append({
                "id": str(conv["id"]),
                "created_at": conv["created_at"].isoformat(),
                "last_activity": conv["last_activity"].isoformat(),
                "message_count": conv["message_count"],
                "preview": conv["preview"],
            })

        return {"conversations": result}

    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "error": "INVALID_USER_ID",
                "message": "user_id must be a valid UUID",
            },
        )
    except Exception as e:
        logger.error(
            "list_conversations_failed",
            error=str(e),
            user_id=user_id,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "LIST_FAILED",
                "message": "Failed to list conversations",
            },
        )


@app.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    user_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get messages in a conversation.

    Task T022: Get conversation messages endpoint per contracts/agent-api.yaml.

    Args:
        conversation_id: Conversation UUID
        user_id: User's unique identifier (for ownership verification)
        limit: Maximum messages to return (1-200, default 50)
        db: Database session (injected)

    Returns:
        List of messages or 404 if not found/unauthorized
    """
    if not AGENT_AVAILABLE or get_conversation_messages is None:
        return JSONResponse(
            status_code=503,
            content={
                "error": "AGENT_UNAVAILABLE",
                "message": "Agent module is not available",
            },
        )

    from uuid import UUID

    try:
        conv_uuid = UUID(conversation_id)
        user_uuid = UUID(user_id)
        limit = max(1, min(200, limit))

        messages = await get_conversation_messages(db, conv_uuid, user_uuid, limit)

        if messages is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "NOT_FOUND",
                    "message": "Conversation not found or you don't have access",
                },
            )

        # Convert UUIDs and datetimes to strings for JSON serialization
        result = []
        for msg in messages:
            result.append({
                "id": str(msg["id"]),
                "role": msg["role"],
                "content": msg["content"],
                "created_at": msg["created_at"].isoformat(),
            })

        return {"messages": result}

    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "error": "INVALID_UUID",
                "message": "conversation_id and user_id must be valid UUIDs",
            },
        )
    except Exception as e:
        logger.error(
            "get_messages_failed",
            error=str(e),
            conversation_id=conversation_id,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "GET_FAILED",
                "message": "Failed to get messages",
            },
        )


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
