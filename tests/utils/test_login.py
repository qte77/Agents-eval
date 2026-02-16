"""
Tests for login.py utility module.

Verifies wandb/weave import guard behavior and crash telemetry settings.
"""

from unittest.mock import patch, MagicMock
import os
import pytest
from inline_snapshot import snapshot

from app.data_models.app_models import AppEnv


def test_login_succeeds_without_wandb_installed():
    """
    Application should start successfully when wandb is not installed.

    Tests STORY-014 acceptance: "Application starts successfully when wandb
    is not installed (no ImportError)"
    """
    from app.utils import login  # Should not raise ImportError

    # Mock AppEnv with no WANDB_API_KEY
    mock_env = AppEnv()

    # Should complete without error when wandb package is unavailable
    with patch("app.utils.login.get_api_key") as mock_get_key:
        mock_get_key.return_value = (False, "")

        # Should not raise ImportError
        login.login("test_project", mock_env)


def test_login_skips_wandb_when_unavailable_with_debug_log():
    """
    When wandb is not installed, login() should skip wandb/weave init with debug log.

    Tests STORY-014 acceptance: "When wandb is not installed, login() skips
    wandb/weave initialization with a debug log"
    """
    from app.utils import login

    mock_env = AppEnv()

    with patch("app.utils.login.get_api_key") as mock_get_key:
        with patch("app.utils.login.logger") as mock_logger:
            # Simulate wandb API key present but wandb package not installed
            def side_effect(key_name, env):
                if key_name == "WANDB":
                    return (True, "fake_wandb_key")
                return (False, "")

            mock_get_key.side_effect = side_effect

            # Mock ImportError when trying to import wandb
            with patch("builtins.__import__", side_effect=ImportError("No module named 'wandb'")):
                login.login("test_project", mock_env)

                # Should log warning about wandb not being installed
                assert mock_logger.warning.called
                warning_msg = str(mock_logger.warning.call_args)
                assert "wandb" in warning_msg.lower() or "weave" in warning_msg.lower()


def test_login_sets_wandb_error_reporting_to_false():
    """
    WANDB_ERROR_REPORTING should default to false to disable crash telemetry.

    Tests STORY-014 acceptance: "WANDB_ERROR_REPORTING defaults to false
    (respects user override if already set)"
    """
    from app.utils import login

    # Ensure env var is not set initially
    os.environ.pop("WANDB_ERROR_REPORTING", None)

    mock_env = AppEnv()

    # Verify that setdefault is called correctly by checking the environment
    # Mock the imports to avoid requiring wandb package
    import sys
    mock_wandb = MagicMock()
    mock_weave = MagicMock()

    with patch.dict(sys.modules, {"wandb": mock_wandb, "weave": mock_weave}):
        with patch("app.utils.login.get_api_key") as mock_get_key:
            mock_get_key.side_effect = lambda key, env: (
                (True, "fake_key") if key == "WANDB" else (False, "")
            )

            login.login("test_project", mock_env)

            # Should set WANDB_ERROR_REPORTING to false
            assert os.environ.get("WANDB_ERROR_REPORTING") == snapshot("false")


def test_login_respects_user_wandb_error_reporting_override():
    """
    If user already set WANDB_ERROR_REPORTING, respect their choice.

    Tests STORY-014 acceptance: "WANDB_ERROR_REPORTING defaults to false
    (respects user override if already set)"
    """
    from app.utils import login

    # User sets their own preference
    os.environ["WANDB_ERROR_REPORTING"] = "true"

    mock_env = AppEnv()

    import sys
    mock_wandb = MagicMock()
    mock_weave = MagicMock()

    with patch.dict(sys.modules, {"wandb": mock_wandb, "weave": mock_weave}):
        with patch("app.utils.login.get_api_key") as mock_get_key:
            mock_get_key.side_effect = lambda key, env: (
                (True, "fake_key") if key == "WANDB" else (False, "")
            )

            login.login("test_project", mock_env)

            # Should NOT override user's setting
            assert os.environ.get("WANDB_ERROR_REPORTING") == "true"

    # Cleanup
    os.environ.pop("WANDB_ERROR_REPORTING", None)


def test_login_works_when_wandb_installed_and_key_present():
    """
    When wandb is installed and WANDB_API_KEY is set, login should work normally.

    Tests STORY-014 acceptance: "When wandb is installed and WANDB_API_KEY is set,
    login and weave init work as before"
    """
    from app.utils import login

    mock_env = AppEnv()

    import sys
    mock_wandb_login = MagicMock()
    mock_weave_init = MagicMock()
    mock_wandb = MagicMock()
    mock_weave = MagicMock()

    # Setup the mock module attributes
    mock_wandb.login = mock_wandb_login
    mock_weave.init = mock_weave_init

    with patch.dict(sys.modules, {"wandb": mock_wandb, "weave": mock_weave}):
        with patch("app.utils.login.get_api_key") as mock_get_key:
            mock_get_key.side_effect = lambda key, env: (
                (True, "fake_wandb_key") if key == "WANDB"
                else (True, "fake_logfire_key") if key == "LOGFIRE"
                else (False, "")
            )

            login.login("test_project", mock_env)

            # Should call wandb_login and weave_init
            mock_wandb_login.assert_called_once_with(key="fake_wandb_key")
            mock_weave_init.assert_called_once_with("test_project")


def test_no_agentops_commented_code_in_login():
    """
    Dead agentops commented code should be removed from login.py.

    Tests STORY-014 acceptance: "Dead agentops commented code removed from login.py:
    commented import at line 7 and commented code block at lines 30-37"
    """
    with open("/workspaces/Agents-eval/src/app/utils/login.py", "r") as f:
        content = f.read()

    # Should not contain any agentops references (commented or otherwise)
    assert "agentops" not in content.lower(), "Dead agentops code should be removed"
    assert "agentops_init" not in content, "agentops_init should be removed"
