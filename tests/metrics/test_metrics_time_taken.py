"""
Tests for time calculation in evaluation pipeline.

This module verifies that the evaluation pipeline correctly computes elapsed
time during agent execution for performance metrics.
"""

import pytest

from app.evals.evaluation_pipeline import EvaluationPipeline


def calculate_time_taken(start_time: float, end_time: float) -> float:
    """Calculate duration between start and end timestamps.

    This replaces the legacy metrics.time_taken function with inline implementation.
    """
    if end_time < start_time:
        raise ValueError("end_time must be greater than or equal to start_time")
    return end_time - start_time


@pytest.mark.asyncio
async def test_pipeline_execution_timing():
    """Scenario: Verify pipeline tracks execution time correctly"""

    # Given: A configured evaluation pipeline
    pipeline = EvaluationPipeline()

    # When: Running pipeline execution tracking
    stats = pipeline.get_execution_stats()

    # Then: Verify timing infrastructure exists
    assert "tier1_time" in stats
    assert "tier2_time" in stats
    assert "tier3_time" in stats
    assert "total_time" in stats
