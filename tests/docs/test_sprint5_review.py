"""Tests for Sprint 5 code review documentation.

Verifies that the comprehensive code quality and MAESTRO security review
was executed and documented according to STORY-010 acceptance criteria.
"""

from pathlib import Path


def test_sprint5_review_document_exists() -> None:
    """Verify sprint5-code-review.md exists in docs/reviews/."""
    review_doc = Path("docs/reviews/sprint5-code-review.md")
    assert review_doc.exists(), "Sprint 5 review document must exist"


def test_sprint5_review_has_required_sections() -> None:
    """Verify review document contains all required MAESTRO layers."""
    review_doc = Path("docs/reviews/sprint5-code-review.md")
    content = review_doc.read_text()

    # Required sections from STORY-010 acceptance criteria
    required_sections = [
        "Layer 1",  # Model security
        "Layer 2",  # Agent Logic
        "Layer 3",  # Integration
        "Layer 4",  # Monitoring
        "Layer 5",  # Execution
        "Layer 6",  # Environment
        "Layer 7",  # Orchestration
        "Code Quality",  # From reviewing-code skill
        "Security",  # From securing-mas skill
    ]

    for section in required_sections:
        assert section in content, f"Review must include {section} analysis"


def test_sprint5_review_documents_findings() -> None:
    """Verify review includes findings with severity levels."""
    review_doc = Path("docs/reviews/sprint5-code-review.md")
    content = review_doc.read_text()

    # Must include severity classification
    severity_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    has_severity = any(level in content for level in severity_levels)

    assert has_severity, "Review must classify findings by severity"


def test_sprint5_review_includes_fixes() -> None:
    """Verify review includes fix recommendations."""
    review_doc = Path("docs/reviews/sprint5-code-review.md")
    content = review_doc.read_text()

    # Must include actionable recommendations
    fix_indicators = ["Fix:", "Mitigation:", "Recommendation:"]
    has_fixes = any(indicator in content for indicator in fix_indicators)

    assert has_fixes, "Review must include fix recommendations"
