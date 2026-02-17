"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database - SQLite for hackathon-safe deployment
    database_url: str = "sqlite+aiosqlite:///./data/evolution_todo.db"

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours

    # CORS - comma-separated list of allowed origins
    frontend_url: str = "http://localhost:3000,https://frontend-chi-two-92.vercel.app"

    @property
    def cors_origins(self) -> list[str]:
        """Get list of CORS origins."""
        return [origin.strip() for origin in self.frontend_url.split(",")]

    # Environment
    environment: str = "development"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    # Password Reset (Resend Email Service)
    resend_api_key: str | None = None
    password_reset_from_email: str = "noreply@lumina-todo.com"
    password_reset_token_expiry_minutes: int = 15
    password_reset_max_requests_per_hour: int = 3

    @property
    def primary_frontend_url(self) -> str:
        """Get primary frontend URL for reset link generation."""
        # Use first URL from comma-separated list
        return self.cors_origins[0] if self.cors_origins else "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
