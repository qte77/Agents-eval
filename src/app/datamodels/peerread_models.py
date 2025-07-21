"""
Data models for PeerRead dataset integration.

This module defines Pydantic models for representing scientific papers and peer reviews
from the PeerRead dataset. These models ensure type safety and validation for data
exchanged between the dataset loading utilities and the multi-agent system evaluation.
"""

from typing import Any

from pydantic import BaseModel, field_validator


class PeerReadPaper(BaseModel):
    """Represents a scientific paper from PeerRead dataset.

    This model validates and structures paper metadata including title, abstract,
    authors, venue information, and optional sections/references data.
    """

    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    venue: str
    year: int
    sections: dict[str, str] | None = None
    references: list[str] | None = None

    @field_validator("paper_id")
    @classmethod
    def validate_paper_id(cls, v: str) -> str:
        """Ensure paper ID is not empty.

        Args:
            v (str): The paper ID to validate.

        Returns:
            str: The validated and stripped paper ID.

        Raises:
            ValueError: If paper ID is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Paper ID cannot be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty.

        Args:
            v (str): The title to validate.

        Returns:
            str: The validated and stripped title.

        Raises:
            ValueError: If title is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("authors")
    @classmethod
    def validate_authors(cls, v: list[str]) -> list[str]:
        """Ensure authors list is not empty and contains valid names.

        Args:
            v (list[str]): The authors list to validate.

        Returns:
            list[str]: The validated authors list with stripped names.

        Raises:
            ValueError: If authors list is empty or contains empty names.
        """
        if not v:
            raise ValueError("Authors list cannot be empty")
        stripped_authors = [author.strip() for author in v]
        if any(not author for author in stripped_authors):
            raise ValueError("Author names cannot be empty")
        return stripped_authors

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Ensure year is a reasonable publication year.

        Args:
            v (int): The year to validate.

        Returns:
            int: The validated year.

        Raises:
            ValueError: If year is not within reasonable bounds (1900-2030).
        """
        if v < 1900 or v > 2030:
            raise ValueError("Year must be between 1900 and 2030")
        return v


class PeerReadReview(BaseModel):
    """Represents a peer review from PeerRead dataset.

    This model validates and structures review data including reviewer information,
    recommendation, comments, scores, and confidence ratings.
    """

    paper_id: str
    reviewer_id: str
    recommendation: str
    comments: str
    scores: dict[str, float] | None = None
    confidence: float | None = None

    @field_validator("paper_id")
    @classmethod
    def validate_paper_id(cls, v: str) -> str:
        """Ensure paper ID is not empty.

        Args:
            v (str): The paper ID to validate.

        Returns:
            str: The validated and stripped paper ID.

        Raises:
            ValueError: If paper ID is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Paper ID cannot be empty")
        return v.strip()

    @field_validator("reviewer_id")
    @classmethod
    def validate_reviewer_id(cls, v: str) -> str:
        """Ensure reviewer ID is not empty.

        Args:
            v (str): The reviewer ID to validate.

        Returns:
            str: The validated and stripped reviewer ID.

        Raises:
            ValueError: If reviewer ID is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Reviewer ID cannot be empty")
        return v.strip()

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(cls, v: str) -> str:
        """Ensure recommendation is not empty and normalize format.

        Args:
            v (str): The recommendation to validate.

        Returns:
            str: The validated and normalized recommendation.

        Raises:
            ValueError: If recommendation is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Recommendation cannot be empty")
        return v.strip().lower()

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float | None) -> float | None:
        """Ensure confidence is within valid range if provided.

        Args:
            v (Optional[float]): The confidence score to validate.

        Returns:
            Optional[float]: The validated confidence score.

        Raises:
            ValueError: If confidence is not between 0 and 10.
        """
        if v is not None and (v < 0 or v > 10):
            raise ValueError("Confidence must be between 0 and 10")
        return v

    @field_validator("scores")
    @classmethod
    def validate_scores(
        cls, v: dict[str, float] | None
    ) -> dict[str, float] | None:
        """Ensure all score values are within valid range if provided.

        Args:
            v (Optional[dict[str, float]]): The scores dictionary to validate.

        Returns:
            Optional[dict[str, float]]: The validated scores dictionary.

        Raises:
            ValueError: If any score is not between 0 and 10.
        """
        if v is not None:
            for aspect, score in v.items():
                if score < 0 or score > 10:
                    raise ValueError(f"Score for {aspect} must be between 0 and 10")
        return v


class PeerReadAgentTask(BaseModel):
    """Agent task format for PeerRead evaluation.

    This model structures tasks for multi-agent system evaluation, including
    paper information and expected output format for benchmarking.
    """

    paper_id: str
    title: str
    abstract: str
    agent_task: str = "Provide a peer review with rating (1-10) and recommendation"
    expected_output: dict[str, Any]

    @field_validator("paper_id")
    @classmethod
    def validate_paper_id(cls, v: str) -> str:
        """Ensure paper ID is not empty.

        Args:
            v (str): The paper ID to validate.

        Returns:
            str: The validated and stripped paper ID.

        Raises:
            ValueError: If paper ID is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Paper ID cannot be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty.

        Args:
            v (str): The title to validate.

        Returns:
            str: The validated and stripped title.

        Raises:
            ValueError: If title is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("abstract")
    @classmethod
    def validate_abstract(cls, v: str) -> str:
        """Ensure abstract is not empty.

        Args:
            v (str): The abstract to validate.

        Returns:
            str: The validated and stripped abstract.

        Raises:
            ValueError: If abstract is empty or whitespace only.
        """
        if not v.strip():
            raise ValueError("Abstract cannot be empty")
        return v.strip()


