"""
Test cases for LLM model creation and configuration.

Tests for model instantiation across different providers and error handling.
"""

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel

from app.data_models.app_models import EndpointConfig, ProviderConfig
from app.llms.models import create_agent_models, create_llm_model, create_simple_model


class TestModelCreation:
    """Test basic model creation functionality."""

    def test_create_llm_model_with_openai(self):
        """Test creating an OpenAI model."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini", base_url="https://api.openai.com/v1"
            ),
            api_key="test-api-key",
            prompts={},  # Required field
        )

        # Act
        model = create_llm_model(endpoint_config)

        # Assert
        assert model is not None
        assert isinstance(model, Model)

    def test_create_llm_model_with_ollama(self):
        """Test creating an Ollama model with local base URL."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="ollama",
            provider_config=ProviderConfig(
                model_name="llama3.2:1b", base_url="http://localhost:11434/v1"
            ),
            api_key=None,
            prompts={},  # Required field
        )

        # Act
        model = create_llm_model(endpoint_config)

        # Assert
        assert model is not None
        assert isinstance(model, OpenAIChatModel)

    def test_create_llm_model_with_cerebras(self):
        """Test creating a Cerebras model with strict tool definition disabled."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="cerebras",
            provider_config=ProviderConfig(
                model_name="llama-3.3-70b", base_url="https://api.cerebras.ai/v1"
            ),
            api_key="test-cerebras-key",
            prompts={},  # Required field
        )

        # Act
        model = create_llm_model(endpoint_config)

        # Assert
        assert model is not None
        assert isinstance(model, OpenAIChatModel)


class TestModelCreationErrorHandling:
    """Test error handling in model creation."""

    def test_create_llm_model_with_unsupported_provider(self):
        """Test creating a model with an unsupported provider."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="unsupported_provider",
            provider_config=ProviderConfig(
                model_name="test-model", base_url="https://example.com/v1"
            ),
            api_key="test-key",
            prompts={},  # Required field
        )

        # Act - should fall through to generic OpenAI-compatible handler
        model = create_llm_model(endpoint_config)

        # Assert - should not raise, fallback to generic handler
        assert model is not None

    def test_create_llm_model_with_invalid_base_url(self):
        """Test model creation with invalid base URL format.

        Note: Pydantic validates URLs at config creation time, so this test
        cannot create a config with an invalid URL. Testing validation happens
        during config creation, not model creation."""
        # This test is effectively testing that Pydantic validation works
        from pydantic import ValidationError

        # Act & Assert - Pydantic should reject invalid URL during config creation
        try:
            _ = EndpointConfig(
                provider="openai",
                provider_config=ProviderConfig(
                    model_name="gpt-4o-mini", base_url="not-a-valid-url"
                ),
                api_key="test-key",
                prompts={},  # Required field
            )
            # If we get here, URL validation was not enforced (unexpected)
            assert False, "Expected ValidationError for invalid URL"
        except ValidationError:
            # Expected - Pydantic rejects invalid URLs
            pass

    def test_create_llm_model_with_missing_api_key(self):
        """Test model creation when API key is missing."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini", base_url="https://api.openai.com/v1"
            ),
            api_key=None,  # Missing API key
            prompts={},  # Required field
        )

        # Act - should use fallback "not-required"
        model = create_llm_model(endpoint_config)

        # Assert
        assert model is not None


class TestAgentModelsCreation:
    """Test creating model dictionaries for multi-agent systems."""

    def test_create_agent_models_with_all_agents_enabled(self):
        """Test creating models with all agents enabled."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini", base_url="https://api.openai.com/v1"
            ),
            api_key="test-key",
            prompts={},  # Required field
        )

        # Act
        model_dict = create_agent_models(
            endpoint_config,
            include_researcher=True,
            include_analyst=True,
            include_synthesiser=True,
        )

        # Assert
        assert model_dict.model_manager is not None
        assert model_dict.model_researcher is not None
        assert model_dict.model_analyst is not None
        assert model_dict.model_synthesiser is not None

    def test_create_agent_models_with_single_agent(self):
        """Test creating models with only manager agent."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini", base_url="https://api.openai.com/v1"
            ),
            api_key="test-key",
            prompts={},  # Required field
        )

        # Act
        model_dict = create_agent_models(
            endpoint_config,
            include_researcher=False,
            include_analyst=False,
            include_synthesiser=False,
        )

        # Assert
        assert model_dict.model_manager is not None
        assert model_dict.model_researcher is None
        assert model_dict.model_analyst is None
        assert model_dict.model_synthesiser is None

    def test_create_agent_models_with_partial_agents(self):
        """Test creating models with only some agents enabled."""
        # Arrange
        endpoint_config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini", base_url="https://api.openai.com/v1"
            ),
            api_key="test-key",
            prompts={},  # Required field
        )

        # Act
        model_dict = create_agent_models(
            endpoint_config,
            include_researcher=True,
            include_analyst=False,
            include_synthesiser=True,
        )

        # Assert
        assert model_dict.model_manager is not None
        assert model_dict.model_researcher is not None
        assert model_dict.model_analyst is None
        assert model_dict.model_synthesiser is not None


class TestSimpleModelCreation:
    """Test simple model creation function."""

    def test_create_simple_model_with_openai(self):
        """Test creating a simple OpenAI model."""
        # Act
        model = create_simple_model("openai", "gpt-4o-mini", api_key="test-key")

        # Assert
        assert model is not None
        assert isinstance(model, OpenAIChatModel)

    def test_create_simple_model_with_github(self):
        """Test creating a simple GitHub model."""
        # Act
        model = create_simple_model("github", "gpt-4o-mini", api_key="test-key")

        # Assert
        assert model is not None
        assert isinstance(model, OpenAIChatModel)

    def test_create_simple_model_with_generic_provider(self):
        """Test creating a simple model with generic provider."""
        # Act
        model = create_simple_model("generic", "test-model", api_key="test-key")

        # Assert
        assert model is not None
        assert isinstance(model, OpenAIChatModel)

    def test_create_simple_model_without_api_key(self):
        """Test creating a simple model without providing API key."""
        # Act
        model = create_simple_model("openai", "gpt-4o-mini")

        # Assert
        assert model is not None
