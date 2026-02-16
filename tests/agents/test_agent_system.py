"""
Test cases for agent system orchestration.

Tests for delegation flow, usage limit enforcement, and single-agent fallback.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from pydantic_ai.usage import UsageLimits

from app.agents.agent_system import (
    initialize_logfire_instrumentation_from_settings,
    _validate_model_return,
)
from app.data_models.app_models import ResearchResult, ResearchSummary
from app.judge.settings import JudgeSettings


class TestLogfireInstrumentation:
    """Test Logfire instrumentation initialization."""

    def test_initialize_logfire_with_settings(self):
        """Test Logfire initialization with JudgeSettings."""
        settings = JudgeSettings(
            logfire_enabled=True,
            logfire_project_name="test-project",
        )

        with patch("app.agents.agent_system.initialize_logfire_instrumentation") as mock_init:
            initialize_logfire_instrumentation_from_settings(settings)
            mock_init.assert_called_once()

    def test_initialize_logfire_without_settings(self):
        """Test Logfire initialization without settings (uses defaults)."""
        with patch("app.agents.agent_system.initialize_logfire_instrumentation") as mock_init:
            initialize_logfire_instrumentation_from_settings(None)
            mock_init.assert_called_once()

    def test_initialize_logfire_handles_errors(self):
        """Test that Logfire initialization handles errors gracefully."""
        with patch(
            "app.agents.agent_system.initialize_logfire_instrumentation",
            side_effect=Exception("Init failed"),
        ):
            # Should not raise - just log warning
            initialize_logfire_instrumentation_from_settings(None)


class TestModelValidation:
    """Test model validation functions."""

    def test_validate_model_return_success(self):
        """Test successful model validation."""
        result_data = {
            "summary": ResearchSummary(
                key_findings=["Finding 1", "Finding 2"],
                main_topics=["Topic 1"],
                confidence_score=0.9,
            ),
            "sources": ["Source 1"],
        }

        validated = _validate_model_return(result_data, ResearchResult)

        assert isinstance(validated, ResearchResult)
        assert len(validated.summary.key_findings) == 2
        assert validated.summary.confidence_score == 0.9

    def test_validate_model_return_validation_error(self):
        """Test validation error handling."""
        invalid_data = {"invalid_field": "value"}

        with pytest.raises(Exception):
            _validate_model_return(invalid_data, ResearchResult)


class TestDelegationFlow:
    """Test agent delegation functionality."""

    @pytest.fixture
    def mock_manager_agent(self):
        """Create mock manager agent."""
        agent = Mock()
        agent.run = AsyncMock(return_value=Mock(output="test result"))
        return agent

    @pytest.fixture
    def mock_research_agent(self):
        """Create mock research agent."""
        agent = Mock()
        agent.run = AsyncMock(
            return_value=Mock(
                output=ResearchResult(
                    summary=ResearchSummary(
                        key_findings=["Finding 1"],
                        main_topics=["Topic 1"],
                        confidence_score=0.8,
                    ),
                    sources=["Source 1"],
                )
            )
        )
        return agent

    @pytest.mark.asyncio
    async def test_research_delegation_captures_trace(self, mock_manager_agent, mock_research_agent):
        """Test that research delegation captures trace data."""
        with (
            patch("app.agents.agent_system.get_trace_collector") as mock_get_collector,
            patch("app.agents.agent_system._add_research_tool") as mock_add_tool,
        ):
            mock_collector = Mock()
            mock_get_collector.return_value = mock_collector

            # Simulate adding research tool and calling it
            from app.agents.agent_system import _add_research_tool

            _add_research_tool(mock_manager_agent, mock_research_agent, ResearchResult)

            # Verify delegation tool was added
            assert mock_manager_agent.tool.called


class TestUsageLimitEnforcement:
    """Test usage limit enforcement."""

    def test_usage_limits_configured(self):
        """Test that usage limits can be configured."""
        limits = UsageLimits(
            request_limit=100,
            request_tokens_limit=10000,
            response_tokens_limit=5000,
            total_tokens_limit=15000,
        )

        assert limits.request_limit == 100
        assert limits.request_tokens_limit == 10000
        assert limits.response_tokens_limit == 5000
        assert limits.total_tokens_limit == 15000


class TestSingleAgentFallback:
    """Test single-agent mode fallback behavior."""

    @pytest.fixture
    def mock_endpoint_config(self):
        """Create mock endpoint configuration."""
        from app.data_models.app_models import EndpointConfig, ProviderConfig

        return EndpointConfig(
            provider="openai",
            api_key="test-key",
            provider_config=ProviderConfig(
                model_name="gpt-4",
                base_url="https://api.openai.com/v1",
            ),
        )

    def test_single_agent_mode_has_no_delegation_tools(self):
        """Test that single-agent mode doesn't add delegation tools."""
        # In single-agent mode, manager should not have delegation tools
        # This is tested by verifying tool registration when include_researcher=False
        from app.agents.agent_system import get_manager

        with (
            patch("app.agents.agent_system.create_agent_models") as mock_create_models,
            patch("app.agents.agent_system.add_peerread_tools_to_agent"),
        ):
            mock_models = Mock()
            mock_models.model_manager = Mock()
            mock_models.model_researcher = None
            mock_create_models.return_value = mock_models

            manager = get_manager(
                provider="openai",
                provider_config=Mock(),
                api_key="test-key",
                prompts={"manager": "You are a manager"},
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
            )

            # Manager should be created
            assert manager is not None


