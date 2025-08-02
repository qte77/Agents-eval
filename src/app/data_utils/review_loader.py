"""Review loading utilities for external evaluation system."""

from pathlib import Path

from app.config.config_app import MAS_REVIEWS_PATH
from app.data_models.peerread_models import PeerReadReview
from app.data_utils.review_persistence import ReviewPersistence


class ReviewLoader:
    """Loads MAS-generated reviews for external evaluation system."""

    def __init__(self, reviews_dir: str = MAS_REVIEWS_PATH):
        """Initialize with reviews directory path.

        Args:
            reviews_dir: Directory containing review files
        """
        # ReviewPersistence will handle path resolution
        self.persistence = ReviewPersistence(reviews_dir)

    def load_review_for_paper(self, paper_id: str) -> PeerReadReview | None:
        """Load the latest review for a specific paper.

        Args:
            paper_id: Paper identifier

        Returns:
            PeerReadReview object if found, None otherwise
        """
        latest_file = self.persistence.get_latest_review(paper_id)
        if not latest_file:
            return None

        _, review = self.persistence.load_review(latest_file)
        return review

    def load_all_reviews(self) -> dict[str, PeerReadReview]:
        """Load all available reviews grouped by paper ID.

        Returns:
            dict: Mapping of paper_id -> latest PeerReadReview
        """
        reviews: dict[str, PeerReadReview] = {}

        # Get all review files
        all_files = self.persistence.list_reviews()

        # Group by paper ID and get latest for each
        paper_ids: set[str] = set()
        for filepath in all_files:
            filename = Path(filepath).stem
            paper_id: str = filename.split("_")[0]  # Extract paper_id from filename
            paper_ids.add(paper_id)

        # Load latest review for each paper
        for paper_id in paper_ids:
            review = self.load_review_for_paper(paper_id)
            if review:
                reviews[paper_id] = review

        return reviews

    def get_available_paper_ids(self) -> list[str]:
        """Get list of paper IDs that have reviews available.

        Returns:
            list: Paper identifiers with available reviews
        """
        all_files = self.persistence.list_reviews()
        paper_ids: set[str] = set()

        for filepath in all_files:
            filename = Path(filepath).stem
            paper_id: str = filename.split("_")[0]  # Extract paper_id from filename
            paper_ids.add(paper_id)

        return sorted(list(paper_ids))
