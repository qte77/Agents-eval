"""
Tests to ensure EvaluationConfig JSON-based config is fully removed.

These tests enforce the migration from config_eval.json to JudgeSettings.
They should fail initially (RED phase) and pass after migration (GREEN phase).
"""

import pytest

from app.evals.evaluation_pipeline import EvaluationPipeline
from app.evals.settings import JudgeSettings


class TestEvaluationConfigRemoval:
    """Test that EvaluationConfig is no longer used in the codebase."""

    def test_pipeline_does_not_accept_config_path(self):
        """EvaluationPipeline should not accept config_path parameter."""
        # This test ensures config_path parameter is removed
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            EvaluationPipeline(config_path="dummy.json")

    def test_pipeline_requires_settings_or_defaults(self):
        """EvaluationPipeline must use JudgeSettings or defaults."""
        # Pipeline with no args should use default JudgeSettings
        pipeline = EvaluationPipeline()
        assert pipeline.settings is not None
        assert isinstance(pipeline.settings, JudgeSettings)

    def test_pipeline_with_explicit_settings(self):
        """EvaluationPipeline should accept only JudgeSettings."""
        settings = JudgeSettings(tiers_enabled=[1, 2])
        pipeline = EvaluationPipeline(settings=settings)

        assert pipeline.settings is settings
        assert pipeline.enabled_tiers == {1, 2}
        assert 3 not in pipeline.enabled_tiers

    def test_no_config_manager_attribute(self):
        """EvaluationPipeline should not have config_manager attribute."""
        pipeline = EvaluationPipeline()

        # config_manager should not exist
        assert not hasattr(pipeline, "config_manager") or pipeline.config_manager is None

    def test_settings_attribute_always_exists(self):
        """EvaluationPipeline should always have settings attribute."""
        pipeline = EvaluationPipeline()
        assert hasattr(pipeline, "settings")
        assert pipeline.settings is not None
