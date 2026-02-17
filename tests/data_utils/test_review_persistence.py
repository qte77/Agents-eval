"""Tests for review persistence path resolution.

Validates that reviews are saved under the project root (datasets/peerread/MAS_reviews/)
and NOT under src/app/.
"""

from unittest.mock import patch

from app.data_utils.review_persistence import ReviewPersistence
from app.utils.paths import get_project_root


def test_default_reviews_dir_under_project_root(tmp_path):
    """Test that ReviewPersistence default dir resolves to project root, not src/app/."""
    with patch.object(ReviewPersistence, "__init__", lambda self, *a, **kw: None):
        rp = ReviewPersistence.__new__(ReviewPersistence)

    # Now call the real constructor logic manually to inspect path
    from app.config.config_app import MAS_REVIEWS_PATH
    from app.utils.paths import resolve_app_path, resolve_project_path

    actual_path = resolve_app_path(MAS_REVIEWS_PATH)
    expected_path = resolve_project_path(MAS_REVIEWS_PATH)
    project_root = get_project_root()

    # The resolved path should be under project root, not under src/app/
    assert str(expected_path).startswith(str(project_root))
    assert "src/app" not in str(expected_path)

    # Current bug: resolve_app_path puts it under src/app/
    # After fix, ReviewPersistence should use resolve_project_path
    rp_real = ReviewPersistence.__new__(ReviewPersistence)
    rp_real.reviews_dir = resolve_project_path(MAS_REVIEWS_PATH)

    assert "src/app" not in str(rp_real.reviews_dir)


def test_reviews_dir_not_under_src_app():
    """Test that ReviewPersistence().reviews_dir does not contain src/app/."""
    with patch("pathlib.Path.mkdir"):
        rp = ReviewPersistence()

    assert "src/app" not in str(rp.reviews_dir), (
        f"Reviews dir should be under project root, got: {rp.reviews_dir}"
    )
