"""Tests for STORY-009: UI string constants consolidated in text.py.

Verifies that header/subheader/label strings are defined as constants
in gui.config.text and used by their respective pages instead of inline literals.
"""

import ast
import importlib
import inspect


def test_evaluation_constants_exist_in_text():
    """All evaluation page string constants exist in text.py."""
    from gui.config import text

    assert hasattr(text, "EVALUATION_HEADER")
    assert hasattr(text, "EVALUATION_OVERALL_RESULTS_SUBHEADER")
    assert hasattr(text, "EVALUATION_TIER_SCORES_SUBHEADER")
    assert hasattr(text, "EVALUATION_METRICS_COMPARISON_SUBHEADER")

    assert text.EVALUATION_HEADER == "Evaluation Results"
    assert text.EVALUATION_OVERALL_RESULTS_SUBHEADER == "Overall Results"
    assert text.EVALUATION_TIER_SCORES_SUBHEADER == "Tier Scores"
    assert (
        text.EVALUATION_METRICS_COMPARISON_SUBHEADER == "Graph Metrics vs Text Metrics Comparison"
    )


def test_agent_graph_constants_exist_in_text():
    """All agent graph page string constants exist in text.py."""
    from gui.config import text

    assert hasattr(text, "AGENT_GRAPH_HEADER")
    assert hasattr(text, "AGENT_GRAPH_NETWORK_SUBHEADER")

    assert text.AGENT_GRAPH_HEADER == "\U0001f578\ufe0f Agent Interaction Graph"
    assert text.AGENT_GRAPH_NETWORK_SUBHEADER == "Interactive Agent Network Visualization"


def test_run_app_label_constants_exist_in_text():
    """Debug Log, Generate Report, Download Report labels exist in text.py."""
    from gui.config import text

    assert hasattr(text, "DEBUG_LOG_LABEL")
    assert hasattr(text, "GENERATE_REPORT_LABEL")
    assert hasattr(text, "DOWNLOAD_REPORT_LABEL")

    assert text.DEBUG_LOG_LABEL == "Debug Log"
    assert text.GENERATE_REPORT_LABEL == "Generate Report"
    assert text.DOWNLOAD_REPORT_LABEL == "Download Report"


def _get_module_source(module_name: str) -> str:
    """Get source code of a module by name."""
    mod = importlib.import_module(module_name)
    return inspect.getsource(mod)


def _module_imports_name(module_name: str, imported_name: str) -> bool:
    """Check if a module imports a specific name from gui.config.text."""
    source = _get_module_source(module_name)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "text" in node.module:
                for alias in node.names:
                    if alias.name == imported_name:
                        return True
    return False


def test_evaluation_page_imports_constants():
    """evaluation.py imports string constants from text.py."""
    assert _module_imports_name("gui.pages.evaluation", "EVALUATION_HEADER")
    assert _module_imports_name("gui.pages.evaluation", "EVALUATION_OVERALL_RESULTS_SUBHEADER")
    assert _module_imports_name("gui.pages.evaluation", "EVALUATION_TIER_SCORES_SUBHEADER")
    assert _module_imports_name("gui.pages.evaluation", "EVALUATION_METRICS_COMPARISON_SUBHEADER")


def test_agent_graph_page_imports_constants():
    """agent_graph.py imports string constants from text.py."""
    assert _module_imports_name("gui.pages.agent_graph", "AGENT_GRAPH_HEADER")
    assert _module_imports_name("gui.pages.agent_graph", "AGENT_GRAPH_NETWORK_SUBHEADER")


def test_run_app_page_imports_label_constants():
    """run_app.py imports label constants from text.py."""
    assert _module_imports_name("gui.pages.run_app", "DEBUG_LOG_LABEL")
    assert _module_imports_name("gui.pages.run_app", "GENERATE_REPORT_LABEL")
    assert _module_imports_name("gui.pages.run_app", "DOWNLOAD_REPORT_LABEL")


def test_evaluation_page_no_inline_header_strings():
    """evaluation.py should not contain inline header/subheader string literals."""
    source = _get_module_source("gui.pages.evaluation")
    # These inline strings should be replaced by constants
    assert 'st.header("Evaluation Results")' not in source
    assert 'st.subheader("Overall Results")' not in source
    assert 'st.subheader("Tier Scores")' not in source
    assert 'st.subheader("Graph Metrics vs Text Metrics Comparison")' not in source


def test_agent_graph_page_no_inline_header_strings():
    """agent_graph.py should not contain inline header/subheader string literals."""
    source = _get_module_source("gui.pages.agent_graph")
    assert 'st.header("\U0001f578\ufe0f Agent Interaction Graph")' not in source
    assert 'st.subheader("Interactive Agent Network Visualization")' not in source


def test_run_app_page_no_inline_label_strings():
    """run_app.py should not contain inline label string literals for Debug Log, Generate Report, Download Report."""
    source = _get_module_source("gui.pages.run_app")
    assert 'st.expander("Debug Log"' not in source
    assert 'st.button("Generate Report"' not in source
    assert 'label="Download Report"' not in source
