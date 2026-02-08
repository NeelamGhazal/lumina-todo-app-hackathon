# Task T006: OpenRouter Client Wrapper
"""OpenRouter client wrapper using OpenAI SDK.

This module provides a singleton OpenAI client configured to use
OpenRouter's API endpoint. OpenRouter provides access to various
LLM models through an OpenAI-compatible API.

References:
- research.md: R1 (OpenRouter compatibility), R2 (Chat Completions API)
- plan.md: ADR-005 (manual tool execution)
- spec.md: FR-020 (OpenRouter integration)
"""

from functools import lru_cache
from typing import Any

import structlog
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from agent.config import AgentSettings, get_agent_settings

logger = structlog.get_logger(__name__)


class OpenRouterClient:
    """Wrapper for OpenAI SDK configured for OpenRouter.

    Uses singleton pattern to maintain a single client instance
    across the application lifecycle.

    Attributes:
        client: AsyncOpenAI client configured for OpenRouter
        settings: Agent settings instance
        tools: List of tool definitions in OpenAI format (loaded at startup)
    """

    def __init__(self, settings: AgentSettings) -> None:
        """Initialize OpenRouter client.

        Args:
            settings: Agent settings with API key and model config
        """
        self.settings = settings
        self.tools: list[dict[str, Any]] = []

        # Initialize OpenAI client with OpenRouter base URL
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            default_headers={
                "HTTP-Referer": "https://evolution-todo.app",
                "X-Title": "Evolution Todo Agent",
            },
        )

        logger.info(
            "openrouter_client_initialized",
            model=settings.agent_model,
            base_url=settings.openrouter_base_url,
        )

    def set_tools(self, tools: list[dict[str, Any]]) -> None:
        """Set the tool definitions for function calling.

        Args:
            tools: List of tool definitions in OpenAI function format
        """
        self.tools = tools
        logger.info("tools_registered", tool_count=len(tools))

    async def create_chat_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        use_tools: bool = True,
    ) -> ChatCompletion:
        """Create a chat completion using OpenRouter.

        Args:
            messages: List of messages in OpenAI format
            use_tools: Whether to include tool definitions

        Returns:
            ChatCompletion response from OpenRouter

        Raises:
            OpenAIError: If API call fails
        """
        logger.debug(
            "creating_chat_completion",
            message_count=len(messages),
            use_tools=use_tools,
            model=self.settings.agent_model,
        )

        kwargs: dict[str, Any] = {
            "model": self.settings.agent_model,
            "messages": messages,
        }

        if use_tools and self.tools:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = "auto"

        response = await self.client.chat.completions.create(**kwargs)

        logger.debug(
            "chat_completion_received",
            finish_reason=response.choices[0].finish_reason if response.choices else None,
            has_tool_calls=bool(
                response.choices
                and response.choices[0].message.tool_calls
            ),
        )

        return response

    async def submit_tool_results(
        self,
        messages: list[dict[str, Any]],
        tool_results: list[dict[str, Any]],
    ) -> ChatCompletion:
        """Submit tool execution results and get final response.

        After executing tool calls, this method sends the results back
        to the LLM to generate a natural language response.

        Args:
            messages: Original messages including the assistant's tool call
            tool_results: List of tool result messages

        Returns:
            ChatCompletion with final response
        """
        # Combine original messages with tool results
        all_messages = messages + tool_results

        logger.debug(
            "submitting_tool_results",
            result_count=len(tool_results),
            total_messages=len(all_messages),
        )

        # Get final response without tools (we already have results)
        return await self.create_chat_completion(all_messages, use_tools=False)

    @property
    def is_ready(self) -> bool:
        """Check if client is ready for use."""
        return self.settings.is_configured


# Singleton instance
_client_instance: OpenRouterClient | None = None


@lru_cache
def get_openrouter_client() -> OpenRouterClient:
    """Get singleton OpenRouter client instance.

    Returns:
        OpenRouterClient instance

    Note:
        Client is created on first call and cached.
        Tools should be loaded separately at startup.
    """
    global _client_instance
    if _client_instance is None:
        settings = get_agent_settings()
        _client_instance = OpenRouterClient(settings)
    return _client_instance


def reset_client() -> None:
    """Reset the singleton client (for testing)."""
    global _client_instance
    _client_instance = None
    get_openrouter_client.cache_clear()


# Task T013: Initialize client with tools at startup
async def initialize_agent() -> bool:
    """Initialize the agent client with MCP tools.

    Should be called during application startup (lifespan handler).
    Fetches tool schemas from MCP server and registers them with
    the OpenRouter client.

    Returns:
        True if initialization succeeded, False otherwise

    Note:
        Per ADR-007, tools are loaded once at startup.
        If MCP server is unavailable, agent will start without tools.
    """
    from agent.tools import get_openai_tools, MCPServerUnavailable

    client = get_openrouter_client()

    if not client.settings.is_configured:
        logger.warning(
            "agent_not_configured",
            message="OPENROUTER_API_KEY not set",
        )
        return False

    try:
        tools = await get_openai_tools()
        client.set_tools(tools)
        logger.info(
            "agent_initialized",
            tool_count=len(tools),
            model=client.settings.agent_model,
        )
        return True
    except MCPServerUnavailable as e:
        logger.warning(
            "agent_init_mcp_unavailable",
            error=str(e),
            message="Agent starting without tools - MCP server unavailable",
        )
        return False
    except Exception as e:
        logger.error(
            "agent_init_failed",
            error=str(e),
        )
        return False
