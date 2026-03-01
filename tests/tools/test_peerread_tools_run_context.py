"""Tests for RunContext wiring in PeerRead tool closures.

Verifies that save_paper_review and save_structured_review use the active
RunContext to pass run_dir to ReviewPersistence.save_review().
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conftest import capture_registered_tools


@pytest.fixture(autouse=True)
def _reset_run_context():
    """Reset active run context before and after each test."""
    from app.utils.run_context import set_active_run_context

    set_active_run_context(None)
    yield
    set_active_run_context(None)


class TestSavePaperReviewRunContext:
    """Tests for save_paper_review using active RunContext."""

    @pytest.fixture
    def save_paper_review(self):
        """Capture the save_paper_review tool function."""
        from app.tools.peerread_tools import add_peerread_review_tools_to_agent

        tools = capture_registered_tools(add_peerread_review_tools_to_agent)
        return tools["save_paper_review"]

    async def test_uses_active_run_context(self, save_paper_review, tmp_path: Path) -> None:
        """save_paper_review passes run_dir from active RunContext to save_review."""
        from app.utils.run_context import RunContext, set_active_run_context

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="mas",
            paper_id="p1",
            execution_id="e1",
            start_time=__import__("datetime").datetime(2026, 3, 1),
            run_dir=run_dir,
        )
        set_active_run_context(ctx)

        with patch("app.tools.peerread_tools.ReviewPersistence") as mock_persist_cls:
            mock_persist = MagicMock()
            mock_persist.save_review.return_value = str(run_dir / "review.json")
            mock_persist_cls.return_value = mock_persist

            with patch("app.tools.peerread_tools.get_trace_collector") as mock_tc:
                mock_tc.return_value = MagicMock()
                await save_paper_review(None, paper_id="p1", review_text="Good paper")

            _, kwargs = mock_persist.save_review.call_args
            assert kwargs["run_dir"] == run_dir

    async def test_falls_back_without_context(self, save_paper_review) -> None:
        """save_paper_review passes run_dir=None when no active RunContext."""
        with patch("app.tools.peerread_tools.ReviewPersistence") as mock_persist_cls:
            mock_persist = MagicMock()
            mock_persist.save_review.return_value = "/some/path.json"
            mock_persist_cls.return_value = mock_persist

            with patch("app.tools.peerread_tools.get_trace_collector") as mock_tc:
                mock_tc.return_value = MagicMock()
                await save_paper_review(None, paper_id="p1", review_text="Good paper")

            _, kwargs = mock_persist.save_review.call_args
            assert kwargs["run_dir"] is None


class TestSaveStructuredReviewRunContext:
    """Tests for save_structured_review using active RunContext."""

    @pytest.fixture
    def save_structured_review(self):
        """Capture the save_structured_review tool function."""
        from app.tools.peerread_tools import add_peerread_review_tools_to_agent

        tools = capture_registered_tools(add_peerread_review_tools_to_agent)
        return tools["save_structured_review"]

    async def test_uses_active_run_context(self, save_structured_review, tmp_path: Path) -> None:
        """save_structured_review passes run_dir from active RunContext."""
        from app.utils.run_context import RunContext, set_active_run_context

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        ctx = RunContext(
            engine_type="mas",
            paper_id="p1",
            execution_id="e1",
            start_time=__import__("datetime").datetime(2026, 3, 1),
            run_dir=run_dir,
        )
        set_active_run_context(ctx)

        mock_review = MagicMock()
        mock_review.to_peerread_format.return_value = {
            "comments": "Good",
            "recommendation": "accept",
            "reviewer_confidence": "4",
        }

        with (
            patch("app.tools.peerread_tools.ReviewPersistence") as mock_persist_cls,
            patch("app.tools.peerread_tools.get_trace_collector") as mock_tc,
            patch("app.tools.peerread_tools.PeerReadReview") as mock_pr_cls,
            patch("app.tools.peerread_tools.ReviewGenerationResult") as mock_rgr_cls,
        ):
            mock_persist = MagicMock()
            mock_persist.save_review.return_value = str(run_dir / "review.json")
            mock_persist_cls.return_value = mock_persist
            mock_tc.return_value = MagicMock()
            mock_pr_cls.model_validate.return_value = MagicMock()
            mock_rgr_cls.return_value = MagicMock(model_dump=MagicMock(return_value={}))

            await save_structured_review(None, paper_id="p1", structured_review=mock_review)

            _, kwargs = mock_persist.save_review.call_args
            assert kwargs["run_dir"] == run_dir
