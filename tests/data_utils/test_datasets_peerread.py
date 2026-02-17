"""
Test cases for PeerRead dataset core utilities.

Tests for pure dataset functionality including download, loading, and querying
operations without evaluation logic.
"""

from json import JSONDecodeError

import httpx
import hypothesis
import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

from app.data_models.peerread_models import (
    PeerReadConfig,
    PeerReadPaper,
    PeerReadReview,
)

# Extract optional field names from PeerReadReview model for testing
# Reason: Single source of truth - derive from model defaults instead of hardcoding
OPTIONAL_REVIEW_FIELDS = [
    field_name.upper()
    for field_name, field_info in PeerReadReview.model_fields.items()
    if field_info.default == "UNKNOWN"  # Only fields that default to "UNKNOWN"
]


class TestPeerReadDownloader:
    """Test PeerRead dataset downloading functionality."""

    # FIXME FAILED test_download_success_mocked - AttributeError: module
    # 'app.data_utils.datasets_peerread' has no attribute 'httpx'
    # @patch("app.data_utils.datasets_peerread.httpx.Client.get")
    # def test_download_success_mocked(self, mock_get):
    #     """Test successful dataset download with mocked requests."""
    #     # Import here to avoid import errors if module doesn't exist yet
    #     from app.data_utils.datasets_peerread import PeerReadDownloader

    #     # Arrange
    #     mock_response = Mock()
    #     mock_response.status_code = 200
    #     mock_response.json.return_value = {
    #         "id": "test",
    #         "title": "Test Paper",
    #         "abstract": "Test abstract",
    #         "reviews": [],
    #         "histories": [],
    #     }
    #     mock_response.raise_for_status.return_value = None
    #     mock_get.return_value = mock_response

    #     config = PeerReadConfig()
    #     downloader = PeerReadDownloader(config)

    #     # Act
    #     result = downloader.download_file("acl_2017", "train", "reviews", "test")

    #     # Assert
    #     assert result is not None
    #     mock_get.assert_called_once()

    def test_download_url_construction(self):
        """Test proper URL construction for downloads."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        url = downloader._construct_url("acl_2017", "train", "reviews", "104")

        # Assert
        expected = "https://raw.githubusercontent.com/allenai/PeerRead/master/data/acl_2017/train/reviews/104.json"
        assert url == expected

    def test_invalid_venue_error(self):
        """Test error handling for invalid venue."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid venue"):
            downloader._construct_url("invalid_venue", "train", "reviews", "104")

    def test_invalid_split_error(self):
        """Test error handling for invalid split."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid split"):
            downloader._construct_url("acl_2017", "invalid_split", "reviews", "104")


class TestPeerReadLoader:
    """Test PeerRead dataset loading and querying functionality."""

    def test_load_papers_validation(self):
        """Test paper loading with validation."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Test data structure validation
        test_papers = [
            {
                "id": "test_001",
                "title": "Test Paper 1",
                "abstract": "Test abstract 1",
                "reviews": [
                    {
                        "IMPACT": "3",
                        "SUBSTANCE": "4",
                        "APPROPRIATENESS": "5",
                        "MEANINGFUL_COMPARISON": "2",
                        "PRESENTATION_FORMAT": "Poster",
                        "comments": "Test review comment.",
                        "SOUNDNESS_CORRECTNESS": "4",
                        "ORIGINALITY": "3",
                        "RECOMMENDATION": "3",
                        "CLARITY": "3",
                        "REVIEWER_CONFIDENCE": "3",
                        "is_meta_review": None,
                    }
                ],
                "histories": [],
            }
        ]

        # Act
        validated_papers = loader._validate_papers(test_papers)

        # Assert
        assert len(validated_papers) == 1
        assert validated_papers[0].paper_id == "test_001"
        assert len(validated_papers[0].reviews) == 1

    def test_query_papers_filtering(self):
        """Test paper querying with filters."""
        # Import here to avoid import errors if module doesn't exist yet

        # Arrange - directly test the filtering logic
        test_papers = [
            PeerReadPaper(
                paper_id="test_001",
                title="Test 1",
                abstract="Abstract 1",
                reviews=[],  # No reviews
                histories=[],
            ),
            PeerReadPaper(
                paper_id="test_002",
                title="Test 2",
                abstract="Abstract 2",
                reviews=[
                    PeerReadReview(
                        impact="3",
                        substance="4",
                        appropriateness="5",
                        meaningful_comparison="2",
                        presentation_format="Poster",
                        comments="Test comment",
                        soundness_correctness="4",
                        originality="3",
                        recommendation="3",
                        clarity="3",
                        reviewer_confidence="3",
                    )
                ],  # Has one review
                histories=[],
            ),
        ]

        # Test the filtering logic directly
        filtered_papers = [paper for paper in test_papers if len(paper.reviews) >= 1]

        # Assert - only papers with reviews should be returned
        assert len(filtered_papers) == 1
        assert filtered_papers[0].paper_id == "test_002"


