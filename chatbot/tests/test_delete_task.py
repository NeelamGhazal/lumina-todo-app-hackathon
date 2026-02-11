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

    async def test_delete_completed_task(self, client, test_user_id):
        """Given a completed task, should delete successfully regardless of status."""
        # Create a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Completed task to delete",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # Complete the task
        complete_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_id,
                },
            },
        )
        assert complete_resp.json()["data"]["status"] == "completed"

        # Delete the completed task - THIS MUST WORK
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

        # Verify task is removed from DB
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                    "status": "all",
                },
            },
        )
        tasks = list_resp.json()["data"]["tasks"]
        task_ids = [t["id"] for t in tasks]
        assert task_id not in task_ids

    async def test_delete_pending_task(self, client, test_user_id):
        """Given a pending task, should delete successfully."""
        # Create a pending task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Pending task to delete",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]
        assert create_resp.json()["data"]["status"] == "created"  # Task was created (pending by default)

        # Delete the pending task
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

        # Verify task is removed from task list
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                },
            },
        )
        tasks = list_resp.json()["data"]["tasks"]
        assert len(tasks) == 0

    async def test_delete_removes_from_db(self, client, test_user_id):
        """Verify deleted task is completely removed from database."""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            create_resp = await client.post(
                "/mcp/call",
                json={
                    "tool": "add_task",
                    "parameters": {
                        "user_id": str(test_user_id),
                        "title": f"Task {i+1}",
                    },
                },
            )
            task_ids.append(create_resp.json()["data"]["task_id"])

        # Delete middle task
        await client.post(
            "/mcp/call",
            json={
                "tool": "delete_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "task_id": task_ids[1],
                },
            },
        )

        # Verify only 2 tasks remain
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": str(test_user_id),
                },
            },
        )
        tasks = list_resp.json()["data"]["tasks"]
        assert len(tasks) == 2
        remaining_ids = [t["id"] for t in tasks]
        assert task_ids[0] in remaining_ids
        assert task_ids[1] not in remaining_ids  # Deleted
        assert task_ids[2] in remaining_ids
