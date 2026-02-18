"""
Test cases for LLM model creation and configuration.

Tests for model creation with different providers, error handling,
and configuration validation.
"""

from unittest.mock import MagicMock, patch

from pydantic_ai.models.openai import OpenAIChatModel

from app.data_models.app_models import EndpointConfig, ProviderConfig
from app.llms.models import create_llm_model, get_llm_model_name


class TestModelNameFormatting:
    """Test model name formatting for different providers."""

    def test_get_llm_model_name_openai(self):
        """Test OpenAI model name formatting (no prefix)."""
        result = get_llm_model_name("openai", "gpt-4")
        # OpenAI doesn't use prefix in PROVIDER_REGISTRY
        assert result == "gpt-4"

    def test_get_llm_model_name_cerebras(self):
        """Test Cerebras model name formatting (no prefix)."""
        result = get_llm_model_name("cerebras", "llama3-8b")
        # Cerebras doesn't use prefix in PROVIDER_REGISTRY
        assert result == "llama3-8b"

    def test_get_llm_model_name_groq(self):
        """Test Groq model name formatting."""
        result = get_llm_model_name("groq", "llama-3.1-70b")
        assert result == "groq/llama-3.1-70b"

    def test_get_llm_model_name_already_prefixed(self):
        """Test model name already has provider prefix."""
        # Test with OpenAI which doesn't use prefix
        result = get_llm_model_name("openai", "gpt-4")
        assert result == "gpt-4"  # Already correct, no prefix added

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
            prompts={"manager": "You are a manager"},
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
            prompts={"manager": "You are a manager"},
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
            prompts={"manager": "You are a manager"},
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
        """Test creating Groq model."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="groq",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="llama-3.1-70b",
                base_url="https://api.groq.com/openai/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)

    def test_create_llm_model_openrouter(self):
        """Test creating OpenRouter model."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
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
            prompts={"manager": "You are a manager"},
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
        """Test that cloud providers work without API key (SDK reads OPENAI_API_KEY env var)."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="openai",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        # When api_key=None, OpenAIProvider reads OPENAI_API_KEY env var.
        # Mock OpenAIProvider to avoid requiring real env var in tests.
        with patch("app.llms.models.OpenAIProvider") as mock_provider:
            mock_provider.return_value = MagicMock()
            model = create_llm_model(endpoint_config)
        assert isinstance(model, OpenAIChatModel)

    def test_create_llm_model_empty_model_name(self):
        """Test error handling for empty model name."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
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
            prompts={"manager": "You are a manager"},
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
            prompts={"manager": "You are a manager"},
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url=custom_base_url,
            ),
        )

        model = create_llm_model(endpoint_config)
        assert isinstance(model, OpenAIChatModel)

    def test_create_agent_models_with_all_agents(self):
        """Test creating models for all agent types."""
        from app.llms.models import create_agent_models

        endpoint_config = EndpointConfig(
            prompts={
                "manager": "Manager prompt",
                "researcher": "Researcher prompt",
                "analyst": "Analyst prompt",
                "synthesiser": "Synthesiser prompt",
            },
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        models = create_agent_models(
            endpoint_config,
            include_researcher=True,
            include_analyst=True,
            include_synthesiser=True,
        )

        assert models.model_manager is not None
        assert models.model_researcher is not None
        assert models.model_analyst is not None
        assert models.model_synthesiser is not None

    def test_create_agent_models_manager_only(self):
        """Test creating models with only manager agent."""
        from app.llms.models import create_agent_models

        endpoint_config = EndpointConfig(
            prompts={"manager": "Manager prompt"},
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        models = create_agent_models(
            endpoint_config,
            include_researcher=False,
            include_analyst=False,
            include_synthesiser=False,
        )

        assert models.model_manager is not None
        assert models.model_researcher is None
        assert models.model_analyst is None
        assert models.model_synthesiser is None


class TestProviderSpecificBehavior:
    """Test provider-specific model creation behavior."""

    def test_openai_compatible_provider_without_strict_tools(self):
        """Test that non-OpenAI providers disable strict tool definitions."""
        from app.llms.models import create_llm_model

        # Test with a provider that doesn't support strict tools
        endpoint_config = EndpointConfig(
            prompts={"manager": "Manager prompt"},
            provider="cerebras",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="llama3-8b",
                base_url="https://api.cerebras.ai/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        # Assert strict tool definition is disabled
        assert model.profile.openai_supports_strict_tool_definition is False

    def test_openai_provider_with_strict_tools_enabled(self):
        """Test that OpenAI provider enables strict tool definitions by default."""
        from app.llms.models import create_llm_model

        endpoint_config = EndpointConfig(
            prompts={"manager": "Manager prompt"},
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        # Assert strict tool definition is enabled for OpenAI
        assert model.profile.openai_supports_strict_tool_definition is True


# STORY-002: Sentinel removal tests
class TestSentinelRemoval:
    """Test that 'not-required' sentinel is removed from all non-ollama providers (STORY-002)."""

    def test_openai_api_key_none_passes_none_not_sentinel(self):
        """When api_key=None, OpenAIProvider must receive None not 'not-required'."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="openai",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

        with patch("app.llms.models.OpenAIProvider") as mock_provider:
            mock_provider.return_value = MagicMock()
            create_llm_model(endpoint_config)

        # Must be called with api_key=None (not "not-required")
        call_kwargs = mock_provider.call_args.kwargs
        assert call_kwargs.get("api_key") is None

    def test_openrouter_api_key_none_passes_none_not_sentinel(self):
        """openrouter with api_key=None should pass None to OpenAIProvider."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="openrouter",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="openai/gpt-4",
                base_url="https://openrouter.ai/api/v1",
            ),
        )

        with patch("app.llms.models.OpenAIProvider") as mock_provider:
            mock_provider.return_value = MagicMock()
            create_llm_model(endpoint_config)

        call_kwargs = mock_provider.call_args.kwargs
        assert call_kwargs.get("api_key") is None

    def test_github_api_key_none_passes_none_not_sentinel(self):
        """github with api_key=None should pass None to OpenAIProvider."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="github",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="gpt-4o",
                base_url="https://models.inference.ai.azure.com",
            ),
        )

        with patch("app.llms.models.OpenAIProvider") as mock_provider:
            mock_provider.return_value = MagicMock()
            create_llm_model(endpoint_config)

        call_kwargs = mock_provider.call_args.kwargs
        assert call_kwargs.get("api_key") is None

    def test_cerebras_api_key_none_passes_none_not_sentinel(self):
        """cerebras with api_key=None should pass None to OpenAIProvider."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="cerebras",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="llama3-8b",
                base_url="https://api.cerebras.ai/v1",
            ),
        )

        with patch("app.llms.models.OpenAIProvider") as mock_provider:
            mock_provider.return_value = MagicMock()
            create_llm_model(endpoint_config)

        call_kwargs = mock_provider.call_args.kwargs
        assert call_kwargs.get("api_key") is None

    def test_generic_provider_api_key_none_passes_none_not_sentinel(self):
        """Generic/unknown provider with api_key=None should pass None to OpenAIProvider."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="groq",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="llama-3.1-70b",
                base_url="https://api.groq.com/openai/v1",
            ),
        )

        with patch("app.llms.models.OpenAIProvider") as mock_provider:
            mock_provider.return_value = MagicMock()
            create_llm_model(endpoint_config)

        call_kwargs = mock_provider.call_args.kwargs
        assert call_kwargs.get("api_key") is None

    def test_ollama_retains_not_required_sentinel(self):
        """Ollama provider must retain 'not-required' api_key (no auth needed)."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="ollama",
            api_key=None,
            provider_config=ProviderConfig(
                model_name="llama3",
                base_url="http://localhost:11434/v1",
            ),
        )

        with patch("app.llms.models.OpenAIProvider") as mock_provider:
            mock_provider.return_value = MagicMock()
            create_llm_model(endpoint_config)

        call_kwargs = mock_provider.call_args.kwargs
        # Ollama must use "not-required" since it has no auth
        assert call_kwargs.get("api_key") == "not-required"
