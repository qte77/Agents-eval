"""Shared fixtures for tests/judge/ test modules.

Provides common evaluation fixtures (JudgeSettings, tier results) to avoid
duplication across judge test files. Fixtures here are auto-discovered by
pytest for all tests in this directory.
"""

import pytest

from app.config.judge_settings import JudgeSettings
from app.data_models.evaluation_models import (
    Tier1Result,
    Tier2Result,
    Tier3Result,
)


@pytest.fixture
def judge_settings():
    """JudgeSettings instance with defaults for judge tests.

    Returns:
        JudgeSettings: Default judge configuration.
    """
    return JudgeSettings()


@pytest.fixture
def sample_tier1_result():
    """Sample Tier 1 evaluation result for judge tests.

    Returns:
        Tier1Result: Tier 1 result with representative scores.
    """
    return Tier1Result(
        cosine_score=0.8,
        jaccard_score=0.7,
        semantic_score=0.85,
        execution_time=5.0,
        time_score=0.9,
        task_success=1.0,
        overall_score=0.8,
    )


@pytest.fixture
def sample_tier2_result():
    """Sample Tier 2 evaluation result for judge tests.

    Returns:
        Tier2Result: Tier 2 result with representative scores.
    """
    return Tier2Result(
        technical_accuracy=0.75,
        constructiveness=0.8,
        planning_rationality=0.85,
        overall_score=0.78,
        model_used="gpt-4",
        api_cost=0.05,
        fallback_used=False,
    )


@pytest.fixture
def sample_tier3_result():
    """Sample Tier 3 evaluation result for judge tests.

    Returns:
        Tier3Result: Tier 3 result with representative scores.
    """
    return Tier3Result(
        path_convergence=0.7,
        tool_selection_accuracy=0.8,
        communication_overhead=0.6,
        coordination_centrality=0.75,
        task_distribution_balance=0.7,
        overall_score=0.72,
        graph_complexity=5,
    )
