"""Tests for MAS composition sweep statistical analysis.

This module tests the statistical analysis module that calculates mean,
stddev, min, max per composition and generates summary reports.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.benchmark.sweep_analysis import (
    SweepAnalyzer,
    calculate_statistics,
    generate_markdown_summary,
)
from app.benchmark.sweep_config import AgentComposition
from app.data_models.evaluation_models import CompositeResult


@pytest.fixture
def sample_results() -> list[tuple[AgentComposition, CompositeResult]]:
    """Create sample results for testing."""
    comp1 = AgentComposition(
        include_researcher=True, include_analyst=False, include_synthesiser=False
    )
    comp2 = AgentComposition(
        include_researcher=False, include_analyst=True, include_synthesiser=False
    )

    results = [
        (
            comp1,
            CompositeResult(
                composite_score=0.75,
                recommendation="Accept",
                recommendation_weight=0.75,
                metric_scores={"tier1": 0.8, "tier2": 0.7, "tier3": 0.75},
                tier1_score=0.8,
                tier2_score=0.7,
                tier3_score=0.75,
                evaluation_complete=True,
            ),
        ),
        (
            comp1,
            CompositeResult(
                composite_score=0.80,
                recommendation="Accept",
                recommendation_weight=0.80,
                metric_scores={"tier1": 0.85, "tier2": 0.75, "tier3": 0.80},
                tier1_score=0.85,
                tier2_score=0.75,
                tier3_score=0.80,
                evaluation_complete=True,
            ),
        ),
        (
            comp2,
            CompositeResult(
                composite_score=0.65,
                recommendation="Reject",
                recommendation_weight=-0.65,
                metric_scores={"tier1": 0.70, "tier2": 0.60, "tier3": 0.65},
                tier1_score=0.70,
                tier2_score=0.60,
                tier3_score=0.65,
                evaluation_complete=True,
            ),
        ),
    ]
    return results


class TestCalculateStatistics:
    """Tests for calculate_statistics() function."""

    def test_single_result_statistics(self):
        """Test statistics calculation with a single result."""
        scores = [0.75]
        stats = calculate_statistics(scores)

        assert stats["mean"] == 0.75
        assert stats["stddev"] == 0.0
        assert stats["min"] == 0.75
        assert stats["max"] == 0.75

    def test_multiple_results_statistics(self):
        """Test statistics calculation with multiple results."""
        scores = [0.75, 0.80, 0.70, 0.85]
        stats = calculate_statistics(scores)

        assert 0.7 < stats["mean"] < 0.8
        assert stats["stddev"] > 0
        assert stats["min"] == 0.70
        assert stats["max"] == 0.85

    def test_empty_scores_raises_error(self):
        """Test that empty scores list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate statistics"):
            calculate_statistics([])

    @given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=1, max_size=100))
    def test_statistics_bounds(self, scores: list[float]):
        """Property test: mean is always between min and max."""
        stats = calculate_statistics(scores)

        assert stats["min"] <= stats["mean"] <= stats["max"]
        assert stats["stddev"] >= 0.0

    @given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=2, max_size=100))
    def test_stddev_zero_only_for_identical_values(self, scores: list[float]):
        """Property test: stddev is zero only when all values are identical."""
        stats = calculate_statistics(scores)

        if len(set(scores)) == 1:
            assert stats["stddev"] == 0.0
        elif len(set(scores)) > 1:
            assert stats["stddev"] > 0.0


class TestSweepAnalyzer:
    """Tests for SweepAnalyzer class."""

    def test_analyzer_aggregates_by_composition(
        self, sample_results: list[tuple[AgentComposition, CompositeResult]]
    ):
        """Test that analyzer groups results by composition."""
        analyzer = SweepAnalyzer(sample_results)
        stats = analyzer.analyze()

        # Should have 2 unique compositions
        assert len(stats) == 2

    def test_analyzer_calculates_correct_means(
        self, sample_results: list[tuple[AgentComposition, CompositeResult]]
    ):
        """Test that analyzer calculates correct mean values."""
        analyzer = SweepAnalyzer(sample_results)
        stats = analyzer.analyze()

        # First composition has 2 results: 0.75, 0.80
        comp1_stats = next(s for s in stats if s.composition.include_researcher is True)
        expected_mean = (0.75 + 0.80) / 2
        assert abs(comp1_stats.overall_score_mean - expected_mean) < 0.01

    def test_analyzer_counts_samples_correctly(
        self, sample_results: list[tuple[AgentComposition, CompositeResult]]
    ):
        """Test that analyzer counts samples per composition."""
        analyzer = SweepAnalyzer(sample_results)
        stats = analyzer.analyze()

        comp1_stats = next(s for s in stats if s.composition.include_researcher is True)
        comp2_stats = next(s for s in stats if s.composition.include_analyst is True)

        assert comp1_stats.num_samples == 2
        assert comp2_stats.num_samples == 1


class TestMarkdownSummaryGeneration:
    """Tests for generate_markdown_summary() function."""

    def test_markdown_summary_has_table(
        self, sample_results: list[tuple[AgentComposition, CompositeResult]]
    ):
        """Test that markdown summary contains a table."""
        analyzer = SweepAnalyzer(sample_results)
        stats = analyzer.analyze()
        markdown = generate_markdown_summary(stats)

        assert "| Composition" in markdown
        assert "|-------" in markdown  # Table separator

    def test_markdown_summary_includes_all_metrics(
        self, sample_results: list[tuple[AgentComposition, CompositeResult]]
    ):
        """Test that markdown summary includes all metrics."""
        analyzer = SweepAnalyzer(sample_results)
        stats = analyzer.analyze()
        markdown = generate_markdown_summary(stats)

        assert "Overall Score" in markdown
        assert "Tier 1" in markdown
        assert "Tier 2" in markdown
        assert "Tier 3" in markdown
        assert "Confidence" in markdown

    def test_markdown_summary_includes_stddev(
        self, sample_results: list[tuple[AgentComposition, CompositeResult]]
    ):
        """Test that markdown summary includes stddev values."""
        analyzer = SweepAnalyzer(sample_results)
        stats = analyzer.analyze()
        markdown = generate_markdown_summary(stats)

        # Should contain mean ± stddev format
        assert "±" in markdown

    def test_markdown_summary_shows_sample_counts(
        self, sample_results: list[tuple[AgentComposition, CompositeResult]]
    ):
        """Test that markdown summary shows sample counts."""
        analyzer = SweepAnalyzer(sample_results)
        stats = analyzer.analyze()
        markdown = generate_markdown_summary(stats)

        assert "n=" in markdown or "samples" in markdown.lower()
