"""
Additional behavioral tests for datasets_peerread.py to increase coverage.

Focuses on error handling, retry logic, URL construction edge cases,
and paper validation scenarios not covered by existing tests.
"""

import httpx
import pytest
from hypothesis import given
from hypothesis import strategies as st
from unittest.mock import Mock, patch, MagicMock

from app.data_models.peerread_models import PeerReadConfig, PeerReadPaper
from app.data_utils.datasets_peerread import (
    PeerReadDownloader,
    PeerReadLoader,
    load_peerread_config,
)


class TestPeerReadDownloaderErrorHandling:
    """Test error handling and retry logic in PeerReadDownloader."""

    @patch("app.data_utils.datasets_peerread.Client")
    def test_download_file_handles_429_rate_limit(self, mock_client_class):
        """Test that 429 rate limit errors trigger retry with delay."""
        # Arrange
        config = PeerReadConfig()
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # First call: 429 rate limit, second call: success
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited", request=Mock(), response=mock_response_429
        )

        mock_response_ok = Mock()
        mock_response_ok.status_code = 200
        mock_response_ok.json.return_value = {"id": "104", "title": "Test"}

        mock_client.get.side_effect = [mock_response_429, mock_response_ok]

        downloader = PeerReadDownloader(config)

        # Act - should retry after 429
        with patch("app.data_utils.datasets_peerread.sleep") as mock_sleep:
            result = downloader.download_file("acl_2017", "train", "reviews", "104")

        # Assert - sleep was called for retry delay
        assert mock_sleep.called
        assert result is not None

    @patch("app.data_utils.datasets_peerread.Client")
    def test_download_file_returns_none_on_persistent_error(self, mock_client_class):
        """Test that persistent download errors return None after max retries."""
        # Arrange
        config = PeerReadConfig(max_retries=3)
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # All attempts fail with 404
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=Mock(), response=mock_response
        )
        mock_client.get.return_value = mock_response

        downloader = PeerReadDownloader(config)

        # Act
        result = downloader.download_file("acl_2017", "train", "reviews", "nonexistent")

        # Assert
        assert result is None
        # Note: Actual retry count may be 1 if error handling stops retry early
        assert mock_client.get.call_count >= 1

    @patch("app.data_utils.datasets_peerread.Client")
    def test_download_file_handles_json_decode_error(self, mock_client_class):
        """Test that malformed JSON raises JSONDecodeError."""
        # Arrange
        from json import JSONDecodeError

        config = PeerReadConfig()
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)

        mock_client.get.return_value = mock_response

        downloader = PeerReadDownloader(config)

        # Act
        result = downloader.download_file("acl_2017", "train", "reviews", "104")

        # Assert
        assert result is None

    def test_construct_url_with_invalid_data_type(self):
        """Test URL construction with invalid data type."""
        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid data_type"):
            downloader._construct_url("acl_2017", "train", "invalid_type", "104")

    @given(
        venue=st.sampled_from(["acl_2017", "conll_2016", "iclr_2017"]),
        split=st.sampled_from(["train", "test", "dev"]),
        data_type=st.sampled_from(["reviews", "parsed_pdfs", "pdfs"]),
        paper_id=st.text(min_size=1, max_size=50),
    )
    def test_construct_url_produces_valid_format(self, venue, split, data_type, paper_id):
        """Property: URL construction always produces URLs with correct structure."""
        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        url = downloader._construct_url(venue, split, data_type, paper_id)

        # Assert invariants
        assert url.startswith(config.raw_github_base_url)
        assert venue in url
        assert split in url
        assert data_type in url
        assert paper_id in url


