"""
Tests for the editable settings page.

This module tests the behavior of the settings page UI components,
including editable judge settings fields, session state persistence,
and reset functionality.
"""

from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.common.settings import CommonSettings
from app.judge.settings import JudgeSettings
from gui.pages.settings import render_settings


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing."""
    with (
        patch("gui.pages.settings.st") as mock_st,
        patch("gui.pages.settings.button") as mock_button,
        patch("gui.pages.settings.checkbox") as mock_checkbox,
        patch("gui.pages.settings.number_input") as mock_number_input,
        patch("gui.pages.settings.selectbox") as mock_selectbox,
        patch("gui.pages.settings.text_input") as mock_text_input,
        patch("gui.pages.settings.text") as mock_text,
        patch("gui.pages.settings.header") as mock_header,
        patch("gui.pages.settings.expander") as mock_expander,
    ):
        # Setup session_state as a dict
        mock_st.session_state = {}

        # Mock component functions to return values and store in session_state
        def number_input_side_effect(label, **kwargs):
            value = kwargs.get("value", 0)
            key = kwargs.get("key", "")
            if key:
                mock_st.session_state[key] = value
            return value

        def checkbox_side_effect(label, **kwargs):
            value = kwargs.get("value", False)
            key = kwargs.get("key", "")
            if key:
                mock_st.session_state[key] = value
            return value

        def text_input_side_effect(label, **kwargs):
            value = kwargs.get("value", "")
            key = kwargs.get("key", "")
            if key:
                mock_st.session_state[key] = value
            return value

        def selectbox_side_effect(label, **kwargs):
            value = kwargs.get("value", "")
            key = kwargs.get("key", "")
            if key:
                mock_st.session_state[key] = value
            return value

        # Wire up the mock functions
        mock_number_input.side_effect = number_input_side_effect
        mock_checkbox.side_effect = checkbox_side_effect
        mock_text_input.side_effect = text_input_side_effect
        mock_selectbox.side_effect = selectbox_side_effect
        mock_button.return_value = False
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()

        # Store references for test assertions
        mock_st.number_input = mock_number_input
        mock_st.checkbox = mock_checkbox
        mock_st.text_input = mock_text_input
        mock_st.selectbox = mock_selectbox
        mock_st.button = mock_button
        mock_st.expander = mock_expander
        mock_st.text = mock_text
        mock_st.header = mock_header
        mock_st.rerun = MagicMock()

        yield mock_st


def test_judge_settings_fields_are_editable(mock_streamlit):
    """Test that JudgeSettings fields are rendered as editable widgets.

    Verifies that key judge settings are displayed as interactive input
    components (number_input, selectbox, text_input, checkbox) rather than
    read-only text.
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    render_settings(common_settings, judge_settings)

    # Verify tier timeout fields are editable (number_input)
    # Should be called at least once for tier timeouts
    assert mock_streamlit.number_input.called

    # Verify provider fields are editable (selectbox or text_input)
    # Should be called for tier2_provider, tier2_model, etc.
    selectbox_or_text_called = mock_streamlit.selectbox.called or mock_streamlit.text_input.called
    assert selectbox_or_text_called

    # Verify boolean fields are editable (checkbox)
    # Should be called for logfire_enabled, trace_collection, etc.
    assert mock_streamlit.checkbox.called


def test_settings_stored_in_session_state(mock_streamlit):
    """Test that changed settings are stored in session state.

    Verifies that when a user changes a setting via the GUI, the new value
    is persisted to st.session_state so it can be used by run_app.py.
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    # Simulate user changing tier2_timeout_seconds to 60
    mock_streamlit.session_state["judge_tier2_timeout_seconds"] = 60.0

    render_settings(common_settings, judge_settings)

    # Verify the value is in session state
    assert "judge_tier2_timeout_seconds" in mock_streamlit.session_state
    assert mock_streamlit.session_state["judge_tier2_timeout_seconds"] == 60.0


def test_reset_to_defaults_button_exists(mock_streamlit):
    """Test that a 'Reset to Defaults' button is present.

    Verifies that the settings page includes a button to restore default
    JudgeSettings values, clearing any user customizations.
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    render_settings(common_settings, judge_settings)

    # Verify button was called with 'Reset' in the label
    button_calls = [call[0][0] for call in mock_streamlit.button.call_args_list]
    assert any("Reset" in label for label in button_calls)


