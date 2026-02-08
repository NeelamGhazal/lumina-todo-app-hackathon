# Task T026: Agent Conversation Tests
"""Tests for conversation management module.

Tests:
- Session lifecycle (30-min timeout)
- Message storage and retrieval
- Context building (10 messages)
- Conversation listing
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from mcp_server.models import Conversation, Message, MessageRole
from agent.conversation import (
    get_or_create_conversation,
    get_context_messages,
    store_message,
    update_conversation_activity,
    get_user_conversations,
    get_conversation_messages,
)


class TestGetOrCreateConversation:
    """Tests for get_or_create_conversation function."""

    @pytest.mark.asyncio
    async def test_creates_new_conversation(self, test_session: AsyncSession):
        """Test creating a new conversation when none exists."""
        user_id = uuid4()

        conversation = await get_or_create_conversation(test_session, user_id)

        assert conversation is not None
        assert conversation.user_id == user_id
        assert conversation.id is not None

    @pytest.mark.asyncio
    async def test_reuses_active_conversation(self, test_session: AsyncSession):
        """Test reusing an existing active conversation."""
        user_id = uuid4()

        # Create first conversation
        conv1 = await get_or_create_conversation(test_session, user_id)
        await test_session.flush()

        # Get conversation again - should reuse
        conv2 = await get_or_create_conversation(test_session, user_id)

        assert conv1.id == conv2.id

    @pytest.mark.asyncio
    async def test_creates_new_after_timeout(self, test_session: AsyncSession):
        """Test creating new conversation after timeout."""
        user_id = uuid4()

        # Create conversation with old last_activity
        old_conv = Conversation(
            user_id=user_id,
            last_activity=datetime.now(UTC) - timedelta(minutes=35),
        )
        test_session.add(old_conv)
        await test_session.flush()

        # Get conversation - should create new one
        new_conv = await get_or_create_conversation(test_session, user_id)

        assert new_conv.id != old_conv.id

    @pytest.mark.asyncio
    async def test_continues_specific_conversation(self, test_session: AsyncSession):
        """Test continuing a specific conversation by ID."""
        user_id = uuid4()

        # Create two conversations
        conv1 = Conversation(user_id=user_id)
        conv2 = Conversation(user_id=user_id)
        test_session.add(conv1)
        test_session.add(conv2)
        await test_session.flush()

        # Request specific conversation
        result = await get_or_create_conversation(
            test_session, user_id, conversation_id=conv1.id
        )

        assert result.id == conv1.id

    @pytest.mark.asyncio
    async def test_ignores_other_users_conversations(self, test_session: AsyncSession):
        """Test that other users' conversations are not returned."""
        user1_id = uuid4()
        user2_id = uuid4()

        # Create conversation for user1
        conv1 = Conversation(user_id=user1_id)
        test_session.add(conv1)
        await test_session.flush()

        # Get conversation for user2 - should create new
        conv2 = await get_or_create_conversation(test_session, user2_id)

        assert conv2.id != conv1.id
        assert conv2.user_id == user2_id


class TestGetContextMessages:
    """Tests for get_context_messages function."""

    @pytest.mark.asyncio
    async def test_returns_empty_for_new_conversation(self, test_session: AsyncSession):
        """Test empty list for conversation with no messages."""
        conv = Conversation(user_id=uuid4())
        test_session.add(conv)
        await test_session.flush()

        messages = await get_context_messages(test_session, conv.id)

        assert messages == []

    @pytest.mark.asyncio
    async def test_returns_messages_in_order(self, test_session: AsyncSession):
        """Test messages are returned in chronological order."""
        conv = Conversation(user_id=uuid4())
        test_session.add(conv)
        await test_session.flush()

        # Add messages
        for i in range(3):
            msg = Message(
                conversation_id=conv.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}",
            )
            test_session.add(msg)
        await test_session.flush()

        messages = await get_context_messages(test_session, conv.id)

        assert len(messages) == 3
        assert messages[0]["content"] == "Message 0"
        assert messages[2]["content"] == "Message 2"

    @pytest.mark.asyncio
    async def test_respects_limit(self, test_session: AsyncSession):
        """Test message limit is respected."""
        conv = Conversation(user_id=uuid4())
        test_session.add(conv)
        await test_session.flush()

        # Add 15 messages
        for i in range(15):
            msg = Message(
                conversation_id=conv.id,
                role=MessageRole.USER,
                content=f"Message {i}",
            )
            test_session.add(msg)
        await test_session.flush()

        # Get with limit of 5
        messages = await get_context_messages(test_session, conv.id, limit=5)

        assert len(messages) == 5

    @pytest.mark.asyncio
    async def test_returns_openai_format(self, test_session: AsyncSession):
        """Test messages are in OpenAI format."""
        conv = Conversation(user_id=uuid4())
        test_session.add(conv)
        await test_session.flush()

        msg = Message(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Hello",
        )
        test_session.add(msg)
        await test_session.flush()

        messages = await get_context_messages(test_session, conv.id)

        assert messages[0] == {"role": "user", "content": "Hello"}


