"""
Test cases for LLM model creation and configuration.

Tests for model creation with different providers, error handling,
and configuration validation.
"""

import pytest
from pydantic_ai.models.openai import OpenAIChatModel

from app.data_models.app_models import EndpointConfig, ProviderConfig
from app.llms.models import create_llm_model, get_llm_model_name


class TestModelNameFormatting:
    """Test model name formatting for different providers."""

    def test_get_llm_model_name_openai(self):
        """Test OpenAI model name formatting."""
        result = get_llm_model_name("openai", "gpt-4")
        assert result == "openai/gpt-4"

    def test_get_llm_model_name_cerebras(self):
        """Test Cerebras model name formatting."""
        result = get_llm_model_name("cerebras", "llama3-8b")
        assert result == "cerebras/llama3-8b"

    def test_get_llm_model_name_groq(self):
        """Test Groq model name formatting."""
        result = get_llm_model_name("groq", "llama-3.1-70b")
        assert result == "groq/llama-3.1-70b"

    def test_get_llm_model_name_already_prefixed(self):
        """Test model name already has provider prefix."""
        result = get_llm_model_name("openai", "openai/gpt-4")
        assert result == "openai/gpt-4"

    def test_get_llm_model_name_unknown_provider(self):
        """Test unknown provider fallback."""
        result = get_llm_model_name("unknown_provider", "model-name")
        assert "unknown_provider" in result.lower()
        assert "model-name" in result


class TestModelCreation:
    """Test model creation with different providers."""

    def test_create_llm_model_openai(self):
        """Test creating OpenAI model."""
        endpoint_config = EndpointConfig(
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)
        assert model.model_name == "gpt-4"

    def test_create_llm_model_ollama(self):
        """Test creating Ollama model."""
        endpoint_config = EndpointConfig(
            provider="ollama",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="llama3",
                base_url="http://localhost:11434/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)
        assert model.model_name == "llama3"

    def test_create_llm_model_cerebras(self):
        """Test creating Cerebras model with strict tool definitions disabled."""
        endpoint_config = EndpointConfig(
            provider="cerebras",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="llama3-8b",
                base_url="https://api.cerebras.ai/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)
        assert model.model_name == "llama3-8b"
        # Cerebras should have strict tool definitions disabled
        assert model.profile.openai_supports_strict_tool_definition is False

    def test_create_llm_model_groq(self):
        """Test creating Groq model with strict tool definitions disabled."""
        endpoint_config = EndpointConfig(
            provider="groq",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="llama-3.1-70b",
                base_url="https://api.groq.com/openai/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)
        # Groq should have strict tool definitions disabled
        assert model.profile.openai_supports_strict_tool_definition is False

    def test_create_llm_model_openrouter(self):
        """Test creating OpenRouter model."""
        endpoint_config = EndpointConfig(
            provider="openrouter",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="openai/gpt-4",
                base_url="https://openrouter.ai/api/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)

    def test_create_llm_model_github(self):
        """Test creating GitHub Models provider model."""
        endpoint_config = EndpointConfig(
            provider="github",
            api_key="test-token",
            provider_config=ProviderConfig(
                model_name="gpt-4o",
                base_url="https://models.inference.ai.azure.com",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)


class TestModelCreationErrorHandling:
    """Test error handling in model creation."""

    def test_create_llm_model_missing_api_key_for_cloud_provider(self):
        """Test that cloud providers work without API key (handled by provider)."""
        endpoint_config = EndpointConfig(
            provider="openai",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        # Should not raise error - uses "not-required" fallback
        model = create_llm_model(endpoint_config)
        assert isinstance(model, OpenAIChatModel)

    def test_create_llm_model_empty_model_name(self):
        """Test error handling for empty model name."""
        endpoint_config = EndpointConfig(
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="",
                base_url="https://api.openai.com/v1",
            ),
        )

        # Empty model name should still create model (validation happens at provider level)
        model = create_llm_model(endpoint_config)
        assert isinstance(model, OpenAIChatModel)


class TestModelConfigurationEdgeCases:
    """Test edge cases in model configuration."""

    def test_create_llm_model_case_insensitive_provider(self):
        """Test that provider names are case-insensitive."""
        endpoint_config = EndpointConfig(
            provider="OpenAI",  # Mixed case
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        model = create_llm_model(endpoint_config)
        assert isinstance(model, OpenAIChatModel)

    def test_create_llm_model_custom_base_url(self):
        """Test model creation with custom base URL."""
        custom_base_url = "https://custom-endpoint.example.com/v1"
        endpoint_config = EndpointConfig(
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url=custom_base_url,
            ),
        )

        model = create_llm_model(endpoint_config)
        assert isinstance(model, OpenAIChatModel)
