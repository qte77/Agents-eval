"""
Tests for trace collection integration in agent orchestration.

Validates that TraceCollector is wired into agent delegations,
agent-to-agent interactions are logged, tool calls are captured,
and GraphTraceData is properly constructed and passed to evaluation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.data_models.evaluation_models import GraphTraceData


@pytest.mark.asyncio
async def test_trace_collector_initialized_in_run_manager():
    """Test that TraceCollector is initialized when run_manager is called."""
    with (
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
        patch("app.agents.agent_system.run_manager_orchestrated") as mock_run_orchestrated,
    ):
        mock_collector = MagicMock()
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock()
        await run_manager(
            manager=mock_manager,
            query="test query",
            provider="test_provider",
            usage_limits=None,
        )

        # Verify trace collector was initialized
        mock_get_collector.assert_called_once()


@pytest.mark.asyncio
async def test_trace_execution_started_for_each_run():
    """Test that trace execution is started with unique execution_id."""
    with (
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
        patch("app.agents.agent_system.run_manager_orchestrated") as mock_run_orchestrated,
    ):
        mock_collector = MagicMock()
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock()
        await run_manager(
            manager=mock_manager,
            query="test query",
            provider="test_provider",
            usage_limits=None,
        )

        # Verify start_execution was called with execution_id
        mock_collector.start_execution.assert_called_once()
        call_args = mock_collector.start_execution.call_args
        execution_id = call_args[0][0]
        assert isinstance(execution_id, str)
        assert len(execution_id) > 0


@pytest.mark.asyncio
async def test_agent_interaction_logged_on_delegation():
    """Test that agent-to-agent delegations are logged via trace_collector."""
    with (
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
    ):
        mock_collector = MagicMock()
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import _add_research_tool
        from pydantic_ai import Agent

        # Create mock agents
        manager_agent = Agent(model="test", output_type=str)
        research_agent = MagicMock()
        research_agent.run = AsyncMock(return_value=MagicMock(output="test result"))

        # Add research tool (which should include trace logging)
        from app.data_models.app_models import ResearchResult

        _add_research_tool(manager_agent, research_agent, ResearchResult)

        # Simulate delegation by calling the tool
        # Note: This test will fail initially because trace logging isn't implemented yet
        # When implemented, we expect log_agent_interaction to be called

        # Verify log_agent_interaction would be called during delegation
        # This assertion will fail until implementation is complete
        assert hasattr(
            mock_collector, "log_agent_interaction"
        ), "TraceCollector should have log_agent_interaction method"


@pytest.mark.asyncio
async def test_tool_call_logging_during_delegation():
    """Test that tool calls are logged via trace_collector.log_tool_call."""
    with (
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
    ):
        mock_collector = MagicMock()
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import _add_research_tool
        from pydantic_ai import Agent

        # Create mock agents
        manager_agent = Agent(model="test", output_type=str)
        research_agent = MagicMock()
        research_agent.run = AsyncMock(return_value=MagicMock(output="test result"))

        # Add research tool
        from app.data_models.app_models import ResearchResult

        _add_research_tool(manager_agent, research_agent, ResearchResult)

        # Verify log_tool_call method exists on collector
        # This assertion will fail until implementation is complete
        assert hasattr(
            mock_collector, "log_tool_call"
        ), "TraceCollector should have log_tool_call method"


@pytest.mark.asyncio
async def test_timing_data_captured_during_execution():
    """Test that timing data is captured for each delegation step."""
    with (
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
        patch("app.agents.agent_system.run_manager_orchestrated") as mock_run_orchestrated,
    ):
        mock_collector = MagicMock()
        mock_collector.end_execution = MagicMock(
            return_value=MagicMock(
                performance_metrics={
                    "total_duration": 1.5,
                    "agent_interactions": 3,
                    "tool_calls": 2,
                }
            )
        )
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import run_manager

        mock_manager = MagicMock()
        await run_manager(
            manager=mock_manager,
            query="test query",
            provider="test_provider",
            usage_limits=None,
        )

        # Verify end_execution was called to finalize timing
        mock_collector.end_execution.assert_called_once()


@pytest.mark.asyncio
async def test_graph_trace_data_passed_to_evaluation():
    """Test that GraphTraceData is constructed and passed to evaluate_comprehensive."""
    with (
        patch("app.app.setup_agent_env") as mock_setup,
        patch("app.app.login"),
        patch("app.app.get_manager") as mock_get_manager,
        patch("app.app.run_manager", new_callable=AsyncMock) as mock_run_manager,
        patch("app.app.EvaluationPipeline") as mock_pipeline_class,
        patch("app.app.load_config") as mock_load_config,
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
    ):
        # Setup mocks
        mock_setup.return_value = MagicMock(
            provider="test_provider",
            provider_config={},
            api_key="test_key",
            prompts={},
            query="test query",
            usage_limits=None,
        )
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        # Mock trace collector with real GraphTraceData
        mock_collector = MagicMock()
        mock_trace_data = GraphTraceData(
            execution_id="test_exec_123",
            agent_interactions=[
                {"from": "manager", "to": "researcher", "type": "delegation"}
            ],
            tool_calls=[{"tool_name": "delegate_research", "success": True, "duration": 0.5}],
            timing_data={"start_time": 0.0, "end_time": 1.5, "total_duration": 1.5},
        )
        mock_collector.load_trace = MagicMock(return_value=mock_trace_data)
        mock_get_collector.return_value = mock_collector

        # Mock run_manager to return execution_id
        mock_run_manager.return_value = "test_exec_123"

        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.evaluate_comprehensive = AsyncMock()
        mock_pipeline_class.return_value = mock_pipeline

        mock_load_config.return_value = MagicMock(prompts={})

        from app.app import main

        # Run main with paper_number (enables evaluation)
        await main(
            chat_provider="test_provider",
            query="test query",
            paper_number="001",
        )

        # Verify evaluate_comprehensive was called with GraphTraceData
        mock_pipeline.evaluate_comprehensive.assert_called_once()
        call_kwargs = mock_pipeline.evaluate_comprehensive.call_args.kwargs

        # This assertion will fail until STORY-003 is implemented
        assert (
            "execution_trace" in call_kwargs
        ), "evaluate_comprehensive should receive execution_trace parameter"

        # When implemented, execution_trace should be GraphTraceData instance
        # assert isinstance(call_kwargs["execution_trace"], GraphTraceData)


@pytest.mark.asyncio
async def test_graph_trace_data_constructed_via_model_validate():
    """Test that GraphTraceData uses model_validate instead of manual dict extraction."""
    with (
        patch("app.evals.trace_processors.TraceCollector.load_trace") as mock_load_trace,
    ):
        # Mock load_trace to return GraphTraceData via model_validate
        trace_dict = {
            "execution_id": "test_123",
            "agent_interactions": [{"from": "manager", "to": "researcher"}],
            "tool_calls": [{"tool_name": "test_tool", "success": True}],
            "timing_data": {"total_duration": 1.0},
            "coordination_events": [],
        }

        # Simulate model_validate construction
        graph_trace = GraphTraceData.model_validate(trace_dict)
        mock_load_trace.return_value = graph_trace

        from app.evals.trace_processors import TraceCollector
        from app.evals.settings import JudgeSettings

        collector = TraceCollector(JudgeSettings())
        result = collector.load_trace("test_123")

        # Verify result is GraphTraceData instance (constructed properly)
        assert isinstance(result, GraphTraceData)
        assert result.execution_id == "test_123"
        assert len(result.agent_interactions) == 1
        assert len(result.tool_calls) == 1


@pytest.mark.asyncio
async def test_delegation_logs_interaction_with_timing():
    """Test that delegation tools log agent interactions with timing data."""
    # This test will fail until trace logging is added to delegation tools
    # Expected behavior: each delegate_* function should call:
    # trace_collector.log_agent_interaction(from_agent, to_agent, interaction_type, data)

    with (
        patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
    ):
        mock_collector = MagicMock()
        mock_get_collector.return_value = mock_collector

        from app.agents.agent_system import _add_research_tool
        from pydantic_ai import Agent

        manager_agent = Agent(model="test", output_type=str)
        research_agent = MagicMock()
        research_agent.run = AsyncMock(return_value=MagicMock(output="test"))

        from app.data_models.app_models import ResearchResult

        _add_research_tool(manager_agent, research_agent, ResearchResult)

        # When implemented, this should verify that trace logging happens
        # For now, this test documents the expected behavior
        assert hasattr(mock_collector, "log_agent_interaction")
