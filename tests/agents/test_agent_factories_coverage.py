"""
Additional test coverage for agent_factories.py low-coverage functions.

Tests target critical untested functions identified in Sprint 5 MAESTRO review:
- AgentFactory model caching
- create_evaluation_agent with different assessment types
- agent creation without models
"""

from unittest.mock import Mock, patch

import pytest

from app.data_models.app_models import EndpointConfig, ModelDict, ProviderConfig


class TestAgentFactoryModelCaching:
    """Test AgentFactory model caching behavior."""

    def test_get_models_without_config_returns_empty_models(self):
        """Test get_models returns empty ModelDict when no endpoint_config provided."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        factory = AgentFactory(endpoint_config=None)

        # Act
        models = factory.get_models()

        # Assert - returns ModelDict with all None values
        assert models.model_manager is None
        assert models.model_researcher is None
        assert models.model_analyst is None
        assert models.model_synthesiser is None

    def test_get_models_creates_models_with_config(self):
        """Test get_models creates models when config provided."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        config = EndpointConfig(
            provider="openai",
            prompts={"manager": "Test prompt"},
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )
        factory = AgentFactory(endpoint_config=config)

        with patch("app.agents.agent_factories.create_agent_models") as mock_create:
            mock_model = Mock()
            # Use model_construct to bypass validation
            mock_models = ModelDict.model_construct(
                model_manager=mock_model,
                model_researcher=None,
                model_analyst=None,
                model_synthesiser=None,
            )
            mock_create.return_value = mock_models

            # Act
            models = factory.get_models()

            # Assert
            assert models.model_manager is not None
            mock_create.assert_called_once()

    def test_get_models_caches_result(self):
        """Test get_models caches the result and doesn't recreate."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        config = EndpointConfig(
            provider="openai",
            prompts={"manager": "Test prompt"},
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )
        factory = AgentFactory(endpoint_config=config)

        with patch("app.agents.agent_factories.create_agent_models") as mock_create:
            mock_model = Mock()
            # Use model_construct to bypass validation
            mock_models = ModelDict.model_construct(
                model_manager=mock_model,
                model_researcher=None,
                model_analyst=None,
                model_synthesiser=None,
            )
            mock_create.return_value = mock_models

            # Act
            models1 = factory.get_models()
            models2 = factory.get_models()

            # Assert
            assert models1 is models2  # Same instance
            assert mock_create.call_count == 1  # Called only once

    def test_get_models_with_researcher_toggle(self):
        """Test get_models respects include_researcher flag."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        config = EndpointConfig(
            provider="openai",
            prompts={"manager": "Test", "researcher": "Test"},
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )
        factory = AgentFactory(endpoint_config=config)

        with patch("app.agents.agent_factories.create_agent_models") as mock_create:
            mock_model = Mock()
            # Use model_construct to bypass validation
            mock_models = ModelDict.model_construct(
                model_manager=mock_model,
                model_researcher=mock_model,
                model_analyst=None,
                model_synthesiser=None,
            )
            mock_create.return_value = mock_models

            # Act
            factory.get_models(include_researcher=True)

            # Assert
            mock_create.assert_called_once_with(
                config,
                include_researcher=True,
                include_analyst=False,
                include_synthesiser=False,
            )


class TestAgentFactoryCreationMethods:
    """Test AgentFactory agent creation methods."""

    def test_create_manager_agent_raises_without_model(self):
        """Test create_manager_agent raises error when model not available."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        factory = AgentFactory(endpoint_config=None)

        # Act & Assert
        # Will raise ValidationError from ModelDict, not ValueError from create_manager_agent
        from pydantic_core import ValidationError

        with pytest.raises((ValidationError, ValueError)):
            factory.create_manager_agent()

    def test_create_researcher_agent_raises_without_model(self):
        """Test create_researcher_agent raises error when model not available."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        factory = AgentFactory(endpoint_config=None)

        # Act & Assert
        from pydantic_core import ValidationError

        with pytest.raises((ValidationError, ValueError)):
            factory.create_researcher_agent()

    def test_create_analyst_agent_raises_without_model(self):
        """Test create_analyst_agent raises error when model not available."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        factory = AgentFactory(endpoint_config=None)

        # Act & Assert
        from pydantic_core import ValidationError

        with pytest.raises((ValidationError, ValueError)):
            factory.create_analyst_agent()

    def test_create_synthesiser_agent_raises_without_model(self):
        """Test create_synthesiser_agent raises error when model not available."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        factory = AgentFactory(endpoint_config=None)

        # Act & Assert
        from pydantic_core import ValidationError

        with pytest.raises((ValidationError, ValueError)):
            factory.create_synthesiser_agent()

    def test_create_manager_agent_with_custom_prompt(self):
        """Test create_manager_agent uses custom system prompt."""
        from app.agents.agent_factories import AgentFactory

        # Arrange
        config = EndpointConfig(
            provider="openai",
            prompts={"manager": "Default prompt"},
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )
        factory = AgentFactory(endpoint_config=config)

        with patch("app.agents.agent_factories.create_agent_models") as mock_create:
            mock_model = Mock()
            # Use model_construct to bypass validation
            mock_models = ModelDict.model_construct(
                model_manager=mock_model,
                model_researcher=None,
                model_analyst=None,
                model_synthesiser=None,
            )
            mock_create.return_value = mock_models

            with patch("app.agents.agent_factories.Agent") as mock_agent_class:
                # Act
                factory.create_manager_agent(system_prompt="Custom prompt")

                # Assert
                mock_agent_class.assert_called_once()
                call_args = mock_agent_class.call_args
                assert call_args[1]["system_prompt"] == "Custom prompt"


