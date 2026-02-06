# Task T031: Integration Tests
"""Integration tests for MCP Server API.

Tests full request/response cycles including:
- Health check endpoint
- Tool listing
- End-to-end workflows
- Error handling

References:
- spec.md: Success Criteria SC-001 to SC-007
"""

import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    async def test_health_check(self, client):
        """Health endpoint should return healthy status."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    async def test_root_endpoint(self, client):
        """Root endpoint should return service info."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "MCP Todo Server"
        assert data["status"] == "running"


class TestToolListing:
    """Tests for /mcp/tools endpoint."""

    async def test_list_tools(self, client):
        """Should return all 5 registered tools."""
        response = await client.get("/mcp/tools")

        assert response.status_code == 200
        data = response.json()
        tool_names = [t["name"] for t in data["tools"]]

        assert len(tool_names) == 5
        assert "add_task" in tool_names
        assert "list_tasks" in tool_names
        assert "complete_task" in tool_names
        assert "delete_task" in tool_names
        assert "update_task" in tool_names

    async def test_tool_has_schema(self, client):
        """Each tool should have a JSON schema for parameters."""
        response = await client.get("/mcp/tools")

        data = response.json()
        for tool in data["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert "properties" in tool["parameters"]


class TestToolCallEndpoint:
    """Tests for /mcp/call endpoint."""

    async def test_unknown_tool(self, client):
        """Calling unknown tool should return error."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "unknown_tool",
                "parameters": {},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "unknown tool" in data["error"]["message"].lower()

    async def test_missing_parameters(self, client):
        """Calling tool without required params should return validation error."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    async def test_complete_task_lifecycle(self, client):
        """Test full lifecycle: create -> list -> complete -> update -> delete."""
        user_id = str(uuid4())

        # 1. Create task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": user_id,
                    "title": "Lifecycle test task",
                    "description": "Testing full lifecycle",
                },
            },
        )
        assert create_resp.json()["status"] == "success"
        task_id = create_resp.json()["data"]["task_id"]

        # 2. List tasks - should find it
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": user_id,
                },
            },
        )
        assert list_resp.json()["status"] == "success"
        tasks = list_resp.json()["data"]["tasks"]
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Lifecycle test task"
        assert tasks[0]["completed"] is False

        # 3. Complete task
        complete_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": user_id,
                    "task_id": task_id,
                },
            },
        )
        assert complete_resp.json()["status"] == "success"
        assert complete_resp.json()["data"]["status"] == "completed"

        # 4. List completed - should find it
        list_completed_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": user_id,
                    "status": "completed",
                },
            },
        )
        assert len(list_completed_resp.json()["data"]["tasks"]) == 1

        # 5. Update task
        update_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": user_id,
                    "task_id": task_id,
                    "title": "Updated lifecycle task",
                },
            },
        )
        assert update_resp.json()["status"] == "success"
        assert update_resp.json()["data"]["title"] == "Updated lifecycle task"

        # 6. Delete task
        delete_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "delete_task",
                "parameters": {
                    "user_id": user_id,
                    "task_id": task_id,
                },
            },
        )
        assert delete_resp.json()["status"] == "success"
        assert delete_resp.json()["data"]["status"] == "deleted"

        # 7. List tasks - should be empty
        final_list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": user_id,
                },
            },
        )
        assert len(final_list_resp.json()["data"]["tasks"]) == 0

    async def test_multi_user_isolation(self, client):
        """Test that users cannot access each other's tasks."""
        user_a = str(uuid4())
        user_b = str(uuid4())

        # User A creates a task
        create_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": user_a,
                    "title": "User A's private task",
                },
            },
        )
        task_id = create_resp.json()["data"]["task_id"]

        # User B cannot see it
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": user_b,
                },
            },
        )
        assert len(list_resp.json()["data"]["tasks"]) == 0

        # User B cannot complete it
        complete_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "complete_task",
                "parameters": {
                    "user_id": user_b,
                    "task_id": task_id,
                },
            },
        )
        assert complete_resp.json()["error"]["code"] == "UNAUTHORIZED"

        # User B cannot delete it
        delete_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "delete_task",
                "parameters": {
                    "user_id": user_b,
                    "task_id": task_id,
                },
            },
        )
        assert delete_resp.json()["error"]["code"] == "UNAUTHORIZED"

        # User B cannot update it
        update_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "update_task",
                "parameters": {
                    "user_id": user_b,
                    "task_id": task_id,
                    "title": "Hacked",
                },
            },
        )
        assert update_resp.json()["error"]["code"] == "UNAUTHORIZED"

        # User A can still see and manage it
        list_a_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": user_a,
                },
            },
        )
        assert len(list_a_resp.json()["data"]["tasks"]) == 1


class TestConcurrentOperations:
    """Test concurrent operations don't cause issues."""

    async def test_multiple_tasks_same_user(self, client):
        """Creating multiple tasks for same user should work correctly."""
        user_id = str(uuid4())

        # Create 10 tasks
        for i in range(10):
            resp = await client.post(
                "/mcp/call",
                json={
                    "tool": "add_task",
                    "parameters": {
                        "user_id": user_id,
                        "title": f"Task {i + 1}",
                    },
                },
            )
            assert resp.json()["status"] == "success"

        # List all
        list_resp = await client.post(
            "/mcp/call",
            json={
                "tool": "list_tasks",
                "parameters": {
                    "user_id": user_id,
                },
            },
        )
        assert len(list_resp.json()["data"]["tasks"]) == 10
