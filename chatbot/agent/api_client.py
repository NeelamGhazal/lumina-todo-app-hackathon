# API Client for Part 1 Task Operations
"""HTTP client for calling Part 1 API task endpoints.

This module replaces direct MCP server calls with HTTP calls to the
Part 1 API, using the user's JWT token for authentication.

This ensures tasks are stored in the Part 1 database (shared with frontend)
instead of the chatbot's local database.
"""

from typing import Any
from uuid import UUID

import httpx
import structlog

from mcp_server.config import get_settings

logger = structlog.get_logger(__name__)


class APIClientError(Exception):
    """Error from API client operations."""

    def __init__(self, message: str, code: str = "API_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class APIUnavailable(APIClientError):
    """Part 1 API is not reachable."""

    def __init__(self, url: str, error: str):
        super().__init__(
            f"API unavailable at {url}: {error}",
            code="API_UNAVAILABLE",
            details={"url": url, "error": error},
        )


class APIAuthError(APIClientError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code="AUTH_REQUIRED")


async def call_api(
    method: str,
    endpoint: str,
    auth_token: str | None,
    json_data: dict | None = None,
    params: dict | None = None,
) -> dict[str, Any]:
    """Make an authenticated HTTP call to Part 1 API.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint path (e.g., "/api/tasks")
        auth_token: JWT Bearer token
        json_data: Request body for POST/PUT/PATCH
        params: Query parameters

    Returns:
        Response JSON data

    Raises:
        APIAuthError: If no auth token provided
        APIUnavailable: If API is not reachable
        APIClientError: For other API errors
    """
    settings = get_settings()
    url = f"{settings.api_base_url}{endpoint}"

    if not auth_token:
        raise APIAuthError("No authentication token available")

    headers = {"Authorization": auth_token}

    logger.debug(
        "api_call_start",
        method=method,
        endpoint=endpoint,
        has_body=json_data is not None,
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )

            # Handle auth errors
            if response.status_code == 401:
                raise APIAuthError("Session expired or invalid token")

            # Handle not found
            if response.status_code == 404:
                raise APIClientError(
                    "Resource not found",
                    code="NOT_FOUND",
                    details={"endpoint": endpoint},
                )

            # Handle other errors
            if response.status_code >= 400:
                error_data = response.json() if response.text else {}
                raise APIClientError(
                    error_data.get("message", f"API error: {response.status_code}"),
                    code=error_data.get("error", "API_ERROR"),
                    details=error_data,
                )

            result = response.json()
            logger.debug(
                "api_call_success",
                method=method,
                endpoint=endpoint,
                status=response.status_code,
            )
            return result

    except httpx.ConnectError as e:
        raise APIUnavailable(url, str(e))
    except httpx.TimeoutException:
        raise APIUnavailable(url, "Request timed out")
    except (APIClientError, APIUnavailable, APIAuthError):
        raise
    except Exception as e:
        logger.error(
            "api_call_failed",
            method=method,
            endpoint=endpoint,
            error=str(e),
        )
        raise APIClientError(f"API call failed: {str(e)}")


# === Task API Operations ===


async def api_create_task(
    auth_token: str | None,
    title: str,
    description: str | None = None,
    priority: str = "medium",
    category: str = "personal",
    tags: list[str] | None = None,
    due_date: str | None = None,
    due_time: str | None = None,
) -> dict[str, Any]:
    """Create a new task via Part 1 API.

    Args:
        auth_token: JWT Bearer token
        title: Task title (required)
        description: Task description
        priority: "high", "medium", or "low"
        category: "work", "personal", "shopping", "health", or "other"
        tags: List of tags
        due_date: YYYY-MM-DD format
        due_time: HH:MM format

    Returns:
        Created task data with task_id
    """
    data: dict[str, Any] = {"title": title}

    if description:
        data["description"] = description
    if priority:
        data["priority"] = priority
    if category:
        data["category"] = category
    if tags:
        data["tags"] = tags
    if due_date:
        data["dueDate"] = due_date
    if due_time:
        data["dueTime"] = due_time

    result = await call_api("POST", "/api/tasks", auth_token, json_data=data)

    # Map API response to MCP tool response format
    task = result.get("task", {})
    return {
        "task_id": task.get("id"),
        "status": "created",
        "title": task.get("title"),
    }


async def api_list_tasks(
    auth_token: str | None,
    status: str = "all",
) -> dict[str, Any]:
    """List tasks via Part 1 API.

    Args:
        auth_token: JWT Bearer token
        status: "all", "pending", or "completed"

    Returns:
        List of tasks
    """
    params = {}
    if status and status != "all":
        params["status"] = status

    result = await call_api("GET", "/api/tasks", auth_token, params=params)

    # Map API response to MCP tool response format
    tasks = result.get("tasks", [])
    return {
        "tasks": [
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "description": t.get("description"),
                "completed": t.get("completed", False),
                "priority": t.get("priority", "medium"),
                "category": t.get("category", "personal"),
                "created_at": t.get("createdAt"),
            }
            for t in tasks
        ]
    }


async def api_complete_task(
    auth_token: str | None,
    task_id: str,
) -> dict[str, Any]:
    """Toggle task completion via Part 1 API.

    Args:
        auth_token: JWT Bearer token
        task_id: Task UUID

    Returns:
        Updated task status
    """
    result = await call_api("PATCH", f"/api/tasks/{task_id}/complete", auth_token)

    task = result.get("task", {})
    return {
        "task_id": task.get("id"),
        "status": "completed" if task.get("completed") else "pending",
        "title": task.get("title"),
    }


async def api_delete_task(
    auth_token: str | None,
    task_id: str,
) -> dict[str, Any]:
    """Delete a task via Part 1 API.

    Args:
        auth_token: JWT Bearer token
        task_id: Task UUID

    Returns:
        Deletion confirmation
    """
    result = await call_api("DELETE", f"/api/tasks/{task_id}", auth_token)

    return {
        "task_id": result.get("taskId"),
        "status": "deleted",
        "title": "Task deleted",
    }


async def api_update_task(
    auth_token: str | None,
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    due_time: str | None = None,
) -> dict[str, Any]:
    """Update a task via Part 1 API.

    Args:
        auth_token: JWT Bearer token
        task_id: Task UUID
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        category: New category (optional)
        tags: New tags (optional)
        due_date: New due date YYYY-MM-DD (optional)
        due_time: New due time HH:MM (optional)

    Returns:
        Updated task data
    """
    data: dict[str, Any] = {}

    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if priority is not None:
        data["priority"] = priority
    if category is not None:
        data["category"] = category
    if tags is not None:
        data["tags"] = tags
    if due_date is not None:
        data["dueDate"] = due_date
    if due_time is not None:
        data["dueTime"] = due_time

    result = await call_api("PUT", f"/api/tasks/{task_id}", auth_token, json_data=data)

    task = result.get("task", {})
    return {
        "task_id": task.get("id"),
        "status": "updated",
        "title": task.get("title"),
        "description": task.get("description"),
    }


# Export public API
__all__ = [
    "APIClientError",
    "APIUnavailable",
    "APIAuthError",
    "call_api",
    "api_create_task",
    "api_list_tasks",
    "api_complete_task",
    "api_delete_task",
    "api_update_task",
]
