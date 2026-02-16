"""
Tests for LLM provider configuration and API key management.

Covers get_api_key() functionality including empty key debug logging.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.data_models.app_models import AppEnv
from app.llms.providers import get_api_key


class TestGetApiKey:
    """Tests for get_api_key() function."""

    def test_empty_api_key_logs_debug_message(self, caplog):
        """When a registered provider key resolves to empty string, debug log is emitted."""
        import logging

        caplog.set_level(logging.DEBUG)

        # Create AppEnv with empty OPENAI_API_KEY
        env = AppEnv(OPENAI_API_KEY="")

        # Call get_api_key for OpenAI provider
        success, message = get_api_key("openai", env)

        # Should fail to get the key
        assert success is False
        assert "not found" in message.lower()

        # Should log debug message with env_key name
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        assert len(debug_logs) >= 1

        # Debug log should mention the env_key name (OPENAI_API_KEY)
        debug_message = " ".join([record.message for record in debug_logs])
        assert "OPENAI_API_KEY" in debug_message
        assert "empty" in debug_message.lower()

    def test_whitespace_only_api_key_logs_debug_message(self, caplog):
        """When a registered provider key resolves to whitespace-only string, debug log is emitted."""
        import logging

        caplog.set_level(logging.DEBUG)

        # Create AppEnv with whitespace-only ANTHROPIC_API_KEY
        env = AppEnv(ANTHROPIC_API_KEY="   ")

        # Call get_api_key for Anthropic provider
        success, message = get_api_key("anthropic", env)

        # Should fail to get the key
        assert success is False
        assert "not found" in message.lower()

        # Should log debug message with env_key name
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        assert len(debug_logs) >= 1

        # Debug log should mention the env_key name
        debug_message = " ".join([record.message for record in debug_logs])
        assert "ANTHROPIC_API_KEY" in debug_message

    def test_no_log_for_providers_without_api_keys(self, caplog):
        """No debug log emitted for providers without API keys (e.g., Ollama)."""
        import logging

        caplog.set_level(logging.DEBUG)

        # Create AppEnv (Ollama doesn't use API keys)
        env = AppEnv()

        # Call get_api_key for Ollama provider
        success, message = get_api_key("ollama", env)

        # Should return False with message about no API key required
        assert success is False
        assert "does not require an API key" in message

        # Should NOT log debug message about empty key
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        empty_key_logs = [
            record
            for record in debug_logs
            if "empty" in record.message.lower()
        ]
        assert len(empty_key_logs) == 0

    def test_no_log_when_key_is_correctly_loaded(self, caplog):
        """No debug log emitted when key is correctly loaded."""
        import logging

        caplog.set_level(logging.DEBUG)

        # Create AppEnv with valid OPENAI_API_KEY
        env = AppEnv(OPENAI_API_KEY="sk-valid-key-12345")

        # Call get_api_key for OpenAI provider
        success, message = get_api_key("openai", env)

        # Should succeed
        assert success is True
        assert message == "sk-valid-key-12345"

        # Should NOT log debug message about empty key
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        empty_key_logs = [
            record
            for record in debug_logs
            if "empty" in record.message.lower()
        ]
        assert len(empty_key_logs) == 0

    def test_debug_message_includes_provider_name(self, caplog):
        """Debug message includes both env_key and provider name for diagnosis."""
        import logging

        caplog.set_level(logging.DEBUG)

        # Create AppEnv with empty CEREBRAS_API_KEY
        env = AppEnv(CEREBRAS_API_KEY="")

        # Call get_api_key for Cerebras provider
        success, message = get_api_key("cerebras", env)

        # Should fail
        assert success is False

        # Debug log should mention both env_key and provider
        debug_logs = [record for record in caplog.records if record.levelname == "DEBUG"]
        debug_message = " ".join([record.message for record in debug_logs])
        assert "CEREBRAS_API_KEY" in debug_message
        assert ("cerebras" in debug_message.lower() or "provider" in debug_message.lower())
