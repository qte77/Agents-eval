"""Tests for optional weave dependency.

This module tests that weave is only imported and initialized when WANDB_API_KEY
is configured, eliminating warning noise for users who don't use Weights & Biases.

Uses TDD approach with hypothesis for property-based testing.
"""

import sys
from unittest.mock import MagicMock, patch

from hypothesis import given
from hypothesis import strategies as st


def _make_mock_wandb_weave():
    """Create mock wandb and weave modules for testing."""
    mock_wandb = MagicMock()
    mock_weave = MagicMock()
    return mock_wandb, mock_weave


def test_weave_import_guard_when_api_key_present():
    """Test that weave is imported when WANDB_API_KEY is present."""
    mock_wandb, mock_weave = _make_mock_wandb_weave()

    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.logfire_conf"),
        patch.dict(sys.modules, {"wandb": mock_wandb, "weave": mock_weave}),
    ):
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY not present
            (True, "test_wandb_key"),  # WANDB_API_KEY present
        ]

        from app.data_models.app_models import AppEnv
        from app.utils.login import login

        env = AppEnv()
        login("test_project", env)

        mock_wandb.login.assert_called_once_with(key="test_wandb_key")
        mock_weave.init.assert_called_once_with("test_project")


def test_weave_not_imported_when_api_key_absent():
    """Test that weave is NOT imported when WANDB_API_KEY is absent."""
    mock_wandb, mock_weave = _make_mock_wandb_weave()

    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.logfire_conf"),
        patch.dict(sys.modules, {"wandb": mock_wandb, "weave": mock_weave}),
    ):
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY not present
            (False, ""),  # WANDB_API_KEY not present
        ]

        from app.data_models.app_models import AppEnv
        from app.utils.login import login

        env = AppEnv()
        login("test_project", env)

        mock_wandb.login.assert_not_called()
        mock_weave.init.assert_not_called()


def test_app_op_decorator_without_weave():
    """Test that op() fallback in app.app is a callable no-op decorator when weave is absent."""
    import sys

    # Remove weave from sys.modules to simulate absence, then reimport app.app
    original_weave = sys.modules.pop("weave", None)
    original_app_app = sys.modules.pop("app.app", None)

    try:
        # Simulate ImportError for weave so the fallback branch executes
        sys.modules["weave"] = None  # type: ignore[assignment]

        # Reimport to trigger the try/except ImportError branch
        import importlib

        import app.app as app_mod

        importlib.reload(app_mod)

        # Behavioral assertion: op() must return a decorator that is a no-op
        op = app_mod.op
        assert callable(op), "op must be callable"

        decorator = op()
        assert callable(decorator), "op() must return a callable decorator"

        def sample_func():
            return "expected"

        wrapped = decorator(sample_func)
        assert wrapped() == "expected", "no-op decorator must return the original function result"
        assert callable(wrapped), "wrapped function must be callable"
    finally:
        # Restore original state
        del sys.modules["weave"]
        if original_weave is not None:
            sys.modules["weave"] = original_weave
        if original_app_app is not None:
            sys.modules["app.app"] = original_app_app


@given(st.text(min_size=1, max_size=50))
def test_weave_optional_with_arbitrary_project_names(project_name: str):
    """Property test: weave initialization should handle arbitrary project names."""
    mock_wandb, mock_weave = _make_mock_wandb_weave()

    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.logfire_conf"),
        patch.dict(sys.modules, {"wandb": mock_wandb, "weave": mock_weave}),
    ):
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY
            (True, "test_key"),  # WANDB_API_KEY
        ]

        from app.data_models.app_models import AppEnv
        from app.utils.login import login

        env = AppEnv()
        login(project_name, env)

        mock_weave.init.assert_called_once_with(project_name)


@given(st.booleans())
def test_weave_import_guard_property(has_api_key: bool):
    """Property test: weave should only be initialized when API key is present."""
    mock_wandb, mock_weave = _make_mock_wandb_weave()

    with (
        patch("app.utils.login.get_api_key") as mock_get_key,
        patch("app.utils.login.logfire_conf"),
        patch.dict(sys.modules, {"wandb": mock_wandb, "weave": mock_weave}),
    ):
        mock_get_key.side_effect = [
            (False, ""),  # LOGFIRE_API_KEY
            (has_api_key, "test_key" if has_api_key else ""),  # WANDB_API_KEY
        ]

        from app.data_models.app_models import AppEnv
        from app.utils.login import login

        env = AppEnv()
        login("test_project", env)

        if has_api_key:
            mock_weave.init.assert_called_once()
            mock_wandb.login.assert_called_once()
        else:
            mock_wandb.login.assert_not_called()
            mock_weave.init.assert_not_called()
