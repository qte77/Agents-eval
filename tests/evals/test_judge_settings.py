"""
Tests for JudgeSettings pydantic-settings configuration.

Validates environment variable overrides and helper methods.
"""

import os
from unittest.mock import patch

from app.judge.settings import JudgeSettings


class TestJudgeSettingsEnvOverrides:
    """Test environment variable overrides with JUDGE_ prefix."""

    def test_env_override_tiers_enabled(self):
        """JUDGE_TIERS_ENABLED should override default."""
        with patch.dict(os.environ, {"JUDGE_TIERS_ENABLED": "[1, 2]"}):
            settings = JudgeSettings()
            assert settings.tiers_enabled == [1, 2]

    def test_env_override_tier1_max_seconds(self):
        """JUDGE_TIER1_MAX_SECONDS should override default."""
        with patch.dict(os.environ, {"JUDGE_TIER1_MAX_SECONDS": "2.5"}):
            settings = JudgeSettings()
            assert settings.tier1_max_seconds == 2.5

    def test_env_override_tier2_model(self):
        """JUDGE_TIER2_MODEL should override default."""
        with patch.dict(os.environ, {"JUDGE_TIER2_MODEL": "gpt-4o"}):
            settings = JudgeSettings()
            assert settings.tier2_model == "gpt-4o"

    def test_env_override_fallback_strategy(self):
        """JUDGE_FALLBACK_STRATEGY should override default."""
        with patch.dict(os.environ, {"JUDGE_FALLBACK_STRATEGY": "tier2_only"}):
            settings = JudgeSettings()
            assert settings.fallback_strategy == "tier2_only"


class TestJudgeSettingsHelperMethods:
    """Test convenience helper methods (get_enabled_tiers, is_tier_enabled, get_performance_targets)."""

    def test_get_enabled_tiers_set(self):
        """Should return tiers as a set for backward compatibility."""
        settings = JudgeSettings(tiers_enabled=[1, 3])
        assert settings.get_enabled_tiers() == {1, 3}

    def test_is_tier_enabled(self):
        """Should check if specific tier is enabled."""
        settings = JudgeSettings(tiers_enabled=[1, 2])
        assert settings.is_tier_enabled(1) is True
        assert settings.is_tier_enabled(2) is True
        assert settings.is_tier_enabled(3) is False

    def test_get_performance_targets(self):
        """Should return performance targets as dict."""
        settings = JudgeSettings()
        targets = settings.get_performance_targets()
        assert targets["tier1_max_seconds"] == 1.0
        assert targets["tier2_max_seconds"] == 10.0
        assert targets["tier3_max_seconds"] == 15.0
        assert targets["total_max_seconds"] == 25.0
