"""Tests for log path configuration.

Validates that log paths are organized under logs/Agent_evals/
instead of the bare logs/ directory.
"""

from app.config.config_app import LOGS_PATH


def test_logs_path_under_agent_evals():
    """Test that LOGS_PATH points to logs/Agent_evals, not bare logs/."""
    assert LOGS_PATH == "logs/Agent_evals", f"Expected 'logs/Agent_evals', got '{LOGS_PATH}'"


def test_trace_storage_path_under_agent_evals():
    """Test that JudgeSettings trace_storage_path is under logs/Agent_evals/."""
    from app.judge.settings import JudgeSettings

    settings = JudgeSettings()
    assert "Agent_evals" in settings.trace_storage_path, (
        f"trace_storage_path should be under Agent_evals, got: {settings.trace_storage_path}"
    )
