"""
Additional behavioral tests for agent_factories.py to increase coverage.

Focuses on agent creation with various toggle combinations,
system prompt construction, and error handling.
"""

import pytest
from unittest.mock import Mock, patch

from app.agents.agent_factories import AgentFactory
from app.data_models.app_models import EndpointConfig, ProviderConfig, ModelDict


class TestAgentFactoryInitialization:
    """Test AgentFactory initialization and configuration."""

    def test_agent_factory_with_config(self):
        """Test factory initialization with endpoint config."""
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
        factory = AgentFactory(config)

        # Assert
        assert factory.endpoint_config == config
        assert factory._models is None  # Lazy initialization

    def test_agent_factory_without_config(self):
        """Test factory initialization without config."""
        # Act
        factory = AgentFactory(None)

        # Assert
        assert factory.endpoint_config is None
        assert factory._models is None


class TestModelRetrieval:
    """Test model retrieval and lazy initialization."""

    @patch("app.agents.agent_factories.create_agent_models")
    def test_get_models_lazy_initialization(self, mock_create_models):
        """Test that models are created lazily on first access."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_model = Mock()
        mock_create_models.return_value = ModelDict(
            model_manager=mock_model,
            model_researcher=None,
            model_analyst=None,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act - first call should create models
        models1 = factory.get_models()
        models2 = factory.get_models()

        # Assert - should only create once
        assert mock_create_models.call_count == 1
        assert models1 is models2  # Same instance

    def test_get_models_without_config_returns_empty(self):
        """Test model retrieval without config returns empty ModelDict."""
        # Arrange
        factory = AgentFactory(None)

        # Act
        models = factory.get_models()

        # Assert
        assert models.model_manager is None
        assert models.model_researcher is None
        assert models.model_analyst is None
        assert models.model_synthesiser is None

    @patch("app.agents.agent_factories.create_agent_models")
    def test_get_models_with_agent_toggles(self, mock_create_models):
        """Test model retrieval respects agent toggle flags."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_model = Mock()
        mock_create_models.return_value = ModelDict(
            model_manager=mock_model,
            model_researcher=mock_model,
            model_analyst=None,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act
        models = factory.get_models(include_researcher=True, include_analyst=False)

        # Assert
        mock_create_models.assert_called_once_with(
            config,
            include_researcher=True,
            include_analyst=False,
            include_synthesiser=False,
        )


class TestManagerAgentCreation:
    """Test manager agent creation."""

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_manager_agent_with_default_prompt(self, mock_create_models):
        """Test manager agent creation with default system prompt."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_model = Mock()
        mock_create_models.return_value = ModelDict(
            model_manager=mock_model,
            model_researcher=None,
            model_analyst=None,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act
        agent = factory.create_manager_agent()

        # Assert
        assert agent is not None

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_manager_agent_with_custom_prompt(self, mock_create_models):
        """Test manager agent creation with custom system prompt."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_model = Mock()
        mock_create_models.return_value = ModelDict(
            model_manager=mock_model,
            model_researcher=None,
            model_analyst=None,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)
        custom_prompt = "Custom manager instructions"

        # Act
        agent = factory.create_manager_agent(system_prompt=custom_prompt)

        # Assert
        assert agent is not None

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_manager_agent_without_model_raises_error(self, mock_create_models):
        """Test that manager creation fails without model."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_create_models.return_value = ModelDict(
            model_manager=None,  # No model available
            model_researcher=None,
            model_analyst=None,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Manager model not available"):
            factory.create_manager_agent()


class TestResearcherAgentCreation:
    """Test researcher agent creation."""

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_researcher_agent_success(self, mock_create_models):
        """Test successful researcher agent creation."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_model = Mock()
        mock_create_models.return_value = ModelDict(
            model_manager=mock_model,
            model_researcher=mock_model,
            model_analyst=None,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act
        agent = factory.create_researcher_agent()

        # Assert
        assert agent is not None

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_researcher_agent_without_model_raises_error(self, mock_create_models):
        """Test that researcher creation fails without model."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_create_models.return_value = ModelDict(
            model_manager=Mock(),
            model_researcher=None,  # No researcher model
            model_analyst=None,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Researcher model not available"):
            factory.create_researcher_agent()


class TestAnalystAgentCreation:
    """Test analyst agent creation."""

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_analyst_agent_success(self, mock_create_models):
        """Test successful analyst agent creation."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_model = Mock()
        mock_create_models.return_value = ModelDict(
            model_manager=mock_model,
            model_researcher=None,
            model_analyst=mock_model,
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act
        agent = factory.create_analyst_agent()

        # Assert
        assert agent is not None

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_analyst_agent_without_model_raises_error(self, mock_create_models):
        """Test that analyst creation fails without model."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_create_models.return_value = ModelDict(
            model_manager=Mock(),
            model_researcher=None,
            model_analyst=None,  # No analyst model
            model_synthesiser=None,
        )

        factory = AgentFactory(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Analyst model not available"):
            factory.create_analyst_agent()


class TestSynthesiserAgentCreation:
    """Test synthesiser agent creation."""

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_synthesiser_agent_success(self, mock_create_models):
        """Test successful synthesiser agent creation."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_model = Mock()
        mock_create_models.return_value = ModelDict(
            model_manager=mock_model,
            model_researcher=None,
            model_analyst=None,
            model_synthesiser=mock_model,
        )

        factory = AgentFactory(config)

        # Act
        agent = factory.create_synthesiser_agent()

        # Assert
        assert agent is not None

    @patch("app.agents.agent_factories.create_agent_models")
    def test_create_synthesiser_agent_without_model_raises_error(self, mock_create_models):
        """Test that synthesiser creation fails without model."""
        # Arrange
        config = EndpointConfig(
            provider="openai",
            provider_config=ProviderConfig(
                model_name="gpt-4o-mini",
                base_url="https://api.openai.com/v1",
            ),
            api_key="test-key",
        )

        mock_create_models.return_value = ModelDict(
            model_manager=Mock(),
            model_researcher=None,
            model_analyst=None,
            model_synthesiser=None,  # No synthesiser model
        )

        factory = AgentFactory(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Synthesiser model not available"):
            factory.create_synthesiser_agent()
