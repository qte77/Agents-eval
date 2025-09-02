#!/usr/bin/env python3
"""
Integration test for the complete three-tier evaluation pipeline.

This test validates the end-to-end evaluation workflow using realistic
scientific paper content, demonstrating the integration of Traditional
metrics, LLM-as-Judge evaluation, and Graph analysis components.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.peerread_models import (
    GeneratedReview,
    PeerReadReview,
)
from app.evals.evaluation_pipeline import EvaluationPipeline
from app.evals.trace_processors import get_trace_collector


class RealisticTestData:
    """Generator for realistic scientific paper and review data."""

    @staticmethod
    def create_scientific_paper() -> dict[str, str]:
        """Create realistic AI/ML scientific paper content."""
        return {
            "paper_id": "test_paper_2024_001",
            "title": "Adaptive Multi-Agent Reinforcement Learning with Dynamic Task Allocation in Distributed Environments",
            "abstract": """
                This paper presents a novel framework for multi-agent reinforcement learning (MARL) that addresses
                the challenge of dynamic task allocation in distributed computing environments. Our approach,
                dubbed DynamicMARL, combines hierarchical task decomposition with adaptive coordination mechanisms
                to enable efficient resource utilization and improved system performance. We introduce a 
                decentralized learning algorithm that allows agents to autonomously discover optimal task
                assignments while maintaining global coordination objectives.

                The key contributions include: (1) A hierarchical task decomposition strategy that scales with
                system complexity, (2) An adaptive coordination protocol that balances autonomy with collaboration,
                (3) A novel reward shaping mechanism that promotes both individual and collective performance,
                and (4) Comprehensive evaluation on distributed computing benchmarks demonstrating significant
                improvements in throughput, latency, and resource utilization compared to existing methods.

                Experimental results across multiple distributed computing scenarios show that DynamicMARL
                achieves 23% better resource utilization, 31% reduction in task completion time, and improved
                scalability compared to state-of-the-art baselines. The approach maintains performance gains
                even under network partitions and agent failures, demonstrating robust operation in realistic
                distributed environments. Our findings suggest that adaptive coordination strategies are
                essential for effective multi-agent learning in dynamic distributed systems.
                """,
            "full_text": """
                ## 1. Introduction

                Multi-agent reinforcement learning has emerged as a powerful paradigm for addressing complex
                distributed computing challenges. Traditional approaches often rely on centralized coordination
                mechanisms that become bottlenecks as system scale increases. This paper introduces DynamicMARL,
                a novel framework that enables autonomous task allocation while maintaining system-wide performance
                objectives.

                ## 2. Related Work

                Previous work in MARL has focused primarily on static task assignments or centralized coordination.
                Notable approaches include hierarchical multi-agent systems (Smith et al., 2023), consensus-based
                coordination (Johnson & Lee, 2022), and market-based task allocation (Chen et al., 2021).
                However, these methods struggle with dynamic environments where task characteristics and system
                conditions change rapidly.

                ## 3. Methodology

                Our approach consists of three main components: (1) Hierarchical Task Decomposition, (2) Adaptive
                Coordination Protocol, and (3) Decentralized Learning Algorithm. The hierarchical decomposition
                enables efficient handling of complex tasks by breaking them into manageable subtasks that can
                be distributed across available agents.

                ## 4. Experimental Results

                We evaluate DynamicMARL on three distributed computing benchmarks: task scheduling, resource
                allocation, and load balancing. Results show consistent improvements across all metrics,
                with particularly strong performance in dynamic scenarios where traditional methods struggle.

                ## 5. Conclusion

                DynamicMARL represents a significant advance in multi-agent coordination for distributed systems.
                The combination of adaptive coordination and decentralized learning enables robust performance
                even under challenging conditions. Future work will explore applications to edge computing
                and IoT environments.
                """,
        }

    @staticmethod
    def create_reference_reviews() -> list[PeerReadReview]:
        """Create multiple reference reviews with varied perspectives."""
        reviews = [
            PeerReadReview(
                impact="4",
                substance="4",
                appropriateness="4",
                meaningful_comparison="4",
                presentation_format="Oral",
                comments="""This paper addresses an important problem in multi-agent reinforcement learning
                for distributed systems. The proposed DynamicMARL framework shows clear technical merit
                and comprehensive experimental validation. The hierarchical task decomposition is well-motivated
                and the adaptive coordination protocol is technically sound.

                Strengths:
                - Novel approach to dynamic task allocation in MARL
                - Comprehensive experimental evaluation with meaningful baselines
                - Clear presentation of methodology and results
                - Demonstrated scalability and robustness

                Weaknesses:
                - Limited theoretical analysis of convergence properties
                - Some implementation details could be clearer
                - Comparison with recent work could be expanded

                Overall, this is solid work that advances the field. I recommend acceptance with minor revisions
                to address the theoretical analysis and expand related work discussion.""",
                soundness_correctness="4",
                originality="4",
                recommendation="4",
                clarity="4",
                reviewer_confidence="4",
                is_meta_review=False,
            ),
            PeerReadReview(
                impact="3",
                substance="4",
                appropriateness="4",
                meaningful_comparison="3",
                presentation_format="Poster",
                comments="""The paper presents an interesting approach to multi-agent task allocation with
                some promising experimental results. The technical contribution is reasonable, though not
                groundbreaking. The experimental section is comprehensive and the results are convincing.

                The hierarchical decomposition strategy is the strongest contribution, showing clear benefits
                in the evaluated scenarios. However, the adaptive coordination protocol is somewhat incremental
                compared to existing consensus-based approaches.

                Some concerns:
                - The scalability analysis could be more thorough
                - Network partition handling needs better explanation
                - Some experimental details are unclear

                The paper is generally well-written and addresses a relevant problem. With revisions to address
                the scalability analysis and experimental details, this could be a solid contribution to the
                conference. I lean toward acceptance but with significant revisions required.""",
                soundness_correctness="4",
                originality="3",
                recommendation="3",
                clarity="4",
                reviewer_confidence="3",
                is_meta_review=False,
            ),
            PeerReadReview(
                impact="4",
                substance="5",
                appropriateness="5",
                meaningful_comparison="4",
                presentation_format="Oral",
                comments="""Excellent work on a challenging and important problem. This paper makes significant
                contributions to multi-agent reinforcement learning with clear practical applications. The
                experimental evaluation is particularly thorough and the results are impressive.

                Key strengths:
                - Novel and well-motivated approach
                - Outstanding experimental methodology
                - Significant performance improvements demonstrated
                - Robust evaluation including failure scenarios
                - Clear practical relevance

                Minor issues:
                - Some notation could be simplified
                - Related work section could be expanded slightly

                This is high-quality research that will be of significant interest to the community. The
                technical contributions are substantial and the experimental validation is exemplary. I
                strongly recommend acceptance. This work represents the kind of rigorous, impactful research
                we want to showcase at our venue.""",
                soundness_correctness="5",
                originality="4",
                recommendation="5",
                clarity="4",
                reviewer_confidence="5",
                is_meta_review=False,
            ),
        ]
        return reviews

    @staticmethod
    def create_agent_generated_review() -> GeneratedReview:
        """Create a realistic agent-generated review."""
        return GeneratedReview(
            impact=4,
            substance=4,
            appropriateness=5,
            meaningful_comparison=4,
            presentation_format="Oral",
            comments="""This paper presents DynamicMARL, a framework for multi-agent reinforcement learning 
            in distributed computing environments. The approach combines hierarchical task decomposition
            with adaptive coordination mechanisms to achieve improved resource utilization and system performance.

            Key contributions: The hierarchical task decomposition strategy effectively addresses scalability 
            challenges, while the adaptive coordination protocol provides a good balance between autonomy and 
            collaboration. The decentralized learning algorithm is properly designed and theoretically motivated.

            Strengths: The experimental evaluation is comprehensive and convincing. Testing across multiple 
            distributed computing scenarios demonstrates the generality of the approach. The 23% improvement
            in resource utilization and 31% reduction in task completion time represent significant practical gains.
            The robustness evaluation under network partitions and agent failures is particularly valuable.

            Weaknesses: Limited theoretical convergence analysis. Some implementation details could be clearer.
            Comparison with very recent work could be expanded. Scalability analysis could be more detailed.

            Technical soundness: The technical approach is sound and well-executed. The methodology is appropriate 
            and the results are convincing.

            Clarity: The paper is generally well-written and addresses a relevant problem. The presentation 
            could be improved in some technical sections but overall clarity is good.""",
            soundness_correctness=4,
            originality=4,
            recommendation=4,  # accept
            clarity=4,
            reviewer_confidence=4,
        )

    @staticmethod
    def create_comprehensive_execution_trace() -> dict[str, Any]:
        """Create detailed execution trace with realistic agent coordination."""
        return {
            "execution_id": "comprehensive_test_2024_001",
            "agent_interactions": [
                {
                    "from": "TaskManager",
                    "to": "ResearchAgent",
                    "type": "paper_analysis_request",
                    "timestamp": 1.0,
                    "data": {
                        "paper_id": "test_paper_2024_001",
                        "analysis_type": "comprehensive",
                        "priority": "high",
                    },
                },
                {
                    "from": "ResearchAgent",
                    "to": "DataAnalyst",
                    "type": "technical_analysis_request",
                    "timestamp": 2.3,
                    "data": {
                        "focus_areas": ["methodology", "experiments", "results"],
                        "depth": "detailed",
                    },
                },
                {
                    "from": "DataAnalyst",
                    "to": "ReviewerAgent",
                    "type": "analysis_results_delivery",
                    "timestamp": 4.7,
                    "data": {
                        "technical_score": 4.2,
                        "experimental_score": 4.5,
                        "novelty_score": 3.8,
                        "analysis_complete": True,
                    },
                },
                {
                    "from": "ReviewerAgent",
                    "to": "QualityAssessor",
                    "type": "draft_review_submission",
                    "timestamp": 6.1,
                    "data": {
                        "review_length": 1247,
                        "recommendation": "accept",
                        "confidence": 0.78,
                    },
                },
                {
                    "from": "QualityAssessor",
                    "to": "ReviewerAgent",
                    "type": "quality_feedback",
                    "timestamp": 7.2,
                    "data": {
                        "quality_score": 0.85,
                        "suggestions": [
                            "expand technical analysis",
                            "add more specific examples",
                        ],
                        "approved": True,
                    },
                },
                {
                    "from": "ReviewerAgent",
                    "to": "TaskManager",
                    "type": "final_review_delivery",
                    "timestamp": 8.5,
                    "data": {
                        "review_complete": True,
                        "final_recommendation": "accept",
                        "review_quality": 0.85,
                    },
                },
                {
                    "from": "TaskManager",
                    "to": "ArchiveAgent",
                    "type": "review_archival_request",
                    "timestamp": 9.0,
                    "data": {
                        "paper_id": "test_paper_2024_001",
                        "review_id": "comprehensive_test_2024_001",
                        "archive_type": "permanent",
                    },
                },
            ],
            "tool_calls": [
                {
                    "agent_id": "ResearchAgent",
                    "tool_name": "paper_parser",
                    "success": True,
                    "duration": 0.8,
                    "timestamp": 1.2,
                    "context": "Parsing paper structure and extracting key sections",
                },
                {
                    "agent_id": "ResearchAgent",
                    "tool_name": "reference_extractor",
                    "success": True,
                    "duration": 0.5,
                    "timestamp": 1.8,
                    "context": "Extracting and analyzing cited references",
                },
                {
                    "agent_id": "DataAnalyst",
                    "tool_name": "methodology_analyzer",
                    "success": True,
                    "duration": 1.2,
                    "timestamp": 2.8,
                    "context": "Deep analysis of proposed methodology",
                },
                {
                    "agent_id": "DataAnalyst",
                    "tool_name": "experiment_validator",
                    "success": True,
                    "duration": 1.8,
                    "timestamp": 3.5,
                    "context": "Validating experimental design and statistical analysis",
                },
                {
                    "agent_id": "DataAnalyst",
                    "tool_name": "results_calculator",
                    "success": True,
                    "duration": 0.7,
                    "timestamp": 4.2,
                    "context": "Verifying reported results and statistical significance",
                },
                {
                    "agent_id": "ReviewerAgent",
                    "tool_name": "review_template_generator",
                    "success": True,
                    "duration": 0.3,
                    "timestamp": 5.0,
                    "context": "Generating structured review template",
                },
                {
                    "agent_id": "ReviewerAgent",
                    "tool_name": "similarity_checker",
                    "success": True,
                    "duration": 0.9,
                    "timestamp": 5.8,
                    "context": "Checking for similarity with existing work",
                },
                {
                    "agent_id": "QualityAssessor",
                    "tool_name": "review_quality_evaluator",
                    "success": True,
                    "duration": 0.6,
                    "timestamp": 7.5,
                    "context": "Evaluating review completeness and quality",
                },
                {
                    "agent_id": "ArchiveAgent",
                    "tool_name": "document_archiver",
                    "success": True,
                    "duration": 0.4,
                    "timestamp": 9.2,
                    "context": "Archiving review and associated metadata",
                },
            ],
            "coordination_events": [
                {
                    "coordination_type": "task_delegation",
                    "manager_agent": "TaskManager",
                    "target_agents": ["ResearchAgent", "DataAnalyst"],
                    "timestamp": 1.0,
                    "data": {
                        "task_id": "comprehensive_review_2024_001",
                        "deadline": "2024-03-15T18:00:00Z",
                        "priority": "high",
                    },
                },
                {
                    "coordination_type": "synchronization_point",
                    "manager_agent": "TaskManager",
                    "target_agents": ["DataAnalyst", "ReviewerAgent"],
                    "timestamp": 4.5,
                    "data": {
                        "sync_type": "analysis_complete",
                        "required_agents": ["DataAnalyst"],
                        "waiting_agents": ["ReviewerAgent"],
                    },
                },
                {
                    "coordination_type": "quality_gate",
                    "manager_agent": "QualityAssessor",
                    "target_agents": ["ReviewerAgent"],
                    "timestamp": 7.0,
                    "data": {
                        "gate_type": "review_quality_check",
                        "threshold": 0.8,
                        "result": "passed",
                    },
                },
            ],
        }


class TestFullEvaluationPipeline:
    """Integration tests for the complete evaluation pipeline."""

    @pytest.fixture
    def realistic_test_data(self):
        """Fixture providing realistic test data."""
        return RealisticTestData()

    @pytest.fixture
    def evaluation_pipeline(self):
        """Fixture providing initialized evaluation pipeline."""
        return EvaluationPipeline()

    @pytest.mark.asyncio
    async def test_comprehensive_evaluation_workflow(
        self, realistic_test_data, evaluation_pipeline
    ):
        """Test complete evaluation workflow with realistic data."""
        # Create comprehensive test data
        paper_data = realistic_test_data.create_scientific_paper()
        reference_reviews = realistic_test_data.create_reference_reviews()
        agent_review = realistic_test_data.create_agent_generated_review()
        execution_trace = realistic_test_data.create_comprehensive_execution_trace()

        # Extract reference review text
        reference_texts = [review.comments for review in reference_reviews]

        # Execute comprehensive evaluation
        result = await evaluation_pipeline.evaluate_comprehensive(
            paper=paper_data["abstract"],
            review=agent_review.comments,
            execution_trace=execution_trace,
            reference_reviews=reference_texts,
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

        # Validate tier scores
        assert 0.0 <= result.tier1_score <= 1.0
        assert 0.0 <= result.tier2_score <= 1.0
        assert 0.0 <= result.tier3_score <= 1.0

        # Validate performance
        stats = evaluation_pipeline.get_execution_stats()
        assert stats["total_time"] > 0
        assert len(stats["tiers_executed"]) > 0

    @pytest.mark.asyncio
    async def test_observability_integration(self, realistic_test_data):
        """Test trace collection and observability features."""
        trace_collector = get_trace_collector(
            config={"observability": {"trace_collection": True}}
        )

        execution_id = "integration_test_observability"
        trace_collector.start_execution(execution_id)

        # Simulate agent interactions
        trace_collector.log_agent_interaction(
            from_agent="TestManager",
            to_agent="TestAgent",
            interaction_type="test_request",
            data={"test_type": "integration"},
        )

        trace_collector.log_tool_call(
            agent_id="TestAgent",
            tool_name="test_evaluator",
            success=True,
            duration=0.5,
            context="Integration test validation",
        )

        # End trace collection
        processed_trace = trace_collector.end_execution()

        # Validate trace data
        assert processed_trace is not None
        assert processed_trace.execution_id == execution_id
        assert len(processed_trace.agent_interactions) > 0
        assert len(processed_trace.tool_calls) > 0

    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(
        self, realistic_test_data, evaluation_pipeline
    ):
        """Test error handling and fallback mechanisms."""
        paper_data = realistic_test_data.create_scientific_paper()
        agent_review = realistic_test_data.create_agent_generated_review()

        # Test with minimal data to trigger potential fallbacks
        result = await evaluation_pipeline.evaluate_comprehensive(
            paper=paper_data["abstract"],
            review=agent_review.comments,
            # No execution_trace or reference_reviews to test robustness
        )

        # Should still produce valid results with fallbacks
        assert result is not None
        assert result.composite_score >= 0.0
        assert result.recommendation is not None

        # Check if fallback was used
        stats = evaluation_pipeline.get_execution_stats()
        # Fallback usage depends on API availability, but should not crash


if __name__ == "__main__":
    """Run the integration test directly."""

    async def run_integration_test():
        data = RealisticTestData()
        pipeline = EvaluationPipeline()

        print("Running comprehensive integration test...")

        paper_data = data.create_scientific_paper()
        reference_reviews = data.create_reference_reviews()
        agent_review = data.create_agent_generated_review()
        execution_trace = data.create_comprehensive_execution_trace()

        reference_texts = [review.comments for review in reference_reviews]

        result = await pipeline.evaluate_comprehensive(
            paper=paper_data["abstract"],
            review=agent_review.comments,
            execution_trace=execution_trace,
            reference_reviews=reference_texts,
        )

        print("✅ Integration test completed successfully!")
        print(f"   Composite Score: {result.composite_score:.3f}")
        print(f"   Recommendation: {result.recommendation}")
        print(f"   All tiers executed: {result.evaluation_complete}")

        stats = pipeline.get_execution_stats()
        print(
            f"   Performance: {stats['total_time']:.3f}s, tiers: {stats['tiers_executed']}"
        )

        return result

    asyncio.run(run_integration_test())
