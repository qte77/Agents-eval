#!/usr/bin/env python3
"""
Real PeerRead data format compatibility tests.

This module validates that the evaluation pipeline can properly handle real
PeerRead data structures, including edge cases and missing fields that may
exist in actual dataset files. Tests Pydantic model compliance and pipeline
integration with real data.
"""

import asyncio
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.peerread_models import (
    PeerReadConfig,
    PeerReadPaper,
    PeerReadReview,
)
from app.data_utils.datasets_peerread import PeerReadDownloader, PeerReadLoader
from app.evals.evaluation_pipeline import EvaluationPipeline


class TestPeerReadFormatCompatibility:
    """Integration tests for real PeerRead data format compatibility."""

    @pytest.fixture
    async def real_peerread_data(self):
        """Fixture providing real PeerRead data for testing."""
        from app.data_utils.datasets_peerread import load_peerread_config

        # Load configuration and create temporary cache
        config = load_peerread_config()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test configuration with limited scope
            test_config = PeerReadConfig(
                venues=config.venues[:1],  # Use first venue only
                splits=config.splits[:1],  # Use first split only
                cache_directory=temp_dir,
                max_papers_per_query=2,  # Download only 2 papers for testing
                raw_github_base_url=config.raw_github_base_url,
                github_api_base_url=config.github_api_base_url,
                download_timeout=config.download_timeout,
                max_retries=config.max_retries,
                retry_delay_seconds=config.retry_delay_seconds,
            )

            # Download small sample of real data
            downloader = PeerReadDownloader(test_config)
            venue = test_config.venues[0]
            split = test_config.splits[0]

            result = downloader.download_venue_split(venue, split, max_papers=2)
            if result.success and result.papers_downloaded > 0:
                # Load papers using loader
                loader = PeerReadLoader(test_config)
                papers = loader.load_papers(venue, split)
                yield papers
            else:
                # Fallback to empty list if download fails
                yield []

    @pytest.fixture
    def evaluation_pipeline(self):
        """Fixture providing initialized evaluation pipeline."""
        return EvaluationPipeline()

    @pytest.mark.integration
    @pytest.mark.network
    async def test_real_data_pydantic_validation(self, real_peerread_data):
        """Test Pydantic model validation with real PeerRead data."""
        papers = real_peerread_data

        # Skip test if no real data available
        pytest.assume(len(papers) > 0, "No real PeerRead data available for testing")

        # Validate each paper
        for i, paper in enumerate(papers):
            # Test that paper is valid PeerReadPaper instance
            assert isinstance(paper, PeerReadPaper), f"Paper {i} is not PeerReadPaper instance"

            # Validate required fields
            assert paper.paper_id is not None, f"Paper {i} missing paper_id"
            assert paper.paper_id != "", f"Paper {i} has empty paper_id"
            assert paper.title is not None, f"Paper {i} missing title"
            assert len(paper.title.strip()) > 0, f"Paper {i} has empty title"
            assert paper.abstract is not None, f"Paper {i} missing abstract"
            assert len(paper.abstract.strip()) > 0, f"Paper {i} has empty abstract"

            # Validate reviews structure
            assert isinstance(paper.reviews, list), f"Paper {i} reviews not a list"
            assert len(paper.reviews) > 0, f"Paper {i} has no reviews"

            # Validate each review
            for j, review in enumerate(paper.reviews):
                assert isinstance(review, PeerReadReview), (
                    f"Paper {i}, Review {j} is not PeerReadReview instance"
                )

                # Validate review fields
                assert review.impact is not None, f"Paper {i}, Review {j} missing impact"
                assert review.recommendation is not None, (
                    f"Paper {i}, Review {j} missing recommendation"
                )
                assert review.comments is not None, f"Paper {i}, Review {j} missing comments"
                assert len(review.comments.strip()) > 0, f"Paper {i}, Review {j} has empty comments"

                # Validate score ranges (PeerRead uses 1-5 scale)
                impact_val = int(review.impact)
                assert 1 <= impact_val <= 5, (
                    f"Paper {i}, Review {j} impact out of range: {impact_val}"
                )

                rec_val = int(review.recommendation)
                assert 1 <= rec_val <= 5, (
                    f"Paper {i}, Review {j} recommendation out of range: {rec_val}"
                )

    @pytest.mark.integration
    async def test_evaluation_pipeline_real_data_integration(
        self, real_peerread_data, evaluation_pipeline
    ):
        """Test evaluation pipeline with real PeerRead data."""
        papers = real_peerread_data

        # Skip test if no real data available
        pytest.assume(len(papers) > 0, "No real PeerRead data available for testing")

        # Test with first available paper
        paper = papers[0]

        # Extract reference reviews for comparison
        reference_reviews = [review.comments for review in paper.reviews]

        # Create synthetic agent review for testing
        agent_review = f"""This paper titled "{paper.title}" presents an interesting approach.

        The abstract suggests a solid methodology with comprehensive evaluation.
        The work addresses important questions in the field and demonstrates
        technical competence. The approach appears sound and the experimental
        design seems appropriate.

        Strengths include clear problem formulation and systematic evaluation.
        Areas for improvement might include more detailed analysis of limitations
        and expanded discussion of related work.

        Overall, this appears to be a valuable contribution to the field."""

        # Create synthetic execution trace
        execution_trace = {
            "execution_id": f"real_data_test_{paper.paper_id}",
            "agent_interactions": [
                {
                    "from": "Manager",
                    "to": "Researcher",
                    "type": "paper_analysis_request",
                    "timestamp": 1.0,
                    "paper_id": paper.paper_id,
                },
                {
                    "from": "Researcher",
                    "to": "Synthesizer",
                    "type": "analysis_results",
                    "timestamp": 2.5,
                    "analysis_complete": True,
                },
            ],
            "tool_calls": [
                {
                    "agent_id": "Researcher",
                    "tool_name": "peerread_loader",
                    "success": True,
                    "duration": 0.3,
                    "timestamp": 1.2,
                    "context": f"Loading paper {paper.paper_id}",
                },
            ],
        }

        # Record start time for performance measurement
        start_time = time.time()

        # Execute evaluation with real data
        result = await evaluation_pipeline.evaluate_comprehensive(
            paper=paper.abstract,
            review=agent_review,
            execution_trace=execution_trace,
            reference_reviews=reference_reviews,
        )

        # Calculate execution time
        execution_time = time.time() - start_time

        # Validate results structure
        assert result is not None, "Evaluation should return result"
        assert hasattr(result, "composite_score"), "Result should have composite_score"
        assert hasattr(result, "recommendation"), "Result should have recommendation"
        assert hasattr(result, "evaluation_complete"), "Result should have evaluation_complete"

        # Validate result values
        assert result.composite_score >= 0.0, "Composite score should be non-negative"
        assert result.composite_score <= 1.0, "Composite score should not exceed 1.0"
        assert result.recommendation in [
            "accept",
            "weak_accept",
            "weak_reject",
            "reject",
        ], f"Invalid recommendation: {result.recommendation}"
        assert result.evaluation_complete is True, "Evaluation should be marked complete"

        # Validate performance targets (from specification: 25 seconds total)
        assert execution_time < 25.0, f"Execution exceeded 25s target: {execution_time:.2f}s"

        # Log successful evaluation details
        print(f"✓ Evaluated paper '{paper.title[:30]}...' in {execution_time:.2f}s")
        print(f"  Composite Score: {result.composite_score:.3f}")
        print(f"  Recommendation: {result.recommendation}")
        print(f"  Reference Reviews: {len(reference_reviews)}")

    @pytest.mark.integration
    async def test_real_data_edge_cases(self, real_peerread_data):
        """Test handling of edge cases in real PeerRead data."""
        papers = real_peerread_data

        # Skip test if no real data available
        pytest.assume(len(papers) > 0, "No real PeerRead data available for testing")

        for i, paper in enumerate(papers):
            # Test handling of optional fields
            assert hasattr(paper, "review_histories"), (
                f"Paper {i} missing review_histories attribute"
            )

            # review_histories can be empty list or None
            if paper.review_histories is not None:
                assert isinstance(paper.review_histories, list), (
                    f"Paper {i} review_histories should be list"
                )

            # Test review field variations
            for j, review in enumerate(paper.reviews):
                # Test is_meta_review field (can be None, True, or False)
                if hasattr(review, "is_meta_review"):
                    assert review.is_meta_review in [None, True, False], (
                        f"Paper {i}, Review {j} invalid is_meta_review value"
                    )

                # Test presentation_format variations
                if hasattr(review, "presentation_format"):
                    # Should be string or None
                    assert isinstance(review.presentation_format, (str, type(None))), (
                        f"Paper {i}, Review {j} invalid presentation_format type"
                    )

    @pytest.mark.integration
    async def test_real_data_content_analysis(self, real_peerread_data):
        """Test content analysis with real scientific paper abstracts and reviews."""
        papers = real_peerread_data

        # Skip test if no real data available
        pytest.assume(len(papers) > 0, "No real PeerRead data available for testing")

        for i, paper in enumerate(papers[:1]):  # Test first paper only for performance
            # Validate abstract characteristics
            abstract_words = len(paper.abstract.split())
            assert abstract_words > 50, f"Paper {i} abstract too short: {abstract_words} words"
            assert abstract_words < 2000, f"Paper {i} abstract too long: {abstract_words} words"

            # Validate title characteristics
            title_words = len(paper.title.split())
            assert title_words > 3, f"Paper {i} title too short: {title_words} words"
            assert title_words < 50, f"Paper {i} title too long: {title_words} words"

            # Validate review characteristics
            for j, review in enumerate(paper.reviews[:2]):  # Check first 2 reviews
                comment_words = len(review.comments.split())
                assert comment_words > 10, (
                    f"Paper {i}, Review {j} comments too short: {comment_words} words"
                )
                # No upper limit as some reviews can be very detailed

    @pytest.mark.integration
    async def test_real_data_serialization(self, real_peerread_data):
        """Test serialization/deserialization of real PeerRead data."""
        papers = real_peerread_data

        # Skip test if no real data available
        pytest.assume(len(papers) > 0, "No real PeerRead data available for testing")

        # Test serialization of first paper
        paper = papers[0]

        # Test JSON serialization
        paper_dict = paper.model_dump()
        assert isinstance(paper_dict, dict), "Serialization should produce dictionary"
        assert "paper_id" in paper_dict, "Serialized data should contain paper_id"
        assert "reviews" in paper_dict, "Serialized data should contain reviews"

        # Test deserialization
        reconstructed_paper = PeerReadPaper.model_validate(paper_dict)
        assert reconstructed_paper.paper_id == paper.paper_id, "Paper ID should match"
        assert reconstructed_paper.title == paper.title, "Title should match"
        assert len(reconstructed_paper.reviews) == len(paper.reviews), "Review count should match"

    @pytest.mark.integration
    async def test_real_data_performance_characteristics(self, real_peerread_data):
        """Test performance characteristics with real data of varying sizes."""
        papers = real_peerread_data

        # Skip test if no real data available
        pytest.assume(len(papers) > 0, "No real PeerRead data available for testing")

        performance_data: list[dict[str, Any]] = []

        # Test processing time for different paper sizes
        for i, paper in enumerate(papers):
            start_time = time.time()

            # Simulate processing operations
            abstract_length = len(paper.abstract)
            review_count = len(paper.reviews)
            total_review_length = sum(len(review.comments) for review in paper.reviews)

            # Validate model operations
            paper_dict = paper.model_dump()
            PeerReadPaper.model_validate(paper_dict)

            processing_time = time.time() - start_time

            performance_data.append(
                {
                    "paper_index": i,
                    "abstract_length": abstract_length,
                    "review_count": review_count,
                    "total_review_length": total_review_length,
                    "processing_time": processing_time,
                }
            )

            # Individual paper processing should be fast
            assert processing_time < 1.0, f"Paper {i} processing too slow: {processing_time:.3f}s"

        # Validate overall performance characteristics
        avg_processing_time = sum(p["processing_time"] for p in performance_data) / len(
            performance_data
        )
        assert avg_processing_time < 0.1, (
            f"Average processing time too high: {avg_processing_time:.3f}s"
        )


