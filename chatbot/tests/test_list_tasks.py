# Task T027: Unit Tests for list_tasks
"""Unit tests for the list_tasks MCP tool.

Tests:
- List all tasks
- Filter by status (pending/completed)
- Empty results
- User isolation

References:
- spec.md: US2 acceptance scenarios
- spec.md: FR-020-024
"""

import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio


class TestListTasks:
    """Tests for list_tasks tool."""

    async def test_list_tasks_all(self, client, test_user_id):
        """Given tasks exist, should return all tasks."""
        # First create some tasks
        for i in range(3):
            await client.post(
                "/mcp/call",
                json={
                    "tool": "add_task",
                    "parameters": {
                        "user_id": str(test_user_id),
                        "title": f"Task {i + 1}",
                    },
                },
            )

        # List all tasks
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                    "status": "all",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["tasks"]) == 3

    async def test_list_tasks_pending(self, client, test_user_id):
        """Given pending filter, should return only pending tasks."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Pending task",
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

        # Create another pending task
        await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Still pending",
                },
            },
        )

        # List pending only
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                    "status": "pending",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["tasks"]) == 1
        assert data["data"]["tasks"][0]["title"] == "Still pending"

    async def test_list_tasks_completed(self, client, test_user_id):
        """Given completed filter, should return only completed tasks."""
        # Create and complete a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Completed task",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

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

        # List completed only
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                    "status": "completed",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["tasks"]) == 1
        assert data["data"]["tasks"][0]["completed"] is True

    async def test_list_tasks_empty(self, client, test_user_id):
        """Given no tasks, should return empty array (not error)."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                    "status": "all",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["tasks"] == []

    async def test_list_tasks_user_isolation(self, client, test_user_id, another_user_id):
        """Given tasks for different users, should only return own tasks."""
        # Create task for user A
        await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "User A task",
                },
            },
        )

        # Create task for user B
        await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(another_user_id),
                    "title": "User B task",
                },
            },
        )

        # List tasks for user A
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                    "status": "all",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["tasks"]) == 1
        assert data["data"]["tasks"][0]["title"] == "User A task"

    async def test_list_tasks_default_status(self, client, test_user_id):
        """Given no status filter, should default to 'all'."""
        await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Test task",
                },
            },
        )

        response = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["tasks"]) == 1
