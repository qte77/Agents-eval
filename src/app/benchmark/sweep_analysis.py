"""Statistical analysis for MAS composition sweep results.

This module provides functions to calculate statistics (mean, stddev, min, max)
across multiple sweep runs and generate summary reports in machine-readable
(JSON) and human-readable (Markdown) formats.
"""

import statistics

from pydantic import BaseModel

from app.benchmark.sweep_config import AgentComposition
from app.data_models.evaluation_models import CompositeResult


def calculate_statistics(scores: list[float]) -> dict[str, float]:
    """Calculate mean, stddev, min, max for a list of scores.

    Args:
        scores: List of numerical scores to analyze.

    Returns:
        dict[str, float]: Dictionary with keys 'mean', 'stddev', 'min', 'max'.

    Raises:
        ValueError: If scores list is empty.

    Example:
        >>> calculate_statistics([0.75, 0.80, 0.70])
        {'mean': 0.75, 'stddev': 0.05, 'min': 0.70, 'max': 0.80}
    """
    if not scores:
        raise ValueError("Cannot calculate statistics for empty scores list")

    return {
        "mean": statistics.mean(scores),
        "stddev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        "min": min(scores),
        "max": max(scores),
    }


class CompositionStats(BaseModel):
    """Statistical summary for a single agent composition.

    Aggregates metrics across all repetitions for one composition.
    """

    composition: AgentComposition
    overall_score_mean: float
    overall_score_stddev: float
    tier1_score_mean: float
    tier1_score_stddev: float
    tier2_score_mean: float
    tier2_score_stddev: float
    tier3_score_mean: float
    tier3_score_stddev: float
    confidence_mean: float
    confidence_stddev: float
    num_samples: int


class SweepAnalyzer:
    """Analyzer for sweep results.

    Groups results by composition and calculates per-composition statistics.
    """

    def __init__(self, results: list[tuple[AgentComposition, CompositeResult]]):
        """Initialize analyzer with sweep results.

        Args:
            results: List of (composition, result) tuples from sweep run.
        """
        self.results = results

    def analyze(self) -> list[CompositionStats]:
        """Analyze sweep results and calculate per-composition statistics.

        Groups results by composition and calculates mean/stddev for all metrics.

        Returns:
            list[CompositionStats]: Statistics for each unique composition.

        Example:
            >>> analyzer = SweepAnalyzer(results)
            >>> stats = analyzer.analyze()
            >>> len(stats)  # Number of unique compositions
            8
        """
        # Group results by composition
        grouped: dict[str, list[CompositeResult]] = {}
        composition_map: dict[str, AgentComposition] = {}

        for composition, result in self.results:
            key = composition.get_name()
            if key not in grouped:
                grouped[key] = []
                composition_map[key] = composition
            grouped[key].append(result)

        # Calculate statistics for each composition
        stats_list = []
        for key, results in grouped.items():
            overall_scores = [r.composite_score for r in results]
            tier1_scores = [r.tier1_score for r in results]
            # Reason: tier2_score is optional, filter out None values
            tier2_scores = [r.tier2_score for r in results if r.tier2_score is not None]
            tier3_scores = [r.tier3_score for r in results]
            # Reason: Use composite_score as proxy for confidence (not exposed in CompositeResult)
            confidences = [r.composite_score for r in results]

            overall_stats = calculate_statistics(overall_scores)
            tier1_stats = calculate_statistics(tier1_scores)
            tier2_stats = (
                calculate_statistics(tier2_scores)
                if tier2_scores
                else {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
            )
            tier3_stats = calculate_statistics(tier3_scores)
            confidence_stats = calculate_statistics(confidences)

            stats_list.append(
                CompositionStats(
                    composition=composition_map[key],
                    overall_score_mean=overall_stats["mean"],
                    overall_score_stddev=overall_stats["stddev"],
                    tier1_score_mean=tier1_stats["mean"],
                    tier1_score_stddev=tier1_stats["stddev"],
                    tier2_score_mean=tier2_stats["mean"],
                    tier2_score_stddev=tier2_stats["stddev"],
                    tier3_score_mean=tier3_stats["mean"],
                    tier3_score_stddev=tier3_stats["stddev"],
                    confidence_mean=confidence_stats["mean"],
                    confidence_stddev=confidence_stats["stddev"],
                    num_samples=len(results),
                )
            )

        return stats_list


def generate_markdown_summary(stats: list[CompositionStats]) -> str:
    """Generate human-readable Markdown summary table.

    Args:
        stats: List of composition statistics to summarize.

    Returns:
        str: Markdown-formatted table with mean ± stddev for all metrics.

    Example:
        >>> markdown = generate_markdown_summary(stats)
        >>> "| Composition" in markdown
        True
        >>> "Overall Score" in markdown
        True
    """
    lines = [
        "# MAS Composition Sweep Results",
        "",
        "| Composition | Overall Score | Tier 1 | Tier 2 | Tier 3 | Confidence | Samples |",
        "|-------------|---------------|---------|---------|---------|------------|---------|",
    ]

    for stat in stats:
        comp_name = stat.composition.get_name()
        overall = f"{stat.overall_score_mean:.3f} ± {stat.overall_score_stddev:.3f}"
        tier1 = f"{stat.tier1_score_mean:.3f} ± {stat.tier1_score_stddev:.3f}"
        tier2 = f"{stat.tier2_score_mean:.3f} ± {stat.tier2_score_stddev:.3f}"
        tier3 = f"{stat.tier3_score_mean:.3f} ± {stat.tier3_score_stddev:.3f}"
        confidence = f"{stat.confidence_mean:.3f} ± {stat.confidence_stddev:.3f}"
        samples = f"n={stat.num_samples}"

        lines.append(
            f"| {comp_name} | {overall} | {tier1} | {tier2} | {tier3} | {confidence} | {samples} |"
        )

    return "\n".join(lines)
