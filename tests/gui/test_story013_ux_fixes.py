"""
Tests for STORY-013: App page UX + Evaluation page UX fixes.

Covers:
- output.py: rename `type` → `output_type` parameter (shadows built-in)
- run_app.py: _execute_query_background stores execution_id in session state
- evaluation.py: _render_overall_results displays execution_id caption
- evaluation.py: Baseline path validation with st.error on missing directory

Mock strategy:
- Streamlit widgets patched throughout
- inspect.signature used for parameter presence checks
- No real Streamlit runtime needed
"""

import inspect
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# 1. output.py — rename `type` → `output_type` parameter
# ---------------------------------------------------------------------------


class TestOutputTypeParameterRename:
    """Verify render_output uses `output_type` instead of `type`.

    `type` shadows Python's built-in — STORY-013 renames it.
    """

    def test_render_output_has_output_type_parameter(self) -> None:
        """render_output signature must have `output_type` parameter, not `type`."""
        from gui.components.output import render_output

        sig = inspect.signature(render_output)
        assert "output_type" in sig.parameters, (
            "render_output must have `output_type` parameter (renamed from `type`)"
        )

    def test_render_output_does_not_have_type_parameter(self) -> None:
        """render_output signature must NOT have `type` parameter (shadows built-in)."""
        from gui.components.output import render_output

        sig = inspect.signature(render_output)
        assert "type" not in sig.parameters, (
            "render_output must not shadow built-in `type` — rename to `output_type`"
        )


# ---------------------------------------------------------------------------
# 2. run_app.py — execution_id stored in session state
# ---------------------------------------------------------------------------


class TestExecutionIdThreading:
    """Verify _execute_query_background stores execution_id in session state.

    The execution_id is returned by app.main() (via _prepare_result_dict),
    and _execute_query_background must store it for the evaluation page.
    """

    def test_execute_query_background_stores_execution_id(self) -> None:
        """execution_id from main() result must be stored in session state.

        Arrange: Mock main() to return dict with execution_id
        Act: Call _execute_query_background
        Expected: st.session_state["execution_id"] contains the returned ID
        """
        import asyncio

        from gui.pages import run_app

        fake_execution_id = "exec_abc123456789"
        mock_result = {
            "composite_result": MagicMock(),
            "graph": MagicMock(),
            "execution_id": fake_execution_id,
        }

        # Use MagicMock to support both attribute-access and dict-like session state
        mock_session_state = MagicMock()
        captured: dict = {}

        # MagicMock magic methods receive (self, *args) — ignore self with *args form
        mock_session_state.__setitem__ = lambda *args: captured.__setitem__(args[1], args[2])
        mock_session_state.__getitem__ = lambda *args: captured[args[1]]
        mock_session_state.get = lambda key, default=None: captured.get(key, default)

        with (
            patch("gui.pages.run_app.main", new_callable=AsyncMock, return_value=mock_result),
            patch("gui.pages.run_app.LogCapture") as mock_log_capture,
            patch("gui.pages.run_app.st") as mock_st,
        ):
            # Setup LogCapture mock
            mock_capture_instance = MagicMock()
            mock_capture_instance.get_logs.return_value = []
            mock_capture_instance.attach_to_logger.return_value = "handler_id"
            mock_log_capture.return_value = mock_capture_instance
            mock_log_capture.format_logs_as_html = MagicMock(return_value="<html/>")

            # Track session_state item assignments
            mock_st.session_state = mock_session_state

            asyncio.run(
                run_app._execute_query_background(
                    query="test query",
                    provider="openai",
                    include_researcher=False,
                    include_analyst=False,
                    include_synthesiser=False,
                    chat_config_file=None,
                )
            )

        assert captured.get("execution_id") == fake_execution_id, (
            "_execute_query_background must store execution_id in session_state"
        )

    def test_execute_query_background_no_execution_id_when_result_none(self) -> None:
        """When main() returns None, execution_id should be None in session state.

        Arrange: Mock main() to return None
        Act: Call _execute_query_background
        Expected: session_state["execution_id"] is None
        """
        import asyncio

        from gui.pages import run_app

        captured: dict = {}

        mock_session_state = MagicMock()

        def setitem(key: str, value: object) -> None:
            captured[key] = value

        mock_session_state.__setitem__ = setitem
        mock_session_state.__getitem__ = lambda self, key: captured[key]
        mock_session_state.get = lambda key, default=None: captured.get(key, default)

        with (
            patch("gui.pages.run_app.main", new_callable=AsyncMock, return_value=None),
            patch("gui.pages.run_app.LogCapture") as mock_log_capture,
            patch("gui.pages.run_app.st") as mock_st,
        ):
            mock_capture_instance = MagicMock()
            mock_capture_instance.get_logs.return_value = []
            mock_capture_instance.attach_to_logger.return_value = "handler_id"
            mock_log_capture.return_value = mock_capture_instance
            mock_log_capture.format_logs_as_html = MagicMock(return_value="<html/>")

            mock_st.session_state = mock_session_state

            asyncio.run(
                run_app._execute_query_background(
                    query="test query",
                    provider="openai",
                    include_researcher=False,
                    include_analyst=False,
                    include_synthesiser=False,
                    chat_config_file=None,
                )
            )

        # Should be None when no result
        assert captured.get("execution_id") is None, (
            "execution_id should be None when main() returns no result"
        )


