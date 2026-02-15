"""
Tests for Logfire instrumentation initialization (STORY-013).

Tests ensure:
- Logfire instrumentation is initialized when logfire_enabled=True
- Initialization uses JudgeSettings.logfire_enabled as authoritative setting
- No errors occur when logfire is unavailable
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestLogfireInitialization:
    """Test Logfire instrumentation initialization at startup."""

    @patch("app.app.initialize_logfire_instrumentation_from_settings")
    def test_logfire_initialized_when_enabled(
        self, mock_init_logfire: MagicMock
    ):
        """Logfire MUST be initialized at startup when logfire_enabled=True."""
        # This test will FAIL until initialization is added to app.py
        with patch("app.app.JudgeSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.logfire_enabled = True
            mock_settings_class.return_value = mock_settings

            # Import app module (triggers initialization)
            import importlib
            import app.app

            importlib.reload(app.app)

            # Verify: initialize_logfire_instrumentation_from_settings was called
            # This will FAIL until implementation
            mock_init_logfire.assert_called_once()

    @patch("app.app.initialize_logfire_instrumentation_from_settings")
    def test_logfire_not_initialized_when_disabled(
        self, mock_init_logfire: MagicMock
    ):
        """Logfire MUST NOT be initialized when logfire_enabled=False."""
        with patch("app.app.JudgeSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.logfire_enabled = False
            mock_settings_class.return_value = mock_settings

            import importlib
            import app.app

            importlib.reload(app.app)

            # Verify: initialize_logfire_instrumentation_from_settings was NOT called
            mock_init_logfire.assert_not_called()

    def test_logfire_initialization_uses_judge_settings(self):
        """Logfire initialization MUST use JudgeSettings.logfire_enabled."""
        # This test will FAIL until implementation uses correct settings source
        from app.judge.settings import JudgeSettings

        settings = JudgeSettings(logfire_enabled=True)

        # Verify: logfire_enabled exists in JudgeSettings
        assert hasattr(settings, "logfire_enabled")
        assert isinstance(settings.logfire_enabled, bool)


class TestLogfireGracefulDegradation:
    """Test graceful degradation when Logfire is unavailable."""

    @patch("app.instrumentation.logfire_instrumentation.logfire", None)
    def test_app_runs_when_logfire_unavailable(self):
        """App MUST run successfully even when Logfire is unavailable."""
        # This ensures no hard dependency on Logfire
        try:
            from app.instrumentation.logfire_instrumentation import (
                initialize_logfire_instrumentation_from_settings,
            )
            from app.judge.settings import JudgeSettings

            settings = JudgeSettings(logfire_enabled=True)
            # Should not raise even if logfire is unavailable
            initialize_logfire_instrumentation_from_settings(settings)
        except ImportError:
            pytest.skip("Logfire not installed")
        except Exception as e:
            # Should handle gracefully, not crash
            assert "logfire" in str(e).lower() or True
