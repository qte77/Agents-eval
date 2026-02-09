#!/usr/bin/env python3
"""
Real PeerRead dataset validation tests.

This module contains integration tests that validate actual PeerRead dataset
download, caching, and format compatibility. Tests real data download using
the existing datasets_peerread.py infrastructure and verifies data integrity.
"""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.peerread_models import PeerReadConfig, PeerReadPaper
from app.data_utils.datasets_peerread import (
    PeerReadDownloader,
    PeerReadLoader,
    load_peerread_config,
)


class TestPeerReadRealDatasetValidation:
    """Integration tests for real PeerRead dataset validation."""

    @pytest.fixture
    def peerread_config(self):
        """Fixture providing PeerRead configuration."""
        return load_peerread_config()

    @pytest.fixture
    def temp_cache_dir(self):
        """Fixture providing temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def test_downloader(self, peerread_config, temp_cache_dir):
        """Fixture providing PeerRead downloader with temporary cache."""
        # Reason: Create modified config with temporary cache directory for testing
        test_config = PeerReadConfig(
            venues=peerread_config.venues[:1],  # Use only first venue for testing
            splits=peerread_config.splits[:1],  # Use only first split for testing
            cache_directory=str(temp_cache_dir),
            max_papers_per_query=3,  # Limit to 3 papers for testing
            raw_github_base_url=peerread_config.raw_github_base_url,
            github_api_base_url=peerread_config.github_api_base_url,
            download_timeout=peerread_config.download_timeout,
            max_retries=peerread_config.max_retries,
            retry_delay_seconds=peerread_config.retry_delay_seconds,
        )
        return PeerReadDownloader(test_config)

    @pytest.mark.integration
    @pytest.mark.network
    async def test_real_peerread_download(self, test_downloader):
        """Test actual PeerRead dataset download and validation."""
        # Get configuration from downloader
        config = test_downloader.config
        venue = config.venues[0]
        split = config.splits[0]

        # Record start time for performance measurement
        start_time = time.time()

        # Execute download
        result = test_downloader.download_venue_split(venue, split, max_papers=3)

        # Calculate download time
        download_time = time.time() - start_time

        # Validate download success
        assert result.success, f"Download failed: {result.error_message}"
        assert result.papers_downloaded > 0, "No papers were downloaded"
        assert result.papers_downloaded <= 3, "Downloaded more papers than expected"

        # Validate performance - should complete within reasonable time
        assert download_time < 30.0, f"Download took too long: {download_time:.2f}s"

        # Validate cache directory structure
        cache_path = Path(result.cache_path)
        assert cache_path.exists(), "Cache directory was not created"

        # Check that required data type directories exist
        data_types = ["reviews", "parsed_pdfs", "pdfs"]
        for data_type in data_types:
            data_type_path = cache_path / data_type
            assert data_type_path.exists(), f"Missing {data_type} directory"

        # Validate that files were actually downloaded
        reviews_path = cache_path / "reviews"
        json_files = list(reviews_path.glob("*.json"))
        assert len(json_files) > 0, "No review JSON files found"
        assert len(json_files) <= 3, "More review files than expected"

        # Validate JSON file structure
        for json_file in json_files[:1]:  # Check first file only for performance
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            # Validate required PeerRead fields
            assert "id" in data, f"Missing 'id' field in {json_file}"
            assert "title" in data, f"Missing 'title' field in {json_file}"
            assert "abstract" in data, f"Missing 'abstract' field in {json_file}"
            assert "reviews" in data, f"Missing 'reviews' field in {json_file}"
            assert isinstance(data["reviews"], list), "Reviews should be a list"

            # Validate review structure
            if data["reviews"]:
                review = data["reviews"][0]
                required_review_fields = [
                    "IMPACT",
                    "SUBSTANCE",
                    "APPROPRIATENESS",
                    "MEANINGFUL_COMPARISON",
                    "PRESENTATION_FORMAT",
                    "comments",
                    "SOUNDNESS_CORRECTNESS",
                    "ORIGINALITY",
                    "RECOMMENDATION",
                    "CLARITY",
                    "REVIEWER_CONFIDENCE",
                ]

                for field in required_review_fields:
                    assert field in review, f"Missing review field '{field}' in {json_file}"

    @pytest.mark.integration
    @pytest.mark.network
    async def test_peerread_cache_functionality(self, test_downloader):
        """Test caching and incremental download behavior."""
        config = test_downloader.config
        venue = config.venues[0]
        split = config.splits[0]

        # First download
        start_time = time.time()
        result1 = test_downloader.download_venue_split(venue, split, max_papers=2)
        first_download_time = time.time() - start_time

        assert result1.success, f"First download failed: {result1.error_message}"
        assert result1.papers_downloaded > 0, "First download got no papers"

        # Second download (should use cache)
        start_time = time.time()
        result2 = test_downloader.download_venue_split(venue, split, max_papers=2)
        second_download_time = time.time() - start_time

        assert result2.success, f"Second download failed: {result2.error_message}"

        # Reason: Cache hit should be much faster than initial download
        # Allow some tolerance for network variability
        if first_download_time > 1.0:  # Only check if first download took reasonable time
            assert second_download_time < first_download_time * 0.5, (
                f"Cache not working effectively: first={first_download_time:.2f}s, second={second_download_time:.2f}s"
            )

        # Validate that same files exist
        cache_path = Path(result2.cache_path)
        reviews_path = cache_path / "reviews"
        json_files = list(reviews_path.glob("*.json"))
        assert len(json_files) > 0, "Cache files missing after second download"

    @pytest.mark.integration
    @pytest.mark.network
    async def test_peerread_error_handling(self, peerread_config, temp_cache_dir):
        """Test error handling for network issues and invalid configurations."""
        # Test with invalid venue
        invalid_config = PeerReadConfig(
            venues=["invalid_venue_2099"],
            splits=["train"],
            cache_directory=str(temp_cache_dir),
            max_papers_per_query=1,
            raw_github_base_url=peerread_config.raw_github_base_url,
            github_api_base_url=peerread_config.github_api_base_url,
            download_timeout=5.0,  # Short timeout for testing
            max_retries=1,  # Single retry for testing
            retry_delay_seconds=1.0,
        )

        downloader = PeerReadDownloader(invalid_config)
        result = downloader.download_venue_split("invalid_venue_2099", "train")

        # Should fail gracefully
        assert not result.success, "Download should fail for invalid venue"
        assert result.error_message is not None, "Should provide error message"
        assert result.papers_downloaded == 0, "Should not download any papers"

    @pytest.mark.integration
    async def test_real_data_loader_integration(self, test_downloader):
        """Test integration between downloader and loader with real data."""
        config = test_downloader.config
        venue = config.venues[0]
        split = config.splits[0]

        # Download data first
        download_result = test_downloader.download_venue_split(venue, split, max_papers=2)
        assert download_result.success, f"Download failed: {download_result.error_message}"

        # Create loader with same configuration
        loader = PeerReadLoader(config)

        # Load papers using the loader
        papers = loader.load_papers(venue, split)

        # Validate loaded papers
        assert len(papers) > 0, "No papers were loaded"
        assert len(papers) <= 2, "More papers loaded than downloaded"

        # Validate paper structure
        for paper in papers[:1]:  # Check first paper only
            assert isinstance(paper, PeerReadPaper), "Paper should be PeerReadPaper instance"
            assert paper.paper_id is not None, "Paper should have ID"
            assert len(paper.title) > 0, "Paper should have title"
            assert len(paper.abstract) > 0, "Paper should have abstract"
            assert len(paper.reviews) > 0, "Paper should have reviews"

            # Validate review structure
            for review in paper.reviews[:1]:  # Check first review only
                assert review.impact is not None, "Review should have impact score"
                assert review.recommendation is not None, "Review should have recommendation"
                assert len(review.comments) > 0, "Review should have comments"

    @pytest.mark.integration
    async def test_download_performance_targets(self, test_downloader):
        """Test that download performance meets targets."""
        config = test_downloader.config
        venue = config.venues[0]
        split = config.splits[0]

        # Record performance metrics
        start_time = time.time()
        result = test_downloader.download_venue_split(venue, split, max_papers=1)
        total_time = time.time() - start_time

        # Validate success
        assert result.success, f"Download failed: {result.error_message}"

        # Validate performance targets from specification
        assert total_time < 30.0, f"Download exceeded 30s target: {total_time:.2f}s"

        # Memory usage should be reasonable (test doesn't exceed limits during execution)
        # This is implicitly tested by the test not failing with memory errors

    @pytest.mark.integration
    @pytest.mark.network
    async def test_file_discovery_mechanism(self, test_downloader):
        """Test file discovery via GitHub API."""
        config = test_downloader.config
        venue = config.venues[0]
        split = config.splits[0]

        # Test file discovery
        available_papers = test_downloader._discover_available_files(venue, split, "reviews")

        # Validate discovery results
        assert isinstance(available_papers, list), "Should return list of paper IDs"
        if available_papers:  # Only test if files are discovered
            assert len(available_papers) > 0, "Should discover some papers"
            assert all(isinstance(paper_id, str) for paper_id in available_papers), (
                "All paper IDs should be strings"
            )
            assert all(len(paper_id) > 0 for paper_id in available_papers), (
                "All paper IDs should be non-empty"
            )


if __name__ == "__main__":
    """Run the real dataset validation tests directly."""

    async def run_real_dataset_validation():
        print("Running PeerRead real dataset validation tests...")

        try:
            # Load configuration
            config = load_peerread_config()
            print(
                f"✓ Configuration loaded: {len(config.venues)} venues, {len(config.splits)} splits"
            )

            # Create test downloader with limited scope
            with tempfile.TemporaryDirectory() as temp_dir:
                test_config = PeerReadConfig(
                    venues=config.venues[:1],
                    splits=config.splits[:1],
                    cache_directory=temp_dir,
                    max_papers_per_query=1,
                    raw_github_base_url=config.raw_github_base_url,
                    github_api_base_url=config.github_api_base_url,
                    download_timeout=config.download_timeout,
                    max_retries=config.max_retries,
                    retry_delay_seconds=config.retry_delay_seconds,
                )

                downloader = PeerReadDownloader(test_config)
                venue = test_config.venues[0]
                split = test_config.splits[0]

                # Test download
                print(f"Testing download for {venue}/{split}...")
                start_time = time.time()
                result = downloader.download_venue_split(venue, split, max_papers=1)
                download_time = time.time() - start_time

                if result.success:
                    print(
                        f"✓ Download successful: {result.papers_downloaded} papers in {download_time:.2f}s"
                    )

                    # Test loader integration
                    loader = PeerReadLoader(test_config)
                    papers = loader.load_papers(venue, split)
                    print(f"✓ Loader integration: {len(papers)} papers loaded")

                    if papers:
                        paper = papers[0]
                        print(
                            f"✓ Sample paper: {paper.title[:50]}... ({len(paper.reviews)} reviews)"
                        )

                else:
                    print(f"✗ Download failed: {result.error_message}")

        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

        print("✅ Real dataset validation completed!")

    asyncio.run(run_real_dataset_validation())
