"""
Tests for judge/evaluation_runner.py — evaluation orchestration extracted from app.py.

Unit tests for build_graph_from_trace, run_evaluation_if_enabled,
and run_baseline_comparisons in isolation from the main entry point.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import networkx as nx
import pytest

from app.data_models.evaluation_models import CompositeResult, GraphTraceData
from app.data_models.peerread_models import PeerReadPaper, PeerReadReview
from app.data_utils.datasets_peerread import PeerReadLoader
from app.judge.cc_trace_adapter import CCTraceAdapter
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.trace_processors import TraceCollector
from app.utils.artifact_registry import ArtifactRegistry

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
            mock_collector = MagicMock(spec=TraceCollector)
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
            mock_collector = MagicMock(spec=TraceCollector)
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
            paper_id=None,
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
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            result = await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
            )

            mock_pipeline.evaluate_comprehensive.assert_called_once()
            assert result is mock_result

    @pytest.mark.asyncio
    async def test_passes_chat_provider_to_pipeline(self):
        """chat_provider must be forwarded to EvaluationPipeline constructor."""
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                chat_provider="cerebras",
            )

            mock_pipeline_class.assert_called_once_with(
                settings=None, chat_provider="cerebras", chat_model=None
            )

    @pytest.mark.asyncio
    async def test_loads_trace_when_execution_id_provided(self):
        """Trace data must be loaded and passed to evaluate_comprehensive."""
        mock_trace = MagicMock(spec=GraphTraceData)
        mock_trace.agent_interactions = [{"from": "a", "to": "b"}]
        mock_trace.tool_calls = [{"tool": "t"}]

        with (
            patch("app.judge.trace_processors.get_trace_collector") as mock_get,
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
        ):
            mock_collector = MagicMock(spec=TraceCollector)
            mock_collector.load_trace.return_value = mock_trace
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="001",
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

            pipeline = MagicMock(spec=EvaluationPipeline)
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
            mock_adapter = MagicMock(spec=CCTraceAdapter)
            mock_adapter.parse.return_value = MagicMock()
            mock_adapter_class.return_value = mock_adapter

            from app.judge.evaluation_runner import run_baseline_comparisons

            pipeline = MagicMock(spec=EvaluationPipeline)
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

            pipeline = MagicMock(spec=EvaluationPipeline)
            await run_baseline_comparisons(pipeline, None, str(tmp_path / "solo"), None, None)

            mock_logger.warning.assert_called_once()
            assert "parse error" in str(mock_logger.warning.call_args)


# MARK: --- CompositeResult.engine_type (STORY-010) ---


class TestCompositeResultEngineType:
    """Tests for CompositeResult.engine_type field."""

    def test_default_engine_type_is_mas(self):
        """CompositeResult defaults to engine_type='mas'."""
        result = CompositeResult(
            composite_score=0.5,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.0,
            evaluation_complete=True,
        )
        assert result.engine_type == "mas"

    def test_engine_type_cc_solo(self):
        """CompositeResult accepts engine_type='cc_solo'."""
        result = CompositeResult(
            composite_score=0.5,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.0,
            evaluation_complete=True,
            engine_type="cc_solo",
        )
        assert result.engine_type == "cc_solo"

    def test_engine_type_cc_teams(self):
        """CompositeResult accepts engine_type='cc_teams'."""
        result = CompositeResult(
            composite_score=0.5,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.0,
            evaluation_complete=True,
            engine_type="cc_teams",
        )
        assert result.engine_type == "cc_teams"


# MARK: --- reference reviews loading (STORY-010) ---


class TestReferenceReviewsLoading:
    """Tests for _load_reference_reviews in evaluation_runner."""

    @pytest.mark.asyncio
    async def test_loads_reference_reviews_when_paper_id_set(self):
        """reference_reviews populated from PeerRead when paper_id is set."""
        mock_paper = MagicMock(spec=PeerReadPaper)
        mock_review_1 = MagicMock(spec=PeerReadReview)
        mock_review_1.comments = "Ground truth review one"
        mock_review_2 = MagicMock(spec=PeerReadReview)
        mock_review_2.comments = "Ground truth review two"
        mock_paper.reviews = [mock_review_1, mock_review_2]

        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.evaluation_runner.PeerReadLoader") as mock_loader_class,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.get_paper_by_id.return_value = mock_paper
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="001",
                execution_id=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["reference_reviews"] is not None
            assert len(call_kwargs["reference_reviews"]) == 2
            assert "Ground truth review one" in call_kwargs["reference_reviews"]

    @pytest.mark.asyncio
    async def test_reference_reviews_none_when_no_paper_id(self):
        """reference_reviews is None when paper_id is not set."""
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["reference_reviews"] is None

    @pytest.mark.asyncio
    async def test_reference_reviews_empty_when_paper_has_no_reviews(self):
        """reference_reviews is empty list when paper exists but has no reviews."""
        mock_paper = MagicMock(spec=PeerReadPaper)
        mock_paper.reviews = []

        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.evaluation_runner.PeerReadLoader") as mock_loader_class,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.get_paper_by_id.return_value = mock_paper
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="001",
                execution_id=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["reference_reviews"] == []


# MARK: --- execution_trace override for CC engine ---


class TestExecutionTraceOverride:
    """Verify run_evaluation_if_enabled accepts execution_trace that skips SQLite lookup."""

    @pytest.mark.asyncio
    async def test_uses_provided_execution_trace_skips_sqlite(self):
        """When execution_trace is provided, get_trace_collector must NOT be called."""
        provided_trace = GraphTraceData(
            execution_id="cc-trace-001",
            agent_interactions=[{"from": "cc_orchestrator", "to": "agent-1", "type": "delegation"}],
        )

        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.trace_processors.get_trace_collector") as mock_get_collector,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id="cc-trace-001",
                execution_trace=provided_trace,
            )

            mock_get_collector.assert_not_called()
            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["execution_trace"] is provided_trace

    @pytest.mark.asyncio
    async def test_falls_back_to_sqlite_when_no_override(self):
        """When execution_trace=None, get_trace_collector must be called (existing behavior)."""
        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.trace_processors.get_trace_collector") as mock_get_collector,
        ):
            mock_collector = MagicMock(spec=TraceCollector)
            mock_collector.load_trace.return_value = None
            mock_get_collector.return_value = mock_collector

            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id="exec-456",
                execution_trace=None,
            )

            mock_get_collector.assert_called_once()


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
            mock_collector = MagicMock(spec=TraceCollector)
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="001",
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
            mock_collector = MagicMock(spec=TraceCollector)
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            # Mock PeerReadLoader to return paper content
            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.load_parsed_pdf_content.return_value = "Full paper content from PDF"
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="001",
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
            mock_collector = MagicMock(spec=TraceCollector)
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            # Mock PeerReadLoader to return None for PDF, then paper with abstract
            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.load_parsed_pdf_content.return_value = None
            mock_paper = MagicMock()
            mock_paper.abstract = "This is the paper abstract as fallback content."
            mock_loader.get_paper_by_id.return_value = mock_paper
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="001",
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
            mock_collector = MagicMock(spec=TraceCollector)
            mock_collector.load_trace.return_value = MagicMock()
            mock_get.return_value = mock_collector

            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id="exec-123",
                manager_output=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["paper"] == ""
            assert call_kwargs["review"] == ""


# MARK: --- CC paper content loading (Gap 2) ---


class TestCCPaperContentLoading:
    """Verify paper content loaded from PeerRead when manager_output is None (CC path)."""

    @pytest.mark.asyncio
    async def test_loads_paper_from_peerread_when_manager_output_none(self):
        """paper_id set + manager_output=None → PeerReadLoader.load_parsed_pdf_content called."""
        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.evaluation_runner.PeerReadLoader") as mock_loader_class,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.load_parsed_pdf_content.return_value = "Full parsed PDF content"
            mock_loader.get_paper_by_id.return_value = None
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="1105.1072",
                execution_id=None,
                manager_output=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["paper"] == "Full parsed PDF content"

    @pytest.mark.asyncio
    async def test_abstract_fallback_when_pdf_unavailable(self):
        """PDF returns None → get_paper_by_id called, abstract used."""
        mock_paper = MagicMock(spec=PeerReadPaper)
        mock_paper.abstract = "Paper abstract as fallback"
        mock_paper.reviews = []

        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.evaluation_runner.PeerReadLoader") as mock_loader_class,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.load_parsed_pdf_content.return_value = None
            mock_loader.get_paper_by_id.return_value = mock_paper
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="1105.1072",
                execution_id=None,
                manager_output=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["paper"] == "Paper abstract as fallback"

    @pytest.mark.asyncio
    async def test_paper_stays_empty_when_paper_not_found(self):
        """Both loaders return None → paper == ''."""
        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.evaluation_runner.PeerReadLoader") as mock_loader_class,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.load_parsed_pdf_content.return_value = None
            mock_loader.get_paper_by_id.return_value = None
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="nonexistent",
                execution_id=None,
                manager_output=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["paper"] == ""

    @pytest.mark.asyncio
    async def test_mas_path_unaffected(self):
        """manager_output set → paper loaded via _extract_paper_and_review_content, not CC fallback."""
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
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.data_utils.datasets_peerread.PeerReadLoader") as mock_loader_class,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            mock_loader = MagicMock(spec=PeerReadLoader)
            mock_loader.load_parsed_pdf_content.return_value = "PDF from MAS path"
            mock_loader_class.return_value = mock_loader

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id="001",
                execution_id=None,
                manager_output=mock_manager_output,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            # MAS path extracts paper from manager_output via _extract_paper_and_review_content
            # The CC fallback should NOT be triggered since paper_content is non-empty
            assert call_kwargs["paper"] == "PDF from MAS path"


# MARK: --- review_text override for CC engine (STORY-010 AC2) ---


class TestReviewTextOverride:
    """Verify run_evaluation_if_enabled accepts review_text that overrides extraction."""

    def test_run_evaluation_if_enabled_accepts_review_text_parameter(self):
        """run_evaluation_if_enabled signature includes review_text parameter."""
        import inspect

        from app.judge.evaluation_runner import run_evaluation_if_enabled

        sig = inspect.signature(run_evaluation_if_enabled)
        assert "review_text" in sig.parameters, (
            "run_evaluation_if_enabled must accept 'review_text' parameter for CC review text"
        )

    @pytest.mark.asyncio
    async def test_review_text_override_passed_to_pipeline(self):
        """When review_text is provided, it is used instead of extracting from manager_output."""
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                manager_output=None,
                review_text="CC generated review text from solo mode",
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            assert call_kwargs["review"] == "CC generated review text from solo mode"

    @pytest.mark.asyncio
    async def test_review_text_none_falls_back_to_extraction(self):
        """When review_text is None, extraction from manager_output is used as before."""
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                manager_output=None,
                review_text=None,
            )

            call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs
            # Falls back to extraction which yields "" for None manager_output
            assert call_kwargs["review"] == ""


# MARK: --- evaluation.json persistence (STORY-010) ---


class TestEvaluationJsonPersistence:
    """Tests for persisting evaluation results to evaluation.json (STORY-010)."""

    @pytest.mark.asyncio
    async def test_writes_evaluation_json_when_result_and_run_dir(self, tmp_path):
        """AC1/AC2: evaluation.json written to run_dir with full CompositeResult."""
        mock_result = CompositeResult(
            composite_score=0.75,
            recommendation="weak_accept",
            recommendation_weight=0.6,
            metric_scores={"cosine": 0.8, "jaccard": 0.7},
            tier1_score=0.75,
            tier2_score=0.0,
            tier3_score=0.0,
            evaluation_complete=True,
        )
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            result = await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                run_dir=tmp_path,
            )

            assert result is mock_result
            eval_file = tmp_path / "evaluation.json"
            assert eval_file.exists(), "evaluation.json must be written to run_dir"

            import json

            data = json.loads(eval_file.read_text())
            assert data["composite_score"] == 0.75
            assert data["recommendation"] == "weak_accept"
            assert "metric_scores" in data

    @pytest.mark.asyncio
    async def test_no_evaluation_json_when_skip_eval(self, tmp_path):
        """AC3: evaluation.json must NOT be written when skip_eval=True."""
        from app.judge.evaluation_runner import run_evaluation_if_enabled

        await run_evaluation_if_enabled(
            skip_eval=True,
            paper_id=None,
            execution_id=None,
            run_dir=tmp_path,
        )

        eval_file = tmp_path / "evaluation.json"
        assert not eval_file.exists(), "evaluation.json must not be written when eval skipped"

    @pytest.mark.asyncio
    async def test_no_evaluation_json_when_run_dir_none(self):
        """evaluation.json must NOT be written when run_dir is None."""
        mock_result = CompositeResult(
            composite_score=0.5,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier2_score=0.0,
            tier3_score=0.0,
            evaluation_complete=True,
        )
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            # Should not raise — just skip writing
            result = await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                run_dir=None,
            )
            assert result is mock_result

    @pytest.mark.asyncio
    async def test_registers_artifact_in_registry(self, tmp_path):
        """AC4: ArtifactRegistry registers evaluation.json as 'Evaluation'."""
        mock_result = CompositeResult(
            composite_score=0.5,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier2_score=0.0,
            tier3_score=0.0,
            evaluation_complete=True,
        )
        with (
            patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class,
            patch("app.judge.evaluation_runner.get_artifact_registry") as mock_get_registry,
        ):
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
            mock_pipeline_class.return_value = mock_pipeline

            mock_registry = MagicMock(spec=ArtifactRegistry)
            mock_get_registry.return_value = mock_registry

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                run_dir=tmp_path,
            )

            mock_registry.register.assert_called_once()
            call_args = mock_registry.register.call_args
            assert call_args[0][0] == "Evaluation"
            assert "evaluation.json" in str(call_args[0][1])


    @pytest.mark.asyncio
    async def test_engine_type_persisted_in_evaluation_json(self, tmp_path):
        """engine_type passed to run_evaluation_if_enabled must appear in evaluation.json."""
        mock_result = CompositeResult(
            composite_score=0.6,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.6,
            tier2_score=0.0,
            tier3_score=0.0,
            evaluation_complete=True,
        )
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=mock_result)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            result = await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                run_dir=tmp_path,
                engine_type="cc_solo",
            )

            assert result is not None
            assert result.engine_type == "cc_solo"

            import json

            data = json.loads((tmp_path / "evaluation.json").read_text())
            assert data["engine_type"] == "cc_solo"


# MARK: --- chat_model threading to EvaluationPipeline ---


class TestChatModelThreading:
    """chat_model must reach EvaluationPipeline from run_evaluation_if_enabled."""

    @pytest.mark.asyncio
    async def test_chat_model_forwarded_to_pipeline(self):
        """chat_model must be forwarded to EvaluationPipeline constructor."""
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                chat_provider="anthropic",
                chat_model="claude-sonnet-4-20250514",
            )

            mock_pipeline_class.assert_called_once_with(
                settings=None, chat_provider="anthropic", chat_model="claude-sonnet-4-20250514"
            )

    @pytest.mark.asyncio
    async def test_chat_model_none_by_default(self):
        """chat_model defaults to None when not provided."""
        with patch("app.judge.evaluation_runner.EvaluationPipeline") as mock_pipeline_class:
            mock_pipeline = MagicMock(spec=EvaluationPipeline)
            mock_pipeline.evaluate_comprehensive = AsyncMock(return_value=None)
            mock_pipeline_class.return_value = mock_pipeline

            from app.judge.evaluation_runner import run_evaluation_if_enabled

            await run_evaluation_if_enabled(
                skip_eval=False,
                paper_id=None,
                execution_id=None,
                chat_provider="openai",
            )

            mock_pipeline_class.assert_called_once_with(
                settings=None, chat_provider="openai", chat_model=None
            )
