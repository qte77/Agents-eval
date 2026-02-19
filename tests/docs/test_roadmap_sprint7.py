"""Tests verifying docs/roadmap.md reflects Sprint 6 delivered and Sprint 7 in progress.

Purpose: Confirm that roadmap.md shows Sprint 6 as Delivered with correct PRD reference,
    Sprint 7 as In Progress with correct PRD reference, and chronological table order.
Setup: No external dependencies — purely filesystem/content checks.
Expected behavior: roadmap.md must contain specific sprint status markers.
Mock strategy: None needed — content assertions only.
"""

from pathlib import Path

ROADMAP = Path(__file__).parent.parent.parent / "docs" / "roadmap.md"


class TestSprint6Delivered:
    """Verify Sprint 6 row shows Delivered status."""

    def test_sprint6_status_is_delivered(self) -> None:
        """Sprint 6 row must show 'Delivered' status.

        Story: STORY-004 — Sprint 6 was marked Planned, must now be Delivered.
        """
        # Arrange
        content = ROADMAP.read_text()
        # Act / Assert
        assert "Sprint 6" in content and "Delivered" in content, (
            "docs/roadmap.md Sprint 6 row must show 'Delivered' status"
        )

    def test_sprint6_references_prd_sprint6(self) -> None:
        """Sprint 6 row must reference PRD-Sprint6-Ralph.md."""
        # Arrange
        content = ROADMAP.read_text()
        # Act / Assert
        assert "PRD-Sprint6-Ralph.md" in content, (
            "docs/roadmap.md Sprint 6 row must reference PRD-Sprint6-Ralph.md"
        )

    def test_sprint6_not_planned(self) -> None:
        """Sprint 6 row must not still show Planned status."""
        # Arrange
        lines = ROADMAP.read_text().splitlines()
        # Act
        sprint6_lines = [line for line in lines if "Sprint 6" in line]
        # Assert
        for line in sprint6_lines:
            assert "Planned" not in line, (
                f"docs/roadmap.md Sprint 6 row must not show 'Planned': {line}"
            )


class TestSprint7InProgress:
    """Verify Sprint 7 row shows In Progress status."""

    def test_sprint7_row_exists(self) -> None:
        """Sprint 7 row must exist in the roadmap table."""
        # Arrange
        content = ROADMAP.read_text()
        # Act / Assert
        assert "Sprint 7" in content, "docs/roadmap.md must include a Sprint 7 row"

    def test_sprint7_status_is_in_progress(self) -> None:
        """Sprint 7 row must show 'In Progress' status.

        Story: STORY-004 — Sprint 7 row must be added with 'In Progress' status.
        """
        # Arrange
        lines = ROADMAP.read_text().splitlines()
        # Act
        sprint7_lines = [line for line in lines if "Sprint 7" in line]
        # Assert
        assert any("In Progress" in line for line in sprint7_lines), (
            "docs/roadmap.md Sprint 7 row must show 'In Progress' status"
        )

    def test_sprint7_references_prd_sprint7(self) -> None:
        """Sprint 7 row must reference PRD-Sprint7-Ralph.md."""
        # Arrange
        content = ROADMAP.read_text()
        # Act / Assert
        assert "PRD-Sprint7-Ralph.md" in content, (
            "docs/roadmap.md Sprint 7 row must reference PRD-Sprint7-Ralph.md"
        )


class TestRoadmapChronology:
    """Verify Sprint table maintains chronological order with correct delivered count."""

    def test_all_sprints_1_through_6_delivered(self) -> None:
        """Sprints 1-6 must all appear in roadmap with Delivered status."""
        # Arrange
        content = ROADMAP.read_text()
        # Act / Assert
        for i in range(1, 7):
            assert f"Sprint {i}" in content, f"docs/roadmap.md must include Sprint {i} row"
        assert content.count("Delivered") >= 6, (
            "docs/roadmap.md must show at least 6 sprints as Delivered (Sprints 1-6)"
        )

    def test_sprint7_appears_after_sprint6(self) -> None:
        """Sprint 7 row must appear after Sprint 6 row in table."""
        # Arrange
        content = ROADMAP.read_text()
        # Act
        sprint6_pos = content.find("Sprint 6")
        sprint7_pos = content.find("Sprint 7")
        # Assert
        assert sprint6_pos < sprint7_pos, (
            "docs/roadmap.md Sprint 7 must appear after Sprint 6 in the table"
        )
