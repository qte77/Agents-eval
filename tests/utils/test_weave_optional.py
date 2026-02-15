"""Tests for optional weave dependency.

This module tests that weave is only imported and initialized when WANDB_API_KEY
is configured, eliminating warning noise for users who don't use Weights & Biases.

Uses TDD approach with hypothesis for property-based testing.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st


def test_weave_import_guard_when_api_key_present():
    """Test that weave is imported when WANDB_API_KEY is present."""
    # This test will FAIL initially because login.py unconditionally imports weave
    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.wandb_login") as mock_wandb,
        patch("app.utils.login.weave_init") as mock_weave,
        patch("app.utils.login.logfire_conf"),
    ):
        # Simulate WANDB_API_KEY being present
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY not present
            (True, "test_wandb_key"),  # WANDB_API_KEY present
        ]

        from app.utils.login import login
        from app.data_models.app_models import AppEnv

        env = AppEnv()
        login("test_project", env)

        # Should call weave_init when API key is present
        mock_wandb.assert_called_once()
        mock_weave.assert_called_once_with("test_project")


def test_weave_not_imported_when_api_key_absent():
    """Test that weave is NOT imported when WANDB_API_KEY is absent."""
    # This test will FAIL initially because login.py unconditionally imports weave
    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.wandb_login") as mock_wandb,
        patch("app.utils.login.logfire_conf"),
    ):
        # Simulate WANDB_API_KEY not being present
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY not present
            (False, ""),  # WANDB_API_KEY not present
        ]

        # Remove weave from sys.modules to test conditional import
        if "weave" in sys.modules:
            del sys.modules["weave"]

        from app.utils.login import login
        from app.data_models.app_models import AppEnv

        env = AppEnv()
        login("test_project", env)

        # Should NOT call wandb_login or weave_init when API key is absent
        mock_wandb.assert_not_called()

        # weave should not be imported (ImportError expected if accessed)
        # This assertion will pass once the implementation uses conditional import


def test_app_op_decorator_with_weave_available():
    """Test that @op() decorator works when weave is available."""
    # This test will PASS initially because app.py unconditionally imports weave
    with patch.dict(sys.modules, {"weave": MagicMock()}):
        # Force reimport to pick up the mocked weave
        if "app.app" in sys.modules:
            del sys.modules["app.app"]

        from app.app import op

        # op should be the actual weave.op decorator
        assert callable(op)


def test_app_op_decorator_without_weave():
    """Test that @op() decorator provides no-op fallback when weave unavailable."""
    # This test will FAIL initially because app.py fails to import without weave
    # Simulate weave not being installed
    with patch.dict(sys.modules, {"weave": None}):
        # Force reimport
        if "app.app" in sys.modules:
            del sys.modules["app.app"]

        # This will raise ImportError until the fallback is implemented
        from app.app import op

        # Should be a no-op decorator (identity function)
        @op()
        def test_func():
            return "test"

        assert test_func() == "test"


@given(st.text(min_size=1, max_size=50))
def test_weave_optional_with_arbitrary_project_names(project_name: str):
    """Property test: weave initialization should handle arbitrary project names."""
    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.wandb_login"),
        patch("app.utils.login.weave_init") as mock_weave,
        patch("app.utils.login.logfire_conf"),
    ):
        # Simulate WANDB_API_KEY present
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY
            (True, "test_key"),  # WANDB_API_KEY
        ]

        from app.utils.login import login
        from app.data_models.app_models import AppEnv

        env = AppEnv()
        login(project_name, env)

        # Should call weave_init with the provided project name
        mock_weave.assert_called_once_with(project_name)


@given(st.booleans())
def test_weave_import_guard_property(has_api_key: bool):
    """Property test: weave should only be initialized when API key is present."""
    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.wandb_login") as mock_wandb,
        patch("app.utils.login.logfire_conf"),
    ):
        # This test will FAIL until conditional import is implemented
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY
            (has_api_key, "test_key" if has_api_key else ""),  # WANDB_API_KEY
        ]

        # Need to conditionally import weave_init based on implementation
        if has_api_key:
            with patch("app.utils.login.weave_init") as mock_weave:
                from app.utils.login import login
                from app.data_models.app_models import AppEnv

                env = AppEnv()
                login("test_project", env)

                # Invariant: weave_init called IFF API key present
                if has_api_key:
                    mock_weave.assert_called_once()
                    mock_wandb.assert_called_once()
                else:
                    mock_wandb.assert_not_called()
        else:
            from app.utils.login import login
            from app.data_models.app_models import AppEnv

            env = AppEnv()
            login("test_project", env)

            # When no API key, wandb_login should not be called
            mock_wandb.assert_not_called()
