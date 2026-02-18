# Task T001: Create Chat Router Scaffold
# Task T002-T005: Chat API endpoints with proxy to Part 2 OpenRouter Agent
"""Chat router for proxying requests to the OpenRouter Agent.

Provides:
- POST /api/chat - Send message to AI assistant (proxies to Part 2 agent)
- GET /api/chat/history - Get conversation history
- GET /api/chat/conversations - List user's conversations
- GET /api/chat/health - Health check for chat subsystem

References:
- spec.md: FR-001-005 (chat interface requirements)
- plan.md: ADR-011 (direct connection to Part 2 agent)
- contracts/frontend-api.yaml: API contract definitions
"""

import logging
from typing import Any
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession

logger = logging.getLogger(__name__)
settings = get_settings()

# Part 2 OpenRouter Agent settings
AGENT_BASE_URL = settings.agent_base_url
AGENT_TIMEOUT = 30.0  # 30 second timeout for AI responses

router = APIRouter(prefix="/chat", tags=["chat"])


# =============================================================================
# Request/Response Schemas
# =============================================================================


class ChatRequest(BaseModel):
    """Request schema for sending a chat message."""

    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    conversation_id: str | None = Field(None, description="Optional conversation ID to continue")


class ToolCallSummary(BaseModel):
    """Summary of a tool call made by the AI."""

    tool: str
    success: bool
    result_preview: str | None = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    message: str = Field(..., description="AI assistant response")
    conversation_id: str = Field(..., description="Conversation ID for continuity")
    tool_calls: list[ToolCallSummary] | None = Field(None, description="Tools used (if any)")


class Message(BaseModel):
    """Message in a conversation."""

    id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: str  # ISO 8601 datetime


class ConversationSummary(BaseModel):
    """Summary of a conversation for list view."""

    id: str
    created_at: str
    last_activity: str
    message_count: int
    preview: str | None = None


# =============================================================================
# Task T001: Health Check Endpoint
# =============================================================================


@router.get("/health")
async def chat_health_check() -> dict[str, Any]:
    """Health check for chat subsystem.

    Verifies:
    - This router is accessible
    - Part 2 agent is reachable (if configured)
    """
    result = {
        "status": "ok",
        "subsystem": "chat",
        "agent_url": AGENT_BASE_URL,
    }

    # Check if Part 2 agent is reachable
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{AGENT_BASE_URL}/health")
            if response.status_code == 200:
                agent_data = response.json()
                result["agent_status"] = agent_data.get("agent_status", "unknown")
                result["agent_reachable"] = True
            else:
                result["agent_status"] = "error"
                result["agent_reachable"] = False
    except Exception as e:
        result["agent_status"] = "unavailable"
        result["agent_reachable"] = False
        result["agent_error"] = str(e)

    return result


