"""Tests for RunContext wiring in app.main() and engine paths.

Verifies that engine paths create RunContext, set the singleton,
pass run_dir to evaluation, and clean up on completion/error.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _reset_run_context():
    """Reset the active run context singleton before and after each test."""
    from app.utils.run_context import set_active_run_context

    set_active_run_context(None)
    yield
    set_active_run_context(None)


class TestMasEnginePathRunContext:
    """Tests for RunContext creation in _run_mas_engine_path."""

    @pytest.fixture
    def _mock_agent_execution(self):
        """Patch _run_agent_execution to return a known execution_id."""
        with patch(
            "app.app._run_agent_execution",
            new_callable=AsyncMock,
            return_value=("exec-abcd1234", {}, MagicMock()),
        ) as m:
            yield m

    @pytest.fixture
    def _mock_eval(self):
        """Patch _run_evaluation_if_enabled to return None."""
        with patch(
            "app.app._run_evaluation_if_enabled",
            new_callable=AsyncMock,
            return_value=None,
        ) as m:
            yield m

    @pytest.fixture
    def _mock_graph(self):
        """Patch _build_graph_from_trace to return None."""
        with patch("app.app._build_graph_from_trace", return_value=None) as m:
            yield m

    @pytest.mark.usefixtures("_mock_agent_execution", "_mock_graph")
    async def test_creates_run_context(self, tmp_path: Path, _mock_eval: AsyncMock) -> None:
        """_run_mas_engine_path creates a RunContext when execution_id is present."""
        from app.app import _run_mas_engine_path

        with patch("app.app.RunContext") as mock_rc_cls:
            mock_ctx = MagicMock()
            mock_ctx.run_dir = tmp_path / "run"
            mock_rc_cls.create.return_value = mock_ctx

            await _run_mas_engine_path(
                chat_config_file="config.yaml",
                chat_provider="test",
                query="test",
                paper_id="1105.1072",
                enable_review_tools=False,
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                token_limit=None,
                skip_eval=True,
                cc_solo_dir=None,
                cc_teams_dir=None,
                cc_teams_tasks_dir=None,
                judge_settings=None,
            )

            mock_rc_cls.create.assert_called_once_with(
                engine_type="mas",
                paper_id="1105.1072",
                execution_id="exec-abcd1234",
            )

    @pytest.mark.usefixtures("_mock_agent_execution", "_mock_graph")
    async def test_passes_run_dir_to_evaluation(
        self, tmp_path: Path, _mock_eval: AsyncMock
    ) -> None:
        """_run_mas_engine_path passes run_dir to evaluation."""
        from app.app import _run_mas_engine_path

        run_dir = tmp_path / "run"
        with patch("app.app.RunContext") as mock_rc_cls:
            mock_ctx = MagicMock()
            mock_ctx.run_dir = run_dir
            mock_rc_cls.create.return_value = mock_ctx

            await _run_mas_engine_path(
                chat_config_file="config.yaml",
                chat_provider="test",
                query="test",
                paper_id=None,
                enable_review_tools=False,
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                token_limit=None,
                skip_eval=True,
                cc_solo_dir=None,
                cc_teams_dir=None,
                cc_teams_tasks_dir=None,
                judge_settings=None,
            )

            _, kwargs = _mock_eval.call_args
            assert kwargs["run_dir"] == run_dir

    @pytest.mark.usefixtures("_mock_agent_execution", "_mock_graph")
    async def test_sets_active_run_context(self, tmp_path: Path, _mock_eval: AsyncMock) -> None:
        """_run_mas_engine_path sets the active run context singleton."""
        from app.app import _run_mas_engine_path
        from app.utils.run_context import get_active_run_context

        with patch("app.app.RunContext") as mock_rc_cls:
            mock_ctx = MagicMock()
            mock_ctx.run_dir = tmp_path / "run"
            mock_rc_cls.create.return_value = mock_ctx

            await _run_mas_engine_path(
                chat_config_file="config.yaml",
                chat_provider="test",
                query="test",
                paper_id="p1",
                enable_review_tools=False,
                include_researcher=False,
                include_analyst=False,
                include_synthesiser=False,
                token_limit=None,
                skip_eval=True,
                cc_solo_dir=None,
                cc_teams_dir=None,
                cc_teams_tasks_dir=None,
                judge_settings=None,
            )

            assert get_active_run_context() is mock_ctx


class TestCcEnginePathRunContext:
    """Tests for RunContext creation in _run_cc_engine_path."""

    @pytest.fixture
    def _mock_cc_artifacts(self):
        """Patch _extract_cc_artifacts to return known values."""
        with patch(
            "app.app._extract_cc_artifacts",
            return_value=("cc-exec-5678", MagicMock()),
        ) as m:
            yield m

    @pytest.fixture
    def _mock_eval(self):
        """Patch _run_evaluation_if_enabled to return None."""
        with patch(
            "app.app._run_evaluation_if_enabled",
            new_callable=AsyncMock,
            return_value=None,
        ) as m:
            yield m

    @pytest.fixture
    def _mock_extract_review(self):
        """Patch extract_cc_review_text."""
        with patch("app.engines.cc_engine.extract_cc_review_text", return_value="review text") as m:
            yield m

    @pytest.mark.usefixtures("_mock_cc_artifacts", "_mock_extract_review")
    async def test_creates_run_context(self, tmp_path: Path, _mock_eval: AsyncMock) -> None:
        """_run_cc_engine_path creates a RunContext."""
        from app.app import _run_cc_engine_path

        with patch("app.app.RunContext") as mock_rc_cls:
            mock_ctx = MagicMock()
            mock_ctx.run_dir = tmp_path / "run"
            mock_rc_cls.create.return_value = mock_ctx

            await _run_cc_engine_path(
                cc_result=MagicMock(),
                skip_eval=True,
                paper_id="p1",
                cc_solo_dir=None,
                cc_teams_dir=None,
                cc_teams_tasks_dir=None,
                chat_provider="test",
                judge_settings=None,
                cc_teams=False,
            )

            mock_rc_cls.create.assert_called_once_with(
                engine_type="cc_solo",
                paper_id="p1",
                execution_id="cc-exec-5678",
            )

    @pytest.mark.usefixtures("_mock_cc_artifacts", "_mock_extract_review")
    async def test_uses_cc_teams_engine_type(self, tmp_path: Path, _mock_eval: AsyncMock) -> None:
        """_run_cc_engine_path uses 'cc_teams' engine_type when cc_teams=True."""
        from app.app import _run_cc_engine_path

        with patch("app.app.RunContext") as mock_rc_cls:
            mock_ctx = MagicMock()
            mock_ctx.run_dir = tmp_path / "run"
            mock_rc_cls.create.return_value = mock_ctx

            await _run_cc_engine_path(
                cc_result=MagicMock(),
                skip_eval=True,
                paper_id="p1",
                cc_solo_dir=None,
                cc_teams_dir=None,
                cc_teams_tasks_dir=None,
                chat_provider="test",
                judge_settings=None,
                cc_teams=True,
            )

            mock_rc_cls.create.assert_called_once_with(
                engine_type="cc_teams",
                paper_id="p1",
                execution_id="cc-exec-5678",
            )


class TestPrepareResultDict:
    """Tests for run_context inclusion in _prepare_result_dict."""

    def test_includes_run_context(self, tmp_path: Path) -> None:
        """_prepare_result_dict includes run_context when provided."""
        from app.app import _prepare_result_dict
        from app.utils.run_context import RunContext

        ctx = RunContext(
            engine_type="mas",
            paper_id="p1",
            execution_id="e1",
            start_time=__import__("datetime").datetime(2026, 3, 1),
            run_dir=tmp_path,
        )
        result = _prepare_result_dict(MagicMock(), MagicMock(), "e1", run_context=ctx)
        assert result is not None
        assert result["run_context"] is ctx

    def test_run_context_none_when_not_set(self) -> None:
        """_prepare_result_dict returns None run_context when not provided."""
        from app.app import _prepare_result_dict

        result = _prepare_result_dict(MagicMock(), MagicMock(), "e1")
        assert result is not None
        assert result["run_context"] is None


class TestMainCleanup:
    """Tests for active RunContext cleanup in main()."""

    async def test_clears_active_run_context_after_completion(self, tmp_path: Path) -> None:
        """main() clears active run context in finally block on success."""
        from app.utils.run_context import (
            RunContext,
            get_active_run_context,
            set_active_run_context,
        )

        ctx = RunContext(
            engine_type="mas",
            paper_id="p1",
            execution_id="e1",
            start_time=__import__("datetime").datetime(2026, 3, 1),
            run_dir=tmp_path,
        )
        set_active_run_context(ctx)

        with (
            patch("app.app.resolve_config_path", return_value="config.yaml"),
            patch(
                "app.app._run_mas_engine_path",
                new_callable=AsyncMock,
                return_value=(None, None, None),
            ),
        ):
            from app.app import main

            await main()

        assert get_active_run_context() is None

    async def test_clears_active_run_context_on_exception(self, tmp_path: Path) -> None:
        """main() clears active run context in finally block on exception."""
        from app.utils.run_context import (
            RunContext,
            get_active_run_context,
            set_active_run_context,
        )

        ctx = RunContext(
            engine_type="mas",
            paper_id="p1",
            execution_id="e1",
            start_time=__import__("datetime").datetime(2026, 3, 1),
            run_dir=tmp_path,
        )
        set_active_run_context(ctx)

        with (
            patch("app.app.resolve_config_path", return_value="config.yaml"),
            patch(
                "app.app._run_mas_engine_path",
                new_callable=AsyncMock,
                side_effect=RuntimeError("boom"),
            ),
            pytest.raises(Exception),
        ):
            from app.app import main

            await main()

        assert get_active_run_context() is None
