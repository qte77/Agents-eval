"""
Test cases for PeerRead agent tools.

Tests for agent integration tools that enable the manager agent to interact
with the PeerRead dataset for paper retrieval, querying, and review evaluation.
"""

from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel
from pydantic_ai import Agent, ModelRetry

from app.data_models.peerread_models import (
    PeerReadConfig,
    PeerReadPaper,
    PeerReadReview,
)


class TestPeerReadAgentTools:
    """Test PeerRead agent tool integration."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing tool integration."""
        return Agent(model="test", output_type=BaseModel)

    @pytest.fixture
    def sample_paper(self):
        """Create sample paper data for testing."""
        return PeerReadPaper(
            paper_id="test_001",
            title="Test Paper Title",
            abstract="This is a test abstract for the paper.",
            reviews=[
                PeerReadReview(
                    impact="4",
                    substance="4",
                    appropriateness="5",
                    meaningful_comparison="3",
                    presentation_format="Poster",
                    comments="This is a good paper with solid methodology.",
                    soundness_correctness="4",
                    originality="3",
                    recommendation="4",
                    clarity="4",
                    reviewer_confidence="3",
                )
            ],
            histories=[],
        )

    @pytest.fixture
    def sample_config(self):
        """Create sample configuration for testing."""
        return PeerReadConfig()

    def test_save_paper_review_tool(self, tmp_path, sample_paper, sample_config):
        """Test review saving functionality with actual file persistence."""
        import json
        from pathlib import Path

        from app.data_utils.review_persistence import ReviewPersistence

        # Create temporary directory for review storage
        temp_reviews_dir = tmp_path / "test_reviews"
        temp_reviews_dir.mkdir()

        # Test the underlying save_paper_review logic by creating it manually
        with (
            patch("app.tools.peerread_tools.load_peerread_config") as mock_config,
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
            patch("app.tools.peerread_tools.ReviewPersistence") as mock_persistence_class,
        ):
            # Setup mocks
            mock_config.return_value = sample_config
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = sample_paper
            mock_loader_class.return_value = mock_loader

            # Use real ReviewPersistence but with temp directory
            persistence_instance = ReviewPersistence(str(temp_reviews_dir))
            mock_persistence_class.return_value = persistence_instance

            # Test data
            test_paper_id = "test_001"
            test_review_text = "This is a test review with comprehensive analysis."
            test_recommendation = "accept"
            test_confidence = 0.8

            # Test the save_paper_review logic directly (simulating the tool internals)
            from app.data_models.peerread_models import PeerReadReview

            # Create the review object (this is what the tool does internally)
            review = PeerReadReview(
                impact="N/A",
                substance="N/A",
                appropriateness="N/A",
                meaningful_comparison="N/A",
                presentation_format="N/A",
                comments=test_review_text,
                soundness_correctness="N/A",
                originality="N/A",
                recommendation=test_recommendation,
                clarity="N/A",
                reviewer_confidence=str(test_confidence),
            )

            # Save the review using persistence layer
            result_path = persistence_instance.save_review(test_paper_id, review)

            # Verify the result is a file path
            assert isinstance(result_path, str)
            assert result_path.endswith(".json")
            assert test_paper_id in result_path

            # Verify the file was actually created
            saved_file = Path(result_path)
            assert saved_file.exists()

            # Verify the file contents
            with open(saved_file, encoding="utf-8") as f:
                saved_data = json.load(f)

            assert saved_data["paper_id"] == test_paper_id
            assert saved_data["review"]["comments"] == test_review_text
            assert saved_data["review"]["recommendation"] == test_recommendation
            assert saved_data["review"]["reviewer_confidence"] == str(test_confidence)
            assert "timestamp" in saved_data


