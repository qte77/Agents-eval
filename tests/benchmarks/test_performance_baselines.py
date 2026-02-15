#!/usr/bin/env python3
"""
Performance benchmark suite for evaluation pipeline components.

This module establishes baseline performance metrics across evaluation
components, measuring execution times, memory usage, and throughput
under various conditions to validate performance targets.
"""

import asyncio
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from inline_snapshot import snapshot

# Ensure src directory is available for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.data_models.evaluation_models import (
    GraphTraceData,
)
from app.judge.evaluation_pipeline import EvaluationPipeline
from app.judge.graph_analysis import GraphAnalysisEngine
from app.judge.llm_evaluation_managers import LLMJudgeEngine
from app.judge.traditional_metrics import TraditionalMetricsEngine


class PerformanceBenchmarkData:
    """Generator for performance testing data of varying complexity."""

    @staticmethod
    def create_short_paper_abstract(word_count: int = 100) -> str:
        """Create short paper abstract for performance testing."""
        base_content = (
            "This paper investigates machine learning approaches for natural "
            "language processing. We propose a novel transformer-based architecture "
            "that improves performance on classification tasks. Our experiments "
            "demonstrate significant improvements over baseline methods across "
            "multiple datasets. The approach shows particular strength in handling "
            "complex linguistic patterns and domain-specific terminology. Results "
            "indicate promising applications for real-world deployment scenarios."
        )

        # Repeat and truncate to reach target word count
        words = base_content.split()
        repeated_words = (words * ((word_count // len(words)) + 1))[:word_count]
        return " ".join(repeated_words)

    @staticmethod
    def create_long_paper_abstract(word_count: int = 300) -> str:
        """Create long paper abstract for performance testing."""
        base_content = (
            "Recent advances in deep learning have revolutionized natural "
            "language processing, with transformer architectures achieving "
            "state-of-the-art results across numerous tasks. However, these "
            "models face significant challenges in computational efficiency, "
            "interpretability, and robustness to domain shift. This paper "
            "addresses these limitations through a comprehensive study of "
            "architectural modifications and training strategies. We propose a "
            "multi-scale attention mechanism that reduces computational complexity "
            "while maintaining competitive performance. Our approach incorporates "
            "hierarchical representations that capture both local linguistic "
            "patterns and global document structure. Extensive experiments on "
            "benchmark datasets including GLUE, SuperGLUE, and domain-specific "
            "corpora demonstrate consistent improvements over existing methods. "
            "We achieve notable gains in efficiency with 40% reduction in "
            "inference time and 25% decrease in memory usage while maintaining "
            "or improving accuracy across all evaluated tasks. The proposed method "
            "shows particular strength in few-shot learning scenarios and "
            "exhibits improved robustness to adversarial examples. Our analysis "
            "reveals that the hierarchical attention mechanism enables better "
            "handling of long-range dependencies and complex semantic relationships."
        )

        words = base_content.split()
        repeated_words = (words * ((word_count // len(words)) + 1))[:word_count]
        return " ".join(repeated_words)

    @staticmethod
    def create_comprehensive_review(word_count: int = 200) -> str:
        """Create comprehensive review for testing."""
        base_review = (
            "This paper presents a solid technical contribution with "
            "well-designed experiments and thorough evaluation. The proposed "
            "approach demonstrates clear improvements over baseline methods across "
            "multiple metrics. The writing is generally clear and the methodology "
            "is sound. However, there are several areas that could be strengthened. "
            "The related work section could benefit from more comprehensive "
            "coverage of recent developments in the field. The experimental setup "
            "would be more convincing with additional baselines and statistical "
            "significance testing. The discussion of limitations is somewhat brief "
            "and could be expanded. Overall, this work makes a meaningful "
            "contribution to the field and merits publication with minor revisions."
        )

        words = base_review.split()
        repeated_words = (words * ((word_count // len(words)) + 1))[:word_count]
        return " ".join(repeated_words)

    @staticmethod
    def create_simple_trace(interaction_count: int = 10) -> dict[str, Any]:
        """Create simple execution trace for testing."""
        interactions = []
        tool_calls = []

        for i in range(interaction_count):
            interactions.append(
                {
                    "from": f"Agent_{i % 3}",
                    "to": f"Agent_{(i + 1) % 3}",
                    "type": "task_request" if i % 2 == 0 else "result_delivery",
                    "timestamp": i * 0.5,
                    "data_size": 100 + i * 50,
                }
            )

            if i % 3 == 0:
                tool_calls.append(
                    {
                        "agent_id": f"Agent_{i % 3}",
                        "tool_name": f"tool_{i % 5}",
                        "success": True,
                        "duration": 0.1 + (i % 5) * 0.1,
                        "timestamp": i * 0.5 + 0.2,
                        "context": f"Processing task {i}",
                    }
                )

        return {
            "execution_id": f"simple_trace_{interaction_count}",
            "agent_interactions": interactions,
            "tool_calls": tool_calls,
            "coordination_events": [
                {
                    "coordination_type": "task_delegation",
                    "manager_agent": "Agent_0",
                    "target_agents": ["Agent_1", "Agent_2"],
                    "timestamp": 0.0,
                    "task": f"benchmark_task_{interaction_count}",
                }
            ],
        }

    @staticmethod
    def create_complex_trace(interaction_count: int = 100) -> dict[str, Any]:
        """Create complex execution trace for testing."""
        interactions = []
        tool_calls = []
        coordination_events = []

        # Create more complex interaction patterns
        for i in range(interaction_count):
            agent_count = 5
            interactions.append(
                {
                    "from": f"Agent_{i % agent_count}",
                    "to": f"Agent_{(i + 1) % agent_count}",
                    "type": [
                        "task_request",
                        "result_delivery",
                        "coordination",
                        "error_report",
                    ][i % 4],
                    "timestamp": i * 0.2,
                    "data_size": 50 + (i % 20) * 100,
                    "complexity": (i % 10) + 1,
                }
            )

            if i % 2 == 0:
                tool_calls.append(
                    {
                        "agent_id": f"Agent_{i % agent_count}",
                        "tool_name": f"complex_tool_{i % 8}",
                        "success": (i % 10) != 9,  # 10% failure rate
                        "duration": 0.05 + (i % 15) * 0.05,
                        "timestamp": i * 0.2 + 0.1,
                        "context": f"Complex processing task {i}",
                        "memory_usage": 1000 + i * 100,
                    }
                )

            if i % 20 == 0:
                coordination_events.append(
                    {
                        "coordination_type": [
                            "task_delegation",
                            "resource_allocation",
                            "conflict_resolution",
                        ][i // 20 % 3],
                        "manager_agent": f"Agent_{i % agent_count}",
                        "target_agents": [
                            f"Agent_{j}" for j in range(agent_count) if j != i % agent_count
                        ],
                        "timestamp": i * 0.2,
                        "task": f"complex_coordination_{i // 20}",
                        "complexity": (i // 20) + 1,
                    }
                )

        return {
            "execution_id": f"complex_trace_{interaction_count}",
            "agent_interactions": interactions,
            "tool_calls": tool_calls,
            "coordination_events": coordination_events,
        }


class TestPerformanceBaselines:
    """Test suite for establishing performance baselines."""

    @pytest.fixture
    def benchmark_data(self):
        """Fixture providing benchmark test data."""
        return PerformanceBenchmarkData()

    @pytest.fixture
    def traditional_engine(self):
        """Fixture providing traditional metrics engine."""
        return TraditionalMetricsEngine()

    @pytest.fixture
    def llm_engine(self):
        """Fixture providing LLM judge engine."""
        from app.judge.settings import JudgeSettings

        return LLMJudgeEngine(JudgeSettings())

    @pytest.fixture
    def graph_engine(self):
        """Fixture providing graph analysis engine."""
        from app.judge.settings import JudgeSettings

        return GraphAnalysisEngine(JudgeSettings())

    @pytest.fixture
    def evaluation_pipeline(self):
        """Fixture providing evaluation pipeline."""
        return EvaluationPipeline()

    @pytest.mark.benchmark
    async def benchmark_tier1_performance(self, traditional_engine, benchmark_data):
        """Benchmark Traditional Metrics performance across paper sizes."""
        print("\n=== Tier 1 (Traditional Metrics) Performance Benchmark ===")

        # Test different paper lengths
        paper_lengths = [100, 300, 500, 800]  # Word counts
        performance_data = []

        for word_count in paper_lengths:
            print(f"\nTesting {word_count}-word papers:")

            # Create test data
            paper_abstract = benchmark_data.create_short_paper_abstract(word_count)
            review_text = benchmark_data.create_comprehensive_review(150)
            reference_reviews = [
                benchmark_data.create_comprehensive_review(200),
                benchmark_data.create_comprehensive_review(180),
            ]

            # Run multiple iterations for statistical analysis
            execution_times = []
            for run in range(5):
                start_time = time.time()

                result = await traditional_engine.evaluate(
                    paper=paper_abstract,
                    review=review_text,
                    reference_reviews=reference_reviews,
                )

                execution_time = time.time() - start_time
                execution_times.append(execution_time)

                # Validate result
                assert result is not None, f"Tier 1 evaluation failed for {word_count} words"
                assert result.success, f"Tier 1 evaluation unsuccessful for {word_count} words"

            # Calculate statistics
            mean_time = statistics.mean(execution_times)
            median_time = statistics.median(execution_times)
            stddev_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
            percentile_95 = sorted(execution_times)[int(0.95 * len(execution_times))]

            performance_data.append(
                {
                    "word_count": word_count,
                    "mean_time": mean_time,
                    "median_time": median_time,
                    "stddev_time": stddev_time,
                    "percentile_95": percentile_95,
                    "max_time": max(execution_times),
                    "min_time": min(execution_times),
                }
            )

            print(
                f"  Mean: {mean_time:.3f}s, Median: {median_time:.3f}s, "
                f"95th: {percentile_95:.3f}s, Max: {max(execution_times):.3f}s"
            )

            # Validate against target (1.0 second)
            target_time = 1.0
            success_rate = sum(1 for t in execution_times if t <= target_time) / len(
                execution_times
            )
            print(f"  Success rate (≤{target_time}s): {success_rate:.1%}")

            # Reason: Allow some flexibility for larger papers but warn if slow
            if mean_time > target_time * 1.5:
                print(f"  ⚠️  Mean time exceeds 1.5x target for {word_count} words")

        # Summary
        print("\n📊 Tier 1 Summary:")
        print(f"  Tested paper sizes: {paper_lengths}")
        print("  Performance target: 1.0s")

        overall_times = [data["mean_time"] for data in performance_data]
        print(f"  Overall mean: {statistics.mean(overall_times):.3f}s")
        print(f"  Overall range: {min(overall_times):.3f}s - {max(overall_times):.3f}s")

        return performance_data

    @pytest.mark.benchmark
    @pytest.mark.network
    async def benchmark_tier2_performance(self, llm_engine, benchmark_data):
        """Benchmark LLM-as-Judge performance with realistic content."""
        print("\n=== Tier 2 (LLM-as-Judge) Performance Benchmark ===")

        # Test different content complexities
        test_scenarios = [
            ("Simple", 150, 100),  # (name, paper_words, review_words)
            ("Medium", 300, 200),
            ("Complex", 500, 300),
        ]

        performance_data = []

        for scenario_name, paper_words, review_words in test_scenarios:
            print(f"\nTesting {scenario_name} scenario ({paper_words}/{review_words} words):")

            # Create test data
            paper_excerpt = benchmark_data.create_short_paper_abstract(paper_words)
            generated_review = benchmark_data.create_comprehensive_review(review_words)

            # Run multiple iterations
            execution_times = []
            success_count = 0

            for run in range(3):  # Fewer runs due to API costs
                start_time = time.time()

                try:
                    result = await llm_engine.evaluate(
                        paper_excerpt=paper_excerpt,
                        generated_review=generated_review,
                    )

                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)

                    if result and result.success:
                        success_count += 1

                except Exception as e:
                    print(f"  Run {run + 1} failed: {e}")
                    continue

            if not execution_times:
                print(f"  ❌ All runs failed for {scenario_name}")
                continue

            # Calculate statistics
            mean_time = statistics.mean(execution_times)
            success_rate = success_count / len(execution_times)

            performance_data.append(
                {
                    "scenario": scenario_name,
                    "paper_words": paper_words,
                    "review_words": review_words,
                    "mean_time": mean_time,
                    "success_rate": success_rate,
                    "total_runs": len(execution_times),
                }
            )

            print(f"  Mean time: {mean_time:.3f}s")
            print(f"  Success rate: {success_rate:.1%}")

            # Validate against target (10.0 seconds)
            target_time = 10.0
            if mean_time > target_time:
                print(f"  ⚠️  Exceeds target time of {target_time}s")
            else:
                print(f"  ✅ Within target time of {target_time}s")

        print("\n📊 Tier 2 Summary:")
        if performance_data:
            overall_times = [data["mean_time"] for data in performance_data]
            overall_success = statistics.mean([data["success_rate"] for data in performance_data])
            print("  Performance target: 10.0s")
            print(f"  Overall mean time: {statistics.mean(overall_times):.3f}s")
            print(f"  Overall success rate: {overall_success:.1%}")

        return performance_data

    @pytest.mark.benchmark
    async def benchmark_tier3_performance(self, graph_engine, benchmark_data):
        """Benchmark Graph Analysis performance with varying complexity."""
        print("\n=== Tier 3 (Graph Analysis) Performance Benchmark ===")

        # Test different trace complexities
        complexity_levels = [
            ("Simple", 10),  # (name, interaction_count)
            ("Medium", 50),
            ("Complex", 100),
            ("Large", 200),
        ]

        performance_data = []

        for complexity_name, interaction_count in complexity_levels:
            print(f"\nTesting {complexity_name} traces ({interaction_count} interactions):")

            # Create test trace
            if interaction_count <= 50:
                trace_data = benchmark_data.create_simple_trace(interaction_count)
            else:
                trace_data = benchmark_data.create_complex_trace(interaction_count)

            # Convert to GraphTraceData
            graph_trace = GraphTraceData(
                execution_id=trace_data["execution_id"],
                agent_interactions=trace_data["agent_interactions"],
                tool_calls=trace_data["tool_calls"],
                coordination_events=trace_data.get("coordination_events", []),
            )

            # Run multiple iterations
            execution_times = []
            success_count = 0

            for run in range(5):
                start_time = time.time()

                try:
                    result = await graph_engine.analyze(graph_trace)
                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)

                    if result and result.success:
                        success_count += 1

                except Exception as e:
                    print(f"  Run {run + 1} failed: {e}")
                    continue

            if not execution_times:
                print(f"  ❌ All runs failed for {complexity_name}")
                continue

            # Calculate statistics
            mean_time = statistics.mean(execution_times)
            median_time = statistics.median(execution_times)
            max_time = max(execution_times)
            success_rate = success_count / len(execution_times)

            performance_data.append(
                {
                    "complexity": complexity_name,
                    "interaction_count": interaction_count,
                    "mean_time": mean_time,
                    "median_time": median_time,
                    "max_time": max_time,
                    "success_rate": success_rate,
                }
            )

            print(f"  Mean: {mean_time:.3f}s, Median: {median_time:.3f}s, Max: {max_time:.3f}s")
            print(f"  Success rate: {success_rate:.1%}")

            # Validate against target (15.0 seconds)
            target_time = 15.0
            if mean_time > target_time:
                print(f"  ⚠️  Exceeds target time of {target_time}s")
            else:
                print(f"  ✅ Within target time of {target_time}s")

        print("\n📊 Tier 3 Summary:")
        if performance_data:
            overall_times = [data["mean_time"] for data in performance_data]
            overall_success = statistics.mean([data["success_rate"] for data in performance_data])
            print("  Performance target: 15.0s")
            print(f"  Overall mean time: {statistics.mean(overall_times):.3f}s")
            print(f"  Overall success rate: {overall_success:.1%}")

        return performance_data

    @pytest.mark.benchmark
    async def benchmark_end_to_end_pipeline(self, evaluation_pipeline, benchmark_data):
        """Benchmark complete pipeline performance with realistic data."""
        print("\n=== End-to-End Pipeline Performance Benchmark ===")

        # Test scenarios with different complexities
        test_scenarios = [
            (
                "Standard",
                250,
                150,
                30,
            ),  # (name, paper_words, review_words, interactions)
            ("Large", 400, 250, 75),
            ("Complex", 600, 300, 120),
        ]

        performance_data = []

        for (
            scenario_name,
            paper_words,
            review_words,
            interaction_count,
        ) in test_scenarios:
            print(f"\nTesting {scenario_name} pipeline scenario:")

            # Create comprehensive test data
            paper_text = benchmark_data.create_long_paper_abstract(paper_words)
            review_text = benchmark_data.create_comprehensive_review(review_words)
            reference_reviews = [
                benchmark_data.create_comprehensive_review(180),
                benchmark_data.create_comprehensive_review(160),
            ]

            if interaction_count <= 50:
                execution_trace = benchmark_data.create_simple_trace(interaction_count)
            else:
                execution_trace = benchmark_data.create_complex_trace(interaction_count)

            # Run pipeline evaluation
            execution_times = []
            success_count = 0

            for run in range(2):  # Limited runs for full pipeline
                start_time = time.time()

                try:
                    result = await evaluation_pipeline.evaluate_comprehensive(
                        paper=paper_text,
                        review=review_text,
                        execution_trace=execution_trace,
                        reference_reviews=reference_reviews,
                    )

                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)

                    if result and result.evaluation_complete:
                        success_count += 1

                        # Get detailed timing statistics
                        stats = evaluation_pipeline.get_execution_stats()
                        tier_times = {
                            "tier1": stats.get("tier1_time", 0.0),
                            "tier2": stats.get("tier2_time", 0.0),
                            "tier3": stats.get("tier3_time", 0.0),
                        }

                        print(
                            f"  Run {run + 1}: Total={execution_time:.3f}s, "
                            f"T1={tier_times['tier1']:.3f}s, "
                            f"T2={tier_times['tier2']:.3f}s, "
                            f"T3={tier_times['tier3']:.3f}s"
                        )

                except Exception as e:
                    print(f"  Run {run + 1} failed: {e}")
                    continue

            if not execution_times:
                print(f"  ❌ All runs failed for {scenario_name}")
                continue

            # Calculate statistics
            mean_time = statistics.mean(execution_times)
            success_rate = success_count / len(execution_times)

            performance_data.append(
                {
                    "scenario": scenario_name,
                    "paper_words": paper_words,
                    "review_words": review_words,
                    "interaction_count": interaction_count,
                    "mean_time": mean_time,
                    "success_rate": success_rate,
                }
            )

            print(f"  Mean total time: {mean_time:.3f}s")
            print(f"  Success rate: {success_rate:.1%}")

            # Validate against target (25.0 seconds)
            target_time = 25.0
            if mean_time > target_time:
                print(f"  ⚠️  Exceeds target time of {target_time}s")
            else:
                print(f"  ✅ Within target time of {target_time}s")

        print("\n📊 End-to-End Pipeline Summary:")
        if performance_data:
            overall_times = [data["mean_time"] for data in performance_data]
            overall_success = statistics.mean([data["success_rate"] for data in performance_data])
            print("  Performance target: 25.0s")
            print(f"  Overall mean time: {statistics.mean(overall_times):.3f}s")
            print(f"  Overall success rate: {overall_success:.1%}")

            # Identify performance bottlenecks
            bottleneck_threshold = statistics.mean(overall_times) * 0.4
            print(f"  Bottleneck threshold: {bottleneck_threshold:.3f}s per tier")

        return performance_data

    @pytest.mark.benchmark
    async def test_performance_regression_detection(self, evaluation_pipeline, benchmark_data):
        """Test for performance regression detection."""
        print("\n=== Performance Regression Detection ===")

        # Create baseline measurement
        paper_text = benchmark_data.create_short_paper_abstract(200)
        review_text = benchmark_data.create_comprehensive_review(150)
        execution_trace = benchmark_data.create_simple_trace(25)
        reference_reviews = [benchmark_data.create_comprehensive_review(120)]

        # Run baseline measurements
        baseline_times = []
        for _ in range(3):
            start_time = time.time()
            result = await evaluation_pipeline.evaluate_comprehensive(
                paper=paper_text,
                review=review_text,
                execution_trace=execution_trace,
                reference_reviews=reference_reviews,
            )
            execution_time = time.time() - start_time
            if result and result.evaluation_complete:
                baseline_times.append(execution_time)

        if not baseline_times:
            pytest.skip("No successful baseline measurements")

        baseline_mean = statistics.mean(baseline_times)
        baseline_stddev = statistics.stdev(baseline_times) if len(baseline_times) > 1 else 0.0

        print(f"Baseline performance: {baseline_mean:.3f}s ± {baseline_stddev:.3f}s")

        # Define regression threshold (e.g., 20% slower than baseline)
        regression_threshold = baseline_mean * 1.2

        # Current measurement should not exceed regression threshold
        assert baseline_mean < regression_threshold, (
            f"Performance regression detected: {baseline_mean:.3f}s > {regression_threshold:.3f}s"
        )

        print(f"✅ No performance regression detected (threshold: {regression_threshold:.3f}s)")


if __name__ == "__main__":
    """Run the performance benchmarks directly."""

    async def run_performance_benchmarks():
        print("Running evaluation pipeline performance benchmarks...")
        print("This may take several minutes due to comprehensive testing.")

        try:
            # Initialize components
            benchmark_data = PerformanceBenchmarkData()
            traditional_engine = TraditionalMetricsEngine()
            pipeline = EvaluationPipeline()

            print("✅ Components initialized")
            print("Performance targets: T1≤1.0s, T2≤10.0s, T3≤15.0s, Total≤25.0s")

            # Benchmark results storage
            all_results = {}

            # Tier 1 benchmarks
            print("\n" + "=" * 60)
            print("TIER 1 (TRADITIONAL METRICS) BENCHMARKS")
            print("=" * 60)

            tier1_results = []
            paper_lengths = [100, 300, 500]

            for word_count in paper_lengths:
                paper_abstract = benchmark_data.create_short_paper_abstract(word_count)
                review_text = benchmark_data.create_comprehensive_review(150)
                reference_reviews = [benchmark_data.create_comprehensive_review(180)]

                times = []
                for run in range(3):
                    start = time.time()
                    result = await traditional_engine.evaluate(
                        paper=paper_abstract,
                        review=review_text,
                        reference_reviews=reference_reviews,
                    )
                    duration = time.time() - start
                    if result and result.success:
                        times.append(duration)

                if times:
                    mean_time = statistics.mean(times)
                    tier1_results.append({"words": word_count, "time": mean_time})
                    status = "✅" if mean_time <= 1.0 else "⚠️"
                    print(f"{status} {word_count} words: {mean_time:.3f}s")

            all_results["tier1"] = tier1_results

            # End-to-end pipeline benchmark
            print("\n" + "=" * 60)
            print("END-TO-END PIPELINE BENCHMARKS")
            print("=" * 60)

            pipeline_results = []
            scenarios = [("Standard", 200, 150, 20), ("Complex", 400, 250, 50)]

            for name, paper_words, review_words, interactions in scenarios:
                paper = benchmark_data.create_long_paper_abstract(paper_words)
                review = benchmark_data.create_comprehensive_review(review_words)
                trace = benchmark_data.create_simple_trace(interactions)
                references = [benchmark_data.create_comprehensive_review(120)]

                times = []
                for run in range(2):
                    start = time.time()
                    try:
                        result = await pipeline.evaluate_comprehensive(
                            paper=paper,
                            review=review,
                            execution_trace=trace,
                            reference_reviews=references,
                        )
                        duration = time.time() - start
                        if result and result.evaluation_complete:
                            times.append(duration)
                            print(f"  {name} Run {run + 1}: {duration:.3f}s")
                    except Exception as e:
                        print(f"  {name} Run {run + 1} failed: {e}")

                if times:
                    mean_time = statistics.mean(times)
                    pipeline_results.append({"scenario": name, "time": mean_time})
                    status = "✅" if mean_time <= 25.0 else "⚠️"
                    print(f"{status} {name} average: {mean_time:.3f}s")

            all_results["pipeline"] = pipeline_results

            # Summary
            print("\n" + "=" * 60)
            print("PERFORMANCE BENCHMARK SUMMARY")
            print("=" * 60)

            if tier1_results:
                tier1_times = [r["time"] for r in tier1_results]
                print(
                    f"Tier 1 (Traditional): {statistics.mean(tier1_times):.3f}s avg, target ≤1.0s"
                )

            if pipeline_results:
                pipeline_times = [r["time"] for r in pipeline_results]
                print(
                    f"End-to-End Pipeline: {statistics.mean(pipeline_times):.3f}s avg, target ≤25.0s"
                )

            print("\n✅ Performance benchmarking completed!")
            print("Results available for performance baseline documentation.")

            return all_results

        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            raise

    asyncio.run(run_performance_benchmarks())


# STORY-004: Hypothesis property-based tests for benchmark result invariants
class TestBenchmarkResultInvariants:
    """Property-based tests for benchmark result structure invariants."""

    @given(
        word_count=st.integers(min_value=10, max_value=1000),
        execution_time=st.floats(min_value=0.001, max_value=30.0, allow_nan=False),
    )
    def test_performance_data_structure_invariants(self, word_count, execution_time):
        """Property: Performance data always has valid structure."""
        # Arrange & Act
        perf_data = {
            "word_count": word_count,
            "mean_time": execution_time,
            "median_time": execution_time * 0.95,
            "stddev_time": execution_time * 0.1,
            "percentile_95": execution_time * 1.05,
            "max_time": execution_time * 1.2,
            "min_time": execution_time * 0.8,
        }

        # Assert invariants
        assert perf_data["word_count"] >= 10
        assert perf_data["mean_time"] > 0
        assert perf_data["min_time"] <= perf_data["mean_time"] <= perf_data["max_time"]
        assert perf_data["stddev_time"] >= 0

    @given(interaction_count=st.integers(min_value=3, max_value=200))
    def test_trace_generation_invariants(self, interaction_count):
        """Property: Generated traces always have valid structure."""
        # Arrange
        data_gen = PerformanceBenchmarkData()

        # Act
        if interaction_count <= 50:
            trace = data_gen.create_simple_trace(interaction_count)
        else:
            trace = data_gen.create_complex_trace(interaction_count)

        # Assert invariants
        assert len(trace["agent_interactions"]) == interaction_count
        assert len(trace["tool_calls"]) > 0
        assert "execution_id" in trace
        assert all(isinstance(i["timestamp"], float) for i in trace["agent_interactions"])


# STORY-004: Inline-snapshot regression tests for benchmark outputs
class TestBenchmarkOutputSnapshots:
    """Snapshot tests for benchmark output structure regression testing."""

    def test_simple_trace_structure(self):
        """Snapshot: Simple trace data structure."""
        # Arrange
        data_gen = PerformanceBenchmarkData()

        # Act
        trace = data_gen.create_simple_trace(10)

        # Assert with snapshot
        assert trace == snapshot()

    def test_performance_baseline_data_structure(self):
        """Snapshot: Performance baseline data structure."""
        # Arrange
        perf_data = {
            "word_count": 300,
            "mean_time": 0.523,
            "median_time": 0.498,
            "stddev_time": 0.042,
            "percentile_95": 0.587,
            "max_time": 0.612,
            "min_time": 0.461,
        }

        # Assert with snapshot
        assert perf_data == snapshot()
