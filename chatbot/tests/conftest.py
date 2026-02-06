# Task T024: Pytest Fixtures
"""Pytest configuration and fixtures for MCP Server tests.

Provides:
- Test database session (in-memory SQLite)
- Mock user IDs for testing
- Cleanup utilities
- Test client for API testing

References:
- Phase II test patterns
- pytest-asyncio for async tests
"""

import asyncio
from collections.abc import AsyncGenerator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from mcp_server.main import app
from mcp_server.database import get_db
from mcp_server.models import Task, Conversation, Message
from mcp_server.tools import registry


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with test database."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clear override
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> UUID:
    """Generate a test user ID."""
    return uuid4()


@pytest.fixture
def another_user_id() -> UUID:
    """Generate another test user ID for isolation tests."""
    return uuid4()


@pytest_asyncio.fixture
async def sample_task(test_session: AsyncSession, test_user_id: UUID) -> Task:
    """Create a sample task for testing."""
    task = Task(
        user_id=test_user_id,
        title="Sample Task",
        description="A sample task for testing",
        completed=False,
    )
    test_session.add(task)
    await test_session.flush()
    return task


@pytest_asyncio.fixture
async def completed_task(test_session: AsyncSession, test_user_id: UUID) -> Task:
    """Create a completed task for testing."""
    from datetime import UTC, datetime

    task = Task(
        user_id=test_user_id,
        title="Completed Task",
        description="A completed task for testing",
        completed=True,
        completed_at=datetime.now(UTC),
    )
    test_session.add(task)
    await test_session.flush()
    return task


@pytest_asyncio.fixture
async def multiple_tasks(
    test_session: AsyncSession, test_user_id: UUID
) -> list[Task]:
    """Create multiple tasks for list testing."""
    tasks = []
    for i in range(5):
        task = Task(
            user_id=test_user_id,
            title=f"Task {i + 1}",
            description=f"Description {i + 1}",
            completed=(i % 2 == 0),  # Alternate completed status
        )
        test_session.add(task)
        tasks.append(task)

    await test_session.flush()
    return tasks


def cleanup_registry():
    """Clear the tool registry (for isolated tests)."""
    # Re-import tools to re-register them
    from mcp_server.tools import add_task, list_tasks, complete_task, delete_task, update_task  # noqa: F401
