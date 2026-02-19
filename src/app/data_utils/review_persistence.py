"""Review persistence interface for MAS and evaluation system integration."""

import json
from datetime import UTC, datetime

from app.config.config_app import MAS_REVIEWS_PATH
from app.data_models.peerread_models import PeerReadReview
from app.utils.paths import resolve_project_path


class ReviewPersistence:
    """Handles saving and loading of MAS-generated reviews."""

    def __init__(self, reviews_dir: str = MAS_REVIEWS_PATH):
        """Initialize with reviews directory path.

        Args:
            reviews_dir: Directory to store review files
        """
        # Resolve reviews directory relative to project root
        self.reviews_dir = resolve_project_path(reviews_dir)
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

    def save_review(self, paper_id: str, review: PeerReadReview, timestamp: str | None = None) -> str:
        """Save a review to the reviews directory.

        Args:
            paper_id: Unique identifier for the paper
            review: The generated review object
            timestamp: Optional timestamp, defaults to current UTC time

        Returns:
            str: Path to the saved review file
        """
        if timestamp is None:
            timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")

        filename = f"{paper_id}_{timestamp}.json"
        filepath = self.reviews_dir / filename

        # Convert review to dict for JSON serialization
        review_data = {
            "paper_id": paper_id,
            "timestamp": timestamp,
            "review": review.model_dump(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(review_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def load_review(self, filepath: str) -> tuple[str, PeerReadReview]:
        """Load a review from file.

        Args:
            filepath: Path to the review file

        Returns:
            tuple: (paper_id, PeerReadReview object)
        """
        with open(filepath, encoding="utf-8") as f:
            review_data = json.load(f)

        paper_id = review_data["paper_id"]
        review = PeerReadReview.model_validate(review_data["review"])

        return paper_id, review

    def list_reviews(self, paper_id: str | None = None) -> list[str]:
        """List available review files.

        Args:
            paper_id: Optional filter by paper ID

        Returns:
            list: Paths to matching review files
        """
        pattern = f"{paper_id}_*.json" if paper_id else "*.json"
        return [str(p) for p in self.reviews_dir.glob(pattern)]

    def get_latest_review(self, paper_id: str) -> str | None:
        """Get the most recent review file for a paper.

        Args:
            paper_id: Paper identifier

        Returns:
            str: Path to latest review file, or None if not found
        """
        reviews = self.list_reviews(paper_id)
        if not reviews:
            return None

        # Sort by timestamp in filename (newest first)
        reviews.sort(reverse=True)
        return reviews[0]
