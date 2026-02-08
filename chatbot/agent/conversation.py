# Task T014-T017: Conversation Management
"""Conversation and session management for the agent.

This module provides:
- Session lifecycle management (30-min timeout)
- Message storage and retrieval
- Context building for LLM requests

References:
- spec.md: FR-043 (30-min timeout), FR-046 (10 messages context)
- plan.md: ADR-006 (database-only context storage)
- data-model.md: Conversation, Message entities
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Conversation, Message, MessageRole
from agent.config import get_agent_settings

logger = structlog.get_logger(__name__)


# === T014: Get or Create Conversation ===


def _ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (UTC).

    SQLite returns naive datetimes, but we need to compare with UTC times.
    This normalizes the datetime to be timezone-aware.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


async def get_or_create_conversation(
    db: AsyncSession,
    user_id: UUID,
    conversation_id: UUID | None = None,
) -> Conversation:
    """Get existing conversation or create a new one.

    Session rules (per FR-043):
    - If conversation_id provided, use it if valid and not expired
    - If no conversation_id, find most recent active conversation
    - Create new conversation if none found or last one expired (30-min timeout)

    Args:
        db: Database session
        user_id: User's unique identifier
        conversation_id: Optional specific conversation to continue

    Returns:
        Active conversation for the user
    """
    settings = get_agent_settings()
    timeout = timedelta(minutes=settings.session_timeout_minutes)
    now = datetime.now(UTC)
    cutoff = now - timeout

    # If specific conversation requested, try to use it
    if conversation_id:
        conversation = await _get_conversation_by_id(db, conversation_id, user_id)
        if conversation:
            # Check if still active (within timeout)
            # Note: SQLite returns naive datetimes, so we normalize to UTC
            last_activity = _ensure_utc(conversation.last_activity)
            if last_activity >= cutoff:
                logger.debug(
                    "conversation_continued",
                    conversation_id=str(conversation_id),
                    user_id=str(user_id),
                )
                return conversation
            else:
                logger.debug(
                    "conversation_expired",
                    conversation_id=str(conversation_id),
                    last_activity=last_activity.isoformat(),
                )

    # Find most recent active conversation for user
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.last_activity >= cutoff)
        .order_by(desc(Conversation.last_activity))
        .limit(1)
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if conversation:
        logger.debug(
            "conversation_found",
            conversation_id=str(conversation.id),
            user_id=str(user_id),
        )
        return conversation

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    await db.flush()

    logger.info(
        "conversation_created",
        conversation_id=str(conversation.id),
        user_id=str(user_id),
    )

    return conversation


async def _get_conversation_by_id(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
) -> Conversation | None:
    """Get conversation by ID if owned by user.

    Args:
        db: Database session
        conversation_id: Conversation ID
        user_id: User ID (for ownership check)

    Returns:
        Conversation if found and owned by user, None otherwise
    """
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# === T015: Get Context Messages ===


async def get_context_messages(
    db: AsyncSession,
    conversation_id: UUID,
    limit: int | None = None,
) -> list[dict]:
    """Get recent messages for LLM context.

    Retrieves the last N messages from the conversation,
    formatted for OpenAI's messages array.

    Args:
        db: Database session
        conversation_id: Conversation ID
        limit: Max messages to retrieve (default from settings)

    Returns:
        List of message dicts in OpenAI format
    """
    settings = get_agent_settings()
    if limit is None:
        limit = settings.context_message_limit

    # Get messages ordered by creation time (oldest first for context)
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    # Reverse to get chronological order (oldest first)
    messages = list(reversed(messages))

    # Convert to OpenAI format
    context = [
        {"role": msg.role.value, "content": msg.content}
        for msg in messages
    ]

    logger.debug(
        "context_messages_retrieved",
        conversation_id=str(conversation_id),
        count=len(context),
    )

    return context


# === T016: Store Message ===


async def store_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
) -> Message:
    """Store a message in the conversation.

    Args:
        db: Database session
        conversation_id: Conversation ID
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Created Message instance
    """
    message_role = MessageRole(role)
    message = Message(
        conversation_id=conversation_id,
        role=message_role,
        content=content,
    )
    db.add(message)
    await db.flush()

    logger.debug(
        "message_stored",
        message_id=str(message.id),
        conversation_id=str(conversation_id),
        role=role,
    )

    return message


# === T017: Update Conversation Activity ===


async def update_conversation_activity(
    db: AsyncSession,
    conversation_id: UUID,
) -> None:
    """Update conversation's last_activity timestamp.

    Called after storing messages to keep session alive.

    Args:
        db: Database session
        conversation_id: Conversation ID
    """
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if conversation:
        conversation.last_activity = datetime.now(UTC)
        await db.flush()

        logger.debug(
            "conversation_activity_updated",
            conversation_id=str(conversation_id),
        )


# === Helper Functions for Endpoints ===


async def get_user_conversations(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 20,
) -> list[dict]:
    """Get user's conversations with summary info.

    Args:
        db: Database session
        user_id: User ID
        limit: Max conversations to return

    Returns:
        List of conversation summaries
    """
    # Get conversations with message count
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.last_activity))
        .limit(limit)
    )
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    summaries = []
    for conv in conversations:
        # Get message count and first user message for preview
        count_stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conv.id)
        )
        count_result = await db.execute(count_stmt)
        message_count = count_result.scalar() or 0

        # Get first user message for preview
        preview_stmt = (
            select(Message.content)
            .where(Message.conversation_id == conv.id)
            .where(Message.role == MessageRole.USER)
            .order_by(Message.created_at)
            .limit(1)
        )
        preview_result = await db.execute(preview_stmt)
        first_message = preview_result.scalar_one_or_none()
        preview = first_message[:100] if first_message else None

        summaries.append({
            "id": conv.id,
            "created_at": conv.created_at,
            "last_activity": conv.last_activity,
            "message_count": message_count,
            "preview": preview,
        })

    return summaries


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    limit: int = 50,
) -> list[dict] | None:
    """Get all messages in a conversation.

    Args:
        db: Database session
        conversation_id: Conversation ID
        user_id: User ID (for ownership check)
        limit: Max messages to return

    Returns:
        List of messages or None if conversation not found/unauthorized
    """
    # Verify ownership
    conversation = await _get_conversation_by_id(db, conversation_id, user_id)
    if not conversation:
        return None

    # Get messages
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return [
        {
            "id": msg.id,
            "role": msg.role.value,
            "content": msg.content,
            "created_at": msg.created_at,
        }
        for msg in messages
    ]


# Export public API
__all__ = [
    "get_or_create_conversation",
    "get_context_messages",
    "store_message",
    "update_conversation_activity",
    "get_user_conversations",
    "get_conversation_messages",
]
