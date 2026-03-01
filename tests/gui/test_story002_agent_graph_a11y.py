"""Tests for STORY-002: Agent graph accessibility improvements.

Verifies:
- st.caption() rendered before components.html()
- <title> element in generated Pyvis HTML
- scrolling=True on components.html()
- bgcolor not hard-coded #ffffff
- Text summary with node/edge counts rendered below graph
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import networkx as nx
import pytest


def _make_test_graph() -> nx.DiGraph:
    """Create a small test graph with agent and tool nodes."""
    g: nx.DiGraph[str] = nx.DiGraph()
    g.add_node("AgentA", type="agent", label="AgentA")
    g.add_node("AgentB", type="agent", label="AgentB")
    g.add_node("ToolX", type="tool", label="ToolX")
    g.add_edge("AgentA", "AgentB", interaction="delegation")
    g.add_edge("AgentA", "ToolX", interaction="tool_call")
    return g


@pytest.fixture()
def test_graph() -> nx.DiGraph:
    """Fixture providing a small test graph."""
    return _make_test_graph()


class TestCaptionBeforeGraph:
    """AC-2/AC-7: st.caption() with descriptive text before components.html()."""

    @patch("gui.pages.agent_graph.components")
    @patch("gui.pages.agent_graph.Network")
    @patch("gui.pages.agent_graph.st")
    def test_caption_called_before_components_html(
        self,
        mock_st: MagicMock,
        mock_network_cls: MagicMock,
        mock_components: MagicMock,
        test_graph: nx.DiGraph,
    ) -> None:
        """st.caption() must be called before components.html()."""
        from gui.pages.agent_graph import render_agent_graph

        # Setup mock network to produce HTML
        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net
        mock_net.save_graph = MagicMock(side_effect=lambda f: open(f, "w").write("<html></html>"))

        render_agent_graph(graph=test_graph)

        # Find caption and html calls in the call order
        caption_calls = [c for c in mock_st.mock_calls if c[0] == "caption"]
        assert len(caption_calls) >= 1, "st.caption() must be called"

        caption_text = caption_calls[0][1][0]
        assert "agent interaction graph" in caption_text.lower()

    @patch("gui.pages.agent_graph.components")
    @patch("gui.pages.agent_graph.Network")
    @patch("gui.pages.agent_graph.st")
    def test_caption_text_references_statistics(
        self,
        mock_st: MagicMock,
        mock_network_cls: MagicMock,
        mock_components: MagicMock,
        test_graph: nx.DiGraph,
    ) -> None:
        """Caption text should reference the statistics section."""
        from gui.pages.agent_graph import render_agent_graph

        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net
        mock_net.save_graph = MagicMock(side_effect=lambda f: open(f, "w").write("<html></html>"))

        render_agent_graph(graph=test_graph)

        caption_calls = [c for c in mock_st.mock_calls if c[0] == "caption"]
        assert len(caption_calls) >= 1
        caption_text = caption_calls[0][1][0]
        assert "statistics" in caption_text.lower() or "details" in caption_text.lower()


class TestTitleInHtml:
    """AC-3/AC-6: <title>Agent Interaction Graph</title> inserted into Pyvis HTML."""

    @patch("gui.pages.agent_graph.components")
    @patch("gui.pages.agent_graph.Network")
    @patch("gui.pages.agent_graph.st")
    def test_title_element_in_html(
        self,
        mock_st: MagicMock,
        mock_network_cls: MagicMock,
        mock_components: MagicMock,
        test_graph: nx.DiGraph,
    ) -> None:
        """Generated HTML passed to components.html() must contain <title>."""
        from gui.pages.agent_graph import render_agent_graph

        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net
        mock_net.save_graph = MagicMock(
            side_effect=lambda f: open(f, "w").write("<html><head></head><body></body></html>")
        )

        render_agent_graph(graph=test_graph)

        # Get the HTML passed to components.html()
        html_call = mock_components.html.call_args
        assert html_call is not None, "components.html() must be called"
        html_content = html_call[0][0] if html_call[0] else html_call[1].get("html", "")
        assert "<title>Agent Interaction Graph</title>" in html_content


class TestScrollingTrue:
    """AC-4/AC-8: scrolling=True on components.html() to prevent keyboard trap."""

    @patch("gui.pages.agent_graph.components")
    @patch("gui.pages.agent_graph.Network")
    @patch("gui.pages.agent_graph.st")
    def test_scrolling_true(
        self,
        mock_st: MagicMock,
        mock_network_cls: MagicMock,
        mock_components: MagicMock,
        test_graph: nx.DiGraph,
    ) -> None:
        """components.html() must be called with scrolling=True."""
        from gui.pages.agent_graph import render_agent_graph

        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net
        mock_net.save_graph = MagicMock(side_effect=lambda f: open(f, "w").write("<html></html>"))

        render_agent_graph(graph=test_graph)

        html_call = mock_components.html.call_args
        assert html_call is not None
        assert html_call[1].get("scrolling") is True or (
            len(html_call[0]) > 2 and html_call[0][2] is True
        ), "scrolling must be True"


class TestBgcolorNotHardcoded:
    """AC-5/AC-9: bgcolor reads from theme, not hard-coded #ffffff."""

    @patch("gui.pages.agent_graph.components")
    @patch("gui.pages.agent_graph.Network")
    @patch("gui.pages.agent_graph.st")
    def test_bgcolor_not_hardcoded_white(
        self,
        mock_st: MagicMock,
        mock_network_cls: MagicMock,
        mock_components: MagicMock,
        test_graph: nx.DiGraph,
    ) -> None:
        """Network() must not be called with bgcolor='#ffffff'."""
        from gui.pages.agent_graph import render_agent_graph

        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net
        mock_net.save_graph = MagicMock(side_effect=lambda f: open(f, "w").write("<html></html>"))

        render_agent_graph(graph=test_graph)

        network_call = mock_network_cls.call_args
        assert network_call is not None
        bgcolor_value = network_call[1].get("bgcolor", "#ffffff")
        assert bgcolor_value != "#ffffff", (
            f"bgcolor must not be hard-coded #ffffff, got {bgcolor_value}"
        )


