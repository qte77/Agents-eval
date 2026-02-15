"""
Base classes for evaluator plugin system.

Defines the EvaluatorPlugin ABC and PluginRegistry for typed,
tier-ordered plugin execution with Pydantic models at all boundaries.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from app.utils.log import logger


class EvaluatorPlugin(ABC):
    """Abstract base class for evaluation plugins.

    Each plugin implements a specific evaluation tier (1, 2, or 3)
    and provides typed input/output using Pydantic models.

    Attributes:
        name: Unique identifier for the plugin
        tier: Evaluation tier (1=Traditional, 2=LLM-Judge, 3=Graph)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return unique plugin identifier.

        Returns:
            Plugin name string
        """
        pass

    @property
    @abstractmethod
    def tier(self) -> int:
        """Return evaluation tier number.

        Returns:
            Tier number (1, 2, or 3)
        """
        pass

    @abstractmethod
    def evaluate(self, input_data: BaseModel, context: dict[str, Any] | None = None) -> BaseModel:
        """Execute plugin evaluation.

        Args:
            input_data: Typed input data (Pydantic model)
            context: Optional context from previous tier evaluations

        Returns:
            Evaluation result as Pydantic model (Tier1Result, Tier2Result, or Tier3Result)

        Raises:
            ValueError: If input validation fails
            RuntimeError: If evaluation execution fails
        """
        pass

    @abstractmethod
    def get_context_for_next_tier(self, result: BaseModel) -> dict[str, Any]:
        """Extract context to pass to next tier.

        Args:
            result: Evaluation result from this tier

        Returns:
            Dictionary of context data for next tier
        """
        pass


class PluginRegistry:
    """Registry for managing and executing evaluation plugins.

    Maintains plugins in tier order and orchestrates sequential execution
    with context passing between tiers.
    """

    def __init__(self) -> None:
        """Initialize empty plugin registry."""
        self._plugins: dict[str, EvaluatorPlugin] = {}

    def register(self, plugin: EvaluatorPlugin) -> None:
        """Register an evaluation plugin.

        Args:
            plugin: Plugin instance to register

        Raises:
            ValueError: If plugin with same name already registered
        """
        if plugin.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.name}' already registered")

        self._plugins[plugin.name] = plugin
        logger.debug(f"Registered plugin: {plugin.name} (Tier {plugin.tier})")

    def get_plugin(self, name: str) -> EvaluatorPlugin | None:
        """Retrieve plugin by name.

        Args:
            name: Plugin name to retrieve

        Returns:
            Plugin instance if found, None otherwise
        """
        return self._plugins.get(name)

    def list_plugins(self) -> list[EvaluatorPlugin]:
        """List all registered plugins in tier order.

        Returns:
            List of plugins sorted by tier number
        """
        return sorted(self._plugins.values(), key=lambda p: p.tier)

    def execute_all(self, input_data: BaseModel) -> list[BaseModel]:
        """Execute all plugins in tier order with context passing.

        Args:
            input_data: Input data for first plugin

        Returns:
            List of results from each plugin in tier order

        Raises:
            ValueError: If plugin evaluation fails
            RuntimeError: If plugin execution fails
        """
        results: list[BaseModel] = []
        context: dict[str, Any] = {}

        for plugin in self.list_plugins():
            logger.debug(f"Executing plugin: {plugin.name} (Tier {plugin.tier})")

            # Execute plugin with accumulated context
            result = plugin.evaluate(input_data, context=context if context else None)
            results.append(result)

            # Extract context for next tier
            next_context = plugin.get_context_for_next_tier(result)
            context.update(next_context)

        return results
