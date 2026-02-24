"""Tests for STORY-008: App page free-form query persistence fix.

Covers:
- run_app.py line 602: text_input called with key="freeform_query"
- run_app.py line 426: fallback text_input called with key="freeform_query_fallback"

Mock strategy:
- AST inspection of source to verify key parameters are present in text_input calls
- unittest.mock.patch used for runtime behavior tests
- No real Streamlit runtime needed
"""

import ast
import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch


def _get_run_app_source() -> tuple[str, ast.Module]:
    """Return source text and parsed AST for run_app.py."""
    import gui.pages.run_app as run_app_module

    source_path = Path(inspect.getfile(run_app_module))
    source = source_path.read_text()
    return source, ast.parse(source)


def _find_text_input_keys(tree: ast.Module) -> set[str]:
    """Walk AST and return all key= values passed to text_input calls."""
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        func_name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
        if func_name != "text_input":
            continue
        for keyword in node.keywords:
            if keyword.arg == "key" and isinstance(keyword.value, ast.Constant):
                keys.add(keyword.value.value)
    return keys


class TestFreeformQueryPersistence:
    """Verify free-form query text_input widgets have key parameters for persistence.

    Streamlit widgets without a `key` parameter do not persist state across
    page navigation. Adding `key=` enables session state persistence.
    """

    def test_freeform_query_text_input_has_key(self) -> None:
        """Free-form query text_input (line ~602) must be called with key="freeform_query".

        Arrange: Parse run_app.py AST
        Act: Walk all text_input call nodes and collect key= values
        Expected: "freeform_query" appears in collected keys
        """
        _, tree = _get_run_app_source()
        keys = _find_text_input_keys(tree)
        assert "freeform_query" in keys, (
            "text_input must be called with key='freeform_query' in run_app.py (line ~602)"
        )

    def test_fallback_query_text_input_has_key(self) -> None:
        """Fallback text_input (line ~426) must be called with key="freeform_query_fallback".

        Arrange: Parse run_app.py AST
        Act: Walk all text_input call nodes and collect key= values
        Expected: "freeform_query_fallback" appears in collected keys
        """
        _, tree = _get_run_app_source()
        keys = _find_text_input_keys(tree)
        assert "freeform_query_fallback" in keys, (
            "text_input must be called with key='freeform_query_fallback' in run_app.py (line ~426)"
        )

    def test_no_widget_key_conflicts(self) -> None:
        """Widget keys must be unique — no duplicates in run_app.py text_input calls.

        Arrange: Parse run_app.py AST
        Act: Collect all text_input key= values (duplicates would reduce the set)
        Expected: Count of all key occurrences equals count of unique keys
        """
        _, tree = _get_run_app_source()

        all_keys: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            func_name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if func_name != "text_input":
                continue
            for keyword in node.keywords:
                if keyword.arg == "key" and isinstance(keyword.value, ast.Constant):
                    all_keys.append(keyword.value.value)

        assert len(all_keys) == len(set(all_keys)), (
            f"Duplicate text_input key= values found in run_app.py: {all_keys}"
        )

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
