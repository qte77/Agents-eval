"""Tests for review persistence path resolution.

Validates that reviews are saved under the project root
and NOT under src/app/.
"""

from unittest.mock import patch

from app.data_utils.review_persistence import ReviewPersistence
from app.utils.paths import get_project_root


def test_default_reviews_dir_under_project_root():
    """Test that resolve_project_path anchors reviews under project root, not src/app/."""
    from app.data_utils.review_persistence import _DEFAULT_REVIEWS_DIR
    from app.utils.paths import resolve_project_path

    expected_path = resolve_project_path(_DEFAULT_REVIEWS_DIR)
    project_root = get_project_root()

    assert str(expected_path).startswith(str(project_root))
    assert "src/app" not in str(expected_path)


def test_reviews_dir_not_under_src_app():
    """Test that ReviewPersistence().reviews_dir does not contain src/app/."""
    with patch("pathlib.Path.mkdir"):
        rp = ReviewPersistence()

    assert "src/app" not in str(rp.reviews_dir), (
        f"Reviews dir should be under project root, got: {rp.reviews_dir}"
    )
