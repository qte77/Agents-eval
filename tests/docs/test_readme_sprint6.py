"""Tests verifying README.md reflects Sprint 6 deliverables and version 4.0.0.

Purpose: Confirm that README.md has been updated to reflect Sprint 6 completion,
    correct version badge (4.0.0), Sprint 7 next steps, and updated example references.
Setup: No external dependencies — purely filesystem/content checks.
Expected behavior: README.md must contain specific version and content markers.
Mock strategy: None needed — content assertions only.
"""

from pathlib import Path

README = Path(__file__).parent.parent.parent / "README.md"


class TestReadmeVersionBadge:
    """Verify the version badge reflects Sprint 6 release (4.0.0)."""

    def test_version_badge_is_4_0_0(self) -> None:
        """Version badge must show 4.0.0 not 3.3.0.

        Sprint 6 deliverables correspond to version 4.0.0.
        """
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "version-4.0.0" in content, (
            "README.md version badge must be updated to 4.0.0 "
            f"(found: {'version-3.3.0' if 'version-3.3.0' in content else 'unknown'})"
        )

    def test_old_version_badge_removed(self) -> None:
        """Old version badge 3.3.0 must not appear."""
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "version-3.3.0" not in content, (
            "README.md must not reference old version 3.3.0"
        )


class TestReadmeCurrentRelease:
    """Verify Current Release section reflects Sprint 6 deliverables."""

    def test_current_release_mentions_sprint6(self) -> None:
        """Current Release section must reference Sprint 6."""
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "Sprint 6" in content and "4.0.0" in content, (
            "README.md must mention Sprint 6 and version 4.0.0 in Current Release"
        )

    def test_current_release_not_sprint5(self) -> None:
        """Current Release section must not describe Sprint 5 as the current release."""
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "Version 3.3.0 - Sprint 5 (Delivered)" not in content, (
            "README.md Current Release must be updated from Sprint 5 to Sprint 6"
        )


class TestReadmeNextSection:
    """Verify Next section points to Sprint 7."""

    def test_next_section_mentions_sprint7(self) -> None:
        """Next section must reference Sprint 7 scope."""
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "Sprint 7" in content, (
            "README.md Next section must reference Sprint 7"
        )

    def test_next_section_not_planned_sprint6(self) -> None:
        """Next section must not say Sprint 6 is Planned."""
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "Sprint 6 (Planned)" not in content, (
            "README.md must not show Sprint 6 as Planned in Next section"
        )


class TestReadmeExamplesReference:
    """Verify Examples section references src/examples/README.md."""

    def test_examples_references_readme(self) -> None:
        """README.md must link to src/examples/README.md for examples."""
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "src/examples/README.md" in content, (
            "README.md must reference src/examples/README.md for examples"
        )
