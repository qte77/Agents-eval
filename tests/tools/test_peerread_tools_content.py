"""
Tests for get_paper_content tool and URL guard in read_paper_pdf.

Tests cover STORY-001: Replace read_paper_pdf_tool with get_paper_content
using parsed JSON fallback chain.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.data_models.peerread_models import PeerReadPaper


class TestReadPaperPdfUrlGuard:
    """Test URL rejection guard in read_paper_pdf."""

    def test_read_paper_pdf_rejects_http_url(self):
        """read_paper_pdf returns error string (not raises) for http URLs."""
        from app.tools.peerread_tools import read_paper_pdf

        result = read_paper_pdf(None, "http://arxiv.org/pdf/1105.1072")
        assert "error" in result.lower() or "url" in result.lower() or "http" in result.lower()
        assert isinstance(result, str)

    def test_read_paper_pdf_rejects_https_url(self):
        """read_paper_pdf returns error string (not raises) for https URLs."""
        from app.tools.peerread_tools import read_paper_pdf

        result = read_paper_pdf(None, "https://arxiv.org/pdf/1105.1072")
        assert isinstance(result, str)
        assert "http" in result.lower() or "url" in result.lower() or "error" in result.lower()

    def test_read_paper_pdf_url_does_not_raise_file_not_found(self):
        """URL input must NOT raise FileNotFoundError (regression guard)."""
        from app.tools.peerread_tools import read_paper_pdf

        # Should return a string, not raise
        try:
            result = read_paper_pdf(None, "https://arxiv.org/pdf/1105.1072")
            assert isinstance(result, str)
        except FileNotFoundError:
            pytest.fail("read_paper_pdf raised FileNotFoundError for a URL — regression!")

    def test_read_paper_pdf_local_path_still_works(self, tmp_path: Path):
        """read_paper_pdf still reads local PDF files normally."""
        from app.tools.peerread_tools import read_paper_pdf

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake content")

        with patch("app.tools.peerread_tools.MarkItDown") as mock_md:
            mock_converter = Mock()
            mock_result = Mock()
            mock_result.text_content = "Extracted text"
            mock_converter.convert.return_value = mock_result
            mock_md.return_value = mock_converter

            result = read_paper_pdf(None, pdf_file)
            assert result == "Extracted text"


class TestGetPaperContent:
    """Test get_paper_content tool registered on agent."""

    def _register_tools(self, agent_id: str = "test") -> list:
        """Helper: register tools and capture them."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        mock_agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        mock_agent.tool = capture_tool
        add_peerread_tools_to_agent(mock_agent, agent_id=agent_id)
        return registered_tools

    def _find_tool(self, tools: list, name: str):
        """Find a registered tool by name."""
        return next((t for t in tools if t.__name__ == name), None)

    @pytest.mark.asyncio
    async def test_get_paper_content_tool_is_registered(self):
        """get_paper_content must be registered on the agent."""
        tools = self._register_tools()
        tool = self._find_tool(tools, "get_paper_content")
        assert tool is not None, "get_paper_content must be registered as an agent tool"

    @pytest.mark.asyncio
    async def test_read_paper_pdf_tool_is_not_registered(self):
        """read_paper_pdf_tool must NOT be registered (removed from agent tools)."""
        tools = self._register_tools()
        tool = self._find_tool(tools, "read_paper_pdf_tool")
        assert tool is None, "read_paper_pdf_tool must be removed from agent tool registration"

    @pytest.mark.asyncio
    async def test_get_paper_content_happy_path_parsed_json(self):
        """get_paper_content returns parsed JSON content when available."""
        tools = self._register_tools()
        tool = self._find_tool(tools, "get_paper_content")
        assert tool is not None

        test_paper = PeerReadPaper(
            paper_id="1105.1072",
            title="Test Paper",
            abstract="Test abstract",
            reviews=[],
            review_histories=[],
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = test_paper
            mock_loader.load_parsed_pdf_content.return_value = "Parsed JSON paper body"
            mock_loader_class.return_value = mock_loader

            result = await tool(None, "1105.1072")

            assert "Parsed JSON paper body" in result
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_paper_content_falls_back_to_abstract(self):
        """get_paper_content falls back to abstract when no PDF/parsed content."""
        tools = self._register_tools()
        tool = self._find_tool(tools, "get_paper_content")
        assert tool is not None

        test_paper = PeerReadPaper(
            paper_id="1105.1072",
            title="Test Paper",
            abstract="This is the abstract fallback",
            reviews=[],
            review_histories=[],
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = test_paper
            mock_loader.load_parsed_pdf_content.return_value = None  # No parsed content
            mock_loader.get_raw_pdf_path.return_value = None  # No raw PDF
            mock_loader_class.return_value = mock_loader

            result = await tool(None, "1105.1072")

            assert "This is the abstract fallback" in result

    @pytest.mark.asyncio
    async def test_get_paper_content_paper_id_not_path_or_url(self):
        """get_paper_content accepts paper_id (not a file path or URL)."""
        tools = self._register_tools()
        tool = self._find_tool(tools, "get_paper_content")
        assert tool is not None

        # Verify tool accepts a plain paper_id string (not a URL or path)
        test_paper = PeerReadPaper(
            paper_id="1105.1072",
            title="Test Paper",
            abstract="Abstract",
            reviews=[],
            review_histories=[],
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = test_paper
            mock_loader.load_parsed_pdf_content.return_value = "Body text"
            mock_loader_class.return_value = mock_loader

            result = await tool(None, "1105.1072")

            # Verify paper_id was looked up — not treated as a path
            mock_loader.get_paper_by_id.assert_called_once_with("1105.1072")
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_paper_content_paper_not_found_raises(self):
        """get_paper_content raises ValueError when paper_id is not in dataset."""
        tools = self._register_tools()
        tool = self._find_tool(tools, "get_paper_content")
        assert tool is not None

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = None
            mock_loader_class.return_value = mock_loader

            with pytest.raises(ValueError, match="not found"):
                await tool(None, "nonexistent-paper")

    @pytest.mark.asyncio
    async def test_get_paper_content_logs_tool_call(self):
        """get_paper_content logs the tool call via trace_collector."""
        tools = self._register_tools(agent_id="researcher")
        tool = self._find_tool(tools, "get_paper_content")
        assert tool is not None

        test_paper = PeerReadPaper(
            paper_id="1105.1072",
            title="Test Paper",
            abstract="Abstract",
            reviews=[],
            review_histories=[],
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
            patch("app.tools.peerread_tools.get_trace_collector") as mock_get_collector,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = test_paper
            mock_loader.load_parsed_pdf_content.return_value = "Content"
            mock_loader_class.return_value = mock_loader

            mock_collector = Mock()
            mock_get_collector.return_value = mock_collector

            await tool(None, "1105.1072")

            mock_collector.log_tool_call.assert_called_once()
            call_kwargs = mock_collector.log_tool_call.call_args
            # Tool name should be "get_paper_content"
            assert call_kwargs.kwargs.get("tool_name") == "get_paper_content" or (
                len(call_kwargs.args) > 1
                and call_kwargs.args[1] == "get_paper_content"
                or "get_paper_content" in str(call_kwargs)
            )
