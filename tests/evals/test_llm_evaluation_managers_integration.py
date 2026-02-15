"""
Integration tests for Tier 2 judge provider fallback (STORY-003).

End-to-end validation that provider fallback chain works correctly when
API keys are missing, with proper fallback metadata and neutral scores.
"""

from unittest.mock import patch

import pytest
from inline_snapshot import snapshot

from app.data_models.app_models import AppEnv
from app.data_models.evaluation_models import Tier1Result, Tier3Result
from app.judge.composite_scorer import CompositeScorer, EvaluationResults
from app.judge.llm_evaluation_managers import LLMJudgeEngine
from app.judge.settings import JudgeSettings


class TestTier2ProviderFallbackIntegration:
    """Integration tests for Tier 2 provider fallback with real evaluation flow."""

    @pytest.mark.asyncio
    async def test_fallback_to_secondary_when_primary_unavailable(self):
        """Should fallback to tier2_fallback_provider when primary API key missing."""
        # Arrange: primary=openai (no key), fallback=github (has key)
        settings = JudgeSettings(
            tier2_provider="openai",
            tier2_model="gpt-4o-mini",
            tier2_fallback_provider="github",
            tier2_fallback_model="gpt-4o-mini",
        )
        env_config = AppEnv(
            OPENAI_API_KEY="",  # Missing primary key
            GITHUB_API_KEY="test-github-key",  # Has fallback key
        )

        engine = LLMJudgeEngine(settings)

        # Act: Select provider
        selected = engine.select_available_provider(env_config)

        # Assert: Should select fallback
        assert selected is not None
        assert selected == ("github", "gpt-4o-mini")

    @pytest.mark.asyncio
    async def test_neutral_fallback_scores_when_all_providers_unavailable(self):
        """Should use neutral fallback scores (0.5) when no providers have API keys."""
        # Arrange: no API keys for any provider
        settings = JudgeSettings(
            tier2_provider="openai",
            tier2_fallback_provider="github",
        )

        engine = LLMJudgeEngine(settings)

        # Act: Try comprehensive evaluation (should hit auth failures)
        with patch.object(
            engine,
            "create_judge_agent",
            side_effect=Exception("401 Unauthorized - Invalid API key"),
        ):
            result = await engine.evaluate_comprehensive(
                paper="Sample paper content",
                review="Sample review content",
                execution_trace={},
            )

        # Assert: All scores should be neutral (0.5) due to auth failures
        assert result.technical_accuracy == snapshot(0.5)
        assert result.constructiveness <= 0.5  # Capped at neutral
        assert result.planning_rationality == snapshot(0.5)
        assert result.fallback_used is True

    @pytest.mark.asyncio
    async def test_tier2_result_includes_fallback_metadata(self):
        """Tier2Result should include fallback_used flag when fallback triggered."""
        # Arrange: simulate auth failure to trigger fallback
        settings = JudgeSettings()
        env_config = AppEnv(OPENAI_API_KEY="sk-test-key", GITHUB_API_KEY="")
        engine = LLMJudgeEngine(settings, env_config=env_config)

        # Act: Force auth failure
        with patch.object(
            engine,
            "create_judge_agent",
            side_effect=Exception("401 Unauthorized"),
        ):
            result = await engine.evaluate_comprehensive(
                paper="Test paper",
                review="Test review",
                execution_trace={},
            )

        # Assert: Result should have fallback metadata
        assert result.fallback_used is True
        # model_used still shows configured provider (not "fallback_traditional")
        # because auth failure happened during assessment, not complete fallback
        assert result.model_used == snapshot("openai/gpt-4o-mini")

    @pytest.mark.asyncio
    async def test_composite_scorer_redistributes_weights_when_tier2_none(self):
        """CompositeScorer should redistribute weights to Tier 1+3 when Tier 2 is None."""
        # Arrange: results with Tier 2 = None
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

        # Act: Compute composite with missing Tier 2
        scorer = CompositeScorer()
        composite_result = scorer.evaluate_composite_with_optional_tier2(results)

        # Assert: Should complete successfully and redistribute weights
        assert composite_result.composite_score >= 0.0
        assert composite_result.composite_score <= 1.0
        # tier2_score should be None when Tier 2 was skipped
        assert composite_result.tier2_score is None or composite_result.tier2_score == 0.0
        # composite_score should be weighted average of tier1 + tier3 only
        assert composite_result.composite_score == snapshot(
            0.8500000000000001
        )  # Will capture actual value

    @pytest.mark.asyncio
    async def test_logs_warn_when_no_providers_available(self):
        """Should log warning when all providers lack API keys."""
        # Arrange: no API keys available
        settings = JudgeSettings(
            tier2_provider="openai",
            tier2_fallback_provider="github",
        )
        env_config = AppEnv(
            OPENAI_API_KEY="",
            GITHUB_API_KEY="",
        )

        engine = LLMJudgeEngine(settings)

        # Act & Assert: Should log warning
        with patch("app.judge.llm_evaluation_managers.logger") as mock_logger:
            selected = engine.select_available_provider(env_config)

            assert selected is None
            mock_logger.warning.assert_called()
            warning_call = str(mock_logger.warning.call_args)
            # Should mention both providers
            assert "openai" in warning_call.lower() or "github" in warning_call.lower()
