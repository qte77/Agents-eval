"""
Tests for judge/evaluation_runner.py — evaluation orchestration extracted from app.py.

Unit tests for build_graph_from_trace, run_evaluation_if_enabled,
and run_baseline_comparisons in isolation from the main entry point.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import networkx as nx
import pytest

from app.data_models.evaluation_models import CompositeResult

# MARK: --- build_graph_from_trace ---


class TestBuildGraphFromTrace:
    """Tests for build_graph_from_trace function."""

    def test_returns_none_when_execution_id_is_none(self):
        """No graph should be built when execution_id is None."""
        from app.judge.evaluation_runner import build_graph_from_trace

        result = build_graph_from_trace(None)
        assert result is None

    def test_returns_none_when_execution_id_is_empty(self):
        """No graph should be built when execution_id is empty string."""
        from app.judge.evaluation_runner import build_graph_from_trace

        result = build_graph_from_trace("")
        assert result is None

    def test_returns_none_when_trace_not_found(self):
        """Returns None when trace collector has no data for execution_id."""
        with patch("app.judge.trace_processors.get_trace_collector") as mock_get:
            mock_collector = MagicMock()
            mock_collector.load_trace.return_value = None
            mock_get.return_value = mock_collector

            from app.judge.evaluation_runner import build_graph_from_trace

            result = build_graph_from_trace("missing-exec-id")
            assert result is None

    def test_returns_graph_when_trace_found(self):
        """Returns a DiGraph when trace data is available."""
        mock_graph = nx.DiGraph()
        mock_graph.add_node("manager")
        mock_graph.add_node("researcher")
        mock_graph.add_edge("manager", "researcher")

        with (
            patch("app.judge.trace_processors.get_trace_collector") as mock_get,
            patch("app.judge.evaluation_runner.build_interaction_graph", return_value=mock_graph),
        ):
            mock_collector = MagicMock()
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            from app.judge.evaluation_runner import build_graph_from_trace

            result = build_graph_from_trace("exec-123")
            assert result is not None
            assert isinstance(result, nx.DiGraph)
            assert result.number_of_nodes() == 2


# MARK: --- run_evaluation_if_enabled ---


class TestRunEvaluationIfEnabled:
    """Tests for run_evaluation_if_enabled function."""

    @pytest.mark.asyncio
    async def test_returns_none_when_skip_eval_true(self):
        """Evaluation must be skipped when skip_eval=True."""
        from app.judge.evaluation_runner import run_evaluation_if_enabled

        result = await run_evaluation_if_enabled(
            skip_eval=True,
            paper_number=None,
            execution_id=None,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_calls_evaluate_comprehensive_when_enabled(self):
        """EvaluationPipeline.evaluate_comprehensive must be called when not skipped."""
        mock_result = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={"test": 0.8},
            tier1_score=0.8,
            tier2_score=0.0,
            tier3_score=0.0,
            evaluation_complete=True,
        )
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock()
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            result = await run_evaluation_if_enabled(
                skip_eval=False,
                paper_number=None,
                execution_id=None,
            )

            mock_pipeline.evaluate_comprehensive.assert_called_once()
            assert result is mock_result

    @pytest.mark.asyncio
    async def test_passes_chat_provider_to_pipeline(self):
        """chat_provider must be forwarded to EvaluationPipeline constructor."""
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock()
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_number=None,
                execution_id=None,
                chat_provider="cerebras",
            )

            mock_pipeline_class.assert_called_once_with(settings=None, chat_provider="cerebras")

    @pytest.mark.asyncio
    async def test_loads_trace_when_execution_id_provided(self):
        """Trace data must be loaded and passed to evaluate_comprehensive."""
        mock_trace = MagicMock()
        mock_trace.agent_interactions = [{"from": "a", "to": "b"}]
        mock_trace.tool_calls = [{"tool": "t"}]

        with (
            patch("app.judge.trace_processors.get_trace_collector") as mock_get,
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        ):
            mock_collector = MagicMock()
            mock_collector.load_trace.return_value = mock_trace
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock()
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_number="001",
                execution_id="exec-123",
            )

            mock_collector.load_trace.assert_called_once_with("exec-123")
            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["execution_trace"] is mock_trace


# MARK: --- run_baseline_comparisons ---


class TestRunBaselineComparisons:
    """Tests for run_baseline_comparisons function."""

    @pytest.mark.asyncio
    async def test_returns_early_when_no_cc_dirs(self):
        """No comparisons when neither cc_solo_dir nor cc_teams_dir provided."""
        with patch("app.judge.evaluation_runner.compare_all") as mock_compare:
            from app.judge.evaluation_runner import run_baseline_comparisons

            pipeline = MagicMock()
            await run_baseline_comparisons(pipeline, None, None, None, None)
            mock_compare.assert_not_called()

    @pytest.mark.asyncio
    async def test_evaluates_solo_baseline(self, tmp_path):
        """Solo baseline must be evaluated when cc_solo_dir is provided."""
        mock_result = CompositeResult(
            composite_score=0.7,
            recommendation="accept",
            recommendation_weight=0.7,
            metric_scores={},
            tier1_score=0.7,
            tier2_score=0.0,
            tier3_score=0.0,
            evaluation_complete=True,
        )
        with (
            patch("app.judge.evaluation_runner.CCTraceAdapter") as mock_adapter_class,
            patch("app.judge.evaluation_runner.compare_all", return_value=[]),
        ):
            mock_adapter = MagicMock()
            mock_adapter.parse.return_value = MagicMock()
            mock_adapter_class.return_value = mock_adapter

            from app.judge.evaluation_runner import run_baseline_comparisons

            pipeline = MagicMock()
            pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)

            await run_baseline_comparisons(pipeline, None, str(tmp_path / "solo"), None, None)

            mock_adapter_class.assert_called_once()
            assert pipeline.evaluate_comprehensive.call_count == 1

    @pytest.mark.asyncio
    async def test_handles_solo_baseline_exception_gracefully(self, tmp_path):
        """Exceptions from solo baseline evaluation must be caught and logged."""
        with (
            patch(
                "app.judge.evaluation_runner.CCTraceAdapter", side_effect=Exception("parse error")
            ),
            patch("app.judge.evaluation_runner.compare_all", return_value=[]),
            patch("app.judge.evaluation_runner.logger") as mock_logger,
        ):
            from app.judge.evaluation_runner import run_baseline_comparisons

            pipeline = MagicMock()
            await run_baseline_comparisons(pipeline, None, str(tmp_path / "solo"), None, None)

            mock_logger.warning.assert_called_once()
            assert "parse error" in str(mock_logger.warning.call_args)


# MARK: --- paper and review extraction (STORY-005) ---


class TestPaperAndReviewExtraction:
    """Tests for paper and review content extraction in evaluation runner."""

    @pytest.mark.asyncio
    async def test_passes_non_empty_review_when_manager_output_contains_review(self):
        """Review text must be extracted from ReviewGenerationResult and passed to evaluate_comprehensive."""
        from app.data_models.peerread_models import GeneratedReview, ReviewGenerationResult

        mock_review = GeneratedReview(
            impact=4,
            substance=4,
            appropriateness=5,
            meaningful_comparison=4,
            presentation_format="Oral",
            comments="This is a detailed review with contributions, strengths, weaknesses, technical analysis, and clarity assessment.",
            soundness_correctness=4,
            originality=5,
            recommendation=4,
            clarity=4,
            reviewer_confidence=4,
        )
        mock_manager_output = ReviewGenerationResult(
            paper_id="001",
            review=mock_review,
            timestamp="2024-01-01T00:00:00Z",
            model_info="test-model",
        )

        with (
            patch("app.judge.trace_processors.get_trace_collector") as mock_get,
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        ):
            mock_collector = MagicMock()
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock()
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_number="001",
                execution_id="exec-123",
                manager_output=mock_manager_output,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["review"] != ""
            assert "detailed review" in call_kwargs["review"]

    @pytest.mark.asyncio
    async def test_passes_non_empty_paper_when_paper_id_provided(self):
        """Paper content must be loaded via PeerReadLoader and passed to evaluate_comprehensive."""
        from app.data_models.peerread_models import GeneratedReview, ReviewGenerationResult

        mock_review = GeneratedReview(
            impact=4,
            substance=4,
            appropriateness=5,
            meaningful_comparison=4,
            presentation_format="Oral",
            comments="This is a detailed review with contributions, strengths, weaknesses, technical analysis, and clarity assessment.",
            soundness_correctness=4,
            originality=5,
            recommendation=4,
            clarity=4,
            reviewer_confidence=4,
        )
        mock_manager_output = ReviewGenerationResult(
            paper_id="001",
            review=mock_review,
            timestamp="2024-01-01T00:00:00Z",
            model_info="test-model",
        )

        with (
            patch("app.judge.trace_processors.get_trace_collector") as mock_get,
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.data_utils.datasets_peerread.PeerReadLoader") as mock_loader_class,
        ):
            mock_collector = MagicMock()
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock()
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            # Mock PeerReadLoader to return paper content
            mock_loader = MagicMock()
            mock_loader.load_parsed_pdf_content.return_value = "Full paper content from PDF"
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_number="001",
                execution_id="exec-123",
                manager_output=mock_manager_output,
            )

            mock_loader.load_parsed_pdf_content.assert_called_once_with("001")
            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["paper"] != ""
            assert "Full paper content" in call_kwargs["paper"]

    @pytest.mark.asyncio
    async def test_falls_back_to_abstract_when_pdf_unavailable(self):
        """Paper abstract must be used as fallback when parsed PDF is unavailable."""
        from app.data_models.peerread_models import GeneratedReview, ReviewGenerationResult

        mock_review = GeneratedReview(
            impact=4,
            substance=4,
            appropriateness=5,
            meaningful_comparison=4,
            presentation_format="Oral",
            comments="This is a detailed review with contributions, strengths, weaknesses, technical analysis, and clarity assessment.",
            soundness_correctness=4,
            originality=5,
            recommendation=4,
            clarity=4,
            reviewer_confidence=4,
        )
        mock_manager_output = ReviewGenerationResult(
            paper_id="001",
            review=mock_review,
            timestamp="2024-01-01T00:00:00Z",
            model_info="test-model",
        )

        with (
            patch("app.judge.trace_processors.get_trace_collector") as mock_get,
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.data_utils.datasets_peerread.PeerReadLoader") as mock_loader_class,
        ):
            mock_collector = MagicMock()
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock()
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            # Mock PeerReadLoader to return None for PDF, then paper with abstract
            mock_loader = MagicMock()
            mock_loader.load_parsed_pdf_content.return_value = None
            mock_paper = MagicMock()
            mock_paper.abstract = "This is the paper abstract as fallback content."
            mock_loader.get_paper_by_id.return_value = mock_paper
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_number="001",
                execution_id="exec-123",
                manager_output=mock_manager_output,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["paper"] != ""
            assert "paper abstract as fallback" in call_kwargs["paper"]

    @pytest.mark.asyncio
    async def test_passes_empty_strings_when_no_manager_output(self):
        """Empty strings must be passed when manager_output is None (preserves current behavior)."""
        with (
            patch("app.judge.trace_processors.get_trace_collector") as mock_get,
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        ):
            mock_collector = MagicMock()
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock()
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_number=None,
                execution_id="exec-123",
                manager_output=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["paper"] == ""
            assert call_kwargs["review"] == ""
