"""Tests for RunContext wiring in app.main() and engine paths.

Verifies that RunContext is created up-front in main() *before* engine
execution starts, so artifacts written during execution can use per-run
directories. Also tests result dict preparation and singleton cleanup.
"""

from __future__ import annotations

import re
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


class TestUpFrontRunContext:
    """Tests that RunContext is active *before* engine execution begins."""

    @pytest.fixture
    def _mock_run_context(self):
        """Patch RunContext.create to return a mock without creating directories."""
        with patch("app.app.RunContext") as mock_rc_cls:
            mock_ctx = MagicMock()
            mock_ctx.run_dir = None
            mock_rc_cls.create.return_value = mock_ctx
            yield mock_rc_cls

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

    @pytest.mark.usefixtures("_mock_eval", "_mock_graph", "_mock_run_context")
    async def test_run_context_active_before_mas_execution(self) -> None:
        """RunContext singleton is set *before* _run_agent_execution runs."""
        from app.utils.run_context import get_active_run_context

        captured_ctx: list[object] = []

        async def _capture_side_effect(*args, **kwargs):
            """Capture the active RunContext at the moment of execution."""
            captured_ctx.append(get_active_run_context())
            return ("exec-abc123", {}, MagicMock())

        with (
            patch(
                "app.app._run_agent_execution",
                new_callable=AsyncMock,
                side_effect=_capture_side_effect,
            ),
            patch("app.app.resolve_config_path", return_value="config.yaml"),
        ):
            from app.app import main

            await main(chat_provider="test", query="test", skip_eval=True)

        assert len(captured_ctx) == 1, "Side-effect should fire exactly once"
        assert captured_ctx[0] is not None, (
            "RunContext must be active before _run_agent_execution"
        )

    @pytest.mark.usefixtures("_mock_eval", "_mock_run_context")
    async def test_run_context_active_before_cc_execution(self) -> None:
        """RunContext singleton is set *before* _extract_cc_artifacts runs."""
        from app.utils.run_context import get_active_run_context

        captured_ctx: list[object] = []

        def _capture_side_effect(cc_result):
            """Capture the active RunContext at the moment of artifact extraction."""
            captured_ctx.append(get_active_run_context())
            return ("cc-exec-123", MagicMock())

        mock_cc_result = MagicMock()
        mock_cc_result.execution_id = "cc-exec-123"

        with (
            patch("app.app._extract_cc_artifacts", side_effect=_capture_side_effect),
            patch("app.app.resolve_config_path", return_value="config.yaml"),
            patch("app.engines.cc_engine.extract_cc_review_text", return_value="review"),
        ):
            from app.app import main

            await main(
                chat_provider="test",
                query="test",
                engine="cc",
                cc_result=mock_cc_result,
                skip_eval=True,
            )

        assert len(captured_ctx) == 1, "Side-effect should fire exactly once"
        assert captured_ctx[0] is not None, (
            "RunContext must be active before _extract_cc_artifacts"
        )

    async def test_run_context_receives_pre_generated_execution_id(self) -> None:
        """RunContext.create() receives a uuid-pattern execution_id from main()."""
        with (
            patch("app.app.resolve_config_path", return_value="config.yaml"),
            patch(
                "app.app._run_mas_engine_path",
                new_callable=AsyncMock,
                return_value=(None, None, None),
            ),
            patch("app.app.RunContext") as mock_rc_cls,
        ):
            mock_ctx = MagicMock()
            mock_ctx.run_dir = None
            mock_rc_cls.create.return_value = mock_ctx

            from app.app import main

            await main(chat_provider="test", query="test", skip_eval=True)

            # RunContext.create() should be called with exec_{hex12} pattern
            mock_rc_cls.create.assert_called_once()
            call_kwargs = mock_rc_cls.create.call_args[1]
            exec_id = call_kwargs.get("execution_id", "")
            assert re.match(r"^exec_[0-9a-f]{12}$", exec_id), (
                f"execution_id should match exec_{{hex12}}, got {exec_id!r}"
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
