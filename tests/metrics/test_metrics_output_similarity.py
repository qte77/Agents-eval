"""
Tests for the output_similarity metric.

This module verifies that the output_similarity metric correctly identifies when
an agent's output matches the expected answer.
"""

from app.evals.metrics import output_similarity


def test_output_similarity_exact_match():
    assert output_similarity("42", "42") is True


def test_output_similarity_whitespace():
    assert output_similarity("  answer  ", "answer") is True


def test_output_similarity_incorrect():
    assert output_similarity("foo", "bar") is False
