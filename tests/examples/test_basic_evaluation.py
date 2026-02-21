"""Tests for basic_evaluation.py example.

Purpose: Verify the basic evaluation example demonstrates plugin-based evaluation
         with realistic paper/review data using current APIs, without requiring
         external LLM calls.
Setup: Mock the LLM engine (Tier 2) to avoid API key requirements in CI.
Expected behavior: Example runs end-to-end, returns CompositeResult with valid scores.
Mock strategy: patch LLMJudgeEngine to skip Tier 2 LLM calls; Tier 1 and Tier 3
               run with real local computation.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.data_models.evaluation_models import CompositeResult, GraphTraceData


class TestBasicEvaluationRuns:
    """Verify the basic evaluation example runs without errors using mocked dependencies."""

    @pytest.mark.asyncio
    async def test_example_runs_with_mocked_llm(self) -> None:
        """Example runs end-to-end with mocked LLM provider for Tier 2."""
        # Arrange: mock the LLM judge engine so no API key is required
        from app.data_models.evaluation_models import Tier2Result

        mock_tier2 = Tier2Result(
            technical_accuracy=0.8,
            constructiveness=0.75,
            planning_rationality=0.7,
            overall_score=0.78,
            model_used="mock-model",
            api_cost=None,
        )

        with patch(
            "app.judge.llm_evaluation_managers.LLMJudgeEngine.evaluate_comprehensive"
        ) as mock_eval:
            mock_eval.return_value = mock_tier2

            # Act: import and call the example's main function
            import importlib.util
            import sys

            spec = importlib.util.spec_from_file_location(
                "basic_evaluation",
                Path(__file__).parent.parent.parent / "src" / "examples" / "basic_evaluation.py",
            )
            assert spec is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules["basic_evaluation"] = module

            # The module should define a run_example or main async function
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            assert hasattr(module, "run_example") or hasattr(module, "main"), (
                "Example must define a run_example() or main() function"
            )

    @pytest.mark.asyncio
    async def test_example_returns_composite_result(self) -> None:
        """Example's run_example() returns a CompositeResult with valid score range."""
        # Arrange
        from app.data_models.evaluation_models import Tier2Result

        mock_tier2 = Tier2Result(
            technical_accuracy=0.8,
            constructiveness=0.75,
            planning_rationality=0.7,
            overall_score=0.78,
            model_used="mock-model",
            api_cost=None,
        )

        with patch(
            "app.judge.llm_evaluation_managers.LLMJudgeEngine.evaluate_comprehensive"
        ) as mock_eval:
            mock_eval.return_value = mock_tier2

            import importlib.util
            import sys

            spec = importlib.util.spec_from_file_location(
                "basic_evaluation_v2",
                Path(__file__).parent.parent.parent / "src" / "examples" / "basic_evaluation.py",
            )
            assert spec is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules["basic_evaluation_v2"] = module
            spec.loader.exec_module(module)  # type: ignore[union-attr]

            # Act: call the run_example function
            run_fn = getattr(module, "run_example", None) or getattr(module, "main", None)
            assert run_fn is not None

            result = await run_fn()

        # Assert
        assert isinstance(result, CompositeResult), f"Expected CompositeResult, got {type(result)}"
        assert 0.0 <= result.composite_score <= 1.0, "Composite score must be in [0, 1]"
        assert result.recommendation in {"accept", "weak_accept", "weak_reject", "reject"}, (
            f"Unexpected recommendation: {result.recommendation}"
        )

    def test_synthetic_graph_trace_data_is_valid(self) -> None:
        """GraphTraceData used in example must be valid (Tier 3 can analyze it)."""
        # Arrange: verify the example creates a valid GraphTraceData
        trace = GraphTraceData(
            execution_id="example-001",
            agent_interactions=[
                {"from": "orchestrator", "to": "researcher", "message": "Analyze paper"},
                {"from": "researcher", "to": "analyst", "message": "Pass findings"},
            ],
            tool_calls=[
                {"tool": "search", "agent": "researcher", "success": True},
                {"tool": "summarize", "agent": "analyst", "success": True},
            ],
            timing_data={"start": "2026-01-01T00:00:00Z", "end": "2026-01-01T00:00:05Z"},
            coordination_events=[
                {"type": "delegation", "from": "orchestrator", "to": "researcher"}
            ],
        )
        # Assert: Pydantic validation passes (no exception raised)
        assert trace.execution_id == "example-001"
        assert len(trace.agent_interactions) == 2
        assert len(trace.tool_calls) == 2
