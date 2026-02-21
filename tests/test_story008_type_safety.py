"""Tests for STORY-008: Type safety and quick fixes.

Covers:
- AC1: sweep_runner._call_main return type via TypedDict
- AC2: cc_engine._parse_jsonl_line returns dict[str, Any] | None (no type: ignore)
- AC3: load_config is generic — returns T where T: BaseModel
- AC4: model_info in ReviewGenerationResult derived from actual model name
- AC5: time.sleep removed from evaluate_single_traditional
- AC6: baseline_comparison.compare handles empty metric_deltas without ZeroDivisionError
- AC7: run_sweep.py uses config_data.get("repetitions", 3) not config_data["repetitions"]
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

# ---------------------------------------------------------------------------
# AC2: cc_engine._parse_jsonl_line type correctness
# ---------------------------------------------------------------------------


class TestCCEngineParseJsonlLine:
    """AC2: _parse_jsonl_line — no type: ignore[no-any-return] in cc_engine.py."""

    def test_cc_engine_has_no_type_ignore_no_any_return(self):
        """cc_engine.py must not have # type: ignore[no-any-return].

        AC2: Adding cast(dict[str, Any] | None, json.loads(stripped)) removes
        the need for the type: ignore[no-any-return] suppression.
        """
        from pathlib import Path

        src_file = Path("src/app/engines/cc_engine.py")
        source = src_file.read_text()

        assert "type: ignore[no-any-return]" not in source, (
            "cc_engine.py still has # type: ignore[no-any-return]. "
            "Fix AC2: wrap json.loads with cast(dict[str, Any] | None, ...)."
        )

    def test_returns_dict_for_valid_json(self):
        """_parse_jsonl_line returns dict[str, Any] for valid JSON."""
        from app.engines.cc_engine import _parse_jsonl_line

        result = _parse_jsonl_line('{"type": "result", "num_turns": 3}')
        assert result is not None
        assert isinstance(result, dict)
        assert result["type"] == "result"
        assert result["num_turns"] == 3

    def test_returns_none_for_empty_line(self):
        """_parse_jsonl_line returns None for blank input."""
        from app.engines.cc_engine import _parse_jsonl_line

        assert _parse_jsonl_line("") is None
        assert _parse_jsonl_line("   ") is None

    def test_returns_none_for_malformed_json(self):
        """_parse_jsonl_line returns None for malformed JSON."""
        from app.engines.cc_engine import _parse_jsonl_line

        assert _parse_jsonl_line("not json") is None
        assert _parse_jsonl_line("{broken") is None


# ---------------------------------------------------------------------------
# AC3: load_config is generic
# ---------------------------------------------------------------------------


class TestLoadConfigGeneric:
    """AC3: load_config returns T, not BaseModel, eliminating cast at app.py:90."""

    def test_load_config_signature_is_generic(self):
        """load_config function must use generic TypeVar return, not BaseModel.

        After fix, the signature is:
            def load_config[T: BaseModel](config_path, data_model: type[T]) -> T

        We detect this by checking the return annotation is NOT 'BaseModel'.
        Before fix: return annotation is BaseModel.
        After fix: return annotation is a TypeVar T (not BaseModel).
        """
        from pydantic import BaseModel as PydanticBaseModel

        from app.utils.load_configs import load_config

        hints = load_config.__annotations__
        return_annotation = hints.get("return")

        # After fix: return annotation should be a TypeVar, not BaseModel itself.
        # TypeVar is NOT equal to BaseModel.
        # If this fails, the function still returns BaseModel (not generic).
        assert return_annotation is not PydanticBaseModel, (
            "load_config still returns BaseModel instead of generic T. "
            "Fix AC3: change signature to def load_config[T: BaseModel](...) -> T"
        )

    def test_app_py_has_no_type_ignore_for_load_config(self):
        """app.py:90 must not have type: ignore for reportAttributeAccessIssue.

        AC3: Once load_config is generic, chat_config has type ChatConfig and
        chat_config.prompts is accessible without type: ignore.
        """
        from pathlib import Path

        src_file = Path("src/app/app.py")
        source = src_file.read_text()

        # The specific type: ignore for reportAttributeAccessIssue at line 90 should be removed
        assert "reportAttributeAccessIssue" not in source, (
            "app.py still has reportAttributeAccessIssue type: ignore. "
            "Fix AC3: make load_config generic so ChatConfig attributes are accessible."
        )


# ---------------------------------------------------------------------------
# AC4: model_info in ReviewGenerationResult uses actual model name
# ---------------------------------------------------------------------------


class TestReviewGenerationResultModelInfo:
    """AC4: model_info must not be hardcoded to 'GPT-4o via PydanticAI'."""

    def test_save_structured_review_model_info_not_hardcoded(self):
        """save_structured_review must not set model_info to hardcoded string.

        AC4: The 'GPT-4o via PydanticAI' string should not appear in peerread_tools.py.
        """
        from pathlib import Path

        src_file = Path("src/app/tools/peerread_tools.py")
        source = src_file.read_text()

        # The hardcoded string 'GPT-4o via PydanticAI' must NOT appear in the source
        assert "GPT-4o via PydanticAI" not in source, (
            "Hardcoded model_info 'GPT-4o via PydanticAI' found in peerread_tools.py. "
            "Fix AC4: derive model_info from actual model name."
        )


# ---------------------------------------------------------------------------
# AC5: time.sleep removed from evaluate_single_traditional
# ---------------------------------------------------------------------------


class TestEvaluateSingleTraditionalNoSleepStory008:
    """AC5: time.sleep(0.001) removed from evaluate_single_traditional."""

    def test_evaluate_single_traditional_does_not_call_sleep(self):
        """evaluate_single_traditional must not call time.sleep.

        If time.sleep is present, mock will capture it and this test will fail (RED).
        After fix, time.sleep won't be called (GREEN).
        """
        from app.judge.traditional_metrics import evaluate_single_traditional

        with patch("app.judge.traditional_metrics.time") as mock_time:
            # Allow perf_counter to return real values
            import time

            mock_time.perf_counter.side_effect = time.perf_counter

            evaluate_single_traditional(
                agent_output="This paper presents a novel approach.",
                reference_texts=["The work demonstrates strong contribution."],
            )
            # time.sleep must NOT be called
            mock_time.sleep.assert_not_called()


# ---------------------------------------------------------------------------
# AC6: baseline_comparison.compare handles empty metric_deltas
# ---------------------------------------------------------------------------


class TestBaselineComparisonEmptyMetrics:
    """AC6: compare() handles empty metric_deltas without ZeroDivisionError."""

    def _make_empty_metric_result(self) -> Any:
        """Create a CompositeResult with empty metric_scores."""
        from app.data_models.evaluation_models import CompositeResult

        return CompositeResult(
            composite_score=0.5,
            recommendation="weak_accept",
            recommendation_weight=0.7,
            metric_scores={},  # empty — triggers division by zero in avg_delta calc
            tier1_score=0.5,
            tier2_score=None,
            tier3_score=0.5,
            evaluation_complete=False,
        )

    def test_compare_does_not_raise_zero_division_on_empty_metrics(self):
        """compare() with empty metric_deltas must not raise ZeroDivisionError.

        AC6: Line 87 divides by len(metric_deltas). Guard added for empty case.
        """
        from app.judge.baseline_comparison import compare

        result_a = self._make_empty_metric_result()
        result_b = self._make_empty_metric_result()

        # This would raise ZeroDivisionError before the fix
        comparison = compare(result_a, result_b, "A", "B")

        # Should return a valid BaselineComparison
        from app.judge.baseline_comparison import BaselineComparison

        assert isinstance(comparison, BaselineComparison)
        assert comparison.metric_deltas == {}

    def test_compare_summary_for_empty_metrics(self):
        """compare() summary is valid string when metric_deltas is empty."""
        from app.judge.baseline_comparison import compare

        result_a = self._make_empty_metric_result()
        result_b = self._make_empty_metric_result()

        comparison = compare(result_a, result_b, "SystemA", "SystemB")
        assert isinstance(comparison.summary, str)
        assert len(comparison.summary) > 0


# ---------------------------------------------------------------------------
# AC7: run_sweep.py uses config_data.get("repetitions", 3)
# ---------------------------------------------------------------------------


class TestRunSweepConfigRepetitions:
    """AC7: _load_config_from_file uses .get("repetitions", 3) not ["repetitions"]."""

    def test_load_config_without_repetitions_key_does_not_raise(self, tmp_path: Path):
        """_load_config_from_file succeeds when 'repetitions' key is missing.

        AC7: config_data["repetitions"] raises KeyError if missing;
        config_data.get("repetitions", 3) returns default 3 instead.
        """
        # Ensure run_sweep module functions are importable
        # run_sweep.py is at src/run_sweep.py, so we need to import it carefully
        config_data = {
            "compositions": [
                {
                    "include_researcher": True,
                    "include_analyst": False,
                    "include_synthesiser": False,
                }
            ],
            "paper_ids": ["1234"],
            "output_dir": str(tmp_path / "output"),
            # 'repetitions' key intentionally omitted
        }
        config_file = tmp_path / "sweep.json"
        config_file.write_text(json.dumps(config_data))

        # Import _load_config_from_file via run_sweep
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "run_sweep_story008",
            Path("src/run_sweep.py"),
        )
        assert spec is not None
        run_sweep_mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(run_sweep_mod)  # type: ignore[union-attr]

        # Before fix: KeyError on missing 'repetitions'
        # After fix: returns SweepConfig with repetitions=3 (default)
        result = run_sweep_mod._load_config_from_file(config_file)

        assert result is not None, (
            "_load_config_from_file returned None. "
            "If 'repetitions' key is required (KeyError path), fix to use .get(..., 3)."
        )
        assert result.repetitions == 3

    def test_load_config_with_repetitions_key_uses_provided_value(self, tmp_path: Path):
        """_load_config_from_file uses provided 'repetitions' value when present."""
        import importlib.util

        config_data = {
            "compositions": [
                {
                    "include_researcher": True,
                    "include_analyst": False,
                    "include_synthesiser": False,
                }
            ],
            "paper_ids": ["1234"],
            "output_dir": str(tmp_path / "output"),
            "repetitions": 5,
        }
        config_file = tmp_path / "sweep_with_reps.json"
        config_file.write_text(json.dumps(config_data))

        spec = importlib.util.spec_from_file_location(
            "run_sweep_story008_b",
            Path("src/run_sweep.py"),
        )
        assert spec is not None
        run_sweep_mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(run_sweep_mod)  # type: ignore[union-attr]

        result = run_sweep_mod._load_config_from_file(config_file)

        assert result is not None
        assert result.repetitions == 5


# ---------------------------------------------------------------------------
# AC1: sweep_runner._call_main return type (TypedDict)
# ---------------------------------------------------------------------------


class TestSweepRunnerTypedReturnDict:
    """AC1: _prepare_result_dict return typed as TypedDict with composite_result: CompositeResult | None."""

    def test_sweep_runner_has_no_type_ignore_return_value(self):
        """sweep_runner.py must not have # type: ignore[return-value] at line 104.

        AC1: Once _prepare_result_dict returns a TypedDict with composite_result: CompositeResult | None,
        the return-value type: ignore is no longer needed.
        """
        from pathlib import Path

        src_file = Path("src/app/benchmark/sweep_runner.py")
        source = src_file.read_text()

        assert "type: ignore[return-value]" not in source, (
            "sweep_runner.py still has # type: ignore[return-value]. "
            "Fix AC1: type _prepare_result_dict return as TypedDict with "
            "composite_result: CompositeResult | None."
        )

    def test_prepare_result_dict_composite_result_key_typed(self):
        """_prepare_result_dict returns correct structure with composite_result key."""
        from app.app import _prepare_result_dict
        from app.data_models.evaluation_models import CompositeResult

        composite = CompositeResult(
            composite_score=0.8,
            recommendation="accept",
            recommendation_weight=1.0,
            metric_scores={"metric_a": 0.8},
            tier1_score=0.8,
            tier2_score=None,
            tier3_score=0.8,
            evaluation_complete=False,
        )

        result = _prepare_result_dict(composite, None, "exec-123")

        assert result is not None
        assert "composite_result" in result
        assert result["composite_result"] is composite
        assert result["execution_id"] == "exec-123"

    def test_prepare_result_dict_none_case(self):
        """_prepare_result_dict returns None when both composite_result and graph are None."""
        from app.app import _prepare_result_dict

        assert _prepare_result_dict(None, None) is None
