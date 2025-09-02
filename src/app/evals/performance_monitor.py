"""
Performance monitoring and analytics for evaluation pipeline.

Handles execution statistics, bottleneck detection, performance warnings,
and failure tracking for the three-tier evaluation system.
"""

import time
from typing import Any

from app.utils.log import logger


class PerformanceMonitor:
    """
    Performance monitoring and analytics for evaluation pipelines.

    Tracks execution times, detects bottlenecks, records failures,
    and provides performance insights for optimization.
    """

    def __init__(self, performance_targets: dict[str, float]):
        """Initialize performance monitor with targets.

        Args:
            performance_targets: Dictionary of performance targets (e.g., tier timeouts)
        """
        self.performance_targets = performance_targets.copy()
        self.execution_stats: dict[str, Any] = self._initialize_stats()

    def _initialize_stats(self) -> dict[str, Any]:
        """Initialize execution statistics structure.

        Returns:
            Dictionary with default statistics structure
        """
        return {
            "tier1_time": 0.0,
            "tier2_time": 0.0,
            "tier3_time": 0.0,
            "total_time": 0.0,
            "tiers_executed": [],
            "fallback_used": False,
            "tier_failures": [],
            "performance_warnings": [],
            "bottlenecks_detected": [],
        }

    def reset_stats(self) -> None:
        """Reset execution statistics for new evaluation."""
        self.execution_stats = self._initialize_stats()

    def record_tier_execution(self, tier: int, duration: float) -> None:
        """Record successful tier execution time.

        Args:
            tier: Tier number (1, 2, or 3)
            duration: Execution duration in seconds
        """
        tier_key = f"tier{tier}"
        self.execution_stats[tier_key] = duration

        if tier not in self.execution_stats["tiers_executed"]:
            self.execution_stats["tiers_executed"].append(tier)

        logger.debug(f"Recorded tier {tier} execution: {duration:.3f}s")

    def record_tier_failure(self, tier: int, failure_type: str, execution_time: float, error_msg: str) -> None:
        """Record tier failure details for monitoring and analysis.

        Args:
            tier: Tier number that failed (0 for pipeline-level failures)
            failure_type: Type of failure (timeout, error)
            execution_time: Time spent before failure
            error_msg: Error message
        """
        failure_record = {
            "tier": tier,
            "failure_type": failure_type,
            "execution_time": execution_time,
            "error_msg": error_msg,
            "timestamp": time.time(),
        }

        self.execution_stats["tier_failures"].append(failure_record)

        logger.debug(f"Recorded tier {tier} failure: {failure_type} after {execution_time:.2f}s")

    def record_fallback_usage(self, fallback_used: bool) -> None:
        """Record whether fallback strategy was used.

        Args:
            fallback_used: Whether fallback strategy was applied
        """
        self.execution_stats["fallback_used"] = fallback_used
        logger.debug(f"Fallback strategy used: {fallback_used}")

    def finalize_execution(self, total_time: float) -> None:
        """Finalize execution statistics and perform analysis.

        Args:
            total_time: Total pipeline execution time
        """
        self.execution_stats["total_time"] = total_time
        self._analyze_performance(total_time)

    def _analyze_performance(self, total_time: float) -> None:
        """Analyze pipeline performance and detect bottlenecks.

        Args:
            total_time: Total pipeline execution time
        """
        tier_times = {
            "tier1": self.execution_stats["tier1_time"],
            "tier2": self.execution_stats["tier2_time"],
            "tier3": self.execution_stats["tier3_time"],
        }

        # Identify bottlenecks (tiers taking >40% of total time)
        bottleneck_threshold = total_time * 0.4
        bottlenecks = []

        for tier, time_taken in tier_times.items():
            if time_taken > bottleneck_threshold and time_taken > 0:
                bottlenecks.append(
                    {
                        "tier": tier,
                        "time": time_taken,
                        "percentage": (time_taken / total_time) * 100,
                    }
                )

        if bottlenecks:
            self.execution_stats["bottlenecks_detected"] = bottlenecks
            for bottleneck in bottlenecks:
                logger.warning(
                    f"Performance bottleneck detected: {bottleneck['tier']} took "
                    f"{bottleneck['time']:.2f}s "
                    f"({bottleneck['percentage']:.1f}% of total time)"
                )

        # Check individual tier targets
        for tier_num in range(1, 4):
            tier_key = f"tier{tier_num}"
            target_key = f"tier{tier_num}_max_seconds"

            if target_key in self.performance_targets and tier_times[tier_key] > 0:
                target_time = self.performance_targets[target_key]
                actual_time = tier_times[tier_key]

                if actual_time > target_time:
                    warning_msg = f"Tier {tier_num} exceeded target: {actual_time:.2f}s > {target_time}s"
                    self._record_performance_warning(f"tier{tier_num}_time_exceeded", warning_msg, actual_time)

        # Check total time target
        if "total_max_seconds" in self.performance_targets:
            total_target = self.performance_targets["total_max_seconds"]
            if total_time > total_target:
                warning_msg = f"Pipeline exceeded time target: {total_time:.2f}s > {total_target}s"
                self._record_performance_warning("total_time_exceeded", warning_msg, total_time)
                logger.warning(warning_msg)

    def _record_performance_warning(self, warning_type: str, message: str, value: float) -> None:
        """Record performance warning for monitoring.

        Args:
            warning_type: Type of warning
            message: Warning message
            value: Associated numeric value
        """
        warning_record = {
            "type": warning_type,
            "message": message,
            "value": value,
            "timestamp": time.time(),
        }

        self.execution_stats["performance_warnings"].append(warning_record)

    def get_execution_stats(self) -> dict[str, Any]:
        """Get detailed execution statistics from last pipeline run.

        Returns:
            Dictionary with timing and execution details including performance analysis
        """
        stats = self.execution_stats.copy()

        # Add derived performance metrics
        if stats["total_time"] > 0:
            stats["tier_time_percentages"] = {
                "tier1": (stats["tier1_time"] / stats["total_time"]) * 100,
                "tier2": (stats["tier2_time"] / stats["total_time"]) * 100,
                "tier3": (stats["tier3_time"] / stats["total_time"]) * 100,
            }

        return stats

    def get_performance_summary(self) -> str:
        """Get concise performance summary.

        Returns:
            Performance summary string
        """
        bottlenecks = len(self.execution_stats.get("bottlenecks_detected", []))
        warnings = len(self.execution_stats.get("performance_warnings", []))
        failures = len(self.execution_stats.get("tier_failures", []))

        return f"bottlenecks={bottlenecks}, warnings={warnings}, failures={failures}"

    def has_performance_issues(self) -> bool:
        """Check if there are any performance issues detected.

        Returns:
            True if bottlenecks or warnings were detected
        """
        return (
            len(self.execution_stats.get("bottlenecks_detected", [])) > 0
            or len(self.execution_stats.get("performance_warnings", [])) > 0
        )

    def get_bottlenecks(self) -> list[dict[str, Any]]:
        """Get detected performance bottlenecks.

        Returns:
            List of bottleneck information dictionaries
        """
        return self.execution_stats.get("bottlenecks_detected", [])

    def get_warnings(self) -> list[dict[str, Any]]:
        """Get performance warnings.

        Returns:
            List of performance warning dictionaries
        """
        return self.execution_stats.get("performance_warnings", [])

    def get_failures(self) -> list[dict[str, Any]]:
        """Get tier failure records.

        Returns:
            List of tier failure dictionaries
        """
        return self.execution_stats.get("tier_failures", [])
