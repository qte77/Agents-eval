"""Tests verifying PlantUML diagrams reflect Sprint 6 changes.

Purpose: Confirm that metrics-eval-sweep.plantuml shows benchmarking workflow
    with SweepConfig/SweepRunner/CC headless path, and MAS-Review-Workflow.plantuml
    includes security boundaries with MAESTRO annotations.
Setup: No external dependencies — purely filesystem/content checks.
Expected behavior: Diagram source files must contain specific Sprint 6 content markers.
Mock strategy: None needed — content assertions only.
"""

from pathlib import Path

ARCH_VIS = Path(__file__).parent.parent.parent / "docs" / "arch_vis"
SWEEP_DIAGRAM = ARCH_VIS / "metrics-eval-sweep.plantuml"
WORKFLOW_DIAGRAM = ARCH_VIS / "MAS-Review-Workflow.plantuml"
README = ARCH_VIS / "README.md"
ARCHITECTURE_MD = Path(__file__).parent.parent.parent / "docs" / "architecture.md"
ROOT_README = Path(__file__).parent.parent.parent / "README.md"


class TestSweepDiagram:
    """Verify metrics-eval-sweep.plantuml contains benchmarking workflow content."""

    def test_sweep_diagram_exists(self) -> None:
        """metrics-eval-sweep.plantuml must exist.

        Story: STORY-006 — PlantUML diagrams don't reflect Sprint 6 changes.
        """
        # Arrange / Act / Assert
        assert SWEEP_DIAGRAM.exists(), "docs/arch_vis/metrics-eval-sweep.plantuml must exist"

    def test_sweep_diagram_has_sweep_config(self) -> None:
        """Sweep diagram must document SweepConfig.

        Story: STORY-006 — Workflow: SweepConfig → SweepRunner → ... → SweepAnalysis.
        """
        # Arrange
        content = SWEEP_DIAGRAM.read_text()
        # Act / Assert
        assert "SweepConfig" in content, (
            "metrics-eval-sweep.plantuml must include SweepConfig in the workflow"
        )

    def test_sweep_diagram_has_sweep_runner(self) -> None:
        """Sweep diagram must document SweepRunner.

        Story: STORY-006 — Workflow: SweepConfig → SweepRunner → ...
        """
        # Arrange
        content = SWEEP_DIAGRAM.read_text()
        # Act / Assert
        assert "SweepRunner" in content, (
            "metrics-eval-sweep.plantuml must include SweepRunner in the workflow"
        )

    def test_sweep_diagram_has_sweep_analysis(self) -> None:
        """Sweep diagram must document SweepAnalysis/SweepAnalyzer.

        Story: STORY-006 — Workflow: ... → SweepAnalysis → output files.
        """
        # Arrange
        content = SWEEP_DIAGRAM.read_text()
        # Act / Assert
        assert "SweepAnalysis" in content or "SweepAnalyzer" in content, (
            "metrics-eval-sweep.plantuml must include SweepAnalysis/SweepAnalyzer"
        )

    def test_sweep_diagram_has_cc_headless_path(self) -> None:
        """Sweep diagram must include optional CC headless path.

        Story: STORY-006 — Includes optional CC headless path: claude -p → artifacts → CCTraceAdapter.
        """
        # Arrange
        content = SWEEP_DIAGRAM.read_text()
        # Act / Assert
        assert "claude -p" in content or "CCTraceAdapter" in content, (
            "metrics-eval-sweep.plantuml must include optional CC headless path (claude -p or CCTraceAdapter)"
        )

    def test_sweep_diagram_has_output_files(self) -> None:
        """Sweep diagram must show output files (results.json or summary.md).

        Story: STORY-006 — Workflow: ... → SweepAnalysis → output files.
        """
        # Arrange
        content = SWEEP_DIAGRAM.read_text()
        # Act / Assert
        assert "results.json" in content or "summary.md" in content, (
            "metrics-eval-sweep.plantuml must show output files (results.json or summary.md)"
        )

    def test_sweep_diagram_is_valid_plantuml(self) -> None:
        """Sweep diagram must be valid PlantUML (start/end tags).

        Story: STORY-006 — All PlantUML sources render without errors.
        """
        # Arrange
        content = SWEEP_DIAGRAM.read_text()
        # Act / Assert
        assert "@startuml" in content and "@enduml" in content, (
            "metrics-eval-sweep.plantuml must have valid PlantUML @startuml/@enduml tags"
        )


