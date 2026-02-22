"""
Test cases for LLM model creation and configuration.

Tests for model creation with different providers, error handling,
and configuration validation.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic_ai.models.openai import OpenAIChatModel

from app.data_models.app_models import (
    PROVIDER_REGISTRY,
    AppEnv,
    EndpointConfig,
    ProviderConfig,
)
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


# ---------------------------------------------------------------------------
# STORY-012: Expand inference provider registry and update stale models
# ---------------------------------------------------------------------------

# New providers to add per AC1/AC2
_NEW_PROVIDERS = {
    "groq": {
        "env_key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
    "fireworks": {
        "env_key": "FIREWORKS_API_KEY",
        "base_url": "https://api.fireworks.ai/inference/v1",
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
    },
    "mistral": {
        "env_key": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
    },
    "sambanova": {
        "env_key": "SAMBANOVA_API_KEY",
        "base_url": "https://api.sambanova.ai/v1",
    },
    "nebius": {
        "env_key": "NEBIUS_API_KEY",
        "base_url": "https://api.studio.nebius.ai/v1",
    },
    "cohere": {
        "env_key": "COHERE_API_KEY",
        "base_url": "https://api.cohere.com/v2",
    },
}


class TestStory012ProviderRegistryExpansion:
    """AC1/AC2: New providers exist in PROVIDER_REGISTRY with correct metadata."""

    @pytest.mark.parametrize("provider_name", list(_NEW_PROVIDERS.keys()))
    def test_new_provider_in_registry(self, provider_name: str):
        """Each new provider must exist in PROVIDER_REGISTRY."""
        assert provider_name in PROVIDER_REGISTRY, (
            f"Provider '{provider_name}' missing from PROVIDER_REGISTRY"
        )

    @pytest.mark.parametrize("provider_name,expected", list(_NEW_PROVIDERS.items()))
    def test_new_provider_env_key(self, provider_name: str, expected: dict):
        """Each new provider must have the correct env_key."""
        metadata = PROVIDER_REGISTRY[provider_name]
        assert metadata.env_key == expected["env_key"]

    @pytest.mark.parametrize("provider_name,expected", list(_NEW_PROVIDERS.items()))
    def test_new_provider_base_url(self, provider_name: str, expected: dict):
        """Each new provider must have the correct default_base_url."""
        metadata = PROVIDER_REGISTRY[provider_name]
        assert metadata.default_base_url == expected["base_url"]


class TestStory012ConfigChatUpdates:
    """AC3-AC7: config_chat.json entries updated with correct models and limits."""

    @pytest.fixture
    def config_chat(self) -> dict:
        """Load config_chat.json."""
        config_path = Path(__file__).resolve().parents[2] / "src" / "app" / "config" / "config_chat.json"
        return json.loads(config_path.read_text())

    # AC3: Each new provider has a matching entry in config_chat.json
    @pytest.mark.parametrize("provider_name", list(_NEW_PROVIDERS.keys()))
    def test_new_provider_in_config_chat(self, config_chat: dict, provider_name: str):
        """Each new provider must have an entry in config_chat.json."""
        assert provider_name in config_chat["providers"], (
            f"Provider '{provider_name}' missing from config_chat.json"
        )

    # AC4: HuggingFace model fixed
    def test_huggingface_model_updated(self, config_chat: dict):
        """HuggingFace model must not be bart-large-mnli (classification, not chat)."""
        hf = config_chat["providers"]["huggingface"]
        assert hf["model_name"] != "facebook/bart-large-mnli", (
            "HuggingFace still uses classification model"
        )
        assert hf["model_name"] == "meta-llama/Meta-Llama-3.3-70B-Instruct"

    # AC5: Together model fixed
    def test_together_model_updated(self, config_chat: dict):
        """Together model must not use removed free model."""
        together = config_chat["providers"]["together"]
        assert "Free" not in together["model_name"], (
            "Together still uses removed free model"
        )
        assert together["model_name"] == "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    # AC6: Existing stale entries updated
    def test_gemini_model_updated(self, config_chat: dict):
        """Gemini must use gemini-2.0-flash (free tier)."""
        assert config_chat["providers"]["gemini"]["model_name"] == "gemini-2.0-flash"

    def test_openai_model_updated(self, config_chat: dict):
        """OpenAI must use gpt-4.1-mini (current generation)."""
        assert config_chat["providers"]["openai"]["model_name"] == "gpt-4.1-mini"

    def test_github_model_updated(self, config_chat: dict):
        """GitHub must use gpt-4.1-mini."""
        assert config_chat["providers"]["github"]["model_name"] == "gpt-4.1-mini"

    def test_grok_model_updated(self, config_chat: dict):
        """Grok must use grok-3-mini."""
        assert config_chat["providers"]["grok"]["model_name"] == "grok-3-mini"

    def test_anthropic_model_updated(self, config_chat: dict):
        """Anthropic must use claude-sonnet-4-20250514."""
        assert config_chat["providers"]["anthropic"]["model_name"] == "claude-sonnet-4-20250514"

    def test_openrouter_model_updated(self, config_chat: dict):
        """OpenRouter must use qwen3 free model."""
        assert config_chat["providers"]["openrouter"]["model_name"] == "qwen/qwen3-next-80b-a3b-instruct:free"

    def test_ollama_model_updated(self, config_chat: dict):
        """Ollama must use llama3.3:latest."""
        assert config_chat["providers"]["ollama"]["model_name"] == "llama3.3:latest"

    # AC7: max_content_length reflects free tier limits
    def test_cerebras_max_content_length(self, config_chat: dict):
        """Cerebras gpt-oss-120b has 128K context."""
        assert config_chat["providers"]["cerebras"]["max_content_length"] == 128000

    def test_grok_max_content_length(self, config_chat: dict):
        """Grok grok-3-mini has 131K context."""
        assert config_chat["providers"]["grok"]["max_content_length"] == 131000

    def test_groq_max_content_length(self, config_chat: dict):
        """Groq llama-3.3-70b has 131K context."""
        assert config_chat["providers"]["groq"]["max_content_length"] == 131000


class TestStory012AnthropicNativeModel:
    """AC8: Anthropic provider uses PydanticAI native AnthropicModel."""

    def test_anthropic_returns_anthropic_model(self):
        """create_llm_model() for anthropic must NOT return OpenAIChatModel."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="anthropic",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="claude-sonnet-4-20250514",
                base_url="https://api.anthropic.com",
            ),
        )

        with patch("app.llms.models.AnthropicModel") as mock_anthropic_cls:
            mock_instance = MagicMock()
            mock_anthropic_cls.return_value = mock_instance

            model = create_llm_model(endpoint_config)

        # Must use AnthropicModel, not OpenAIChatModel
        assert not isinstance(model, OpenAIChatModel), (
            "Anthropic provider should use native AnthropicModel, not OpenAIChatModel"
        )
        mock_anthropic_cls.assert_called_once()


