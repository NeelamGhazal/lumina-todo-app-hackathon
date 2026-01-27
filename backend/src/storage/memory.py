# Tasks T010-T017: Storage Layer per ADR-003
"""In-memory storage layer for Todo CLI using dict-based structure."""

from threading import Lock
from typing import Optional

from src.models.task import Task, generate_id


# Task T010: Implement TaskStorage class (dict-based per ADR-003)
class TaskStorage:
    """
    Thread-safe in-memory storage for tasks.

    Uses dict[str, Task] structure per ADR-003 for O(1) lookup.
    """

    def __init__(self) -> None:
        """Initialize empty storage with thread lock."""
        self._tasks: dict[str, Task] = {}
        self._lock = Lock()

    # Task T011: Implement add() method
    def add(self, task: Task) -> Task:
        """
        Add a task to storage.

        Args:
            task: Task to add (must have valid ID).

        Returns:
            The added task.

        Raises:
            ValueError: If task with same ID already exists.
        """
        with self._lock:
            if task.id in self._tasks:
                raise ValueError(f"Task with ID '{task.id}' already exists")
            self._tasks[task.id] = task
            return task

    # Task T012: Implement get() method
    def get(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: The 6-character task ID.

        Returns:
            Task if found, None otherwise.
        """
        return self._tasks.get(task_id)

    # Task T013: Implement update() method
    def update(self, task_id: str, **updates) -> Optional[Task]:
        """
        Update a task's fields.

        Args:
            task_id: The task ID to update.
            **updates: Field name-value pairs to update.

        Returns:
            Updated task if found, None if task doesn't exist.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None

            # Create updated task using model_copy
            updated_task = task.model_copy(update=updates)
            self._tasks[task_id] = updated_task
            return updated_task

    # Task T014: Implement delete() method
    def delete(self, task_id: str) -> bool:
        """
        Delete a task by ID.

        Args:
            task_id: The task ID to delete.

        Returns:
            True if task was deleted, False if not found.
        """
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False

    # Task T015: Implement list_all() method
    def list_all(self) -> list[Task]:
        """
        Get all tasks.

        Returns:
            List of all tasks (order not guaranteed).
        """
        return list(self._tasks.values())

    # Task T016: Implement search() method
    def search(self, query: str) -> list[Task]:
        """
        Search tasks by keyword across all text fields.

        Searches: title, description, tags, category.
        Case-insensitive matching.

        Args:
            query: Search keyword.

        Returns:
            List of matching tasks.
        """
        query_lower = query.lower()
        results: list[Task] = []

        for task in self._tasks.values():
            # Check title
            if query_lower in task.title.lower():
                results.append(task)
                continue

            # Check description
            if query_lower in task.description.lower():
                results.append(task)
                continue

            # Check tags
            for tag in task.tags:
                if query_lower in tag.lower():
                    results.append(task)
                    break
            else:
                # Check category (enum value)
                if query_lower in task.category.lower():
                    results.append(task)

        return results

    def create_task(self, **kwargs) -> Task:
        """
        Create and add a new task with auto-generated ID.

        Args:
            **kwargs: Task field values (excluding 'id').

        Returns:
            The created task with generated ID.
        """
        existing_ids = set(self._tasks.keys())
        task_id = generate_id(existing_ids)
        task = Task(id=task_id, **kwargs)
        return self.add(task)

    def clear(self) -> None:
        """Remove all tasks from storage."""
        with self._lock:
            self._tasks.clear()

    def count(self) -> int:
        """Return the number of tasks in storage."""
        return len(self._tasks)


# Task T017: Implement get_storage() singleton
_storage: Optional[TaskStorage] = None


def get_storage() -> TaskStorage:
    """
    Get the global TaskStorage singleton instance.

    Returns:
        The shared TaskStorage instance.
    """
    global _storage
    if _storage is None:
        _storage = TaskStorage()
    return _storage


def reset_storage() -> None:
    """Reset the storage singleton (for testing)."""
    global _storage
    _storage = None
