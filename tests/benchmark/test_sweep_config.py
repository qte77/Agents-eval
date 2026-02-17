"""Tests for MAS composition sweep configuration models.

This module tests the generate_all_compositions() convenience function
and composition name generation.
"""

from app.benchmark.sweep_config import AgentComposition, generate_all_compositions


class TestAgentComposition:
    """Tests for AgentComposition model."""

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
            (c.include_researcher, c.include_analyst, c.include_synthesiser) for c in compositions
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
            not c.include_researcher and not c.include_analyst and not c.include_synthesiser
            for c in compositions
        )
        assert all_disabled is True
