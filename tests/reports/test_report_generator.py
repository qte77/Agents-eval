"""Tests for report_generator module.

Covers:
- Executive summary section generation
- Per-tier breakdown (T1/T2/T3)
- Weakness identification based on thresholds
- Actionable suggestions sourced from SuggestionEngine
- Markdown file writing to output path
- --generate-report flag incompatibility with --skip-eval
"""

import re
import sys
from pathlib import Path

import pytest

from app.data_models.evaluation_models import CompositeResult
from app.data_models.report_models import Suggestion, SuggestionSeverity


def _make_result(
    composite_score: float = 0.72,
    recommendation: str = "weak_accept",
    tier1_score: float = 0.80,
    tier2_score: float | None = 0.65,
    tier3_score: float = 0.60,
    metric_scores: dict | None = None,
    weights_used: dict | None = None,
) -> CompositeResult:
    """Build a minimal CompositeResult for test use."""
    if metric_scores is None:
        metric_scores = {
            "cosine_score": 0.75,
            "jaccard_score": 0.65,
            "semantic_score": 0.80,
            "task_success": 1.0,
            "time_score": 0.70,
        }
    if weights_used is None:
        weights_used = {"tier1": 0.4, "tier2": 0.4, "tier3": 0.2}
    return CompositeResult(
        composite_score=composite_score,
        recommendation=recommendation,
        recommendation_weight=0.2,
        metric_scores=metric_scores,
        tier1_score=tier1_score,
        tier2_score=tier2_score,
        tier3_score=tier3_score,
        evaluation_complete=True,
        weights_used=weights_used,
        timestamp="2026-01-01T00:00:00Z",
        config_version="1.0.0",
    )


# ---------------------------------------------------------------------------
# Markdown structure — executive summary
# ---------------------------------------------------------------------------


def test_report_contains_executive_summary() -> None:
    """Report must contain an Executive Summary heading."""
    from app.reports.report_generator import generate_report

    result = _make_result()
    md = generate_report(result)

    assert "Executive Summary" in md


def test_executive_summary_contains_composite_score() -> None:
    """Executive summary must embed the composite score."""
    from app.reports.report_generator import generate_report

    result = _make_result(composite_score=0.72)
    md = generate_report(result)

    assert "0.72" in md or "72" in md


def test_executive_summary_contains_recommendation() -> None:
    """Executive summary must embed the recommendation."""
    from app.reports.report_generator import generate_report

    result = _make_result(recommendation="weak_accept")
    md = generate_report(result)

    assert "weak_accept" in md.lower() or "weak accept" in md.lower()


def test_executive_summary_contains_timestamp() -> None:
    """Executive summary must include the evaluation timestamp."""
    from app.reports.report_generator import generate_report

    result = _make_result()
    md = generate_report(result)

    assert "2026-01-01" in md


# ---------------------------------------------------------------------------
# Per-tier breakdown section
# ---------------------------------------------------------------------------


def test_report_contains_tier_breakdown_heading() -> None:
    """Report must contain a tier breakdown section."""
    from app.reports.report_generator import generate_report

    result = _make_result()
    md = generate_report(result)

    assert "Tier" in md and ("Breakdown" in md or "Scores" in md or "Results" in md)


def test_tier_breakdown_shows_tier1_score() -> None:
    """Tier breakdown must display Tier 1 score."""
    from app.reports.report_generator import generate_report

    result = _make_result(tier1_score=0.80)
    md = generate_report(result)

    assert "0.80" in md or "80" in md


def test_tier_breakdown_shows_tier2_score_when_present() -> None:
    """Tier breakdown must display Tier 2 score when available."""
    from app.reports.report_generator import generate_report

    result = _make_result(tier2_score=0.65)
    md = generate_report(result)

    assert "0.65" in md or "65" in md


def test_tier_breakdown_shows_tier2_absent_when_none() -> None:
    """Tier breakdown must indicate Tier 2 was not run when tier2_score is None."""
    from app.reports.report_generator import generate_report

    result = _make_result(tier2_score=None)
    md = generate_report(result)

    assert "not run" in md.lower() or "skipped" in md.lower() or "n/a" in md.lower()


def test_tier_breakdown_shows_weights_when_present() -> None:
    """Tier breakdown includes weights_used when available."""
    from app.reports.report_generator import generate_report

    result = _make_result(weights_used={"tier1": 0.4, "tier2": 0.4, "tier3": 0.2})
    md = generate_report(result)

    assert "0.4" in md or "40%" in md


# ---------------------------------------------------------------------------
# Weakness identification
# ---------------------------------------------------------------------------


def test_report_contains_weakness_section() -> None:
    """Report must have a weakness / improvement section."""
    from app.reports.report_generator import generate_report

    result = _make_result()
    md = generate_report(result)

    assert "Weakness" in md or "Improvement" in md or "Suggestion" in md


