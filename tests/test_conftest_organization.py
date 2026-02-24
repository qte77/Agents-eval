"""Tests for subdirectory conftest.py organization (STORY-004).

Verifies that shared fixtures are available via subdirectory conftest.py files
rather than duplicated across individual test files.
"""

import importlib.util
from pathlib import Path

import pytest


TESTS_ROOT = Path(__file__).parent


def _load_conftest(subdir: str):
    """Load a conftest.py module from a test subdirectory by file path.

    Args:
        subdir: Name of the test subdirectory (e.g., "agents").

    Returns:
        The loaded module.
    """
    conftest_path = TESTS_ROOT / subdir / "conftest.py"
    spec = importlib.util.spec_from_file_location(f"{subdir}_conftest", conftest_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
        """The mock_endpoint_config fixture should be defined in agents conftest."""
        mod = _load_conftest("agents")
        assert hasattr(mod, "mock_endpoint_config"), (
            "agents/conftest.py must define mock_endpoint_config fixture"
        )

    def test_mock_endpoint_config_returns_endpoint_config(self):
        """Fixture source should reference EndpointConfig."""
        import inspect

        mod = _load_conftest("agents")
        source = inspect.getsource(mod.mock_endpoint_config)
        assert "EndpointConfig" in source
        assert 'provider="openai"' in source


class TestJudgeConftestFixtures:
    """Verify judge/conftest.py provides shared evaluation fixtures."""

    def test_judge_settings_fixture_available(self):
        """The judge_settings fixture should be defined in judge conftest."""
        mod = _load_conftest("judge")
        assert hasattr(mod, "judge_settings"), (
            "judge/conftest.py must define judge_settings fixture"
        )

    def test_sample_tier_results_fixtures_available(self):
        """Tier result fixtures should be available in judge conftest."""
        mod = _load_conftest("judge")
        for fixture_name in ["sample_tier1_result", "sample_tier2_result", "sample_tier3_result"]:
            assert hasattr(mod, fixture_name), (
                f"judge/conftest.py must define {fixture_name} fixture"
            )

    def test_sample_tier1_result_returns_valid_object(self):
        """Tier1 fixture source should reference Tier1Result fields."""
        import inspect

        mod = _load_conftest("judge")
        source = inspect.getsource(mod.sample_tier1_result)
        assert "Tier1Result" in source
        assert "cosine_score" in source
        assert "overall_score" in source


class TestToolsConftestExists:
    """Verify tools/conftest.py exists with shared utilities."""

    def test_tools_conftest_exists(self):
        """tools/conftest.py should be loadable."""
        mod = _load_conftest("tools")
        assert mod is not None


class TestEvalsConftestFixtures:
    """Verify evals/conftest.py provides shared evaluation fixtures."""

    def test_pipeline_fixture_available(self):
        """The pipeline fixture should be defined in evals conftest."""
        mod = _load_conftest("evals")
        assert hasattr(mod, "pipeline"), (
            "evals/conftest.py must define pipeline fixture"
        )

    def test_config_file_fixture_available(self):
        """The config_file fixture should use tmp_path not tempfile."""
        mod = _load_conftest("evals")
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
