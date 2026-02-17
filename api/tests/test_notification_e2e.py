"""End-to-end tests for notification flows.

T027: Due-soon notification flow
T028: Overdue notification flow
T029: Task completion notification flow
"""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient


class TestDueSoonNotificationFlow:
    """T027: E2E Test for due-soon notification flow."""

    async def test_due_soon_notification_complete_flow(
        self, client: AsyncClient, test_user: dict
    ):
        """Test complete due-soon notification flow:
        1. Create task due tomorrow
        2. Trigger job manually
        3. Verify notification appears
        4. Verify badge count updated
        """
        token = test_user["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create task due tomorrow
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()
        create_response = await client.post(
            "/api/tasks",
            headers=headers,
            json={
                "title": "Task due tomorrow",
                "dueDate": tomorrow,
                "priority": "high",
                "category": "work",
            },
        )
        assert create_response.status_code == 201
        task = create_response.json()["task"]

        # 2. Trigger notification job manually
        trigger_response = await client.post(
            "/api/notifications/trigger-job",
            headers=headers,
        )
        assert trigger_response.status_code == 200
        trigger_data = trigger_response.json()
        assert trigger_data["dueSoonCount"] >= 1

        # 3. Verify notification appears in list
        list_response = await client.get(
            "/api/notifications",
            headers=headers,
        )
        assert list_response.status_code == 200
        notifications = list_response.json()["notifications"]

        due_soon_notifications = [
            n for n in notifications
            if n["type"] == "TASK_DUE_SOON" and n["taskId"] == task["id"]
        ]
        assert len(due_soon_notifications) == 1
        assert "Task due tomorrow" in due_soon_notifications[0]["message"]

        # 4. Verify unread count updated
        count_response = await client.get(
            "/api/notifications/unread-count",
            headers=headers,
        )
        assert count_response.status_code == 200
        assert count_response.json()["count"] >= 1


class TestOverdueNotificationFlow:
    """T028: E2E Test for overdue notification flow."""

    async def test_overdue_notification_complete_flow(
        self, client: AsyncClient, test_user: dict
    ):
        """Test complete overdue notification flow:
        1. Create task with yesterday's due date
        2. Trigger job manually
        3. Verify overdue notification appears
        4. Trigger again - verify NO duplicate
        """
        token = test_user["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create task with yesterday's due date
        yesterday = (datetime.now(UTC) - timedelta(days=1)).date().isoformat()
        create_response = await client.post(
            "/api/tasks",
            headers=headers,
            json={
                "title": "Overdue task",
                "dueDate": yesterday,
                "priority": "high",
                "category": "work",
            },
        )
        assert create_response.status_code == 201
        task = create_response.json()["task"]

        # 2. Trigger notification job manually
        trigger_response = await client.post(
            "/api/notifications/trigger-job",
            headers=headers,
        )
        assert trigger_response.status_code == 200
        first_overdue_count = trigger_response.json()["overdueCount"]
        assert first_overdue_count >= 1

        # 3. Verify overdue notification appears
        list_response = await client.get(
            "/api/notifications",
            headers=headers,
        )
        assert list_response.status_code == 200
        notifications = list_response.json()["notifications"]

        overdue_notifications = [
            n for n in notifications
            if n["type"] == "TASK_OVERDUE" and n["taskId"] == task["id"]
        ]
        assert len(overdue_notifications) == 1
        assert "overdue" in overdue_notifications[0]["message"].lower()

        # 4. Trigger again - verify NO duplicate created
        trigger_response_2 = await client.post(
            "/api/notifications/trigger-job",
            headers=headers,
        )
        assert trigger_response_2.status_code == 200
        # Should be 0 new overdue notifications (duplicate prevention)
        assert trigger_response_2.json()["overdueCount"] == 0

        # Verify still only 1 overdue notification for this task
        list_response_2 = await client.get(
            "/api/notifications",
            headers=headers,
        )
        overdue_notifications_2 = [
            n for n in list_response_2.json()["notifications"]
            if n["type"] == "TASK_OVERDUE" and n["taskId"] == task["id"]
        ]
        assert len(overdue_notifications_2) == 1


class TestTaskCompletionNotificationFlow:
    """T029: E2E Test for task completion notification flow."""

    async def test_completion_notification_immediate(
        self, client: AsyncClient, test_user: dict
    ):
        """Test task completion notification flow:
        1. Create a task
        2. Complete the task
        3. Verify completion notification appears immediately
        4. Verify badge updates
        """
        token = test_user["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create a task
        create_response = await client.post(
            "/api/tasks",
            headers=headers,
            json={
                "title": "Task to complete",
                "priority": "medium",
                "category": "personal",
            },
        )
        assert create_response.status_code == 201
        task = create_response.json()["task"]
        task_id = task["id"]

        # Get initial unread count
        initial_count_response = await client.get(
            "/api/notifications/unread-count",
            headers=headers,
        )
        initial_count = initial_count_response.json()["count"]

        # 2. Complete the task
        complete_response = await client.patch(
            f"/api/tasks/{task_id}/complete",
            headers=headers,
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["task"]["completed"] is True

        # 3. Verify completion notification appears immediately
        list_response = await client.get(
            "/api/notifications",
            headers=headers,
        )
        assert list_response.status_code == 200
        notifications = list_response.json()["notifications"]

        completion_notifications = [
            n for n in notifications
            if n["type"] == "TASK_COMPLETED" and n["taskId"] == task_id
        ]
        assert len(completion_notifications) >= 1
        assert "Task to complete" in completion_notifications[0]["message"]

        # 4. Verify badge updates (unread count increased)
        final_count_response = await client.get(
            "/api/notifications/unread-count",
            headers=headers,
        )
        final_count = final_count_response.json()["count"]
        assert final_count > initial_count


class TestUncompleteNotificationDeletion:
    """ISSUE 3: Test that completion notification is deleted on uncomplete."""

    async def test_uncomplete_task_deletes_completion_notification(
        self, client: AsyncClient, test_user: dict
    ):
        """Test that uncompleting a task deletes its completion notification:
        1. Create a task
        2. Complete the task (creates notification)
        3. Verify notification exists
        4. Uncomplete the task
        5. Verify notification is deleted
        """
        token = test_user["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create a task
        create_response = await client.post(
            "/api/tasks",
            headers=headers,
            json={
                "title": "Task to uncomplete",
                "priority": "medium",
                "category": "personal",
            },
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["task"]["id"]

        # 2. Complete the task
        complete_response = await client.patch(
            f"/api/tasks/{task_id}/complete",
            headers=headers,
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["task"]["completed"] is True

        # 3. Verify completion notification exists
        list_response = await client.get(
            "/api/notifications",
            headers=headers,
        )
        notifications = list_response.json()["notifications"]
        completion_notifications = [
            n for n in notifications
            if n["type"] == "TASK_COMPLETED" and n["taskId"] == task_id
        ]
        assert len(completion_notifications) == 1

        # 4. Uncomplete the task
        uncomplete_response = await client.patch(
            f"/api/tasks/{task_id}/complete",
            headers=headers,
        )
        assert uncomplete_response.status_code == 200
        assert uncomplete_response.json()["task"]["completed"] is False

        # 5. Verify notification is deleted
        list_response_2 = await client.get(
            "/api/notifications",
            headers=headers,
        )
        notifications_2 = list_response_2.json()["notifications"]
        completion_notifications_2 = [
            n for n in notifications_2
            if n["type"] == "TASK_COMPLETED" and n["taskId"] == task_id
        ]
        assert len(completion_notifications_2) == 0, "Completion notification should be deleted on uncomplete"


class TestDuplicatePrevention:
    """Additional tests for duplicate prevention logic."""

    async def test_no_duplicate_due_soon_on_multiple_triggers(
        self, client: AsyncClient, test_user: dict
    ):
        """Verify cron job can run multiple times without creating duplicates."""
        token = test_user["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create task due tomorrow
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()
        await client.post(
            "/api/tasks",
            headers=headers,
            json={"title": "No duplicates test", "dueDate": tomorrow, "priority": "low", "category": "other"},
        )

        # Trigger job 3 times
        counts = []
        for _ in range(3):
            response = await client.post(
                "/api/notifications/trigger-job",
                headers=headers,
            )
            counts.append(response.json()["dueSoonCount"])

        # First trigger should create notification, subsequent should not
        assert counts[0] >= 1
        assert counts[1] == 0
        assert counts[2] == 0


class TestPollingEndpointPerformance:
    """T035: Verify polling endpoint is lightweight."""

    async def test_unread_count_endpoint_fast(
        self, client: AsyncClient, test_user: dict
    ):
        """Verify unread-count endpoint responds quickly."""
        import time

        token = test_user["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Measure response time
        start = time.perf_counter()
        response = await client.get(
            "/api/notifications/unread-count",
            headers=headers,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        # Should respond in under 100ms for polling efficiency
        assert elapsed_ms < 100, f"Endpoint took {elapsed_ms:.2f}ms, expected < 100ms"
