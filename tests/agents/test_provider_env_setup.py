"""
Tests for dynamic provider environment setup (STORY-008).

Expected behavior:
- All PROVIDER_REGISTRY providers with env_key are included in env setup
- Providers without env_key (e.g. ollama) are excluded
- New providers added to PROVIDER_REGISTRY are picked up automatically
- No hardcoded provider list in setup_agent_env
"""

from unittest.mock import patch

from app.data_models.app_models import PROVIDER_REGISTRY, AppEnv


class TestProviderEnvSetup:
    """Test that setup_llm_environment uses PROVIDER_REGISTRY dynamically."""

    def test_cerebras_key_included_in_env_setup(self):
        """Cerebras API key MUST be set as env var when configured."""
        env_config = AppEnv(CEREBRAS_API_KEY="test-cerebras-key")

        with patch.dict("os.environ", {}, clear=True):
            import os

            from app.llms.providers import setup_llm_environment

            api_keys = {
                meta.name: getattr(env_config, meta.env_key, "")
                for meta in PROVIDER_REGISTRY.values()
                if meta.env_key is not None
            }
            setup_llm_environment(api_keys)

            assert os.environ.get("CEREBRAS_API_KEY") == "test-cerebras-key"

    def test_all_registry_providers_with_keys_included(self):
        """Every PROVIDER_REGISTRY entry with env_key MUST appear in api_keys dict."""
        env_config = AppEnv()

        api_keys = {
            meta.name: getattr(env_config, meta.env_key, "")
            for meta in PROVIDER_REGISTRY.values()
            if meta.env_key is not None
        }

        for name, meta in PROVIDER_REGISTRY.items():
            if meta.env_key is not None:
                assert name in api_keys, (
                    f"Provider '{name}' has env_key='{meta.env_key}' but is missing from api_keys"
                )

    def test_ollama_excluded_from_env_setup(self):
        """Providers with env_key=None (e.g. ollama) MUST be excluded."""
        api_keys = {
            meta.name: getattr(AppEnv(), meta.env_key, "")
            for meta in PROVIDER_REGISTRY.values()
            if meta.env_key is not None
        }

        assert "ollama" not in api_keys

    def test_empty_keys_not_set_as_env_vars(self):
        """Empty API keys MUST NOT be set as environment variables."""
        # Reason: AppEnv (BaseSettings) reads real env vars at construction time,
        # so it must be created inside the cleared env context
        with patch.dict("os.environ", {}, clear=True):
            import os

            from app.llms.providers import setup_llm_environment

            env_config = AppEnv()  # All keys default to "" with cleared env
            api_keys = {
                meta.name: getattr(env_config, meta.env_key, "")
                for meta in PROVIDER_REGISTRY.values()
                if meta.env_key is not None
            }
            setup_llm_environment(api_keys)

            # No provider env vars should be set since all keys are empty
            provider_env_keys = {
                meta.env_key for meta in PROVIDER_REGISTRY.values() if meta.env_key is not None
            }
            for env_key in provider_env_keys:
                assert env_key not in os.environ, (
                    f"Empty key '{env_key}' should not be set as env var"
                )

    def test_only_configured_keys_set_as_env_vars(self):
        """Only providers with non-empty keys MUST be set as env vars."""
        # Reason: AppEnv (BaseSettings) reads real env vars at construction time,
        # so it must be created inside the cleared env context
        with patch.dict("os.environ", {}, clear=True):
            import os

            from app.llms.providers import setup_llm_environment

            env_config = AppEnv(
                CEREBRAS_API_KEY="cerebras-key-123",
                OPENAI_API_KEY="openai-key-456",
            )
            api_keys = {
                meta.name: getattr(env_config, meta.env_key, "")
                for meta in PROVIDER_REGISTRY.values()
                if meta.env_key is not None
            }
            setup_llm_environment(api_keys)

            assert os.environ.get("CEREBRAS_API_KEY") == "cerebras-key-123"
            assert os.environ.get("OPENAI_API_KEY") == "openai-key-456"
            assert "GITHUB_API_KEY" not in os.environ