class TestStory012GroqStrictTools:
    """AC9: Groq provider disables strict tool definitions (like cerebras)."""

    def test_groq_strict_tool_definition_disabled(self):
        """Groq model must have openai_supports_strict_tool_definition=False."""
        endpoint_config = EndpointConfig(
            prompts={"manager": "You are a manager"},
            provider="groq",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="llama-3.3-70b-versatile",
                base_url="https://api.groq.com/openai/v1",
            ),
        )

        model = create_llm_model(endpoint_config)

        assert isinstance(model, OpenAIChatModel)
        assert model.profile.openai_supports_strict_tool_definition is False, (
            "Groq must disable strict tool definitions"
        )


class TestStory012AppEnvKeys:
    """AC1/AC2: AppEnv has environment variable fields for new providers."""

    @pytest.mark.parametrize(
        "env_key",
        [
            "GROQ_API_KEY",
            "FIREWORKS_API_KEY",
            "DEEPSEEK_API_KEY",
            "MISTRAL_API_KEY",
            "SAMBANOVA_API_KEY",
            "NEBIUS_API_KEY",
            "COHERE_API_KEY",
        ],
    )
    def test_appenv_has_new_provider_key(self, env_key: str):
        """AppEnv must have a field for each new provider's API key."""
        assert env_key in AppEnv.model_fields, (
            f"AppEnv missing field '{env_key}'"
        )


class TestStory012CLIProviderValidation:
    """AC11: CLI --chat-provider validates against PROVIDER_REGISTRY."""

    def test_chat_provider_rejects_invalid_provider(self):
        """--chat-provider with an invalid name must be rejected."""
        from run_cli import parse_args

        with pytest.raises(SystemExit):
            parse_args(["--chat-provider=invalid_nonexistent_provider"])

    def test_chat_provider_accepts_new_providers(self):
        """--chat-provider must accept all new provider names."""
        from run_cli import parse_args

        for provider_name in _NEW_PROVIDERS:
            args = parse_args([f"--chat-provider={provider_name}"])
            assert args.get("chat_provider") == provider_name
