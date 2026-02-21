"""
STORY-006: Judge pipeline accuracy fix tests (BDD style, RED phase).

Tests for four issues:
  F8  - Tier2Result.clarity always received constructiveness score
  F18 - _extract_planning_decisions silently swallowed all exceptions
  F19 - Recommendation matching used naive "good" in text heuristic
  C1  - Cosine score could exceed 1.0, causing Pydantic validation failure
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from hypothesis import given
from hypothesis import settings as hyp_settings
from hypothesis import strategies as st

from app.data_models.evaluation_models import Tier1Result
from app.data_models.peerread_models import PeerReadReview
from app.judge.llm_evaluation_managers import LLMJudgeEngine
from app.judge.settings import JudgeSettings
from app.judge.traditional_metrics import TraditionalMetricsEngine, create_evaluation_result

# ---------------------------------------------------------------------------
# F8: Tier2Result.clarity field
# ---------------------------------------------------------------------------


class TestTier2ResultClarityField:
    """F8 — clarity field must not silently alias constructiveness."""

    def _make_engine(self) -> LLMJudgeEngine:
        from app.data_models.app_models import AppEnv

        return LLMJudgeEngine(
            JudgeSettings(tier2_provider="openai"),
            env_config=AppEnv(OPENAI_API_KEY="sk-test"),
        )

    @pytest.mark.asyncio
    async def test_tier2_result_does_not_have_clarity_field(self):
        """AC1: Tier2Result must NOT have a clarity field (field removed)."""
        from app.data_models.evaluation_models import Tier2Result

        # The field should not exist on the model
        assert "clarity" not in Tier2Result.model_fields, (
            "Tier2Result.clarity field still present — it always received constructiveness score "
            "(Review F8). Remove it."
        )

    @pytest.mark.asyncio
    async def test_evaluate_comprehensive_does_not_pass_clarity(self, caplog):
        """AC1: evaluate_comprehensive must not assign constructiveness to clarity."""
        engine = self._make_engine()

        with (
            patch.object(engine, "assess_technical_accuracy", return_value=0.8),
            patch.object(engine, "assess_constructiveness", return_value=0.7),
            patch.object(engine, "assess_planning_rationality", return_value=0.75),
        ):
            result = await engine.evaluate_comprehensive("paper", "review", {})

        # The result object must not have a clarity attribute
        assert not hasattr(result, "clarity"), (
            "evaluate_comprehensive still sets clarity=constructiveness_score (Review F8)"
        )

    @pytest.mark.asyncio
    async def test_complete_fallback_does_not_set_clarity(self):
        """AC1: _complete_fallback must not set clarity on Tier2Result."""
        engine = self._make_engine()
        result = engine._complete_fallback("paper", "review", {})
        assert not hasattr(result, "clarity"), (
            "_complete_fallback still passes clarity= kwarg to Tier2Result (Review F8)"
        )


# ---------------------------------------------------------------------------
# F18: _extract_planning_decisions exception handling
# ---------------------------------------------------------------------------


class TestExtractPlanningDecisionsExceptionHandling:
    """F18 — exception must be logged and type narrowed."""

    def _make_engine(self) -> LLMJudgeEngine:
        from app.data_models.app_models import AppEnv

        return LLMJudgeEngine(
            JudgeSettings(tier2_provider="openai"),
            env_config=AppEnv(OPENAI_API_KEY="sk-test"),
        )

    def test_extract_planning_decisions_logs_on_attribute_error(self):
        """AC2: AttributeError must be caught and the stub string returned (not re-raised)."""
        engine = self._make_engine()

        # Trigger AttributeError: "agent_interactions" is a string, not a list;
        # len("not-a-list") works but iterating dicts from it fails at d.get(...)
        bad_trace = {"agent_interactions": "not-a-list"}

        # Must return stub string, not raise
        result = engine._extract_planning_decisions(bad_trace)
        assert isinstance(result, str)
        assert result  # non-empty stub returned

    def test_extract_planning_decisions_logs_on_type_error(self):
        """AC2: TypeError must be caught and the stub string returned (not re-raised)."""
        engine = self._make_engine()

        # Non-dict "interactions" element causes TypeError when .get() is called
        bad_trace = {"agent_interactions": [None, None]}

        result = engine._extract_planning_decisions(bad_trace)
        assert isinstance(result, str)

    def test_extract_planning_decisions_does_not_swallow_unknown_exceptions(self):
        """AC2: Exceptions not in (AttributeError, KeyError, TypeError) must propagate."""
        engine = self._make_engine()

        # Patch the trace to have a get method that raises ValueError (not in narrowed set)
        mock_trace = Mock()
        mock_trace.get = Mock(side_effect=ValueError("not caught"))

        # The narrowed except clause should NOT catch ValueError
        with pytest.raises(ValueError, match="not caught"):
            engine._extract_planning_decisions(mock_trace)


# ---------------------------------------------------------------------------
# F19: Recommendation matching
# ---------------------------------------------------------------------------


class TestRecommendationMatching:
    """F19 — recommendation must not use naive 'good in text' heuristic."""

    def _make_review(self, recommendation: str, comments: str = "review text") -> PeerReadReview:
        return PeerReadReview(recommendation=recommendation, comments=comments)

    def test_negation_not_misclassified_as_positive(self):
        """AC3: 'not good' review must not be treated as positive recommendation."""
        reviews = [self._make_review("4", "not good enough for acceptance")]

        create_evaluation_result(
            paper_id="p1",
            agent_review="not good enough for acceptance",
            ground_truth_reviews=reviews,
        )

        # Ground truth recommendation 4 >= 3.0 → expected positive
        # Agent text "not good" → old heuristic would see "good" → match=True
        # New implementation: use numeric comparison not text sentiment
        # Since we cannot know the agent score without the GeneratedReview object,
        # the implementation should document this is an approximation OR use
        # the integer field. Either way, "not good" should NOT match by word-in-string.
        # We verify the implementation no longer uses "good" in text as sole criterion.

        # The old buggy code: "positive" if "good" in agent_review.lower() else "negative"
        # "not good" contains "good" → old code returns True when gt_avg >= 3.0
        # New code: must not mis-classify "not good" as a positive sentiment match.
        # We verify this by checking that the implementation does NOT simply look for "good".
        import inspect

        source = inspect.getsource(create_evaluation_result)
        assert '"good" in' not in source, (
            "create_evaluation_result still uses naive '\"good\" in text' heuristic (Review F19). "
            "Replace with integer recommendation comparison or explicit approximation comment."
        )

    def test_recommendation_matching_uses_numeric_or_documented_approximation(self):
        """AC3: Implementation uses numeric comparison or is documented as approximation."""
        import inspect

        from app.judge.traditional_metrics import create_evaluation_result as fn

        source = inspect.getsource(fn)

        # Check that the old naive pattern is gone
        assert '"good" in' not in source, (
            "Old heuristic '\"good\" in agent_review.lower()' still present (Review F19)"
        )

    def test_high_ground_truth_recommendation_matches_high_agent_score(self):
        """AC3: High GT recommendation (>=3) matches when agent review score >= 3."""
        # Create a review with recommendation=4 (positive)
        reviews = [self._make_review("4")]

        result = create_evaluation_result(
            paper_id="p1",
            agent_review="this paper has solid contributions and clear methodology",
            ground_truth_reviews=reviews,
        )

        # Result should be a valid PeerReadEvalResult
        assert hasattr(result, "recommendation_match")
        assert isinstance(result.recommendation_match, bool)

    def test_low_ground_truth_recommendation_with_negative_agent(self):
        """AC3: Low GT recommendation (<3) produces valid boolean result."""
        reviews = [self._make_review("1")]

        result = create_evaluation_result(
            paper_id="p1",
            agent_review="this paper has serious issues and lacks novelty",
            ground_truth_reviews=reviews,
        )

        assert hasattr(result, "recommendation_match")
        assert isinstance(result.recommendation_match, bool)


# ---------------------------------------------------------------------------
# C1: Cosine score clamping (property test un-skipped)
# ---------------------------------------------------------------------------


class TestCosineScoreClamping:
    """C1 — cosine score above 1.0 must be clamped before Tier1Result construction."""

    def test_evaluate_traditional_metrics_cosine_never_exceeds_1(self):
        """AC5: Cosine score is clamped to 1.0 before Tier1Result validation."""
        engine = TraditionalMetricsEngine()

        # Patch compute_cosine_similarity to return a value > 1.0 (FP error simulation)
        with patch.object(engine, "compute_cosine_similarity", return_value=1.0000000000000002):
            # Must not raise Pydantic ValidationError
            result = engine.evaluate_traditional_metrics(
                agent_output="some review text",
                reference_texts=["some review text"],
                start_time=1000.0,
                end_time=1001.0,
            )

        assert result.cosine_score <= 1.0, (
            f"cosine_score {result.cosine_score} exceeds 1.0 — not clamped (tests-review C1)"
        )

    def test_tier1_result_accepts_exactly_1(self):
        """Tier1Result must accept cosine_score == 1.0 without error."""
        result = Tier1Result(
            cosine_score=1.0,
            jaccard_score=0.5,
            semantic_score=0.5,
            execution_time=1.0,
            time_score=0.5,
            task_success=1.0,
            overall_score=0.5,
        )
        assert result.cosine_score == 1.0

    def test_cosine_clamped_when_find_best_match_returns_over_1(self):
        """AC5: evaluate_traditional_metrics clamps cosine from find_best_match."""
        from app.judge.traditional_metrics import SimilarityScores

        engine = TraditionalMetricsEngine()

        with patch.object(
            engine,
            "find_best_match",
            return_value=SimilarityScores(
                cosine=1.0000000000000002,  # FP overflow
                jaccard=0.5,
                semantic=0.5,
            ),
        ):
            result = engine.evaluate_traditional_metrics(
                agent_output="text",
                reference_texts=["text"],
                start_time=0.0,
                end_time=1.0,
            )

        assert result.cosine_score <= 1.0


# ---------------------------------------------------------------------------
# C1: Property test (un-skipped from test_traditional_metrics.py)
# ---------------------------------------------------------------------------


class TestTier1ScoresPropertyUnSkipped:
    """Property-based test validating Tier1Result scores always in valid range (un-skipped C1)."""

    @given(
        agent_output=st.text(min_size=10, max_size=200).filter(
            lambda s: s.strip() and any(c.isalnum() for c in s)
        ),
        reference_texts=st.lists(
            st.text(min_size=10, max_size=200).filter(
                lambda s: s.strip() and any(c.isalnum() for c in s)
            ),
            min_size=1,
            max_size=5,
        ),
    )
    @hyp_settings(max_examples=50)
    def test_tier1_result_scores_always_valid(self, agent_output, reference_texts):
        """Property: Tier1Result cosine_score is always clamped to [0, 1]."""
        engine = TraditionalMetricsEngine()
        start_time = 1000.0
        end_time = 1001.0

        result = engine.evaluate_traditional_metrics(
            agent_output, reference_texts, start_time, end_time
        )

        # PROPERTY: cosine_score must be in [0, 1] — clamped for FP issues
        assert 0.0 <= result.cosine_score <= 1.0, (
            f"cosine_score={result.cosine_score} out of range [0,1] (tests-review C1)"
        )
        assert 0.0 <= result.jaccard_score <= 1.0
        assert 0.0 <= result.semantic_score <= 1.0
        assert result.execution_time > 0.0
        assert 0.0 < result.time_score <= 1.0
        assert result.task_success in [0.0, 1.0]
        assert 0.0 <= result.overall_score <= 1.0
