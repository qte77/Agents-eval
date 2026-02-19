"""
Tests for STORY-007: GUI polish for run_app.py, evaluation.py, sidebar.py.

Covers:
- ARIA live regions (role="status", role="alert") in run_app.py
- Dead "Downloads page" reference fix in _render_paper_selection_input
- help= kwarg on engine selector and paper selectbox
- Post-run navigation guidance after completion
- Sidebar execution-in-progress indicator
- Human-readable metric labels in evaluation.py
- Baseline comparison inputs wrapped in collapsed expander
- Dataframe alt text below bar charts
- Delta indicators populated from BaselineComparison.tier_deltas
- Tabular display for metric columns (st.dataframe or tabular-nums HTML)

Mock strategy:
- Streamlit widgets (st.info, st.markdown, st.metric, st.dataframe, etc.) patched
- inspect.signature used for parameter presence checks
- No real Streamlit runtime needed
"""

import inspect
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# 1. ARIA live regions in run_app.py
# ---------------------------------------------------------------------------


class TestRunAppARIALiveRegions:
    """Verify _display_execution_result wraps states in ARIA role attributes.

    Arrange: Mock Streamlit markdown/info/exception calls
    Act: Call _display_execution_result with different states
    Expected: ARIA role="status" for running/completed, role="alert" for error
    """

    def test_display_execution_result_running_emits_role_status(self) -> None:
        """Running state wraps output in ARIA role='status' region."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.spinner") as mock_spinner,
            patch("streamlit.info"),
        ):
            mock_spinner.return_value.__enter__ = MagicMock(return_value=None)
            mock_spinner.return_value.__exit__ = MagicMock(return_value=False)

            _display_execution_result("running")

        # Check that ARIA role="status" appears in any markdown call
        all_md_calls = [str(c) for c in mock_md.call_args_list]
        assert any('role="status"' in c or "role='status'" in c for c in all_md_calls), (
            "Expected ARIA role='status' in markdown output for running state"
        )

    def test_display_execution_result_error_emits_role_alert(self) -> None:
        """Error state wraps output in ARIA role='alert' region."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.exception"),
            patch("streamlit.session_state", {"execution_error": "Something failed"}),
        ):
            _display_execution_result("error")

        all_md_calls = [str(c) for c in mock_md.call_args_list]
        assert any('role="alert"' in c or "role='alert'" in c for c in all_md_calls), (
            "Expected ARIA role='alert' in markdown output for error state"
        )

    def test_display_execution_result_completed_emits_role_status(self) -> None:
        """Completed state wraps output in ARIA role='status' region."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.info"),
            patch("streamlit.session_state", {}),
        ):
            _display_execution_result("completed")

        all_md_calls = [str(c) for c in mock_md.call_args_list]
        assert any('role="status"' in c or "role='status'" in c for c in all_md_calls), (
            "Expected ARIA role='status' in markdown output for completed state"
        )


# ---------------------------------------------------------------------------
# 2. Dead "Downloads page" reference fix
# ---------------------------------------------------------------------------


class TestRunAppDeadReferenceFixed:
    """Verify _render_paper_selection_input shows CLI instructions, not 'Downloads page'.

    Arrange: Mock _load_available_papers to return empty list, mock st.session_state
    Act: Call _render_paper_selection_input
    Expected: Info message contains 'make setup_dataset_sample', NOT 'Downloads page'
    """

    def test_no_papers_shows_cli_instructions_not_downloads_page(self) -> None:
        """When no papers, message references CLI command, not 'Downloads page'."""
        from unittest.mock import MagicMock

        import streamlit as st

        from gui.pages.run_app import _render_paper_selection_input

        # Use a MagicMock for session_state so attribute assignment works
        mock_session_state = MagicMock()
        mock_session_state.get = MagicMock(return_value=[])

        with (
            patch("gui.pages.run_app._load_available_papers", return_value=[]),
            patch.object(st, "session_state", mock_session_state),
            patch("streamlit.info") as mock_info,
            patch("streamlit.text_input", return_value=""),
        ):
            _render_paper_selection_input()

        # Gather all info messages
        all_info_msgs = " ".join(str(c) for c in mock_info.call_args_list)
        assert "Downloads page" not in all_info_msgs, (
            "Dead 'Downloads page' reference must be removed"
        )
        assert "make setup_dataset_sample" in all_info_msgs, (
            "CLI instruction 'make setup_dataset_sample' must appear in info message"
        )


# ---------------------------------------------------------------------------
# 3. help= kwarg on engine selector and paper selectbox
# ---------------------------------------------------------------------------


class TestRunAppHelpText:
    """Verify engine selector and paper selectbox have help= kwarg.

    Arrange: Inspect source / mock st.radio and st.selectbox
    Act: Call render_app or inspect function source
    Expected: help= argument present in respective widget calls
    """

    def test_engine_selector_radio_has_help_kwarg(self) -> None:
        """Engine selector st.radio call includes help= kwarg."""
        import ast
        from pathlib import Path

        source = Path("src/gui/pages/run_app.py").read_text()
        tree = ast.parse(source)

        # Walk AST to find st.radio / radio calls with 'help' keyword
        found_help = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                # Match: st.radio(...) or radio(...)
                is_radio = (
                    isinstance(func, ast.Attribute)
                    and func.attr == "radio"
                    or isinstance(func, ast.Name)
                    and func.id == "radio"
                )
                if is_radio:
                    kwarg_names = [kw.arg for kw in node.keywords]
                    if "help" in kwarg_names:
                        found_help = True
                        break

        assert found_help, "Engine selector st.radio must have a 'help=' kwarg"

    def test_paper_selectbox_has_help_kwarg(self) -> None:
        """Paper selection st.selectbox call includes help= kwarg."""
        import ast
        from pathlib import Path

        source = Path("src/gui/pages/run_app.py").read_text()
        tree = ast.parse(source)

        found_help = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                is_selectbox = (
                    isinstance(func, ast.Attribute)
                    and func.attr == "selectbox"
                    or isinstance(func, ast.Name)
                    and func.id == "selectbox"
                )
                if is_selectbox:
                    kwarg_names = [kw.arg for kw in node.keywords]
                    if "help" in kwarg_names:
                        found_help = True
                        break

        assert found_help, "Paper selectbox st.selectbox must have a 'help=' kwarg"


# ---------------------------------------------------------------------------
# 4. Post-run navigation guidance
# ---------------------------------------------------------------------------


class TestRunAppPostRunNavigationGuidance:
    """Verify completed state shows navigation guidance to Evaluation Results and Agent Graph.

    Arrange: Mock session state with completed state and no result
    Act: Call _display_execution_result('completed')
    Expected: Output references 'Evaluation Results' and 'Agent Graph'
    """

    def test_completed_state_shows_evaluation_results_guidance(self) -> None:
        """Completed state includes navigation hint to Evaluation Results page."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.info") as mock_info,
            patch("streamlit.session_state", {}),
        ):
            _display_execution_result("completed")

        all_output = " ".join(
            [str(c) for c in mock_md.call_args_list] + [str(c) for c in mock_info.call_args_list]
        )
        assert "Evaluation Results" in all_output, (
            "Post-completion guidance must reference 'Evaluation Results' page"
        )

    def test_completed_state_shows_agent_graph_guidance(self) -> None:
        """Completed state includes navigation hint to Agent Graph page."""
        from gui.pages.run_app import _display_execution_result

        with (
            patch("streamlit.markdown") as mock_md,
            patch("streamlit.info") as mock_info,
            patch("streamlit.session_state", {}),
        ):
            _display_execution_result("completed")

        all_output = " ".join(
            [str(c) for c in mock_md.call_args_list] + [str(c) for c in mock_info.call_args_list]
        )
        assert "Agent Graph" in all_output, (
            "Post-completion guidance must reference 'Agent Graph' page"
        )


