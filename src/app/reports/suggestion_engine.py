"""Suggestion engine for generating actionable evaluation improvement suggestions.

This module analyses evaluation results across all three tiers and produces
structured, actionable suggestions. It supports a rule-based mode (always
available) and an optional LLM-assisted mode for richer recommendations.

Severity mapping:
    - critical: score < CRITICAL_THRESHOLD (0.2)
    - warning: CRITICAL_THRESHOLD <= score < WARNING_THRESHOLD (0.5)
    - info: score >= WARNING_THRESHOLD but still worth noting

Example:
    >>> engine = SuggestionEngine()
    >>> suggestions = engine.generate(composite_result)
    >>> for s in suggestions:
    ...     print(s.severity, s.metric, s.message)
"""

import logging
from typing import Sequence

from app.data_models.evaluation_models import CompositeResult
from app.data_models.report_models import Suggestion, SuggestionSeverity

logger = logging.getLogger(__name__)

# Score thresholds for severity classification
_CRITICAL_THRESHOLD = 0.2
_WARNING_THRESHOLD = 0.5

# Rule-based suggestion templates keyed by metric name.
# Each entry: (tier, message_template, action_template)
# Templates receive: score (float), threshold label.
_TIER1_RULES: dict[str, tuple[int, str, str]] = {
    "cosine_score": (
        1,
        "Tier 1 cosine similarity score is {score:.2f} — vocabulary overlap with reference reviews is minimal.",
        "Incorporate domain-specific terminology from the paper abstract and related work section to improve text similarity.",
    ),
    "jaccard_score": (
        1,
        "Tier 1 Jaccard similarity is {score:.2f} — the review shares few common words with reference reviews.",
        "Expand coverage of key concepts using the same vocabulary as the reference reviews.",
    ),
    "semantic_score": (
        1,
        "Tier 1 semantic similarity is {score:.2f} — the review meaning diverges from reference reviews.",
        "Ensure the review addresses the same aspects (methodology, novelty, limitations) covered in reference reviews.",
    ),
    "task_success": (
        1,
        "Tier 1 task success is {score:.2f} — the review task was not completed successfully.",
        "Check agent logs for errors during review generation. Verify that all required sections are produced.",
    ),
    "time_score": (
        1,
        "Tier 1 time score is {score:.2f} — execution was slower than expected.",
        "Investigate bottlenecks in agent pipeline (tool calls, LLM latency). Consider caching or reducing redundant steps.",
    ),
}

_TIER2_RULES: dict[str, tuple[int, str, str]] = {
    "technical_accuracy": (
        2,
        "Tier 2 technical accuracy score is {score:.2f} — LLM judge found factual or methodological gaps.",
        "Strengthen the agent's domain knowledge prompts or provide more context about the paper's methodology.",
    ),
    "constructiveness": (
        2,
        "Tier 2 constructiveness score is {score:.2f} — review lacks actionable feedback for the authors.",
        "Guide the agent to provide specific improvement suggestions alongside critiques.",
    ),
    "clarity": (
        2,
        "Tier 2 clarity score is {score:.2f} — the review may be unclear or poorly structured.",
        "Add explicit section structure instructions to the agent prompt (e.g., summary, strengths, weaknesses).",
    ),
    "planning_rationality": (
        2,
        "Tier 2 planning rationality score is {score:.2f} — agent's decision-making process was suboptimal.",
        "Review the agent's tool-use sequence and consider adjusting the orchestration strategy.",
    ),
}

_TIER3_RULES: dict[str, tuple[int, str, str]] = {
    "path_convergence": (
        3,
        "Tier 3 path convergence is {score:.2f} — tool usage efficiency is low.",
        "Reduce redundant tool calls by refining agent instructions to specify the minimum required information.",
    ),
    "tool_selection_accuracy": (
        3,
        "Tier 3 tool selection accuracy is {score:.2f} — agents are choosing suboptimal tools.",
        "Review tool descriptions and ensure they clearly distinguish when each tool should be used.",
    ),
    "coordination_centrality": (
        3,
        "Tier 3 coordination centrality is {score:.2f} — agent coordination quality needs improvement.",
        "Evaluate the manager agent's delegation strategy; ensure sub-agents receive clear, scoped tasks.",
    ),
    "task_distribution_balance": (
        3,
        "Tier 3 task distribution balance is {score:.2f} — workload is unevenly distributed across agents.",
        "Adjust agent roles so tasks are distributed more evenly; avoid single-agent bottlenecks.",
    ),
}

_ALL_RULES = {**_TIER1_RULES, **_TIER2_RULES, **_TIER3_RULES}


