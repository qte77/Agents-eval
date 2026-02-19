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
    assert defaults == snapshot(
        {
            "chat_provider": CHAT_DEFAULT_PROVIDER,
            "include_researcher": False,
            "include_analyst": False,
            "include_synthesiser": False,
        }
    )


def test_session_state_provider_is_valid():
    """Test that default provider exists in PROVIDER_REGISTRY."""
    # Arrange
    from app.data_models.app_models import PROVIDER_REGISTRY
    from run_gui import get_session_state_defaults

    # Act
    defaults = get_session_state_defaults()
    provider = defaults["chat_provider"]

    # Assert: Provider must be in registry
    assert provider in PROVIDER_REGISTRY, f"Default provider '{provider}' not in PROVIDER_REGISTRY"


def test_session_state_all_agents_disabled_by_default():
    """Test that all sub-agents are disabled by default."""
    # Arrange
    from run_gui import get_session_state_defaults

    # Act
    defaults = get_session_state_defaults()

    # Assert: All agent flags should be False
    assert defaults["include_researcher"] is False
    assert defaults["include_analyst"] is False
    assert defaults["include_synthesiser"] is False
