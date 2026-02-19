"""
Tests for LLM provider configuration and API key management.

Covers get_api_key() functionality including empty key debug logging.
"""

from io import StringIO

from app.data_models.app_models import AppEnv
from app.llms.providers import get_api_key
from app.utils.log import logger


class TestGetApiKey:
    """Tests for get_api_key() function."""

    def test_empty_api_key_logs_debug_message(self):
        """When a registered provider key resolves to empty string, debug log is emitted."""
        # Capture loguru output
        log_output = StringIO()
        log_id = logger.add(log_output, level="DEBUG", format="{message}")

        try:
            # Create AppEnv with empty OPENAI_API_KEY
            env = AppEnv(OPENAI_API_KEY="")

            # Call get_api_key for OpenAI provider
            success, message = get_api_key("openai", env)

            # Should fail to get the key
            assert success is False
            assert "not found" in message.lower()

            # Should log debug message with env_key name (scrubbed)
            log_content = log_output.getvalue()
            assert "[REDACTED]" in log_content  # API key names are scrubbed
            assert "empty" in log_content.lower()
        finally:
            logger.remove(log_id)

    def test_whitespace_only_api_key_logs_debug_message(self):
        """When a registered provider key resolves to whitespace-only string, debug log is emitted."""
        # Capture loguru output
        log_output = StringIO()
        log_id = logger.add(log_output, level="DEBUG", format="{message}")

        try:
            # Create AppEnv with whitespace-only ANTHROPIC_API_KEY
            env = AppEnv(ANTHROPIC_API_KEY="   ")

            # Call get_api_key for Anthropic provider
            success, message = get_api_key("anthropic", env)

            # Should fail to get the key
            assert success is False
            assert "not found" in message.lower()

            # Should log debug message with env_key name (scrubbed)
            log_content = log_output.getvalue()
            assert "[REDACTED]" in log_content  # API key names are scrubbed
        finally:
            logger.remove(log_id)

    def test_no_log_for_providers_without_api_keys(self):
        """No debug log emitted for providers without API keys (e.g., Ollama)."""
        # Capture loguru output
        log_output = StringIO()
        log_id = logger.add(log_output, level="DEBUG", format="{message}")

        try:
            # Create AppEnv (Ollama doesn't use API keys)
            env = AppEnv()

            # Call get_api_key for Ollama provider
            success, message = get_api_key("ollama", env)

            # Should return False with message about no API key required
            assert success is False
            assert "does not require an API key" in message

            # Should NOT log debug message about empty key
            log_content = log_output.getvalue()
            assert "empty" not in log_content.lower()
        finally:
            logger.remove(log_id)

    def test_no_log_when_key_is_correctly_loaded(self):
        """No debug log emitted when key is correctly loaded."""
        # Capture loguru output
        log_output = StringIO()
        log_id = logger.add(log_output, level="DEBUG", format="{message}")

        try:
            # Create AppEnv with valid OPENAI_API_KEY
            env = AppEnv(OPENAI_API_KEY="sk-valid-key-12345")

            # Call get_api_key for OpenAI provider
            success, message = get_api_key("openai", env)

            # Should succeed
            assert success is True
            assert message == "sk-valid-key-12345"

            # Should NOT log debug message about empty key
            log_content = log_output.getvalue()
            assert "empty" not in log_content.lower()
        finally:
            logger.remove(log_id)

    def test_debug_message_includes_provider_name(self):
        """Debug message includes both env_key and provider name for diagnosis."""
        # Capture loguru output
        log_output = StringIO()
        log_id = logger.add(log_output, level="DEBUG", format="{message}")

        try:
            # Create AppEnv with empty CEREBRAS_API_KEY
            env = AppEnv(CEREBRAS_API_KEY="")

            # Call get_api_key for Cerebras provider
            success, message = get_api_key("cerebras", env)

            # Should fail
            assert success is False

            # Debug log should mention env_key (scrubbed) and provider
            log_content = log_output.getvalue()
            assert "[REDACTED]" in log_content  # API key names are scrubbed
            assert "cerebras" in log_content.lower() or "provider" in log_content.lower()
        finally:
            logger.remove(log_id)