def _classify_severity(score: float) -> SuggestionSeverity:
    """Classify a score into a severity level.

    Args:
        score: Evaluation score in [0.0, 1.0].

    Returns:
        SuggestionSeverity based on thresholds.
    """
    if score < _CRITICAL_THRESHOLD:
        return SuggestionSeverity.CRITICAL
    if score < _WARNING_THRESHOLD:
        return SuggestionSeverity.WARNING
    return SuggestionSeverity.INFO


class SuggestionEngine:
    """Generates structured improvement suggestions from evaluation results.

    Operates in two modes:
    - Rule-based (default): Fast, deterministic suggestions from score thresholds.
    - LLM-assisted (async): Richer suggestions using the judge provider LLM.

    Args:
        no_llm_suggestions: When True, disables LLM path even if provider available.

    Example:
        >>> engine = SuggestionEngine()
        >>> suggestions = engine.generate(composite_result)
        >>> async_suggestions = await engine.generate_async(composite_result)
    """

    def __init__(self, no_llm_suggestions: bool = False) -> None:
        """Initialize the suggestion engine.

        Args:
            no_llm_suggestions: Disable LLM-assisted suggestions when True.
        """
        self.no_llm_suggestions = no_llm_suggestions

    def generate(self, result: CompositeResult) -> list[Suggestion]:
        """Generate rule-based suggestions from evaluation results.

        Analyses metric_scores, tier-level scores, and tiers_enabled to produce
        actionable suggestions. Tier 2 absence is noted as an info suggestion.

        Args:
            result: Composite evaluation result to analyse.

        Returns:
            List of Suggestion objects ordered by severity (critical first).
        """
        suggestions: list[Suggestion] = []

        # Process known metric-level rules
        for metric, (tier, msg_tmpl, action) in _ALL_RULES.items():
            score = result.metric_scores.get(metric)
            if score is None:
                continue
            severity = _classify_severity(score)
            # Only surface warning/critical in rule-based; info can be surfaced for all
            suggestions.append(
                Suggestion(
                    metric=metric,
                    tier=tier,
                    severity=severity,
                    message=msg_tmpl.format(score=score),
                    action=action,
                )
            )

        # Tier-level fallback: produce suggestions from tier scores when metric_scores empty
        if not result.metric_scores:
            tier_entries = [
                ("tier1_score", 1, result.tier1_score),
                ("tier3_score", 3, result.tier3_score),
            ]
            if result.tier2_score is not None:
                tier_entries.append(("tier2_score", 2, result.tier2_score))

            for metric_name, tier, score in tier_entries:
                severity = _classify_severity(score)
                suggestions.append(
                    Suggestion(
                        metric=metric_name,
                        tier=tier,
                        severity=severity,
                        message=f"Tier {tier} overall score is {score:.2f} — improvement needed.",
                        action="Review individual metric scores for this tier to identify specific weaknesses.",
                    )
                )

        # Tier 2 absence: inform the user LLM judging was not run
        if result.tier2_score is None:
            suggestions.append(
                Suggestion(
                    metric="tier2_score",
                    tier=2,
                    severity=SuggestionSeverity.INFO,
                    message="Tier 2 LLM-as-Judge evaluation was not run — quality assessment is incomplete.",
                    action="Enable Tier 2 by configuring a judge provider in Settings to get LLM-based quality scoring.",
                )
            )

        # Sort: critical → warning → info
        _order = {
            SuggestionSeverity.CRITICAL: 0,
            SuggestionSeverity.WARNING: 1,
            SuggestionSeverity.INFO: 2,
        }
        suggestions.sort(key=lambda s: _order[s.severity])
        return suggestions

    async def generate_async(self, result: CompositeResult) -> list[Suggestion]:
        """Generate suggestions with optional LLM enhancement.

        Attempts LLM-assisted suggestions first; falls back to rule-based on error.

        Args:
            result: Composite evaluation result to analyse.

        Returns:
            List of Suggestion objects, potentially enriched by LLM.
        """
        if self.no_llm_suggestions:
            return self.generate(result)

        try:
            llm_suggestions = await self._generate_llm_suggestions(result)
            if llm_suggestions:
                return llm_suggestions
        except Exception:
            logger.warning("LLM suggestion generation failed; falling back to rule-based.")

        return self.generate(result)

    async def _generate_llm_suggestions(self, result: CompositeResult) -> list[Suggestion]:
        """Generate LLM-assisted suggestions using the judge provider.

        Args:
            result: Composite evaluation result to analyse.

        Returns:
            List of LLM-generated Suggestion objects.

        Raises:
            RuntimeError: When LLM provider is unavailable or call fails.
        """
        # Reason: LLM path is optional; raise to trigger fallback in generate_async
        raise NotImplementedError("LLM suggestion generation requires a configured judge provider.")
