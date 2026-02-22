"""
Tests for get_paper_content tool and URL guard in read_paper_pdf.

Tests cover STORY-001: Replace read_paper_pdf_tool with get_paper_content
using parsed JSON fallback chain.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic_ai import ModelRetry

from app.data_models.peerread_models import PeerReadPaper
from app.tools.peerread_tools import add_peerread_tools_to_agent
from conftest import capture_registered_tools


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

    @pytest.mark.asyncio
    async def test_get_paper_content_tool_is_registered(self):
        """get_paper_content must be registered on the agent."""
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        assert "get_paper_content" in tools, "get_paper_content must be registered as an agent tool"

    @pytest.mark.asyncio
    async def test_read_paper_pdf_tool_is_not_registered(self):
        """read_paper_pdf_tool must NOT be registered (removed from agent tools)."""
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        assert "read_paper_pdf_tool" not in tools, (
            "read_paper_pdf_tool must be removed from agent tool registration"
        )

    @pytest.mark.asyncio
    async def test_get_paper_content_happy_path_parsed_json(self):
        """get_paper_content returns parsed JSON content when available."""
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        tool = tools["get_paper_content"]
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
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        tool = tools["get_paper_content"]
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
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        tool = tools["get_paper_content"]
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
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        tool = tools["get_paper_content"]
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
        tools = capture_registered_tools(add_peerread_tools_to_agent, agent_id="researcher")
        tool = tools["get_paper_content"]
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


class TestReadPaperPdfErrors:
    """Test error cases in read_paper_pdf function."""

    def test_read_paper_pdf_file_not_found(self):
        """Test PDF reading with nonexistent file raises FileNotFoundError."""
        from app.tools.peerread_tools import read_paper_pdf

        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            read_paper_pdf(None, "/nonexistent/path.pdf")

    def test_read_paper_pdf_not_a_pdf(self, tmp_path: Path):
        """Test PDF reading with non-PDF file raises ValueError."""
        from app.tools.peerread_tools import read_paper_pdf

        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a PDF file")

        with pytest.raises(ValueError, match="Not a PDF file"):
            read_paper_pdf(None, txt_file)

    def test_read_paper_pdf_conversion_error(self, tmp_path: Path):
        """Test PDF reading with conversion failure raises ValueError."""
        from app.tools.peerread_tools import read_paper_pdf

        pdf_file = tmp_path / "corrupt.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 corrupted")

        with patch("app.tools.peerread_tools.MarkItDown") as mock_markitdown:
            mock_converter = Mock()
            mock_converter.convert.side_effect = Exception("Conversion failed")
            mock_markitdown.return_value = mock_converter

            with pytest.raises(ValueError, match="Failed to read PDF"):
                read_paper_pdf(None, pdf_file)


class TestTruncatePaperContent:
    """Test _truncate_paper_content function."""

    def test_truncate_paper_content_within_limit(self):
        """Test truncation when content is within limit preserves both fields."""
        from app.tools.peerread_tools import _truncate_paper_content

        abstract = "Short abstract"
        body = "Short body"
        max_length = 1000

        result = _truncate_paper_content(abstract, body, max_length)

        assert abstract in result
        assert body in result
        assert len(result) <= max_length

    def test_truncate_paper_content_exceeds_limit(self):
        """Test truncation when content exceeds limit truncates body, preserves abstract."""
        from app.tools.peerread_tools import _truncate_paper_content

        abstract = "A" * 50
        body = "B" * 1000
        max_length = 200

        result = _truncate_paper_content(abstract, body, max_length)

        assert abstract in result  # Abstract always preserved
        assert len(result) <= max_length
        assert "..." in result or len(body) > len(result)  # Body truncated


class TestGetPeerreadPaperTool:
    """Test get_peerread_paper and query_peerread_papers tools registered on agent."""

    @pytest.mark.asyncio
    async def test_get_peerread_paper_tool_success(self):
        """Test get_peerread_paper tool returns paper successfully."""
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        get_paper_tool = tools["get_peerread_paper"]
        assert get_paper_tool is not None

        test_paper = PeerReadPaper(
            paper_id="104",
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
            mock_loader_class.return_value = mock_loader

            result = await get_paper_tool(None, "104")

            assert result.paper_id == "104"
            assert result.title == "Test Paper"

    @pytest.mark.asyncio
    async def test_get_peerread_paper_tool_not_found(self):
        """Test get_peerread_paper tool raises ModelRetry when paper not found."""
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        get_paper_tool = tools["get_peerread_paper"]
        assert get_paper_tool is not None

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = None
            mock_loader_class.return_value = mock_loader

            with pytest.raises(ModelRetry, match="not found"):
                await get_paper_tool(None, "nonexistent")

    @pytest.mark.asyncio
    async def test_query_peerread_papers_tool_success(self):
        """Test query_peerread_papers tool returns list of papers."""
        tools = capture_registered_tools(add_peerread_tools_to_agent)
        query_tool = tools["query_peerread_papers"]
        assert query_tool is not None

        test_papers = [
            PeerReadPaper(
                paper_id="104",
                title="Test 1",
                abstract="Abstract 1",
                reviews=[],
                review_histories=[],
            )
        ]

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.query_papers.return_value = test_papers
            mock_loader_class.return_value = mock_loader

            result = await query_tool(None, venue="acl_2017", min_reviews=1)

            assert len(result) == 1
            assert result[0].paper_id == "104"
