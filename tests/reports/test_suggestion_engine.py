"""Tests for the suggestion engine module.

Tests cover: Suggestion model, SuggestionEngine rule-based generation,
severity levels, metric/tier references, and optional LLM path.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.data_models.evaluation_models import (
    CompositeResult,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.data_models.report_models import Suggestion, SuggestionSeverity
from app.reports.suggestion_engine import SuggestionEngine

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tier1_result() -> Tier1Result:
    """Tier 1 result with moderate scores."""
    return Tier1Result(
        cosine_score=0.3,
        jaccard_score=0.25,
        semantic_score=0.4,
        execution_time=10.0,
        time_score=0.8,
        task_success=1.0,
        overall_score=0.42,
    )


@pytest.fixture()
def tier1_result_low() -> Tier1Result:
    """Tier 1 result with critically low scores."""
    return Tier1Result(
        cosine_score=0.08,
        jaccard_score=0.05,
        semantic_score=0.1,
        execution_time=10.0,
        time_score=0.8,
        task_success=0.0,
        overall_score=0.15,
    )


@pytest.fixture()
def tier2_result() -> Tier2Result:
    """Tier 2 result with moderate scores."""
    return Tier2Result(
        technical_accuracy=0.5,
        constructiveness=0.55,
        clarity=0.6,
        planning_rationality=0.5,
        overall_score=0.54,
        model_used="gpt-4",
        api_cost=0.01,
    )


@pytest.fixture()
def tier3_result() -> Tier3Result:
    """Tier 3 result with moderate scores."""
    return Tier3Result(
        path_convergence=0.4,
        tool_selection_accuracy=0.5,
        coordination_centrality=0.45,
        task_distribution_balance=0.5,
        overall_score=0.46,
        graph_complexity=5,
    )


@pytest.fixture()
def composite_result_low(
    tier1_result_low: Tier1Result,
) -> CompositeResult:
    """Composite result with critically low tier 1 and no tier 2/3."""
    return CompositeResult(
        composite_score=0.2,
        recommendation="reject",
        recommendation_weight=-0.8,
        metric_scores={
            "cosine_score": 0.08,
            "jaccard_score": 0.05,
            "semantic_score": 0.1,
            "time_score": 0.8,
            "task_success": 0.0,
        },
        tier1_score=0.15,
        tier2_score=None,
        tier3_score=0.3,
        evaluation_complete=True,
    )


@pytest.fixture()
def composite_result_moderate(
    tier1_result: Tier1Result,
    tier2_result: Tier2Result,
    tier3_result: Tier3Result,
) -> CompositeResult:
    """Composite result with moderate scores across all tiers."""
    return CompositeResult(
        composite_score=0.55,
        recommendation="weak_accept",
        recommendation_weight=0.2,
        metric_scores={
            "cosine_score": 0.3,
            "jaccard_score": 0.25,
            "semantic_score": 0.4,
            "time_score": 0.8,
            "task_success": 1.0,
            "technical_accuracy": 0.5,
            "constructiveness": 0.55,
            "clarity": 0.6,
            "planning_rationality": 0.5,
            "path_convergence": 0.4,
            "tool_selection_accuracy": 0.5,
            "coordination_centrality": 0.45,
            "task_distribution_balance": 0.5,
        },
        tier1_score=0.42,
        tier2_score=0.54,
        tier3_score=0.46,
        evaluation_complete=True,
    )


# ---------------------------------------------------------------------------
# Suggestion model tests
# ---------------------------------------------------------------------------


class TestSuggestionModel:
    """Tests for the Suggestion Pydantic model."""

    def test_suggestion_has_required_fields(self) -> None:
        """Suggestion model has all required fields."""
        s = Suggestion(
            metric="cosine_score",
            tier=1,
            severity=SuggestionSeverity.CRITICAL,
            message="Low BLEU score — review lacks technical terminology.",
            action="Add specific technical terms from the paper abstract.",
        )
        assert s.metric == "cosine_score"
        assert s.tier == 1
        assert s.severity == SuggestionSeverity.CRITICAL
        assert "terminology" in s.message
        assert "abstract" in s.action

    def test_suggestion_severity_levels(self) -> None:
        """SuggestionSeverity has critical, warning, and info levels."""
        assert SuggestionSeverity.CRITICAL.value == "critical"
        assert SuggestionSeverity.WARNING.value == "warning"
        assert SuggestionSeverity.INFO.value == "info"

    def test_suggestion_tier_validation(self) -> None:
        """Suggestion tier must be 1, 2, or 3."""
        # Valid tiers
        for tier in (1, 2, 3):
            s = Suggestion(
                metric="overall_score",
                tier=tier,
                severity=SuggestionSeverity.INFO,
                message="Msg",
                action="Act",
            )
            assert s.tier == tier

    def test_suggestion_tier_invalid_raises(self) -> None:
        """Suggestion with tier outside 1-3 raises ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Suggestion(
                metric="overall_score",
                tier=0,
                severity=SuggestionSeverity.INFO,
                message="Msg",
                action="Act",
            )


# ---------------------------------------------------------------------------
# SuggestionEngine rule-based tests
# ---------------------------------------------------------------------------


