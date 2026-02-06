# Task T029: Unit Tests for delete_task
"""Unit tests for the delete_task MCP tool.

Tests:
- Successful deletion
- Task not found
- Unauthorized access

References:
- spec.md: US4 acceptance scenarios
- spec.md: FR-040-043
"""

import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio


class TestDeleteTask:
    """Tests for delete_task tool."""

    async def test_delete_task_success(self, client, test_user_id):
        """Given valid task, should delete and return confirmation."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Task to delete",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Delete it
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "delete_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "deleted"
        assert data["data"]["task_id"] == task_id
        assert data["data"]["title"] == "Task to delete"

        # Verify task is actually deleted
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                },
            },
        )
        assert len(list_resp.json()["data"]["tasks"]) == 0

    async def test_delete_task_not_found(self, client, test_user_id):
        """Given non-existent task_id, should return TASK_NOT_FOUND."""
        fake_task_id = str(uuid4())

        response = await client.post(
            "/mcp/call",
            json={
                "tool": "delete_task",
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

    async def test_delete_task_unauthorized(self, client, test_user_id, another_user_id):
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

        # Try to delete as user B
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "delete_task",
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

        # Verify task still exists for user A
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                },
            },
        )
        assert len(list_resp.json()["data"]["tasks"]) == 1