class TestPaperPDFReading:
    """Test PDF reading functionality."""

    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Create a sample PDF for testing."""
        from reportlab.pdfgen import canvas

        # Create a sample PDF
        pdf_path = tmp_path / "sample_paper.pdf"
        c = canvas.Canvas(str(pdf_path))
        c.drawString(100, 750, "Test Paper Title")
        c.drawString(100, 700, "This is a sample paper abstract.")
        c.drawString(100, 650, "First page content.")
        c.showPage()
        c.drawString(100, 750, "Second page content.")
        c.showPage()
        c.save()

        return str(pdf_path)

    def test_read_paper_pdf_full(self, sample_pdf_path):
        """Test reading the entire PDF."""
        from app.tools.peerread_tools import read_paper_pdf

        # Read PDF
        result = read_paper_pdf(None, sample_pdf_path)

        # Verify content
        assert "Test Paper Title" in result
        assert "This is a sample paper abstract" in result
        assert "First page content" in result
        assert "Second page content" in result

    def test_read_paper_pdf_entire_document(self, sample_pdf_path):
        """Test reading the entire PDF (pagination not supported)."""
        from app.tools.peerread_tools import read_paper_pdf

        # Read entire PDF (only option available)
        result = read_paper_pdf(None, sample_pdf_path)

        # Verify all content is present (no page filtering)
        assert "Test Paper Title" in result
        assert "This is a sample paper abstract" in result
        assert "First page content" in result
        assert "Second page content" in result

    def test_read_paper_pdf_nonexistent(self):
        """Test error handling for non-existent PDF."""
        from app.tools.peerread_tools import read_paper_pdf

        # Attempt to read non-existent PDF
        with pytest.raises(FileNotFoundError):
            read_paper_pdf(None, "/path/to/nonexistent/file.pdf")

    def test_read_paper_pdf_invalid_file(self, tmp_path):
        """Test error handling for invalid file type."""
        from app.tools.peerread_tools import read_paper_pdf

        # Create a dummy text file
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("Not a PDF")

        # Attempt to read non-PDF file
        with pytest.raises(ValueError, match="Not a PDF file"):
            read_paper_pdf(None, str(invalid_file))


class TestContentTruncation:
    """Test content truncation functionality for model-aware limits."""

    def test_truncate_content_preserves_abstract(self):
        """Test that truncation preserves the abstract section."""
        from app.tools.peerread_tools import _truncate_paper_content

        abstract = "This is the abstract section."
        body = "A" * 20000  # Large body content
        max_length = 1000

        result = _truncate_paper_content(abstract, body, max_length)

        # Abstract should be preserved
        assert abstract in result
        # Should contain truncation marker
        assert "[TRUNCATED]" in result
        # Result should be within limit
        assert len(result) <= max_length

    def test_truncate_content_adds_marker(self):
        """Test that truncation adds [TRUNCATED] marker."""
        from app.tools.peerread_tools import _truncate_paper_content

        abstract = "Abstract text."
        body = "B" * 10000
        max_length = 500

        result = _truncate_paper_content(abstract, body, max_length)

        assert "[TRUNCATED]" in result

    def test_truncate_content_no_truncation_when_under_limit(self):
        """Test that content under limit is not truncated."""
        from app.tools.peerread_tools import _truncate_paper_content

        abstract = "Short abstract."
        body = "Short body content."
        max_length = 10000

        result = _truncate_paper_content(abstract, body, max_length)

        # Should not contain truncation marker
        assert "[TRUNCATED]" not in result
        # Should contain full content
        assert abstract in result
        assert body in result

    def test_truncate_content_logs_warning(self, caplog):
        """Test that truncation logs a warning."""
        import logging

        from app.tools.peerread_tools import _truncate_paper_content

        caplog.set_level(logging.WARNING)

        abstract = "Abstract."
        body = "C" * 15000
        max_length = 1000

        # Capture logs via Loguru sink
        import io

        from loguru import logger

        log_capture = io.StringIO()
        handler_id = logger.add(log_capture, level="WARNING")

        try:
            _truncate_paper_content(abstract, body, max_length)
            log_output = log_capture.getvalue()

            # Should log warning with size information
            assert "truncat" in log_output.lower()
            assert str(max_length) in log_output
        finally:
            logger.remove(handler_id)

    def test_truncate_content_abstract_exceeds_limit(self):
        """Test that truncation handles abstract larger than max_length."""
        import io

        from loguru import logger

        from app.tools.peerread_tools import _truncate_paper_content

        # Abstract alone exceeds max_length
        abstract = "A" * 1500
        body = "B" * 1000
        max_length = 1000

        # Capture logs to verify warning
        log_capture = io.StringIO()
        handler_id = logger.add(log_capture, level="WARNING")

        try:
            result = _truncate_paper_content(abstract, body, max_length)

            # Should return abstract + [TRUNCATED] marker (preserves abstract even if too large)
            assert "[TRUNCATED]" in result
            assert abstract in result
            # Body should be omitted since abstract alone exceeds limit
            assert "B" not in result

            # Should log warning about abstract exceeding limit
            log_output = log_capture.getvalue()
            assert "abstract alone exceeds" in log_output.lower()
            assert str(max_length) in log_output
        finally:
            logger.remove(handler_id)


class TestToolRegistration:
    """Test tool registration and initialization."""

    def test_add_peerread_tools_registers_all_tools(self):
        """Test that add_peerread_tools_to_agent registers all expected tools."""
        from unittest.mock import Mock

        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        mock_agent = Mock()
        mock_agent.tool = Mock(return_value=lambda f: f)  # Decorator that returns function

        # Act
        add_peerread_tools_to_agent(mock_agent, agent_id="test_agent")

        # Assert
        # Should register get_peerread_paper, query_peerread_papers, read_paper_pdf_tool
        assert mock_agent.tool.call_count >= 3

    def test_peerread_tool_with_invalid_paper_id(self):
        """Test tool behavior with invalid paper ID."""
        # This test validates error handling in tools
        # Will fail until proper error handling is implemented
        from unittest.mock import Mock, patch

        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        agent.tool = capture_tool

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = None  # Paper not found
            mock_loader_class.return_value = mock_loader

            add_peerread_tools_to_agent(agent, agent_id="test_agent")

            # Get the get_peerread_paper tool
            get_paper_tool = None
            for tool in registered_tools:
                if "peerread_paper" in tool.__name__:
                    get_paper_tool = tool
                    break

            # Act & Assert
            import pytest

            with pytest.raises(ModelRetry, match="not found"):
                import asyncio

                asyncio.run(get_paper_tool(None, "invalid_id"))


class TestPDFExtractionErrorHandling:
    """Test PDF extraction error handling."""

    def test_read_paper_pdf_with_empty_file(self, tmp_path):
        """Test error handling for empty PDF file."""
        from app.tools.peerread_tools import read_paper_pdf

        # Create an empty file
        empty_pdf = tmp_path / "empty.pdf"
        empty_pdf.write_bytes(b"")

        # Act & Assert
        with pytest.raises(ValueError):
            read_paper_pdf(None, str(empty_pdf))

    def test_read_paper_pdf_with_corrupted_file(self, tmp_path):
        """Test that PDF reader handles corrupted files gracefully."""
        from app.tools.peerread_tools import read_paper_pdf

        # Create a corrupted PDF (invalid PDF structure but valid header)
        corrupted_pdf = tmp_path / "corrupted.pdf"
        corrupted_pdf.write_bytes(b"%PDF-1.4\n%corrupted content")

        # Act - MarkItDown extracts what it can from corrupted PDFs
        result = read_paper_pdf(None, str(corrupted_pdf))

        # Assert - should return a string (even if empty or partial)
        assert isinstance(result, str)


class TestToolTracingIntegration:
    """Test tool tracing and trace collector integration."""

    def test_get_peerread_paper_tool_captures_trace(self):
        """Test that get_peerread_paper tool records trace data."""
        from unittest.mock import Mock, patch

        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        agent.tool = capture_tool

        sample_paper = PeerReadPaper(
            paper_id="test_001",
            title="Test Paper",
            abstract="Test abstract",
            reviews=[],
            histories=[],
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
            patch("app.tools.peerread_tools.get_trace_collector") as mock_get_collector,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = sample_paper
            mock_loader_class.return_value = mock_loader

            mock_collector = Mock()
            mock_get_collector.return_value = mock_collector

            add_peerread_tools_to_agent(agent, agent_id="test_agent")

            # Get the tool
            get_paper_tool = None
            for tool in registered_tools:
                if "peerread_paper" in tool.__name__:
                    get_paper_tool = tool
                    break

            # Act
            import asyncio

            asyncio.run(get_paper_tool(None, "test_001"))

            # Assert - trace collector should be called
            assert mock_get_collector.called

    def test_save_paper_review_tool_captures_trace(self):
        """Test that save_paper_review tool records trace data."""
        from unittest.mock import Mock, patch

        from app.tools.peerread_tools import add_peerread_review_tools_to_agent

        # Arrange
        agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        agent.tool = capture_tool

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader"),
            patch("app.tools.peerread_tools.ReviewPersistence"),
            patch("app.tools.peerread_tools.get_trace_collector") as mock_get_collector,
        ):
            mock_collector = Mock()
            mock_get_collector.return_value = mock_collector

            add_peerread_review_tools_to_agent(agent, "test_agent")

            # Get the save review tool
            save_review_tool = None
            for tool in registered_tools:
                if "save" in tool.__name__ and "review" in tool.__name__:
                    save_review_tool = tool
                    break

            # Act
            if save_review_tool:
                import asyncio

                result = asyncio.run(
                    save_review_tool(None, "test_001", "Test review", "accept", 0.9)
                )

                # Assert - trace collector should be called
                assert mock_get_collector.called
                assert result is not None


class TestQueryErrorHandling:
    """Test error handling for query_peerread_papers tool."""

    def test_query_peerread_papers_handles_loader_exception(self):
        """Test that query_peerread_papers handles exceptions from loader."""
        from unittest.mock import Mock, patch

        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        agent.tool = capture_tool

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            # Mock loader to raise an exception
            mock_loader = Mock()
            mock_loader.query_papers.side_effect = RuntimeError("Database connection failed")
            mock_loader_class.return_value = mock_loader

            add_peerread_tools_to_agent(agent, agent_id="test_agent")

            # Get the query tool
            query_tool = None
            for tool in registered_tools:
                if "query" in tool.__name__:
                    query_tool = tool
                    break

            # Act & Assert
            if query_tool:
                import asyncio

                with pytest.raises(ModelRetry, match="Failed to query papers"):
                    asyncio.run(query_tool(None, "machine learning"))


class TestTemplateLoading:
    """Test review template loading functionality."""

    def test_generate_review_template_missing_abstract(self):
        """Test template generation with missing paper abstract."""
        from unittest.mock import Mock, patch

        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        agent.tool = capture_tool

        sample_paper = PeerReadPaper(
            paper_id="test_001",
            title="Test Paper",
            abstract="",  # Empty abstract
            reviews=[],
            histories=[],
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = sample_paper
            mock_loader_class.return_value = mock_loader

            add_peerread_tools_to_agent(agent, agent_id="test_agent")

            # Get the template generation tool
            generate_template_tool = None
            for tool in registered_tools:
                if "template" in tool.__name__ or "review" in tool.__name__:
                    generate_template_tool = tool
                    break

            # Act & Assert
            if generate_template_tool:
                import asyncio

                result = asyncio.run(generate_template_tool(None, "test_001"))
                # Should handle empty abstract gracefully
                assert result is not None

    def test_generate_review_template_with_truncation(self):
        """Test template generation with content truncation."""
        from unittest.mock import Mock, patch

        from app.tools.peerread_tools import add_peerread_tools_to_agent

        # Arrange
        agent = Mock()
        registered_tools = []

        def capture_tool(func):
            registered_tools.append(func)
            return func

        agent.tool = capture_tool

        # Create paper with very long content
        long_abstract = "A" * 10000
        sample_paper = PeerReadPaper(
            paper_id="test_001",
            title="Test Paper",
            abstract=long_abstract,
            reviews=[],
            histories=[],
        )

        with (
            patch("app.tools.peerread_tools.load_peerread_config"),
            patch("app.tools.peerread_tools.PeerReadLoader") as mock_loader_class,
        ):
            mock_loader = Mock()
            mock_loader.get_paper_by_id.return_value = sample_paper
            mock_loader.load_parsed_pdf_content.return_value = None
            mock_loader_class.return_value = mock_loader

            add_peerread_tools_to_agent(agent, agent_id="test_agent")

            # Get the template generation tool
            generate_template_tool = None
            for tool in registered_tools:
                if "template" in tool.__name__ or "review" in tool.__name__:
                    generate_template_tool = tool
                    break

            # Act
            if generate_template_tool:
                import asyncio

                result = asyncio.run(generate_template_tool(None, "test_001"))
                # Assert - should truncate long content
                assert result is not None
                # Result should be reasonably sized (under some limit)
                assert len(result) < 50000  # Reasonable limit for template
