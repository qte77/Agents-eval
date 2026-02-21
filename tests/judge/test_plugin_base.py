"""
Tests for EvaluatorPlugin ABC and PluginRegistry.

Tests the plugin system that enables tier-ordered evaluation
with typed Pydantic models at all boundaries.
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from app.data_models.evaluation_models import Tier1Result, Tier2Result, Tier3Result
from app.judge.plugins.base import EvaluatorPlugin, PluginRegistry


class MockPluginInput(BaseModel):
    """Mock input model for testing."""

    text: str
    paper_id: str


class MockTier1Plugin(EvaluatorPlugin):
    """Mock Tier 1 plugin for testing."""

    @property
    def name(self) -> str:
        return "mock_tier1"

    @property
    def tier(self) -> int:
        return 1

    def evaluate(self, input_data: MockPluginInput, context: dict | None = None) -> Tier1Result:
        """Mock evaluation returning Tier1Result."""
        return Tier1Result(
            cosine_score=0.8,
            jaccard_score=0.7,
            semantic_score=0.75,
            execution_time=1.5,
            time_score=0.9,
            task_success=1.0,
            overall_score=0.78,
        )

    def get_context_for_next_tier(self, result: Tier1Result) -> dict:
        """Pass traditional metrics to next tier."""
        return {"tier1_scores": result.model_dump()}


class MockTier2Plugin(EvaluatorPlugin):
    """Mock Tier 2 plugin for testing."""

    @property
    def name(self) -> str:
        return "mock_tier2"

    @property
    def tier(self) -> int:
        return 2

    def evaluate(self, input_data: MockPluginInput, context: dict | None = None) -> Tier2Result:
        """Mock evaluation returning Tier2Result."""
        return Tier2Result(
            technical_accuracy=0.85,
            constructiveness=0.80,
            planning_rationality=0.75,
            overall_score=0.82,
            model_used="mock-model",
            api_cost=0.01,
            fallback_used=False,
        )

    def get_context_for_next_tier(self, result: Tier2Result) -> dict:
        """Pass LLM judge scores to next tier."""
        return {"tier2_scores": result.model_dump()}


class MockTier3Plugin(EvaluatorPlugin):
    """Mock Tier 3 plugin for testing."""

    @property
    def name(self) -> str:
        return "mock_tier3"

    @property
    def tier(self) -> int:
        return 3

    def evaluate(self, input_data: MockPluginInput, context: dict | None = None) -> Tier3Result:
        """Mock evaluation returning Tier3Result."""
        return Tier3Result(
            path_convergence=0.88,
            tool_selection_accuracy=0.92,
            communication_overhead=0.85,
            coordination_centrality=0.90,
            task_distribution_balance=0.87,
            overall_score=0.88,
            graph_complexity=15,
        )

    def get_context_for_next_tier(self, result: Tier3Result) -> dict:
        """No next tier after Tier 3."""
        return {}


class TestEvaluatorPluginABC:
    """Test EvaluatorPlugin abstract base class interface."""

    def test_tier2_plugin_accepts_context(self):
        """Tier 2 plugin accepts context from Tier 1."""
        tier1_plugin = MockTier1Plugin()
        tier2_plugin = MockTier2Plugin()

        input_data = MockPluginInput(text="test review", paper_id="123")
        tier1_result = tier1_plugin.evaluate(input_data)
        tier1_context = tier1_plugin.get_context_for_next_tier(tier1_result)

        tier2_result = tier2_plugin.evaluate(input_data, context=tier1_context)
        assert isinstance(tier2_result, Tier2Result)

    def test_tier3_plugin_accepts_context(self):
        """Tier 3 plugin accepts context from previous tiers."""
        tier3_plugin = MockTier3Plugin()
        input_data = MockPluginInput(text="test review", paper_id="123")

        # Simulate context from Tier 1 and Tier 2
        context = {
            "tier1_scores": {"overall_score": 0.78},
            "tier2_scores": {"overall_score": 0.82},
        }

        tier3_result = tier3_plugin.evaluate(input_data, context=context)
        assert isinstance(tier3_result, Tier3Result)


class TestPluginRegistry:
    """Test PluginRegistry for registration and tier-ordered execution."""

    def test_registry_initializes_empty(self):
        """Registry starts with no plugins."""
        registry = PluginRegistry()
        assert len(registry.list_plugins()) == 0

    def test_registry_register_plugin(self):
        """Registry can register a plugin."""
        registry = PluginRegistry()
        plugin = MockTier1Plugin()
        registry.register(plugin)
        assert len(registry.list_plugins()) == 1

    def test_registry_register_multiple_plugins(self):
        """Registry can register multiple plugins."""
        registry = PluginRegistry()
        registry.register(MockTier1Plugin())
        registry.register(MockTier2Plugin())
        registry.register(MockTier3Plugin())
        assert len(registry.list_plugins()) == 3

    def test_registry_returns_plugins_in_tier_order(self):
        """Registry returns plugins sorted by tier."""
        registry = PluginRegistry()

        # Register out of order
        registry.register(MockTier3Plugin())
        registry.register(MockTier1Plugin())
        registry.register(MockTier2Plugin())

        plugins = registry.list_plugins()
        assert plugins[0].tier == 1
        assert plugins[1].tier == 2
        assert plugins[2].tier == 3

    def test_registry_get_plugin_by_name(self):
        """Registry can retrieve plugin by name."""
        registry = PluginRegistry()
        plugin = MockTier1Plugin()
        registry.register(plugin)

        retrieved = registry.get_plugin("mock_tier1")
        assert retrieved is not None
        assert retrieved.name == "mock_tier1"

    def test_registry_get_nonexistent_plugin_returns_none(self):
        """Registry returns None for nonexistent plugin."""
        registry = PluginRegistry()
        assert registry.get_plugin("nonexistent") is None

    def test_registry_execute_all_in_order(self):
        """Registry executes all plugins in tier order."""
        registry = PluginRegistry()
        registry.register(MockTier3Plugin())
        registry.register(MockTier1Plugin())
        registry.register(MockTier2Plugin())

        input_data = MockPluginInput(text="test review", paper_id="123")
        results = registry.execute_all(input_data)

        # Should have 3 results in tier order
        assert len(results) == 3
        assert isinstance(results[0], Tier1Result)
        assert isinstance(results[1], Tier2Result)
        assert isinstance(results[2], Tier3Result)

    def test_registry_passes_context_between_tiers(self):
        """Registry passes context from one tier to the next."""
        registry = PluginRegistry()

        # Create a special Tier 2 plugin that validates context
        class ContextValidatingTier2Plugin(MockTier2Plugin):
            def evaluate(
                self, input_data: MockPluginInput, context: dict | None = None
            ) -> Tier2Result:
                # Verify Tier 1 context is present
                assert context is not None
                assert "tier1_scores" in context
                return super().evaluate(input_data, context)

        registry.register(MockTier1Plugin())
        registry.register(ContextValidatingTier2Plugin())

        input_data = MockPluginInput(text="test review", paper_id="123")
        results = registry.execute_all(input_data)
        assert len(results) == 2

    def test_registry_handles_plugin_error_gracefully(self):
        """Registry handles plugin evaluation errors gracefully."""

        class FailingPlugin(EvaluatorPlugin):
            @property
            def name(self) -> str:
                return "failing"

            @property
            def tier(self) -> int:
                return 1

            def evaluate(
                self, input_data: MockPluginInput, context: dict | None = None
            ) -> Tier1Result:
                raise ValueError("Simulated plugin failure")

            def get_context_for_next_tier(self, result: Tier1Result) -> dict:
                return {}

        registry = PluginRegistry()
        registry.register(FailingPlugin())

        input_data = MockPluginInput(text="test review", paper_id="123")

        # Should raise the error or return structured error result
        with pytest.raises(ValueError, match="Simulated plugin failure"):
            registry.execute_all(input_data)
