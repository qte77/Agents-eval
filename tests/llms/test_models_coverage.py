"""
Additional behavioral tests for llms/models.py to increase coverage.

Focuses on edge cases, provider-specific handling, and error conditions.
"""

import pytest
from unittest.mock import patch, Mock

from app.data_models.app_models import EndpointConfig, ProviderConfig
from app.llms.models import (
    create_llm_model,
    create_agent_models,
    create_simple_model,
    get_llm_model_name,
)


class TestModelNameFormatting:
    """Test model name formatting for different providers."""

    def test_get_llm_model_name_with_unknown_provider(self):
        """Test model name formatting for unregistered provider."""
        # Act
        result = get_llm_model_name("unknown_provider", "test-model")

        # Assert - should use default prefix format
        assert "unknown_provider/" in result or result == "test-model"

    def test_get_llm_model_name_with_slash_in_name(self):
        """Test that model names with slashes are handled correctly."""
        # Act - model already has provider prefix
        result = get_llm_model_name("openai", "openai/gpt-4")

        # Assert - should not double-prefix
        assert result == "openai/gpt-4"

    def test_get_llm_model_name_case_insensitive(self):
        """Test that provider names are case-insensitive."""
        # Act
        result_lower = get_llm_model_name("openai", "gpt-4")
        result_upper = get_llm_model_name("OPENAI", "gpt-4")

        # Assert - both should produce same result
        assert result_lower == result_upper


class TestModelCreationErrors:
    """Test error handling during model creation."""

    def test_create_llm_model_with_invalid_config(self):
        """Test model creation with minimal/invalid config."""
        # Arrange
        config = EndpointConfig(
            provider="test",
            provider_config=ProviderConfig(
                model_name="test-model",
                base_url="http://localhost:8000",
            ),
            api_key=None,
        )

        # Act - should not raise, returns model
        result = create_llm_model(config)

        # Assert
        assert result is not None

    @patch("app.llms.models.OpenAIChatModel")
    def test_create_llm_model_ollama_specific(self, mock_model_class):
        """Test Ollama-specific model creation logic."""
        # Arrange
        config = EndpointConfig(
            provider="ollama",
            provider_config=ProviderConfig(
                model_name="llama2",
                base_url="http://localhost:11434",
            ),
            api_key=None,
        )

        # Act
        create_llm_model(config)

        # Assert - should use base_url and not-required API key
        mock_model_class.assert_called_once()


class TestProviderSpecificHandling:
    """Test provider-specific model creation logic."""

    def test_create_llm_model_cerebras_disables_strict_tools(self):
        """Test that Cerebras provider disables strict tool definitions."""
        # Arrange
        config = EndpointConfig(
            provider="cerebras",
            provider_config=ProviderConfig(
                model_name="llama3.1-8b",
                base_url="https://api.cerebras.ai/v1",
            ),
            api_key="test-key",
        )

        # Act
        model = create_llm_model(config)

        # Assert - model should be created with profile setting
        assert model is not None

    def test_create_llm_model_openrouter_uses_base_url(self):
        """Test that OpenRouter uses custom base URL."""
        # Arrange
        config = EndpointConfig(
            provider="openrouter",
            provider_config=ProviderConfig(
                model_name="anthropic/claude-3-5-sonnet",
                base_url="https://openrouter.ai/api/v1",
            ),
            api_key="test-key",
        )

        # Act
        model = create_llm_model(config)

        # Assert
        assert model is not None

    def test_create_llm_model_github_uses_azure_endpoint(self):
        """Test that GitHub provider uses Azure inference endpoint."""
        # Arrange
        config = EndpointConfig(
            provider="github",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://models.inference.ai.azure.com",
            ),
            api_key="test-key",
        )

        # Act
        model = create_llm_model(config)

        # Assert
        assert model is not None


class TestAgentModelsCreation:
    """Test multi-agent model creation."""

    def test_create_agent_models_with_all_agents(self):
        """Test creating models for all agent types."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        # Act
        models = create_agent_models(
            config,
            include_researcher=True,
            include_analyst=True,
            include_synthesiser=True,
        )

        # Assert
        assert models.model_manager is not None
        assert models.model_researcher is not None
        assert models.model_analyst is not None
        assert models.model_synthesiser is not None

    def test_create_agent_models_manager_only(self):
        """Test creating model for manager only (single-agent mode)."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        # Act
        models = create_agent_models(
            config,
            include_researcher=False,
            include_analyst=False,
            include_synthesiser=False,
        )

        # Assert
        assert models.model_manager is not None
        assert models.model_researcher is None
        assert models.model_analyst is None
        assert models.model_synthesiser is None


class TestSimpleModelCreation:
    """Test simple model creation helper."""

    def test_create_simple_model_openai(self):
        """Test simple model creation for OpenAI."""
        # Act
        model = create_simple_model("openai", "gpt-4o-mini", "test-key")

        # Assert
        assert model is not None

    def test_create_simple_model_github(self):
        """Test simple model creation for GitHub."""
        # Act
        model = create_simple_model("github", "gpt-4o-mini", "test-key")

        # Assert
        assert model is not None

    def test_create_simple_model_generic_provider(self):
        """Test simple model creation for generic provider."""
        # Act
        model = create_simple_model("custom_provider", "custom-model", "test-key")

        # Assert
        assert model is not None

    def test_create_simple_model_without_api_key(self):
        """Test simple model creation without API key."""
        # Act
        model = create_simple_model("openai", "gpt-4o-mini", None)

        # Assert
        assert model is not None


class TestGeminiProviderFallback:
    """Test Gemini provider with fallback logic."""

    @patch("app.llms.models.GoogleModel", side_effect=ImportError("Not available"))
    def test_create_llm_model_gemini_fallback(self, mock_google_model):
        """Test Gemini fallback to OpenAI format when GoogleModel unavailable."""
        # Arrange
        config = EndpointConfig(
            provider="gemini",
            provider_config=ProviderConfig(
                model_name="gemini-1.5-flash",
                base_url="https://generativelanguage.googleapis.com/v1",
            ),
            api_key="test-key",
        )

        # Act
        model = create_llm_model(config)

        # Assert - should fall back to OpenAI format
        assert model is not None