# ---------------------------------------------------------------------------
# 4. evaluation.py — run ID display in _render_overall_results
# ---------------------------------------------------------------------------


class TestEvaluationRunIdDisplay:
    """Verify _render_overall_results displays a shortened run ID from session state.

    The execution_id is stored by _execute_query_background and should be
    displayed as a caption/metric on the Evaluation Results page.
    """

    def test_render_overall_results_displays_execution_id(self) -> None:
        """_render_overall_results must display execution_id from session state.

        Arrange: Mock st.session_state with execution_id, mock result
        Act: Call _render_overall_results
        Expected: st.caption or st.markdown called with execution_id
        """
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages import evaluation

        mock_result = MagicMock(spec=CompositeResult)
        mock_result.composite_score = 0.75
        mock_result.recommendation = "accept"
        mock_result.recommendation_weight = 0.8

        session_state = {"execution_id": "exec_abc123456789"}

        with (
            patch("streamlit.columns") as mock_cols,
            patch("streamlit.metric"),
            patch("streamlit.caption") as mock_caption,
            patch("streamlit.subheader"),
            patch("streamlit.session_state", session_state),
        ):
            # Mock column context managers
            mock_col = MagicMock()
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=False)
            mock_cols.return_value = [mock_col, mock_col, mock_col]

            evaluation._render_overall_results(mock_result)

        # Check that caption was called with execution_id content
        all_caption_calls = [str(c) for c in mock_caption.call_args_list]
        assert any("exec_abc123456789" in c for c in all_caption_calls), (
            "_render_overall_results must display execution_id via st.caption"
        )


# ---------------------------------------------------------------------------
# 5. evaluation.py — baseline path validation
# ---------------------------------------------------------------------------


