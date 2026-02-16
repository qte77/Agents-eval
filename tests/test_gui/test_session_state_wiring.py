"""
Tests for GUI session state wiring (STORY-008).

Verifies that CompositeResult and graph data from App tab execution
flow correctly through session state to Evaluation Results and Agent Graph tabs.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import networkx as nx
import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.evaluation_models import CompositeResult

# MARK: --- Fixtures ---


@pytest.fixture
def sample_composite_result():
    """CompositeResult representing a typical evaluation output."""
    return CompositeResult(
        composite_score=0.85,
        recommendation="accept",
        recommendation_weight=0.9,
        metric_scores={
            "cosine_score": 0.8,
            "jaccard_score": 0.7,
            "semantic_score": 0.9,
            "path_convergence": 0.85,
            "tool_selection_accuracy": 0.90,
        },
        tier1_score=0.80,
        tier2_score=0.88,
        tier3_score=0.83,
        evaluation_complete=True,
        timestamp="2026-02-16T00:00:00Z",
        config_version="1.0.0",
    )


@pytest.fixture
def sample_graph():
    """NetworkX graph representing agent interactions."""
    graph = nx.DiGraph()
    graph.add_node("manager", node_type="agent", label="Manager")
    graph.add_node("researcher", node_type="agent", label="Researcher")
    graph.add_edge("manager", "researcher", interaction="delegation")
    return graph


# MARK: --- Behavioral: _execute_query_background stores results in session state ---


class TestExecuteQueryStoresData:
    """Verify _execute_query_background stores composite_result and graph in session state."""

    @pytest.mark.asyncio
    async def test_dict_result_stored_in_session_state(self, sample_composite_result, sample_graph):
        """When main() returns a result dict, both keys are stored in session state."""
        from gui.pages.run_app import _execute_query_background

        mock_state = SimpleNamespace()

        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            mock_main.return_value = {
                "composite_result": sample_composite_result,
                "graph": sample_graph,
            }

            await _execute_query_background(
                query="test",
                provider="cerebras",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
            )

            assert mock_state.execution_state == "completed"
            assert mock_state.execution_composite_result is sample_composite_result
            assert mock_state.execution_graph is sample_graph
            # Legacy key also set
            assert mock_state.execution_result is sample_composite_result

    @pytest.mark.asyncio
    async def test_none_result_clears_session_state(self):
        """When main() returns None (skip_eval), session state keys are set to None."""
        from gui.pages.run_app import _execute_query_background

        mock_state = SimpleNamespace()

        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            mock_main.return_value = None

            await _execute_query_background(
                query="test",
                provider="cerebras",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
            )

            assert mock_state.execution_state == "completed"
            assert mock_state.execution_composite_result is None
            assert mock_state.execution_graph is None


# MARK: --- Behavioral: run_gui.main() passes session state to page renderers ---


class TestRunGuiWiring:
    """Verify run_gui.main() reads session state and passes data to page renderers."""

    @pytest.mark.asyncio
    async def test_evaluation_page_receives_session_data(self, sample_composite_result):
        """When user navigates to Evaluation Results, render_evaluation gets session data."""
        from run_gui import main

        with (
            patch("run_gui.add_custom_styling"),
            patch("run_gui.render_sidebar", return_value="Evaluation Results"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_evaluation") as mock_render,
            patch("run_gui.st") as mock_st,
        ):
            mock_st.session_state = {"execution_composite_result": sample_composite_result}

            await main()

            mock_render.assert_called_once_with(sample_composite_result)

    @pytest.mark.asyncio
    async def test_agent_graph_page_receives_session_data(self, sample_graph):
        """When user navigates to Agent Graph, render_agent_graph gets session data."""
        from run_gui import main

        with (
            patch("run_gui.add_custom_styling"),
            patch("run_gui.render_sidebar", return_value="Agent Graph"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_agent_graph") as mock_render,
            patch("run_gui.st") as mock_st,
        ):
            mock_st.session_state = {"execution_graph": sample_graph}

            await main()

            mock_render.assert_called_once_with(sample_graph)

    @pytest.mark.asyncio
    async def test_evaluation_page_gets_none_when_no_execution(self):
        """Before any execution, render_evaluation receives None."""
        from run_gui import main

        with (
            patch("run_gui.add_custom_styling"),
            patch("run_gui.render_sidebar", return_value="Evaluation Results"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_evaluation") as mock_render,
            patch("run_gui.st") as mock_st,
        ):
            mock_st.session_state = {}

            await main()

            mock_render.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_agent_graph_page_gets_none_when_no_execution(self):
        """Before any execution, render_agent_graph receives None."""
        from run_gui import main

        with (
            patch("run_gui.add_custom_styling"),
            patch("run_gui.render_sidebar", return_value="Agent Graph"),
            patch("run_gui.initialize_session_state"),
            patch("run_gui.render_agent_graph") as mock_render,
            patch("run_gui.st") as mock_st,
        ):
            mock_st.session_state = {}

            await main()

            mock_render.assert_called_once_with(None)


# MARK: --- Behavioral: main() returns result dict ---


class TestMainReturnType:
    """Verify app.main() returns properly structured result dict."""

    @pytest.mark.asyncio
    async def test_main_returns_dict_with_composite_and_graph_keys(self):
        """main() returns a dict containing composite_result and graph."""
        from app.app import main

        mock_result = CompositeResult(
            composite_score=0.85,
            recommendation="accept",
            recommendation_weight=0.9,
            metric_scores={},
            tier1_score=0.80,
            tier2_score=0.88,
            tier3_score=0.83,
            evaluation_complete=True,
        )

        with (
            patch("app.app.load_config"),
            patch("app.app.setup_agent_env"),
            patch("app.app.login"),
            patch("app.app._initialize_instrumentation"),
            patch("app.app.get_manager"),
            patch(
                "app.app.run_manager", return_value=("exec-id", None)
            ),  # (execution_id, manager_output)
            patch("app.app._run_evaluation_if_enabled", return_value=mock_result),
            patch("app.app._build_graph_from_trace", return_value=None),
        ):
            result = await main(
                query="test query",
                chat_config_file="test.json",
                skip_eval=False,
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "composite_result" in result
            assert "graph" in result
            assert result["composite_result"] is mock_result

    @pytest.mark.asyncio
    async def test_main_returns_none_when_eval_skipped(self):
        """main() returns None when evaluation is skipped."""
        from app.app import main

        with (
            patch("app.app.load_config"),
            patch("app.app.setup_agent_env"),
            patch("app.app.login"),
            patch("app.app._initialize_instrumentation"),
            patch("app.app.get_manager"),
            patch(
                "app.app.run_manager", return_value=("exec-id", None)
            ),  # (execution_id, manager_output)
            patch("app.app._run_evaluation_if_enabled", return_value=None),
        ):
            result = await main(
                query="test query",
                chat_config_file="test.json",
                skip_eval=True,
            )

            assert result is None


# MARK: --- Inline-Snapshot Tests ---


class TestSessionStateSnapshots:
    """Snapshot tests for session state structure after execution."""

    @pytest.mark.asyncio
    async def test_session_state_keys_after_successful_execution(self, sample_composite_result):
        """Snapshot: session state keys set after a successful execution."""
        from gui.pages.run_app import _execute_query_background

        mock_state = SimpleNamespace()

        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            mock_main.return_value = {
                "composite_result": sample_composite_result,
                "graph": None,
            }

            await _execute_query_background(
                query="review paper 304",
                provider="cerebras",
                include_researcher=True,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
            )

        state_keys = sorted(k for k in vars(mock_state) if k.startswith("execution_"))
        assert state_keys == snapshot(
            [
                "execution_composite_result",
                "execution_graph",
                "execution_provider",
                "execution_query",
                "execution_result",
                "execution_state",
            ]
        )

    @pytest.mark.asyncio
    async def test_session_state_values_after_successful_execution(self):
        """Snapshot: session state values after execution with known inputs."""
        from gui.pages.run_app import _execute_query_background

        mock_state = SimpleNamespace()
        mock_result = CompositeResult(
            composite_score=0.75,
            recommendation="weak_accept",
            recommendation_weight=0.5,
            metric_scores={"cosine_score": 0.75},
            tier1_score=0.75,
            tier2_score=None,
            tier3_score=0.80,
            evaluation_complete=False,
        )

        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            mock_main.return_value = {"composite_result": mock_result, "graph": None}

            await _execute_query_background(
                query="test query",
                provider="openai",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
            )

        assert mock_state.execution_state == snapshot("completed")
        assert mock_state.execution_query == snapshot("test query")
        assert mock_state.execution_provider == snapshot("openai")
        assert mock_state.execution_composite_result.composite_score == snapshot(0.75)
        assert mock_state.execution_composite_result.recommendation == snapshot("weak_accept")


# MARK: --- Hypothesis Property Tests ---


class TestSessionStateProperties:
    """Property tests for data fidelity through the session state wiring."""

    @given(
        composite_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        tier1=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        tier3=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    )
    @pytest.mark.asyncio
    async def test_composite_score_preserved_through_execution(
        self,
        composite_score,
        tier1,
        tier3,
    ):
        """Property: composite score is stored unchanged through _execute_query_background."""
        from gui.pages.run_app import _execute_query_background

        mock_result = CompositeResult(
            composite_score=composite_score,
            recommendation="accept",
            recommendation_weight=0.8,
            metric_scores={},
            tier1_score=tier1,
            tier2_score=None,
            tier3_score=tier3,
            evaluation_complete=True,
        )

        mock_state = SimpleNamespace()

        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            mock_main.return_value = {"composite_result": mock_result, "graph": None}

            await _execute_query_background(
                query="q",
                provider="p",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
            )

        assert mock_state.execution_composite_result.composite_score == composite_score
        assert mock_state.execution_composite_result.tier1_score == tier1
        assert mock_state.execution_composite_result.tier3_score == tier3

    @given(num_nodes=st.integers(min_value=1, max_value=20))
    @pytest.mark.asyncio
    async def test_graph_node_count_preserved_through_execution(self, num_nodes):
        """Property: graph node count is preserved through _execute_query_background."""
        from gui.pages.run_app import _execute_query_background

        graph = nx.DiGraph()
        for i in range(num_nodes):
            graph.add_node(f"agent_{i}", node_type="agent")

        mock_result = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier2_score=None,
            tier3_score=0.5,
            evaluation_complete=True,
        )

        mock_state = SimpleNamespace()

        with (
            patch("gui.pages.run_app.st.session_state", mock_state),
            patch("gui.pages.run_app.main", new_callable=AsyncMock) as mock_main,
        ):
            mock_main.return_value = {"composite_result": mock_result, "graph": graph}

            await _execute_query_background(
                query="q",
                provider="p",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
            )

        assert mock_state.execution_graph.number_of_nodes() == num_nodes
        assert isinstance(mock_state.execution_graph, nx.DiGraph)
