# Task T004: Agent Configuration
"""Agent configuration using pydantic-settings.

Environment variables:
- OPENROUTER_API_KEY: OpenRouter API key (required)
- AGENT_MODEL: Model to use via OpenRouter (default: gpt-4o-mini)
- MCP_SERVER_URL: URL of MCP server for tool execution (default: http://localhost:8001)

References:
- spec.md: FR-020 (OpenRouter integration), FR-022 (configurable model)
- plan.md: ADR-007 (startup tool loading), ADR-008 (LLM-based intent)
- research.md: R1 (OpenRouter compatibility), R9 (model selection)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Agent settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenRouter Configuration
    openrouter_api_key: str = ""
    agent_model: str = "gpt-4o-mini"

    # MCP Server URL (for tool execution)
    mcp_server_url: str = "http://localhost:8001"

    # Context Configuration (per ADR-006)
    context_message_limit: int = 10

    # Tool Loop Configuration (per plan.md risk mitigation)
    max_tool_rounds: int = 5

    @property
    def openrouter_base_url(self) -> str:
        """OpenRouter API base URL."""
        return "https://openrouter.ai/api/v1"

    @property
    def is_configured(self) -> bool:
        """Check if agent is properly configured."""
        return bool(self.openrouter_api_key)

    @property
    def agent_instructions(self) -> str:
        """System instructions for the todo assistant agent.

        These instructions guide the LLM's behavior for task management.
        Per ADR-008, we rely on LLM for intent recognition.
        """
        return """You are a helpful todo assistant. Your job is to help users manage their tasks.

Available actions:
- Add new tasks when users want to create todos
- List tasks when users want to see their tasks (can filter by status)
- Complete tasks when users mark them as done
- Delete tasks when users want to remove them
- Update tasks when users want to change title or description

Guidelines:
1. Be conversational and friendly in responses
2. When adding a task, extract the title from the user's message
3. When listing tasks, present them in a clear, readable format
4. When a user refers to a task by number or description, find the matching task
5. Confirm actions after completing them
6. If you're unsure what the user wants, ask for clarification
7. When listing tasks, include the task ID so users can reference them
8. Handle errors gracefully - if a task isn't found, explain and suggest alternatives

Remember: You can only manage tasks for the current user. All operations are scoped to their account."""


@lru_cache
def get_agent_settings() -> AgentSettings:
    """Get cached agent settings instance."""
    return AgentSettings()
