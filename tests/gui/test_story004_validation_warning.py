"""Tests for STORY-004: Fix validation warning placement on Run page.

The validation warning for empty query/paper fires inside the async handler
(_handle_query_submission) and disappears on Streamlit rerender. The fix moves
validation to render_app() scope and uses session_state to persist the warning.

Mock strategy:
- Use _SessionDict (dict with attribute access) to simulate st.session_state
- Patch gui.pages.run_app.<widget> for directly imported streamlit functions
- Patch streamlit.<widget> for functions accessed via st.<widget>
- Assert session_state flag is set when validation fails
- Assert st.warning() is called in render scope (not inside async handler)
- Assert warning clears when valid input is provided
"""

from unittest.mock import MagicMock, patch

import pytest

# Prefix for patching directly imported streamlit functions in run_app
_RA = "gui.pages.run_app"


class _SessionDict(dict):
    """Dict subclass that supports attribute access like st.session_state."""

    def __getattr__(self, key: str) -> object:
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key: str, value: object) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


class TestValidationWarningSessionState:
    """Verify that validation warning state is managed via session_state."""

    @pytest.mark.asyncio
    async def test_empty_input_sets_validation_warning_flag(self) -> None:
        """When Run is clicked with no query and no paper, show_validation_warning must be True."""
        from gui.pages.run_app import render_app

        mock_session = _SessionDict()

        with (
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.header"),
            patch("streamlit.radio", return_value="Multi-Agent System (MAS)"),
            patch(f"{_RA}.text_input", return_value=""),
            patch(f"{_RA}.button", return_value=True),
            patch("streamlit.markdown"),
            patch(f"{_RA}.info"),
            patch(f"{_RA}.subheader"),
            patch(f"{_RA}.warning"),
            patch("streamlit.expander") as mock_expander,
            patch(f"{_RA}.spinner") as mock_spinner,
            patch("streamlit.checkbox"),
            patch(f"{_RA}.render_output"),
            patch(f"{_RA}._load_available_papers", return_value=[]),
        ):
            mock_expander.return_value.__enter__ = MagicMock(return_value=None)
            mock_expander.return_value.__exit__ = MagicMock(return_value=False)
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            await render_app()

        assert mock_session.get("show_validation_warning") is True, (
            "session_state['show_validation_warning'] must be True when input is empty"
        )

    @pytest.mark.asyncio
    async def test_valid_input_clears_validation_warning_flag(self) -> None:
        """When valid query is provided, show_validation_warning must be cleared."""
        from gui.pages.run_app import render_app

        mock_session = _SessionDict({"show_validation_warning": True})

        with (
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.header"),
            patch("streamlit.radio", return_value="Multi-Agent System (MAS)"),
            patch(f"{_RA}.text_input", return_value="Evaluate this paper"),
            patch(f"{_RA}.button", return_value=True),
            patch("streamlit.markdown"),
            patch(f"{_RA}.info"),
            patch(f"{_RA}.subheader"),
            patch(f"{_RA}.warning"),
            patch("streamlit.expander") as mock_expander,
            patch(f"{_RA}.spinner") as mock_spinner,
            patch("streamlit.checkbox"),
            patch("streamlit.rerun", side_effect=Exception("rerun")),
            patch(f"{_RA}.render_output"),
            patch(f"{_RA}._load_available_papers", return_value=[]),
            patch(f"{_RA}._execute_query_background"),
            patch(f"{_RA}._build_judge_settings_from_session", return_value=None),
            patch(f"{_RA}._build_common_settings_from_session", return_value=None),
        ):
            mock_expander.return_value.__enter__ = MagicMock(return_value=None)
            mock_expander.return_value.__exit__ = MagicMock(return_value=False)
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            try:
                await render_app()
            except Exception:
                pass  # st.rerun() raises to halt execution

        assert not mock_session.get("show_validation_warning"), (
            "show_validation_warning must be cleared when valid input is provided"
        )


class TestValidationWarningRenderedNearButton:
    """Verify that st.warning() is called in render_app scope, not inside async handler."""

    @pytest.mark.asyncio
    async def test_warning_rendered_when_flag_is_set(self) -> None:
        """When show_validation_warning is True, st.warning() must be called in render scope."""
        from gui.pages.run_app import render_app

        mock_session = _SessionDict({"show_validation_warning": True})

        with (
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.header"),
            patch("streamlit.radio", return_value="Multi-Agent System (MAS)"),
            patch(f"{_RA}.text_input", return_value=""),
            patch(f"{_RA}.button", return_value=False),
            patch("streamlit.markdown"),
            patch(f"{_RA}.info"),
            patch(f"{_RA}.subheader"),
            patch(f"{_RA}.warning") as mock_warning,
            patch("streamlit.expander") as mock_expander,
            patch(f"{_RA}.spinner") as mock_spinner,
            patch("streamlit.checkbox"),
            patch(f"{_RA}.render_output"),
            patch(f"{_RA}._load_available_papers", return_value=[]),
        ):
            mock_expander.return_value.__enter__ = MagicMock(return_value=None)
            mock_expander.return_value.__exit__ = MagicMock(return_value=False)
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            await render_app()

        mock_warning.assert_called()
        warning_text = str(mock_warning.call_args_list[0].args[0])
        assert "query" in warning_text.lower() or "enter" in warning_text.lower(), (
            f"Warning must mention query input. Got: {warning_text}"
        )

    @pytest.mark.asyncio
    async def test_warning_not_rendered_when_flag_is_false(self) -> None:
        """When show_validation_warning is False, st.warning() must NOT be called."""
        from gui.pages.run_app import render_app

        mock_session = _SessionDict({"show_validation_warning": False})

        with (
            patch("streamlit.session_state", mock_session),
            patch(f"{_RA}.header"),
            patch("streamlit.radio", return_value="Multi-Agent System (MAS)"),
            patch(f"{_RA}.text_input", return_value=""),
            patch(f"{_RA}.button", return_value=False),
            patch("streamlit.markdown"),
            patch(f"{_RA}.info"),
            patch(f"{_RA}.subheader"),
            patch(f"{_RA}.warning") as mock_warning,
            patch("streamlit.expander") as mock_expander,
            patch(f"{_RA}.spinner") as mock_spinner,
            patch("streamlit.checkbox"),
            patch(f"{_RA}.render_output"),
            patch(f"{_RA}._load_available_papers", return_value=[]),
        ):
            mock_expander.return_value.__enter__ = MagicMock(return_value=None)
            mock_expander.return_value.__exit__ = MagicMock(return_value=False)
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            await render_app()

        # st.warning should not be called for validation (CC warning may still fire)
        validation_warning_calls = [
            c for c in mock_warning.call_args_list
            if c.args and "query" in str(c.args[0]).lower()
        ]
        assert not validation_warning_calls, (
            "st.warning() for validation must NOT be called when flag is False"
        )
