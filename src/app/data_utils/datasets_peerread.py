"""
PeerRead dataset core utilities for download and loading.

This module provides pure dataset functionality for downloading, caching, and
loading the PeerRead scientific paper review dataset. It contains no evaluation
logic - only data access and management.
"""

from json import JSONDecodeError, dump, load
from time import sleep
from typing import Any

from httpx import Client, HTTPStatusError, RequestError

from app.config.config_app import DATASETS_CONFIG_FILE
from app.data_models.peerread_models import (
    DownloadResult,
    PeerReadConfig,
    PeerReadPaper,
    PeerReadReview,
)
from app.utils.load_settings import chat_config
from app.utils.log import logger
from app.utils.paths import resolve_config_path, resolve_project_path


def download_peerread_dataset(
    peerread_max_papers_per_sample_download: int | None = None,
) -> None:
    """
    Download PeerRead dataset and verify the download.

    This function handles the setup phase separately from MAS execution,
    following Separation of Concerns principle. It downloads the dataset
    to the configured path and verifies the download was successful.

    Args:
        peerread_max_papers_per_sample_download: The maximum number of papers to
            download. If None, downloads all papers it can find.

    Raises:
        Exception: If download or verification fails.
    """
    logger.info("Starting PeerRead dataset download (setup mode)")

    try:
        # Load configuration
        config = load_peerread_config()
        logger.info(f"Loaded PeerRead config: {len(config.venues)} venues, {len(config.splits)} splits")

        # Initialize downloader
        downloader = PeerReadDownloader(config)
        logger.info(f"Download target directory: {downloader.cache_dir}")

        # Track download statistics
        total_downloaded = 0
        failed_downloads: list[str] = []

        # Determine max papers to download
        max_papers = (
            peerread_max_papers_per_sample_download
            if peerread_max_papers_per_sample_download is not None
            else config.max_papers_per_query
        )

        # Download dataset for each venue/split combination
        for venue in config.venues:
            for split in config.splits:
                logger.info(f"Downloading {venue}/{split}...")
                result = downloader.download_venue_split(venue, split, max_papers=max_papers)

                if result.success:
                    logger.info(f"✓ {venue}/{split}: {result.papers_downloaded} downloaded")
                    total_downloaded += result.papers_downloaded
                else:
                    error_msg = f"✗ {venue}/{split}: {result.error_message}"
                    logger.error(error_msg)
                    failed_downloads.append(f"{venue}/{split}")

        # Verify download by attempting to load papers
        logger.info("Verifying download integrity...")
        loader = PeerReadLoader(config)

        verification_count = 0
        for venue in config.venues:
            for split in config.splits:
                try:
                    papers = loader.load_papers(venue, split)
                    verification_count += len(papers)
                    logger.info(f"✓ Verified {venue}/{split}: {len(papers)} papers loaded")
                except Exception as e:
                    logger.error(f"✗ Verification failed for {venue}/{split}: {e}")
                    failed_downloads.append(f"{venue}/{split} (verification)")

        # Summary report
        logger.info("=== Download Summary ===")
        logger.info(f"Total papers downloaded: {total_downloaded}")
        logger.info(f"Total papers verified: {verification_count}")
        logger.info(f"Download directory: {downloader.cache_dir}")

        if failed_downloads:
            logger.warning(f"Failed downloads/verifications: {failed_downloads}")
            # Don't raise exception for partial failures - venue might not have data
            logger.warning("Some downloads failed, but continuing (this may be expected)")
            raise Exception(f"Failed to download from {len(failed_downloads)} sources.")

        if total_downloaded == 0 and verification_count == 0:
            raise Exception("No papers were downloaded or verified successfully")

        logger.info("✓ PeerRead dataset download and verification completed successfully")

    except Exception as e:
        error_msg = f"PeerRead dataset download failed: {e}"
        logger.error(error_msg)
        raise Exception(error_msg) from e