if __name__ == "__main__":
    """Run the format compatibility tests directly."""

    async def run_format_compatibility():
        print("Running PeerRead format compatibility tests...")

        try:
            from app.data_utils.datasets_peerread import load_peerread_config

            # Load configuration
            config = load_peerread_config()
            print(f"✓ Configuration loaded: {len(config.venues)} venues")

            # Create temporary test setup
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

                # Test download and validation
                downloader = PeerReadDownloader(test_config)
                result = downloader.download_venue_split(
                    test_config.venues[0], test_config.splits[0], max_papers=1
                )

                if result.success:
                    print(f"✓ Sample download successful: {result.papers_downloaded} papers")

                    # Test format validation
                    loader = PeerReadLoader(test_config)
                    papers = loader.load_papers(test_config.venues[0], test_config.splits[0])
                    print(f"✓ Format validation: {len(papers)} papers loaded")

                    if papers:
                        paper = papers[0]
                        print(f"✓ Paper structure valid: '{paper.title[:40]}...'")
                        print(f"  Abstract: {len(paper.abstract)} chars")
                        print(f"  Reviews: {len(paper.reviews)} reviews")

                        # Test serialization
                        paper_dict = paper.model_dump()
                        PeerReadPaper.model_validate(paper_dict)
                        print("✓ Serialization test passed")

                        # Test evaluation pipeline integration
                        pipeline = EvaluationPipeline()
                        reference_reviews = [review.comments for review in paper.reviews]

                        sample_review = "This paper presents a solid technical contribution with appropriate methodology and clear results."

                        start_time = time.time()
                        result = await pipeline.evaluate_comprehensive(
                            paper=paper.abstract,
                            review=sample_review,
                            execution_trace={"execution_id": "test"},
                            reference_reviews=reference_reviews,
                        )
                        eval_time = time.time() - start_time

                        print(
                            f"✓ Pipeline integration: {eval_time:.2f}s, score={result.composite_score:.3f}"
                        )
                else:
                    print(f"✗ Download failed: {result.error_message}")
                    print("Note: This may be expected if network access is limited")

        except Exception as e:
            print(f"✗ Test failed: {e}")
            raise

        print("✅ Format compatibility testing completed!")

    asyncio.run(run_format_compatibility())
