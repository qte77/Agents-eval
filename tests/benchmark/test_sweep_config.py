"""Tests for MAS composition sweep configuration models.

This module tests the Pydantic models that define sweep configuration,
including agent composition definitions and the generate_all_compositions()
convenience function.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.benchmark.sweep_config import (
    AgentComposition,
    SweepConfig,
    generate_all_compositions,
)


class TestAgentComposition:
    """Tests for AgentComposition model."""

    def test_valid_composition(self):
        """Test creating a valid agent composition."""
        comp = AgentComposition(
            include_researcher=True,
            include_analyst=False,
            include_synthesiser=True,
        )
        assert comp.include_researcher is True
        assert comp.include_analyst is False
        assert comp.include_synthesiser is True

    def test_composition_name_generation(self):
        """Test that composition generates a readable name."""
        comp = AgentComposition(
            include_researcher=True,
            include_analyst=False,
            include_synthesiser=True,
        )
        name = comp.get_name()
        assert "researcher" in name.lower()
        assert "synthesiser" in name.lower()

    def test_all_agents_disabled(self):
        """Test composition with all agents disabled (manager-only mode)."""
        comp = AgentComposition(
            include_researcher=False,
            include_analyst=False,
            include_synthesiser=False,
        )
        assert comp.include_researcher is False
        assert comp.include_analyst is False
        assert comp.include_synthesiser is False


class TestSweepConfig:
    """Tests for SweepConfig model."""

    def test_valid_sweep_config(self):
        """Test creating a valid sweep configuration."""
        compositions = [
            AgentComposition(
                include_researcher=True,
                include_analyst=False,
                include_synthesiser=False,
            ),
            AgentComposition(
                include_researcher=False,
                include_analyst=True,
                include_synthesiser=False,
            ),
        ]
        config = SweepConfig(
            compositions=compositions,
            repetitions=3,
            paper_numbers=[1, 2],
            output_dir=Path("/tmp/sweep_output"),
        )
        assert len(config.compositions) == 2
        assert config.repetitions == 3
        assert config.paper_numbers == [1, 2]
        assert config.output_dir == Path("/tmp/sweep_output")

    def test_cc_baseline_disabled_by_default(self):
        """Test that CC baseline is disabled by default."""
        config = SweepConfig(
            compositions=[
                AgentComposition(
                    include_researcher=True,
                    include_analyst=False,
                    include_synthesiser=False,
                )
            ],
            repetitions=1,
            paper_numbers=[1],
            output_dir=Path("/tmp/output"),
        )
        assert config.cc_baseline_enabled is False

    def test_empty_compositions_rejected(self):
        """Test that empty compositions list is rejected."""
        with pytest.raises(ValidationError):
            SweepConfig(
                compositions=[],
                repetitions=3,
                paper_numbers=[1],
                output_dir=Path("/tmp/output"),
            )

    def test_zero_repetitions_rejected(self):
        """Test that zero or negative repetitions are rejected."""
        with pytest.raises(ValidationError):
            SweepConfig(
                compositions=[
                    AgentComposition(
                        include_researcher=True,
                        include_analyst=False,
                        include_synthesiser=False,
                    )
                ],
                repetitions=0,
                paper_numbers=[1],
                output_dir=Path("/tmp/output"),
            )

    def test_empty_paper_numbers_rejected(self):
        """Test that empty paper_numbers list is rejected."""
        with pytest.raises(ValidationError):
            SweepConfig(
                compositions=[
                    AgentComposition(
                        include_researcher=True,
                        include_analyst=False,
                        include_synthesiser=False,
                    )
                ],
                repetitions=3,
                paper_numbers=[],
                output_dir=Path("/tmp/output"),
            )


class TestGenerateAllCompositions:
    """Tests for generate_all_compositions() utility function."""

    def test_generates_8_compositions(self):
        """Test that all 2^3 = 8 combinations are generated."""
        compositions = generate_all_compositions()
        assert len(compositions) == 8

    def test_all_combinations_unique(self):
        """Test that all generated combinations are unique."""
        compositions = generate_all_compositions()
        # Convert to tuples for set comparison
        unique = {
            (c.include_researcher, c.include_analyst, c.include_synthesiser)
            for c in compositions
        }
        assert len(unique) == 8

    def test_includes_all_agents_enabled(self):
        """Test that combination with all agents enabled is included."""
        compositions = generate_all_compositions()
        all_enabled = any(
            c.include_researcher and c.include_analyst and c.include_synthesiser
            for c in compositions
        )
        assert all_enabled is True

    def test_includes_all_agents_disabled(self):
        """Test that combination with all agents disabled is included."""
        compositions = generate_all_compositions()
        all_disabled = any(
            not c.include_researcher
            and not c.include_analyst
            and not c.include_synthesiser
            for c in compositions
        )
        assert all_disabled is True