# ---------------------------------------------------------------------------
# 5. Sidebar execution-in-progress indicator
# ---------------------------------------------------------------------------


class TestSidebarExecutionIndicator:
    """Verify render_sidebar accepts execution_state and shows indicator when running.

    Arrange: Mock sidebar Streamlit calls
    Act: Call render_sidebar with execution_state='running'
    Expected: Indicator text/markdown visible; absent when idle
    """

    def test_render_sidebar_accepts_execution_state_parameter(self) -> None:
        """render_sidebar signature includes execution_state parameter."""
        from gui.components.sidebar import render_sidebar

        sig = inspect.signature(render_sidebar)
        assert "execution_state" in sig.parameters, (
            "render_sidebar must accept 'execution_state' parameter"
        )

    def test_render_sidebar_shows_indicator_when_running(self) -> None:
        """In-progress indicator visible when execution_state='running'."""
        from gui.components.sidebar import render_sidebar

        mock_sidebar_module = MagicMock()
        mock_sidebar_module.radio.return_value = "App"

        # Patch the sidebar object imported into gui.components.sidebar module
        with patch("gui.components.sidebar.sidebar", mock_sidebar_module):
            render_sidebar("Test App", execution_state="running")

        all_calls = " ".join(
            str(c)
            for c in mock_sidebar_module.markdown.call_args_list
            + mock_sidebar_module.info.call_args_list
            + mock_sidebar_module.caption.call_args_list
        )
        assert any(
            keyword in all_calls
            for keyword in ["running", "progress", "⏳", "in progress", "Executing"]
        ), "Sidebar must show execution-in-progress indicator when running"

    def test_render_sidebar_no_indicator_when_idle(self) -> None:
        """No in-progress indicator when execution_state='idle'."""
        from gui.components.sidebar import render_sidebar

        mock_sidebar_module = MagicMock()
        mock_sidebar_module.radio.return_value = "App"

        with patch("gui.components.sidebar.sidebar", mock_sidebar_module):
            render_sidebar("Test App", execution_state="idle")

        # info should NOT be called for idle state (only called for running indicator)
        info_calls = " ".join(str(c) for c in mock_sidebar_module.info.call_args_list)
        assert "progress" not in info_calls.lower() and "running" not in info_calls.lower(), (
            "No in-progress indicator should be shown when idle"
        )


