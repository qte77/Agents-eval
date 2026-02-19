"""Report generator for evaluation result summarization.

This module produces structured Markdown reports from CompositeResult objects.
Reports include an executive summary, per-tier score breakdown, weakness
identification, and actionable suggestions sourced from the SuggestionEngine.

Report structure:
    1. Executive Summary — composite score, recommendation, timestamp
    2. Tier Score Breakdown — T1/T2/T3 scores with weights
    3. Weaknesses & Suggestions — severity-ordered list from SuggestionEngine

Example:
    >>> from app.reports.report_generator import generate_report, save_report
    >>> md = generate_report(composite_result)
    >>> save_report(md, Path("results/reports/latest.md"))
"""

from pathlib import Path

from app.data_models.evaluation_models import CompositeResult
from app.data_models.report_models import Suggestion, SuggestionSeverity
from app.reports.suggestion_engine import SuggestionEngine


def generate_report(
    result: CompositeResult,
    suggestions: list[Suggestion] | None = None,
) -> str:
    """Generate a Markdown report from a CompositeResult.

    Args:
        result: Composite evaluation result to report on.
        suggestions: Optional pre-computed suggestion list.  When provided,
            skips the SuggestionEngine and uses these directly.

    Returns:
        Markdown-formatted report string.
    """
    # S8-F6.1: build suggestions if not provided by caller
    if suggestions is None:
        engine = SuggestionEngine(no_llm_suggestions=True)
        suggestions = engine.generate(result)

    sections: list[str] = [
        _render_executive_summary(result),
        _render_tier_breakdown(result),
        _render_weaknesses(suggestions),
    ]
    return "\n\n".join(sections) + "\n"


def save_report(markdown: str, output_path: Path) -> None:
    """Write a Markdown report string to disk.

    Args:
        markdown: Report content as a Markdown string.
        output_path: Destination file path.  Parent directories are created
            automatically if they do not exist.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


# ---------------------------------------------------------------------------
# Internal section renderers
# ---------------------------------------------------------------------------


def _render_executive_summary(result: CompositeResult) -> str:
    """Render the Executive Summary section.

    Args:
        result: Composite evaluation result.

    Returns:
        Markdown string for the executive summary section.
    """
    rec = result.recommendation.replace("_", " ")
    timestamp = result.timestamp or "N/A"

    lines = [
        "# Evaluation Report",
        "",
        "## Executive Summary",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| **Composite Score** | {result.composite_score:.2f} |",
        f"| **Recommendation** | {rec} |",
        f"| **Timestamp** | {timestamp} |",
        f"| **Config Version** | {result.config_version} |",
        f"| **All Tiers Complete** | {'Yes' if result.evaluation_complete else 'No'} |",
    ]
    return "\n".join(lines)


def _render_tier_breakdown(result: CompositeResult) -> str:
    """Render the per-tier score breakdown section.

    Args:
        result: Composite evaluation result.

    Returns:
        Markdown string for the tier breakdown section.
    """
    lines = [
        "## Tier Score Breakdown",
        "",
        "| Tier | Score | Weight |",
        "|------|-------|--------|",
    ]

    weights = result.weights_used or {}

    # Tier 1 — always present
    t1_weight = weights.get("tier1", weights.get("t1", "—"))
    t1_weight_str = f"{t1_weight:.2f}" if isinstance(t1_weight, float) else str(t1_weight)
    lines.append(f"| Tier 1 — Traditional Metrics | {result.tier1_score:.2f} | {t1_weight_str} |")

    # Tier 2 — optional
    t2_weight = weights.get("tier2", weights.get("t2", "—"))
    t2_weight_str = f"{t2_weight:.2f}" if isinstance(t2_weight, float) else str(t2_weight)
    if result.tier2_score is not None:
        lines.append(f"| Tier 2 — LLM-as-Judge | {result.tier2_score:.2f} | {t2_weight_str} |")
    else:
        lines.append(f"| Tier 2 — LLM-as-Judge | N/A (not run) | {t2_weight_str} |")

    # Tier 3 — always present
    t3_weight = weights.get("tier3", weights.get("t3", "—"))
    t3_weight_str = f"{t3_weight:.2f}" if isinstance(t3_weight, float) else str(t3_weight)
    lines.append(f"| Tier 3 — Graph Analysis | {result.tier3_score:.2f} | {t3_weight_str} |")

    return "\n".join(lines)


def _render_weaknesses(suggestions: list[Suggestion]) -> str:
    """Render the weaknesses and actionable suggestions section.

    Args:
        suggestions: List of Suggestion objects ordered by severity.

    Returns:
        Markdown string for the weaknesses section.
    """
    lines = [
        "## Weaknesses & Suggestions",
        "",
    ]

    criticals = [s for s in suggestions if s.severity == SuggestionSeverity.CRITICAL]
    warnings = [s for s in suggestions if s.severity == SuggestionSeverity.WARNING]
    infos = [s for s in suggestions if s.severity == SuggestionSeverity.INFO]

    if not criticals and not warnings and not infos:
        lines.append(
            "No significant weaknesses detected. "
            "All evaluated metrics are within acceptable bounds."
        )
        return "\n".join(lines)

    # Render each severity group
    for severity_label, group in [
        ("Critical", criticals),
        ("Warning", warnings),
        ("Info", infos),
    ]:
        if not group:
            continue
        lines.append(f"### {severity_label}")
        lines.append("")
        for s in group:
            lines.append(f"- **{s.metric}** (Tier {s.tier}): {s.message}")
            lines.append(f"  - *Action*: {s.action}")
        lines.append("")

    return "\n".join(lines).rstrip()