def load_peerread_config() -> PeerReadConfig:
    """Load PeerRead dataset configuration from config file.

    Returns:
        PeerReadConfig: Validated configuration object.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValidationError: If config data is invalid.
    """
    # Get absolute path to config file
    ds_cfg_file_path = resolve_config_path(DATASETS_CONFIG_FILE)
    try:
        # Load as raw JSON data first
        with open(ds_cfg_file_path, encoding="utf-8") as f:
            data = load(f)
        return PeerReadConfig.model_validate(data["peerread"])
    except Exception as e:
        logger.error(f"Failed to load PeerRead config: {e}")
        raise


class PeerReadDownloader:
    """Downloads PeerRead dataset files with caching and validation.

    Handles direct download from GitHub repository with progress tracking,
    error recovery, and integrity verification.
    """

    def __init__(self, config: PeerReadConfig):
        """Initialize downloader with configuration.

        Args:
            config: PeerRead dataset configuration.
        """
        self.config = config
        # Resolve cache directory relative to project root
        self.cache_dir = resolve_project_path(config.cache_directory)
        headers: dict[str, str] = {}
        if chat_config.GITHUB_API_KEY:
            logger.info("Using GitHub API key for authenticated requests")
            headers["Authorization"] = f"token {chat_config.GITHUB_API_KEY}"
        self.client = Client(headers=headers)

    def _construct_url(
        self,
        venue: str,
        split: str,
        data_type: str,
        paper_id: str,
    ) -> str:
        """Construct download URL for specific file.

        Args:
            venue: Conference venue (e.g., 'acl_2017').
            split: Data split ('train', 'test', 'dev').
            data_type: Type of data ('reviews', 'parsed_pdfs', 'pdfs').
            paper_id: Unique paper identifier.

        Returns:
            Complete download URL.

        Raises:
            ValueError: If venue or split is invalid.
        """
        if venue not in self.config.venues:
            raise ValueError(f"Invalid venue: {venue}. Valid venues: {self.config.venues}")

        if split not in self.config.splits:
            raise ValueError(f"Invalid split: {split}. Valid splits: {self.config.splits}")

        # Construct filename based on data type
        if data_type == "reviews":
            filename = f"{paper_id}.json"
        elif data_type == "parsed_pdfs":
            filename = f"{paper_id}.pdf.json"
        elif data_type == "pdfs":
            filename = f"{paper_id}.pdf"
        else:
            raise ValueError(f"Invalid data_type: {data_type}. Valid types: reviews, parsed_pdfs, pdfs")

        return f"{self.config.raw_github_base_url}/{venue}/{split}/{data_type}/{filename}"

    def _discover_available_files(
        self,
        venue: str,
        split: str,
        data_type: str,
    ) -> list[str]:
        """Discover available files in a GitHub repository directory.

        Args:
            venue: Conference venue (e.g., 'acl_2017').
            split: Data split ('train', 'test', 'dev').
            data_type: Type of data ('reviews', 'parsed_pdfs', 'pdfs').

        Returns:
            List of paper IDs (without extensions) available in the directory.
        """
        # Use GitHub API to list directory contents
        api_url = f"{self.config.github_api_base_url}/{venue}/{split}/{data_type}"

        try:
            logger.info(f"Discovering {data_type} files in {venue}/{split} via GitHub API")
            response = self.client.get(api_url, timeout=self.config.download_timeout)
            response.raise_for_status()

            files_data = response.json()

            # Extract paper IDs from filenames based on data type
            paper_ids: list[str] = []
            for file_info in files_data:
                if file_info.get("type") == "file":
                    filename = file_info.get("name", "")
                    if data_type == "reviews" and filename.endswith(".json"):
                        paper_id = filename[:-5]  # Remove .json extension
                        paper_ids.append(paper_id)
                    elif data_type == "parsed_pdfs" and filename.endswith(".pdf.json"):
                        paper_id = filename[:-9]  # Remove .pdf.json extension
                        paper_ids.append(paper_id)
                    elif data_type == "pdfs" and filename.endswith(".pdf"):
                        paper_id = filename[:-4]  # Remove .pdf extension
                        paper_ids.append(paper_id)

            logger.info(f"Found {len(paper_ids)} {data_type} files in {venue}/{split}")
            return sorted(paper_ids)

        except RequestError as e:
            logger.error(f"Failed to discover {data_type} files for {venue}/{split}: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse GitHub API response for {venue}/{split}/{data_type}: {e}")
            return []

    def download_file(
        self,
        venue: str,
        split: str,
        data_type: str,
        paper_id: str,
    ) -> bytes | dict[str, Any] | None:
        """Download a single file.

        Args:
            venue: Conference venue.
            split: Data split.
            data_type: Type of data ('reviews', 'parsed_pdfs', 'pdfs').
            paper_id: Paper identifier.

        Returns:
            File content (JSON dict for .json files, bytes for PDFs),
            or None if download fails.

        Raises:
            ValueError: If venue/split is invalid.
        """
        url = self._construct_url(venue, split, data_type, paper_id)
        for attempt in range(self.config.max_retries):
            try:
                logger.info(
                    f"Downloading {data_type}/{paper_id} from {url} (Attempt {attempt + 1}/{self.config.max_retries})"
                )

                response = self.client.get(url, timeout=self.config.download_timeout)
                response.raise_for_status()

                # Return JSON for .json files, bytes for PDFs
                if data_type in ["reviews", "parsed_pdfs"]:
                    return response.json()
                else:  # PDFs
                    return response.content

            except HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning(
                        f"Rate limit hit for {data_type}/{paper_id}. "
                        f"Retrying in {self.config.retry_delay_seconds} seconds..."
                    )
                    sleep(self.config.retry_delay_seconds)
                else:
                    logger.error(f"Failed to download {data_type}/{paper_id}: {e}")
                    return None
            except RequestError as e:
                logger.error(f"Failed to download {data_type}/{paper_id}: {e}")
                return None
            except JSONDecodeError as e:
                logger.error(f"Invalid JSON for {data_type}/{paper_id}: {e}")
                return None
        logger.error(f"Failed to download {data_type}/{paper_id} after {self.config.max_retries} attempts.")
        return None

    def download_venue_split(
        self,
        venue: str,
        split: str,
        max_papers: int | None = None,
    ) -> DownloadResult:
        """Download all files for a venue/split combination across all data types.

        Args:
            venue: Conference venue.
            split: Data split.
            max_papers: Maximum number of papers to download.

        Returns:
            DownloadResult with download statistics.
        """
        # Create base cache directory structure
        base_cache_path = self.cache_dir / venue / split

        downloaded = 0
        errors: list[str] = []
        data_types = ["reviews", "parsed_pdfs", "pdfs"]

        # Discover available papers from reviews (use as master list)
        available_paper_ids = self._discover_available_files(venue, split, "reviews")

        if not available_paper_ids:
            error_msg = f"No review files discovered for {venue}/{split}"
            logger.error(error_msg)
            return DownloadResult(
                success=False,
                cache_path=str(base_cache_path),
                papers_downloaded=0,
                error_message=error_msg,
            )

        # Apply max_papers limit if specified
        max_papers = max_papers or self.config.max_papers_per_query
        paper_ids_to_download = available_paper_ids[:max_papers]
        logger.info(
            f"Will download {len(paper_ids_to_download)} of "
            f"{len(available_paper_ids)} available papers across all data types"
        )

        # Download all data types for each paper
        for paper_id in paper_ids_to_download:
            paper_downloaded = False

            for data_type in data_types:
                # Create data type directory
                data_type_path = base_cache_path / data_type
                data_type_path.mkdir(parents=True, exist_ok=True)

                # Determine cache filename based on data type
                if data_type == "reviews":
                    cache_filename = f"{paper_id}.json"
                elif data_type == "parsed_pdfs":
                    cache_filename = f"{paper_id}.pdf.json"
                elif data_type == "pdfs":
                    cache_filename = f"{paper_id}.pdf"
                else:
                    # This case should not be reached if data_types list is correct
                    logger.warning(f"Unsupported data_type: {data_type}")
                    continue

                cache_file = data_type_path / cache_filename

                if cache_file.exists():
                    logger.debug(f"{data_type}/{paper_id} already cached")
                    if not paper_downloaded:
                        paper_downloaded = True
                    continue

                # Download the file
                file_data = self.download_file(venue, split, data_type, paper_id)
                if file_data is not None:
                    if data_type in ["reviews", "parsed_pdfs"]:
                        # JSON data
                        with open(cache_file, "w", encoding="utf-8") as f:
                            dump(file_data, f, indent=2)
                    elif isinstance(file_data, bytes):
                        # PDF binary data
                        with open(cache_file, "wb") as f:
                            f.write(file_data)

                    logger.info(f"Cached {data_type}/{paper_id}")
                    if not paper_downloaded:
                        paper_downloaded = True
                else:
                    errors.append(f"Failed to download {data_type}/{paper_id}")

            if paper_downloaded:
                downloaded += 1

        success = downloaded > 0
        error_message = None if success else "; ".join(errors[:5])

        return DownloadResult(
            success=success,
            cache_path=str(base_cache_path),
            papers_downloaded=downloaded,
            error_message=error_message,
        )