# ---------------------------------------------------------------------------
# 6. Human-readable metric labels
# ---------------------------------------------------------------------------


class TestEvaluationHumanReadableLabels:
    """Verify a label mapping/function converts snake_case metric keys to readable labels.

    Arrange: Import the label mapping or formatting function from evaluation.py
    Act: Look up known metric names
    Expected: Human-readable label returned for each
    """

    def test_cosine_score_maps_to_readable_label(self) -> None:
        """'cosine_score' maps to a human-readable label."""
        import gui.pages.evaluation as eval_module

        if hasattr(eval_module, "METRIC_LABELS"):
            label = eval_module.METRIC_LABELS.get("cosine_score", "")
        else:
            label = eval_module.format_metric_label("cosine_score")

        assert label != "cosine_score", "cosine_score must be mapped to a human-readable label"
        assert len(label) > 0, "Label must not be empty"

    def test_path_convergence_maps_to_readable_label(self) -> None:
        """'path_convergence' maps to a human-readable label."""
        import gui.pages.evaluation as eval_module

        if hasattr(eval_module, "METRIC_LABELS"):
            label = eval_module.METRIC_LABELS.get("path_convergence", "")
        else:
            label = eval_module.format_metric_label("path_convergence")

        assert label != "path_convergence", (
            "path_convergence must be mapped to a human-readable label"
        )

    def test_tool_selection_accuracy_maps_to_readable_label(self) -> None:
        """'tool_selection_accuracy' maps to a human-readable label."""
        import gui.pages.evaluation as eval_module

        if hasattr(eval_module, "METRIC_LABELS"):
            label = eval_module.METRIC_LABELS.get("tool_selection_accuracy", "")
        else:
            label = eval_module.format_metric_label("tool_selection_accuracy")

        assert label != "tool_selection_accuracy", (
            "tool_selection_accuracy must be mapped to a human-readable label"
        )

    def test_jaccard_score_maps_to_readable_label(self) -> None:
        """'jaccard_score' maps to a human-readable label."""
        import gui.pages.evaluation as eval_module

        if hasattr(eval_module, "METRIC_LABELS"):
            label = eval_module.METRIC_LABELS.get("jaccard_score", "")
        else:
            label = eval_module.format_metric_label("jaccard_score")

        assert label != "jaccard_score", "jaccard_score must be mapped to a human-readable label"


# ---------------------------------------------------------------------------
# 7. Baseline comparison inputs wrapped in collapsed expander
# ---------------------------------------------------------------------------


