"""Shared fixtures for tests/evals/ test modules.

Provides common evaluation pipeline fixtures to avoid duplication across
eval test files. Fixtures here are auto-discovered by pytest for all tests
in this directory.
"""

import json

import pytest

from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.traditional_metrics import TraditionalMetricsEngine


@pytest.fixture(autouse=True)
def _reset_bertscore_cache():
    """Force Levenshtein fallback to avoid BERTScore model download in normal test runs.

    BERTScore lazy-loads a HuggingFace model (distilbert-base-uncased) on first use.
    This autouse fixture disables that for all evals/ tests. BERTScore-specific behavior
    is tested with proper mocks in TestBERTScoreReenablement (which resets _init_failed=False).
    """
    TraditionalMetricsEngine._bertscore_instance = None
    TraditionalMetricsEngine._bertscore_init_failed = True
    yield
    TraditionalMetricsEngine._bertscore_instance = None
    TraditionalMetricsEngine._bertscore_init_failed = False


@pytest.fixture
def pipeline():
    """EvaluationPipeline instance with default settings.

    Returns:
        EvaluationPipeline: Default pipeline for testing.
    """
    return EvaluationPipeline()


@pytest.fixture
def sample_config():
    """Sample configuration dict for pipeline testing.

    Returns:
        dict: Nested config structure matching pipeline config schema.
    """
    return {
        "version": "1.0.0",
        "evaluation_system": {
            "tiers_enabled": [1, 2, 3],
            "performance_targets": {
                "tier1_max_seconds": 1.0,
                "tier2_max_seconds": 10.0,
                "tier3_max_seconds": 15.0,
                "total_max_seconds": 25.0,
            },
        },
        "tier1_traditional": {
            "similarity_metrics": ["cosine", "jaccard", "semantic"],
            "confidence_threshold": 0.8,
        },
        "tier2_llm_judge": {
            "model": "gpt-4o-mini",
            "max_retries": 2,
            "timeout_seconds": 30.0,
        },
        "tier3_graph": {
            "min_nodes_for_analysis": 2,
            "centrality_measures": ["betweenness", "closeness", "degree"],
        },
        "composite_scoring": {
            "metrics_and_weights": {
                "time_taken": 0.167,
                "task_success": 0.167,
                "coordination_quality": 0.167,
                "tool_efficiency": 0.167,
                "planning_rationality": 0.167,
                "output_similarity": 0.167,
            },
            "recommendation_thresholds": {
                "accept": 0.8,
                "weak_accept": 0.6,
                "weak_reject": 0.4,
                "reject": 0.0,
            },
            "recommendation_weights": {
                "accept": 1.0,
                "weak_accept": 0.7,
                "weak_reject": -0.7,
                "reject": -1.0,
            },
            "fallback_strategy": "tier1_only",
        },
    }


@pytest.fixture
def config_file(tmp_path, sample_config):
    """Temporary configuration file for testing using tmp_path.

    Args:
        tmp_path: Pytest tmp_path fixture for automatic cleanup.
        sample_config: Sample configuration dict.

    Returns:
        Path: Path to the temporary config JSON file.
    """
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(sample_config))
    return config_path