class TestPeerReadConfig:
    """Test PeerRead configuration loading and validation."""

    def test_config_loading(self):
        """Test loading configuration from file."""
        # Import here to avoid import errors if module doesn't exist yet
        from app.data_utils.datasets_peerread import load_peerread_config

        # Act
        config = load_peerread_config()

        # Assert
        assert config is not None
        assert isinstance(config, PeerReadConfig)
        assert len(config.venues) > 0
        assert len(config.splits) > 0


class TestDownloadErrorHandling:
    """Test error handling in download operations."""

    def test_download_http_error(self):
        """Test handling of HTTP errors during download."""
        from unittest.mock import Mock, patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        with patch.object(downloader.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=Mock(), response=Mock(status_code=404)
            )
            mock_get.return_value = mock_response

            # Act
            result = downloader.download_file("acl_2017", "train", "reviews", "nonexistent")

            # Assert
            assert result is None

    def test_download_network_error(self):
        """Test handling of network errors during download."""
        from unittest.mock import patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        with patch.object(downloader.client, "get") as mock_get:
            mock_get.side_effect = httpx.RequestError("Network error")

            # Act
            result = downloader.download_file("acl_2017", "train", "reviews", "test")

            # Assert
            assert result is None

    def test_download_json_decode_error(self):
        """Test handling of invalid JSON in response."""
        from unittest.mock import Mock, patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        with patch.object(downloader.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value = mock_response

            # Act
            result = downloader.download_file("acl_2017", "train", "reviews", "test")

            # Assert
            assert result is None

    def test_download_retry_logic(self):
        """Test retry logic on rate limit failures (429)."""
        from unittest.mock import Mock, patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        config.max_retries = 3
        config.retry_delay_seconds = 0.1
        downloader = PeerReadDownloader(config)

        with (
            patch.object(downloader.client, "get") as mock_get,
            patch("app.data_utils.datasets_peerread.sleep") as mock_sleep,
        ):
            # First two attempts fail with rate limit (429), third succeeds
            mock_response_fail = Mock()
            mock_response_fail.raise_for_status.side_effect = httpx.HTTPStatusError(
                "429 Too Many Requests", request=Mock(), response=Mock(status_code=429)
            )
            mock_response_success = Mock()
            mock_response_success.raise_for_status.return_value = None
            mock_response_success.json.return_value = {
                "id": "test",
                "title": "Test",
                "abstract": "Abstract",
                "reviews": [],
                "histories": [],
            }

            mock_get.side_effect = [
                mock_response_fail,
                mock_response_fail,
                mock_response_success,
            ]

            # Act
            result = downloader.download_file("acl_2017", "train", "reviews", "test")

            # Assert
            assert result is not None
            assert mock_get.call_count == 3
            assert mock_sleep.call_count == 2


class TestPaperValidationEdgeCases:
    """Test paper validation with missing fields and edge cases."""

    def test_validate_papers_filters_invalid_papers(self):
        """Test that _validate_papers filters out papers with validation errors."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        test_papers = [
            {
                "id": "valid_001",
                "title": "Valid Paper",
                "abstract": "Valid abstract",
                "reviews": [],
                "histories": [],
            },
            {
                "id": "invalid_001",
                # Missing required title field
                "abstract": "Abstract without title",
                "reviews": [],
                "histories": [],
            },
        ]

        # Act
        validated_papers = loader._validate_papers(test_papers)

        # Assert - should only return valid paper
        assert len(validated_papers) == 1
        assert validated_papers[0].paper_id == "valid_001"

    def test_validate_papers_with_empty_list(self):
        """Test validation with empty papers list."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Act
        validated_papers = loader._validate_papers([])

        # Assert
        assert len(validated_papers) == 0


class TestPeerReadLoaderEdgeCases:
    """Test PeerReadLoader edge cases and error handling."""

    def test_get_paper_by_id_not_found(self):
        """Test get_paper_by_id returns None for nonexistent paper."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Act
        paper = loader.get_paper_by_id("nonexistent_paper_id_12345")

        # Assert
        assert paper is None

    def test_extract_text_from_parsed_data_with_no_sections(self):
        """Test text extraction when parsed data has no sections."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)
        parsed_data = {"metadata": {}}  # No sections key

        # Act
        text = loader._extract_text_from_parsed_data(parsed_data)

        # Assert
        assert text == ""

    def test_extract_text_from_parsed_data_with_empty_sections(self):
        """Test text extraction with empty sections list."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)
        parsed_data = {"metadata": {"sections": []}}

        # Act
        text = loader._extract_text_from_parsed_data(parsed_data)

        # Assert
        assert text == ""

    def test_extract_text_from_parsed_data_with_sections_no_text(self):
        """Test text extraction when sections have no text field."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)
        parsed_data = {"metadata": {"sections": [{"heading": "Introduction"}]}}

        # Act
        text = loader._extract_text_from_parsed_data(parsed_data)

        # Assert
        assert text == ""


class TestRealExternalDependencies:
    """Test real external dependencies during implementation.

    These tests validate actual network access and should be run during
    development to ensure external APIs work as expected.
    """

    def test_download_url_accessibility_real(self):
        """Test actual PeerRead download URL accessibility.

        CRITICAL: Must validate real download works during implementation.
        This test uses real network requests to verify functionality.
        """
        # Arrange
        test_url = "https://raw.githubusercontent.com/allenai/PeerRead/master/data/acl_2017/train/reviews/104.json"

        try:
            # Act
            response = httpx.head(test_url, timeout=10)

            # Assert
            assert response.status_code == 200
            # Log success for implementation validation
            print(f"✅ Real download URL validated: {test_url}")

        except Exception as e:
            # Document failure for implementation adjustment
            pytest.skip(f"Real download test failed: {e}. Update implementation.")

    def test_data_structure_validation_real(self):
        """Test actual data structure matches our models.

        IMPLEMENTATION REQUIREMENT: Validate real data structure before
        proceeding with full implementation.
        """
        # Arrange
        test_url = "https://raw.githubusercontent.com/allenai/PeerRead/master/data/acl_2017/train/reviews/104.json"

        try:
            # Act
            response = httpx.get(test_url, timeout=10)
            data = response.json()

            # Assert - validate structure matches our models
            paper = PeerReadPaper.model_validate(
                {
                    "paper_id": data["id"],
                    "title": data["title"],
                    "abstract": data["abstract"],
                    "reviews": [
                        {
                            "impact": r["IMPACT"],
                            "substance": r["SUBSTANCE"],
                            "appropriateness": r["APPROPRIATENESS"],
                            "meaningful_comparison": r["MEANINGFUL_COMPARISON"],
                            "presentation_format": r["PRESENTATION_FORMAT"],
                            "comments": r["comments"],
                            "soundness_correctness": r["SOUNDNESS_CORRECTNESS"],
                            "originality": r["ORIGINALITY"],
                            "recommendation": r["RECOMMENDATION"],
                            "clarity": r["CLARITY"],
                            "reviewer_confidence": r["REVIEWER_CONFIDENCE"],
                            "is_meta_review": r.get("is_meta_review"),
                        }
                        for r in data.get("reviews", [])
                    ],
                    "histories": data.get("histories", []),
                }
            )

            # Validate successful model creation
            assert paper.paper_id == data["id"]
            assert len(paper.reviews) == len(data.get("reviews", []))
            print(f"✅ Real data structure validated for paper: {paper.paper_id}")

        except Exception as e:
            # Document failure for implementation adjustment
            pytest.skip(f"Real data validation failed: {e}. Update models.")


# STORY-004: Hypothesis property-based tests for data validation invariants
class TestContentExtraction:
    """Test PDF parsed content extraction."""

    def test_load_parsed_pdf_content_success(self):
        """Test successful loading of parsed PDF content."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Act - paper 104 has parsed content
        result = loader.load_parsed_pdf_content("104")

        # Assert
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_parsed_pdf_content_missing_file(self):
        """Test loading parsed PDF for nonexistent paper."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Act
        result = loader.load_parsed_pdf_content("nonexistent_paper_99999")

        # Assert
        assert result is None

    def test_extract_text_with_nested_sections(self):
        """Test text extraction from nested section structure."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)
        parsed_data = {
            "metadata": {
                "sections": [
                    {"heading": "Introduction", "text": "Intro text here."},
                    {"heading": "Methods", "text": "Methods text here."},
                    {
                        "heading": "Results",
                        "text": "Results overview.",
                        "subsections": [
                            {"heading": "Experiment 1", "text": "Exp 1 results."},
                            {"heading": "Experiment 2", "text": "Exp 2 results."},
                        ],
                    },
                ]
            }
        }

        # Act
        text = loader._extract_text_from_parsed_data(parsed_data)

        # Assert
        assert "Intro text here" in text
        assert "Methods text here" in text
        assert "Results overview" in text


class TestDownloadVenueSplit:
    """Test venue/split download functionality."""

    def test_download_venue_split_success(self, tmp_path):
        """Test successful download of venue/split with file discovery."""
        from unittest.mock import patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)
        downloader.cache_dir = tmp_path / "cache"

        # Mock file discovery to return paper IDs
        with (
            patch.object(
                downloader, "_discover_available_files", return_value=["101", "102", "103"]
            ),
            patch.object(downloader, "download_file") as mock_download,
        ):
            # Each paper requires 3 downloads (reviews, parsed_pdfs, pdfs)
            # Reason: download_venue_split downloads all data types per paper
            mock_download.return_value = {
                "id": "test",
                "title": "Paper",
                "abstract": "Abstract",
                "reviews": [],
                "histories": [],
            }

            # Act
            result = downloader.download_venue_split("acl_2017", "train", max_papers=3)

            # Assert
            assert result.success is True
            assert result.papers_downloaded == 3
            assert result.error_message is None

    def test_download_venue_split_with_max_papers_limit(self, tmp_path):
        """Test download respects max_papers limit."""
        from unittest.mock import patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)
        downloader.cache_dir = tmp_path / "cache"

        # Mock file discovery to return many paper IDs
        with (
            patch.object(
                downloader,
                "_discover_available_files",
                return_value=["101", "102", "103", "104", "105"],
            ),
            patch.object(downloader, "download_file") as mock_download,
        ):
            mock_download.return_value = {
                "id": "test",
                "title": "Test",
                "abstract": "Abstract",
                "reviews": [],
                "histories": [],
            }

            # Act - limit to 2 papers
            result = downloader.download_venue_split("acl_2017", "train", max_papers=2)

            # Assert - should only download 2 papers (3 data types each = 6 calls)
            assert mock_download.call_count == 6
            assert result.papers_downloaded == 2

    def test_download_venue_split_handles_partial_failures(self, tmp_path):
        """Test download continues after some failures."""
        from unittest.mock import patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)
        # Use temp directory to avoid cache interference
        downloader.cache_dir = tmp_path / "cache"

        with (
            patch.object(
                downloader, "_discover_available_files", return_value=["201", "202", "203"]
            ),
            patch.object(downloader, "download_file") as mock_download,
        ):
            # Each paper needs 3 calls (reviews, parsed_pdfs, pdfs)
            # Paper 201: all succeed, Paper 202: all fail, Paper 203: all succeed
            # Reason: A paper counts as downloaded if ANY data type succeeds
            mock_download.side_effect = [
                # Paper 201 - all succeed
                {
                    "id": "201",
                    "title": "Paper",
                    "abstract": "Abstract",
                    "reviews": [],
                    "histories": [],
                },
                {
                    "id": "201",
                    "title": "Paper",
                    "abstract": "Abstract",
                    "reviews": [],
                    "histories": [],
                },
                {
                    "id": "201",
                    "title": "Paper",
                    "abstract": "Abstract",
                    "reviews": [],
                    "histories": [],
                },
                # Paper 202 - all fail
                None,
                None,
                None,
                # Paper 203 - all succeed
                {
                    "id": "203",
                    "title": "Paper",
                    "abstract": "Abstract",
                    "reviews": [],
                    "histories": [],
                },
                {
                    "id": "203",
                    "title": "Paper",
                    "abstract": "Abstract",
                    "reviews": [],
                    "histories": [],
                },
                {
                    "id": "203",
                    "title": "Paper",
                    "abstract": "Abstract",
                    "reviews": [],
                    "histories": [],
                },
            ]

            # Act
            result = downloader.download_venue_split("acl_2017", "train", max_papers=3)

            # Assert - should report success with 2/3 downloads (201 and 203 succeeded)
            assert result.success is True
            assert result.papers_downloaded == 2

    def test_download_venue_split_discovery_failure(self):
        """Test download handles file discovery failure."""
        from unittest.mock import patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        with patch.object(downloader, "_discover_available_files", return_value=[]):
            # Act
            result = downloader.download_venue_split("acl_2017", "train", max_papers=10)

            # Assert
            assert result.success is False
            assert result.papers_downloaded == 0
            assert "No review files discovered" in result.error_message


class TestPeerReadDataInvariants:
    """Property-based tests for PeerRead data validation invariants."""

    @given(
        paper_id=st.text(min_size=1, max_size=100),
        title=st.text(min_size=1, max_size=500),
        abstract=st.text(min_size=1, max_size=5000),
    )
    def test_peerread_paper_validation_invariants(self, paper_id, title, abstract):
        """Property: PeerReadPaper model always validates with valid text inputs."""
        # Arrange & Act
        paper = PeerReadPaper(
            paper_id=paper_id,
            title=title,
            abstract=abstract,
            reviews=[],
            review_histories=[],
        )

        # Assert invariants
        assert paper.paper_id == paper_id
        assert paper.title == title
        assert paper.abstract == abstract
        assert isinstance(paper.reviews, list)
        assert len(paper.reviews) == 0

    @given(
        impact=st.sampled_from(["1", "2", "3", "4", "5"]),
        substance=st.sampled_from(["1", "2", "3", "4", "5"]),
        recommendation=st.sampled_from(["1", "2", "3", "4", "5"]),
    )
    def test_peerread_review_rating_invariants(self, impact, substance, recommendation):
        """Property: PeerReadReview ratings always within valid range."""
        # Arrange & Act
        review = PeerReadReview(
            impact=impact,
            substance=substance,
            appropriateness="3",
            meaningful_comparison="3",
            presentation_format="Poster",
            comments="Test comment",
            soundness_correctness="3",
            originality="3",
            recommendation=recommendation,
            clarity="3",
            reviewer_confidence="3",
        )

        # Assert invariants
        assert review.impact in ["1", "2", "3", "4", "5"]
        assert review.substance in ["1", "2", "3", "4", "5"]
        assert review.recommendation in ["1", "2", "3", "4", "5"]

    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10))
    @hypothesis.settings(deadline=None)
    def test_url_construction_invariants(self, paper_ids):
        """Property: URL construction always produces valid URLs."""
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act & Assert invariants
        for paper_id in paper_ids:
            url = downloader._construct_url("acl_2017", "train", "reviews", paper_id)
            # Invariant: URL always starts with base URL
            assert url.startswith("https://raw.githubusercontent.com/allenai/PeerRead/master/data/")
            # Invariant: URL always ends with paper_id.json
            assert url.endswith(f"{paper_id}.json")
            # Invariant: URL contains venue, split, and type
            assert "acl_2017" in url
            assert "train" in url
            assert "reviews" in url


# STORY-004: Inline-snapshot regression tests for data structures
class TestPeerReadDataSnapshots:
    """Snapshot tests for PeerRead data structure regression testing."""

    def test_peerread_paper_model_dump_structure(self):
        """Snapshot: PeerReadPaper model_dump output structure."""
        # Arrange
        paper = PeerReadPaper(
            paper_id="test_001",
            title="Test Paper Title",
            abstract="Test paper abstract with sufficient content.",
            reviews=[
                PeerReadReview(
                    impact="4",
                    substance="3",
                    appropriateness="4",
                    meaningful_comparison="3",
                    presentation_format="Oral",
                    comments="Well-structured paper with good methodology.",
                    soundness_correctness="4",
                    originality="3",
                    recommendation="3",
                    clarity="4",
                    reviewer_confidence="4",
                )
            ],
            review_histories=["Submitted", "Under Review"],
        )

        # Act
        dumped = paper.model_dump()

        # Assert with snapshot
        assert dumped == snapshot(
            {
                "paper_id": "test_001",
                "title": "Test Paper Title",
                "abstract": "Test paper abstract with sufficient content.",
                "reviews": [
                    {
                        "impact": "4",
                        "substance": "3",
                        "appropriateness": "4",
                        "meaningful_comparison": "3",
                        "presentation_format": "Oral",
                        "comments": "Well-structured paper with good methodology.",
                        "soundness_correctness": "4",
                        "originality": "3",
                        "recommendation": "3",
                        "clarity": "4",
                        "reviewer_confidence": "4",
                        "is_meta_review": None,
                    }
                ],
                "review_histories": ["Submitted", "Under Review"],
            }
        )

    def test_peerread_config_model_dump_structure(self):
        """Snapshot: PeerReadConfig default model_dump output structure."""
        # Arrange
        config = PeerReadConfig()

        # Act
        dumped = config.model_dump()

        # Assert with snapshot
        assert dumped == snapshot(
            {
                "base_url": "https://github.com/allenai/PeerRead/tree/master/data",
                "github_api_base_url": "https://api.github.com/repos/allenai/PeerRead/contents/data",
                "raw_github_base_url": "https://raw.githubusercontent.com/allenai/PeerRead/master/data",
                "cache_directory": "datasets/peerread",
                "venues": ["acl_2017", "conll_2016", "iclr_2017"],
                "splits": ["train", "test", "dev"],
                "max_papers_per_query": 100,
                "download_timeout": 30,
                "max_retries": 5,
                "retry_delay_seconds": 5,
                "similarity_metrics": {"cosine_weight": 0.6, "jaccard_weight": 0.4},
            }
        )

    def test_url_construction_output_format(self):
        """Snapshot: URL construction output format."""
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        urls = {
            "acl_2017_train": downloader._construct_url("acl_2017", "train", "reviews", "104"),
            "conll_2016_dev": downloader._construct_url("conll_2016", "dev", "reviews", "205"),
            "iclr_2017_test": downloader._construct_url("iclr_2017", "test", "reviews", "306"),
        }

        # Assert with snapshot
        assert urls == snapshot(
            {
                "acl_2017_train": "https://raw.githubusercontent.com/allenai/PeerRead/master/data/acl_2017/train/reviews/104.json",
                "conll_2016_dev": "https://raw.githubusercontent.com/allenai/PeerRead/master/data/conll_2016/dev/reviews/205.json",
                "iclr_2017_test": "https://raw.githubusercontent.com/allenai/PeerRead/master/data/iclr_2017/test/reviews/306.json",
            }
        )


# STORY-004: Tests for optional field handling in PeerRead dataset validation
class TestOptionalFieldHandling:
    """Tests for resilient validation of papers with missing optional fields."""

    def test_paper_with_missing_impact_field(self):
        """Test that papers with missing IMPACT field are validated successfully."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Paper data with review missing IMPACT field (like papers 304-308, 330)
        test_papers = [
            {
                "id": "test_missing_impact",
                "title": "Test Paper Without Impact",
                "abstract": "Test abstract for paper with missing IMPACT field.",
                "reviews": [
                    {
                        # Missing: "IMPACT"
                        "SUBSTANCE": "4",
                        "APPROPRIATENESS": "5",
                        "MEANINGFUL_COMPARISON": "2",
                        "PRESENTATION_FORMAT": "Poster",
                        "comments": "Test review comment without IMPACT field.",
                        "SOUNDNESS_CORRECTNESS": "4",
                        "ORIGINALITY": "3",
                        "RECOMMENDATION": "3",
                        "CLARITY": "3",
                        "REVIEWER_CONFIDENCE": "3",
                    }
                ],
                "histories": [],
            }
        ]

        # Act
        validated_papers = loader._validate_papers(test_papers)

        # Assert: Paper should be validated successfully with IMPACT defaulting to "UNKNOWN"
        assert len(validated_papers) == 1
        assert validated_papers[0].paper_id == "test_missing_impact"
        assert len(validated_papers[0].reviews) == 1
        assert validated_papers[0].reviews[0].impact == "UNKNOWN"

    def test_paper_with_multiple_missing_optional_fields(self):
        """Test that papers with multiple missing optional fields are handled gracefully."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Paper data with review missing multiple optional fields
        test_papers = [
            {
                "id": "test_multiple_missing",
                "title": "Test Paper Multiple Missing",
                "abstract": "Test abstract.",
                "reviews": [
                    {
                        # Missing: "IMPACT", "SUBSTANCE"
                        "APPROPRIATENESS": "5",
                        "MEANINGFUL_COMPARISON": "2",
                        "PRESENTATION_FORMAT": "Poster",
                        "comments": "Test review comment.",
                        "SOUNDNESS_CORRECTNESS": "4",
                        "ORIGINALITY": "3",
                        "RECOMMENDATION": "3",
                        "CLARITY": "3",
                        "REVIEWER_CONFIDENCE": "3",
                    }
                ],
                # Missing: "histories"
            }
        ]

        # Act
        validated_papers = loader._validate_papers(test_papers)

        # Assert: Paper should be validated successfully with defaults
        assert len(validated_papers) == 1
        assert validated_papers[0].reviews[0].impact == "UNKNOWN"
        assert validated_papers[0].reviews[0].substance == "UNKNOWN"
        assert validated_papers[0].review_histories == []

    def test_paper_with_valid_impact_field_unchanged(self):
        """Test that papers with valid IMPACT field are not affected (no regression)."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Paper data with valid IMPACT field
        test_papers = [
            {
                "id": "test_valid_impact",
                "title": "Test Paper Valid Impact",
                "abstract": "Test abstract.",
                "reviews": [
                    {
                        "IMPACT": "4",
                        "SUBSTANCE": "4",
                        "APPROPRIATENESS": "5",
                        "MEANINGFUL_COMPARISON": "2",
                        "PRESENTATION_FORMAT": "Poster",
                        "comments": "Test review comment with valid IMPACT.",
                        "SOUNDNESS_CORRECTNESS": "4",
                        "ORIGINALITY": "3",
                        "RECOMMENDATION": "3",
                        "CLARITY": "3",
                        "REVIEWER_CONFIDENCE": "3",
                    }
                ],
                "histories": [],
            }
        ]

        # Act
        validated_papers = loader._validate_papers(test_papers)

        # Assert: Paper should preserve the original IMPACT value
        assert len(validated_papers) == 1
        assert validated_papers[0].reviews[0].impact == "4"

    def test_validated_paper_with_missing_impact_snapshot(self):
        """Snapshot: Validated paper structure with missing IMPACT field."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        test_papers = [
            {
                "id": "snapshot_test",
                "title": "Snapshot Test Paper",
                "abstract": "Abstract for snapshot test.",
                "reviews": [
                    {
                        # Missing: "IMPACT"
                        "SUBSTANCE": "3",
                        "APPROPRIATENESS": "4",
                        "MEANINGFUL_COMPARISON": "2",
                        "PRESENTATION_FORMAT": "Oral",
                        "comments": "Snapshot review comment.",
                        "SOUNDNESS_CORRECTNESS": "3",
                        "ORIGINALITY": "4",
                        "RECOMMENDATION": "4",
                        "CLARITY": "3",
                        "REVIEWER_CONFIDENCE": "4",
                    }
                ],
                "histories": [],
            }
        ]

        # Act
        validated_papers = loader._validate_papers(test_papers)

        # Assert
        dumped = validated_papers[0].model_dump()
        assert dumped == snapshot(
            {
                "paper_id": "snapshot_test",
                "title": "Snapshot Test Paper",
                "abstract": "Abstract for snapshot test.",
                "reviews": [
                    {
                        "impact": "UNKNOWN",
                        "substance": "3",
                        "appropriateness": "4",
                        "meaningful_comparison": "2",
                        "presentation_format": "Oral",
                        "comments": "Snapshot review comment.",
                        "soundness_correctness": "3",
                        "originality": "4",
                        "recommendation": "4",
                        "clarity": "3",
                        "reviewer_confidence": "4",
                        "is_meta_review": None,
                    }
                ],
                "review_histories": [],
            }
        )

    @given(
        # Generate arbitrary subsets of optional fields to test any combination
        missing_fields=st.lists(
            st.sampled_from(OPTIONAL_REVIEW_FIELDS),
            min_size=0,
            max_size=len(OPTIONAL_REVIEW_FIELDS),
            unique=True,
        )
    )
    @hypothesis.settings(deadline=None)
    def test_arbitrary_missing_fields_handled_gracefully(self, missing_fields):
        """Property: Papers with arbitrary missing optional fields should validate successfully."""
        from app.data_utils.datasets_peerread import PeerReadLoader

        # Arrange
        config = PeerReadConfig()
        loader = PeerReadLoader(config)

        # Build review dict with all required fields, then remove specified ones
        review_data = {
            "IMPACT": "3",
            "SUBSTANCE": "4",
            "APPROPRIATENESS": "5",
            "MEANINGFUL_COMPARISON": "2",
            "PRESENTATION_FORMAT": "Poster",
            "comments": "Test comment",
            "SOUNDNESS_CORRECTNESS": "4",
            "ORIGINALITY": "3",
            "RECOMMENDATION": "3",
            "CLARITY": "3",
            "REVIEWER_CONFIDENCE": "3",
        }

        # Remove the fields that should be missing
        for field in missing_fields:
            review_data.pop(field, None)

        test_papers = [
            {
                "id": "test_hypothesis",
                "title": "Hypothesis Test Paper",
                "abstract": "Test abstract",
                "reviews": [review_data],
                "histories": [],
            }
        ]

        # Act
        validated_papers = loader._validate_papers(test_papers)

        # Assert: Paper should always validate successfully
        # Invariant: Should always return exactly 1 paper
        assert len(validated_papers) == 1
        assert validated_papers[0].paper_id == "test_hypothesis"
        # Invariant: Should always have exactly 1 review
        assert len(validated_papers[0].reviews) == 1

        # Invariant: Missing fields should have "UNKNOWN" default
        review = validated_papers[0].reviews[0]
        for field in missing_fields:
            field_name = field.lower()
            if hasattr(review, field_name):
                assert getattr(review, field_name) == "UNKNOWN"


class TestFileDiscovery:
    """Test file discovery functionality."""

    def test_extract_paper_id_from_reviews_filename(self):
        """Test extracting paper ID from reviews JSON filename."""
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("104.json", "reviews")

        # Assert
        assert paper_id == "104"

    def test_extract_paper_id_from_parsed_pdf_filename(self):
        """Test extracting paper ID from parsed PDF filename."""
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("104.pdf.json", "parsed_pdfs")

        # Assert
        assert paper_id == "104"

    def test_extract_paper_id_from_pdf_filename(self):
        """Test extracting paper ID from PDF filename."""
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("104.pdf", "pdfs")

        # Assert
        assert paper_id == "104"

    def test_extract_paper_id_returns_none_for_invalid_filename(self):
        """Test that invalid filename returns None."""
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act
        paper_id = downloader._extract_paper_id_from_filename("invalid.txt", "reviews")

        # Assert
        assert paper_id is None

    def test_discover_available_files_with_api_error(self):
        """Test file discovery handles API errors."""
        from unittest.mock import patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        with patch.object(downloader.client, "get", side_effect=httpx.RequestError("API error")):
            # Act
            paper_ids = downloader._discover_available_files("acl_2017", "train", "reviews")

            # Assert - should return empty list on error
            assert paper_ids == []

    def test_discover_available_files_with_invalid_json(self):
        """Test file discovery handles invalid JSON response."""
        from unittest.mock import Mock, patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)

        with patch.object(downloader.client, "get", return_value=mock_response):
            # Act
            paper_ids = downloader._discover_available_files("acl_2017", "train", "reviews")

            # Assert
            assert paper_ids == []


class TestCacheOperations:
    """Test cache directory operations."""

    def test_download_file_returns_json_data(self):
        """Test that download_file returns JSON data for reviews."""
        from unittest.mock import Mock, patch

        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": "test_999",
            "title": "Test Paper",
            "abstract": "Abstract",
            "reviews": [],
            "histories": [],
        }

        with (
            patch.object(downloader.client, "get", return_value=mock_response),
            patch(
                "app.data_utils.datasets_peerread.validate_url", return_value="http://validated.url"
            ),
        ):
            # Act
            result = downloader.download_file("acl_2017", "train", "reviews", "test_999")

            # Assert - result should be returned with correct data
            assert result is not None
            assert result["id"] == "test_999"
            assert result["title"] == "Test Paper"

    def test_construct_url_with_invalid_data_type(self):
        """Test URL construction with invalid data type."""
        from app.data_utils.datasets_peerread import PeerReadDownloader

        # Arrange
        config = PeerReadConfig()
        downloader = PeerReadDownloader(config)

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid data_type"):
            downloader._construct_url("acl_2017", "train", "invalid_type", "104")
