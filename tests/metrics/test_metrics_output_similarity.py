"""
Tests for output similarity in evaluation pipeline.

This module verifies that the traditional metrics engine correctly computes
similarity scores between agent outputs and reference texts.
"""

from hypothesis import given, settings
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.judge.traditional_metrics import TraditionalMetricsEngine


def test_traditional_metrics_similarity():
    """Test similarity calculation through the traditional metrics engine."""
    engine = TraditionalMetricsEngine()

    result = engine.evaluate_traditional_metrics(
        agent_output="The quick brown fox",
        reference_texts=["The quick brown fox jumps"],
        start_time=0.0,
        end_time=0.1,
    )

    # Verify similarity scores are calculated
    assert 0.0 <= result.cosine_score <= 1.0
    assert 0.0 <= result.jaccard_score <= 1.0
    assert 0.0 <= result.semantic_score <= 1.0
    assert result.overall_score > 0.0


# STORY-004: Hypothesis property-based tests for metrics invariants
# Reason: deadline=None because this tests a math invariant, not performance
@settings(deadline=None)
@given(
    text_length=st.integers(min_value=1, max_value=200),
    reference_count=st.integers(min_value=1, max_value=5),
)
def test_similarity_scores_always_in_bounds(text_length: int, reference_count: int):
    """Property: Similarity scores always in [0, 1] range."""
    # Arrange
    engine = TraditionalMetricsEngine()
    agent_output = "word " * text_length
    reference_texts = ["reference text " * 10 for _ in range(reference_count)]

    # Act
    result = engine.evaluate_traditional_metrics(
        agent_output=agent_output,
        reference_texts=reference_texts,
        start_time=0.0,
        end_time=0.1,
    )

    # Assert invariants
    assert 0.0 <= result.cosine_score <= 1.0
    assert 0.0 <= result.jaccard_score <= 1.0
    assert 0.0 <= result.semantic_score <= 1.0
    assert 0.0 <= result.overall_score <= 1.0


# STORY-004: Inline-snapshot regression tests for metrics output
def test_similarity_result_structure():
    """Snapshot: Traditional metrics result structure."""
    # Arrange
    engine = TraditionalMetricsEngine()

    # Act
    result = engine.evaluate_traditional_metrics(
        agent_output="The quick brown fox",
        reference_texts=["The quick brown fox jumps"],
        start_time=0.0,
        end_time=0.1,
    )
    dumped = result.model_dump()

    # Assert with snapshot
    assert dumped == snapshot(
        {
            "cosine_score": 0.7765145304745156,
            "jaccard_score": 0.8,
            "semantic_score": 0.7765145304745156,
            "execution_time": 0.1,
            "time_score": 0.9048374180359595,
            "task_success": 0.0,
            "overall_score": 0.794043913135757,
        }
    )
