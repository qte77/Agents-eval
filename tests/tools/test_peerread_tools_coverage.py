"""
Additional test coverage for peerread_tools.py low-coverage functions.

Tests target critical untested functions identified in Sprint 5 MAESTRO review:
- review generation tool functions
- paper content truncation
- file operations
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.data_models.peerread_models import PeerReadPaper


class TestReadPaperPdf:
    """Test read_paper_pdf function."""

    def test_read_paper_pdf_success(self, tmp_path: Path):
        """Test successful PDF reading."""
        from app.tools.peerread_tools import read_paper_pdf

        # Arrange
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

        with patch("app.tools.peerread_tools.MarkItDown") as mock_markitdown:
            mock_converter = Mock()
            mock_result = Mock()
            mock_result.text_content = "Extracted PDF text content"
            mock_converter.convert.return_value = mock_result
            mock_markitdown.return_value = mock_converter

            # Act
            result = read_paper_pdf(None, pdf_file)

            # Assert
            assert result == "Extracted PDF text content"
            mock_converter.convert.assert_called_once()

    def test_read_paper_pdf_file_not_found(self):
        """Test PDF reading with nonexistent file."""
        from app.tools.peerread_tools import read_paper_pdf

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            read_paper_pdf(None, "/nonexistent/path.pdf")

    def test_read_paper_pdf_not_a_pdf(self, tmp_path: Path):
        """Test PDF reading with non-PDF file."""
        from app.tools.peerread_tools import read_paper_pdf

        # Arrange
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not a PDF file")

        # Act & Assert
        with pytest.raises(ValueError, match="Not a PDF file"):
            read_paper_pdf(None, txt_file)

    def test_read_paper_pdf_conversion_error(self, tmp_path: Path):
        """Test PDF reading with conversion failure."""
        from app.tools.peerread_tools import read_paper_pdf

        # Arrange
        pdf_file = tmp_path / "corrupt.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 corrupted")

        with patch("app.tools.peerread_tools.MarkItDown") as mock_markitdown:
            mock_converter = Mock()
            mock_converter.convert.side_effect = Exception("Conversion failed")
            mock_markitdown.return_value = mock_converter

            # Act & Assert
            with pytest.raises(ValueError, match="Failed to read PDF"):
                read_paper_pdf(None, pdf_file)


class TestTruncatePaperContent:
    """Test _truncate_paper_content function."""

    def test_truncate_paper_content_within_limit(self):
        """Test truncation when content is within limit."""
        from app.tools.peerread_tools import _truncate_paper_content

        # Arrange
        abstract = "Short abstract"
        body = "Short body"
        max_length = 1000

        # Act
        result = _truncate_paper_content(abstract, body, max_length)

        # Assert
        assert abstract in result
        assert body in result
        assert len(result) <= max_length

    def test_truncate_paper_content_exceeds_limit(self):
        """Test truncation when content exceeds limit."""
        from app.tools.peerread_tools import _truncate_paper_content

        # Arrange
        abstract = "A" * 50
        body = "B" * 1000
        max_length = 200

        # Act
        result = _truncate_paper_content(abstract, body, max_length)

        # Assert
        assert abstract in result  # Abstract always preserved
        assert len(result) <= max_length
        assert "..." in result or len(body) > len(result)  # Body truncated


class TestAddPeerreadToolsToAgent:
    """Test add_peerread_tools_to_agent function and registered tools."""

    @pytest.mark.asyncio
    async def test_get_peerread_paper_tool_success(self):
        """Test get_peerread_paper tool returns paper successfully."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        mock_agent = Mock()
        mock_agent.tool = Mock()

        # Capture the registered tool function
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        mock_agent.tool = capture_tool

        # Register tools
        add_peerread_tools_to_agent(mock_agent, agent_id="test_agent")

        # Find get_peerread_paper tool
        get_paper_tool = next(
            (t for t in registered_tools if t.__name__ == "get_peerread_paper"), None
        )
        assert get_paper_tool is not None

        # Mock the loader
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

            # Act
            result = await get_paper_tool(None, "104")

            # Assert
            assert result.paper_id == "104"
            assert result.title == "Test Paper"

    @pytest.mark.asyncio
    async def test_get_peerread_paper_tool_not_found(self):
        """Test get_peerread_paper tool raises when paper not found."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        mock_agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        mock_agent.tool = capture_tool
        add_peerread_tools_to_agent(mock_agent, agent_id="test_agent")

        get_paper_tool = next(
            (t for t in registered_tools if t.__name__ == "get_peerread_paper"), None
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = None  # Paper not found
            mock_loader_class.return_value = mock_loader

            # Act & Assert
            with pytest.raises(ValueError, match="Paper .* not found"):
                await get_paper_tool(None, "nonexistent")

    @pytest.mark.asyncio
    async def test_query_peerread_papers_tool_success(self):
        """Test query_peerread_papers tool returns papers."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        mock_agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        mock_agent.tool = capture_tool
        add_peerread_tools_to_agent(mock_agent, agent_id="test_agent")

        query_tool = next(
            (t for t in registered_tools if t.__name__ == "query_peerread_papers"), None
        )
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

            # Act
            result = await query_tool(None, venue="acl_2017", min_reviews=1)

            # Assert
            assert len(result) == 1
            assert result[0].paper_id == "104"

    @pytest.mark.asyncio
    async def test_read_paper_pdf_tool_success(self, tmp_path: Path):
        """Test read_paper_pdf_tool wrapper function."""
        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        mock_agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        mock_agent.tool = capture_tool
        add_peerread_tools_to_agent(mock_agent, agent_id="test_agent")

        pdf_tool = next((t for t in registered_tools if t.__name__ == "read_paper_pdf_tool"), None)
        assert pdf_tool is not None

        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 content")

        with patch("app.tools.peerread_tools.read_paper_pdf") as mock_read:
            mock_read.return_value = "Extracted text"

            # Act
            result = await pdf_tool(None, str(pdf_file))

            # Assert
            assert result == "Extracted text"