class TestEvaluationBaselineExpander:
    """Verify baseline comparison config inputs are inside a collapsed expander.

    Arrange: Mock st.expander and st.text_input
    Act: Call render_evaluation(result=None)
    Expected: st.expander called before st.text_input for baseline fields
    """

    def test_baseline_inputs_rendered_inside_expander(self) -> None:
        """Baseline comparison text_inputs are wrapped in a collapsed st.expander."""

        from gui.pages.evaluation import render_evaluation

        expander_ctx = MagicMock()
        expander_ctx.__enter__ = MagicMock(return_value=expander_ctx)
        expander_ctx.__exit__ = MagicMock(return_value=False)

        call_order: list[str] = []

        def track_expander(*args, **kwargs):
            call_order.append("expander")
            return expander_ctx

        def track_text_input(*args, **kwargs):
            call_order.append("text_input")
            return ""

        with (
            patch("streamlit.header"),
            patch("streamlit.info"),
            patch("streamlit.subheader"),
            patch("streamlit.expander", side_effect=track_expander),
            patch("streamlit.text_input", side_effect=track_text_input),
        ):
            render_evaluation(result=None)

        # expander must appear before at least one text_input
        assert "expander" in call_order, "st.expander must be called for baseline config"
        exp_idx = call_order.index("expander")
        text_idxs = [i for i, v in enumerate(call_order) if v == "text_input"]
        assert any(t > exp_idx for t in text_idxs), (
            "text_input calls must come after expander is opened"
        )

    def test_baseline_expander_defaults_to_collapsed(self) -> None:
        """Baseline expander uses expanded=False (collapsed by default)."""
        import ast
        from pathlib import Path

        source = Path("src/gui/pages/evaluation.py").read_text()
        tree = ast.parse(source)

        # Find st.expander calls with expanded=False
        found_collapsed = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                is_expander = (
                    isinstance(func, ast.Attribute)
                    and func.attr == "expander"
                    or isinstance(func, ast.Name)
                    and func.id == "expander"
                )
                if is_expander:
                    for kw in node.keywords:
                        if kw.arg == "expanded":
                            if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                                found_collapsed = True
                            break

        assert found_collapsed, (
            "Baseline comparison expander must use expanded=False (collapsed by default)"
        )


# ---------------------------------------------------------------------------
# 8. Dataframe alt text below bar chart
# ---------------------------------------------------------------------------


class TestEvaluationDataframeAltText:
    """Verify _render_metrics_comparison adds st.dataframe() below bar chart.

    Arrange: Mock st.bar_chart and st.dataframe, provide metric data
    Act: Call _render_metrics_comparison with result containing graph+text metrics
    Expected: st.dataframe called after st.bar_chart in the same function
    """

    def test_metrics_comparison_calls_dataframe_after_bar_chart(self) -> None:
        """st.dataframe called after st.bar_chart for accessible table alternative."""
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages.evaluation import _render_metrics_comparison

        result = MagicMock(spec=CompositeResult)
        result.metric_scores = {
            "cosine_score": 0.7,
            "jaccard_score": 0.5,
            "semantic_score": 0.6,
            "path_convergence": 0.8,
            "tool_selection_accuracy": 0.9,
            "coordination_centrality": 0.75,
            "task_distribution_balance": 0.65,
        }

        call_order: list[str] = []

        def track_bar_chart(*args, **kwargs):
            call_order.append("bar_chart")

        def track_dataframe(*args, **kwargs):
            call_order.append("dataframe")

        with (
            patch("streamlit.subheader"),
            patch("streamlit.columns") as mock_cols,
            patch("streamlit.markdown"),
            patch("streamlit.text"),
            patch("streamlit.bar_chart", side_effect=track_bar_chart),
            patch("streamlit.dataframe", side_effect=track_dataframe),
        ):
            # Mock columns context manager
            col_ctx = MagicMock()
            col_ctx.__enter__ = MagicMock(return_value=col_ctx)
            col_ctx.__exit__ = MagicMock(return_value=False)
            mock_cols.return_value = [col_ctx, col_ctx]

            _render_metrics_comparison(result)

        assert "bar_chart" in call_order, "st.bar_chart must be called"
        assert "dataframe" in call_order, (
            "st.dataframe must be called as accessible alt text after bar_chart"
        )
        bar_idx = call_order.index("bar_chart")
        df_idx = call_order.index("dataframe")
        assert df_idx > bar_idx, "st.dataframe must come AFTER st.bar_chart"


# ---------------------------------------------------------------------------
# 9. Delta indicators from BaselineComparison.tier_deltas
# ---------------------------------------------------------------------------