def test_reset_button_clears_session_state(mock_streamlit):
    """Test that clicking 'Reset to Defaults' clears custom settings.

    Verifies that when the reset button is clicked, all judge settings
    in session state are removed, reverting to JudgeSettings() defaults.
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    # Simulate user having customized settings
    mock_streamlit.session_state["judge_tier2_timeout_seconds"] = 60.0
    mock_streamlit.session_state["judge_composite_accept_threshold"] = 0.9

    # Simulate button click
    mock_streamlit.button.return_value = True

    render_settings(common_settings, judge_settings)

    # Verify session state was cleared (or settings were reset)
    # Implementation should either clear keys or reset to defaults
    # We'll check that at least one approach was taken
    cleared = "judge_tier2_timeout_seconds" not in mock_streamlit.session_state
    reset_to_default = (
        mock_streamlit.session_state.get("judge_tier2_timeout_seconds")
        == JudgeSettings().tier2_timeout_seconds
    )

    assert cleared or reset_to_default


@given(
    timeout_value=st.floats(min_value=0.1, max_value=300.0),
    threshold_value=st.floats(min_value=0.0, max_value=1.0),
)
def test_settings_value_bounds_hypothesis(timeout_value: float, threshold_value: float):
    """Property test: Settings values respect Pydantic field constraints.

    Verifies that input validation matches JudgeSettings field constraints:
    - timeout values: gt=0, le=300
    - threshold values: ge=0, le=1

    Args:
        timeout_value: Random timeout value to validate
        threshold_value: Random threshold value to validate
    """
    # Test that valid values are accepted
    judge_settings = JudgeSettings(
        tier2_timeout_seconds=timeout_value,
        composite_accept_threshold=threshold_value,
    )

    # Verify values are within constraints
    assert 0 < judge_settings.tier2_timeout_seconds <= 300
    assert 0 <= judge_settings.composite_accept_threshold <= 1


def test_settings_page_widget_structure_snapshot(mock_streamlit):
    """Snapshot test: Verify settings page widget structure.

    Captures the structure of widgets rendered on the settings page to
    detect unintended changes in layout or component types.
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    render_settings(common_settings, judge_settings)

    # Capture widget call counts and types
    widget_structure = {
        "number_input_calls": mock_streamlit.number_input.call_count,
        "checkbox_calls": mock_streamlit.checkbox.call_count,
        "text_input_calls": mock_streamlit.text_input.call_count,
        "selectbox_calls": mock_streamlit.selectbox.call_count,
        "button_calls": mock_streamlit.button.call_count,
    }

    # Snapshot the structure
    # Note: Exact counts will be determined after implementation
    assert widget_structure == snapshot(
        {
            "number_input_calls": 10,
            "checkbox_calls": 5,
            "text_input_calls": 5,
            "selectbox_calls": 2,
            "button_calls": 1,
        }
    )


def test_composite_thresholds_are_editable(mock_streamlit):
    """Test that composite scoring thresholds are editable.

    Verifies that composite_accept_threshold, composite_weak_accept_threshold,
    and composite_weak_reject_threshold are rendered as editable number inputs.
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    render_settings(common_settings, judge_settings)

    # Check that number_input was called for threshold fields
    # We expect at least 3 calls for the threshold values
    assert mock_streamlit.number_input.call_count >= 3


def test_observability_settings_are_editable(mock_streamlit):
    """Test that observability settings are editable.

    Verifies that logfire_enabled, phoenix_endpoint, and trace_collection
    are rendered as editable widgets (checkbox for booleans, text_input for URLs).
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    render_settings(common_settings, judge_settings)

    # Verify checkbox used for boolean observability settings
    assert mock_streamlit.checkbox.call_count >= 2  # logfire_enabled, trace_collection

    # Verify text_input used for phoenix_endpoint
    assert mock_streamlit.text_input.call_count >= 1


def test_tier_provider_and_model_are_editable(mock_streamlit):
    """Test that tier2_provider and tier2_model are editable.

    Verifies that provider and model fields for Tier 2 are rendered as
    editable components (selectbox or text_input).
    """
    common_settings = CommonSettings()
    judge_settings = JudgeSettings()

    render_settings(common_settings, judge_settings)

    # Verify that provider/model fields are editable
    # At minimum, tier2_provider, tier2_model, tier2_fallback_provider, tier2_fallback_model
    selectbox_or_text_count = (
        mock_streamlit.selectbox.call_count + mock_streamlit.text_input.call_count
    )
    assert selectbox_or_text_count >= 4
