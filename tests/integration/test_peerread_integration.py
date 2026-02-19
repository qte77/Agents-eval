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

import hypothesis
import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.peerread_models import PeerReadPaper, PeerReadReview
from app.judge.evaluation_pipeline import EvaluationPipeline


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
        """Fixture providing evaluation pipeline with Tier 2 enabled for integration testing."""
        p = EvaluationPipeline()
        # Reason: Integration tests mock engines and expect full 3-tier flow;
        # tier2_available must be True regardless of env API key availability.
        p.llm_engine.tier2_available = True
        return p

    @pytest.mark.asyncio
    @pytest.mark.network
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
    @pytest.mark.network
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


# STORY-004: Hypothesis property-based tests for integration test invariants
class TestPeerReadIntegrationInvariants:
    """Property-based tests for PeerRead integration test invariants."""

    @pytest.fixture
    def evaluation_pipeline(self):
        """Fixture providing initialized evaluation pipeline."""
        return EvaluationPipeline()

    @given(
        interaction_count=st.integers(min_value=3, max_value=50),
        tool_call_count=st.integers(min_value=1, max_value=20),
    )
    def test_execution_trace_structure_invariants(self, interaction_count, tool_call_count):
        """Property: Execution trace always has valid structure regardless of counts."""
        # Arrange
        interactions = [
            {
                "from": f"Agent_{i % 3}",
                "to": f"Agent_{(i + 1) % 3}",
                "type": "task_request",
                "timestamp": float(i),
            }
            for i in range(interaction_count)
        ]

        tool_calls = [
            {
                "agent_id": f"Agent_{i % 3}",
                "tool_name": f"tool_{i}",
                "success": True,
                "duration": 0.5,
                "timestamp": float(i),
                "context": f"Task {i}",
            }
            for i in range(tool_call_count)
        ]

        trace = {
            "execution_id": "test_trace",
            "agent_interactions": interactions,
            "tool_calls": tool_calls,
            "coordination_events": [],
        }

        # Assert invariants
        assert len(trace["agent_interactions"]) == interaction_count
        assert len(trace["tool_calls"]) == tool_call_count
        assert all(isinstance(i["timestamp"], float) for i in interactions)
        assert all(t["success"] is True for t in tool_calls)

    @pytest.mark.asyncio
    @pytest.mark.network
    @given(abstract_word_count=st.integers(min_value=50, max_value=500))
    @hypothesis.settings(
        suppress_health_check=[hypothesis.HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_paper_abstract_length_invariants(self, abstract_word_count, evaluation_pipeline):
        """Property: Pipeline handles variable abstract lengths consistently."""
        # Arrange
        words = ["word"] * abstract_word_count
        abstract = " ".join(words)

        review = "This is a test review with sufficient content for evaluation."
        trace = {
            "execution_id": "test",
            "agent_interactions": [],
            "tool_calls": [],
            "coordination_events": [],
        }

        # Act
        result = await evaluation_pipeline.evaluate_comprehensive(
            paper=abstract, review=review, execution_trace=trace, reference_reviews=[]
        )

        # Assert invariants
        assert result is not None
        assert 0.0 <= result.composite_score <= 1.0
        assert result.recommendation in ["accept", "weak_accept", "weak_reject", "reject"]


# STORY-004: Inline-snapshot regression tests for integration test outputs
class TestPeerReadIntegrationSnapshots:
    """Snapshot tests for PeerRead integration test output structures."""

    def test_synthetic_peerread_data_structure(self):
        """Snapshot: Synthetic PeerRead data structure."""
        # Arrange
        data_generator = PeerReadTestData()

        # Act
        paper = data_generator.create_synthetic_peerread_data()
        dumped = paper.model_dump()

        # Assert with snapshot
        assert dumped == snapshot(
            {
                "paper_id": "test_paper_001",
                "title": "Transformer-Based Language Models for Scientific Text Generation: A Comprehensive Study",
                "abstract": """\
Recent advances in transformer architectures have shown remarkable
            success in natural language processing tasks. This paper investigates their
            application to scientific text generation, focusing on automatic paper summarization
            and review generation. We present a novel fine-tuning approach that leverages
            domain-specific scientific corpora and evaluates performance across multiple
            scientific disciplines. Our experiments demonstrate significant improvements
            in coherence, factual accuracy, and domain-specific terminology usage compared
            to general-purpose language models. The results suggest that specialized training
            on scientific text can substantially enhance the quality of generated scientific
            content, with particular improvements in methodology description and result
            interpretation sections.\
""",
                "reviews": [
                    {
                        "impact": "4",
                        "substance": "4",
                        "appropriateness": "4",
                        "meaningful_comparison": "3",
                        "presentation_format": "Poster",
                        "comments": """\
This paper presents a solid approach to transformer-based
                language modeling for scientific text. The methodology is sound and
                the experimental validation is comprehensive. The results demonstrate
                significant improvements over baseline methods. Minor issues with
                presentation clarity that should be addressed. I recommend acceptance
                with minor revisions.\
""",
                        "soundness_correctness": "4",
                        "originality": "3",
                        "recommendation": "4",
                        "clarity": "3",
                        "reviewer_confidence": "4",
                        "is_meta_review": False,
                    },
                    {
                        "impact": "3",
                        "substance": "4",
                        "appropriateness": "4",
                        "meaningful_comparison": "4",
                        "presentation_format": "Oral",
                        "comments": """\
The technical contribution is valuable and the experimental
                design is appropriate. The paper addresses an important problem in
                scientific text generation. Some concerns about generalizability of
                the approach across different scientific domains. The writing quality
                is good but could benefit from clearer explanations in the methodology
                section. Overall a solid paper that merits publication.\
""",
                        "soundness_correctness": "4",
                        "originality": "4",
                        "recommendation": "3",
                        "clarity": "4",
                        "reviewer_confidence": "3",
                        "is_meta_review": False,
                    },
                ],
                "review_histories": [
                    "Initial submission",
                    "Revised version addressing reviewer concerns",
                ],
            }
        )

    def test_agent_review_structure(self):
        """Snapshot: Agent-generated review structure."""
        # Arrange
        data_generator = PeerReadTestData()

        # Act
        review = data_generator.create_agent_generated_review()

        # Assert with snapshot - verify review format remains consistent
        assert review == snapshot("""\
This paper explores the application of transformer models to scientific
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
        issues and expand the discussion of limitations.\
""")

    def test_execution_trace_structure(self):
        """Snapshot: Execution trace structure for PeerRead integration."""
        # Arrange
        data_generator = PeerReadTestData()

        # Act
        trace = data_generator.create_execution_trace()

        # Assert with snapshot
        assert trace == snapshot(
            {
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
        )
