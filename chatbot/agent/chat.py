# Task T018-T019: Chat Orchestration
"""Main chat orchestration for the agent.

This module provides the core chat processing logic:
- Message handling and context building
- LLM interaction via OpenRouter
- Tool execution loop with max rounds limit
- Response formatting

References:
- spec.md: FR-020-026 (agent requirements)
- plan.md: ADR-005 (manual tool execution), risk mitigation (max 5 rounds)
- data-model.md: Data flow section
"""

import json
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from agent.config import get_agent_settings
from agent.client import get_openrouter_client
from agent.conversation import (
    get_or_create_conversation,
    get_context_messages,
    store_message,
    update_conversation_activity,
)
from agent.tools import (
    execute_mcp_tool,
    build_tool_result_message,
    format_tool_error_for_user,
    MCPToolError,
)
from agent.schemas import ChatResponse, ToolCallSummary

logger = structlog.get_logger(__name__)


# === T018: Main Chat Processing ===


async def process_chat(
    message: str,
    user_id: UUID,
    db: AsyncSession,
    conversation_id: UUID | None = None,
) -> ChatResponse:
    """Process a chat message and return agent response.

    Main orchestration function that:
    1. Gets or creates conversation
    2. Builds context from message history
    3. Sends to LLM with tool definitions
    4. Executes any tool calls
    5. Returns natural language response

    Args:
        message: User's message
        user_id: User's unique identifier
        db: Database session
        conversation_id: Optional conversation to continue

    Returns:
        ChatResponse with agent's reply and metadata
    """
    settings = get_agent_settings()
    client = get_openrouter_client()

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

    # Step 3: Build context messages
    context = await get_context_messages(db, conversation.id)

    # Step 4: Build messages array for LLM
    messages = _build_messages(settings.agent_instructions, context, message)

    # Step 5: Execute chat with tool loop
    tool_calls_summary: list[ToolCallSummary] = []

    try:
        response_content, tool_calls_summary = await _execute_chat_with_tools(
            client, messages, user_id, settings.max_tool_rounds
        )
    except Exception as e:
        logger.error(
            "chat_processing_failed",
            error=str(e),
            conversation_id=str(conversation.id),
        )
        response_content = "I'm sorry, I encountered an error processing your request. Please try again."

    # Step 6: Store assistant response
    await store_message(db, conversation.id, "assistant", response_content)

    # Step 7: Update conversation activity
    await update_conversation_activity(db, conversation.id)

    # Step 8: Commit transaction
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


def _build_messages(
    system_instructions: str,
    context: list[dict],
    current_message: str,
) -> list[dict[str, Any]]:
    """Build messages array for LLM.

    Args:
        system_instructions: System prompt for the agent
        context: Previous messages from conversation
        current_message: Current user message

    Returns:
        List of messages in OpenAI format
    """
    messages = [
        {"role": "system", "content": system_instructions},
    ]

    # Add context messages (already includes current if from DB)
    # But we store user message before getting context, so it's included
    messages.extend(context)

    return messages


# === T019: Tool Execution Loop ===


async def _execute_chat_with_tools(
    client: Any,
    messages: list[dict[str, Any]],
    user_id: UUID,
    max_rounds: int,
) -> tuple[str, list[ToolCallSummary]]:
    """Execute chat with tool calling loop.

    Implements the manual tool execution pattern (ADR-005):
    1. Send messages to LLM
    2. If LLM requests tool calls, execute them
    3. Submit results back to LLM
    4. Repeat until LLM gives final response or max rounds reached

    Args:
        client: OpenRouter client
        messages: Initial messages array
        user_id: User ID for tool execution
        max_rounds: Maximum tool execution rounds

    Returns:
        Tuple of (response_content, tool_call_summaries)
    """
    tool_summaries: list[ToolCallSummary] = []
    current_messages = messages.copy()
    round_count = 0

    while round_count < max_rounds:
        round_count += 1

        logger.debug(
            "tool_loop_round",
            round=round_count,
            message_count=len(current_messages),
        )

        # Get LLM response
        response = await client.create_chat_completion(current_messages)
        choice = response.choices[0]
        assistant_message = choice.message

        # Check if LLM is done (no tool calls)
        if choice.finish_reason == "stop" or not assistant_message.tool_calls:
            return assistant_message.content or "", tool_summaries

        # LLM wants to call tools
        logger.debug(
            "tool_calls_requested",
            count=len(assistant_message.tool_calls),
        )

        # Add assistant's message with tool calls to context
        current_messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_message.tool_calls
            ],
        })

        # Execute each tool call
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            logger.debug(
                "executing_tool",
                tool=tool_name,
                tool_call_id=tool_call.id,
            )

            try:
                result = await execute_mcp_tool(tool_name, arguments, user_id)
                tool_results.append(
                    build_tool_result_message(tool_call.id, result=result)
                )
                tool_summaries.append(
                    ToolCallSummary(
                        tool=tool_name,
                        success=True,
                        result_preview=_format_result_preview(tool_name, result),
                    )
                )
            except MCPToolError as e:
                error_message = format_tool_error_for_user(e)
                tool_results.append(
                    build_tool_result_message(tool_call.id, error=error_message)
                )
                tool_summaries.append(
                    ToolCallSummary(
                        tool=tool_name,
                        success=False,
                        result_preview=error_message,
                    )
                )

        # Add tool results to messages
        current_messages.extend(tool_results)

    # Max rounds reached - get final response without tools
    logger.warning(
        "tool_loop_max_rounds",
        rounds=max_rounds,
    )

    response = await client.create_chat_completion(
        current_messages, use_tools=False
    )
    return response.choices[0].message.content or "", tool_summaries


def _format_result_preview(tool_name: str, result: dict[str, Any]) -> str:
    """Format a brief preview of tool result.

    Args:
        tool_name: Name of the tool
        result: Tool execution result

    Returns:
        Brief description of result
    """
    if tool_name == "add_task":
        title = result.get("title", "task")
        return f"Created task: {title}"

    if tool_name == "list_tasks":
        tasks = result.get("tasks", [])
        return f"Found {len(tasks)} task(s)"

    if tool_name == "complete_task":
        status = result.get("status", "updated")
        title = result.get("title", "task")
        return f"Marked '{title}' as {status}"

    if tool_name == "delete_task":
        title = result.get("title", "task")
        return f"Deleted task: {title}"

    if tool_name == "update_task":
        title = result.get("title", "task")
        return f"Updated task: {title}"

    return "Operation completed"


# Export public API
__all__ = [
    "process_chat",
]
