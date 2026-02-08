# Task T005: Agent Schemas
"""Pydantic models for agent chat API.

These models define the request/response structure for the /chat endpoint
and related conversation endpoints.

References:
- data-model.md: Runtime Data Structures section
- contracts/agent-api.yaml: ChatRequest, ChatResponse, ToolCallSummary schemas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request to send message to agent.

    Attributes:
        message: User's natural language message (1-4000 chars)
        user_id: Authenticated user's ID
        conversation_id: Optional - continue specific conversation
    """

    message: str = Field(..., min_length=1, max_length=4000)
    user_id: UUID
    conversation_id: UUID | None = None


class ToolCallSummary(BaseModel):
    """Summary of a tool call made during response generation.

    Provides transparency about what tools were used without
    exposing internal details.

    Attributes:
        tool: Tool name (add_task, list_tasks, etc.)
        success: Whether the tool call succeeded
        result_preview: Brief description of result
    """

    tool: str
    success: bool
    result_preview: str | None = None


class ChatResponse(BaseModel):
    """Response from agent.

    Attributes:
        message: Agent's natural language response
        conversation_id: For continuing the conversation
        tool_calls: Optional summary of tools used
    """

    message: str
    conversation_id: UUID
    tool_calls: list[ToolCallSummary] | None = None


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing.

    Used by /conversations endpoint to show user's conversation history.

    Attributes:
        id: Conversation UUID
        created_at: When conversation started
        last_activity: Last message timestamp
        message_count: Total messages in conversation
        preview: First user message (truncated to 100 chars)
    """

    id: UUID
    created_at: datetime
    last_activity: datetime
    message_count: int
    preview: str | None = None


class MessageResponse(BaseModel):
    """Message for history viewing.

    Used by /conversations/{id}/messages endpoint.

    Attributes:
        id: Message UUID
        role: "user" or "assistant"
        content: Message text
        created_at: Timestamp
    """

    id: UUID
    role: str
    content: str
    created_at: datetime
