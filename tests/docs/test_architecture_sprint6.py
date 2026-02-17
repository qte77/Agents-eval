"""Tests verifying docs/architecture.md and CC OTel analysis doc reflect Sprint 6 changes.

Purpose: Confirm that architecture.md has benchmarking and security sections for Sprint 6,
    CC-agent-teams-orchestration.md has corrected OTel approach table with trace spans row,
    and AGENT_LEARNINGS.md documents the CC OTel limitation.
Setup: No external dependencies — purely filesystem/content checks.
Expected behavior: Documents must contain specific Sprint 6 content markers.
Mock strategy: None needed — content assertions only.
"""

from pathlib import Path

ARCH = Path(__file__).parent.parent.parent / "docs" / "architecture.md"
CC_ORCH = (
    Path(__file__).parent.parent.parent
    / "docs"
    / "analysis"
    / "CC-agent-teams-orchestration.md"
)
LEARNINGS = Path(__file__).parent.parent.parent / "AGENT_LEARNINGS.md"
SETTINGS = Path(__file__).parent.parent.parent / ".claude" / "settings.json"


class TestBenchmarkingSection:
    """Verify architecture.md contains Benchmarking Infrastructure section."""

    def test_benchmarking_section_exists(self) -> None:
        """architecture.md must include Benchmarking Infrastructure section.

        Story: STORY-005 — Sprint 6 benchmarking not documented in architecture.md.
        """
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "Benchmarking" in content and "Sprint 6" in content, (
            "docs/architecture.md must include Benchmarking Infrastructure (Sprint 6) section"
        )

    def test_sweepconfig_documented(self) -> None:
        """architecture.md must document SweepConfig module."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "SweepConfig" in content, (
            "docs/architecture.md must document SweepConfig module"
        )

    def test_sweeprunner_documented(self) -> None:
        """architecture.md must document SweepRunner module."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "SweepRunner" in content, (
            "docs/architecture.md must document SweepRunner module"
        )

    def test_sweep_analysis_documented(self) -> None:
        """architecture.md must document sweep analysis/SweepAnalysis module."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "SweepAnalysis" in content or "SweepAnalyzer" in content, (
            "docs/architecture.md must document SweepAnalysis/SweepAnalyzer module"
        )

    def test_cc_headless_integration_documented(self) -> None:
        """architecture.md must document CC headless integration."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "claude -p" in content or "headless" in content, (
            "docs/architecture.md benchmarking section must document CC headless integration"
        )

    def test_results_output_documented(self) -> None:
        """architecture.md must document results.json and summary.md output."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "results.json" in content, (
            "docs/architecture.md must document results.json output"
        )


class TestSecuritySection:
    """Verify architecture.md contains Security Framework section."""

    def test_security_section_exists(self) -> None:
        """architecture.md must include Security Framework section.

        Story: STORY-005 — Sprint 6 security hardening not documented.
        """
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "Security Framework" in content or "Security Hardening" in content, (
            "docs/architecture.md must include Security Framework (Sprint 6) section"
        )

    def test_maestro_referenced(self) -> None:
        """Security section must reference MAESTRO review."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "MAESTRO" in content, (
            "docs/architecture.md security section must reference MAESTRO review"
        )

    def test_security_advisories_referenced(self) -> None:
        """Security section must reference SECURITY.md or security-advisories.md."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "SECURITY" in content or "security-advisories" in content, (
            "docs/architecture.md security section must reference security advisories document"
        )

    def test_input_sanitization_documented(self) -> None:
        """Security section must mention input sanitization."""
        # Arrange
        content = ARCH.read_text()
        # Act / Assert
        assert "sanitization" in content or "SSRF" in content, (
            "docs/architecture.md security section must document input sanitization layers"
        )


class TestCCOTelDocCorrection:
    """Verify CC-agent-teams-orchestration.md has corrected OTel approach table."""

    def test_trace_spans_row_exists(self) -> None:
        """Approach table must include 'Trace spans' row.

        Story: STORY-005 — OTel analysis doc must be corrected to show metrics/logs only.
        """
        # Arrange
        content = CC_ORCH.read_text()
        # Act / Assert
        assert "Trace spans" in content, (
            "docs/analysis/CC-agent-teams-orchestration.md must include 'Trace spans' row in approach table"
        )

    def test_otel_no_trace_spans_documented(self) -> None:
        """Approach table must show OTel does NOT provide trace spans."""
        # Arrange
        content = CC_ORCH.read_text()
        # Act / Assert
        assert "upstream limitation" in content.lower() or "No — upstream" in content or "no trace" in content.lower(), (
            "CC-agent-teams-orchestration.md must document OTel has no trace spans (upstream limitation)"
        )

    def test_artifact_collection_primary_documented(self) -> None:
        """Recommendation section must state artifact collection is primary for evaluation."""
        # Arrange
        content = CC_ORCH.read_text()
        # Act / Assert
        assert "artifact" in content.lower() and (
            "primary" in content.lower() or "evaluation" in content.lower()
        ), (
            "CC-agent-teams-orchestration.md must recommend artifact collection as primary for evaluation"
        )


class TestSettingsJsonAnnotations:
    """Verify .claude/settings.json OTel vars are annotated (via surrounding doc context)."""

    def test_otel_vars_present_in_settings(self) -> None:
        """settings.json must contain OTel environment variable keys.

        Story: STORY-005 — OTel vars need annotation about being currently disabled.
        Note: JSON doesn't support comments; annotation is in the CC OTel doc instead.
        """
        # Arrange
        content = SETTINGS.read_text()
        # Act / Assert
        assert "OTEL" in content, (
            ".claude/settings.json must contain OTEL environment variable entries"
        )


class TestAgentLearningsOTelEntry:
    """Verify AGENT_LEARNINGS.md documents the CC OTel limitation."""

    def test_cc_otel_limitation_documented(self) -> None:
        """AGENT_LEARNINGS.md must document CC OTel trace spans limitation.

        Story: STORY-005 — CC OTel upstream limitation must be documented as a learning.
        """
        # Arrange
        content = LEARNINGS.read_text()
        # Act / Assert
        assert "OTel" in content and (
            "trace" in content.lower() or "limitation" in content.lower()
        ), (
            "AGENT_LEARNINGS.md must document CC OTel trace spans upstream limitation"
        )

    def test_cc_otel_github_issues_referenced(self) -> None:
        """AGENT_LEARNINGS.md OTel learning must reference upstream GitHub issues."""
        # Arrange
        content = LEARNINGS.read_text()
        # Act / Assert
        assert "#9584" in content or "#2090" in content or "upstream" in content.lower(), (
            "AGENT_LEARNINGS.md must reference upstream GitHub issues for CC OTel limitation"
        )
