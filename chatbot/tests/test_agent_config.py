# Task T023: Agent Config Tests
"""Tests for agent configuration module.

Tests:
- Settings loading from environment
- Default values
- Agent instructions template
- Configuration validation
"""

import os
from unittest.mock import patch

import pytest

from agent.config import AgentSettings, get_agent_settings


class TestAgentSettings:
    """Tests for AgentSettings class."""

    def test_default_values(self):
        """Test default configuration values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = AgentSettings()

            assert settings.agent_model == "gpt-4o-mini"
            assert settings.mcp_server_url == "http://localhost:8001"
            assert settings.context_message_limit == 10
            assert settings.max_tool_rounds == 5
            assert settings.openrouter_base_url == "https://openrouter.ai/api/v1"

    def test_environment_override(self):
        """Test configuration from environment variables."""
        env = {
            "OPENROUTER_API_KEY": "test-key-123",
            "AGENT_MODEL": "gpt-4o",
            "MCP_SERVER_URL": "http://custom:9000",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = AgentSettings()

            assert settings.openrouter_api_key == "test-key-123"
            assert settings.agent_model == "gpt-4o"
            assert settings.mcp_server_url == "http://custom:9000"

    def test_is_configured_with_key(self):
        """Test is_configured returns True when API key is set."""
        env = {"OPENROUTER_API_KEY": "sk-or-v1-test"}
        with patch.dict(os.environ, env, clear=True):
            settings = AgentSettings()
            assert settings.is_configured is True

    def test_is_configured_without_key(self):
        """Test is_configured returns False when API key is empty."""
        with patch.dict(os.environ, {}, clear=True):
            settings = AgentSettings()
            assert settings.is_configured is False

    def test_agent_instructions_not_empty(self):
        """Test agent instructions template is populated."""
        settings = AgentSettings()
        instructions = settings.agent_instructions

        assert len(instructions) > 100
        assert "todo" in instructions.lower()
        assert "task" in instructions.lower()

    def test_agent_instructions_contains_guidelines(self):
        """Test agent instructions include key guidelines."""
        settings = AgentSettings()
        instructions = settings.agent_instructions

        # Should mention key actions
        assert "add" in instructions.lower()
        assert "list" in instructions.lower()
        assert "complete" in instructions.lower()
        assert "delete" in instructions.lower()

    def test_openrouter_base_url_property(self):
        """Test OpenRouter base URL is correctly set."""
        settings = AgentSettings()
        assert settings.openrouter_base_url == "https://openrouter.ai/api/v1"


class TestGetAgentSettings:
    """Tests for get_agent_settings function."""

    def test_returns_settings_instance(self):
        """Test get_agent_settings returns AgentSettings instance."""
        # Clear cache first
        get_agent_settings.cache_clear()

        settings = get_agent_settings()
        assert isinstance(settings, AgentSettings)

    def test_caches_settings(self):
        """Test get_agent_settings returns cached instance."""
        get_agent_settings.cache_clear()

        settings1 = get_agent_settings()
        settings2 = get_agent_settings()

        assert settings1 is settings2
