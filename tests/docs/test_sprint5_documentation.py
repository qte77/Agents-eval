"""Tests for Sprint 5 documentation updates (STORY-005).

This test file verifies that all required documentation updates for Sprint 5
are present and correct. Following TDD approach, these tests are written
first (RED phase) and will fail until documentation is updated (GREEN phase).
"""

import re
from pathlib import Path


def test_readme_version_badge_updated() -> None:
    """Verify README.md version badge is updated to include Sprint 5."""
    readme_path = Path("README.md")
    readme_content = readme_path.read_text()

    # Check that version badge exists (should be 3.3.x or higher for Sprint 5)
    version_pattern = r"!\[Version\]\(https://img.shields.io/badge/version-(\d+\.\d+\.\d+)-"
    match = re.search(version_pattern, readme_content)

    assert match is not None, "Version badge not found in README.md"
    version = match.group(1)
    major, minor, _ = map(int, version.split("."))

    # Sprint 5 should be version 3.3.0 or higher
    assert (major > 3 or (major == 3 and minor >= 3)), \
        f"Version {version} is too low for Sprint 5 (expected 3.3.x or higher)"


def test_readme_mentions_sprint5() -> None:
    """Verify README.md references Sprint 5 in status section."""
    readme_path = Path("README.md")
    readme_content = readme_path.read_text()

    # Should mention Sprint 5 somewhere in the status/project details
    assert "Sprint 5" in readme_content or "sprint 5" in readme_content.lower(), \
        "README.md should reference Sprint 5 in status section"


def test_roadmap_has_sprint5_entry() -> None:
    """Verify docs/roadmap.md has Sprint 5 row with correct status and link."""
    roadmap_path = Path("docs/roadmap.md")
    roadmap_content = roadmap_path.read_text()

    # Check for Sprint 5 row in the table
    assert "Sprint 5" in roadmap_content, "Sprint 5 entry not found in roadmap.md"

    # Should have status (Active or Delivered)
    sprint5_pattern = r"\*\*Sprint 5\*\*.*\|.*(Active|Delivered)"
    assert re.search(sprint5_pattern, roadmap_content), \
        "Sprint 5 entry should have Active or Delivered status"

    # Should link to PRD-Sprint5-Ralph.md
    assert "PRD-Sprint5-Ralph.md" in roadmap_content, \
        "Sprint 5 should link to PRD-Sprint5-Ralph.md"


def test_architecture_composite_scoring_updated() -> None:
    """Verify architecture.md documents single-agent weight redistribution."""
    arch_path = Path("docs/architecture.md")
    arch_content = arch_path.read_text()

    # Should mention single-agent mode or weight redistribution
    assert any(phrase in arch_content.lower() for phrase in [
        "single-agent",
        "single agent",
        "weight redistribution",
        "coordination_quality"
    ]), "architecture.md should document single-agent weight redistribution behavior"


def test_architecture_tier2_provider_fallback_updated() -> None:
    """Verify architecture.md documents Tier 2 provider fallback and auto mode."""
    arch_path = Path("docs/architecture.md")
    arch_content = arch_path.read_text()

    # Should mention provider fallback or auto mode
    assert any(phrase in arch_content.lower() for phrase in [
        "provider fallback",
        "fallback chain",
        "tier2_provider",
        "auto mode"
    ]), "architecture.md should document Tier 2 provider fallback and auto mode"


def test_architecture_implementation_status_has_sprint5() -> None:
    """Verify architecture.md Implementation Status section mentions Sprint 5."""
    arch_path = Path("docs/architecture.md")
    arch_content = arch_path.read_text()

    # Find Implementation Status section
    impl_status_pattern = r"## Implementation Status.*?(?=##|\Z)"
    match = re.search(impl_status_pattern, arch_content, re.DOTALL)

    assert match is not None, "Implementation Status section not found"
    impl_section = match.group(0)

    # Should mention Sprint 5
    assert "Sprint 5" in impl_section or "sprint 5" in impl_section.lower(), \
        "Implementation Status section should reference Sprint 5"


def test_graph_analysis_no_opik_references() -> None:
    """Verify graph_analysis.py has no stale Opik references in docstrings."""
    graph_path = Path("src/app/judge/graph_analysis.py")
    graph_content = graph_path.read_text()

    # Find all docstrings (triple-quoted strings)
    docstring_pattern = r'"""(.*?)"""'
    docstrings = re.findall(docstring_pattern, graph_content, re.DOTALL)

    # Check that no docstring contains "Opik" (should reference Phoenix instead)
    for docstring in docstrings:
        assert "Opik" not in docstring, \
            "Found stale 'Opik' reference in docstring - should be 'Phoenix'"


def test_changelog_has_story005_entry() -> None:
    """Verify CHANGELOG.md has STORY-005 documentation update entry."""
    changelog_path = Path("CHANGELOG.md")
    changelog_content = changelog_path.read_text()

    # Should have STORY-005 entry in Unreleased section
    assert "STORY-005" in changelog_content, \
        "CHANGELOG.md should have STORY-005 entry"

    # Should mention documentation update
    assert any(phrase in changelog_content.lower() for phrase in [
        "documentation update",
        "architecture update",
        "sprint 5 documentation"
    ]), "CHANGELOG.md should describe documentation updates for Sprint 5"


def test_no_broken_internal_links_in_updated_docs() -> None:
    """Verify no broken internal links were introduced in documentation updates."""
    # This is a placeholder - would need proper link checker implementation
    # For now, just check that key referenced files exist

    required_files = [
        Path("docs/PRD-Sprint5-Ralph.md"),
        Path("docs/roadmap.md"),
        Path("docs/architecture.md"),
        Path("README.md"),
        Path("CHANGELOG.md"),
    ]

    for file_path in required_files:
        assert file_path.exists(), f"Referenced file {file_path} does not exist"
