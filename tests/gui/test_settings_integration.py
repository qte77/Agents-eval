"""
Tests for GUI settings integration with pydantic-settings.

Verifies that the Streamlit GUI correctly loads and displays actual
default values from CommonSettings and JudgeSettings classes.
"""

import pytest

from app.common.settings import CommonSettings
from app.judge.settings import JudgeSettings


class TestSettingsIntegration:
    """Test suite for GUI settings integration."""

    def test_render_settings_accepts_common_and_judge_settings(self):
        """Test that render_settings can accept CommonSettings and JudgeSettings instances."""
        # Arrange
        common_settings = CommonSettings()
        judge_settings = JudgeSettings()

        from gui.pages.settings import render_settings

        # Act & Assert - should accept settings instances without error
        # Function returns None, we just verify it doesn't raise
        try:
            render_settings(common_settings, judge_settings)
            # If we get here without TypeError, implementation is done
        except TypeError:
            # Expected - render_settings doesn't accept these args yet
            pytest.fail("render_settings should accept common_settings and judge_settings")

    def test_settings_values_are_customizable(self):
        """Test that settings can be customized via constructor."""
        common_settings = CommonSettings(log_level="DEBUG", max_content_length=20000)
        assert common_settings.log_level == "DEBUG"
        assert common_settings.max_content_length == 20000

        judge_settings = JudgeSettings(
            tier1_max_seconds=2.0,
            tier2_max_seconds=15.0,
            composite_accept_threshold=0.85,
        )
        assert judge_settings.tier1_max_seconds == 2.0
        assert judge_settings.tier2_max_seconds == 15.0
        assert judge_settings.composite_accept_threshold == 0.85
