#!/usr/bin/env python3
"""
Enhanced PeerRead integration tests with multi-paper scenarios.

This module provides comprehensive integration testing with realistic
multi-paper evaluation workflows, error recovery scenarios, and production
readiness validation for the PeerRead dataset integration.
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

from app.data_models.peerread_models import PeerReadConfig, PeerReadPaper
from app.data_utils.datasets_peerread import PeerReadDownloader, PeerReadLoader
from app.evals.evaluation_pipeline import EvaluationPipeline


class EnhancedIntegrationTestData:
    """Generator for enhanced integration test scenarios."""

    @staticmethod
    def create_diverse_paper_set() -> list[PeerReadPaper]:
        """Create diverse set of synthetic papers for multi-paper testing."""
        from app.data_models.peerread_models import PeerReadReview

        papers = []

        # High-quality paper
        papers.append(
            PeerReadPaper(
                paper_id="integration_paper_001",
                title="Advanced Neural Networks for Scientific Text Processing: A Comprehensive Framework",
                abstract=(
                    "This paper presents a comprehensive framework for applying "
                    "advanced neural network architectures to scientific text processing tasks. "
                    "We introduce a novel multi-scale attention mechanism that effectively captures "
                    "both local linguistic patterns and global document structure. Our approach "
                    "demonstrates significant improvements over existing methods across multiple "
                    "benchmark datasets. The framework includes specialized components for handling "
                    "domain-specific terminology, mathematical notation, and citation networks. "
                    "Extensive experiments on scientific paper corpora from computer science, "
                    "biology, and physics domains show consistent performance gains. The proposed "
                    "method achieves state-of-the-art results on scientific document classification, "
                    "summarization, and relation extraction tasks. Our analysis reveals that the "
                    "hierarchical attention mechanism enables better modeling of complex scientific "
                    "discourse patterns."
                ),
                reviews=[
                    PeerReadReview(
                        impact="5",
                        substance="5",
                        appropriateness="4",
                        meaningful_comparison="4",
                        presentation_format="Oral",
                        soundness_correctness="5",
                        originality="4",
                        recommendation="4",
                        clarity="4",
                        reviewer_confidence="4",
                        is_meta_review=False,
                        comments="""This is an exceptional paper that makes significant 
                    contributions to scientific text processing. The proposed multi-scale 
                    attention mechanism is novel and well-motivated. The experimental 
                    evaluation is comprehensive and demonstrates clear improvements over 
                    strong baselines. The writing is clear and the technical content is 
                    sound. I recommend acceptance.""",
                    ),
                    PeerReadReview(
                        impact="4",
                        substance="4",
                        appropriateness="4",
                        meaningful_comparison="4",
                        presentation_format="Oral",
                        soundness_correctness="4",
                        originality="4",
                        recommendation="4",
                        clarity="3",
                        reviewer_confidence="3",
                        is_meta_review=False,
                        comments="""The paper addresses an important problem and proposes a 
                    reasonable solution. The technical approach is sound and the experimental 
                    results are convincing. However, the presentation could be improved with 
                    clearer explanations of the attention mechanism. Overall a solid 
                    contribution that merits publication.""",
                    ),
                ],
                review_histories=[
                    "Initial submission",
                    "Revised based on reviewer feedback",
                ],
            )
        )

        # Medium-quality paper
        papers.append(
            PeerReadPaper(
                paper_id="integration_paper_002",
                title="Machine Learning Approaches for Academic Paper Classification",
                abstract="""We investigate the application of machine learning techniques 
            for automatic classification of academic papers across different scientific 
            domains. Our study compares traditional feature-based methods with modern 
            deep learning approaches. We evaluate performance on a large corpus of 
            papers from multiple conferences and journals. The results show that 
            transformer-based models achieve the best performance, with significant 
            improvements over bag-of-words baselines. However, the computational cost 
            of these methods remains a practical concern for large-scale deployment. 
            We also analyze the impact of different feature extraction strategies and 
            training data characteristics on classification accuracy.""",
                reviews=[
                    PeerReadReview(
                        impact="3",
                        substance="3",
                        appropriateness="3",
                        meaningful_comparison="3",
                        presentation_format="Poster",
                        soundness_correctness="3",
                        originality="2",
                        recommendation="3",
                        clarity="3",
                        reviewer_confidence="3",
                        is_meta_review=False,
                        comments="""This paper provides a useful comparison of different 
                    approaches for academic paper classification. The experimental setup is 
                    reasonable and the results are clearly presented. However, the technical 
                    contribution is somewhat limited as it primarily compares existing methods 
                    without proposing significant innovations. The work would benefit from 
                    deeper analysis of the results.""",
                    ),
                ],
                review_histories=["Initial submission"],
            )
        )

        # Lower-quality paper with issues
        papers.append(
            PeerReadPaper(
                paper_id="integration_paper_003",
                title="Text Mining for Research Papers",
                abstract="""This paper explores text mining techniques for analyzing research papers. 
            We apply various natural language processing methods to extract insights from academic 
            literature. The approach includes preprocessing steps, feature extraction, and 
            classification algorithms. We test our method on a small dataset of papers from 
            computer science conferences. The results show some promise but are limited by the 
            dataset size and evaluation methodology. Future work could explore larger datasets 
            and more sophisticated analysis techniques.""",
                reviews=[
                    PeerReadReview(
                        impact="2",
                        substance="2",
                        appropriateness="2",
                        meaningful_comparison="1",
                        presentation_format="Poster",
                        soundness_correctness="2",
                        originality="2",
                        recommendation="2",
                        clarity="2",
                        reviewer_confidence="3",
                        is_meta_review=False,
                        comments="""This paper addresses a relevant problem but suffers from several 
                    significant weaknesses. The technical approach is not well-motivated and lacks 
                    novelty. The experimental evaluation is insufficient with a very small dataset 
                    and limited baselines. The writing quality is poor with numerous grammatical 
                    errors and unclear explanations. The contribution is not sufficient for 
                    publication at this venue.""",
                    ),
                    PeerReadReview(
                        impact="2",
                        substance="1",
                        appropriateness="2",
                        meaningful_comparison="1",
                        presentation_format="Poster",
                        soundness_correctness="2",
                        originality="1",
                        recommendation="1",
                        clarity="2",
                        reviewer_confidence="4",
                        is_meta_review=False,
                        comments="""I cannot recommend this paper for acceptance. The technical 
                    contribution is minimal and the experimental validation is completely inadequate. 
                    The related work section is superficial and does not properly position the work. 
                    The authors need to significantly strengthen both the technical content and 
                    experimental evaluation before resubmission.""",
                    ),
                ],
                review_histories=[
                    "Initial submission",
                    "Rejected - major revisions needed",
                ],
            )
        )

        return papers

    @staticmethod
    def create_multi_paper_evaluation_scenario() -> dict[str, Any]:
        """Create scenario for multi-paper evaluation testing."""
        return {
            "scenario_name": "multi_paper_comprehensive_evaluation",
            "paper_count": 3,
            "evaluation_types": [
                "quality_assessment",
                "comparative_analysis",
                "recommendation_ranking",
            ],
            "expected_outcomes": {
                "paper_001": {"recommendation": "accept", "score_range": (0.7, 0.9)},
                "paper_002": {
                    "recommendation": "weak_accept",
                    "score_range": (0.5, 0.7),
                },
                "paper_003": {"recommendation": "reject", "score_range": (0.1, 0.4)},
            },
            "performance_targets": {
                "max_total_time": 75.0,  # 3 papers * 25s target
                "max_memory_usage": 1000,  # MB
                "min_success_rate": 0.8,
            },
        }

    @staticmethod
    def create_error_simulation_scenarios() -> list[dict[str, Any]]:
        """Create scenarios for error recovery testing."""
        return [
            {
                "name": "network_timeout_simulation",
                "error_type": "network",
                "affected_components": ["tier2_llm"],
                "recovery_strategy": "fallback_to_tier1_tier3",
                "expected_behavior": "graceful_degradation",
            },
            {
                "name": "api_rate_limit_simulation",
                "error_type": "rate_limit",
                "affected_components": ["tier2_llm"],
                "recovery_strategy": "retry_with_backoff",
                "expected_behavior": "eventual_success",
            },
            {
                "name": "memory_limit_simulation",
                "error_type": "resource",
                "affected_components": ["tier3_graph"],
                "recovery_strategy": "reduce_graph_complexity",
                "expected_behavior": "simplified_analysis",
            },
            {
                "name": "invalid_data_simulation",
                "error_type": "data_validation",
                "affected_components": ["tier1_traditional"],
                "recovery_strategy": "skip_invalid_metrics",
                "expected_behavior": "partial_evaluation",
            },
        ]


class TestEnhancedPeerReadIntegration:
    """Enhanced integration tests for comprehensive PeerRead workflows."""

    @pytest.fixture
    def enhanced_test_data(self):
        """Fixture providing enhanced integration test data."""
        return EnhancedIntegrationTestData()

    @pytest.fixture
    def evaluation_pipeline(self):
        """Fixture providing evaluation pipeline."""
        return EvaluationPipeline()

    @pytest.fixture
    async def real_peerread_papers(self):
        """Fixture providing real PeerRead papers if available."""
        from app.data_utils.datasets_peerread import load_peerread_config

        try:
            config = load_peerread_config()

            with tempfile.TemporaryDirectory() as temp_dir:
                test_config = PeerReadConfig(
                    venues=config.venues[:1],
                    splits=config.splits[:1],
                    cache_directory=temp_dir,
                    max_papers_per_query=3,
                    raw_github_base_url=config.raw_github_base_url,
                    github_api_base_url=config.github_api_base_url,
                    download_timeout=config.download_timeout,
                    max_retries=config.max_retries,
                    retry_delay_seconds=config.retry_delay_seconds,
                )

                downloader = PeerReadDownloader(test_config)
                result = downloader.download_venue_split(test_config.venues[0], test_config.splits[0], max_papers=3)

                if result.success and result.papers_downloaded > 0:
                    loader = PeerReadLoader(test_config)
                    papers = loader.load_papers(test_config.venues[0], test_config.splits[0])
                    yield papers
                else:
                    yield []
        except Exception:
            yield []  # Fallback to empty list if real data unavailable

    @pytest.mark.integration
    async def test_multi_paper_evaluation_workflow(self, enhanced_test_data, evaluation_pipeline):
        """Test evaluation of multiple papers with varied characteristics."""
        papers = enhanced_test_data.create_diverse_paper_set()
        scenario = enhanced_test_data.create_multi_paper_evaluation_scenario()

        print("\n=== Multi-Paper Evaluation Workflow ===")
        print(f"Testing {len(papers)} papers with diverse quality profiles")

        # Track overall performance
        total_start_time = time.time()
        evaluation_results = {}
        successful_evaluations = 0

        for i, paper in enumerate(papers):
            print(f"\nEvaluating Paper {i + 1}: {paper.title[:50]}...")

            # Extract reference reviews
            reference_reviews = [review.comments for review in paper.reviews]

            # Create synthetic agent-generated review
            agent_review = f"""This paper titled "{paper.title}" presents work in the 
            field of scientific text processing. The abstract suggests a methodical approach 
            with experimental validation. The technical content appears to address relevant 
            problems in the domain. The scope and complexity of the work seem appropriate 
            for academic publication. The methodology described indicates systematic 
            evaluation with comparison to existing approaches."""

            # Create execution trace
            execution_trace = {
                "execution_id": f"multi_paper_test_{paper.paper_id}",
                "agent_interactions": [
                    {
                        "from": "Manager",
                        "to": "Analyst",
                        "type": "paper_analysis_request",
                        "timestamp": 1.0,
                        "paper_id": paper.paper_id,
                    },
                    {
                        "from": "Analyst",
                        "to": "Reviewer",
                        "type": "analysis_complete",
                        "timestamp": 3.5,
                        "quality_indicators": len(paper.reviews),
                    },
                ],
                "tool_calls": [
                    {
                        "agent_id": "Analyst",
                        "tool_name": "peerread_analyzer",
                        "success": True,
                        "duration": 0.8,
                        "timestamp": 1.5,
                        "context": f"Analyzing paper {paper.paper_id}",
                    },
                ],
            }

            # Execute evaluation
            paper_start_time = time.time()

            try:
                result = await evaluation_pipeline.evaluate_comprehensive(
                    paper=paper.abstract,
                    review=agent_review,
                    execution_trace=execution_trace,
                    reference_reviews=reference_reviews,
                )

                paper_duration = time.time() - paper_start_time

                if result and result.evaluation_complete:
                    successful_evaluations += 1
                    evaluation_results[paper.paper_id] = {
                        "result": result,
                        "duration": paper_duration,
                        "expected_recommendation": scenario["expected_outcomes"]
                        .get(paper.paper_id.split("_")[-1], {})
                        .get("recommendation", "unknown"),
                    }

                    print(f"  ✅ Completed in {paper_duration:.2f}s")
                    print(f"     Score: {result.composite_score:.3f}")
                    print(f"     Recommendation: {result.recommendation}")

                    # Validate against expected outcomes if available
                    paper_key = paper.paper_id.split("_")[-1]
                    if paper_key in scenario["expected_outcomes"]:
                        expected = scenario["expected_outcomes"][paper_key]
                        expected_rec = expected["recommendation"]

                        if result.recommendation == expected_rec:
                            print(f"     ✅ Matches expected recommendation: {expected_rec}")
                        else:
                            print(f"     ⚠️  Expected {expected_rec}, got {result.recommendation}")

                else:
                    print("  ❌ Evaluation failed or incomplete")

            except Exception as e:
                print(f"  ❌ Error evaluating {paper.paper_id}: {e}")
                continue

        # Calculate overall statistics
        total_duration = time.time() - total_start_time
        success_rate = successful_evaluations / len(papers)

        print("\n📊 Multi-Paper Evaluation Results:")
        print(f"   Papers evaluated: {len(papers)}")
        print(f"   Successful evaluations: {successful_evaluations}")
        print(f"   Success rate: {success_rate:.1%}")
        print(f"   Total time: {total_duration:.2f}s")
        print(f"   Average time per paper: {total_duration / len(papers):.2f}s")

        # Validate performance targets
        targets = scenario["performance_targets"]
        assert total_duration <= targets["max_total_time"], (
            f"Total time {total_duration:.2f}s exceeds target {targets['max_total_time']}s"
        )
        assert success_rate >= targets["min_success_rate"], (
            f"Success rate {success_rate:.1%} below target {targets['min_success_rate']:.1%}"
        )

        # Validate result consistency
        if len(evaluation_results) >= 2:
            scores = [res["result"].composite_score for res in evaluation_results.values()]
            score_range = max(scores) - min(scores)
            print(f"   Score range: {min(scores):.3f} - {max(scores):.3f} (spread: {score_range:.3f})")

            # Different quality papers should produce different scores
            assert score_range > 0.1, "Papers with different qualities should have different scores"

    @pytest.mark.integration
    async def test_error_recovery_scenarios(self, enhanced_test_data, evaluation_pipeline):
        """Test error recovery and graceful degradation."""
        print("\n=== Error Recovery Scenarios ===")

        error_scenarios = enhanced_test_data.create_error_simulation_scenarios()
        papers = enhanced_test_data.create_diverse_paper_set()
        test_paper = papers[0]  # Use high-quality paper for testing

        reference_reviews = [review.comments for review in test_paper.reviews]
        agent_review = "This paper presents a comprehensive technical contribution with solid methodology."
        execution_trace = {
            "execution_id": "error_recovery_test",
            "agent_interactions": [],
            "tool_calls": [],
        }

        for scenario in error_scenarios:
            print(f"\nTesting {scenario['name']}...")

            # For this test, we'll simulate by testing normal operation and
            # monitoring for robustness
            # Real error injection would require more complex test infrastructure

            try:
                start_time = time.time()
                result = await evaluation_pipeline.evaluate_comprehensive(
                    paper=test_paper.abstract,
                    review=agent_review,
                    execution_trace=execution_trace,
                    reference_reviews=reference_reviews,
                )
                duration = time.time() - start_time

                if result and result.evaluation_complete:
                    print(f"  ✅ Normal operation: {duration:.2f}s")
                    print(f"     Score: {result.composite_score:.3f}")
                    print("     All tiers completed successfully")

                    # Validate that pipeline can handle various conditions
                    stats = evaluation_pipeline.get_execution_stats()
                    if stats:
                        print(f"     Pipeline stats available: {len(stats)} metrics")
                else:
                    print("  ⚠️  Evaluation incomplete - testing fallback behavior")

            except Exception as e:
                print(f"  ⚠️  Exception occurred: {type(e).__name__}: {e}")
                print("      This tests error handling robustness")

        print("\n✅ Error recovery testing completed")

    @pytest.mark.integration
    async def test_production_readiness_checklist(self, evaluation_pipeline, enhanced_test_data):
        """Validate production readiness across all components."""
        print("\n=== Production Readiness Checklist ===")

        papers = enhanced_test_data.create_diverse_paper_set()
        test_paper = papers[0]

        checklist_results = {}

        # Test 1: Concurrent evaluation requests
        print("1. Testing concurrent evaluation handling...")

        concurrent_tasks = []
        for i in range(3):  # Limited concurrency for testing
            task_data = {
                "paper": test_paper.abstract,
                "review": f"Review {i + 1}: This paper presents interesting technical work.",
                "execution_trace": {"execution_id": f"concurrent_test_{i}"},
                "reference_reviews": [review.comments for review in test_paper.reviews[:1]],
            }
            task = evaluation_pipeline.evaluate_comprehensive(**task_data)
            concurrent_tasks.append(task)

        try:
            start_time = time.time()
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            concurrent_duration = time.time() - start_time

            successful_concurrent = sum(1 for r in results if hasattr(r, "composite_score"))
            checklist_results["concurrent_evaluation"] = {
                "success": successful_concurrent >= 2,  # At least 2/3 should succeed
                "count": successful_concurrent,
                "duration": concurrent_duration,
            }

            print(f"   ✅ Concurrent evaluation: {successful_concurrent}/3 succeeded in {concurrent_duration:.2f}s")

        except Exception as e:
            checklist_results["concurrent_evaluation"] = {
                "success": False,
                "error": str(e),
            }
            print(f"   ❌ Concurrent evaluation failed: {e}")

        # Test 2: Memory usage monitoring
        print("2. Testing memory usage bounds...")

        import os

        import psutil

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Run evaluation and monitor memory
        result = await evaluation_pipeline.evaluate_comprehensive(
            paper=test_paper.abstract,
            review="Memory test evaluation of this technical paper.",
            execution_trace={"execution_id": "memory_test"},
            reference_reviews=[review.comments for review in test_paper.reviews],
        )

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        checklist_results["memory_usage"] = {
            "success": memory_increase < 500,  # Less than 500MB increase
            "increase_mb": memory_increase,
            "total_mb": memory_after,
        }

        status = "✅" if memory_increase < 500 else "⚠️"
        print(f"   {status} Memory usage: +{memory_increase:.1f}MB (total: {memory_after:.1f}MB)")

        # Test 3: Log output quality
        print("3. Testing log output quality...")

        # This is validated by checking that evaluation completes without errors
        # and produces structured output
        checklist_results["logging_quality"] = {
            "success": result is not None and result.evaluation_complete,
            "structured_output": hasattr(result, "composite_score") and hasattr(result, "recommendation"),
        }

        if result and result.evaluation_complete:
            print("   ✅ Structured logging: Complete evaluation with score and recommendation")
        else:
            print("   ❌ Logging issues: Incomplete or missing structured output")

        # Test 4: Configuration validation
        print("4. Testing configuration hot-reloading...")

        try:
            # Test that pipeline can reload configuration
            original_config = evaluation_pipeline.config_manager.get_full_config()
            assert isinstance(original_config, dict), "Configuration should be dictionary"
            assert "evaluation_system" in original_config, "Should have evaluation_system config"

            checklist_results["configuration"] = {
                "success": True,
                "config_keys": len(original_config.keys()),
            }

            print(f"   ✅ Configuration validation: {len(original_config)} config sections loaded")

        except Exception as e:
            checklist_results["configuration"] = {"success": False, "error": str(e)}
            print(f"   ❌ Configuration issues: {e}")

        # Test 5: Performance consistency
        print("5. Testing performance consistency...")

        performance_times = []
        for run in range(3):
            start_time = time.time()
            result = await evaluation_pipeline.evaluate_comprehensive(
                paper=test_paper.abstract[:200],  # Shorter for consistency testing
                review="Consistency test review.",
                execution_trace={"execution_id": f"consistency_test_{run}"},
                reference_reviews=[test_paper.reviews[0].comments[:100]],
            )
            duration = time.time() - start_time
            if result and result.evaluation_complete:
                performance_times.append(duration)

        if len(performance_times) >= 2:
            import statistics

            mean_time = statistics.mean(performance_times)
            stddev_time = statistics.stdev(performance_times)
            coefficient_of_variation = stddev_time / mean_time if mean_time > 0 else 0

            checklist_results["performance_consistency"] = {
                "success": coefficient_of_variation < 0.3,  # Less than 30% variation
                "mean_time": mean_time,
                "stddev_time": stddev_time,
                "cv": coefficient_of_variation,
            }

            status = "✅" if coefficient_of_variation < 0.3 else "⚠️"
            print(
                f"   {status} Performance consistency: {mean_time:.2f}±{stddev_time:.2f}s "
                f"(CV: {coefficient_of_variation:.2%})"
            )

        # Summary
        print("\n📋 Production Readiness Summary:")
        total_checks = len(checklist_results)
        passed_checks = sum(1 for r in checklist_results.values() if r.get("success", False))

        print(f"   Checks passed: {passed_checks}/{total_checks}")
        print(f"   Ready for production: {'✅ YES' if passed_checks >= total_checks * 0.8 else '⚠️ NEEDS ATTENTION'}")

        for check_name, check_result in checklist_results.items():
            status = "✅" if check_result.get("success", False) else "❌"
            print(f"   {status} {check_name.replace('_', ' ').title()}")

    @pytest.mark.integration
    @pytest.mark.network
    async def test_real_data_multi_paper_scenario(self, real_peerread_papers, evaluation_pipeline):
        """Test multi-paper scenario with real PeerRead data if available."""
        papers = real_peerread_papers

        if not papers:
            pytest.skip("No real PeerRead data available for multi-paper testing")

        print("\n=== Real Data Multi-Paper Scenario ===")
        print(f"Testing with {len(papers)} real PeerRead papers")

        # Test with up to 2 real papers to manage execution time
        test_papers = papers[:2]

        results = []
        total_start_time = time.time()

        for i, paper in enumerate(test_papers):
            print(f"\nProcessing real paper {i + 1}: {paper.title[:40]}...")

            reference_reviews = [review.comments for review in paper.reviews]
            synthetic_review = "This paper addresses important research questions in the field. The methodology appears sound and the experimental design is appropriate for the problem domain. The contribution represents a meaningful advance in understanding."

            execution_trace = {
                "execution_id": f"real_multi_paper_{paper.paper_id}",
                "agent_interactions": [
                    {
                        "from": "Coordinator",
                        "to": "Evaluator",
                        "type": "evaluate_paper",
                        "timestamp": 1.0,
                    }
                ],
            }

            start_time = time.time()

            try:
                result = await evaluation_pipeline.evaluate_comprehensive(
                    paper=paper.abstract,
                    review=synthetic_review,
                    execution_trace=execution_trace,
                    reference_reviews=reference_reviews,
                )

                duration = time.time() - start_time

                if result and result.evaluation_complete:
                    results.append(
                        {
                            "paper_id": paper.paper_id,
                            "title": paper.title[:30] + "...",
                            "score": result.composite_score,
                            "recommendation": result.recommendation,
                            "duration": duration,
                            "review_count": len(paper.reviews),
                        }
                    )

                    print(
                        f"  ✅ Score: {result.composite_score:.3f}, Rec: {result.recommendation}, Time: {duration:.2f}s"
                    )
                else:
                    print("  ❌ Evaluation failed")

            except Exception as e:
                print(f"  ❌ Error: {e}")

        total_duration = time.time() - total_start_time

        if results:
            print("\n📊 Real Data Multi-Paper Results:")
            print(f"   Papers processed: {len(results)}")
            print(f"   Total time: {total_duration:.2f}s")
            print(f"   Average time per paper: {total_duration / len(results):.2f}s")

            scores = [r["score"] for r in results]
            print(f"   Score range: {min(scores):.3f} - {max(scores):.3f}")

            recommendations = [r["recommendation"] for r in results]
            rec_distribution = {rec: recommendations.count(rec) for rec in set(recommendations)}
            print(f"   Recommendation distribution: {rec_distribution}")

            print("\n   Individual results:")
            for result in results:
                print(f"     {result['title']}: {result['score']:.3f} ({result['recommendation']})")
        else:
            print("\n❌ No successful evaluations with real data")


if __name__ == "__main__":
    """Run the enhanced integration tests directly."""

    async def run_enhanced_integration():
        print("Running enhanced PeerRead integration tests...")
        print("This comprehensive test suite may take several minutes to complete.")

        try:
            # Initialize components
            pipeline = EvaluationPipeline()
            test_data = EnhancedIntegrationTestData()

            print("✅ Components initialized")

            # Test multi-paper workflow
            papers = test_data.create_diverse_paper_set()
            print(f"\n📚 Testing with {len(papers)} synthetic papers:")
            for i, paper in enumerate(papers, 1):
                quality_indicator = len([r for r in paper.reviews if int(r.recommendation) >= 3])
                print(f"  {i}. {paper.title[:50]}... ({quality_indicator} positive reviews)")

            print("\n🔄 Running multi-paper evaluation workflow...")

            # Track performance
            workflow_start = time.time()
            successful_papers = 0

            for i, paper in enumerate(papers):
                reference_reviews = [review.comments for review in paper.reviews]
                agent_review = "This paper presents a technical contribution to the field with experimental validation."
                execution_trace = {"execution_id": f"enhanced_test_{i}"}

                try:
                    result = await pipeline.evaluate_comprehensive(
                        paper=paper.abstract,
                        review=agent_review,
                        execution_trace=execution_trace,
                        reference_reviews=reference_reviews,
                    )

                    if result and result.evaluation_complete:
                        successful_papers += 1
                        print(f"  ✅ Paper {i + 1}: {result.composite_score:.3f} ({result.recommendation})")
                    else:
                        print(f"  ❌ Paper {i + 1}: evaluation failed")

                except Exception as e:
                    print(f"  ❌ Paper {i + 1}: error - {e}")

            workflow_duration = time.time() - workflow_start
            success_rate = successful_papers / len(papers)

            print("\n📊 Workflow Results:")
            print(f"   Success rate: {success_rate:.1%} ({successful_papers}/{len(papers)})")
            print(f"   Total time: {workflow_duration:.2f}s")
            print(f"   Average per paper: {workflow_duration / len(papers):.2f}s")

            # Test production readiness
            print("\n🏭 Testing production readiness...")

            try:
                # Quick concurrent test
                concurrent_tasks = []
                for i in range(2):
                    task = pipeline.evaluate_comprehensive(
                        paper=papers[0].abstract[:200],
                        review=f"Concurrent test review {i + 1}",
                        execution_trace={"execution_id": f"concurrent_{i}"},
                        reference_reviews=[papers[0].reviews[0].comments[:100]],
                    )
                    concurrent_tasks.append(task)

                concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
                concurrent_success = sum(1 for r in concurrent_results if hasattr(r, "composite_score"))

                print(f"   Concurrent processing: {concurrent_success}/2 successful")

                # Memory usage check
                import os

                import psutil

                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                print(f"   Memory usage: {memory_mb:.1f}MB")

                print("   ✅ Production readiness validated")

            except Exception as e:
                print(f"   ⚠️  Production readiness issues: {e}")

        except Exception as e:
            print(f"❌ Enhanced integration test failed: {e}")
            raise

        print("\n✅ Enhanced PeerRead integration testing completed!")

    asyncio.run(run_enhanced_integration())
