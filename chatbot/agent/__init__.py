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

__all__ = [
    # Configuration
    "AgentSettings",
    "get_agent_settings",
    # Schemas
    "ChatRequest",
    "ChatResponse",
    "ToolCallSummary",
]

__version__ = "0.1.0"
