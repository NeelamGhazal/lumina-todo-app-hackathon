# Task T002: Database Migration Script
"""Phase III database migration for conversation tables.

This script creates the conversations and messages tables
required for MCP server conversation tracking.

Supports both SQLite (development) and PostgreSQL (production).

Usage:
    uv run python -m mcp_server.migrations

Tables Created:
    - conversations: Stores conversation sessions
    - messages: Stores individual messages within conversations

References:
    - data-model.md: Entity definitions and migration DDL
    - spec.md: FR-070, FR-071 (database requirements)
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

# Import models to register them with SQLModel metadata
from mcp_server.models import Conversation, Message, MessageRole  # noqa: F401


async def init_tables(database_url: str) -> bool:
    """Initialize database tables using SQLModel create_all.

    This is the recommended approach for development and matches
    Phase II's pattern. Works with both SQLite and PostgreSQL.

    Args:
        database_url: Database connection string

    Returns:
        True if tables created successfully
    """
    engine = create_async_engine(database_url, echo=True)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("Tables created successfully via SQLModel.metadata.create_all")
        return True
    except Exception as e:
        print(f"Table creation failed: {e}")
        return False
    finally:
        await engine.dispose()


async def verify_tables(database_url: str) -> list[str]:
    """Verify that Phase III tables exist in database.

    Args:
        database_url: Database connection string

    Returns:
        List of table names found
    """
    engine = create_async_engine(database_url, echo=False)

    # SQLite vs PostgreSQL query
    if "sqlite" in database_url:
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('conversations', 'messages')
            ORDER BY name;
        """
    else:
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('conversations', 'messages')
            ORDER BY table_name;
        """

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(query))
            tables = [row[0] for row in result.fetchall()]
        return tables
    finally:
        await engine.dispose()


async def drop_tables(database_url: str) -> bool:
    """Drop Phase III tables (for testing/rollback).

    Args:
        database_url: Database connection string

    Returns:
        True if tables dropped successfully
    """
    engine = create_async_engine(database_url, echo=True)

    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS messages;"))
            await conn.execute(text("DROP TABLE IF EXISTS conversations;"))
        print("Tables dropped successfully")
        return True
    except Exception as e:
        print(f"Drop tables failed: {e}")
        return False
    finally:
        await engine.dispose()


def get_database_url() -> str | None:
    """Get database URL from environment or .env file."""
    import os

    # Check environment first
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        # Try to load from chatbot/.env or api/.env
        api_dir = Path(__file__).parent.parent.parent / "api"
        env_paths = [
            Path(__file__).parent.parent / ".env",
            api_dir / ".env",
        ]
        for env_path in env_paths:
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("DATABASE_URL=") and not line.startswith("#"):
                            database_url = line.split("=", 1)[1]
                            # Remove quotes if present
                            database_url = database_url.strip("'\"")
                            break
                if database_url:
                    # Fix relative SQLite path to be absolute (relative to api dir)
                    if "sqlite" in database_url and ":///./" in database_url:
                        # Extract the file path part
                        db_file = database_url.split(":///./")[1]
                        abs_path = str(api_dir / db_file)
                        database_url = f"sqlite+aiosqlite:///{abs_path}"
                    break

    return database_url


async def main() -> int:
    """Main entry point for migration script."""
    database_url = get_database_url()

    if not database_url:
        print("ERROR: DATABASE_URL not set")
        print("Set DATABASE_URL environment variable or create chatbot/.env")
        return 1

    print(f"Database: {database_url.split('@')[-1] if '@' in database_url else database_url}")

    # Check for flags
    if "--drop" in sys.argv:
        success = await drop_tables(database_url)
        return 0 if success else 1

    if "--verify" in sys.argv:
        tables = await verify_tables(database_url)
        print(f"Found tables: {tables}")
        expected = {"conversations", "messages"}
        if set(tables) == expected:
            print("All Phase III tables present")
            return 0
        else:
            print(f"Missing tables: {expected - set(tables)}")
            return 1

    # Default: create tables
    success = await init_tables(database_url)
    if not success:
        return 1

    # Verify
    tables = await verify_tables(database_url)
    print(f"Verified tables: {tables}")

    if set(tables) >= {"conversations", "messages"}:
        print("Migration complete: All Phase III tables created")
        return 0
    else:
        print("ERROR: Tables not found after migration")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
