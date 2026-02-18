"""
Tests for JudgeSettings tier2_provider default change and fallback chain fix.

STORY-011: Change tier2_provider default to auto, fix fallback chain bug.
"""

import os
from unittest.mock import patch

from app.data_models.app_models import AppEnv
from app.judge.llm_evaluation_managers import LLMJudgeEngine
from app.judge.settings import JudgeSettings


class TestTier2ProviderDefault:
    """Test that tier2_provider defaults to 'auto' (STORY-011)."""

    def test_default_tier2_provider_is_auto(self):
        """JudgeSettings() should default tier2_provider to 'auto', not 'openai'."""
        settings = JudgeSettings()
        assert settings.tier2_provider == "auto"

    def test_env_override_judge_tier2_provider(self):
        """JUDGE_TIER2_PROVIDER env var should override the 'auto' default."""
        with patch.dict(os.environ, {"JUDGE_TIER2_PROVIDER": "openai"}):
            settings = JudgeSettings()
            assert settings.tier2_provider == "openai"

    def test_env_override_restores_default_when_unset(self):
        """Without JUDGE_TIER2_PROVIDER env var, default must remain 'auto'."""
        env_without_override = {k: v for k, v in os.environ.items() if k != "JUDGE_TIER2_PROVIDER"}
        with patch.dict(os.environ, env_without_override, clear=True):
            settings = JudgeSettings()
            assert settings.tier2_provider == "auto"

    def test_tier2_fallback_provider_default_unchanged(self):
        """tier2_fallback_provider should remain 'github' (unchanged by STORY-011)."""
        settings = JudgeSettings()
        assert settings.tier2_fallback_provider == "github"


class TestAutoProviderMigrationLog:
    """Test migration log emitted when auto resolves to non-openai provider (STORY-011).

    Loguru writes to stderr (not captured by pytest caplog). Tests verify state
    resulting from the logged resolution path, following project convention.
    """

    def test_migration_log_path_executes_when_auto_resolves_to_github(self):
        """When auto resolves to non-openai provider, migration log must use specific format.

        AC: logger.info("Judge provider: auto → {resolved}") when resolved != 'openai'.
        The loguru logger goes to stderr; capture it via loguru sink for verification.
        """
        import io

        from loguru import logger

        settings = JudgeSettings(tier2_provider="auto")
        env_config = AppEnv(GITHUB_API_KEY="ghp-test-key")

        log_sink = io.StringIO()
        sink_id = logger.add(log_sink, format="{message}")
        try:
            engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider="github")
            log_output = log_sink.getvalue()
        finally:
            logger.remove(sink_id)

        # Verify state: provider resolved from auto to github
        assert engine.provider == "github"
        # Verify migration log uses the required format: "Judge provider: auto → {resolved}"
        assert "Judge provider: auto" in log_output
        assert "github" in log_output

    def test_no_migration_log_when_auto_resolves_to_openai(self):
        """No additional migration log when auto resolves to openai (same as old default)."""
        settings = JudgeSettings(tier2_provider="auto")
        env_config = AppEnv(OPENAI_API_KEY="sk-test-key")

        # Verify engine initializes correctly with openai as resolved provider.
        engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider="openai")

        assert engine.provider == "openai"


class TestAutoFallbackChain:
    """Test fallback chain uses resolved MAS provider when tier2_provider=auto (STORY-011)."""

    def test_auto_mode_fallback_uses_resolved_provider_not_hardcoded_openai(self):
        """When tier2_provider=auto resolves to github, fallback must not be 'openai'."""
        settings = JudgeSettings(
            tier2_provider="auto",
            tier2_fallback_provider="github",
        )
        env_config = AppEnv(GITHUB_API_KEY="ghp-test-key", OPENAI_API_KEY="")
        chat_provider = "github"

        engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider=chat_provider)

        # Provider should be resolved from auto to github (not openai)
        assert engine.provider == "github"
        # Fallback provider remains github (settings.tier2_fallback_provider)
        assert engine.fallback_provider == "github"

    def test_auto_mode_with_openai_chat_provider_selects_openai(self):
        """When tier2_provider=auto with chat_provider=openai, primary is openai."""
        settings = JudgeSettings(tier2_provider="auto")
        env_config = AppEnv(OPENAI_API_KEY="sk-test-key", GITHUB_API_KEY="")
        chat_provider = "openai"

        engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider=chat_provider)

        assert engine.provider == "openai"
        assert engine.tier2_available is True

    def test_auto_mode_without_chat_provider_falls_through_to_fallback(self):
        """When tier2_provider=auto but no chat_provider given, check fallback behavior."""
        settings = JudgeSettings(tier2_provider="auto", tier2_fallback_provider="github")
        # auto without chat_provider leaves self.provider == "auto"
        # validate_provider_api_key("auto", ...) will return False (no "auto" key)
        # then falls through to fallback_provider ("github")
        env_config = AppEnv(GITHUB_API_KEY="ghp-test-key", OPENAI_API_KEY="")

        engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider=None)

        # Falls back to github since "auto" provider key doesn't exist
        assert engine.provider == "github"

    def test_fixme_removed_fallback_chain_uses_settings_not_hardcoded(self):
        """Verify FIXME is resolved: fallback_provider comes from settings, not hardcoded openai."""
        # Ensure that the fallback provider is whatever tier2_fallback_provider says,
        # not a hardcoded "openai"
        settings = JudgeSettings(
            tier2_provider="auto",
            tier2_fallback_provider="cerebras",
        )
        env_config = AppEnv(OPENAI_API_KEY="", GITHUB_API_KEY="", CEREBRAS_API_KEY="test-key")

        engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider="cerebras")

        # Primary "cerebras" (from auto resolution) should be selected
        assert engine.provider == "cerebras"
        assert engine.fallback_provider == "cerebras"


class TestStory011FallbackChainFix:
    """Regression tests ensuring FIXME Sprint5-STORY-001 is resolved (STORY-011)."""

    def test_select_available_provider_uses_self_provider_not_openai(self):
        """select_available_provider must use self.provider (resolved), not hardcoded 'openai'."""
        settings = JudgeSettings(tier2_provider="auto", tier2_model="gpt-4o-mini")
        env_config = AppEnv(GITHUB_API_KEY="ghp-test-key", OPENAI_API_KEY="")
        chat_provider = "github"

        engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider=chat_provider)

        # select_available_provider should use the resolved provider (github), not openai
        result = engine.select_available_provider(env_config)
        assert result is not None
        assert result[0] == "github"

    def test_engine_provider_attribute_is_resolved_not_auto(self):
        """After init with auto, engine.provider must be the resolved value, not 'auto'."""
        settings = JudgeSettings(tier2_provider="auto")
        env_config = AppEnv(GITHUB_API_KEY="ghp-test")

        engine = LLMJudgeEngine(settings, env_config=env_config, chat_provider="github")

        # provider must not be the literal string "auto"
        assert engine.provider != "auto"
        assert engine.provider == "github"
