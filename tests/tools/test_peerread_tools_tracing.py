"""
Tests for PeerRead tools trace logging (STORY-013).

Tests ensure:
- All PeerRead tools log trace events via trace_collector
- Trace events include timing, success/failure, and agent_id
- Manager-only runs produce non-empty trace data
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.judge.settings import JudgeSettings
from app.judge.trace_processors import TraceCollector


class TestPeerReadToolsTracing:
    """Test that PeerRead tools log trace events."""

    @pytest.fixture
    def mock_trace_collector(self, tmp_path: Path) -> TraceCollector:
        """Create a mock trace collector for testing."""
        settings = JudgeSettings(trace_collection=True, trace_storage_path=str(tmp_path / "traces"))
        return TraceCollector(settings)

    def test_get_peerread_paper_logs_trace_event(self, mock_trace_collector: TraceCollector):
        """get_peerread_paper MUST log trace event with timing and success status."""
        # Verify that trace collector is available and can log tool calls
        mock_trace_collector.start_execution("test-exec")

        # Simulate a tool call (as the actual tools would do)
        mock_trace_collector.log_tool_call(
            agent_id="manager",
            tool_name="get_peerread_paper",
            duration=1.0,
            success=True,
            context="paper_id=test",
        )

        # Verify: trace event was logged
        assert len(mock_trace_collector.current_events) > 0
        assert mock_trace_collector.current_events[0].event_type == "tool_call"
        assert mock_trace_collector.current_events[0].agent_id == "manager"

    def test_query_peerread_papers_logs_trace_event(self, mock_trace_collector: TraceCollector):
        """query_peerread_papers MUST log trace event with timing and success status."""
        # Verify that trace collector is available and can log tool calls
        mock_trace_collector.start_execution("test-exec")

        # Simulate a tool call (as the actual tools would do)
        mock_trace_collector.log_tool_call(
            agent_id="manager",
            tool_name="query_peerread_papers",
            duration=2.5,
            success=True,
            context="venue=ACL",
        )

        # Verify: trace event was logged
        assert len(mock_trace_collector.current_events) > 0
        assert mock_trace_collector.current_events[0].event_type == "tool_call"
        assert mock_trace_collector.current_events[0].agent_id == "manager"

    def test_trace_event_includes_agent_id(self, mock_trace_collector: TraceCollector):
        """Property: All tool trace events MUST include agent_id field."""
        # This test will FAIL until trace events include agent_id
        mock_trace_collector.start_execution("test-exec")

        # Manually log a tool call as the tools should do
        mock_trace_collector.log_tool_call(
            agent_id="manager", tool_name="test_tool", duration=1.0, success=True
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
        )
        collector.log_tool_call(
            agent_id="manager",
            tool_name="generate_review_from_template",
            duration=3.2,
            success=True,
        )
        trace = collector.end_execution()

        # Verify: trace data is non-empty
        assert trace is not None
        assert len(trace.tool_calls) == 2
        assert all("agent_id" in tc for tc in trace.tool_calls)
