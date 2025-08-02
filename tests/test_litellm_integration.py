"""
Tests for LLM integration with the agent system.

This module tests the LLM-based model functions and their integration
with PydanticAI agents, including proper API key handling, model creation,
and environment setup.
"""

import os
from unittest.mock import Mock, patch

import pytest

from app.agents.llm_model_funs import (
    _get_llm_model_name,  # type:ignore[reportPrivateUsage]
    get_api_key,
    get_models,
    setup_llm_environment,
)
from app.data_models.app_models import AppEnv, EndpointConfig, ProviderConfig


class TestLLMModelFunctions:
    """Test suite for LLM model function utilities."""

    def test_get_llm_model_name_openai(self):
        """Test LLM model name formatting for OpenAI."""
        result = _get_llm_model_name("openai", "gpt-4")
        assert result == "gpt-4"

    def test_get_llm_model_name_anthropic(self):
        """Test LLM model name formatting for Anthropic."""
        result = _get_llm_model_name("anthropic", "claude-3-sonnet")
        assert result == "anthropic/claude-3-sonnet"

    def test_get_llm_model_name_gemini(self):
        """Test LLM model name formatting for Gemini."""
        result = _get_llm_model_name("gemini", "gemini-pro")
        assert result == "gemini/gemini-pro"

    def test_get_llm_model_name_already_formatted(self):
        """Test that already formatted model names are not double-prefixed."""
        result = _get_llm_model_name("anthropic", "anthropic/claude-3-sonnet")
        assert result == "anthropic/claude-3-sonnet"

    def test_get_api_key_ollama(self):
        """Test API key retrieval for Ollama (should not require key)."""
        mock_env = Mock(spec=AppEnv)
        has_key, message = get_api_key("ollama", mock_env)
        assert has_key is False
        assert "does not require an API key" in message

    def test_get_api_key_openai_success(self):
        """Test successful API key retrieval for OpenAI."""
        mock_env = Mock(spec=AppEnv)
        mock_env.OPENAI_API_KEY = "test-key"

        has_key, message = get_api_key("openai", mock_env)
        assert has_key is True
        assert message == "test-key"

    def test_get_api_key_missing(self):
        """Test API key retrieval when key is missing."""
        mock_env = Mock(spec=AppEnv)
        mock_env.OPENAI_API_KEY = ""

        has_key, message = get_api_key("openai", mock_env)
        assert has_key is False
        assert "not found in configuration" in message

    def test_get_api_key_unsupported_provider(self):
        """Test API key retrieval for unsupported provider."""
        mock_env = Mock(spec=AppEnv)

        has_key, message = get_api_key("unsupported", mock_env)
        assert has_key is False
        assert "is not supported" in message

    @patch.dict(os.environ, {}, clear=True)
    def test_setup_llm_environment(self):
        """Test LLM environment variable setup."""
        api_keys = {
            "openai": "test-openai-key",
            "anthropic": "test-anthropic-key",
            "gemini": "",  # Empty key should be ignored
        }

        setup_llm_environment(api_keys)

        assert os.environ.get("OPENAI_API_KEY") == "test-openai-key"
        assert os.environ.get("ANTHROPIC_API_KEY") == "test-anthropic-key"
        assert os.environ.get("GEMINI_API_KEY") is None

    @patch("app.agents.llm_model_funs._create_llm_model")
    def test_get_models_all_agents(self, mock_create_model):
        """Test model creation for all agent types."""
        mock_model = Mock()
        mock_create_model.return_value = mock_model

        mock_config = Mock(spec=EndpointConfig)

        result = get_models(
            mock_config,
            include_researcher=True,
            include_analyst=True,
            include_synthesiser=True,
        )

        assert result.model_manager == mock_model
        assert result.model_researcher == mock_model
        assert result.model_analyst == mock_model
        assert result.model_synthesiser == mock_model

    @patch("app.agents.llm_model_funs._create_llm_model")
    def test_get_models_manager_only(self, mock_create_model):
        """Test model creation for manager agent only."""
        mock_model = Mock()
        mock_create_model.return_value = mock_model

        mock_config = Mock(spec=EndpointConfig)

        result = get_models(mock_config)

        assert result.model_manager == mock_model
        assert result.model_researcher is None
        assert result.model_analyst is None
        assert result.model_synthesiser is None