class TestWorkflowDiagramSecurity:
    """Verify MAS-Review-Workflow.plantuml includes security boundaries."""

    def test_workflow_diagram_exists(self) -> None:
        """MAS-Review-Workflow.plantuml must exist.

        Story: STORY-006 — Updated diagram: MAS-Review-Workflow.plantuml includes security boundaries.
        """
        # Arrange / Act / Assert
        assert WORKFLOW_DIAGRAM.exists(), "docs/arch_vis/MAS-Review-Workflow.plantuml must exist"

    def test_workflow_has_url_validation(self) -> None:
        """Workflow diagram must show URL validation checkpoint.

        Story: STORY-006 — Shows URL validation checkpoints.
        """
        # Arrange
        content = WORKFLOW_DIAGRAM.read_text()
        # Act / Assert
        assert "URL" in content or "url" in content.lower() or "validate" in content.lower(), (
            "MAS-Review-Workflow.plantuml must include URL validation checkpoint"
        )

    def test_workflow_has_prompt_sanitization(self) -> None:
        """Workflow diagram must show prompt sanitization before LLM calls.

        Story: STORY-006 — Shows prompt sanitization before LLM calls.
        """
        # Arrange
        content = WORKFLOW_DIAGRAM.read_text()
        # Act / Assert
        assert "sanitiz" in content.lower() or "Sanitiz" in content, (
            "MAS-Review-Workflow.plantuml must include prompt sanitization annotation"
        )

    def test_workflow_has_log_scrubbing(self) -> None:
        """Workflow diagram must show log scrubbing before trace export.

        Story: STORY-006 — Shows log scrubbing before trace export.
        """
        # Arrange
        content = WORKFLOW_DIAGRAM.read_text()
        # Act / Assert
        assert "scrub" in content.lower() or "Scrub" in content, (
            "MAS-Review-Workflow.plantuml must include log scrubbing annotation"
        )

    def test_workflow_has_maestro_annotation(self) -> None:
        """Workflow diagram must include MAESTRO layer annotations.

        Story: STORY-006 — Annotations for MAESTRO layers.
        """
        # Arrange
        content = WORKFLOW_DIAGRAM.read_text()
        # Act / Assert
        assert "MAESTRO" in content, (
            "MAS-Review-Workflow.plantuml must include MAESTRO layer annotations"
        )

    def test_workflow_is_valid_plantuml(self) -> None:
        """Workflow diagram must be valid PlantUML (start/end tags).

        Story: STORY-006 — All PlantUML sources render without errors.
        """
        # Arrange
        content = WORKFLOW_DIAGRAM.read_text()
        # Act / Assert
        assert "@startuml" in content and "@enduml" in content, (
            "MAS-Review-Workflow.plantuml must have valid PlantUML @startuml/@enduml tags"
        )


class TestArchVisReadme:
    """Verify docs/arch_vis/README.md updated with new diagram descriptions."""

    def test_readme_mentions_sweep_diagram(self) -> None:
        """README.md must reference metrics-eval-sweep.plantuml.

        Story: STORY-006 — docs/arch_vis/README.md updated with new diagram descriptions.
        """
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "metrics-eval-sweep" in content, (
            "docs/arch_vis/README.md must reference metrics-eval-sweep diagram"
        )

    def test_readme_describes_sweep_content(self) -> None:
        """README.md sweep entry must describe sweep workflow content.

        Story: STORY-006 — New diagram descriptions in README.
        """
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "sweep" in content.lower() and (
            "composition" in content.lower()
            or "benchmark" in content.lower()
            or "SweepRunner" in content
        ), "docs/arch_vis/README.md must describe sweep diagram with composition/benchmark content"

    def test_readme_mentions_workflow_security(self) -> None:
        """README.md must note that MAS-Review-Workflow includes security boundaries.

        Story: STORY-006 — Updated diagram includes security boundaries.
        """
        # Arrange
        content = README.read_text()
        # Act / Assert
        assert "security" in content.lower() or "MAS-Review-Workflow" in content, (
            "docs/arch_vis/README.md must reference MAS-Review-Workflow with security"
        )
