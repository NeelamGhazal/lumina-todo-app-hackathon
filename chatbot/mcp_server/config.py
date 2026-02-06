# Task T005: Configuration Settings
"""Application configuration using pydantic-settings.

Environment variables:
- DATABASE_URL: PostgreSQL connection string (required)
- MCP_SERVER_PORT: Server port (default: 8001)
- ENVIRONMENT: development/production (default: development)
- LOG_LEVEL: Logging level (default: INFO)
- CORS_ORIGINS: Comma-separated CORS origins

References:
- spec.md: FR-003 (stateless), FR-060 (user_id validation)
- plan.md: ADR-001 (standalone FastAPI on port 8001)
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MCP Server settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database - defaults to api's SQLite for local dev
    database_url: str = "sqlite+aiosqlite:///./evolution_todo.db"

    # Server
    mcp_server_port: int = 8001
    mcp_server_host: str = "0.0.0.0"

    # Environment
    environment: str = "development"
    log_level: str = "INFO"

    # CORS - comma-separated list of allowed origins
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Session timeout (minutes) for conversation lifecycle
    session_timeout_minutes: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        """Get list of CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def database_url_resolved(self) -> str:
        """Resolve relative SQLite paths to absolute paths."""
        if "sqlite" in self.database_url and ":///./" in self.database_url:
            # Relative path - resolve to api/ directory
            db_file = self.database_url.split(":///./")[1]
            api_dir = Path(__file__).parent.parent.parent / "api"
            abs_path = str(api_dir / db_file)
            return f"sqlite+aiosqlite:///{abs_path}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
