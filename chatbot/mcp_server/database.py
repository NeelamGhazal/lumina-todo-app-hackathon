# Task T006: Database Connection
"""Database connection and session management.

Provides async SQLAlchemy engine and session factory for
direct database access following Phase II patterns.

References:
- api/app/core/database.py: Phase II implementation (reused pattern)
- plan.md: ADR-002 (direct SQLModel access)
- spec.md: FR-003 (stateless), FR-070-072 (database requirements)
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from mcp_server.config import get_settings

settings = get_settings()

# Create async engine with resolved database URL
engine = create_async_engine(
    settings.database_url_resolved,
    echo=settings.is_development,
    future=True,
)

# Session factory for dependency injection
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in SQLModel metadata.
    Safe to call multiple times (uses CREATE IF NOT EXISTS).
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields an async session that auto-commits on success
    and rolls back on exception.

    Usage:
        async with get_session() as session:
            # use session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session.

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async for session in get_session():
        yield session
