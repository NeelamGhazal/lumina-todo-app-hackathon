# Task T026: Unit Tests for add_task
"""Unit tests for the add_task MCP tool.

Tests:
- Valid task creation
- Validation errors (empty title, too long)
- Database persistence

References:
- spec.md: US1 acceptance scenarios
- spec.md: FR-010-014
"""

import pytest
from uuid import uuid4

pytestmark = pytest.mark.asyncio


class TestAddTask:
    """Tests for add_task tool."""

    async def test_add_task_success(self, client, test_user_id):
        """Given valid params, should create task and return task_id."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Buy groceries",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "created"
        assert data["data"]["title"] == "Buy groceries"
        assert "task_id" in data["data"]

    async def test_add_task_with_description(self, client, test_user_id):
        """Given title and description, should create task with both."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Meeting prep",
                    "description": "Review Q1 slides",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["title"] == "Meeting prep"

    async def test_add_task_empty_title(self, client, test_user_id):
        """Given empty title, should return validation error."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_add_task_whitespace_title(self, client, test_user_id):
        """Given whitespace-only title, should return validation error."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "   ",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_add_task_title_too_long(self, client, test_user_id):
        """Given title > 200 chars, should return validation error."""
        long_title = "x" * 201

        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": long_title,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_add_task_description_too_long(self, client, test_user_id):
        """Given description > 1000 chars, should return validation error."""
        long_desc = "x" * 1001

        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": str(test_user_id),
                    "title": "Valid title",
                    "description": long_desc,
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_add_task_invalid_user_id(self, client):
        """Given invalid UUID, should return validation error."""
        response = await client.post(
            "/mcp/call",
            json={
                "tool": "add_task",
                "parameters": {
                    "user_id": "not-a-uuid",
                    "title": "Valid title",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
