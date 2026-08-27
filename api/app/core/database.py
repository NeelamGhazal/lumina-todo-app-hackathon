"""Database connection and session management."""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import get_settings

# Import all models to ensure they're registered with SQLModel metadata
from app.models import Notification, NotificationType, Task, User  # noqa: F401

settings = get_settings()

# Configure connect_args per backend
connect_args = {}
if "sqlite" in settings.database_url:
    # Timeout prevents "database is locked" errors when multiple processes access DB
    connect_args = {
        "check_same_thread": False,
        "timeout": 30,
    }
elif "postgresql" in settings.database_url:
    # Neon (and most managed Postgres) require TLS. statement_cache_size=0 keeps
    # asyncpg working through Neon's PgBouncer-pooled endpoint, which does not
    # support server-side prepared statements.
    connect_args = {
        "ssl": "require",
        "statement_cache_size": 0,
    }

engine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,
    future=True,
    connect_args=connect_args,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables.

    Also enables WAL mode for SQLite to improve concurrent access
    from multiple processes (Phase II API and MCP server).
    """
    async with engine.begin() as conn:
        # One-shot schema reset. Set DB_RESET_ON_START=1 to drop and rebuild
        # every table on startup (used to migrate the legacy naive-timestamp
        # schema to timestamptz). REMOVE the var immediately afterwards, or the
        # next restart wipes all data.
        if os.getenv("DB_RESET_ON_START") == "1":
            await conn.run_sync(SQLModel.metadata.drop_all)

        await conn.run_sync(SQLModel.metadata.create_all)

        # Enable WAL mode for SQLite to allow concurrent access
        if "sqlite" in settings.database_url:
            from sqlalchemy import text
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA busy_timeout=30000"))


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
