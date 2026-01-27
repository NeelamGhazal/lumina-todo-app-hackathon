# Tasks T036-T037: Unit tests for TaskStorage
"""Unit tests for storage layer."""

import pytest

from src.models.task import Task, Priority, Category
from src.storage.memory import TaskStorage, get_storage, reset_storage


# Task T036: Tests for TaskStorage CRUD operations
class TestTaskStorageCRUD:
    """Tests for TaskStorage CRUD operations."""

    def test_add_task(self, storage: TaskStorage, sample_task: Task):
        """Test adding a task to storage."""
        result = storage.add(sample_task)
        assert result == sample_task
        assert storage.count() == 1

    def test_add_duplicate_raises_error(self, storage: TaskStorage, sample_task: Task):
        """Test adding duplicate task ID raises ValueError."""
        storage.add(sample_task)
        with pytest.raises(ValueError, match="already exists"):
            storage.add(sample_task)

    def test_get_existing_task(self, storage: TaskStorage, sample_task: Task):
        """Test getting an existing task."""
        storage.add(sample_task)
        result = storage.get(sample_task.id)
        assert result == sample_task

    def test_get_nonexistent_task(self, storage: TaskStorage):
        """Test getting a non-existent task returns None."""
        result = storage.get("nonexistent")
        assert result is None

    def test_update_task(self, storage: TaskStorage, sample_task: Task):
        """Test updating a task."""
        storage.add(sample_task)
        updated = storage.update(sample_task.id, title="New title", is_completed=True)
        assert updated is not None
        assert updated.title == "New title"
        assert updated.is_completed is True
        # Original fields preserved
        assert updated.priority == sample_task.priority

    def test_update_nonexistent_task(self, storage: TaskStorage):
        """Test updating non-existent task returns None."""
        result = storage.update("nonexistent", title="New title")
        assert result is None

    def test_delete_existing_task(self, storage: TaskStorage, sample_task: Task):
        """Test deleting an existing task."""
        storage.add(sample_task)
        result = storage.delete(sample_task.id)
        assert result is True
        assert storage.get(sample_task.id) is None
        assert storage.count() == 0

    def test_delete_nonexistent_task(self, storage: TaskStorage):
        """Test deleting non-existent task returns False."""
        result = storage.delete("nonexistent")
        assert result is False

    def test_list_all_empty(self, storage: TaskStorage):
        """Test listing all tasks from empty storage."""
        result = storage.list_all()
        assert result == []

    def test_list_all_with_tasks(self, populated_storage: TaskStorage):
        """Test listing all tasks."""
        result = populated_storage.list_all()
        assert len(result) == 3

    def test_count(self, populated_storage: TaskStorage):
        """Test counting tasks."""
        assert populated_storage.count() == 3

    def test_clear(self, populated_storage: TaskStorage):
        """Test clearing all tasks."""
        populated_storage.clear()
        assert populated_storage.count() == 0

    def test_create_task(self, storage: TaskStorage):
        """Test creating a task with auto-generated ID."""
        task = storage.create_task(title="New task", priority=Priority.HIGH)
        assert len(task.id) == 6
        assert task.title == "New task"
        assert task.priority == Priority.HIGH
        assert storage.count() == 1


# Task T037: Tests for TaskStorage search
class TestTaskStorageSearch:
    """Tests for TaskStorage search functionality."""

    def test_search_by_title(self, populated_storage: TaskStorage):
        """Test searching by title."""
        results = populated_storage.search("groceries")
        assert len(results) == 1
        assert results[0].title == "Buy groceries"

    def test_search_by_title_case_insensitive(self, populated_storage: TaskStorage):
        """Test search is case-insensitive."""
        results = populated_storage.search("GROCERIES")
        assert len(results) == 1

    def test_search_by_description(self, storage: TaskStorage):
        """Test searching by description."""
        task = Task(
            id="a1b2c3",
            title="Task",
            description="Important meeting notes",
        )
        storage.add(task)
        results = storage.search("meeting")
        assert len(results) == 1

    def test_search_by_tags(self, populated_storage: TaskStorage):
        """Test searching by tags."""
        results = populated_storage.search("appointment")
        assert len(results) == 1
        assert "appointment" in results[0].tags

    def test_search_by_category(self, populated_storage: TaskStorage):
        """Test searching by category."""
        results = populated_storage.search("shopping")
        assert len(results) == 1
        assert results[0].category == Category.SHOPPING

    def test_search_no_results(self, populated_storage: TaskStorage):
        """Test search with no matches."""
        results = populated_storage.search("nonexistent")
        assert results == []

    def test_search_multiple_results(self, storage: TaskStorage):
        """Test search returning multiple results."""
        storage.add(Task(id="aaaaaa", title="Buy milk"))
        storage.add(Task(id="bbbbbb", title="Buy bread"))
        storage.add(Task(id="cccccc", title="Sell car"))
        results = storage.search("buy")
        assert len(results) == 2

    def test_search_partial_match(self, populated_storage: TaskStorage):
        """Test partial word matching."""
        results = populated_storage.search("groc")  # Partial match for "groceries"
        assert len(results) == 1


class TestStorageSingleton:
    """Tests for storage singleton."""

    def test_get_storage_singleton(self):
        """Test get_storage returns same instance."""
        reset_storage()
        s1 = get_storage()
        s2 = get_storage()
        assert s1 is s2

    def test_reset_storage(self):
        """Test reset_storage creates new instance."""
        s1 = get_storage()
        s1.create_task(title="Test")
        reset_storage()
        s2 = get_storage()
        assert s2.count() == 0
