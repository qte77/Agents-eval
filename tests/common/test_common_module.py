"""Tests for common module structure and backward compatibility.

This module tests that the common/ module structure is correct and that
backward-compatible re-exports work properly for zero-breakage migration.
"""



def test_common_module_imports():
    """Test that common module exports are available."""


def test_common_settings_import():
    """Test that CommonSettings can be imported from common.settings."""
    from app.common.settings import CommonSettings

    assert CommonSettings is not None


def test_common_log_import():
    """Test that logger can be imported from common.log."""
    from app.common.log import logger

    assert logger is not None


def test_common_error_messages_import():
    """Test that error_messages module can be imported from common."""
    from app.common import error_messages

    assert hasattr(error_messages, "failed_to_load_config")
    assert hasattr(error_messages, "file_not_found")
    assert hasattr(error_messages, "invalid_json")


def test_backward_compat_utils_log_import():
    """Test backward compatibility - logger import from utils.log still works."""
    from app.utils.log import logger

    assert logger is not None


def test_backward_compat_utils_error_messages_import():
    """Test backward compatibility - error_messages from utils still works."""
    from app.utils.error_messages import failed_to_load_config, file_not_found

    assert failed_to_load_config is not None
    assert file_not_found is not None


def test_common_models_import():
    """Test that shared models can be imported from common.models."""
    from app.common.models import CommonBaseModel

    assert CommonBaseModel is not None