class TestBaselinePathValidation:
    """Verify baseline comparison inputs validate directory existence.

    Paths entered by the user in Baseline Comparison Configuration should
    be checked with Path.is_dir() — if invalid, st.error is shown.
    """

    def test_invalid_cc_solo_dir_shows_error(self) -> None:
        """A non-existent CC solo directory path shows st.error.

        Arrange: text_input returns a path that does not exist on disk
        Act: Call render_evaluation with no result (shows baseline config)
        Expected: st.error called indicating the directory does not exist
        """
        from gui.pages import evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.info"),
            patch("streamlit.expander") as mock_expander,
            patch("streamlit.markdown"),
            patch("streamlit.text_input") as mock_text_input,
            patch("streamlit.error") as mock_error,
            patch("streamlit.session_state", {}),
        ):
            # Mock expander context manager
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_expander.return_value = mock_ctx

            # Simulate user entering a non-existent path
            mock_text_input.side_effect = [
                "/nonexistent/cc_solo_path",  # cc_solo_dir_input
                "/nonexistent/cc_teams_path",  # cc_teams_dir_input
            ]

            evaluation.render_evaluation(result=None)

        # Verify error was shown for invalid path
        assert mock_error.called, (
            "st.error must be called when baseline directory path does not exist"
        )

    def test_valid_cc_solo_dir_no_error(self, tmp_path: Path) -> None:
        """A valid CC solo directory path does not show st.error.

        Arrange: text_input returns a path that exists on disk (tmp_path)
        Act: Call render_evaluation with no result
        Expected: st.error NOT called for the valid path
        """
        from gui.pages import evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.info"),
            patch("streamlit.expander") as mock_expander,
            patch("streamlit.markdown"),
            patch("streamlit.text_input") as mock_text_input,
            patch("streamlit.error") as mock_error,
            patch("streamlit.session_state", {}),
        ):
            # Mock expander context manager
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_expander.return_value = mock_ctx

            # Simulate user entering a valid path (tmp_path exists)
            mock_text_input.side_effect = [
                str(tmp_path),  # cc_solo_dir_input — valid
                "",  # cc_teams_dir_input — empty (no validation needed)
            ]

            evaluation.render_evaluation(result=None)

        # No error for valid directory
        assert not mock_error.called, "st.error must NOT be called when the directory path is valid"

    def test_empty_dir_input_skips_validation(self) -> None:
        """An empty directory input is not validated (user hasn't entered anything).

        Arrange: text_input returns empty strings
        Act: Call render_evaluation with no result
        Expected: st.error NOT called for empty inputs
        """
        from gui.pages import evaluation

        with (
            patch("streamlit.header"),
            patch("streamlit.info"),
            patch("streamlit.expander") as mock_expander,
            patch("streamlit.markdown"),
            patch("streamlit.text_input", return_value=""),
            patch("streamlit.error") as mock_error,
            patch("streamlit.session_state", {}),
        ):
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_expander.return_value = mock_ctx

            evaluation.render_evaluation(result=None)

        assert not mock_error.called, "st.error must NOT be called when directory input is empty"


# ---------------------------------------------------------------------------
# 6. evaluation.py — Evaluation Details expander shows full execution_id
# ---------------------------------------------------------------------------


class TestEvaluationDetailsShowsExecutionId:
    """Verify 'Evaluation Details' expander includes the full execution_id.

    The expander shows metadata like timestamp and config_version.
    It must also show the execution_id from session state.
    """

    def test_evaluation_details_expander_shows_execution_id(self) -> None:
        """Evaluation Details expander must display full execution_id.

        Arrange: Mock result and session state with execution_id
        Act: Call render_evaluation with a valid result
        Expected: st.text or st.caption called with execution_id content in expander
        """
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages import evaluation

        mock_result = MagicMock(spec=CompositeResult)
        mock_result.composite_score = 0.75
        mock_result.recommendation = "accept"
        mock_result.recommendation_weight = 0.8
        mock_result.tier1_score = 0.7
        mock_result.tier2_score = 0.8
        mock_result.tier3_score = 0.75
        mock_result.evaluation_complete = True
        mock_result.metric_scores = {}
        mock_result.timestamp = "2026-02-18T00:00:00"
        mock_result.config_version = "1.0.0"
        mock_result.weights_used = {}

        session_state = {"execution_id": "exec_full123456789"}

        with (
            patch("streamlit.header"),
            patch("streamlit.subheader"),
            patch("streamlit.columns") as mock_cols,
            patch("streamlit.metric"),
            patch("streamlit.caption"),
            patch("streamlit.warning"),
            patch("streamlit.info"),
            patch("streamlit.bar_chart"),
            patch("streamlit.dataframe"),
            patch("streamlit.expander") as mock_expander,
            patch("streamlit.text") as mock_text,
            patch("streamlit.session_state", session_state),
        ):
            mock_col = MagicMock()
            mock_col.__enter__ = MagicMock(return_value=mock_col)
            mock_col.__exit__ = MagicMock(return_value=False)
            mock_cols.return_value = [mock_col, mock_col, mock_col]

            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_expander.return_value = mock_ctx

            evaluation.render_evaluation(result=mock_result)

        # Check st.text was called with execution_id somewhere
        all_text_calls = [str(c) for c in mock_text.call_args_list]
        assert any("exec_full123456789" in c for c in all_text_calls), (
            "Evaluation Details expander must show full execution_id via st.text"
        )
