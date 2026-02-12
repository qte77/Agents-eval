"""
Tests for JudgeSettings pydantic-settings configuration.

Validates settings initialization, defaults, environment variable
overrides, and validation rules following TDD methodology.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.evals.settings import JudgeSettings


class TestJudgeSettingsDefaults:
    """Test default values match config_eval.json."""

    def test_tiers_enabled_defaults(self):
        """Tiers enabled should default to [1, 2, 3]."""
        settings = JudgeSettings()
        assert settings.tiers_enabled == [1, 2, 3]

    def test_performance_targets_defaults(self):
        """Performance targets should have correct defaults."""
        settings = JudgeSettings()
        assert settings.tier1_max_seconds == 1.0
        assert settings.tier2_max_seconds == 10.0
        assert settings.tier3_max_seconds == 15.0
        assert settings.total_max_seconds == 25.0

    def test_tier1_config_defaults(self):
        """Tier 1 traditional metrics config defaults."""
        settings = JudgeSettings()
        assert settings.tier1_similarity_metrics == ["cosine", "jaccard", "semantic"]
        assert settings.tier1_confidence_threshold == 0.8
        assert settings.tier1_bertscore_model == "distilbert-base-uncased"
        assert settings.tier1_tfidf_max_features == 5000

    def test_tier2_config_defaults(self):
        """Tier 2 LLM judge config defaults."""
        settings = JudgeSettings()
        assert settings.tier2_model == "gpt-4o-mini"
        assert settings.tier2_max_retries == 2
        assert settings.tier2_timeout_seconds == 30.0
        assert settings.tier2_cost_budget_usd == 0.05
        assert settings.tier2_paper_excerpt_length == 2000

    def test_tier3_config_defaults(self):
        """Tier 3 graph analysis config defaults."""
        settings = JudgeSettings()
        assert settings.tier3_min_nodes == 2
        assert settings.tier3_centrality_measures == ["betweenness", "closeness", "degree"]
        assert settings.tier3_max_nodes == 1000
        assert settings.tier3_max_edges == 5000
        assert settings.tier3_operation_timeout == 10.0

    def test_composite_scoring_defaults(self):
        """Composite scoring config defaults."""
        settings = JudgeSettings()
        assert settings.fallback_strategy == "tier1_only"

    def test_observability_defaults(self):
        """Observability config defaults."""
        settings = JudgeSettings()
        assert settings.trace_collection is True
        assert settings.opik_enabled is True
        assert settings.performance_logging is True


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


class TestJudgeSettingsValidation:
    """Test validation rules and bounded values."""

    def test_timeout_positive_validation(self):
        """Timeout fields must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            JudgeSettings(tier1_max_seconds=-1.0)
        assert "greater than 0" in str(exc_info.value)

    def test_timeout_max_bound_validation(self):
        """Timeout fields must be <= 300 seconds."""
        with pytest.raises(ValidationError) as exc_info:
            JudgeSettings(tier2_max_seconds=301.0)
        assert "less than or equal to 300" in str(exc_info.value)

    def test_tier3_max_nodes_positive(self):
        """Tier 3 max_nodes must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            JudgeSettings(tier3_max_nodes=0)
        assert "greater than 0" in str(exc_info.value)

    def test_tier3_max_edges_positive(self):
        """Tier 3 max_edges must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            JudgeSettings(tier3_max_edges=-100)
        assert "greater than 0" in str(exc_info.value)


class TestJudgeSettingsCompatibility:
    """Test backward compatibility helpers."""

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

    def test_get_tier1_config(self):
        """Should return tier1 config dict for engines."""
        settings = JudgeSettings()
        config = settings.get_tier1_config()
        assert config["similarity_metrics"] == ["cosine", "jaccard", "semantic"]
        assert config["confidence_threshold"] == 0.8

    def test_get_tier2_config(self):
        """Should return tier2 config dict for engines."""
        settings = JudgeSettings()
        config = settings.get_tier2_config()
        assert config["model"] == "gpt-4o-mini"
        assert config["max_retries"] == 2
        assert config["timeout_seconds"] == 30.0

    def test_get_tier3_config(self):
        """Should return tier3 config dict for engines."""
        settings = JudgeSettings()
        config = settings.get_tier3_config()
        assert config["min_nodes_for_analysis"] == 2
        assert config["centrality_measures"] == ["betweenness", "closeness", "degree"]
