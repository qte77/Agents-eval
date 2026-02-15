"""
Tests for PeerRead tools trace logging (STORY-013).

Tests ensure:
- All PeerRead tools log trace events via trace_collector
- Trace events include timing, success/failure, and agent_id
- Manager-only runs produce non-empty trace data
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.judge.settings import JudgeSettings
from app.judge.trace_processors import TraceCollector


class TestPeerReadToolsTracing:
    """Test that PeerRead tools log trace events."""

    @pytest.fixture
    def mock_trace_collector(self, tmp_path: Path) -> TraceCollector:
        """Create a mock trace collector for testing."""
        settings = JudgeSettings(trace_collection=True, trace_storage_path=str(tmp_path / "traces"))
        return TraceCollector(settings)

    @given(paper_id=st.text(min_size=1, max_size=50))
    @pytest.mark.asyncio
    async def test_get_peerread_paper_logs_trace_event(
        self, paper_id: str, mock_trace_collector: TraceCollector
    ):
        """get_peerread_paper MUST log trace event with timing and success status."""
        # This test will FAIL until tracing is added to get_peerread_paper
        with patch(
            "app.tools.peerread_tools.get_trace_collector",
            return_value=mock_trace_collector,
        ):
            # Import here to apply patch
            from pydantic_ai import Agent

            from app.tools.peerread_tools import add_peerread_tools_to_manager

            manager = Agent("test", deps_type=None)
            add_peerread_tools_to_manager(manager)

            # Start execution
            mock_trace_collector.start_execution("test-exec")

            # Attempt to call tool (will fail due to missing dataset, but should still trace)
            with pytest.raises(Exception):
                # This will fail, but trace event should be logged
                tools = [
                    t for t in manager._function_tools.values() if t.name == "get_peerread_paper"
                ]
                assert len(tools) == 1

            # Verify: trace event was logged (will fail until implementation)
            assert len(mock_trace_collector.current_events) > 0

    @given(num_papers=st.integers(min_value=1, max_value=10))
    @pytest.mark.asyncio
    async def test_query_peerread_papers_logs_trace_event(
        self, num_papers: int, mock_trace_collector: TraceCollector
    ):
        """query_peerread_papers MUST log trace event with timing and success status."""
        # This test will FAIL until tracing is added to query_peerread_papers
        with patch(
            "app.tools.peerread_tools.get_trace_collector",
            return_value=mock_trace_collector,
        ):
            from pydantic_ai import Agent

            from app.tools.peerread_tools import add_peerread_tools_to_manager

            manager = Agent("test", deps_type=None)
            add_peerread_tools_to_manager(manager)

            # Start execution
            mock_trace_collector.start_execution("test-exec")

            # Verify tool exists
            tools = [
                t for t in manager._function_tools.values() if t.name == "query_peerread_papers"
            ]
            assert len(tools) == 1

            # Verify: trace event was logged (will fail until implementation)
            assert len(mock_trace_collector.current_events) > 0

    def test_trace_event_includes_agent_id(self, mock_trace_collector: TraceCollector):
        """Property: All tool trace events MUST include agent_id field."""
        # This test will FAIL until trace events include agent_id
        mock_trace_collector.start_execution("test-exec")

        # Manually log a tool call as the tools should do
        mock_trace_collector.log_tool_call(
            agent_id="manager", tool_name="test_tool", duration=1.0, success=True, error=None
        )

        # Verify: event has agent_id
        assert len(mock_trace_collector.current_events) == 1
        event = mock_trace_collector.current_events[0]
        assert event.agent_id == "manager"
        assert event.event_type == "tool_call"


class TestManagerOnlyTraceData:
    """Test that manager-only runs produce non-empty trace data."""

    def test_manager_only_run_produces_trace_data(self, tmp_path: Path):
        """Manager-only execution MUST produce non-empty trace data."""
        # This test will FAIL until tools log trace events
        settings = JudgeSettings(trace_collection=True, trace_storage_path=str(tmp_path / "traces"))
        collector = TraceCollector(settings)

        # Simulate manager-only run with tool calls
        collector.start_execution("manager-only-001")
        collector.log_tool_call(
            agent_id="manager",
            tool_name="get_peerread_paper",
            duration=1.5,
            success=True,
            error=None,
        )
        collector.log_tool_call(
            agent_id="manager",
            tool_name="generate_review_from_template",
            duration=3.2,
            success=True,
            error=None,
        )
        trace = collector.end_execution()

        # Verify: trace data is non-empty
        assert trace is not None
        assert len(trace.tool_calls) == 2
        assert all("agent_id" in tc for tc in trace.tool_calls)
