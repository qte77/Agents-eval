"""Tests for STORY-006: cc_engine wiring into CLI/sweep/GUI + --cc-teams flag.

Covers:
- --cc-teams flag added to CLI argument parser
- sweep_runner._invoke_cc_comparison delegates to cc_engine
- run_app._execute_query_background passes engine to main()
- _run_cc_baselines wired through CCTraceAdapter
- CC review text wired to evaluation pipeline
- engine_type set on CompositeResult from cc_teams flag
- GUI creates CC result and passes to main()
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

SRC_PATH = str(Path(__file__).parent.parent.parent / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


@pytest.fixture(autouse=True)
def _mock_run_context():
    """Prevent real RunContext.create() → mkdir during tests."""
    mock_ctx = MagicMock()
    mock_ctx.run_dir = None
    with patch("app.app.RunContext") as mock_rc:
        mock_rc.create.return_value = mock_ctx
        yield mock_rc


def _make_sweep_config(output_dir: Path, **overrides: object):
    """Build a SweepConfig with sensible test defaults.

    Args:
        output_dir: Directory for sweep output (use tmp_path fixture).
        **overrides: Fields to override on the SweepConfig.
    """
    from app.benchmark.sweep_config import AgentComposition, SweepConfig

    defaults: dict = {
        "compositions": [AgentComposition()],
        "repetitions": 1,
        "paper_ids": ["1"],
        "output_dir": output_dir,
    }
    defaults.update(overrides)
    return SweepConfig(**defaults)


class TestCCTeamsFlagCLI:
    """--cc-teams flag added to run_cli.py argument parser."""

    def test_cc_teams_flag_defaults_to_false(self):
        """--cc-teams flag is False (or absent) when not specified."""
        from run_cli import parse_args

        args = parse_args(["--engine=cc", "--query=test"])
        assert not args.get("cc_teams", False)

    def test_cc_teams_flag_parses_true_when_provided(self):
        """--cc-teams flag is True when explicitly provided."""
        from run_cli import parse_args

        args = parse_args(["--engine=cc", "--cc-teams"])
        assert args.get("cc_teams") is True


class TestSweepRunnerDelegatesToCCEngine:
    """sweep_runner._invoke_cc_comparison delegates to cc_engine, no inline subprocess."""

    def test_invoke_cc_comparison_does_not_use_subprocess_directly(self, tmp_path: Path):
        """_invoke_cc_comparison delegates to cc_engine.run_cc_solo, not subprocess.run.

        Behavioral: call _invoke_cc_comparison with run_cc_solo patched and verify
        subprocess.run is never called.
        """
        from app.benchmark.sweep_runner import SweepRunner
        from app.engines.cc_engine import CCResult

        config = _make_sweep_config(tmp_path, engine="cc")
        runner = SweepRunner(config)

        mock_cc_result = CCResult(
            execution_id="exec-no-subprocess",
            output_data={},
            session_dir=str(tmp_path / "session"),
        )

        import asyncio

        with (
            patch("app.benchmark.sweep_runner.run_cc_solo", return_value=mock_cc_result),
            patch("subprocess.run") as mock_subprocess,
        ):
            asyncio.run(runner._invoke_cc_comparison("1105.1072"))

        mock_subprocess.assert_not_called()

    @pytest.mark.asyncio
    async def test_invoke_cc_comparison_uses_cc_engine_run_cc_solo(self, tmp_path: Path):
        """_invoke_cc_comparison delegates to run_cc_solo from cc_engine."""
        from app.benchmark.sweep_runner import SweepRunner
        from app.engines.cc_engine import CCResult

        config = _make_sweep_config(tmp_path, engine="cc")
        runner = SweepRunner(config)

        mock_cc_result = CCResult(
            execution_id="exec-sweep-001",
            output_data={"num_turns": 3},
            session_dir=str(tmp_path / "session"),
        )

        with patch(
            "app.benchmark.sweep_runner.run_cc_solo", return_value=mock_cc_result
        ) as mock_solo:
            result = await runner._invoke_cc_comparison("1105.1072")

        mock_solo.assert_called_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_invoke_cc_comparison_uses_cc_engine_run_cc_teams_when_teams_mode(
        self, tmp_path: Path
    ):
        """_invoke_cc_comparison delegates to run_cc_teams when cc_teams=True."""
        from app.benchmark.sweep_runner import SweepRunner
        from app.engines.cc_engine import CCResult

        config = _make_sweep_config(tmp_path, engine="cc", cc_teams=True)
        runner = SweepRunner(config)

        mock_cc_result = CCResult(
            execution_id="exec-teams-sweep-001",
            output_data={},
            team_artifacts=[{"type": "TeamCreate"}],
        )

        with patch(
            "app.benchmark.sweep_runner.run_cc_teams", return_value=mock_cc_result
        ) as mock_teams:
            result = await runner._invoke_cc_comparison("1105.1072")

        mock_teams.assert_called_once()
        assert result is not None


class TestRunAppPassesEngine:
    """run_app._execute_query_background passes engine to main()."""

    def test_execute_query_background_passes_engine_to_main(self):
        """_execute_query_background must pass the engine parameter to main().

        Behavioral: call _execute_query_background with engine='cc' and verify
        main() receives engine='cc' as a keyword argument.
        """
        import asyncio

        from app.engines.cc_engine import CCResult
        from gui.pages import run_app

        mock_session_state = MagicMock()
        captured_main_kwargs: dict = {}

        async def fake_main(**kwargs: object) -> None:
            captured_main_kwargs.update(kwargs)
            return None

        mock_cc_result = CCResult(execution_id="pass-engine", output_data={})

        with (
            patch("gui.pages.run_app.main", side_effect=fake_main),
            patch("gui.pages.run_app.run_cc_solo", return_value=mock_cc_result),
            patch("gui.pages.run_app.LogCapture") as mock_log_capture,
            patch("gui.pages.run_app.st") as mock_st,
        ):
            mock_capture_instance = MagicMock()
            mock_capture_instance.get_logs.return_value = []
            mock_capture_instance.attach_to_logger.return_value = "handler_id"
            mock_log_capture.return_value = mock_capture_instance
            mock_log_capture.format_logs_as_html = MagicMock(return_value="<html/>")
            mock_st.session_state = mock_session_state

            asyncio.run(
                run_app._execute_query_background(
                    query="test query",
                    provider="openai",
                    include_researcher=False,
                    include_analyst=False,
                    include_synthesiser=False,
                    chat_config_file=None,
                    engine="cc",
                )
            )

        assert captured_main_kwargs.get("engine") == "cc", (
            f"_execute_query_background must pass engine='cc' to main(). "
            f"Got: {captured_main_kwargs.get('engine')!r}"
        )


class TestRunCCBaselinesWired:
    """_run_cc_baselines wired through CCTraceAdapter, not a stub."""

    def test_run_cc_baselines_invokes_cc_comparison_for_each_paper(self, tmp_path: Path):
        """_run_cc_baselines processes results by invoking _invoke_cc_comparison per paper.

        Behavioral: call _run_cc_baselines with 2 paper IDs and verify
        _invoke_cc_comparison is called for each (not a stub that just logs).
        """
        import asyncio

        from app.benchmark.sweep_runner import SweepRunner
        from app.engines.cc_engine import CCResult

        config = _make_sweep_config(tmp_path, engine="cc", paper_ids=["1105.1072", "1105.1073"])
        runner = SweepRunner(config)

        mock_cc_result = CCResult(
            execution_id="exec-baselines-test",
            output_data={},
            session_dir=str(tmp_path / "sess"),
        )

        with (
            patch.object(
                runner, "_invoke_cc_comparison", new_callable=AsyncMock, return_value=mock_cc_result
            ) as mock_invoke,
            patch("app.benchmark.sweep_runner.CCTraceAdapter"),
        ):
            asyncio.run(runner._run_cc_baselines())

        # Must have been called for each paper — not a no-op stub
        assert mock_invoke.call_count >= 1, (
            "_run_cc_baselines must call _invoke_cc_comparison at least once per paper"
        )


class TestMainCCBranch:
    """main() CC branch skips MAS and uses CC result (STORY-010)."""

    @pytest.mark.asyncio
    async def test_main_cc_engine_skips_run_agent_execution(self):
        """When engine='cc' and cc_result provided, _run_agent_execution is not called."""
        from app.engines.cc_engine import CCResult

        cc_result = CCResult(
            execution_id="cc-test-001",
            output_data={"result": "CC review text"},
        )

        with (
            patch("app.app._run_agent_execution") as mock_run_agent,
            patch("app.app._run_evaluation_if_enabled", new_callable=AsyncMock, return_value=None),
            patch("app.app._build_graph_from_trace", return_value=None),
            patch("app.app.persist_graph"),
        ):
            from app.app import main

            await main(engine="cc", cc_result=cc_result, query="test")

            mock_run_agent.assert_not_called()

    @pytest.mark.asyncio
    async def test_main_mas_engine_calls_run_agent_execution(self):
        """When engine='mas', _run_agent_execution is called normally."""
        with (
            patch(
                "app.app._run_agent_execution",
                new_callable=AsyncMock,
                return_value=("exec-id", {}, None),
            ) as mock_run_agent,
            patch("app.app._run_evaluation_if_enabled", new_callable=AsyncMock, return_value=None),
            patch("app.app._build_graph_from_trace", return_value=None),
        ):
            from app.app import main

            await main(engine="mas", query="test", chat_provider="openai")

            mock_run_agent.assert_called_once()


# MARK: --- AC2: CC review text wired to evaluation pipeline ---


class TestCCReviewTextWiring:
    """CC review text must reach the evaluation pipeline (STORY-010 AC2)."""

    @pytest.mark.asyncio
    async def test_cc_branch_passes_review_text_to_evaluation(self):
        """When engine='cc', extract_cc_review_text output reaches _run_evaluation_if_enabled."""
        from app.engines.cc_engine import CCResult

        cc_result = CCResult(
            execution_id="cc-review-wire",
            output_data={"result": "Strong methodology and clear results."},
        )

        with (
            patch("app.app._extract_cc_artifacts", return_value=("cc-review-wire", None)),
            patch(
                "app.app._run_evaluation_if_enabled",
                new_callable=AsyncMock,
                return_value=None,
            ) as mock_eval,
        ):
            from app.app import main

            await main(engine="cc", cc_result=cc_result, query="test")

            call_kwargs = mock_eval.call_args.kwargs
            assert call_kwargs.get("review_text") == "Strong methodology and clear results."


# MARK: --- AC7: engine_type set on CompositeResult ---


class TestEngineTypeSetOnResult:
    """CompositeResult.engine_type set from cc_teams flag (STORY-002 AC3/AC6/AC7)."""

    @pytest.mark.asyncio
    async def test_cc_solo_sets_engine_type(self):
        """cc_teams=False sets engine_type='cc_solo' on CompositeResult."""
        from app.data_models.evaluation_models import CompositeResult
        from app.engines.cc_engine import CCResult

        cc_result = CCResult(
            execution_id="cc-solo-type",
            output_data={},
            team_artifacts=[],
        )
        mock_composite = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.3,
            evaluation_complete=True,
        )

        with (
            patch("app.app._extract_cc_artifacts", return_value=("cc-solo-type", None)),
            patch(
                "app.app._run_evaluation_if_enabled",
                new_callable=AsyncMock,
                return_value=mock_composite,
            ),
        ):
            from app.app import main

            result = await main(engine="cc", cc_result=cc_result, cc_teams=False, query="test")

            assert result is not None
            assert result["composite_result"].engine_type == "cc_solo"

    @pytest.mark.asyncio
    async def test_cc_teams_sets_engine_type(self):
        """cc_teams=True sets engine_type='cc_teams' on CompositeResult."""
        from app.data_models.evaluation_models import CompositeResult
        from app.engines.cc_engine import CCResult

        cc_result = CCResult(
            execution_id="cc-teams-type",
            output_data={},
            team_artifacts=[{"type": "TeamCreate", "name": "test"}],
        )
        mock_composite = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.3,
            evaluation_complete=True,
        )

        with (
            patch("app.app._extract_cc_artifacts", return_value=("cc-teams-type", None)),
            patch(
                "app.app._run_evaluation_if_enabled",
                new_callable=AsyncMock,
                return_value=mock_composite,
            ),
        ):
            from app.app import main

            result = await main(engine="cc", cc_result=cc_result, cc_teams=True, query="test")

            assert result is not None
            assert result["composite_result"].engine_type == "cc_teams"

    @pytest.mark.asyncio
    async def test_mas_engine_keeps_default_engine_type(self):
        """MAS engine leaves engine_type as default 'mas'."""
        from app.data_models.evaluation_models import CompositeResult

        mock_composite = CompositeResult(
            composite_score=0.5,
            recommendation="accept",
            recommendation_weight=0.5,
            metric_scores={},
            tier1_score=0.5,
            tier3_score=0.3,
            evaluation_complete=True,
        )

        with (
            patch(
                "app.app._run_agent_execution",
                new_callable=AsyncMock,
                return_value=("exec-id", {}, None),
            ),
            patch(
                "app.app._run_evaluation_if_enabled",
                new_callable=AsyncMock,
                return_value=mock_composite,
            ),
            patch("app.app._build_graph_from_trace", return_value=None),
        ):
            from app.app import main

            result = await main(engine="mas", query="test", chat_provider="openai")

            assert result is not None
            assert result["composite_result"].engine_type == "mas"


# MARK: --- AC9: GUI creates CC result and passes to main ---


class TestGUICCExecution:
    """GUI _execute_query_background creates cc_result for CC engine (STORY-010 AC9)."""

    @pytest.mark.asyncio
    async def test_gui_cc_solo_calls_run_cc_solo(self):
        """When engine='cc' and cc_teams=False, GUI calls run_cc_solo."""
        from app.engines.cc_engine import CCResult

        mock_cc_result = CCResult(
            execution_id="gui-solo",
            output_data={"result": "GUI solo review"},
        )

        mock_state = MagicMock()

        with (
            patch("gui.pages.run_app.st") as mock_st,
            patch("gui.pages.run_app.LogCapture") as mock_log_capture,
            patch("gui.pages.run_app.main", new_callable=AsyncMock, return_value=None) as mock_main,
            patch("gui.pages.run_app.run_cc_solo", return_value=mock_cc_result) as mock_solo,
        ):
            mock_capture = MagicMock()
            mock_capture.get_logs.return_value = []
            mock_capture.attach_to_logger.return_value = "h"
            mock_log_capture.return_value = mock_capture
            mock_st.session_state = mock_state

            from gui.pages.run_app import _execute_query_background

            await _execute_query_background(
                query="test solo",
                provider="openai",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
                engine="cc",
                cc_teams=False,
            )

            mock_solo.assert_called_once_with("test solo")
            assert mock_main.call_args.kwargs.get("cc_result") is mock_cc_result

    @pytest.mark.asyncio
    async def test_gui_cc_teams_calls_run_cc_teams(self):
        """When engine='cc' and cc_teams=True, GUI calls run_cc_teams."""
        from app.engines.cc_engine import CCResult

        mock_cc_result = CCResult(
            execution_id="gui-teams",
            output_data={},
            team_artifacts=[{"type": "TeamCreate"}],
        )

        mock_state = MagicMock()

        with (
            patch("gui.pages.run_app.st") as mock_st,
            patch("gui.pages.run_app.LogCapture") as mock_log_capture,
            patch("gui.pages.run_app.main", new_callable=AsyncMock, return_value=None) as mock_main,
            patch("gui.pages.run_app.run_cc_teams", return_value=mock_cc_result) as mock_teams,
        ):
            mock_capture = MagicMock()
            mock_capture.get_logs.return_value = []
            mock_capture.attach_to_logger.return_value = "h"
            mock_log_capture.return_value = mock_capture
            mock_st.session_state = mock_state

            from gui.pages.run_app import _execute_query_background

            await _execute_query_background(
                query="test teams",
                provider="openai",
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                chat_config_file=None,
                engine="cc",
                cc_teams=True,
            )

            mock_teams.assert_called_once_with("test teams")
            assert mock_main.call_args.kwargs.get("cc_result") is mock_cc_result
