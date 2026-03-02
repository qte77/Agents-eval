"""
Tests for GUI session state initialization and persistence.

This module tests session state defaults for provider selection and
sub-agent configuration in the Streamlit GUI.
"""

from inline_snapshot import snapshot

from app.config.config_app import CHAT_DEFAULT_PROVIDER


def test_session_state_defaults_structure():
    """Test session state defaults match expected structure using inline-snapshot."""
    # Arrange: Import the session state initialization function
    from run_gui import get_session_state_defaults

    # Act: Get the default session state structure
    defaults = get_session_state_defaults()

    # Assert: Verify structure matches expected schema
    # S8-F8.1: researcher and analyst default to True for better UX
    assert defaults == snapshot(
        {
            "chat_provider": CHAT_DEFAULT_PROVIDER,
            "include_researcher": False,
            "include_analyst": False,
            "include_synthesiser": False,
        }
    )
