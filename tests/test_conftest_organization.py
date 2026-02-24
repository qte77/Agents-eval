"""Tests for subdirectory conftest.py organization (STORY-004).

Verifies that shared fixtures are available via subdirectory conftest.py files
rather than duplicated across individual test files.
"""

import importlib
from pathlib import Path

import pytest


TESTS_ROOT = Path(__file__).parent


class TestSubdirectoryConftestFilesExist:
    """Verify conftest.py files exist in key test subdirectories."""

    @pytest.mark.parametrize(
        "subdir",
        ["agents", "judge", "tools", "evals"],
    )
    def test_conftest_exists(self, subdir):
        """Given a test subdirectory, conftest.py should exist."""
        conftest_path = TESTS_ROOT / subdir / "conftest.py"
        assert conftest_path.is_file(), f"Missing {subdir}/conftest.py"


class TestAgentsConftestFixtures:
    """Verify agents/conftest.py provides shared fixtures."""

    def test_mock_endpoint_config_fixture_available(self):
        """The mock_endpoint_config fixture should be importable from agents conftest."""
        mod = importlib.import_module("tests.agents.conftest")
        # The module should define a mock_endpoint_config function (fixture)
        assert hasattr(mod, "mock_endpoint_config"), (
            "agents/conftest.py must define mock_endpoint_config fixture"
        )

    def test_mock_endpoint_config_returns_endpoint_config(self):
        """Fixture should return an EndpointConfig instance."""
        from tests.agents.conftest import mock_endpoint_config

        # Call the raw fixture function (unwrapped)
        result = mock_endpoint_config()
        from app.data_models.app_models import EndpointConfig

        assert hasattr(result, "provider")
        assert hasattr(result, "api_key")
        assert result.provider == "openai"


class TestJudgeConftestFixtures:
    """Verify judge/conftest.py provides shared evaluation fixtures."""

    def test_judge_settings_fixture_available(self):
        """The judge_settings fixture should be importable from judge conftest."""
        mod = importlib.import_module("tests.judge.conftest")
        assert hasattr(mod, "judge_settings"), (
            "judge/conftest.py must define judge_settings fixture"
        )

    def test_sample_tier_results_fixtures_available(self):
        """Tier result fixtures should be available in judge conftest."""
        mod = importlib.import_module("tests.judge.conftest")
        for fixture_name in ["sample_tier1_result", "sample_tier2_result", "sample_tier3_result"]:
            assert hasattr(mod, fixture_name), (
                f"judge/conftest.py must define {fixture_name} fixture"
            )

    def test_sample_tier1_result_returns_valid_object(self):
        """Tier1 fixture should return an object with expected fields."""
        from tests.judge.conftest import sample_tier1_result

        result = sample_tier1_result()
        assert hasattr(result, "cosine_score")
        assert hasattr(result, "overall_score")
        assert result.cosine_score >= 0.0


class TestToolsConftestExists:
    """Verify tools/conftest.py exists with shared utilities."""

    def test_tools_conftest_exists(self):
        """tools/conftest.py should be importable."""
        mod = importlib.import_module("tests.tools.conftest")
        assert mod is not None


class TestEvalsConftestFixtures:
    """Verify evals/conftest.py provides shared evaluation fixtures."""

    def test_pipeline_fixture_available(self):
        """The pipeline fixture should be importable from evals conftest."""
        mod = importlib.import_module("tests.evals.conftest")
        assert hasattr(mod, "pipeline"), (
            "evals/conftest.py must define pipeline fixture"
        )

    def test_config_file_fixture_available(self):
        """The config_file fixture should use tmp_path not tempfile."""
        mod = importlib.import_module("tests.evals.conftest")
        assert hasattr(mod, "config_file"), (
            "evals/conftest.py must define config_file fixture"
        )


class TestNoTempfileUsage:
    """Verify tempfile.mkdtemp/NamedTemporaryFile replaced with tmp_path (AC6)."""

    def test_no_tempfile_in_evals_pipeline(self):
        """test_evaluation_pipeline.py should not use tempfile directly."""
        pipeline_test = TESTS_ROOT / "evals" / "test_evaluation_pipeline.py"
        content = pipeline_test.read_text()
        assert "tempfile.NamedTemporaryFile" not in content, (
            "test_evaluation_pipeline.py should use tmp_path instead of tempfile.NamedTemporaryFile"
        )
        assert "tempfile.mkdtemp" not in content, (
            "test_evaluation_pipeline.py should use tmp_path instead of tempfile.mkdtemp"
        )