# =============================================================================
# Task T002: POST /api/chat - Send Message (Proxy to Part 2 Agent)
# =============================================================================


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: CurrentUser,
) -> ChatResponse:
    """Send message to AI assistant via Part 2 OpenRouter Agent.

    Proxies the request to the Part 2 agent running on port 8001,
    passing the authenticated user's ID for context.

    Args:
        request: Chat message and optional conversation_id
        current_user: Authenticated user (from JWT)

    Returns:
        AI response with conversation_id for continuity

    Raises:
        HTTPException 503: If Part 2 agent is unavailable
        HTTPException 500: If chat processing fails
    """
    user_id = str(current_user.id)

    logger.info(
        "chat_request",
        extra={
            "user_id": user_id,
            "message_length": len(request.message),
            "has_conversation_id": request.conversation_id is not None,
        },
    )

    try:
        async with httpx.AsyncClient(timeout=AGENT_TIMEOUT) as client:
            # Build request payload for Part 2 agent
            # Per hackathon spec: user_id is in URL path, not body
            payload = {
                "message": request.message,
            }
            if request.conversation_id:
                payload["conversation_id"] = request.conversation_id

            # Forward to Part 2 agent at /api/{user_id}/chat (hackathon spec)
            response = await client.post(
                f"{AGENT_BASE_URL}/api/{user_id}/chat",
                json=payload,
            )

            if response.status_code == 503:
                logger.error("agent_unavailable", extra={"status": 503})
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "error": "AGENT_UNAVAILABLE",
                        "message": "AI assistant is temporarily unavailable. Please try again.",
                    },
                )

            if response.status_code != 200:
                logger.error(
                    "agent_error",
                    extra={"status": response.status_code, "body": response.text[:500]},
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "CHAT_FAILED",
                        "message": "Failed to get response from AI assistant.",
                    },
                )

            data = response.json()

            # Map response to our schema
            tool_calls = None
            if data.get("tool_calls"):
                tool_calls = [
                    ToolCallSummary(
                        tool=tc.get("tool", "unknown"),
                        success=tc.get("success", False),
                        result_preview=tc.get("result_preview"),
                    )
                    for tc in data["tool_calls"]
                ]

            return ChatResponse(
                message=data["message"],
                conversation_id=data["conversation_id"],
                tool_calls=tool_calls,
            )

    except httpx.TimeoutException:
        logger.error("agent_timeout", extra={"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "error": "TIMEOUT",
                "message": "AI assistant took too long to respond. Please try again.",
            },
        )
    except httpx.RequestError as e:
        logger.error("agent_connection_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AGENT_UNAVAILABLE",
                "message": "Cannot connect to AI assistant. Please try again later.",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("chat_error", extra={"user_id": user_id, "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            },
        )


# =============================================================================
# Task T003: GET /api/chat/history - Get Conversation Messages
# =============================================================================


@router.get("/history", response_model=dict[str, list[Message]])
async def get_chat_history(
    current_user: CurrentUser,
    conversation_id: str | None = None,
    limit: int = 50,
) -> dict[str, list[Message]]:
    """Get chat message history for the current user.

    If conversation_id is provided, returns messages from that conversation.
    Otherwise, returns messages from the most recent conversation.

    Args:
        current_user: Authenticated user (from JWT)
        conversation_id: Optional specific conversation to fetch
        limit: Maximum messages to return (1-200, default 50)

    Returns:
        List of messages in chronological order

    Raises:
        HTTPException 404: If conversation not found or unauthorized
        HTTPException 503: If Part 2 agent is unavailable
    """
    user_id = str(current_user.id)
    limit = max(1, min(200, limit))

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # If no conversation_id, get the most recent one
            if not conversation_id:
                conv_response = await client.get(
                    f"{AGENT_BASE_URL}/conversations",
                    params={"user_id": user_id, "limit": 1},
                )

                if conv_response.status_code != 200:
                    # No conversations yet - return empty
                    return {"messages": []}

                conversations = conv_response.json().get("conversations", [])
                if not conversations:
                    return {"messages": []}

                conversation_id = conversations[0]["id"]

            # Fetch messages from the conversation
            response = await client.get(
                f"{AGENT_BASE_URL}/conversations/{conversation_id}/messages",
                params={"user_id": user_id, "limit": limit},
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "NOT_FOUND",
                        "message": "Conversation not found or you don't have access.",
                    },
                )

            if response.status_code != 200:
                logger.error(
                    "history_fetch_error",
                    extra={"status": response.status_code, "user_id": user_id},
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "FETCH_FAILED",
                        "message": "Failed to load chat history.",
                    },
                )

            data = response.json()
            messages = [
                Message(
                    id=msg["id"],
                    role=msg["role"],
                    content=msg["content"],
                    created_at=msg["created_at"],
                )
                for msg in data.get("messages", [])
            ]

            return {"messages": messages}

    except httpx.RequestError as e:
        logger.error("history_connection_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AGENT_UNAVAILABLE",
                "message": "Cannot connect to chat service.",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("history_error", extra={"user_id": user_id, "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            },
        )


# =============================================================================
# Task T003 (continued): GET /api/chat/conversations - List Conversations
# =============================================================================


@router.get("/conversations", response_model=dict[str, list[ConversationSummary]])
async def list_conversations(
    current_user: CurrentUser,
    limit: int = 20,
) -> dict[str, list[ConversationSummary]]:
    """List user's conversations.

    Args:
        current_user: Authenticated user (from JWT)
        limit: Maximum conversations to return (1-100, default 20)

    Returns:
        List of conversation summaries sorted by last activity

    Raises:
        HTTPException 503: If Part 2 agent is unavailable
    """
    user_id = str(current_user.id)
    limit = max(1, min(100, limit))

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{AGENT_BASE_URL}/conversations",
                params={"user_id": user_id, "limit": limit},
            )

            if response.status_code != 200:
                logger.error(
                    "conversations_fetch_error",
                    extra={"status": response.status_code, "user_id": user_id},
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "FETCH_FAILED",
                        "message": "Failed to load conversations.",
                    },
                )

            data = response.json()
            conversations = [
                ConversationSummary(
                    id=conv["id"],
                    created_at=conv["created_at"],
                    last_activity=conv["last_activity"],
                    message_count=conv["message_count"],
                    preview=conv.get("preview"),
                )
                for conv in data.get("conversations", [])
            ]

            return {"conversations": conversations}

    except httpx.RequestError as e:
        logger.error("conversations_connection_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "AGENT_UNAVAILABLE",
                "message": "Cannot connect to chat service.",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("conversations_error", extra={"user_id": user_id, "error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            },
        )
