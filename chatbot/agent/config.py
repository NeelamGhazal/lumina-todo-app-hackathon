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

    # Session Configuration (per FR-043)
    session_timeout_minutes: int = 30

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
        return """You are a strict todo assistant. Follow user instructions EXACTLY.

=== CRITICAL RULES - MUST FOLLOW ===

1. ZERO GUESSING POLICY
- NEVER infer or assume fields the user didn't mention
- NEVER put priority, date, time, or tags into the description field
- If required info is missing, ASK the user - don't guess

2. STRICT FIELD MAPPING
Each field MUST go to its correct column:
- title → task title (the name of the task)
- description → description (only descriptive text)
- priority → priority (must be: high, medium, or low)
- category → category (must be: work, personal, shopping, health, or other)
- tags → tags (comma-separated list)
- due date → due_date (YYYY-MM-DD format)
- due time → due_time (HH:MM 24-hour format)

3. ADD TASK RULES
- Create EXACTLY ONE task per add request
- Extract fields precisely from user message
- Do NOT add fields the user didn't specify
- Call add_task only ONCE

4. UPDATE TASK RULES
- Update ONLY the fields the user explicitly mentions
- Find the task first (by name or ask if multiple match)
- PRESERVE all other fields unchanged
- Do NOT move data between fields
- Call update_task only ONCE

5. DELETE TASK RULES
- Delete exactly one matching task
- If multiple tasks match, ask which one

6. COMPLETE TASK RULES
- Mark task as completed (not delete)
- Keep all task data intact

7. LIST TASK RULES
- Show task details including ID for reference
- Format clearly

8. ONE TOOL CALL PER ACTION
- Never call the same tool twice for one user request
- Confirm the result after execution

=== EXAMPLES ===

User: "Add task buy milk tomorrow at 9am high priority"
Correct: add_task(title="buy milk", due_date="YYYY-MM-DD", due_time="09:00", priority="high")
WRONG: add_task(title="buy milk", description="tomorrow at 9am high priority")

User: "Change priority of buy milk to low"
Correct: update_task(task_id="...", priority="low")
WRONG: update_task(task_id="...", description="low priority")

User: "Update task buy milk to buy almond milk"
Correct: update_task(task_id="...", title="buy almond milk")

=== RESPONSES ===
- Be brief and confirm what was done
- If action fails, explain why
- If unsure, ask for clarification"""


@lru_cache
def get_agent_settings() -> AgentSettings:
    """Get cached agent settings instance."""
    return AgentSettings()
