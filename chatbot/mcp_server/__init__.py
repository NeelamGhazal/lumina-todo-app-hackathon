# Task T009: MCP Server Module
"""MCP Server for Todo Operations - Phase III.

This package provides an MCP server that exposes todo CRUD operations
for AI agents via the Model Context Protocol.

Modules:
- models: SQLModel entities (Conversation, Message)
- config: Application configuration
- database: Async database connection
- logging: Structured JSON logging
- main: FastAPI application
"""

from mcp_server.models import Conversation, Message, MessageRole
from mcp_server.config import get_settings, Settings
from mcp_server.database import get_db, get_session
from mcp_server.logging import get_logger, log_tool_call

__all__ = [
    # Models
    "Conversation",
    "Message",
    "MessageRole",
    # Config
    "get_settings",
    "Settings",
    # Database
    "get_db",
    "get_session",
    # Logging
    "get_logger",
    "log_tool_call",
]

__version__ = "0.1.0"
