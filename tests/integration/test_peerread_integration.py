#!/usr/bin/env python3
"""
Integration test for PeerRead dataset format compatibility with evaluation pipeline.

This test validates that the evaluation pipeline can properly handle PeerRead
data structures and produce meaningful results with scientific paper content.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.peerread_models import PeerReadPaper, PeerReadReview
from app.evals.evaluation_pipeline import EvaluationPipeline


class PeerReadTestData:
    """Generator for synthetic PeerRead data matching real dataset structure."""

    @staticmethod
    def create_synthetic_peerread_data() -> PeerReadPaper:
        """Create synthetic PeerRead data matching the real structure."""

        # Create sample reviews matching PeerRead format
        reviews = [
            PeerReadReview(
                impact="4",
                substance="4",
                appropriateness="4",
                meaningful_comparison="3",
                presentation_format="Poster",
                comments="""This paper presents a solid approach to transformer-based
                language modeling for scientific text. The methodology is sound and
                the experimental validation is comprehensive. The results demonstrate
                significant improvements over baseline methods. Minor issues with
                presentation clarity that should be addressed. I recommend acceptance
                with minor revisions.""",
                soundness_correctness="4",
                originality="3",
                recommendation="4",
                clarity="3",
                reviewer_confidence="4",
                is_meta_review=False,
            ),
            PeerReadReview(
                impact="3",
                substance="4",
                appropriateness="4",
                meaningful_comparison="4",
                presentation_format="Oral",
                comments="""The technical contribution is valuable and the experimental
                design is appropriate. The paper addresses an important problem in
                scientific text generation. Some concerns about generalizability of
                the approach across different scientific domains. The writing quality
                is good but could benefit from clearer explanations in the methodology
                section. Overall a solid paper that merits publication.""",
                soundness_correctness="4",
                originality="4",
                recommendation="3",
                clarity="4",
                reviewer_confidence="3",
                is_meta_review=False,
            ),
        ]

        # Create sample paper matching PeerRead structure
        paper = PeerReadPaper(
            paper_id="test_paper_001",
            title="Transformer-Based Language Models for Scientific Text Generation: A Comprehensive Study",
            abstract="""Recent advances in transformer architectures have shown remarkable
            success in natural language processing tasks. This paper investigates their
            application to scientific text generation, focusing on automatic paper summarization
            and review generation. We present a novel fine-tuning approach that leverages
            domain-specific scientific corpora and evaluates performance across multiple
            scientific disciplines. Our experiments demonstrate significant improvements
            in coherence, factual accuracy, and domain-specific terminology usage compared
            to general-purpose language models. The results suggest that specialized training
            on scientific text can substantially enhance the quality of generated scientific
            content, with particular improvements in methodology description and result
            interpretation sections.""",
            reviews=reviews,
            review_histories=[
                "Initial submission",
                "Revised version addressing reviewer concerns",
            ],
        )

        return paper

    @staticmethod
    def create_agent_generated_review() -> str:
        """Create a sample agent-generated review for comparison."""

        return """This paper explores the application of transformer models to scientific
        text generation with a focus on domain adaptation. The proposed approach demonstrates
        technical soundness with comprehensive experimental validation across multiple scientific
        domains. The methodology is well-designed and the results show clear improvements over
        baseline approaches.

        Strengths include the thorough experimental design, appropriate baseline comparisons,
        and comprehensive evaluation metrics. The paper addresses an important problem in
        automated scientific text generation. The writing is generally clear and the technical
        content is accessible.

        Areas for improvement include more detailed analysis of failure cases and discussion
        of limitations. The generalizability claims could be better supported with additional
        experiments. Some sections would benefit from clearer explanations.

        Overall, this is a solid technical contribution that advances the field of scientific
        text generation. I recommend acceptance with minor revisions to address the presentation
        issues and expand the discussion of limitations."""

    @staticmethod
    def create_execution_trace() -> dict[str, Any]:
        """Create execution trace mimicking multi-agent workflow."""
        return {
            "execution_id": "peerread_integration_test",
            "agent_interactions": [
                {
                    "from": "Manager",
                    "to": "Researcher",
                    "type": "paper_analysis_request",
                    "timestamp": 1.0,
                    "paper_id": "test_paper_001",
                },
                {
                    "from": "Researcher",
                    "to": "Analyst",
                    "type": "research_data_transfer",
                    "timestamp": 2.3,
                    "data_size": 1247,
                },
                {
                    "from": "Analyst",
                    "to": "Synthesizer",
                    "type": "analysis_results",
                    "timestamp": 4.1,
                    "analysis_complete": True,
                },
            ],
            "tool_calls": [
                {
                    "agent_id": "Researcher",
                    "tool_name": "peerread_paper_loader",
                    "success": True,
                    "duration": 0.5,
                    "timestamp": 1.2,
                    "context": "Loading paper test_paper_001",
                },
                {
                    "agent_id": "Researcher",
                    "tool_name": "reference_comparison",
                    "success": True,
                    "duration": 1.1,
                    "timestamp": 2.0,
                    "context": "Comparing against existing reviews",
                },
                {
                    "agent_id": "Synthesizer",
                    "tool_name": "review_generation",
                    "success": True,
                    "duration": 2.3,
                    "timestamp": 4.5,
                    "context": "Generating comprehensive review",
                },
            ],
            "coordination_events": [
                {
                    "coordination_type": "task_delegation",
                    "manager_agent": "Manager",
                    "target_agents": ["Researcher", "Analyst"],
                    "timestamp": 1.0,
                    "task": "comprehensive_paper_review",
                }
            ],
        }


class TestPeerReadIntegration:
    """Integration tests for PeerRead dataset compatibility."""

    @pytest.fixture
    def peerread_data(self):
        """Fixture providing synthetic PeerRead data."""
        return PeerReadTestData()

    @pytest.fixture
    def evaluation_pipeline(self):
        """Fixture providing initialized evaluation pipeline."""
        return EvaluationPipeline()

    @pytest.mark.asyncio
    async def test_peerread_data_format_compatibility(self, peerread_data, evaluation_pipeline):
        """Test that pipeline can handle PeerRead data structures."""
        # Create test data
        peerread_paper = peerread_data.create_synthetic_peerread_data()
        agent_review = peerread_data.create_agent_generated_review()
        execution_trace = peerread_data.create_execution_trace()

        # Extract reference reviews for comparison
        reference_reviews = [review.comments for review in peerread_paper.reviews]

        # Execute evaluation
        result = await evaluation_pipeline.evaluate_comprehensive(
            paper=peerread_paper.abstract,
            review=agent_review,
            execution_trace=execution_trace,
            reference_reviews=reference_reviews,
        )

        # Validate results
        assert result is not None
        assert result.composite_score > 0.0
        assert result.recommendation in [
            "accept",
            "weak_accept",
            "weak_reject",
            "reject",
        ]
        assert result.evaluation_complete is True

        # Validate that PeerRead-specific data was processed correctly
        assert len(reference_reviews) == 2  # Both reviews were extracted
        assert peerread_paper.paper_id == "test_paper_001"

        # Performance validation
        stats = evaluation_pipeline.get_execution_stats()
        assert stats["total_time"] > 0
        assert stats["total_time"] < 25.0  # Within performance target

    @pytest.mark.asyncio
    async def test_peerread_model_validation(self, peerread_data):
        """Test PeerRead data model validation."""
        # Create PeerRead data
        paper = peerread_data.create_synthetic_peerread_data()

        # Validate paper structure
        assert paper.paper_id is not None
        assert len(paper.title) > 0
        assert len(paper.abstract) > 0
        assert len(paper.reviews) == 2

        # Validate review structure
        for review in paper.reviews:
            assert review.impact in ["1", "2", "3", "4", "5"]
            assert review.recommendation in ["1", "2", "3", "4", "5"]
            assert review.presentation_format in ["Poster", "Oral"]
            assert len(review.comments) > 0
            assert review.is_meta_review is False

    @pytest.mark.asyncio
    async def test_large_context_handling(self, peerread_data, evaluation_pipeline):
        """Test pipeline with larger scientific paper content."""
        # Create paper with extended content
        peerread_paper = peerread_data.create_synthetic_peerread_data()

        # Create longer abstract to test large context handling
        extended_abstract = (
            peerread_paper.abstract
            + """

        Further experimental validation across eight different scientific domains
        demonstrates the robustness and generalizability of the proposed approach.
        We evaluate on computational linguistics, machine learning, computer vision,
        natural language processing, robotics, bioinformatics, materials science,
        and climate modeling domains. Results show consistent improvements with
        domain-adapted models achieving 15-25% better coherence scores and 20-30%
        improvement in domain-specific terminology accuracy compared to general
        models. The approach scales effectively to papers with 8,000+ words and
        maintains performance quality even with complex technical jargon and
        mathematical notation prevalent in scientific literature.
        """
        )

        agent_review = peerread_data.create_agent_generated_review()
        execution_trace = peerread_data.create_execution_trace()
        reference_reviews = [review.comments for review in peerread_paper.reviews]

        # Test with extended content
        result = await evaluation_pipeline.evaluate_comprehensive(
            paper=extended_abstract,
            review=agent_review,
            execution_trace=execution_trace,
            reference_reviews=reference_reviews,
        )

        # Should handle large context successfully
        assert result is not None
        assert result.composite_score > 0.0

        # Performance should still be reasonable
        stats = evaluation_pipeline.get_execution_stats()
        assert stats["total_time"] < 25.0

    def test_peerread_data_serialization(self, peerread_data):
        """Test that PeerRead data can be serialized/deserialized."""
        paper = peerread_data.create_synthetic_peerread_data()

        # Test JSON serialization
        paper_dict = paper.model_dump()
        assert isinstance(paper_dict, dict)
        assert paper_dict["paper_id"] == "test_paper_001"
        assert len(paper_dict["reviews"]) == 2

        # Test deserialization
        reconstructed_paper = PeerReadPaper(**paper_dict)
        assert reconstructed_paper.paper_id == paper.paper_id
        assert reconstructed_paper.title == paper.title
        assert len(reconstructed_paper.reviews) == len(paper.reviews)


if __name__ == "__main__":
    """Run the PeerRead integration test directly."""

    async def run_peerread_integration():
        data = PeerReadTestData()
        pipeline = EvaluationPipeline()

        print("Running PeerRead integration test...")

        peerread_paper = data.create_synthetic_peerread_data()
        agent_review = data.create_agent_generated_review()
        execution_trace = data.create_execution_trace()
        reference_reviews = [review.comments for review in peerread_paper.reviews]

        result = await pipeline.evaluate_comprehensive(
            paper=peerread_paper.abstract,
            review=agent_review,
            execution_trace=execution_trace,
            reference_reviews=reference_reviews,
        )

        print("✅ PeerRead integration test completed!")
        print(f"   Paper: {peerread_paper.title[:50]}...")
        print(f"   Reviews: {len(peerread_paper.reviews)} reference reviews")
        print(f"   Composite Score: {result.composite_score:.3f}")
        print(f"   Recommendation: {result.recommendation}")

        stats = pipeline.get_execution_stats()
        print(f"   Performance: {stats['total_time']:.3f}s")

        return result

    asyncio.run(run_peerread_integration())