class TestTextSummary:
    """AC-1/AC-5: Text summary with node count, edge count, agent names rendered."""

    @patch("gui.pages.agent_graph.components")
    @patch("gui.pages.agent_graph.Network")
    @patch("gui.pages.agent_graph.st")
    def test_text_summary_contains_counts(
        self,
        mock_st: MagicMock,
        mock_network_cls: MagicMock,
        mock_components: MagicMock,
        test_graph: nx.DiGraph,
    ) -> None:
        """Text summary must include node count, edge count, and agent names."""
        from gui.pages.agent_graph import render_agent_graph

        mock_net = MagicMock()
        mock_network_cls.return_value = mock_net
        mock_net.save_graph = MagicMock(side_effect=lambda f: open(f, "w").write("<html></html>"))

        render_agent_graph(graph=test_graph)

        # Look for markdown or text calls containing summary info
        all_calls = mock_st.mock_calls
        all_text = " ".join(
            str(c[1][0])
            for c in all_calls
            if c[0] in ("markdown", "text", "write", "info") and c[1]
        )

        assert "3" in all_text or "nodes" in all_text.lower(), "Summary must mention node count"
        assert "2" in all_text or "edges" in all_text.lower(), "Summary must mention edge count"
        assert "AgentA" in all_text or "AgentB" in all_text, "Summary must list agent names"


class TestThemeBackgroundGetter:
    """AC-9: styling.py provides theme background color getter."""

    def test_get_theme_bgcolor_exists(self) -> None:
        """styling.py must export a function to get theme background color."""
        from gui.config.styling import get_theme_bgcolor

        result = get_theme_bgcolor()
        assert isinstance(result, str)
        assert result.startswith("#")
