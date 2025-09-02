"""
Configuration management for evaluation pipeline.

Handles loading, validation, and access to evaluation configuration
including tier settings, performance targets, and scoring weights.
"""

import json
from pathlib import Path
from typing import Any

from app.utils.log import logger


class EvaluationConfig:
    """
    Configuration manager for evaluation pipeline.

    Loads and validates configuration from JSON files, provides
    type-safe access to configuration values with defaults.
    """

    def __init__(self, config_path: str | Path | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to config_eval.json file. If None, uses default location.
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_and_validate()

    def _resolve_config_path(self, config_path: str | Path | None) -> Path:
        """Resolve configuration file path.

        Args:
            config_path: User-provided path or None

        Returns:
            Resolved Path to configuration file
        """
        if config_path is None:
            # Default configuration path
            return Path(__file__).parent.parent / "config" / "config_eval.json"
        return Path(config_path)

    def _load_and_validate(self) -> dict[str, Any]:
        """Load and validate evaluation configuration.

        Returns:
            Validated configuration dictionary

        Raises:
            FileNotFoundError: If config file not found
            json.JSONDecodeError: If invalid JSON
            ValueError: If configuration validation fails
        """
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            logger.debug(f"Loaded pipeline configuration from {self.config_path}")

            # Validate configuration structure
            self._validate_config(config)
            return config

        except FileNotFoundError as e:
            error_msg = f"Pipeline configuration file not found: {self.config_path}"
            logger.error(
                f"{error_msg}. Please ensure config file exists and is accessible."
            )
            raise FileNotFoundError(error_msg) from e

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in pipeline configuration: {e}"
            logger.error(
                f"{error_msg}. Check file syntax at line "
                f"{e.lineno if hasattr(e, 'lineno') else 'unknown'}."
            )
            raise json.JSONDecodeError(error_msg, e.doc, e.pos) from e

        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            raise

    def _validate_config(self, config: dict[str, Any]) -> None:
        """Validate configuration structure and values.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate required sections
        required_sections = ["evaluation_system", "composite_scoring"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate evaluation system settings
        eval_system = config["evaluation_system"]
        if "tiers_enabled" not in eval_system:
            raise ValueError("Missing 'tiers_enabled' in evaluation_system")

        tiers_enabled = eval_system["tiers_enabled"]
        if not isinstance(tiers_enabled, list):
            raise ValueError("'tiers_enabled' must be a list")

        if not all(tier in [1, 2, 3] for tier in tiers_enabled):
            raise ValueError("'tiers_enabled' must contain only values 1, 2, 3")

        # Validate performance targets if present
        if "performance_targets" in eval_system:
            targets = eval_system["performance_targets"]
            if not isinstance(targets, dict):
                raise ValueError("'performance_targets' must be a dictionary")

            # Check that performance targets are positive numbers
            for key, value in targets.items():
                if not isinstance(value, int | float) or value <= 0:
                    raise ValueError(
                        f"Performance target {key} must be a positive number"
                    )

        # Validate composite scoring section
        composite = config["composite_scoring"]
        if "fallback_strategy" not in composite:
            raise ValueError("Missing 'fallback_strategy' in composite_scoring")

        logger.debug("Configuration validation passed")

    def get_enabled_tiers(self) -> set[int]:
        """Get enabled tiers as a set.

        Returns:
            Set of enabled tier numbers
        """
        return set(self.config["evaluation_system"]["tiers_enabled"])

    def get_performance_targets(self) -> dict[str, float]:
        """Get performance targets configuration.

        Returns:
            Dictionary of performance targets with defaults
        """
        eval_system = self.config["evaluation_system"]
        targets = eval_system.get("performance_targets", {})

        # Apply defaults for missing targets
        default_targets = {
            "tier1_max_seconds": 1.0,
            "tier2_max_seconds": 10.0,
            "tier3_max_seconds": 15.0,
            "total_max_seconds": 25.0,
        }

        # Merge with defaults
        return {**default_targets, **targets}

    def get_fallback_strategy(self) -> str:
        """Get fallback strategy setting.

        Returns:
            Fallback strategy name
        """
        return self.config["composite_scoring"]["fallback_strategy"]

    def get_tier1_config(self) -> dict[str, Any]:
        """Get Tier 1 (Traditional Metrics) configuration.

        Returns:
            Tier 1 configuration with defaults
        """
        return self.config.get(
            "tier1_traditional",
            {
                "similarity_metrics": ["cosine", "jaccard", "semantic"],
                "confidence_threshold": 0.8,
            },
        )

    def get_tier2_config(self) -> dict[str, Any]:
        """Get Tier 2 (LLM-as-Judge) configuration.

        Returns:
            Tier 2 configuration with defaults
        """
        return self.config.get(
            "tier2_llm_judge",
            {"model": "gpt-4o-mini", "max_retries": 2, "timeout_seconds": 30.0},
        )

    def get_tier3_config(self) -> dict[str, Any]:
        """Get Tier 3 (Graph Analysis) configuration.

        Returns:
            Tier 3 configuration with defaults
        """
        return self.config.get(
            "tier3_graph",
            {
                "min_nodes_for_analysis": 2,
                "centrality_measures": ["betweenness", "closeness", "degree"],
            },
        )

    def get_composite_scoring_config(self) -> dict[str, Any]:
        """Get composite scoring configuration.

        Returns:
            Composite scoring configuration
        """
        return self.config["composite_scoring"]

    def get_system_config(self) -> dict[str, Any]:
        """Get system-level configuration.

        Returns:
            System configuration dictionary
        """
        return self.config["evaluation_system"]

    def is_tier_enabled(self, tier: int) -> bool:
        """Check if a specific tier is enabled.

        Args:
            tier: Tier number to check (1, 2, or 3)

        Returns:
            True if tier is enabled
        """
        return tier in self.get_enabled_tiers()

    def get_full_config(self) -> dict[str, Any]:
        """Get complete configuration dictionary.

        Returns:
            Full configuration dictionary (copy)
        """
        return self.config.copy()

    def reload_config(self) -> None:
        """Reload configuration from file.

        Useful for updating configuration without restarting the application.
        """
        logger.info(f"Reloading configuration from {self.config_path}")
        self.config = self._load_and_validate()

    def get_config_summary(self) -> dict[str, Any]:
        """Get configuration summary for logging/debugging.

        Returns:
            Dictionary with key configuration details
        """
        return {
            "config_path": str(self.config_path),
            "enabled_tiers": sorted(self.get_enabled_tiers()),
            "fallback_strategy": self.get_fallback_strategy(),
            "performance_targets": self.get_performance_targets(),
            "has_tier1_config": "tier1_traditional" in self.config,
            "has_tier2_config": "tier2_llm_judge" in self.config,
            "has_tier3_config": "tier3_graph" in self.config,
        }