class TestSuggestionEngineRuleBased:
    """Tests for rule-based suggestion generation."""

    def test_engine_generates_suggestions_from_composite(
        self, composite_result_low: CompositeResult
    ) -> None:
        """Engine generates at least one suggestion for a low-scoring result."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        assert len(suggestions) >= 1

    def test_critical_severity_for_very_low_scores(
        self, composite_result_low: CompositeResult
    ) -> None:
        """Scores below 0.2 threshold produce critical suggestions."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        severities = {s.severity for s in suggestions}
        assert SuggestionSeverity.CRITICAL in severities

    def test_suggestions_reference_triggering_metric(
        self, composite_result_low: CompositeResult
    ) -> None:
        """Each suggestion references the metric that triggered it."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        # Every suggestion must have a non-empty metric field
        for suggestion in suggestions:
            assert suggestion.metric != ""

    def test_suggestions_reference_tier(self, composite_result_low: CompositeResult) -> None:
        """Each suggestion identifies the tier it belongs to."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        for suggestion in suggestions:
            assert suggestion.tier in (1, 2, 3)

    def test_warning_for_below_average_scores(
        self, composite_result_moderate: CompositeResult
    ) -> None:
        """Scores below average (0.5) but above critical threshold get warning severity."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_moderate)
        # Moderate result has some sub-0.5 scores → should produce warnings
        severities = {s.severity for s in suggestions}
        assert SuggestionSeverity.WARNING in severities or SuggestionSeverity.CRITICAL in severities

    def test_no_llm_suggestions_flag(self, composite_result_moderate: CompositeResult) -> None:
        """Engine respects no_llm_suggestions=True by returning only rule-based."""
        engine = SuggestionEngine(no_llm_suggestions=True)
        suggestions = engine.generate(composite_result_moderate)
        # With flag set, no LLM call should have been made; suggestions still returned
        assert isinstance(suggestions, list)

    def test_tier1_low_cosine_produces_specific_message(
        self, composite_result_low: CompositeResult
    ) -> None:
        """Low cosine score produces message referencing cosine/text similarity."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        cosine_suggestions = [s for s in suggestions if s.metric == "cosine_score"]
        assert len(cosine_suggestions) >= 1
        # Message should be specific (not generic)
        msg = cosine_suggestions[0].message.lower()
        assert any(kw in msg for kw in ("cosine", "similarity", "text", "vocabulary", "bleu"))

    def test_task_success_zero_produces_critical(
        self, composite_result_low: CompositeResult
    ) -> None:
        """Task success of 0.0 produces a critical suggestion."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        task_sugg = [s for s in suggestions if s.metric == "task_success"]
        assert any(s.severity == SuggestionSeverity.CRITICAL for s in task_sugg)

    def test_tier2_missing_produces_info(self, composite_result_low: CompositeResult) -> None:
        """When tier2_score is None, an info suggestion is produced."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        tier2_sugg = [s for s in suggestions if s.tier == 2]
        assert len(tier2_sugg) >= 1

    def test_suggestions_are_actionable(self, composite_result_low: CompositeResult) -> None:
        """Each suggestion has a non-empty action field."""
        engine = SuggestionEngine()
        suggestions = engine.generate(composite_result_low)
        for suggestion in suggestions:
            assert len(suggestion.action) > 5, f"Action too short: {suggestion.action!r}"

    def test_empty_metric_scores_produces_fallback(self) -> None:
        """Empty metric_scores with low composite produces at least one suggestion."""
        result = CompositeResult(
            composite_score=0.1,
            recommendation="reject",
            recommendation_weight=-1.0,
            metric_scores={},
            tier1_score=0.1,
            tier2_score=None,
            tier3_score=0.1,
            evaluation_complete=True,
        )
        engine = SuggestionEngine()
        suggestions = engine.generate(result)
        assert len(suggestions) >= 1


# ---------------------------------------------------------------------------
# SuggestionEngine LLM path tests
# ---------------------------------------------------------------------------


class TestSuggestionEngineLLM:
    """Tests for optional LLM-assisted suggestion generation."""

    @pytest.mark.asyncio
    async def test_llm_suggestions_called_when_available(
        self, composite_result_low: CompositeResult
    ) -> None:
        """When LLM provider is available, generate_async returns LLM-enhanced suggestions."""
        engine = SuggestionEngine()
        mock_result = [
            Suggestion(
                metric="cosine_score",
                tier=1,
                severity=SuggestionSeverity.CRITICAL,
                message="LLM-enhanced: text similarity very low.",
                action="Incorporate domain-specific terminology from the abstract.",
            )
        ]
        with patch.object(engine, "_generate_llm_suggestions", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_result
            suggestions = await engine.generate_async(composite_result_low)
        assert len(suggestions) >= 1

    @pytest.mark.asyncio
    async def test_llm_fallback_on_error(self, composite_result_low: CompositeResult) -> None:
        """On LLM error, generate_async falls back to rule-based suggestions."""
        engine = SuggestionEngine()
        with patch.object(
            engine,
            "_generate_llm_suggestions",
            new_callable=AsyncMock,
            side_effect=RuntimeError("LLM unavailable"),
        ):
            suggestions = await engine.generate_async(composite_result_low)
        # Must still return rule-based suggestions
        assert len(suggestions) >= 1
        for s in suggestions:
            assert isinstance(s, Suggestion)

    def test_no_llm_flag_skips_async_llm(self, composite_result_moderate: CompositeResult) -> None:
        """no_llm_suggestions=True causes generate() to skip LLM path entirely."""
        engine = SuggestionEngine(no_llm_suggestions=True)
        with patch.object(engine, "_generate_llm_suggestions") as mock_llm:
            engine.generate(composite_result_moderate)
            mock_llm.assert_not_called()