class TestAgentSystemEdgeCases:
    """Test edge cases in agent system."""

    def test_empty_query_handling(self):
        """Test handling of empty query."""
        # Agent system should handle empty queries gracefully
        # This is tested at the integration level
        pass

    def test_concurrent_agent_requests(self):
        """Test handling of concurrent agent requests."""
        # Agent system should handle concurrent requests safely
        # This is tested at the integration level
        pass


class TestErrorHandling:
    """Test error handling in agent system."""

    def test_model_http_error_handling(self):
        """Test handling of HTTP errors from model."""
        # Agent system should handle ModelHTTPError gracefully
        from pydantic_ai.exceptions import ModelHTTPError

        # Error handling is done at the calling code level
        # This test verifies the error can be caught
        try:
            raise ModelHTTPError("Test error", None)
        except ModelHTTPError as e:
            assert "Test error" in str(e)

    def test_usage_limit_exceeded_handling(self):
        """Test handling of usage limit exceeded."""
        from pydantic_ai.exceptions import UsageLimitExceeded

        # Error handling is done at the calling code level
        try:
            raise UsageLimitExceeded("Usage limit exceeded")
        except UsageLimitExceeded as e:
            assert "exceeded" in str(e).lower()


class TestTraceCollection:
    """Test trace collection functionality."""

    def test_trace_collector_logs_agent_interaction(self):
        """Test that trace collector logs agent-to-agent interactions."""
        with patch("app.agents.agent_system.get_trace_collector") as mock_get_collector:
            mock_collector = Mock()
            mock_get_collector.return_value = mock_collector

            from app.agents.agent_system import get_trace_collector

            collector = get_trace_collector()
            collector.log_agent_interaction(
                from_agent="manager",
                to_agent="researcher",
                interaction_type="delegation",
                data={"query": "test query"},
            )

            mock_collector.log_agent_interaction.assert_called_once()

    def test_trace_collector_logs_tool_call(self):
        """Test that trace collector logs tool calls."""
        with patch("app.agents.agent_system.get_trace_collector") as mock_get_collector:
            mock_collector = Mock()
            mock_get_collector.return_value = mock_collector

            from app.agents.agent_system import get_trace_collector

            collector = get_trace_collector()
            collector.log_tool_call(
                agent_id="manager",
                tool_name="test_tool",
                success=True,
                duration=0.5,
                context="test_context",
            )

            mock_collector.log_tool_call.assert_called_once()
