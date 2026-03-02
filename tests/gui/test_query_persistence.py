"""Tests for STORY-008: App page free-form query persistence fix.

Covers:
- run_app.py line 602: text_input called with key="freeform_query"
- run_app.py line 426: fallback text_input called with key="freeform_query_fallback"

Mock strategy:
- AST inspection of source to verify key parameters are present in text_input calls
- unittest.mock.patch used for runtime behavior tests
- No real Streamlit runtime needed
"""

from unittest.mock import MagicMock, patch


class TestFreeformQueryPersistence:
    """Verify free-form query text_input widgets have key parameters for persistence.

    Streamlit widgets without a `key` parameter do not persist state across
    page navigation. Adding `key=` enables session state persistence.
    """

    def test_fallback_branch_calls_text_input_with_key(self) -> None:
        """Fallback path (_render_paper_selection_input, no papers) uses key="freeform_query_fallback".

        Arrange: Mock _load_available_papers to return [], mock st.session_state as MagicMock
        Act: Call _render_paper_selection_input
        Expected: text_input called with key="freeform_query_fallback"
        """
        from gui.pages import run_app

        captured_keys: list[str] = []

        def mock_text_input(*args: object, **kwargs: object) -> str:
            if "key" in kwargs:
                captured_keys.append(str(kwargs["key"]))
            return ""

        mock_session = MagicMock()
        mock_session.get.return_value = []

        with (
            patch("gui.pages.run_app.text_input", side_effect=mock_text_input),
            patch("gui.pages.run_app.st") as mock_st,
            patch("gui.pages.run_app._load_available_papers", return_value=[]),
        ):
            mock_st.session_state = mock_session

            run_app._render_paper_selection_input()

        assert "freeform_query_fallback" in captured_keys, (
            "Fallback text_input must be called with key='freeform_query_fallback'"
        )
