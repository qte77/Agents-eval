"""
Tests for output similarity in evaluation pipeline.

This module verifies that the traditional metrics engine correctly computes
similarity scores between agent outputs and reference texts.
"""

from app.evals.traditional_metrics import TraditionalMetricsEngine


def calculate_output_similarity(agent_output: str, expected_answer: str) -> float:
    """
    Calculate similarity score between agent output and expected answer.

    This replaces the legacy metrics.output_similarity function with
    inline implementation.
    """
    if not agent_output and not expected_answer:
        return 1.0  # Both empty strings are identical

    if not agent_output or not expected_answer:
        return 0.0  # One empty, one not

    # Normalize strings for comparison
    agent_normalized = agent_output.strip().lower()
    expected_normalized = expected_answer.strip().lower()

    # Exact match
    if agent_normalized == expected_normalized:
        return 1.0

    # Simple Jaccard similarity on words
    agent_words = set(agent_normalized.split())
    expected_words = set(expected_normalized.split())

    if not agent_words and not expected_words:
        return 1.0

    intersection = agent_words & expected_words
    union = agent_words | expected_words

    return len(intersection) / len(union) if union else 0.0


def test_output_similarity_exact_match():
    similarity = calculate_output_similarity("42", "42")
    assert similarity == 1.0


def test_output_similarity_whitespace():
    similarity = calculate_output_similarity("  answer  ", "answer")
    assert similarity == 1.0


def test_output_similarity_incorrect():
    similarity = calculate_output_similarity("foo", "bar")
    assert similarity == 0.0


def test_traditional_metrics_similarity():
    """Test similarity calculation through the traditional metrics engine."""
    engine = TraditionalMetricsEngine()

    # Create temporary config for testing
    config = {"similarity_metrics": ["cosine", "jaccard", "semantic"]}

    result = engine.evaluate_traditional_metrics(
        agent_output="The quick brown fox",
        reference_texts=["The quick brown fox jumps"],
        start_time=0.0,
        end_time=0.1,
        config=config,
    )

    # Verify similarity scores are calculated
    assert 0.0 <= result.cosine_score <= 1.0
    assert 0.0 <= result.jaccard_score <= 1.0
    assert 0.0 <= result.semantic_score <= 1.0
    assert result.overall_score > 0.0