def test_weakness_section_empty_when_all_scores_high() -> None:
    """No critical weaknesses when all metrics are high."""
    from app.reports.report_generator import generate_report

    result = _make_result(
        composite_score=0.95,
        tier1_score=0.95,
        tier2_score=0.95,
        tier3_score=0.95,
        metric_scores={
            "cosine_score": 0.95,
            "jaccard_score": 0.95,
            "semantic_score": 0.95,
            "task_success": 1.0,
            "time_score": 0.95,
        },
    )
    md = generate_report(result)

    assert "critical" not in md.lower()


def test_weakness_section_highlights_low_metric() -> None:
    """A very low metric score (< 0.2) must appear as critical in the report."""
    from app.reports.report_generator import generate_report

    result = _make_result(
        metric_scores={
            "cosine_score": 0.10,  # critical threshold
        }
    )
    md = generate_report(result)

    assert "critical" in md.lower() or "cosine" in md.lower()


# ---------------------------------------------------------------------------
# Suggestions integration (delegates to SuggestionEngine)
# ---------------------------------------------------------------------------


def test_report_integrates_suggestions() -> None:
    """generate_report() must include at least one suggestion for a weak result."""
    from app.reports.report_generator import generate_report

    result = _make_result(
        composite_score=0.45,
        tier1_score=0.40,
        metric_scores={"cosine_score": 0.10},
    )
    md = generate_report(result)

    assert "cosine" in md.lower() or "action" in md.lower() or "suggestion" in md.lower()


def test_report_accepts_precomputed_suggestions() -> None:
    """generate_report() should accept an optional suggestions list."""
    from app.reports.report_generator import generate_report

    result = _make_result()
    custom_suggestions: list[Suggestion] = [
        Suggestion(
            metric="cosine_score",
            tier=1,
            severity=SuggestionSeverity.WARNING,
            message="Custom message for test",
            action="Custom action for test",
        )
    ]
    md = generate_report(result, suggestions=custom_suggestions)

    assert "Custom message for test" in md


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------


def test_save_report_writes_markdown_file(tmp_path: Path) -> None:
    """save_report() must write the Markdown string to the given output path."""
    from app.reports.report_generator import generate_report, save_report

    result = _make_result()
    md = generate_report(result)
    output_file = tmp_path / "report.md"

    save_report(md, output_file)

    assert output_file.exists()
    assert output_file.read_text() == md


def test_save_report_creates_parent_dirs(tmp_path: Path) -> None:
    """save_report() must create intermediate directories if they don't exist."""
    from app.reports.report_generator import save_report

    md = "# Test"
    output_file = tmp_path / "nested" / "dir" / "report.md"

    save_report(md, output_file)

    assert output_file.exists()


# ---------------------------------------------------------------------------
# CLI flag: --generate-report
# ---------------------------------------------------------------------------


def _load_run_cli():  # type: ignore[no-untyped-def]
    """Import run_cli from src/, reloading to pick up latest state."""
    import importlib

    src_dir = str(Path(__file__).parents[2] / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    import run_cli  # type: ignore[import-not-found]

    importlib.reload(run_cli)
    return run_cli


def test_cli_has_generate_report_flag() -> None:
    """run_cli._parser must have --generate-report flag."""
    run_cli = _load_run_cli()

    parsed = run_cli.parse_args(["--generate-report"])
    assert parsed.get("generate_report") is True


def test_cli_generate_report_excluded_from_skip_eval() -> None:
    """When both --skip-eval and --generate-report are passed, the CLI should reject them."""
    run_cli = _load_run_cli()

    # Mutual exclusion implemented via argparse group raises SystemExit on conflict
    with pytest.raises(SystemExit):
        run_cli.parse_args(["--skip-eval", "--generate-report"])


# ---------------------------------------------------------------------------
# CLI flag: --no-llm-suggestions
# ---------------------------------------------------------------------------


def test_cli_has_no_llm_suggestions_flag() -> None:
    """run_cli._parser must have --no-llm-suggestions flag."""
    run_cli = _load_run_cli()

    parsed = run_cli.parse_args(["--no-llm-suggestions"])
    assert parsed.get("no_llm_suggestions") is True


# ---------------------------------------------------------------------------
# Report return type
# ---------------------------------------------------------------------------


def test_generate_report_returns_string() -> None:
    """generate_report() must return a non-empty str."""
    from app.reports.report_generator import generate_report

    result = _make_result()
    md = generate_report(result)

    assert isinstance(md, str)
    assert len(md) > 0


def test_report_is_valid_markdown_with_headings() -> None:
    """Report must contain at least one Markdown heading (#)."""
    from app.reports.report_generator import generate_report

    result = _make_result()
    md = generate_report(result)

    assert re.search(r"^#{1,3} ", md, re.MULTILINE) is not None