class TestStoreMessage:
    """Tests for store_message function."""

    @pytest.mark.asyncio
    async def test_stores_user_message(self, test_session: AsyncSession):
        """Test storing a user message."""
        conv = Conversation(user_id=uuid4())
        test_session.add(conv)
        await test_session.flush()

        message = await store_message(
            test_session, conv.id, "user", "Hello, I need help"
        )

        assert message.id is not None
        assert message.role == MessageRole.USER
        assert message.content == "Hello, I need help"

    @pytest.mark.asyncio
    async def test_stores_assistant_message(self, test_session: AsyncSession):
        """Test storing an assistant message."""
        conv = Conversation(user_id=uuid4())
        test_session.add(conv)
        await test_session.flush()

        message = await store_message(
            test_session, conv.id, "assistant", "I can help!"
        )

        assert message.role == MessageRole.ASSISTANT
        assert message.content == "I can help!"


class TestUpdateConversationActivity:
    """Tests for update_conversation_activity function."""

    @pytest.mark.asyncio
    async def test_updates_last_activity(self, test_session: AsyncSession):
        """Test last_activity is updated."""
        old_time = datetime.now(UTC) - timedelta(hours=1)
        conv = Conversation(user_id=uuid4(), last_activity=old_time)
        test_session.add(conv)
        await test_session.flush()

        await update_conversation_activity(test_session, conv.id)
        await test_session.refresh(conv)

        # Compare with timezone-aware datetime
        assert conv.last_activity.replace(tzinfo=UTC) > old_time


class TestGetUserConversations:
    """Tests for get_user_conversations function."""

    @pytest.mark.asyncio
    async def test_returns_user_conversations(self, test_session: AsyncSession):
        """Test listing user's conversations."""
        user_id = uuid4()

        # Create conversations
        for i in range(3):
            conv = Conversation(user_id=user_id)
            test_session.add(conv)
        await test_session.flush()

        conversations = await get_user_conversations(test_session, user_id)

        assert len(conversations) == 3

    @pytest.mark.asyncio
    async def test_includes_message_count(self, test_session: AsyncSession):
        """Test message count is included."""
        user_id = uuid4()
        conv = Conversation(user_id=user_id)
        test_session.add(conv)
        await test_session.flush()

        # Add messages
        for i in range(5):
            msg = Message(
                conversation_id=conv.id,
                role=MessageRole.USER,
                content=f"Message {i}",
            )
            test_session.add(msg)
        await test_session.flush()

        conversations = await get_user_conversations(test_session, user_id)

        assert conversations[0]["message_count"] == 5

    @pytest.mark.asyncio
    async def test_respects_limit(self, test_session: AsyncSession):
        """Test conversation limit is respected."""
        user_id = uuid4()

        # Create many conversations
        for i in range(10):
            conv = Conversation(user_id=user_id)
            test_session.add(conv)
        await test_session.flush()

        conversations = await get_user_conversations(test_session, user_id, limit=5)

        assert len(conversations) == 5


class TestGetConversationMessages:
    """Tests for get_conversation_messages function."""

    @pytest.mark.asyncio
    async def test_returns_messages(self, test_session: AsyncSession):
        """Test getting conversation messages."""
        user_id = uuid4()
        conv = Conversation(user_id=user_id)
        test_session.add(conv)
        await test_session.flush()

        msg = Message(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Hello",
        )
        test_session.add(msg)
        await test_session.flush()

        messages = await get_conversation_messages(
            test_session, conv.id, user_id
        )

        assert messages is not None
        assert len(messages) == 1
        assert messages[0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_returns_none_for_unauthorized(self, test_session: AsyncSession):
        """Test returns None for unauthorized access."""
        user1_id = uuid4()
        user2_id = uuid4()

        conv = Conversation(user_id=user1_id)
        test_session.add(conv)
        await test_session.flush()

        # Try to access as different user
        messages = await get_conversation_messages(
            test_session, conv.id, user2_id
        )

        assert messages is None

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent(self, test_session: AsyncSession):
        """Test returns None for nonexistent conversation."""
        user_id = uuid4()
        fake_conv_id = uuid4()

        messages = await get_conversation_messages(
            test_session, fake_conv_id, user_id
        )

        assert messages is None
