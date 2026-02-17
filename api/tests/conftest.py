"""Pytest configuration and fixtures for API tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel

from app.core.database import engine, get_session, async_session_maker
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator:
    """Create a fresh database session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async for session in get_session():
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def test_user(client: AsyncClient) -> dict:
    """Create a test user and return user data with token."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123",
            "name": "Test User",
        },
    )
    assert response.status_code == 201
    return response.json()
