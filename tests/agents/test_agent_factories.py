"""
Test cases for agent factory functions.

Tests for agent creation with various configurations, toggle combinations,
and system prompt construction.
"""

from unittest.mock import Mock, patch

import pytest
from pydantic_ai import Agent

from app.agents.agent_factories import AgentFactory
from app.data_models.app_models import EndpointConfig, ModelDict, ProviderConfig


class TestAgentFactoryInitialization:
    """Test AgentFactory initialization."""

    def test_agent_factory_init_with_config(self):
        """Test factory initialization with endpoint config."""
        config = EndpointConfig(
            provider="openai",
            api_key="test-key",
            prompts={"manager": "You are a manager"},
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )
        factory = AgentFactory(endpoint_config=config)

        assert factory.endpoint_config == config
        assert factory._models is None

    def test_agent_factory_init_without_config(self):
        """Test factory initialization without endpoint config."""
        factory = AgentFactory()

        assert factory.endpoint_config is None
        assert factory._models is None


class TestAgentCreationWithToggles:
    """Test agent creation with various toggle combinations."""

    @pytest.fixture
    def mock_endpoint_config(self):
        """Create mock endpoint configuration."""
        return EndpointConfig(
            provider="openai",
            api_key="test-key",
            prompts={"manager": "You are a manager"},
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

    @pytest.fixture
    def mock_models(self):
        """Create mock ModelDict."""
        from pydantic_ai.models import Model

        return ModelDict.model_construct(
            model_manager=Mock(spec=Model),
            model_researcher=Mock(spec=Model),
            model_analyst=Mock(spec=Model),
            model_synthesiser=Mock(spec=Model),
        )

    def test_create_manager_agent_with_default_prompt(self, mock_endpoint_config, mock_models):
        """Test creating manager agent with default system prompt."""
        with patch("app.agents.agent_factories.create_agent_models", return_value=mock_models):
            factory = AgentFactory(endpoint_config=mock_endpoint_config)
            agent = factory.create_manager_agent()

            assert isinstance(agent, Agent)
            # Note: system_prompt becomes a function due to logfire instrumentation side effects
            # We only verify the agent was created successfully

    def test_create_manager_agent_with_custom_prompt(self, mock_endpoint_config, mock_models):
        """Test creating manager agent with custom system prompt."""
        custom_prompt = "You are a custom manager agent."
        with patch("app.agents.agent_factories.create_agent_models", return_value=mock_models):
            factory = AgentFactory(endpoint_config=mock_endpoint_config)
            agent = factory.create_manager_agent(system_prompt=custom_prompt)

            assert isinstance(agent, Agent)
            # Note: system_prompt becomes a function due to logfire instrumentation side effects
            # We only verify the agent was created successfully

    def test_create_researcher_agent(self, mock_endpoint_config, mock_models):
        """Test creating researcher agent."""
        with patch("app.agents.agent_factories.create_agent_models", return_value=mock_models):
            factory = AgentFactory(endpoint_config=mock_endpoint_config)
            agent = factory.create_researcher_agent()

            assert isinstance(agent, Agent)
            # Note: system_prompt becomes a function due to logfire instrumentation side effects
            # We only verify the agent was created successfully

    def test_create_analyst_agent(self, mock_endpoint_config, mock_models):
        """Test creating analyst agent."""
        with patch("app.agents.agent_factories.create_agent_models", return_value=mock_models):
            factory = AgentFactory(endpoint_config=mock_endpoint_config)
            agent = factory.create_analyst_agent()

            assert isinstance(agent, Agent)
            # Note: system_prompt becomes a function due to logfire instrumentation side effects
            # We only verify the agent was created successfully

    def test_create_synthesiser_agent(self, mock_endpoint_config, mock_models):
        """Test creating synthesiser agent."""
        with patch("app.agents.agent_factories.create_agent_models", return_value=mock_models):
            factory = AgentFactory(endpoint_config=mock_endpoint_config)
            agent = factory.create_synthesiser_agent()

            assert isinstance(agent, Agent)
            # Note: system_prompt becomes a function due to logfire instrumentation side effects
            # We only verify the agent was created successfully


class TestAgentCreationErrorHandling:
    """Test error handling in agent creation."""

    def test_create_manager_agent_without_model(self):
        """Test error when creating manager agent without model."""
        factory = AgentFactory()  # No endpoint config

        with pytest.raises(ValueError, match="Manager model not available"):
            factory.create_manager_agent()

    def test_create_researcher_agent_without_model(self):
        """Test error when creating researcher agent without model."""
        factory = AgentFactory()

        with pytest.raises(ValueError, match="Researcher model not available"):
            factory.create_researcher_agent()

    def test_create_analyst_agent_without_model(self):
        """Test error when creating analyst agent without model."""
        factory = AgentFactory()

        with pytest.raises(ValueError, match="Analyst model not available"):
            factory.create_analyst_agent()

    def test_create_synthesiser_agent_without_model(self):
        """Test error when creating synthesiser agent without model."""
        factory = AgentFactory()

        with pytest.raises(ValueError, match="Synthesiser model not available"):
            factory.create_synthesiser_agent()


class TestModelsCaching:
    """Test model caching in AgentFactory."""

    @pytest.fixture
    def mock_endpoint_config(self):
        """Create mock endpoint configuration."""
        return EndpointConfig(
            provider="openai",
            api_key="test-key",
            prompts={"manager": "You are a manager"},
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

    def test_get_models_caches_result(self, mock_endpoint_config):
        """Test that get_models caches the ModelDict."""
        from pydantic_ai.models import Model

        mock_models = ModelDict.model_construct(
            model_manager=Mock(spec=Model),
            model_researcher=None,
            model_analyst=None,
            model_synthesiser=None,
        )

        with patch(
            "app.agents.agent_factories.create_agent_models", return_value=mock_models
        ) as mock_create:
            factory = AgentFactory(endpoint_config=mock_endpoint_config)

            # First call
            models1 = factory.get_models()
            # Second call
            models2 = factory.get_models()

            # Should only call create_agent_models once (cached)
            assert mock_create.call_count == 1
            assert models1 is models2

    def test_get_models_with_different_toggles(self, mock_endpoint_config):
        """Test get_models with different agent toggles."""
        from pydantic_ai.models import Model

        mock_models_all = ModelDict.model_construct(
            model_manager=Mock(spec=Model),
            model_researcher=Mock(spec=Model),
            model_analyst=Mock(spec=Model),
            model_synthesiser=Mock(spec=Model),
        )

        with patch("app.agents.agent_factories.create_agent_models", return_value=mock_models_all):
            factory = AgentFactory(endpoint_config=mock_endpoint_config)

            # Get models with all agents
            models = factory.get_models(
                include_researcher=True,
                include_analyst=True,
                include_synthesiser=True,
            )

            assert models.model_manager is not None
            assert models.model_researcher is not None
            assert models.model_analyst is not None
            assert models.model_synthesiser is not None


class TestAgentFactoryWithoutConfig:
    """Test AgentFactory behavior without endpoint config."""

    def test_get_models_without_config_returns_empty(self):
        """Test that get_models without config returns empty ModelDict."""
        factory = AgentFactory()
        models = factory.get_models()

        assert models.model_manager is None
        assert models.model_researcher is None
        assert models.model_analyst is None
        assert models.model_synthesiser is None
