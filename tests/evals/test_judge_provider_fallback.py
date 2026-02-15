"""
Tests for Tier 2 judge provider fallback and resilience (STORY-002).

Tests API key validation, provider fallback chain, and graceful degradation
when Tier 2 LLM-as-Judge is unavailable.
"""

from unittest.mock import Mock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.data_models.app_models import AppEnv
from app.evals.composite_scorer import CompositeScorer, EvaluationResults
from app.evals.llm_evaluation_managers import LLMJudgeEngine
from app.evals.settings import JudgeSettings


class TestProviderAPIKeyValidation:
    """Test API key availability checks for judge providers."""

    def test_validate_primary_provider_api_key_available(self):
        """Should return True when primary provider API key is available."""
        settings = JudgeSettings(tier2_provider="openai", tier2_model="gpt-4o-mini")
        env_config = AppEnv(OPENAI_API_KEY="test-key-123")

        engine = LLMJudgeEngine(settings)
        is_valid = engine.validate_provider_api_key(settings.tier2_provider, env_config)

        assert is_valid is True

    def test_validate_primary_provider_api_key_missing(self):
        """Should return False when primary provider API key is missing."""
        settings = JudgeSettings(tier2_provider="openai", tier2_model="gpt-4o-mini")
        env_config = AppEnv()  # No API keys

        engine = LLMJudgeEngine(settings)
        is_valid = engine.validate_provider_api_key(settings.tier2_provider, env_config)

        assert is_valid is False

    def test_validate_fallback_provider_api_key_available(self):
        """Should return True when fallback provider API key is available."""
        settings = JudgeSettings(
            tier2_provider="openai",
            tier2_fallback_provider="github",
            tier2_fallback_model="gpt-4o-mini",
        )
        env_config = AppEnv(GITHUB_API_KEY="github-test-key")

        engine = LLMJudgeEngine(settings)
        is_valid = engine.validate_provider_api_key(settings.tier2_fallback_provider, env_config)

        assert is_valid is True


class TestProviderFallbackChain:
    """Test provider fallback chain logic."""

    def test_should_use_primary_when_available(self):
        """Should use primary provider when API key is available."""
        settings = JudgeSettings(tier2_provider="openai")
        env_config = AppEnv(OPENAI_API_KEY="test-key")

        engine = LLMJudgeEngine(settings)
        selected_provider = engine.select_available_provider(env_config)

        assert selected_provider == ("openai", "gpt-4o-mini")

    def test_should_fallback_when_primary_unavailable(self):
        """Should fallback to tier2_fallback_provider when primary unavailable."""
        settings = JudgeSettings(
            tier2_provider="openai",
            tier2_fallback_provider="github",
            tier2_fallback_model="gpt-4o-mini",
        )
        env_config = AppEnv(GITHUB_API_KEY="github-key")  # No OPENAI_API_KEY

        engine = LLMJudgeEngine(settings)
        selected_provider = engine.select_available_provider(env_config)

        assert selected_provider == ("github", "gpt-4o-mini")

    def test_should_return_none_when_all_unavailable(self):
        """Should return None when both primary and fallback unavailable."""
        settings = JudgeSettings(
            tier2_provider="openai",
            tier2_fallback_provider="github",
        )
        env_config = AppEnv()  # No API keys

        engine = LLMJudgeEngine(settings)
        selected_provider = engine.select_available_provider(env_config)

        assert selected_provider is None


class TestFallbackScoreCapping:
    """Test fallback score capping at 0.5 (neutral) per acceptance criteria."""

    @given(
        interactions=st.integers(min_value=0, max_value=100),
        tool_calls=st.integers(min_value=0, max_value=100),
    )
    def test_fallback_planning_check_capped_at_neutral(self, interactions, tool_calls):
        """Fallback planning scores should never exceed 0.5 (neutral)."""
        settings = JudgeSettings()
        engine = LLMJudgeEngine(settings)

        execution_trace = {
            "agent_interactions": [{"type": "test"}] * interactions,
            "tool_calls": [{"name": "test"}] * tool_calls,
        }

        score = engine._fallback_planning_check(execution_trace)

        # Acceptance criteria: fallback scores capped at 0.5
        assert 0.0 <= score <= 0.5, f"Fallback score {score} exceeds neutral cap of 0.5"

    @given(review_text=st.text(min_size=0, max_size=1000))
    def test_fallback_constructiveness_check_capped_at_neutral(self, review_text):
        """Fallback constructiveness scores should never exceed 0.5 (neutral)."""
        settings = JudgeSettings()
        engine = LLMJudgeEngine(settings)

        score = engine._fallback_constructiveness_check(review_text)

        # Acceptance criteria: fallback scores capped at 0.5
        assert 0.0 <= score <= 0.5, f"Fallback score {score} exceeds neutral cap of 0.5"


