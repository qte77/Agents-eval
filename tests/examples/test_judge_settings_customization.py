"""Tests for judge_settings_customization.py example.

Purpose: Verify the settings customization example demonstrates JudgeSettings
         configuration patterns including env var override and programmatic
         modification.
Setup: No external dependencies required — JudgeSettings is pure Python/Pydantic.
Expected behavior: Example demonstrates timeout adjustment, tier weight customization,
                   and provider selection modifications.
Mock strategy: No mocking needed; JudgeSettings is local configuration only.
"""

from pathlib import Path
import importlib.util
import sys

import pytest

from app.judge.settings import JudgeSettings


class TestJudgeSettingsCustomizationExists:
    """Verify the judge_settings_customization.py example file is created."""

    def test_example_file_exists(self) -> None:
        """judge_settings_customization.py must exist in src/examples/."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        target = examples_dir / "judge_settings_customization.py"
        # Assert
        assert target.exists(), f"Example file missing: {target}"

    def test_example_demonstrates_key_settings(self) -> None:
        """Example must show timeout, tier weight, and provider customization."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        content = (examples_dir / "judge_settings_customization.py").read_text()
        # Assert
        assert "JudgeSettings" in content, "Must use JudgeSettings"
        assert "tier" in content.lower(), "Must demonstrate tier configuration"
        assert "provider" in content.lower(), "Must show provider selection"


class TestJudgeSettingsModifications:
    """Verify settings modifications shown in the example work correctly."""

    def test_timeout_adjustment(self) -> None:
        """Adjusting tier timeouts via JudgeSettings constructor works correctly."""
        # Arrange / Act
        settings = JudgeSettings(tier1_max_seconds=2.0, tier2_max_seconds=20.0)
        # Assert
        assert settings.tier1_max_seconds == 2.0
        assert settings.tier2_max_seconds == 20.0

    def test_tier_weight_customization(self) -> None:
        """Tier weights can be customized and sum correctly."""
        # Arrange / Act
        settings = JudgeSettings(
            tier1_weight=0.5,
            tier2_weight=0.3,
            tier3_weight=0.2,
        )
        # Assert
        total = settings.tier1_weight + settings.tier2_weight + settings.tier3_weight
        assert abs(total - 1.0) < 1e-9, f"Weights must sum to 1.0, got {total}"

    def test_provider_selection(self) -> None:
        """Provider selection via JudgeSettings works correctly."""
        # Arrange / Act
        settings = JudgeSettings(tier2_provider="anthropic")
        # Assert
        assert settings.tier2_provider == "anthropic"

    def test_tiers_enabled_subset(self) -> None:
        """Restricting enabled tiers via JudgeSettings works correctly."""
        # Arrange / Act
        settings = JudgeSettings(tiers_enabled=[1, 3])
        # Assert
        enabled = settings.get_enabled_tiers()
        assert enabled == {1, 3}, f"Expected {{1, 3}}, got {enabled}"
        assert not settings.is_tier_enabled(2), "Tier 2 should be disabled"

    def test_example_is_importable(self) -> None:
        """judge_settings_customization.py imports without errors."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        spec = importlib.util.spec_from_file_location(
            "judge_settings_customization",
            examples_dir / "judge_settings_customization.py",
        )
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        # Act / Assert: loading must not raise
        sys.modules["judge_settings_customization"] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]

    def test_example_demonstrates_env_var_override(self) -> None:
        """Example explains how environment variable override works."""
        # Arrange
        examples_dir = Path(__file__).parent.parent.parent / "src" / "examples"
        content = (examples_dir / "judge_settings_customization.py").read_text()
        # Assert: content must mention env var pattern
        assert "JUDGE_" in content or "env" in content.lower(), (
            "Example must explain JUDGE_ environment variable override pattern"
        )
