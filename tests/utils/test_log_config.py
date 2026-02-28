"""Tests for log path configuration.

Validates that log paths are organized under logs/Agent_evals/
instead of the bare logs/ directory.
"""

from app.config.config_app import LOGS_BASE_PATH, LOGS_PATH


def test_logs_path_under_agent_evals():
    """Test that LOGS_PATH is under logs/Agent_evals, not bare logs/."""
    assert LOGS_PATH == f"{LOGS_BASE_PATH}/logs", (
        f"Expected '{LOGS_BASE_PATH}/logs', got '{LOGS_PATH}'"
    )


def test_trace_storage_path_under_agent_evals():
    """Test that JudgeSettings trace_storage_path is under logs/Agent_evals/."""
    from app.config.judge_settings import JudgeSettings

    settings = JudgeSettings()
    assert settings.trace_storage_path == "output/runs", (
        f"trace_storage_path should be 'output/runs', got: {settings.trace_storage_path}"
    )