class TestCompositeScorerMissingTier2:
    """Test CompositeScorer handling missing Tier 2 with weight redistribution."""

    def test_should_skip_tier2_when_none(self):
        """Should handle missing Tier 2 by redistributing weights to Tier 1 + Tier 3."""
        from app.data_models.evaluation_models import Tier1Result, Tier3Result

        # Create results with Tier 2 = None
        tier1 = Tier1Result(
            cosine_score=0.8,
            jaccard_score=0.75,
            semantic_score=0.85,
            execution_time=1.0,
            time_score=0.9,
            task_success=1.0,
            overall_score=0.85,
        )
        tier3 = Tier3Result(
            coordination_centrality=0.7,
            tool_selection_accuracy=0.8,
            path_convergence=0.75,
            task_distribution_balance=0.78,
            communication_overhead=0.7,
            overall_score=0.75,
            graph_complexity=50,
        )

        results = EvaluationResults(tier1=tier1, tier2=None, tier3=tier3)

        scorer = CompositeScorer()
        composite_result = scorer.evaluate_composite_with_optional_tier2(results)

        # Should complete without error
        assert composite_result.composite_score >= 0.0
        assert composite_result.composite_score <= 1.0
        # tier2_score should be None or 0.0 in result metadata
        assert composite_result.tier2_score is None or composite_result.tier2_score == 0.0

    def test_should_log_warning_when_tier2_skipped(self):
        """Should log warning when Tier 2 is skipped due to missing provider."""
        from app.data_models.evaluation_models import Tier1Result, Tier3Result

        tier1 = Tier1Result(
            cosine_score=0.8,
            jaccard_score=0.75,
            semantic_score=0.85,
            execution_time=1.0,
            time_score=0.9,
            task_success=1.0,
            overall_score=0.85,
        )
        tier3 = Tier3Result(
            coordination_centrality=0.7,
            tool_selection_accuracy=0.8,
            path_convergence=0.75,
            task_distribution_balance=0.78,
            communication_overhead=0.7,
            overall_score=0.75,
            graph_complexity=50,
        )

        results = EvaluationResults(tier1=tier1, tier2=None, tier3=tier3)

        scorer = CompositeScorer()

        with patch("app.evals.composite_scorer.logger") as mock_logger:
            scorer.evaluate_composite_with_optional_tier2(results)

            # Should warn about skipping Tier 2
            mock_logger.warning.assert_called()
            warning_call = str(mock_logger.warning.call_args)
            assert "Tier 2" in warning_call or "tier2" in warning_call.lower()


class TestAuthFailureVsTimeoutDistinction:
    """Test distinction between auth failures (401) and timeouts in fallback scoring."""

    @pytest.mark.asyncio
    async def test_auth_failure_triggers_neutral_fallback(self):
        """Auth failure (401) should trigger neutral fallback score (0.5)."""
        settings = JudgeSettings()
        engine = LLMJudgeEngine(settings)

        # Simulate 401 auth failure
        with patch.object(
            engine,
            "create_judge_agent",
            side_effect=Exception("401 Unauthorized"),
        ):
            with patch.object(
                engine.fallback_engine,
                "compute_semantic_similarity",
                return_value=0.8,  # Would normally be higher
            ):
                score = await engine.assess_technical_accuracy("paper", "review")

                # Should cap at 0.5 for auth failures (not use full semantic score)
                assert score <= 0.5

    @pytest.mark.asyncio
    async def test_timeout_allows_higher_fallback(self):
        """Timeout should use full fallback score (not capped at 0.5)."""
        settings = JudgeSettings()
        engine = LLMJudgeEngine(settings)

        # Simulate timeout (not auth failure)
        with patch.object(
            engine,
            "create_judge_agent",
            side_effect=TimeoutError("Request timed out"),
        ):
            with patch.object(
                engine.fallback_engine,
                "compute_semantic_similarity",
                return_value=0.8,
            ):
                score = await engine.assess_technical_accuracy("paper", "review")

                # Timeout allows using full semantic similarity score
                assert score == 0.8  # Not capped
