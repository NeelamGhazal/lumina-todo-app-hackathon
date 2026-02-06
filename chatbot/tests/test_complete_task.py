# Task T028: Unit Tests for complete_task
"""Unit tests for the complete_task MCP tool.

Tests:
- Toggle to completed
- Toggle back to pending
- Task not found
- Unauthorized access

References:
- spec.md: US3 acceptance scenarios
- spec.md: FR-030-033
"""

import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio


class TestCompleteTask:
    """Tests for complete_task tool."""

    async def test_complete_task_pending_to_completed(self, client, test_user_id):
        """Given pending task, should toggle to completed."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Task to complete",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Complete it
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "completed"
        assert data["data"]["task_id"] == task_id

    async def test_complete_task_completed_to_pending(self, client, test_user_id):
        """Given completed task, should toggle back to pending."""
        # Create and complete a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Task to uncomplete",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Complete it
        await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                },
            },
        )

        # Uncomplete it
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "pending"

    async def test_complete_task_not_found(self, client, test_user_id):
        """Given non-existent task_id, should return TASK_NOT_FOUND."""
        fake_task_id = str(uuid4())

        response = await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": fake_task_id,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "TASK_NOT_FOUND"

    async def test_complete_task_unauthorized(self, client, test_user_id, another_user_id):
        """Given task owned by another user, should return UNAUTHORIZED."""
        # Create task for user A
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "User A's task",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Try to complete as user B
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": str(another_user_id),
                    "task_id": task_id,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "UNAUTHORIZED"
