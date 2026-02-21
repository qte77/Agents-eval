"""Tests for traditional metrics — STORY-008 AC5.

Verifies that evaluate_single_traditional does NOT use time.sleep
(AC5: remove artificial delay from evaluate_single_traditional).
"""

from unittest.mock import patch

from app.judge.traditional_metrics import evaluate_single_traditional


class TestEvaluateSingleTraditionalNoSleep:
    """Tests for AC5: time.sleep removed from evaluate_single_traditional."""

    def test_evaluate_single_traditional_does_not_sleep(self):
        """evaluate_single_traditional must not call time.sleep.

        AC5: The artificial time.sleep(0.001) was removed because
        measure_execution_time already clamps minimum.
        """
        with patch("time.sleep") as mock_sleep:
            evaluate_single_traditional(
                agent_output="This paper presents a novel approach.",
                reference_texts=["The work demonstrates strong contribution."],
            )
            # If time.sleep is called anywhere during evaluate_single_traditional,
            # this assertion will fail — confirming the sleep is still present (RED).
            mock_sleep.assert_not_called()

    def test_evaluate_single_traditional_returns_tier1_result(self):
        """evaluate_single_traditional returns a Tier1Result."""
        from app.data_models.evaluation_models import Tier1Result

        result = evaluate_single_traditional(
            agent_output="This paper presents a novel approach to machine learning.",
            reference_texts=["The work demonstrates strong machine learning contributions."],
        )
        assert isinstance(result, Tier1Result)
        assert 0.0 <= result.overall_score <= 1.0
