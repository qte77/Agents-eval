"""
Tests for dynamic provider environment setup.

After STORY-004: setup_llm_environment() is a no-op.
API keys are passed directly to provider constructors in models.py.
These tests verify the registry metadata and that no keys leak to os.environ.
"""

from app.data_models.app_models import PROVIDER_REGISTRY, AppEnv

# MARK: --- Unit Tests: registry metadata ---


class TestProviderRegistry:
    """Test that PROVIDER_REGISTRY metadata is correct and consistent with AppEnv."""

    def test_all_registry_providers_have_valid_metadata(self):
        """Every PROVIDER_REGISTRY entry with env_key MUST be resolvable from AppEnv."""
        env_config = AppEnv()

        for name, meta in PROVIDER_REGISTRY.items():
            if meta.env_key is not None:
                assert hasattr(env_config, meta.env_key), (
                    f"Provider '{name}' has env_key='{meta.env_key}' but AppEnv lacks that field"
                )

    def test_ollama_has_no_env_key(self):
        """Ollama provider MUST have env_key=None (no API key needed)."""
        ollama_meta = PROVIDER_REGISTRY.get("ollama")
        assert ollama_meta is not None
        assert ollama_meta.env_key is None

    def test_openai_has_env_key(self):
        """OpenAI provider must have a valid env_key."""
        openai_meta = PROVIDER_REGISTRY.get("openai")
        assert openai_meta is not None
        assert openai_meta.env_key is not None

    def test_anthropic_has_env_key(self):
        """Anthropic provider must have a valid env_key."""
        anthropic_meta = PROVIDER_REGISTRY.get("anthropic")
        assert anthropic_meta is not None
        assert anthropic_meta.env_key is not None


# MARK: --- Unit Tests: setup_llm_environment is no-op ---


class TestSetupLlmEnvironmentIsNoOp:
    """After STORY-004: setup_llm_environment must NOT write to os.environ."""

    def test_setup_llm_environment_does_not_write_to_environ(self):
        """setup_llm_environment is a no-op and must not write to os.environ."""
        import os
        from unittest.mock import patch

        from app.llms.providers import setup_llm_environment

        with patch.dict(os.environ, {}, clear=True):
            setup_llm_environment({"openai": "sk-test-key", "cerebras": "csk-test-key"})

            # No keys must appear in os.environ after the call
            assert "OPENAI_API_KEY" not in os.environ
            assert "CEREBRAS_API_KEY" not in os.environ

    def test_setup_llm_environment_empty_key_no_write(self):
        """Empty keys must not write to os.environ (was the old behavior too, now still true)."""
        import os
        from unittest.mock import patch

        from app.llms.providers import setup_llm_environment

        with patch.dict(os.environ, {}, clear=True):
            setup_llm_environment({"cerebras": ""})

            assert "CEREBRAS_API_KEY" not in os.environ

    def test_setup_llm_environment_only_selected_provider_no_write(self):
        """No provider keys must be written to os.environ regardless of input."""
        import os
        from unittest.mock import patch

        from app.llms.providers import setup_llm_environment

        with patch.dict(os.environ, {}, clear=True):
            setup_llm_environment(
                {
                    "cerebras": "cerebras-key-123",
                    "github": "github-key-456",
                    "openai": "openai-key-789",
                }
            )

            assert "CEREBRAS_API_KEY" not in os.environ
            assert "GITHUB_API_KEY" not in os.environ
            assert "OPENAI_API_KEY" not in os.environ


# MARK: --- Integration Tests: setup_agent_env ---


class TestSetupAgentEnvProviderFiltering:
    """Test that setup_agent_env does not write API keys to os.environ (STORY-004)."""

    def test_setup_agent_env_does_not_write_api_key_to_environ(self):
        """setup_agent_env MUST NOT write any provider API key to os.environ."""
        import os
        from unittest.mock import MagicMock, patch

        from app.agents.agent_system import setup_agent_env
        from app.data_models.app_models import ChatConfig

        env_config = AppEnv(
            CEREBRAS_API_KEY="cerebras-key",
            GITHUB_API_KEY="github-key",
            OPENAI_API_KEY="openai-key",
        )

        mock_provider_config = MagicMock()
        mock_provider_config.usage_limits = 60000

        with (
            patch("app.agents.agent_system.get_provider_config", return_value=mock_provider_config),
            patch("app.agents.agent_system.get_api_key", return_value=(True, "cerebras-key")),
            patch("app.agents.agent_system.EndpointConfig"),
            patch.dict(os.environ, {}, clear=True),
        ):
            chat_config = MagicMock()
            chat_config.__class__ = ChatConfig

            setup_agent_env(
                provider="cerebras",
                query="test query",
                chat_config=chat_config,
                chat_env_config=env_config,
            )

            # No API keys must appear in os.environ
            assert "CEREBRAS_API_KEY" not in os.environ
            assert "GITHUB_API_KEY" not in os.environ
            assert "OPENAI_API_KEY" not in os.environ

    def test_setup_agent_env_does_not_import_setup_llm_environment(self):
        """agent_system must not import or call setup_llm_environment (AC3)."""
        import app.agents.agent_system as agent_system_module

        # setup_llm_environment must not be an attribute of agent_system
        assert not hasattr(agent_system_module, "setup_llm_environment"), (
            "setup_llm_environment must be removed from agent_system imports (AC3)"
        )
