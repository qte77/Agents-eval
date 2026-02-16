"""
Tests for dynamic provider environment setup (STORY-008).

Expected behavior:
- Only the selected provider's API key is set as env var
- Other provider keys are NOT set, even if configured in AppEnv
- Providers without env_key (e.g. ollama) are excluded
- New providers added to PROVIDER_REGISTRY are picked up automatically
- setup_agent_env passes only selected provider's key to setup_llm_environment
"""

from unittest.mock import patch

from app.data_models.app_models import PROVIDER_REGISTRY, AppEnv

# MARK: --- Unit Tests: setup_llm_environment ---


class TestProviderEnvSetup:
    """Test that setup_llm_environment uses PROVIDER_REGISTRY dynamically."""

    def test_selected_provider_key_set_in_env(self):
        """Selected provider's API key MUST be set as env var."""
        env_config = AppEnv(CEREBRAS_API_KEY="test-cerebras-key")

        with patch.dict("os.environ", {}, clear=True):
            import os

            from app.llms.providers import setup_llm_environment

            selected = PROVIDER_REGISTRY["cerebras"]
            api_keys = (
                {selected.name: getattr(env_config, selected.env_key, "")}
                if selected.env_key
                else {}
            )
            setup_llm_environment(api_keys)

            assert os.environ.get("CEREBRAS_API_KEY") == "test-cerebras-key"

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

    def test_empty_key_not_set_as_env_var(self):
        """Empty API key MUST NOT be set as environment variable."""
        with patch.dict("os.environ", {}, clear=True):
            import os

            from app.llms.providers import setup_llm_environment

            setup_llm_environment({"cerebras": ""})

            assert "CEREBRAS_API_KEY" not in os.environ

    def test_only_selected_provider_key_set(self):
        """Only the selected provider's key MUST be set, others MUST NOT."""
        with patch.dict("os.environ", {}, clear=True):
            import os

            from app.llms.providers import setup_llm_environment

            env_config = AppEnv(
                CEREBRAS_API_KEY="cerebras-key-123",
                GITHUB_API_KEY="github-key-456",
                OPENAI_API_KEY="openai-key-789",
            )

            # Simulate selecting cerebras as provider
            selected = PROVIDER_REGISTRY["cerebras"]
            api_keys = (
                {selected.name: getattr(env_config, selected.env_key, "")}
                if selected.env_key
                else {}
            )
            setup_llm_environment(api_keys)

            assert os.environ.get("CEREBRAS_API_KEY") == "cerebras-key-123"
            assert "GITHUB_API_KEY" not in os.environ
            assert "OPENAI_API_KEY" not in os.environ


# MARK: --- Integration Tests: setup_agent_env ---


class TestSetupAgentEnvProviderFiltering:
    """Test that setup_agent_env passes only the selected provider's key."""

    def test_setup_agent_env_only_passes_selected_provider_key(self):
        """setup_agent_env MUST pass only the selected provider's API key."""
        from unittest.mock import MagicMock

        env_config = AppEnv(
            CEREBRAS_API_KEY="cerebras-key",
            GITHUB_API_KEY="github-key",
            OPENAI_API_KEY="openai-key",
        )

        mock_provider_config = MagicMock()
        mock_provider_config.usage_limits = 60000

        with (
            patch("app.agents.agent_system.setup_llm_environment") as mock_setup_llm,
            patch(
                "app.agents.agent_system.get_provider_config",
                return_value=mock_provider_config,
            ),
            patch("app.agents.agent_system.get_api_key", return_value=(True, "cerebras-key")),
            patch("app.agents.agent_system.EndpointConfig"),
        ):
            from app.agents.agent_system import setup_agent_env
            from app.data_models.app_models import ChatConfig

            # Reason: setup_agent_env checks isinstance(chat_config, ChatConfig)
            chat_config = MagicMock()
            chat_config.__class__ = ChatConfig

            setup_agent_env(
                provider="cerebras",
                query="test query",
                chat_config=chat_config,
                chat_env_config=env_config,
            )

            mock_setup_llm.assert_called_once()
            api_keys = mock_setup_llm.call_args[0][0]
            assert "cerebras" in api_keys
            assert api_keys["cerebras"] == "cerebras-key"
            assert "github" not in api_keys, f"github key should not be passed, got: {api_keys}"
            assert "openai" not in api_keys, f"openai key should not be passed, got: {api_keys}"
