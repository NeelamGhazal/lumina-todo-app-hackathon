# Task T018-T019: Chat Orchestration
# Updated: Use OpenAI Agents SDK instead of manual client
"""Main chat orchestration for the agent.

This module provides the core chat processing logic using the
OpenAI Agents SDK with OpenRouter backend.

References:
- spec.md: FR-020-026 (agent requirements)
- hackathon spec: Must use OpenAI Agents SDK
"""

import traceback
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from agent.conversation import (
    get_or_create_conversation,
    get_context_messages,
    store_message,
    update_conversation_activity,
)
from agent.agent_sdk import run_agent, is_agent_ready
from agent.schemas import ChatResponse, ToolCallSummary

logger = structlog.get_logger(__name__)


async def process_chat(
    message: str,
    user_id: UUID,
    db: AsyncSession,
    conversation_id: UUID | None = None,
    auth_token: str | None = None,
) -> ChatResponse:
    """Process a chat message and return agent response.

    Main orchestration function that:
    1. Gets or creates conversation
    2. Builds context from message history
    3. Runs OpenAI Agents SDK with MCP tools
    4. Returns natural language response

    Args:
        message: User's message
        user_id: User's unique identifier
        db: Database session
        conversation_id: Optional conversation to continue

    Returns:
        ChatResponse with agent's reply and metadata
    """
    logger.info(
        "chat_processing_started",
        user_id=str(user_id),
        conversation_id=str(conversation_id) if conversation_id else None,
        message_length=len(message),
    )

    # Step 1: Get or create conversation
    conversation = await get_or_create_conversation(
        db, user_id, conversation_id
    )

    # Step 2: Store user message
    await store_message(db, conversation.id, "user", message)

    # Step 3: Commit user message BEFORE running agent
    # This releases the database lock so MCP tools can write
    await db.commit()

    # Step 4: Build context messages
    context = await get_context_messages(db, conversation.id)

    # Step 5: Run agent with OpenAI Agents SDK
    tool_calls_summary: list[ToolCallSummary] = []
    response_content: str

    try:
        if not is_agent_ready():
            logger.warning("agent_not_ready")
            response_content = "I'm sorry, the AI assistant is not available right now. Please try again later."
        else:
            # Run the agent
            response_text, tool_calls = await run_agent(
                message=message,
                user_id=user_id,
                conversation_history=context,
                auth_token=auth_token,
            )
            response_content = response_text

            # Convert tool calls to summary format
            for tc in tool_calls:
                tool_calls_summary.append(
                    ToolCallSummary(
                        tool=tc.get("tool", "unknown"),
                        success=tc.get("success", True),
                        result_preview=tc.get("result_preview"),
                    )
                )

    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(
            "chat_processing_failed",
            error=str(e),
            error_type=type(e).__name__,
            conversation_id=str(conversation.id),
            user_id=str(user_id),
            traceback=error_traceback,
        )
        response_content = "I'm sorry, I encountered an error processing your request. Please try again."

    # Step 6: Store assistant response
    await store_message(db, conversation.id, "assistant", response_content)

    # Step 7: Update conversation activity
    await update_conversation_activity(db, conversation.id)

    # Step 8: Commit remaining changes
    await db.commit()

    logger.info(
        "chat_processing_completed",
        conversation_id=str(conversation.id),
        tool_calls=len(tool_calls_summary),
        response_length=len(response_content),
    )

    return ChatResponse(
        message=response_content,
        conversation_id=conversation.id,
        tool_calls=tool_calls_summary if tool_calls_summary else None,
    )


# Export public API
__all__ = [
    "process_chat",
]