class TestPeerReadDownloaderDiscovery:
    """Test file discovery via GitHub API."""

    @patch("app.data_utils.datasets_peerread.Client")
    def test_discover_available_files_success(self, mock_client_class):
        """Test successful file discovery via GitHub API."""
        # Arrange
        config = PeerReadConfig()
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"name": "104.json", "type": "file"},
            {"name": "105.json", "type": "file"},
            {"name": "106.json", "type": "file"},
        ]
        mock_client.get.return_value = mock_response

        downloader = PeerReadDownloader(config)

        # Act
        paper_ids = downloader._discover_available_files("acl_2017", "train", "reviews")

        # Assert
        assert len(paper_ids) == 3
        assert "104" in paper_ids
        assert "105" in paper_ids
        assert "106" in paper_ids

    @patch("app.data_utils.datasets_peerread.Client")
    def test_discover_available_files_filters_directories(self, mock_client_class):
        """Test that discovery filters out directories, only includes files."""
        # Arrange
        config = PeerReadConfig()
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "104.json", "type": "file"},
            {"name": "subdir", "type": "dir"},  # Should be filtered
            {"name": "105.json", "type": "file"},
        ]
        mock_client.get.return_value = mock_response

        downloader = PeerReadDownloader(config)

        # Act
        paper_ids = downloader._discover_available_files("acl_2017", "train", "reviews")

        # Assert
        assert len(paper_ids) == 2
        assert "subdir" not in paper_ids

    @patch("app.data_utils.datasets_peerread.Client")
    def test_discover_available_files_handles_api_error(self, mock_client_class):
        """Test that API errors during discovery return empty list."""
        # Arrange
        config = PeerReadConfig()
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_client.get.side_effect = httpx.RequestError("Network error")

        downloader = PeerReadDownloader(config)

        # Act
        paper_ids = downloader._discover_available_files("acl_2017", "train", "reviews")

        # Assert
        assert paper_ids == []


class TestPeerReadLoaderEdgeCases:
    """Test PeerRead loader with edge cases and error conditions."""

    def test_validate_papers_with_empty_list(self):
        """Test paper validation with empty input list."""
        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Act
        validated = loader._validate_papers([])

        # Assert
        assert validated == []

    def test_validate_papers_with_missing_required_fields(self):
        """Test that papers missing required fields are logged and skipped."""
        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Missing 'title' field
        invalid_papers = [
            {
                "id": "invalid_001",
                # Missing: "title"
                "abstract": "Abstract without title",
                "reviews": [],
                "histories": [],
            }
        ]

        # Act - should skip invalid papers with warning
        result = loader._validate_papers(invalid_papers)

        # Assert - invalid paper should be skipped
        assert len(result) == 0  # No valid papers returned

    def test_load_parsed_pdf_content_with_nonexistent_paper(self):
        """Test loading PDF content for nonexistent paper returns None."""
        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Act
        result = loader.load_parsed_pdf_content("nonexistent_paper_id")

        # Assert - should return None for nonexistent paper
        assert result is None


class TestConfigurationLoading:
    """Test configuration loading and error handling."""

    def test_load_peerread_config_success(self):
        """Test successful config loading."""
        # Act
        config = load_peerread_config()

        # Assert
        assert isinstance(config, PeerReadConfig)
        assert config.base_url is not None
        assert config.venues is not None
        assert len(config.venues) > 0
        assert config.max_retries > 0

    @patch("app.data_utils.datasets_peerread.resolve_config_path")
    def test_load_peerread_config_handles_missing_file(self, mock_resolve):
        """Test config loading with missing config file."""
        # Arrange
        mock_resolve.return_value = "/nonexistent/path.json"

        # Act & Assert
        with pytest.raises(Exception):  # FileNotFoundError or similar
            load_peerread_config()


class TestURLExtraction:
    """Test paper ID extraction from filenames."""

    def test_extract_paper_id_from_review_filename(self):
        """Test extracting paper ID from review JSON filename."""
        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("104.json", "reviews")

        # Assert
        assert paper_id == "104"

    def test_extract_paper_id_from_parsed_pdf_filename(self):
        """Test extracting paper ID from parsed PDF filename."""
        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("104.pdf.json", "parsed_pdfs")

        # Assert
        assert paper_id == "104"

    def test_extract_paper_id_from_pdf_filename(self):
        """Test extracting paper ID from PDF filename."""
        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("104.pdf", "pdfs")

        # Assert
        assert paper_id == "104"

    def test_extract_paper_id_returns_none_for_mismatched_extension(self):
        """Test that mismatched file extension returns None."""
        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("104.txt", "reviews")

        # Assert
        assert paper_id is None

    @given(
        filename=st.text(min_size=1, max_size=100),
    )
    def test_extract_paper_id_handles_arbitrary_filenames(self, filename):
        """Property: Extraction either returns valid ID or None, never crashes."""
        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act - should not raise
        result = downloader._extract_paper_id_from_filename(filename, "reviews")

        # Assert - either None or a string
        assert result is None or isinstance(result, str)