class TestLLMIntegration:
    """Integration tests for LLM with agent system."""

    @pytest.fixture
    def mock_endpoint_config(self):
        """Create a mock EndpointConfig for testing."""
        provider_config = ProviderConfig(
            model_name="gpt-4",
            base_url="https://api.openai.com/v1",  # type:ignore[reportArgumentType]
        )

        return EndpointConfig(
            provider="openai",
            api_key="test-key",
            prompts={"system_prompt_manager": "You are a helpful assistant."},
            provider_config=provider_config,
        )

    @patch("app.agents.llm_model_funs.OpenAIModel")
    @patch("app.agents.llm_model_funs.OpenAIProvider")
    def test_create_llm_model_openai(
        self, mock_provider, mock_model, mock_endpoint_config
    ):
        """Test LLM model creation for OpenAI."""
        from app.agents.llm_model_funs import (
            _create_llm_model,  # type:ignore[reportPrivateUsage]
        )

        _create_llm_model(mock_endpoint_config)

        mock_provider.assert_called_once()
        mock_model.assert_called_once()

    @patch("app.agents.llm_model_funs.OpenAIModel")
    @patch("app.agents.llm_model_funs.OpenAIProvider")
    def test_create_llm_model_ollama(
        self, mock_provider, mock_model, mock_endpoint_config
    ):
        """Test LLM model creation for Ollama."""
        from app.agents.llm_model_funs import (
            _create_llm_model,  # type:ignore[reportPrivateUsage]
        )

        mock_endpoint_config.provider = "ollama"
        mock_endpoint_config.provider_config.base_url = "http://localhost:11434"
        mock_endpoint_config.api_key = None

        _create_llm_model(mock_endpoint_config)

        mock_provider.assert_called_once_with(
            base_url="http://localhost:11434",
            api_key="not-required",
        )
        mock_model.assert_called_once()


@pytest.mark.asyncio
class TestLLMAgentSystem:
    """Async tests for LLM integration with agent system."""

    @patch("app.agents.llm_model_funs.setup_llm_environment")
    @patch("app.agents.agent_system.get_api_key")
    @patch("app.agents.agent_system.get_provider_config")
    def test_setup_agent_env_calls_llm_setup(
        self, mock_get_provider_config, mock_get_api_key, mock_setup_llm
    ):
        """Test that setup_agent_env calls LLM environment setup."""
        from app.agents.agent_system import setup_agent_env
        from app.data_models.app_models import ChatConfig

        # Mock dependencies
        mock_get_api_key.return_value = (True, "test-key")
        mock_provider_config = Mock(spec=ProviderConfig)
        mock_provider_config.usage_limits = None
        mock_get_provider_config.return_value = mock_provider_config

        # Create mock chat config
        mock_chat_config = Mock(spec=ChatConfig)
        mock_chat_config.providers = {"openai": mock_provider_config}
        mock_chat_config.prompts = {"system_prompt_manager": "Test prompt"}

        # Create mock env config
        mock_env_config = Mock(spec=AppEnv)
        mock_env_config.OPENAI_API_KEY = "test-openai-key"
        mock_env_config.ANTHROPIC_API_KEY = "test-anthropic-key"
        mock_env_config.GEMINI_API_KEY = ""
        mock_env_config.GROK_API_KEY = ""
        mock_env_config.HUGGINGFACE_API_KEY = ""
        mock_env_config.OPENROUTER_API_KEY = ""
        mock_env_config.PERPLEXITY_API_KEY = ""
        mock_env_config.TOGETHER_API_KEY = ""

        setup_agent_env("openai", "test query", mock_chat_config, mock_env_config)

        # Verify LLM environment setup was called
        mock_setup_llm.assert_called_once()
        call_args = mock_setup_llm.call_args[0][0]
        assert call_args["openai"] == "test-openai-key"
        assert call_args["anthropic"] == "test-anthropic-key"