class PeerReadConfig(BaseModel):
    """Configuration for PeerRead dataset loading.

    This model validates configuration settings for dataset loading including
    venue selection, data splits, batch processing, and caching options.
    """

    venues: list[str] = ["acl_2017", "nips_2013-2017", "iclr_2017"]
    splits: list[str] = ["train", "dev", "test"]
    batch_size: int = 100
    cache_dir: str = "data/peerread"
    streaming: bool = False

    @field_validator("venues")
    @classmethod
    def validate_venues(cls, v: list[str]) -> list[str]:
        """Ensure venues list contains valid venue names.

        Args:
            v (list[str]): The venues list to validate.

        Returns:
            list[str]: The validated venues list.

        Raises:
            ValueError: If venues list is empty or contains invalid venue names.
        """
        if not v:
            raise ValueError("Venues list cannot be empty")

        valid_venues = ["acl_2017", "nips_2013-2017", "iclr_2017"]
        for venue in v:
            if venue not in valid_venues:
                raise ValueError(
                    f"Invalid venue: {venue}. Must be one of {valid_venues}"
                )
        return v

    @field_validator("splits")
    @classmethod
    def validate_splits(cls, v: list[str]) -> list[str]:
        """Ensure splits list contains valid split names.

        Args:
            v (list[str]): The splits list to validate.

        Returns:
            list[str]: The validated splits list.

        Raises:
            ValueError: If splits list is empty or contains invalid split names.
        """
        if not v:
            raise ValueError("Splits list cannot be empty")

        valid_splits = ["train", "dev", "test"]
        for split in v:
            if split not in valid_splits:
                raise ValueError(
                    f"Invalid split: {split}. Must be one of {valid_splits}"
                )
        return v

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        """Ensure batch size is positive and reasonable.

        Args:
            v (int): The batch size to validate.

        Returns:
            int: The validated batch size.

        Raises:
            ValueError: If batch size is not between 1 and 10000.
        """
        if v < 1 or v > 10000:
            raise ValueError("Batch size must be between 1 and 10000")
        return v

    @field_validator("cache_dir")
    @classmethod
    def validate_cache_dir(cls, v: str) -> str:
        """Ensure cache directory path is not empty.

        Args:
            v (str): The cache directory path to validate.

        Returns:
            str: The validated cache directory path.

        Raises:
            ValueError: If cache directory path is empty.
        """
        if not v.strip():
            raise ValueError("Cache directory cannot be empty")
        return v.strip()
