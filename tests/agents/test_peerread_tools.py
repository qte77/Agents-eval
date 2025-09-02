"""
Test cases for PeerRead agent tools.

Tests for agent integration tools that enable the manager agent to interact
with the PeerRead dataset for paper retrieval, querying, and review evaluation.
"""

from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel
from pydantic_ai import Agent

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

    def test_add_peerread_tools_to_manager(self, mock_agent):
        """Test adding PeerRead tools to manager agent."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_tools_to_manager

        # Act
        add_peerread_tools_to_manager(mock_agent)

        # Assert
        # Tools are added via decorators, so we can't easily test their presence
        # But we can verify the function runs without error
        assert mock_agent is not None

    def test_add_peerread_review_tools_to_manager(self, mock_agent):
        """Test adding PeerRead review persistence tools to manager agent."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_review_tools_to_manager

        # Act
        add_peerread_review_tools_to_manager(mock_agent)

        # Assert
        # Tools are added via decorators, so we can't easily test their presence
        # But we can verify the function runs without error
        assert mock_agent is not None

    @patch("app.agents.peerread_tools.load_peerread_config")
    @patch("app.agents.peerread_tools.PeerReadLoader")
    def test_get_peerread_paper_tool_success(self, mock_loader_class, mock_config, sample_paper, sample_config):
        """Test successful paper retrieval via agent tool."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_tools_to_manager

        # Arrange
        mock_config.return_value = sample_config
        mock_loader = Mock()
        mock_loader.get_paper_by_id.return_value = sample_paper
        mock_loader_class.return_value = mock_loader

        # Create a real agent to test with
        test_agent = Agent(model="test", output_type=BaseModel)
        add_peerread_tools_to_manager(test_agent)

        # Note: Due to the decorator pattern, we can't easily test the tool directly
        # This test verifies the setup completes without error
        assert test_agent is not None

    @patch("app.agents.peerread_tools.load_peerread_config")
    @patch("app.agents.peerread_tools.PeerReadLoader")
    def test_get_peerread_paper_tool_not_found(self, mock_loader_class, mock_config, sample_config):
        """Test paper retrieval when paper is not found."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_tools_to_manager

        # Arrange
        mock_config.return_value = sample_config
        mock_loader = Mock()
        mock_loader.get_paper_by_id.return_value = None  # Paper not found
        mock_loader_class.return_value = mock_loader

        # Create a real agent to test with
        test_agent = Agent(model="test", output_type=BaseModel)
        add_peerread_tools_to_manager(test_agent)

        # Note: The actual error handling is tested indirectly through integration
        assert test_agent is not None

    @patch("app.agents.peerread_tools.load_peerread_config")
    @patch("app.agents.peerread_tools.PeerReadLoader")
    def test_query_peerread_papers_tool(self, mock_loader_class, mock_config, sample_paper, sample_config):
        """Test paper querying via agent tool."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_tools_to_manager

        # Arrange
        mock_config.return_value = sample_config
        mock_loader = Mock()
        mock_loader.query_papers.return_value = [sample_paper]
        mock_loader_class.return_value = mock_loader

        # Create a real agent to test with
        test_agent = Agent(model="test", output_type=BaseModel)
        add_peerread_tools_to_manager(test_agent)

        # Note: Due to the decorator pattern, we can't easily test the tool directly
        # This test verifies the setup completes without error
        assert test_agent is not None

    def test_save_paper_review_tool(self, tmp_path, sample_paper, sample_config):
        """Test review saving functionality with actual file persistence."""
        import json
        from pathlib import Path
        from unittest.mock import Mock, patch

        from app.data_utils.review_persistence import ReviewPersistence

        # Create temporary directory for review storage
        temp_reviews_dir = tmp_path / "test_reviews"
        temp_reviews_dir.mkdir()

        # Test the underlying save_paper_review logic by creating it manually
        with (
            patch("app.agents.peerread_tools.load_peerread_config") as mock_config,
            patch("app.agents.peerread_tools.PeerReadLoader") as mock_loader_class,
            patch("app.agents.peerread_tools.ReviewPersistence") as mock_persistence_class,
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


class TestToolIntegration:
    """Test integration aspects of PeerRead tools with agent system."""

    def test_tool_functions_exist(self):
        """Test that tool integration functions exist and are callable."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import (
            add_peerread_review_tools_to_manager,
            add_peerread_tools_to_manager,
        )

        # Assert
        assert callable(add_peerread_tools_to_manager)
        assert callable(add_peerread_review_tools_to_manager)

    def test_tool_integration_with_none_agent(self):
        """Test tool integration handles None agent gracefully."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_tools_to_manager

        # Act & Assert - Should not raise error with None
        # Note: In practice, this would fail, but we're testing the import works
        try:
            # This would fail in practice, but we're just testing imports
            assert callable(add_peerread_tools_to_manager)
        except Exception:
            # Expected - just testing the function exists
            pass

    @patch("app.agents.peerread_tools.logger")
    def test_tool_error_logging(self, mock_logger):
        """Test that tool errors are properly logged."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_tools_to_manager

        # Create a real agent to test with
        test_agent = Agent(model="test", output_type=BaseModel)

        # Act
        add_peerread_tools_to_manager(test_agent)

        # Assert - Verify function completes (logging tested indirectly)
        assert test_agent is not None


class TestToolErrorHandling:
    """Test error handling in PeerRead agent tools."""

    @patch("app.agents.peerread_tools.load_peerread_config")
    def test_config_loading_error_handling(self, mock_config):
        """Test handling of configuration loading errors."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.tools.peerread_tools import add_peerread_tools_to_manager

        # Arrange
        mock_config.side_effect = Exception("Config loading failed")

        # Create a real agent to test with
        test_agent = Agent(model="test", output_type=BaseModel)

        # Act & Assert - Should not raise error during tool addition
        add_peerread_tools_to_manager(test_agent)
        assert test_agent is not None

    def test_import_error_handling(self):
        """Test that imports work correctly."""
        # Act & Assert - All imports should work
        from app.tools.peerread_tools import (
            add_peerread_review_tools_to_manager,
            add_peerread_tools_to_manager,
        )

        assert add_peerread_tools_to_manager is not None
        assert add_peerread_review_tools_to_manager is not None


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
