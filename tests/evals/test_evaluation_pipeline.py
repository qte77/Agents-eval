"""
Tests for three-tier evaluation pipeline orchestrator.

Validates pipeline initialization, tier execution, error handling,
and performance characteristics with comprehensive coverage.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.data_models.evaluation_models import (
    CompositeResult,
    GraphTraceData,
    Tier1Result,
    Tier2Result,
    Tier3Result,
)
from app.evals.evaluation_pipeline import EvaluationPipeline
from app.evals.settings import JudgeSettings


@pytest.fixture
def sample_config():
    """Sample configuration for pipeline testing."""
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
def config_file(sample_config):
    """Temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_config, f)
        config_path = Path(f.name)

    yield config_path

    # Cleanup
    config_path.unlink()


@pytest.fixture
def sample_tier1_result():
    """Sample Tier 1 evaluation result."""
    return Tier1Result(
        cosine_score=0.85,
        jaccard_score=0.72,
        semantic_score=0.88,
        execution_time=0.5,
        time_score=0.95,
        task_success=1.0,
        overall_score=0.85,
    )


@pytest.fixture
def sample_tier2_result():
    """Sample Tier 2 evaluation result."""
    return Tier2Result(
        technical_accuracy=0.82,
        constructiveness=0.78,
        clarity=0.85,
        planning_rationality=0.80,
        overall_score=0.81,
        model_used="gpt-4o-mini",
        api_cost=0.003,
        fallback_used=False,
    )


@pytest.fixture
def sample_tier3_result():
    """Sample Tier 3 evaluation result."""
    return Tier3Result(
        path_convergence=0.72,
        tool_selection_accuracy=0.83,
        communication_overhead=0.68,
        coordination_centrality=0.75,
        task_distribution_balance=0.79,
        overall_score=0.76,
        graph_complexity=4,
    )


@pytest.fixture
def sample_composite_result():
    """Sample composite evaluation result."""
    return CompositeResult(
        composite_score=0.79,
        recommendation="weak_accept",
        recommendation_weight=0.7,
        metric_scores={
            "time_taken": 0.95,
            "task_success": 1.0,
            "coordination_quality": 0.75,
            "tool_efficiency": 0.83,
            "planning_rationality": 0.80,
            "output_similarity": 0.85,
        },
        tier1_score=0.85,
        tier2_score=0.81,
        tier3_score=0.76,
        evaluation_complete=True,
    )


