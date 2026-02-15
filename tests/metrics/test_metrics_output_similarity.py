"""
Tests for output similarity in evaluation pipeline.

This module verifies that the traditional metrics engine correctly computes
similarity scores between agent outputs and reference texts.
"""

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
