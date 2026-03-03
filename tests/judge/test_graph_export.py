"""Tests for graph export functions (JSON and PNG).

Verifies that export_graph_json and export_graph_png correctly serialize
nx.DiGraph instances to disk.
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_graph() -> nx.DiGraph:
    """Graph with 1 agent node, 1 tool node, and 1 edge."""
    g: nx.DiGraph[str] = nx.DiGraph()
    g.add_node("manager", type="agent", label="Manager")
    g.add_node("search_tool", type="tool", label="Search Tool")
    g.add_edge("manager", "search_tool", interaction="tool_call", success=True)
    return g


@pytest.fixture
def empty_graph() -> nx.DiGraph:
    """Empty directed graph with no nodes or edges."""
    return nx.DiGraph()


# ---------------------------------------------------------------------------
# TestExportGraphJson
# ---------------------------------------------------------------------------


class TestExportGraphJson:
    """Tests for export_graph_json."""

    def test_returns_path_pointing_to_agent_graph_json(
        self, simple_graph: nx.DiGraph, tmp_path: Path
    ) -> None:
        """Returned path has correct filename and parent directory."""
        from app.judge.graph_export import export_graph_json

        result = export_graph_json(simple_graph, tmp_path)

        assert result.name == "agent_graph.json"
        assert result.parent == tmp_path

    def test_file_is_created_on_disk(self, simple_graph: nx.DiGraph, tmp_path: Path) -> None:
        """File exists after call."""
        from app.judge.graph_export import export_graph_json

        path = export_graph_json(simple_graph, tmp_path)

        assert path.exists()
        assert path.is_file()

    def test_file_contains_valid_json(self, simple_graph: nx.DiGraph, tmp_path: Path) -> None:
        """Written file parses as a JSON dict."""
        from app.judge.graph_export import export_graph_json

        path = export_graph_json(simple_graph, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))

        assert isinstance(data, dict)

    def test_json_contains_node_link_structure(
        self, simple_graph: nx.DiGraph, tmp_path: Path
    ) -> None:
        """JSON has 'nodes' and 'edges' keys (node_link_data format)."""
        from app.judge.graph_export import export_graph_json

        path = export_graph_json(simple_graph, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))

        assert "nodes" in data
        assert "edges" in data

    def test_json_preserves_node_attributes(self, simple_graph: nx.DiGraph, tmp_path: Path) -> None:
        """Agent and tool node IDs survive JSON round-trip."""
        from app.judge.graph_export import export_graph_json

        path = export_graph_json(simple_graph, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))

        node_ids = {n["id"] for n in data["nodes"]}
        assert "manager" in node_ids
        assert "search_tool" in node_ids

    def test_empty_graph_writes_valid_json(self, empty_graph: nx.DiGraph, tmp_path: Path) -> None:
        """Empty graph produces valid JSON with empty nodes/edges lists."""
        from app.judge.graph_export import export_graph_json

        path = export_graph_json(empty_graph, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))

        assert data["nodes"] == []
        assert data["edges"] == []


# ---------------------------------------------------------------------------
# TestExportGraphPng
# ---------------------------------------------------------------------------


class TestExportGraphPng:
    """Tests for export_graph_png."""

    def test_returns_path_pointing_to_agent_graph_png(
        self, simple_graph: nx.DiGraph, tmp_path: Path
    ) -> None:
        """Returned path has correct filename."""
        from app.judge.graph_export import export_graph_png

        result = export_graph_png(simple_graph, tmp_path)

        assert result.name == "agent_graph.png"
        assert result.parent == tmp_path

    def test_file_is_created_on_disk(self, simple_graph: nx.DiGraph, tmp_path: Path) -> None:
        """File exists after call."""
        from app.judge.graph_export import export_graph_png

        path = export_graph_png(simple_graph, tmp_path)

        assert path.exists()
        assert path.is_file()

    def test_png_file_has_nonzero_size(self, simple_graph: nx.DiGraph, tmp_path: Path) -> None:
        """PNG file is not empty."""
        from app.judge.graph_export import export_graph_png

        path = export_graph_png(simple_graph, tmp_path)

        assert path.stat().st_size > 0

    def test_png_starts_with_png_magic_bytes(
        self, simple_graph: nx.DiGraph, tmp_path: Path
    ) -> None:
        r"""File starts with PNG signature \x89PNG."""
        from app.judge.graph_export import export_graph_png

        path = export_graph_png(simple_graph, tmp_path)
        header = path.read_bytes()[:4]

        assert header == b"\x89PNG"

    def test_empty_graph_writes_valid_png(self, empty_graph: nx.DiGraph, tmp_path: Path) -> None:
        """Empty graph still produces a valid PNG file."""
        from app.judge.graph_export import export_graph_png

        path = export_graph_png(empty_graph, tmp_path)

        assert path.exists()
        assert path.read_bytes()[:4] == b"\x89PNG"
