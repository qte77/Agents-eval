"""Data models for evaluation report generation.

This module provides Pydantic models for structured report output including
suggestion severity levels and individual suggestion records.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class SuggestionSeverity(StrEnum):
    """Severity level for evaluation suggestions.

    Attributes:
        CRITICAL: Score below critical threshold (< 0.2); immediate action required.
        WARNING: Score below average (< 0.5); improvement recommended.
        INFO: Improvement opportunity; score acceptable but can be enhanced.
    """

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Suggestion(BaseModel):
    """A single actionable suggestion derived from evaluation results.

    Each suggestion is grounded in a specific metric and tier, with a severity
    level indicating urgency. The action field provides concrete guidance.

    Example:
        >>> s = Suggestion(
        ...     metric="cosine_score",
        ...     tier=1,
        ...     severity=SuggestionSeverity.CRITICAL,
        ...     message="Tier 1 cosine score very low (0.08) — vocabulary overlap minimal.",
        ...     action="Incorporate domain-specific terminology from the paper abstract.",
        ... )
    """

    metric: str = Field(
        description="Metric name that triggered this suggestion (e.g., 'cosine_score')"
    )
    tier: int = Field(
        ge=1, le=3, description="Evaluation tier (1=Traditional, 2=LLM Judge, 3=Graph)"
    )
    severity: SuggestionSeverity = Field(description="Severity level: critical, warning, or info")
    message: str = Field(
        description="Human-readable description of the issue referencing the metric and score"
    )
    action: str = Field(description="Concrete, actionable recommendation to address the issue")
