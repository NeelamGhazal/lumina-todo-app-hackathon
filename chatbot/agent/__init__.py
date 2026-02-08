# Task T003: Agent Module Initialization
"""
OpenAI Agent with MCP Integration - Phase III Part 2

This module provides a conversational AI agent that uses OpenAI SDK
routed through OpenRouter to process natural language task requests
and execute MCP tools.

Components:
- config: Agent configuration and instructions
- client: OpenRouter client wrapper
- schemas: Chat request/response models
- tools: MCP tool integration layer
- conversation: Session and context management
- chat: Main chat orchestration
"""

from agent.config import AgentSettings, get_agent_settings
from agent.schemas import ChatRequest, ChatResponse, ToolCallSummary
from agent.client import (
    OpenRouterClient,
    get_openrouter_client,
    initialize_agent,
)
from agent.tools import (
    execute_mcp_tool,
    get_openai_tools,
    MCPToolError,
)
from agent.conversation import (
    get_or_create_conversation,
    get_context_messages,
    store_message,
    update_conversation_activity,
    get_user_conversations,
    get_conversation_messages,
)
from agent.chat import process_chat

__all__ = [
    # Configuration
    "AgentSettings",
    "get_agent_settings",
    # Schemas
    "ChatRequest",
    "ChatResponse",
    "ToolCallSummary",
    # Client
    "OpenRouterClient",
    "get_openrouter_client",
    "initialize_agent",
    # Tools
    "execute_mcp_tool",
    "get_openai_tools",
    "MCPToolError",
    # Conversation
    "get_or_create_conversation",
    "get_context_messages",
    "store_message",
    "update_conversation_activity",
    "get_user_conversations",
    "get_conversation_messages",
    # Chat
    "process_chat",
]

__version__ = "0.1.0"
