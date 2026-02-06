# Task T030: Unit Tests for update_task
"""Unit tests for the update_task MCP tool.

Tests:
- Update title only
- Update description only
- Update both
- No changes provided (validation error)
- Unauthorized access

References:
- spec.md: US5 acceptance scenarios
- spec.md: FR-050-054
"""

import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio


class TestUpdateTask:
    """Tests for update_task tool."""

    async def test_update_task_title(self, client, test_user_id):
        """Given new title, should update task title."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Original title",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Update title
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                    "title": "Updated title",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "updated"
        assert data["data"]["title"] == "Updated title"

    async def test_update_task_description(self, client, test_user_id):
        """Given new description, should update task description."""
        # Create a task without description
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Task title",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Add description
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                    "description": "New description",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["description"] == "New description"

    async def test_update_task_both_fields(self, client, test_user_id):
        """Given both title and description, should update both."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Old title",
                    "description": "Old description",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Update both
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                    "title": "New title",
                    "description": "New description",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["title"] == "New title"
        assert data["data"]["description"] == "New description"

    async def test_update_task_no_changes(self, client, test_user_id):
        """Given no changes, should return validation error."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Task title",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Try to update without changes
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_update_task_not_found(self, client, test_user_id):
        """Given non-existent task_id, should return TASK_NOT_FOUND."""
        fake_task_id = str(uuid4())

        response = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": fake_task_id,
                    "title": "New title",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "TASK_NOT_FOUND"

    async def test_update_task_unauthorized(self, client, test_user_id, another_user_id):
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

        # Try to update as user B
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": str(another_user_id),
                    "task_id": task_id,
                    "title": "Hacked title",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "UNAUTHORIZED"

    async def test_update_task_title_validation(self, client, test_user_id):
        """Given empty title, should return validation error."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Original title",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Try to update with empty title
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                    "title": "",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
