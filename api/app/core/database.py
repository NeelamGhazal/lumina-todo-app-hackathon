"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import get_settings

settings = get_settings()

# Configure connect_args for SQLite concurrency
connect_args = {}
if "sqlite" in settings.database_url:
    # Timeout prevents "database is locked" errors when multiple processes access DB
    connect_args = {
        "check_same_thread": False,
        "timeout": 30,
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