class TestCreateEvaluationAgent:
    """Test create_evaluation_agent function."""

    def test_create_evaluation_agent_technical_accuracy(self):
        """Test creating evaluation agent for technical_accuracy assessment."""
        from app.agents.agent_factories import create_evaluation_agent

        # Arrange
        with patch("app.agents.agent_factories.create_simple_model") as mock_create_model:
            mock_model = Mock()
            mock_create_model.return_value = mock_model

            with patch("app.agents.agent_factories.Agent") as mock_agent_class:
                # Act
                create_evaluation_agent(
                    provider="openai",
                    model_name="gpt-4",
                    assessment_type="technical_accuracy",
                    api_key="test-key",
                )

                # Assert
                mock_create_model.assert_called_once_with("openai", "gpt-4", "test-key")
                mock_agent_class.assert_called_once()
                call_args = mock_agent_class.call_args
                assert "technical accuracy" in call_args[1]["system_prompt"].lower()

    def test_create_evaluation_agent_constructiveness(self):
        """Test creating evaluation agent for constructiveness assessment."""
        from app.agents.agent_factories import create_evaluation_agent

        # Arrange
        with patch("app.agents.agent_factories.create_simple_model") as mock_create_model:
            mock_model = Mock()
            mock_create_model.return_value = mock_model

            with patch("app.agents.agent_factories.Agent") as mock_agent_class:
                # Act
                create_evaluation_agent(
                    provider="openai",
                    model_name="gpt-4",
                    assessment_type="constructiveness",
                    api_key="test-key",
                )

                # Assert
                call_args = mock_agent_class.call_args
                assert "constructiveness" in call_args[1]["system_prompt"].lower()

    def test_create_evaluation_agent_planning_rationality(self):
        """Test creating evaluation agent for planning_rationality assessment."""
        from app.agents.agent_factories import create_evaluation_agent

        # Arrange
        with patch("app.agents.agent_factories.create_simple_model") as mock_create_model:
            mock_model = Mock()
            mock_create_model.return_value = mock_model

            with patch("app.agents.agent_factories.Agent") as mock_agent_class:
                # Act
                create_evaluation_agent(
                    provider="openai",
                    model_name="gpt-4",
                    assessment_type="planning_rationality",
                    api_key="test-key",
                )

                # Assert
                call_args = mock_agent_class.call_args
                assert "planning" in call_args[1]["system_prompt"].lower()

    def test_create_evaluation_agent_with_custom_prompt(self):
        """Test creating evaluation agent with custom system prompt."""
        from app.agents.agent_factories import create_evaluation_agent

        # Arrange
        custom_prompt = "Custom evaluation prompt"

        with (
            patch("app.agents.agent_factories.create_simple_model") as mock_create_model,
            patch("app.agents.agent_factories.Agent") as mock_agent_class,
        ):
            mock_model = Mock()
            mock_create_model.return_value = mock_model

            # Act
            create_evaluation_agent(
                provider="openai",
                model_name="gpt-4",
                assessment_type="technical_accuracy",
                api_key="test-key",
                system_prompt=custom_prompt,
            )

            # Assert
            call_args = mock_agent_class.call_args
            assert call_args[1]["system_prompt"] == custom_prompt

    def test_create_evaluation_agent_with_prompts_config(self):
        """Test creating evaluation agent using prompts from config."""
        from app.agents.agent_factories import create_evaluation_agent

        # Arrange
        prompts = {
            "system_prompt_evaluator_technical_accuracy": "Config prompt for technical accuracy"
        }

        with (
            patch("app.agents.agent_factories.create_simple_model") as mock_create_model,
            patch("app.agents.agent_factories.Agent") as mock_agent_class,
        ):
            mock_model = Mock()
            mock_create_model.return_value = mock_model

            # Act
            create_evaluation_agent(
                provider="openai",
                model_name="gpt-4",
                assessment_type="technical_accuracy",
                api_key="test-key",
                prompts=prompts,
            )

            # Assert
            call_args = mock_agent_class.call_args
            assert call_args[1]["system_prompt"] == "Config prompt for technical accuracy"
