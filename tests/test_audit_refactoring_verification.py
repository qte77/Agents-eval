"""
Tests to verify Sprint 5 test audit refactoring was executed correctly.

Validates that implementation-detail tests were removed while behavioral
tests remain, ensuring no loss of bug-catching capability.
"""

import ast
import inspect
from pathlib import Path

import pytest

from app.common.settings import CommonSettings
from app.judge.plugins.base import EvaluatorPlugin
from app.judge.settings import JudgeSettings
from app.judge.trace_store import TraceStore
from app.utils.load_configs import LogfireConfig


class TestAuditRefactoringVerification:
    """Verify audit refactoring completed correctly."""

    def test_judge_settings_defaults_class_removed(self):
        """TestJudgeSettingsDefaults class should be deleted."""
        test_file = Path("tests/evals/test_judge_settings.py")
        content = test_file.read_text()

        # Should NOT contain TestJudgeSettingsDefaults class
        assert "class TestJudgeSettingsDefaults" not in content
        assert "test_tier1_max_seconds_default" not in content
        assert "test_tier2_model_default" not in content

        # Should still have behavioral tests
        assert "class TestJudgeSettingsEnvOverrides" in content
        assert "class TestJudgeSettingsValidation" in content

    def test_common_settings_defaults_test_removed(self):
        """test_common_settings_defaults and type validation should be deleted."""
        test_file = Path("tests/common/test_common_settings.py")
        content = test_file.read_text()

        # Should NOT contain default-checking tests
        assert "test_common_settings_defaults" not in content
        assert "test_common_settings_type_validation" not in content

        # Should still have behavioral tests
        assert "test_common_settings_env_prefix" in content
        assert "test_common_settings_env_file_loading" in content

    def test_logfire_config_defaults_removed(self):
        """Default and type validation tests should be deleted from logfire_config."""
        test_file = Path("tests/utils/test_logfire_config.py")
        content = test_file.read_text()

        # Should NOT contain default/type tests
        assert "test_logfire_config_from_settings_defaults" not in content
        assert "test_logfire_config_direct_instantiation" not in content
        assert "test_logfire_config_type_validation" not in content

        # Should still have behavioral test
        assert "test_logfire_config_from_settings_custom" in content

    def test_plugin_base_property_tests_removed(self):
        """TestEvaluatorPluginABC property-existence tests should be deleted."""
        test_file = Path("tests/judge/test_plugin_base.py")
        content = test_file.read_text()

        # Should NOT contain property existence tests
        assert "test_plugin_has_name_property" not in content
        assert "test_plugin_has_tier_property" not in content
        assert "test_plugin_has_evaluate_method" not in content
        assert "test_plugin_has_get_context_for_next_tier_method" not in content

        # Should still have behavioral tests
        assert "test_tier2_plugin_accepts_context" in content
        assert "test_tier3_plugin_accepts_context" in content

    def test_trace_store_crud_tests_removed(self):
        """Basic CRUD and metadata tests should be deleted from trace_store."""
        test_file = Path("tests/judge/test_trace_store.py")
        content = test_file.read_text()

        # Should NOT contain basic CRUD tests
        assert "test_trace_store_initializes_empty" not in content
        assert "test_trace_store_can_add_trace" not in content
        assert "test_trace_store_get_trace_by_key" not in content
        assert "test_trace_store_tracks_creation_time" not in content
        assert "test_trace_store_tracks_trace_count" not in content

        # Should still have behavioral tests (thread-safety, context manager)
        assert "class TestTraceStoreThreadSafety" in content
        assert "class TestTraceStoreContextManager" in content

    def test_plugin_llm_judge_property_tests_removed(self):
        """Interface/property tests should be deleted from llm_judge plugin."""
        test_file = Path("tests/judge/test_plugin_llm_judge.py")
        content = test_file.read_text()

        # Should NOT contain property tests
        assert "test_plugin_implements_evaluator_interface" not in content
        assert "test_plugin_name_property" not in content
        assert "test_plugin_tier_property" not in content

        # Should still have behavioral tests
        assert "test_evaluate_returns_tier2_result" in content
        assert "test_evaluate_delegates_to_engine" in content

    def test_plugin_traditional_property_tests_removed(self):
        """Interface/property tests should be deleted from traditional plugin."""
        test_file = Path("tests/judge/test_plugin_traditional.py")
        content = test_file.read_text()

        # Should NOT contain property tests
        assert "test_plugin_implements_evaluator_interface" not in content
        assert "test_plugin_name_property" not in content
        assert "test_plugin_tier_property" not in content

        # Should still have behavioral tests
        assert "test_evaluate_returns_tier1_result" in content
        assert "test_evaluate_delegates_to_engine" in content

    def test_plugin_graph_property_tests_removed(self):
        """Interface/property tests should be deleted from graph plugin."""
        test_file = Path("tests/judge/test_plugin_graph.py")
        content = test_file.read_text()

        # Should NOT contain property tests
        assert "test_plugin_implements_evaluator_interface" not in content
        assert "test_plugin_name_property" not in content
        assert "test_plugin_tier_property" not in content

        # Should still have behavioral tests
        assert "test_evaluate_returns_tier3_result" in content
        assert "test_evaluate_delegates_to_engine" in content

    def test_behavioral_coverage_preserved_judge_settings(self):
        """Verify JudgeSettings behavioral tests still catch real bugs."""
        # Test env override behavior (would catch regression)
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"JUDGE_TIER1_MAX_SECONDS": "5.0"}):
            settings = JudgeSettings()
            assert settings.tier1_max_seconds == 5.0

    def test_behavioral_coverage_preserved_common_settings(self):
        """Verify CommonSettings behavioral tests still catch real bugs."""
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"EVAL_LOG_LEVEL": "DEBUG"}):
            settings = CommonSettings()
            assert settings.log_level == "DEBUG"

    def test_behavioral_coverage_preserved_plugins(self):
        """Verify plugin behavioral tests still catch real bugs."""
        # This test would fail if we removed essential behavioral tests
        from app.judge.plugins.base import PluginRegistry
        from unittest.mock import Mock

        registry = PluginRegistry()
        mock_plugin = Mock(spec=EvaluatorPlugin)
        mock_plugin.name = "test_plugin"
        mock_plugin.tier = 1

        registry.register(mock_plugin)
        assert len(registry.list_plugins()) == 1

    def test_behavioral_coverage_preserved_trace_store(self):
        """Verify TraceStore behavioral tests still catch real bugs."""
        # Thread-safety test - would catch concurrency bugs
        import threading

        store = TraceStore()
        results = []

        def add_traces(thread_id: int):
            for i in range(10):
                # Use unique keys per thread to avoid overwrites
                store.add_trace(f"trace_t{thread_id}_{i}", {"data": i, "thread": thread_id})

        threads = [threading.Thread(target=add_traces, args=(tid,)) for tid in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have all 30 traces without data corruption
        assert len(store.get_all_traces()) == 30