class TestEvaluationDeltaIndicators:
    """Verify _render_overall_results populates delta param when baseline available.

    Arrange: Mock st.metric, provide result + baseline tier_deltas in session state
    Act: Call render_evaluation with a result and baseline in session state
    Expected: st.metric called with non-None delta when baseline is present
    """

    def test_overall_results_metric_delta_populated_from_baseline(self) -> None:
        """Composite score metric has delta populated from BaselineComparison.tier_deltas."""
        from app.data_models.evaluation_models import CompositeResult
        from app.judge.baseline_comparison import BaselineComparison
        from gui.pages.evaluation import _render_overall_results

        result = MagicMock(spec=CompositeResult)
        result.composite_score = 0.75
        result.recommendation = "accept"
        result.recommendation_weight = 0.6

        baseline = MagicMock(spec=BaselineComparison)
        baseline.tier_deltas = {"tier1": 0.05, "tier2": 0.03, "tier3": -0.02}

        metric_calls: list[dict] = []

        def track_metric(*args, **kwargs):
            metric_calls.append({"args": args, "kwargs": kwargs})

        with (
            patch("streamlit.subheader"),
            patch("streamlit.columns") as mock_cols,
            patch("streamlit.metric", side_effect=track_metric),
        ):
            col_ctx = MagicMock()
            col_ctx.__enter__ = MagicMock(return_value=col_ctx)
            col_ctx.__exit__ = MagicMock(return_value=False)
            mock_cols.return_value = [col_ctx, col_ctx, col_ctx]

            _render_overall_results(result, baseline_comparison=baseline)

        # At least one metric call should have a non-None delta
        deltas = [c["kwargs"].get("delta") for c in metric_calls]
        assert any(d is not None for d in deltas), (
            "At least one st.metric call must have delta populated from BaselineComparison"
        )

    def test_overall_results_metric_no_delta_when_no_baseline(self) -> None:
        """Composite score metric has no delta when baseline_comparison is None."""
        from app.data_models.evaluation_models import CompositeResult
        from gui.pages.evaluation import _render_overall_results

        result = MagicMock(spec=CompositeResult)
        result.composite_score = 0.75
        result.recommendation = "accept"
        result.recommendation_weight = 0.6

        metric_calls: list[dict] = []

        def track_metric(*args, **kwargs):
            metric_calls.append({"args": args, "kwargs": kwargs})

        with (
            patch("streamlit.subheader"),
            patch("streamlit.columns") as mock_cols,
            patch("streamlit.metric", side_effect=track_metric),
        ):
            col_ctx = MagicMock()
            col_ctx.__enter__ = MagicMock(return_value=col_ctx)
            col_ctx.__exit__ = MagicMock(return_value=False)
            mock_cols.return_value = [col_ctx, col_ctx, col_ctx]

            _render_overall_results(result)

        # No deltas should be set when no baseline
        deltas = [c["kwargs"].get("delta") for c in metric_calls]
        assert all(d is None for d in deltas), (
            "st.metric delta must be None when no baseline_comparison provided"
        )


# ---------------------------------------------------------------------------
# 10. Tabular display for metric columns
# ---------------------------------------------------------------------------


class TestEvaluationTabularDisplay:
    """Verify metric columns use st.dataframe or tabular HTML, not raw st.text.

    Arrange: Inspect source AST
    Act: Walk AST of _render_metrics_comparison function body
    Expected: No bare st.text calls inside the metric display columns
             (replaced with st.dataframe or st.markdown with tabular HTML)
    """

    def test_metrics_comparison_does_not_use_st_text_for_metric_display(self) -> None:
        """_render_metrics_comparison does not display metrics via st.text()."""
        import ast
        from pathlib import Path

        source = Path("src/gui/pages/evaluation.py").read_text()
        tree = ast.parse(source)

        # Find _render_metrics_comparison function
        func_body = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_render_metrics_comparison":
                func_body = node
                break

        assert func_body is not None, "_render_metrics_comparison must exist in evaluation.py"

        # Check no st.text or text() calls in the metric display loop
        has_st_text = False
        for node in ast.walk(func_body):
            if isinstance(node, ast.Call):
                func = node.func
                is_text = (
                    isinstance(func, ast.Attribute)
                    and func.attr == "text"
                    or isinstance(func, ast.Name)
                    and func.id == "text"
                )
                if is_text:
                    has_st_text = True
                    break

        assert not has_st_text, (
            "_render_metrics_comparison must not use st.text() for metric display; "
            "use st.dataframe() or tabular HTML instead"
        )
