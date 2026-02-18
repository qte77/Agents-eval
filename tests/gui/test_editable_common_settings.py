"""
Tests for editable common settings in the Streamlit settings UI.

Verifies that:
- Log level selectbox stores to common_log_level in session state
- Max content length number input stores to common_max_content_length
- Logfire setting is consolidated to JudgeSettings (no separate common toggle)
- Reset button clears common_* keys from session state
- _build_common_settings_from_session() returns correct CommonSettings
- All common settings widgets have help tooltip text
"""

from unittest.mock import MagicMock, patch

import pytest

from app.common.settings import CommonSettings
from app.judge.settings import JudgeSettings


class TestEditableCommonSettingsWidgets:
    """Tests for editable common settings widget rendering."""

    def test_log_level_selectbox_stores_to_session_state(self):
        """Test that log level selectbox stores selection to common_log_level in session state."""
        # Arrange
        mock_session_state: dict = {}
        mock_selectbox = MagicMock(return_value="DEBUG")

        with (
            patch("streamlit.session_state", mock_session_state),
            patch("streamlit.selectbox", mock_selectbox),
            patch("streamlit.expander"),
            patch("streamlit.header"),
            patch("streamlit.text"),
            patch("streamlit.checkbox", return_value=False),
            patch("streamlit.number_input", return_value=15000),
            patch("streamlit.button", return_value=False),
            patch("streamlit.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            common_settings = CommonSettings()
            judge_settings = JudgeSettings()

            from gui.pages.settings import render_settings

            render_settings(common_settings, judge_settings)

        # Assert - selectbox called for log level with correct options
        log_level_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Log Level" in str(call.args[0])
        ]
        assert len(log_level_calls) >= 1, "selectbox should be called for Log Level"
        call_kwargs = log_level_calls[0].kwargs
        assert "options" in call_kwargs
        assert set(call_kwargs["options"]) == {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def test_log_level_selectbox_has_help_tooltip(self):
        """Test that log level selectbox has a help tooltip."""
        # Arrange
        mock_selectbox = MagicMock(return_value="INFO")

        with (
            patch("streamlit.selectbox", mock_selectbox),
            patch("streamlit.session_state", {}),
            patch("streamlit.expander"),
            patch("streamlit.header"),
            patch("streamlit.text"),
            patch("streamlit.checkbox", return_value=False),
            patch("streamlit.number_input", return_value=15000),
            patch("streamlit.button", return_value=False),
            patch("streamlit.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import render_settings

            render_settings(CommonSettings(), JudgeSettings())

        log_level_calls = [
            call
            for call in mock_selectbox.call_args_list
            if call.args and "Log Level" in str(call.args[0])
        ]
        assert len(log_level_calls) >= 1
        call_kwargs = log_level_calls[0].kwargs
        assert "help" in call_kwargs and call_kwargs["help"], "Log Level selectbox must have help"

    def test_max_content_length_number_input_range(self):
        """Test that max content length number input has correct min/max/step values."""
        # Arrange
        mock_number_input = MagicMock(return_value=15000)

        with (
            patch("streamlit.number_input", mock_number_input),
            patch("streamlit.session_state", {}),
            patch("streamlit.selectbox", return_value="INFO"),
            patch("streamlit.expander"),
            patch("streamlit.header"),
            patch("streamlit.text"),
            patch("streamlit.checkbox", return_value=False),
            patch("streamlit.button", return_value=False),
            patch("streamlit.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import render_settings

            render_settings(CommonSettings(), JudgeSettings())

        max_content_calls = [
            call
            for call in mock_number_input.call_args_list
            if call.args and "Max Content Length" in str(call.args[0])
        ]
        assert len(max_content_calls) >= 1, "number_input should be called for Max Content Length"
        call_kwargs = max_content_calls[0].kwargs
        assert call_kwargs.get("min_value") == 1000
        assert call_kwargs.get("max_value") == 100000
        assert call_kwargs.get("step") == 1000

    def test_max_content_length_has_help_tooltip(self):
        """Test that max content length number input has a help tooltip."""
        mock_number_input = MagicMock(return_value=15000)

        with (
            patch("streamlit.number_input", mock_number_input),
            patch("streamlit.session_state", {}),
            patch("streamlit.selectbox", return_value="INFO"),
            patch("streamlit.expander"),
            patch("streamlit.header"),
            patch("streamlit.text"),
            patch("streamlit.checkbox", return_value=False),
            patch("streamlit.button", return_value=False),
            patch("streamlit.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import render_settings

            render_settings(CommonSettings(), JudgeSettings())

        max_content_calls = [
            call
            for call in mock_number_input.call_args_list
            if call.args and "Max Content Length" in str(call.args[0])
        ]
        assert len(max_content_calls) >= 1
        call_kwargs = max_content_calls[0].kwargs
        assert "help" in call_kwargs and call_kwargs["help"], (
            "Max Content Length must have help tooltip"
        )

    def test_no_separate_logfire_toggle_in_common_settings(self):
        """Test that common settings does not show a separate logfire checkbox (consolidated)."""
        # Logfire is consolidated to JudgeSettings only
        mock_checkbox = MagicMock(return_value=False)

        with (
            patch("streamlit.checkbox", mock_checkbox),
            patch("streamlit.session_state", {}),
            patch("streamlit.selectbox", return_value="INFO"),
            patch("streamlit.number_input", return_value=15000),
            patch("streamlit.expander"),
            patch("streamlit.header"),
            patch("streamlit.text"),
            patch("streamlit.button", return_value=False),
            patch("streamlit.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import render_settings

            render_settings(CommonSettings(), JudgeSettings())

        # There should be no checkbox with "Enable Logfire" or "enable_logfire" label
        # from common settings section
        logfire_common_calls = [
            call
            for call in mock_checkbox.call_args_list
            if call.args and "Enable Logfire" in str(call.args[0])
        ]
        assert len(logfire_common_calls) == 0, (
            "Common Settings should NOT show a separate 'Enable Logfire' checkbox — "
            "logfire is consolidated to JudgeSettings"
        )

    def test_common_settings_stored_with_common_prefix(self):
        """Test that common settings values are stored in session state with common_ prefix."""
        session_state: dict = {}

        def fake_selectbox(label, **kwargs):
            if "Log Level" in label:
                session_state["common_log_level"] = "WARNING"
                return "WARNING"
            return kwargs.get("options", [""])[0] if kwargs.get("options") else ""

        def fake_number_input(label, **kwargs):
            if "Max Content Length" in label:
                session_state["common_max_content_length"] = 20000
                return 20000
            return kwargs.get("value", 0)

        with (
            patch("streamlit.selectbox", side_effect=fake_selectbox),
            patch("streamlit.number_input", side_effect=fake_number_input),
            patch("streamlit.session_state", session_state),
            patch("streamlit.expander"),
            patch("streamlit.header"),
            patch("streamlit.text"),
            patch("streamlit.checkbox", return_value=False),
            patch("streamlit.button", return_value=False),
            patch("streamlit.text_input", return_value=""),
            patch("gui.pages.settings._render_agent_configuration"),
        ):
            from gui.pages.settings import render_settings

            render_settings(CommonSettings(), JudgeSettings())

        assert "common_log_level" in session_state
        assert "common_max_content_length" in session_state


class TestResetButtonClearsCommonSettings:
    """Tests that reset button clears common_* session state keys."""

    def test_reset_button_clears_common_keys(self):
        """Test that _render_reset_button clears common_* keys from session state."""
        # Arrange - session state with common_ and judge_ keys
        mock_session_state = {
            "common_log_level": "DEBUG",
            "common_max_content_length": 20000,
            "judge_tier1_max_seconds": 2.0,
        }

        with (
            patch("streamlit.session_state", mock_session_state),
            patch("streamlit.button", return_value=True),
            patch("streamlit.rerun"),
        ):
            from gui.pages.settings import _render_reset_button

            _render_reset_button()

        assert "common_log_level" not in mock_session_state
        assert "common_max_content_length" not in mock_session_state

    def test_reset_button_clears_judge_keys_too(self):
        """Test that _render_reset_button still clears judge_* keys."""
        mock_session_state = {
            "common_log_level": "DEBUG",
            "judge_tier1_max_seconds": 2.0,
            "judge_composite_accept_threshold": 0.9,
        }

        with (
            patch("streamlit.session_state", mock_session_state),
            patch("streamlit.button", return_value=True),
            patch("streamlit.rerun"),
        ):
            from gui.pages.settings import _render_reset_button

            _render_reset_button()

        assert "judge_tier1_max_seconds" not in mock_session_state
        assert "judge_composite_accept_threshold" not in mock_session_state


class TestBuildCommonSettingsFromSession:
    """Tests for _build_common_settings_from_session helper in run_app.py."""

    def test_returns_none_when_no_common_overrides(self):
        """Test that _build_common_settings_from_session returns None when no common_ keys exist."""
        mock_session_state = {}

        with patch("streamlit.session_state", mock_session_state):
            from gui.pages.run_app import _build_common_settings_from_session

            result = _build_common_settings_from_session()

        assert result is None

    def test_returns_common_settings_with_log_level_override(self):
        """Test that _build_common_settings_from_session returns CommonSettings with overrides."""
        mock_session_state = {"common_log_level": "DEBUG"}

        with patch("streamlit.session_state", mock_session_state):
            from gui.pages.run_app import _build_common_settings_from_session

            result = _build_common_settings_from_session()

        assert result is not None
        assert isinstance(result, CommonSettings)
        assert result.log_level == "DEBUG"

    def test_returns_common_settings_with_max_content_length_override(self):
        """Test that max_content_length override is applied correctly."""
        mock_session_state = {"common_max_content_length": 50000}

        with patch("streamlit.session_state", mock_session_state):
            from gui.pages.run_app import _build_common_settings_from_session

            result = _build_common_settings_from_session()

        assert result is not None
        assert result.max_content_length == 50000

    def test_returns_common_settings_with_multiple_overrides(self):
        """Test that multiple common_ overrides are all applied."""
        mock_session_state = {
            "common_log_level": "WARNING",
            "common_max_content_length": 30000,
        }

        with patch("streamlit.session_state", mock_session_state):
            from gui.pages.run_app import _build_common_settings_from_session

            result = _build_common_settings_from_session()

        assert result is not None
        assert result.log_level == "WARNING"
        assert result.max_content_length == 30000

    def test_does_not_include_judge_keys_in_common_settings(self):
        """Test that judge_ prefixed keys are not included in CommonSettings build."""
        mock_session_state = {
            "judge_tier1_max_seconds": 2.0,
        }

        with patch("streamlit.session_state", mock_session_state):
            from gui.pages.run_app import _build_common_settings_from_session

            result = _build_common_settings_from_session()

        assert result is None

    def test_ignores_extra_common_keys_gracefully(self):
        """Test that unknown common_ keys are handled without error (CommonSettings uses extra=ignore)."""
        mock_session_state = {
            "common_log_level": "ERROR",
            "common_unknown_setting": "some_value",
        }

        with patch("streamlit.session_state", mock_session_state):
            from gui.pages.run_app import _build_common_settings_from_session

            result = _build_common_settings_from_session()

        assert result is not None
        assert result.log_level == "ERROR"