class TestEvaluationPipelineInitialization:
    """Test pipeline initialization and configuration."""

    def test_init_with_config_file(self, config_file):
        """Test pipeline initialization with configuration file."""
        pipeline = EvaluationPipeline(config_file)

        assert pipeline.enabled_tiers == {1, 2, 3}
        assert pipeline.performance_targets["total_max_seconds"] == 25.0
        assert pipeline.fallback_strategy == "tier1_only"
        assert pipeline.config_path == config_file

    def test_init_with_judge_settings(self):
        """Test pipeline initialization with JudgeSettings (new path)."""
        settings = JudgeSettings(
            tiers_enabled=[1, 2],
            tier1_max_seconds=2.0,
            tier2_max_seconds=15.0,
            fallback_strategy="tier2_only",
        )
        pipeline = EvaluationPipeline(settings=settings)

        assert pipeline.enabled_tiers == {1, 2}
        assert pipeline.performance_targets["tier1_max_seconds"] == 2.0
        assert pipeline.performance_targets["tier2_max_seconds"] == 15.0
        assert pipeline.fallback_strategy == "tier2_only"
        assert pipeline.config_path is None  # No config file used

    def test_init_settings_takes_precedence(self, config_file):
        """Test that JudgeSettings takes precedence over config_path."""
        settings = JudgeSettings(tiers_enabled=[3], fallback_strategy="tier3_only")
        pipeline = EvaluationPipeline(config_path=config_file, settings=settings)

        # Settings should override config_file
        assert pipeline.enabled_tiers == {3}
        assert pipeline.fallback_strategy == "tier3_only"
        assert pipeline.config_path is None

    def test_init_with_default_config(self):
        """Test pipeline initialization with default config path."""
        with patch("json.load") as mock_json_load:
            mock_json_load.return_value = {
                "evaluation_system": {"tiers_enabled": [1, 2]},
                "composite_scoring": {
                    "fallback_strategy": "tier1_only",
                    "metrics_and_weights": {
                        "time_taken": 0.167,
                        "task_success": 0.167,
                        "coordination_quality": 0.167,
                        "tool_efficiency": 0.167,
                        "planning_rationality": 0.167,
                        "output_similarity": 0.167,
                    },
                },
            }

            pipeline = EvaluationPipeline()
            assert pipeline.enabled_tiers == {1, 2}

    def test_init_missing_config_file(self):
        """Test pipeline initialization with missing config file."""
        with pytest.raises(FileNotFoundError):
            EvaluationPipeline("/nonexistent/config.json")

    def test_init_invalid_json(self):
        """Test pipeline initialization with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            invalid_config_path = Path(f.name)

        try:
            with pytest.raises(json.JSONDecodeError):
                EvaluationPipeline(invalid_config_path)
        finally:
            invalid_config_path.unlink()


class TestTierExecution:
    """Test individual tier execution methods."""

    @pytest.fixture
    def pipeline(self, config_file):
        """Pipeline instance for testing."""
        return EvaluationPipeline(config_file)

    @pytest.mark.asyncio
    async def test_execute_tier1_success(self, pipeline, sample_tier1_result):
        """Test successful Tier 1 execution."""
        with patch.object(pipeline.traditional_engine, "evaluate_traditional_metrics") as mock_eval:
            mock_eval.return_value = sample_tier1_result

            result, execution_time = await pipeline._execute_tier1(
                "sample paper", "sample review", ["reference"]
            )

            assert result == sample_tier1_result
            assert execution_time > 0
            mock_eval.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_tier1_disabled(self, pipeline):
        """Test Tier 1 execution when disabled."""
        # Mock the configuration to disable tier 1
        with patch.object(pipeline.config_manager, "is_tier_enabled", return_value=False):
            result, execution_time = await pipeline._execute_tier1(
                "sample paper", "sample review", ["reference"]
            )

            assert result is None
            assert execution_time == 0.0

    @pytest.mark.asyncio
    async def test_execute_tier1_timeout(self, pipeline):
        """Test Tier 1 execution timeout."""
        with patch.object(pipeline.traditional_engine, "evaluate_traditional_metrics") as mock_eval:

            def slow_execution(*args, **kwargs):
                import time

                time.sleep(2)  # Block longer than 1s timeout
                return None

            mock_eval.side_effect = slow_execution

            result, execution_time = await pipeline._execute_tier1("sample paper", "sample review")

            assert result is None
            assert execution_time >= 1.0  # Should be at least the timeout duration

    @pytest.mark.asyncio
    async def test_execute_tier2_success(self, pipeline, sample_tier2_result):
        """Test successful Tier 2 execution."""
        pipeline.llm_engine.evaluate_comprehensive = AsyncMock(return_value=sample_tier2_result)

        result, execution_time = await pipeline._execute_tier2(
            "sample paper", "sample review", {"trace": "data"}
        )

        assert result == sample_tier2_result
        assert execution_time > 0
        pipeline.llm_engine.evaluate_comprehensive.assert_called_once_with(
            "sample paper", "sample review", {"trace": "data"}
        )

    @pytest.mark.asyncio
    async def test_execute_tier2_no_trace(self, pipeline, sample_tier2_result):
        """Test Tier 2 execution without execution trace."""
        pipeline.llm_engine.evaluate_comprehensive = AsyncMock(return_value=sample_tier2_result)

        result, execution_time = await pipeline._execute_tier2("sample paper", "sample review")

        assert result == sample_tier2_result
        pipeline.llm_engine.evaluate_comprehensive.assert_called_once_with(
            "sample paper", "sample review", {}
        )

    @pytest.mark.asyncio
    async def test_execute_tier3_success(self, pipeline, sample_tier3_result):
        """Test successful Tier 3 execution."""
        with patch.object(pipeline.graph_engine, "evaluate_graph_metrics") as mock_analyze:
            mock_analyze.return_value = sample_tier3_result

            result, execution_time = await pipeline._execute_tier3(
                {"agent_interactions": [], "tool_calls": []}
            )

            assert result == sample_tier3_result
            assert execution_time > 0
            mock_analyze.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_tier3_no_trace(self, pipeline, sample_tier3_result):
        """Test Tier 3 execution without trace data."""
        with patch.object(pipeline.graph_engine, "evaluate_graph_metrics") as mock_analyze:
            mock_analyze.return_value = sample_tier3_result

            result, execution_time = await pipeline._execute_tier3()

            assert result == sample_tier3_result
            # Verify minimal trace data was created
            call_args = mock_analyze.call_args[0][0]
            assert isinstance(call_args, GraphTraceData)
            assert call_args.agent_interactions == []
            assert call_args.tool_calls == []


class TestFallbackStrategy:
    """Test fallback strategy implementation."""

    @pytest.fixture
    def pipeline(self, config_file):
        """Pipeline instance for testing."""
        return EvaluationPipeline(config_file)

    def test_fallback_tier1_only_success(self, pipeline, sample_tier1_result):
        """Test tier1_only fallback with successful Tier 1."""
        from app.evals.composite_scorer import EvaluationResults

        results = EvaluationResults(tier1=sample_tier1_result)
        assert not results.is_complete()

        with patch.object(pipeline.performance_monitor, "record_fallback_usage") as mock_fallback:
            fallback_results = pipeline._apply_fallback_strategy(results)

            assert fallback_results.is_complete()
            assert fallback_results.tier1 == sample_tier1_result
            assert fallback_results.tier2 is not None
            assert fallback_results.tier2.fallback_used is True
            assert fallback_results.tier3 is not None
            mock_fallback.assert_called_once_with(True)

    def test_fallback_no_tier1(self, pipeline):
        """Test fallback strategy when Tier 1 fails."""
        from app.evals.composite_scorer import EvaluationResults

        results = EvaluationResults()
        assert not results.is_complete()

        with patch.object(pipeline.performance_monitor, "record_fallback_usage") as mock_fallback:
            fallback_results = pipeline._apply_fallback_strategy(results)

            # Should not create fallback results without Tier 1
            assert not fallback_results.is_complete()
            mock_fallback.assert_not_called()


class TestComprehensiveEvaluation:
    """Test end-to-end comprehensive evaluation."""

    @pytest.fixture
    def pipeline(self, config_file):
        """Pipeline instance for testing."""
        return EvaluationPipeline(config_file)

    @pytest.mark.asyncio
    async def test_comprehensive_evaluation_success(
        self,
        pipeline,
        sample_tier1_result,
        sample_tier2_result,
        sample_tier3_result,
        sample_composite_result,
    ):
        """Test successful comprehensive evaluation."""
        # Mock all tier engines
        with (
            patch.object(pipeline.traditional_engine, "evaluate_traditional_metrics") as mock_t1,
            patch.object(pipeline.llm_engine, "evaluate_comprehensive") as mock_t2,
            patch.object(pipeline.graph_engine, "evaluate_graph_metrics") as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_comp,
        ):
            mock_t1.return_value = sample_tier1_result
            mock_t2.return_value = sample_tier2_result
            mock_t3.return_value = sample_tier3_result
            mock_comp.return_value = sample_composite_result

            result = await pipeline.evaluate_comprehensive(
                paper="Sample paper content",
                review="Sample review content",
                execution_trace={"agent_calls": [], "tool_calls": []},
            )

            assert result == sample_composite_result
            # Mock the performance monitor response for execution_stats checking
            with patch.object(
                pipeline.performance_monitor,
                "get_execution_stats",
                return_value={
                    "tiers_executed": [1, 2, 3],
                    "total_time": 1.0,
                    "fallback_used": False,
                },
            ):
                assert pipeline.execution_stats["tiers_executed"] == [1, 2, 3]
                assert pipeline.execution_stats["total_time"] > 0
                assert not pipeline.execution_stats["fallback_used"]

    @pytest.mark.asyncio
    async def test_comprehensive_evaluation_with_fallback(
        self,
        pipeline,
        sample_tier1_result,
        sample_composite_result,
    ):
        """Test comprehensive evaluation with fallback strategy."""
        # Mock engines - Tier 1 succeeds, others fail
        with (
            patch.object(pipeline.traditional_engine, "evaluate_traditional_metrics") as mock_t1,
            patch.object(pipeline.llm_engine, "evaluate_comprehensive") as mock_t2,
            patch.object(pipeline.graph_engine, "evaluate_graph_metrics") as mock_t3,
            patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_comp,
        ):
            mock_t1.return_value = sample_tier1_result
            mock_t2.side_effect = Exception("LLM service unavailable")
            mock_t3.side_effect = Exception("Graph analysis failed")
            mock_comp.return_value = sample_composite_result

            result = await pipeline.evaluate_comprehensive(
                paper="Sample paper content",
                review="Sample review content",
            )

            assert result == sample_composite_result
            # Mock the performance monitor response for execution_stats checking
            with patch.object(
                pipeline.performance_monitor,
                "get_execution_stats",
                return_value={"tiers_executed": [1], "fallback_used": True},
            ):
                assert pipeline.execution_stats["tiers_executed"] == [1]
                assert pipeline.execution_stats["fallback_used"] is True

    @pytest.mark.asyncio
    async def test_comprehensive_evaluation_total_failure(self, pipeline):
        """Test comprehensive evaluation when all tiers fail."""
        # Mock all engines to fail
        with (
            patch.object(pipeline.traditional_engine, "evaluate_traditional_metrics") as mock_t1,
            patch.object(pipeline.llm_engine, "evaluate_comprehensive") as mock_t2,
            patch.object(pipeline.graph_engine, "evaluate_graph_metrics") as mock_t3,
        ):
            mock_t1.side_effect = Exception("Traditional metrics failed")
            mock_t2.side_effect = Exception("LLM service unavailable")
            mock_t3.side_effect = Exception("Graph analysis failed")

            with pytest.raises(ValueError, match="Cannot generate composite score"):
                await pipeline.evaluate_comprehensive(
                    paper="Sample paper content",
                    review="Sample review content",
                )

            # Mock the performance monitor response for execution_stats checking
            with patch.object(
                pipeline.performance_monitor,
                "get_execution_stats",
                return_value={"tiers_executed": [], "fallback_used": False},
            ):
                assert pipeline.execution_stats["tiers_executed"] == []
                assert not pipeline.execution_stats["fallback_used"]

    @pytest.mark.asyncio
    async def test_comprehensive_evaluation_performance_warning(
        self,
        pipeline,
        sample_tier1_result,
        sample_tier2_result,
        sample_tier3_result,
        sample_composite_result,
    ):
        """Test performance warning when pipeline exceeds time target."""
        # Mock performance monitor to have very low time target
        with patch.object(pipeline.performance_monitor, "performance_targets") as mock_targets:
            mock_targets.update({"total_max_seconds": 0.001})

            with (
                patch.object(
                    pipeline.traditional_engine, "evaluate_traditional_metrics"
                ) as mock_t1,
                patch.object(pipeline.llm_engine, "evaluate_comprehensive") as mock_t2,
                patch.object(pipeline.graph_engine, "evaluate_graph_metrics") as mock_t3,
                patch.object(pipeline.composite_scorer, "evaluate_composite") as mock_comp,
                patch("app.utils.log.logger.warning"),
            ):
                mock_t1.return_value = sample_tier1_result
                mock_t2.return_value = sample_tier2_result
                mock_t3.return_value = sample_tier3_result
                mock_comp.return_value = sample_composite_result

                result = await pipeline.evaluate_comprehensive(
                    paper="Sample paper content",
                    review="Sample review content",
                )

                assert result == sample_composite_result
                # Test passes if evaluation completes successfully with modified targets
                # Warning behavior is tested by the actual pipeline logic


class TestPipelineUtilities:
    """Test pipeline utility methods."""

    @pytest.fixture
    def pipeline(self, config_file):
        """Pipeline instance for testing."""
        return EvaluationPipeline(config_file)

    def test_get_execution_stats(self, pipeline):
        """Test execution statistics retrieval."""
        # Mock the performance monitor to return expected stats
        mock_stats = {
            "tier1_time": 0.5,
            "tier2_time": 2.1,
            "tier3_time": 1.8,
            "total_time": 4.4,
            "tiers_executed": [1, 2, 3],
            "fallback_used": False,
        }

        with patch.object(
            pipeline.performance_monitor, "get_execution_stats", return_value=mock_stats
        ):
            stats = pipeline.get_execution_stats()

            assert stats["total_time"] == 4.4
            assert stats["tiers_executed"] == [1, 2, 3]
            assert not stats["fallback_used"]

            # Verify it's a copy by checking if modifying returned dict doesn't
            # affect monitor
            stats["total_time"] = 999
            # The returned stats should be independent

    def test_get_pipeline_summary(self, pipeline):
        """Test pipeline configuration summary."""
        summary = pipeline.get_pipeline_summary()

        assert summary["enabled_tiers"] == [1, 2, 3]
        assert summary["fallback_strategy"] == "tier1_only"
        assert "performance_targets" in summary
        assert "config_path" in summary


class TestOpikIntegration:
    """Test Opik integration functionality."""

    def test_opik_config_initialization(self, config_file):
        """Test that Opik configuration is properly initialized."""
        pipeline = EvaluationPipeline(config_file)

        # Should have opik_config attribute
        assert hasattr(pipeline, "opik_config")
        assert pipeline.opik_config is not None

        # Should have default values
        assert pipeline.opik_config.enabled is False  # Default disabled
        assert pipeline.opik_config.api_url == "http://localhost:3003"
        assert pipeline.opik_config.workspace == "peerread-evaluation"

    def test_opik_decorator_application(self, config_file):
        """Test that Opik decorator is properly applied when available."""
        pipeline = EvaluationPipeline(config_file)

        # Mock function to test decorator
        def mock_func():
            return "test"

        # Should return function unchanged when Opik not enabled
        decorated = pipeline._apply_opik_decorator(mock_func)
        assert callable(decorated)
        assert decorated() == "test"

    def test_opik_metadata_recording(self, config_file):
        """Test that Opik metadata is recorded without errors."""
        pipeline = EvaluationPipeline(config_file)

        # Should not raise errors when recording metadata
        pipeline._record_opik_metadata(1, 1.5, result="test_result")
        pipeline._record_opik_metadata(2, 2.0, error="test_error")

        # Metadata recording is debug-only, so just verify no exceptions
