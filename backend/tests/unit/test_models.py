# Tasks T034-T035: Unit tests for Task model and generate_id
"""Unit tests for data models."""

from datetime import date, time, datetime

import pytest
from pydantic import ValidationError

from src.models.task import Task, Priority, Category, generate_id


class TestPriorityEnum:
    """Tests for Priority enum."""

    def test_priority_values(self):
        """Test Priority enum has correct values."""
        assert Priority.HIGH.value == "high"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.LOW.value == "low"

    def test_priority_is_string_enum(self):
        """Test Priority is a string enum."""
        assert isinstance(Priority.HIGH, str)
        assert Priority.HIGH == "high"


class TestCategoryEnum:
    """Tests for Category enum."""

    def test_category_values(self):
        """Test Category enum has correct values."""
        assert Category.WORK.value == "work"
        assert Category.PERSONAL.value == "personal"
        assert Category.SHOPPING.value == "shopping"
        assert Category.HEALTH.value == "health"
        assert Category.OTHER.value == "other"


# Task T034: Tests for Task model validation
class TestTaskModel:
    """Tests for Task Pydantic model."""

    def test_task_creation_minimal(self):
        """Test creating a task with only required fields."""
        task = Task(id="a1b2c3", title="Test task")
        assert task.id == "a1b2c3"
        assert task.title == "Test task"
        assert task.description == ""
        assert task.priority == Priority.MEDIUM
        assert task.category == Category.OTHER
        assert task.tags == []
        assert task.due_date is None
        assert task.due_time is None
        assert task.is_completed is False

    def test_task_creation_full(self):
        """Test creating a task with all fields."""
        task = Task(
            id="x9y8z7",
            title="Complete task",
            description="Full description",
            priority=Priority.HIGH,
            category=Category.WORK,
            tags=["urgent", "project"],
            due_date=date(2026, 2, 1),
            due_time=time(9, 0),
            is_completed=True,
        )
        assert task.id == "x9y8z7"
        assert task.title == "Complete task"
        assert task.description == "Full description"
        assert task.priority == Priority.HIGH
        assert task.category == Category.WORK
        assert task.tags == ["urgent", "project"]
        assert task.due_date == date(2026, 2, 1)
        assert task.due_time == time(9, 0)
        assert task.is_completed is True

    def test_task_id_validation_valid(self):
        """Test valid task IDs pass validation."""
        valid_ids = ["a1b2c3", "000000", "zzzzzz", "abc123"]
        for task_id in valid_ids:
            task = Task(id=task_id, title="Test")
            assert task.id == task_id

    def test_task_id_validation_invalid_length(self):
        """Test task ID must be exactly 6 characters."""
        with pytest.raises(ValidationError):
            Task(id="abc", title="Test")
        with pytest.raises(ValidationError):
            Task(id="abcdefgh", title="Test")

    def test_task_id_validation_invalid_chars(self):
        """Test task ID must be lowercase alphanumeric."""
        with pytest.raises(ValidationError):
            Task(id="ABC123", title="Test")  # Uppercase
        with pytest.raises(ValidationError):
            Task(id="ab-c12", title="Test")  # Special char

    def test_title_validation_empty(self):
        """Test title cannot be empty."""
        with pytest.raises(ValidationError):
            Task(id="a1b2c3", title="")

    def test_title_validation_max_length(self):
        """Test title max length is 200 characters."""
        long_title = "x" * 200
        task = Task(id="a1b2c3", title=long_title)
        assert len(task.title) == 200

        with pytest.raises(ValidationError):
            Task(id="a1b2c3", title="x" * 201)

    def test_title_whitespace_stripped(self):
        """Test title leading/trailing whitespace is stripped."""
        task = Task(id="a1b2c3", title="  Test task  ")
        assert task.title == "Test task"

    def test_description_max_length(self):
        """Test description max length is 2000 characters."""
        long_desc = "x" * 2000
        task = Task(id="a1b2c3", title="Test", description=long_desc)
        assert len(task.description) == 2000

        with pytest.raises(ValidationError):
            Task(id="a1b2c3", title="Test", description="x" * 2001)

    def test_tags_cleaned(self):
        """Test tags are trimmed and deduplicated."""
        task = Task(id="a1b2c3", title="Test", tags=["  tag1  ", "tag2", "TAG1", ""])
        # Empty tags removed, duplicates (case-insensitive) removed
        assert "tag1" in task.tags or "TAG1" in task.tags
        assert "tag2" in task.tags
        assert len(task.tags) == 2

    def test_priority_default(self):
        """Test default priority is MEDIUM."""
        task = Task(id="a1b2c3", title="Test")
        assert task.priority == Priority.MEDIUM

    def test_category_default(self):
        """Test default category is OTHER."""
        task = Task(id="a1b2c3", title="Test")
        assert task.category == Category.OTHER

    def test_created_at_auto_generated(self):
        """Test created_at is auto-generated."""
        before = datetime.now()
        task = Task(id="a1b2c3", title="Test")
        after = datetime.now()
        assert before <= task.created_at <= after

    def test_task_serialization(self):
        """Test task can be serialized to dict."""
        task = Task(
            id="a1b2c3",
            title="Test",
            priority=Priority.HIGH,
            category=Category.WORK,
        )
        data = task.model_dump()
        assert data["id"] == "a1b2c3"
        assert data["priority"] == "high"  # Enum value, not enum
        assert data["category"] == "work"


# Task T035: Tests for generate_id function
class TestGenerateId:
    """Tests for ID generation."""

    def test_generate_id_format(self):
        """Test generated ID is 6 lowercase alphanumeric characters."""
        task_id = generate_id()
        assert len(task_id) == 6
        assert task_id.islower() or task_id.isdigit() or task_id.isalnum()
        assert task_id == task_id.lower()

    def test_generate_id_unique(self):
        """Test generated IDs are unique."""
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_id_avoids_collisions(self):
        """Test generate_id avoids existing IDs."""
        existing = {"a1b2c3", "x9y8z7"}
        for _ in range(50):
            new_id = generate_id(existing)
            assert new_id not in existing
            existing.add(new_id)

    def test_generate_id_with_empty_existing(self):
        """Test generate_id works with empty existing set."""
        task_id = generate_id(set())
        assert len(task_id) == 6

    def test_generate_id_with_none_existing(self):
        """Test generate_id works with None existing set."""
        task_id = generate_id(None)
        assert len(task_id) == 6
