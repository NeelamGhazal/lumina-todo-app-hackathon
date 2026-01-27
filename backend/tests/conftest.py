# Task T033: Pytest fixtures for Todo CLI tests
"""Shared pytest fixtures for Todo CLI test suite."""

from datetime import date, time, datetime
from io import StringIO

import pytest
from rich.console import Console

from src.models.task import Task, Priority, Category
from src.storage.memory import TaskStorage, reset_storage
from src.ui.console import set_console, reset_console
from src.commands.base import reset_registry


@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        id="a1b2c3",
        title="Buy groceries",
        description="Milk, bread, eggs",
        priority=Priority.HIGH,
        category=Category.SHOPPING,
        tags=["food", "weekly"],
        due_date=date(2026, 1, 28),
        due_time=time(14, 0),
        is_completed=False,
        created_at=datetime(2026, 1, 26, 10, 30, 0),
    )


@pytest.fixture
def sample_tasks() -> list[Task]:
    """Create a list of sample tasks for testing."""
    return [
        Task(
            id="a1b2c3",
            title="Buy groceries",
            priority=Priority.HIGH,
            category=Category.SHOPPING,
            is_completed=False,
        ),
        Task(
            id="x9y8z7",
            title="Finish report",
            priority=Priority.MEDIUM,
            category=Category.WORK,
            is_completed=True,
        ),
        Task(
            id="m4n5o6",
            title="Call doctor",
            priority=Priority.LOW,
            category=Category.HEALTH,
            tags=["appointment"],
            is_completed=False,
        ),
    ]


@pytest.fixture
def storage() -> TaskStorage:
    """Create a fresh TaskStorage instance."""
    return TaskStorage()


@pytest.fixture
def populated_storage(sample_tasks: list[Task]) -> TaskStorage:
    """Create a TaskStorage with sample tasks."""
    storage = TaskStorage()
    for task in sample_tasks:
        storage.add(task)
    return storage


@pytest.fixture
def mock_console() -> Console:
    """Create a mock console that captures output."""
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=80)
    return console


@pytest.fixture
def capture_console(mock_console: Console):
    """Set up console capture and return output getter."""
    set_console(mock_console)
    yield mock_console
    reset_console()


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singletons before each test."""
    reset_storage()
    reset_console()
    reset_registry()
    yield
    reset_storage()
    reset_console()
    reset_registry()
