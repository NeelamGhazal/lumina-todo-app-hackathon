# Task T028-T032: Chat Integration Tests
"""Integration tests for chat endpoints.

These tests verify endpoint wiring and basic functionality.
Full integration testing requires:
- MCP server running
- OPENROUTER_API_KEY configured

Tests cover:
- T028 [US1]: Adding tasks via natural language
- T029 [US2]: Listing tasks via natural language
- T030 [US3/US4]: Completing and deleting tasks
- T031 [US5]: Updating tasks via natural language
- T032 [US6]: Multi-turn conversations with context
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestChatEndpoint:
    """Tests for /chat endpoint."""

    @pytest.mark.asyncio
    async def test_chat_endpoint_exists(self, client: AsyncClient):
        """Test /chat endpoint is registered."""
        user_id = str(uuid4())

        response = await client.post(
            "/chat",
            json={
                "message": "Hello",
                "user_id": user_id,
            },
        )

        # Should not be 404 (endpoint exists)
        # May be 503 if agent not configured, or 200 if working
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_chat_requires_message(self, client: AsyncClient):
        """Test /chat requires message field."""
        response = await client.post(
            "/chat",
            json={
                "user_id": str(uuid4()),
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_requires_user_id(self, client: AsyncClient):
        """Test /chat requires user_id field."""
        response = await client.post(
            "/chat",
            json={
                "message": "Hello",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_validates_user_id_format(self, client: AsyncClient):
        """Test /chat validates user_id is UUID."""
        response = await client.post(
            "/chat",
            json={
                "message": "Hello",
                "user_id": "not-a-uuid",
            },
        )

        assert response.status_code == 422  # Validation error


class TestConversationsEndpoint:
    """Tests for /conversations endpoint."""

    @pytest.mark.asyncio
    async def test_list_conversations_endpoint_exists(self, client: AsyncClient):
        """Test /conversations endpoint is registered."""
        user_id = str(uuid4())

        response = await client.get(
            "/conversations",
            params={"user_id": user_id},
        )

        # Should return 200 with empty list or 503 if agent unavailable
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_list_conversations_requires_user_id(self, client: AsyncClient):
        """Test /conversations requires user_id parameter."""
        response = await client.get("/conversations")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_conversations_validates_user_id(self, client: AsyncClient):
        """Test /conversations validates user_id format."""
        response = await client.get(
            "/conversations",
            params={"user_id": "invalid-uuid"},
        )

        assert response.status_code == 400  # Bad request


class TestConversationMessagesEndpoint:
    """Tests for /conversations/{id}/messages endpoint."""

    @pytest.mark.asyncio
    async def test_get_messages_endpoint_exists(self, client: AsyncClient):
        """Test /conversations/{id}/messages endpoint is registered."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())

        response = await client.get(
            f"/conversations/{conversation_id}/messages",
            params={"user_id": user_id},
        )

        # Should return 404 (not found) or 503 if agent unavailable
        assert response.status_code in [404, 503]

    @pytest.mark.asyncio
    async def test_get_messages_requires_user_id(self, client: AsyncClient):
        """Test /conversations/{id}/messages requires user_id."""
        conversation_id = str(uuid4())

        response = await client.get(
            f"/conversations/{conversation_id}/messages",
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_messages_validates_uuids(self, client: AsyncClient):
        """Test /conversations/{id}/messages validates UUIDs."""
        response = await client.get(
            "/conversations/not-a-uuid/messages",
            params={"user_id": str(uuid4())},
        )

        assert response.status_code == 400  # Bad request


class TestHealthEndpointWithAgent:
    """Tests for /health endpoint with agent status."""

    @pytest.mark.asyncio
    async def test_health_includes_agent_status(self, client: AsyncClient):
        """Test /health includes agent status fields."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Agent status fields should be present
        assert "agent_status" in data
        assert "agent_model" in data


# === User Story Integration Test Stubs ===
# These would be full integration tests with a running MCP server

class TestUS1AddTask:
    """[US1] Integration tests for adding tasks via natural language."""

    @pytest.mark.skip(reason="Requires running MCP server and API key")
    @pytest.mark.asyncio
    async def test_add_task_natural_language(self, client: AsyncClient):
        """Test adding a task with natural language."""
        # This would test: "Add a task to buy groceries"
        # Expected: Task created, confirmation message returned
        pass


class TestUS2ListTasks:
    """[US2] Integration tests for listing tasks via natural language."""

    @pytest.mark.skip(reason="Requires running MCP server and API key")
    @pytest.mark.asyncio
    async def test_list_tasks_natural_language(self, client: AsyncClient):
        """Test listing tasks with natural language."""
        # This would test: "Show my tasks"
        # Expected: Task list in response
        pass


class TestUS3US4CompleteDelete:
    """[US3/US4] Integration tests for completing and deleting tasks."""

    @pytest.mark.skip(reason="Requires running MCP server and API key")
    @pytest.mark.asyncio
    async def test_complete_task_natural_language(self, client: AsyncClient):
        """Test completing a task with natural language."""
        # This would test: "Mark task X as done"
        # Expected: Task marked complete, confirmation
        pass

    @pytest.mark.skip(reason="Requires running MCP server and API key")
    @pytest.mark.asyncio
    async def test_delete_task_natural_language(self, client: AsyncClient):
        """Test deleting a task with natural language."""
        # This would test: "Delete task X"
        # Expected: Task deleted, confirmation
        pass


class TestUS5UpdateTask:
    """[US5] Integration tests for updating tasks via natural language."""

    @pytest.mark.skip(reason="Requires running MCP server and API key")
    @pytest.mark.asyncio
    async def test_update_task_natural_language(self, client: AsyncClient):
        """Test updating a task with natural language."""
        # This would test: "Change task X title to Y"
        # Expected: Task updated, confirmation
        pass


class TestUS6MultiTurn:
    """[US6] Integration tests for multi-turn conversations."""

    @pytest.mark.skip(reason="Requires running MCP server and API key")
    @pytest.mark.asyncio
    async def test_multi_turn_context(self, client: AsyncClient):
        """Test multi-turn conversation maintains context."""
        # This would test:
        # 1. "Show my tasks"
        # 2. "Complete the first one"
        # Expected: Context from first message used in second
        pass
