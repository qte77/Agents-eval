"""Tests for STORY-009: ReviewPersistence writer migration to RunContext.

AC4: ReviewPersistence.save_review() writes to run_context.review_path
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.data_models.peerread_models import PeerReadReview
from app.data_utils.review_persistence import ReviewPersistence
from app.utils.run_context import RunContext


class TestReviewPersistenceSaveToRunContext:
    """AC4: ReviewPersistence.save_review() writes to run_context.review_path."""

    def _make_review(self) -> PeerReadReview:
        """Create a minimal PeerReadReview for testing."""
        return PeerReadReview(
            comments="Good paper",
            RECOMMENDATION=5,
            SUBSTANCE=3,
            CLARITY=4,
        )

    def test_save_review_accepts_run_dir(self, tmp_path: Path) -> None:
        """ReviewPersistence.save_review() accepts a run_dir parameter."""
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        rp = ReviewPersistence(reviews_dir=str(tmp_path / "fallback"))
        review = self._make_review()

        with patch("app.utils.artifact_registry.get_artifact_registry") as mock_reg:
            mock_reg.return_value = MagicMock()
            path = rp.save_review("paper_001", review, run_dir=run_dir)

        assert Path(path).parent == run_dir
        assert Path(path).name == "review.json"
        assert Path(path).exists()

    def test_save_review_run_dir_overrides_default(self, tmp_path: Path) -> None:
        """When run_dir is provided, review is saved there, not in default reviews_dir."""
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        default_dir = tmp_path / "default_reviews"
        default_dir.mkdir()

        rp = ReviewPersistence(reviews_dir=str(default_dir))
        review = self._make_review()

        with patch("app.utils.artifact_registry.get_artifact_registry") as mock_reg:
            mock_reg.return_value = MagicMock()
            path = rp.save_review("paper_001", review, run_dir=run_dir)

        # Written to run_dir, not default_dir
        assert str(run_dir) in str(path)
        assert str(default_dir) not in str(path)

    def test_save_review_without_run_dir_uses_legacy(self, tmp_path: Path) -> None:
        """When run_dir is not provided, save_review uses legacy timestamp behavior."""
        with patch("pathlib.Path.mkdir"):
            rp = ReviewPersistence(reviews_dir=str(tmp_path))
        review = self._make_review()

        with patch("app.utils.artifact_registry.get_artifact_registry") as mock_reg:
            mock_reg.return_value = MagicMock()
            path = rp.save_review("paper_001", review)

        # Legacy behavior: filename contains paper_id and timestamp
        assert "paper_001" in Path(path).name


class TestReviewLoaderDeleted:
    """AC7: review_loader.py is deleted — dead code."""

    def test_review_loader_module_does_not_exist(self) -> None:
        """review_loader.py module cannot be imported after deletion."""
        import importlib

        with __import__("pytest").raises(ModuleNotFoundError):
            importlib.import_module("app.data_utils.review_loader")
