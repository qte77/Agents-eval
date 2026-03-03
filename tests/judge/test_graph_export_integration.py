"""Integration tests for graph export wiring in main().

Verifies that persist_graph is called from main() with the graph and run_dir,
and that it correctly delegates to export_graph_json/export_graph_png when
graph is available, and is a no-op when graph is None.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import networkx as nx
import pytest


@pytest.fixture
def _stub_graph() -> nx.DiGraph:
    """Minimal graph for integration tests."""
    g: nx.DiGraph[str] = nx.DiGraph()
    g.add_node("agent_a", type="agent", label="Agent A")
    return g


class TestGraphExportIntegration:
    """Tests for graph export wiring in app.main()."""

    @pytest.mark.asyncio
    async def test_persist_graph_called_with_graph_and_run_dir(
        self, tmp_path: Path, _stub_graph: nx.DiGraph
    ) -> None:
        """persist_graph is called with the graph and run_dir."""
        mock_persist = MagicMock()

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        with (
            patch(
                "app.app._run_mas_engine_path",
                new_callable=AsyncMock,
                return_value=(MagicMock(), _stub_graph, "exec_abc"),
            ),
            patch("app.app.RunContext.create") as mock_create,
            patch("app.app.persist_graph", mock_persist),
            patch("app.app.set_active_run_context"),
            patch("app.app.get_active_run_context", return_value=MagicMock(run_dir=run_dir)),
        ):
            mock_ctx = MagicMock()
            mock_ctx.run_dir = run_dir
            mock_create.return_value = mock_ctx

            from app.app import main

            await main(
                chat_provider="test",
                query="test query",
                paper_id="p1",
                skip_eval=True,
            )

        mock_persist.assert_called_once_with(_stub_graph, run_dir)

    @pytest.mark.asyncio
    async def test_persist_graph_called_with_none_graph(self, tmp_path: Path) -> None:
        """persist_graph is called even when graph is None (it handles the no-op)."""
        mock_persist = MagicMock()

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        with (
            patch(
                "app.app._run_mas_engine_path",
                new_callable=AsyncMock,
                return_value=(MagicMock(), None, "exec_abc"),
            ),
            patch("app.app.RunContext.create") as mock_create,
            patch("app.app.persist_graph", mock_persist),
            patch("app.app.set_active_run_context"),
            patch("app.app.get_active_run_context", return_value=MagicMock(run_dir=run_dir)),
        ):
            mock_ctx = MagicMock()
            mock_ctx.run_dir = run_dir
            mock_create.return_value = mock_ctx

            from app.app import main

            await main(
                chat_provider="test",
                query="test query",
                paper_id="p1",
                skip_eval=True,
            )

        mock_persist.assert_called_once_with(None, run_dir)


class TestPersistGraphDelegation:
    """Tests that persist_graph correctly delegates to export functions."""

    def test_persist_graph_calls_both_exports_when_graph_available(
        self, tmp_path: Path, _stub_graph: nx.DiGraph
    ) -> None:
        """persist_graph calls export_graph_json and export_graph_png."""
        with (
            patch("app.judge.graph_export.export_graph_json") as mock_json,
            patch("app.judge.graph_export.export_graph_png") as mock_png,
        ):
            from app.judge.graph_export import persist_graph

            persist_graph(_stub_graph, tmp_path)

        mock_json.assert_called_once_with(_stub_graph, tmp_path)
        mock_png.assert_called_once_with(_stub_graph, tmp_path)

    def test_persist_graph_skips_exports_when_graph_is_none(self, tmp_path: Path) -> None:
        """persist_graph does not call export functions when graph is None."""
        with (
            patch("app.judge.graph_export.export_graph_json") as mock_json,
            patch("app.judge.graph_export.export_graph_png") as mock_png,
        ):
            from app.judge.graph_export import persist_graph

            persist_graph(None, tmp_path)

        mock_json.assert_not_called()
        mock_png.assert_not_called()