class PeerReadLoader:
    """Loads and queries PeerRead dataset with structured access."""

    def __init__(self, config: PeerReadConfig | None = None):
        """Initialize loader with configuration.

        Args:
            config: PeerRead dataset configuration. Loads from file if None.
        """
        self.config = config or load_peerread_config()
        # Resolve cache directory relative to project root
        self.cache_dir = resolve_project_path(self.config.cache_directory)

    def load_parsed_pdf_content(self, paper_id: str) -> str | None:
        """Load the text content from the parsed PDF for a given paper ID.

        Assumes parsed PDF files are JSON and contain a 'sections' key with 'text'
        within. Defaults to the latest revision if multiple exist (by filename).

        Args:
            paper_id: Unique identifier for the paper.

        Returns:
            str: The extracted text content, or None if not found/parsed.
        """
        for venue in self.config.venues:
            for split in self.config.splits:
                parsed_pdfs_path = self.cache_dir / venue / split / "parsed_pdfs"
                if parsed_pdfs_path.exists():
                    # Find all parsed PDF files for this paper_id
                    # Assuming filenames are like 'PAPER_ID.pdf.json'
                    # If multiple revisions, we'll just take the first one found for now
                    parsed_files = sorted(parsed_pdfs_path.glob(f"{paper_id}.pdf.json"), reverse=True)
                    if parsed_files:
                        latest_parsed_file = parsed_files[0]
                        try:
                            with open(latest_parsed_file, encoding="utf-8") as f:
                                parsed_data = load(f)

                            # Extract and concatenate text from all sections
                            full_text: list[str] = []
                            for section in parsed_data.get("metadata", {}).get("sections", []):
                                if "text" in section:
                                    full_text.append(section["text"])
                            return "\n".join(full_text).strip()
                        except Exception as e:
                            logger.warning(f"Failed to load/parse {latest_parsed_file}: {e}")
        return None

    def get_raw_pdf_path(self, paper_id: str) -> str | None:
        """Get the absolute path to the raw PDF file for a given paper ID.

        Args:
            paper_id: Unique identifier for the paper.

        Returns:
            str: The absolute path to the PDF file, or None if not found.
        """
        for venue in self.config.venues:
            for split in self.config.splits:
                pdf_path = self.cache_dir / venue / split / "pdfs" / f"{paper_id}.pdf"
                if pdf_path.exists():
                    return str(pdf_path)
        return None

    def _validate_papers(
        self,
        papers_data: list[dict[str, Any]],
    ) -> list[PeerReadPaper]:
        """Validate and convert paper data to Pydantic models.

        Args:
            papers_data: List of paper dictionaries.

        Returns:
            List of validated PeerReadPaper models.
        """
        validated_papers: list[PeerReadPaper] = []

        for paper_data in papers_data:
            try:
                # Convert from PeerRead format to our model format
                reviews = [
                    PeerReadReview(
                        impact=r["IMPACT"],
                        substance=r["SUBSTANCE"],
                        appropriateness=r["APPROPRIATENESS"],
                        meaningful_comparison=r["MEANINGFUL_COMPARISON"],
                        presentation_format=r["PRESENTATION_FORMAT"],
                        comments=r["comments"],
                        soundness_correctness=r["SOUNDNESS_CORRECTNESS"],
                        originality=r["ORIGINALITY"],
                        recommendation=r["RECOMMENDATION"],
                        clarity=r["CLARITY"],
                        reviewer_confidence=r["REVIEWER_CONFIDENCE"],
                        is_meta_review=r.get("is_meta_review"),
                    )
                    for r in paper_data.get("reviews", [])
                ]

                paper = PeerReadPaper(
                    paper_id=str(paper_data["id"]),
                    title=paper_data["title"],
                    abstract=paper_data["abstract"],
                    reviews=reviews,
                    review_histories=[" ".join(map(str, h)) for h in paper_data.get("histories", [])],
                )
                validated_papers.append(paper)

            except Exception as e:
                logger.warning(f"Failed to validate paper {paper_data.get('id', 'unknown')}: {e}")
                continue

        return validated_papers

    def load_papers(
        self,
        venue: str = "acl_2017",
        split: str = "train",
    ) -> list[PeerReadPaper]:
        """Load papers from cached data or download if needed.

        Args:
            venue: Conference venue.
            split: Data split.

        Returns:
            List of validated PeerReadPaper models.

        Raises:
            FileNotFoundError: If cache directory doesn't exist and download fails.
        """
        cache_path = self.cache_dir / venue / split

        if not cache_path.exists():
            error_msg = (
                f"PeerRead dataset not found for {venue}/{split}. "
                f"Please download the dataset first using: "
                f"'python src/app/main.py --download-peerread-only' or "
                f"'make run_cli ARGS=\"--download-peerread-only\"'"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Load all cached papers from reviews directory
        reviews_path = cache_path / "reviews"

        if not reviews_path.exists():
            error_msg = (
                f"PeerRead reviews not found for {venue}/{split}. "
                f"Please download the dataset first using: "
                f"'python src/app/main.py --download-peerread-only' or "
                f"'make run_cli ARGS=\"--download-peerread-only\"'"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        papers_data: list[dict[str, Any]] = []
        for json_file in reviews_path.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    papers_data.append(load(f))
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")
                continue

        return self._validate_papers(papers_data)

    def get_paper_by_id(self, paper_id: str) -> PeerReadPaper | None:
        """Get a specific paper by ID.

        Args:
            paper_id: Paper identifier.

        Returns:
            PeerReadPaper if found, None otherwise.
        """
        # Search across all venues and splits in reviews directory
        for venue in self.config.venues:
            for split in self.config.splits:
                cache_path = self.cache_dir / venue / split / "reviews" / f"{paper_id}.json"
                if cache_path.exists():
                    try:
                        with open(cache_path, encoding="utf-8") as f:
                            data: dict[str, Any] = load(f)
                        papers = self._validate_papers([data])
                        return papers[0] if papers else None
                    except Exception as e:
                        logger.warning(f"Failed to load paper {paper_id}: {e}")
                        continue
        return None

    def query_papers(
        self,
        venue: str | None = None,
        min_reviews: int = 1,
        limit: int | None = None,
    ) -> list[PeerReadPaper]:
        """Query papers with filters.

        Args:
            venue: Filter by venue (None for all venues).
            min_reviews: Minimum number of reviews required.
            limit: Maximum number of papers to return.

        Returns:
            List of filtered PeerReadPaper models.
        """
        all_papers: list[PeerReadPaper] = []
        venues_to_search = [venue] if venue else self.config.venues

        for search_venue in venues_to_search:
            for split in self.config.splits:
                try:
                    papers = self.load_papers(search_venue, split)
                    all_papers.extend(papers)
                except Exception as e:
                    logger.warning(f"Failed to load {search_venue}/{split}: {e}")
                    continue

        # Apply filters
        filtered_papers = [paper for paper in all_papers if len(paper.reviews) >= min_reviews]

        # Apply limit
        if limit:
            filtered_papers = filtered_papers[:limit]

        return filtered_papers
