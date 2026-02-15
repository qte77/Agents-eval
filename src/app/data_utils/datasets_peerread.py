"""
PeerRead dataset core utilities for download and loading.

This module provides pure dataset functionality for downloading, caching, and
loading the PeerRead scientific paper review dataset. It contains no evaluation
logic - only data access and management.
"""

from json import JSONDecodeError, dump, load
from pathlib import Path
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


def _perform_downloads(
    downloader: "PeerReadDownloader",
    config: PeerReadConfig,
    max_papers: int,
) -> tuple[int, list[str]]:
    """Perform downloads for all venue/split combinations.

    Args:
        downloader: PeerReadDownloader instance.
        config: PeerRead dataset configuration.
        max_papers: Maximum number of papers to download per venue/split.

    Returns:
        Tuple of (total_downloaded, failed_downloads).
    """
    total_downloaded = 0
    failed_downloads: list[str] = []

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

    return total_downloaded, failed_downloads


def _verify_downloads(
    loader: "PeerReadLoader",
    config: PeerReadConfig,
    failed_downloads: list[str],
) -> int:
    """Verify downloads by attempting to load papers.

    Args:
        loader: PeerReadLoader instance.
        config: PeerRead dataset configuration.
        failed_downloads: List to append verification failures to.

    Returns:
        Number of papers verified.
    """
    logger.info("Verifying download integrity...")
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

    return verification_count


def _validate_download_results(
    total_downloaded: int,
    verification_count: int,
    failed_downloads: list[str],
) -> None:
    """Validate download results and raise if failures occurred.

    Args:
        total_downloaded: Number of papers downloaded.
        verification_count: Number of papers verified.
        failed_downloads: List of failed download/verification items.

    Raises:
        Exception: If download or verification failed.
    """
    if failed_downloads:
        logger.warning(f"Failed downloads/verifications: {failed_downloads}")
        logger.warning("Some downloads failed, but continuing (this may be expected)")
        raise Exception(f"Failed to download from {len(failed_downloads)} sources.")

    if total_downloaded == 0 and verification_count == 0:
        raise Exception("No papers were downloaded or verified successfully")


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
        config = load_peerread_config()
        logger.info(
            f"Loaded PeerRead config: {len(config.venues)} venues, {len(config.splits)} splits"
        )

        downloader = PeerReadDownloader(config)
        logger.info(f"Download target directory: {downloader.cache_dir}")

        max_papers = (
            peerread_max_papers_per_sample_download
            if peerread_max_papers_per_sample_download is not None
            else config.max_papers_per_query
        )

        total_downloaded, failed_downloads = _perform_downloads(downloader, config, max_papers)

        loader = PeerReadLoader(config)
        verification_count = _verify_downloads(loader, config, failed_downloads)

        logger.info("=== Download Summary ===")
        logger.info(f"Total papers downloaded: {total_downloaded}")
        logger.info(f"Total papers verified: {verification_count}")
        logger.info(f"Download directory: {downloader.cache_dir}")

        _validate_download_results(total_downloaded, verification_count, failed_downloads)

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
            raise ValueError(
                f"Invalid data_type: {data_type}. Valid types: reviews, parsed_pdfs, pdfs"
            )

        return f"{self.config.raw_github_base_url}/{venue}/{split}/{data_type}/{filename}"

    def _extract_paper_id_from_filename(
        self,
        filename: str,
        data_type: str,
    ) -> str | None:
        """Extract paper ID from filename based on data type.

        Args:
            filename: Name of the file.
            data_type: Type of data ('reviews', 'parsed_pdfs', 'pdfs').

        Returns:
            Paper ID without extension, or None if filename doesn't match.
        """
        if data_type == "reviews" and filename.endswith(".json"):
            return filename[:-5]  # Remove .json extension
        elif data_type == "parsed_pdfs" and filename.endswith(".pdf.json"):
            return filename[:-9]  # Remove .pdf.json extension
        elif data_type == "pdfs" and filename.endswith(".pdf"):
            return filename[:-4]  # Remove .pdf extension
        return None

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
        api_url = f"{self.config.github_api_base_url}/{venue}/{split}/{data_type}"

        try:
            logger.info(f"Discovering {data_type} files in {venue}/{split} via GitHub API")
            response = self.client.get(api_url, timeout=self.config.download_timeout)
            response.raise_for_status()

            files_data = response.json()

            paper_ids: list[str] = []
            for file_info in files_data:
                if file_info.get("type") != "file":
                    continue

                filename = file_info.get("name", "")
                paper_id = self._extract_paper_id_from_filename(filename, data_type)
                if paper_id:
                    paper_ids.append(paper_id)

            logger.info(f"Found {len(paper_ids)} {data_type} files in {venue}/{split}")
            return sorted(paper_ids)

        except (RequestError, HTTPStatusError) as e:
            logger.error(f"Failed to discover {data_type} files for {venue}/{split}: {e}")
            return []
        except (KeyError, ValueError) as e:
            logger.error(
                f"Failed to parse GitHub API response for {venue}/{split}/{data_type}: {e}"
            )
            return []

    def _handle_download_error(
        self,
        error: Exception,
        data_type: str,
        paper_id: str,
    ) -> bool:
        """Handle download errors and determine if retry should continue.

        Args:
            error: The exception that occurred.
            data_type: Type of data being downloaded.
            paper_id: Paper identifier.

        Returns:
            True if retry should continue, False otherwise.
        """
        if isinstance(error, HTTPStatusError) and error.response.status_code == 429:
            logger.warning(
                f"Rate limit hit for {data_type}/{paper_id}. "
                f"Retrying in {self.config.retry_delay_seconds} seconds..."
            )
            sleep(self.config.retry_delay_seconds)
            return True

        logger.error(f"Failed to download {data_type}/{paper_id}: {error}")
        return False

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
                    f"Downloading {data_type}/{paper_id} from {url} "
                    f"(Attempt {attempt + 1}/{self.config.max_retries})"
                )

                response = self.client.get(url, timeout=self.config.download_timeout)
                response.raise_for_status()

                if data_type in ["reviews", "parsed_pdfs"]:
                    return response.json()
                return response.content

            except (HTTPStatusError, RequestError, JSONDecodeError) as e:
                should_retry = self._handle_download_error(e, data_type, paper_id)
                if not should_retry:
                    return None

        logger.error(
            f"Failed to download {data_type}/{paper_id} after {self.config.max_retries} attempts."
        )
        return None

    def _get_cache_filename(self, data_type: str, paper_id: str) -> str:
        """Get cache filename for given data type and paper ID.

        Args:
            data_type: Type of data ('reviews', 'parsed_pdfs', 'pdfs').
            paper_id: Paper identifier.

        Returns:
            Cache filename.
        """
        if data_type == "reviews":
            return f"{paper_id}.json"
        elif data_type == "parsed_pdfs":
            return f"{paper_id}.pdf.json"
        elif data_type == "pdfs":
            return f"{paper_id}.pdf"
        else:
            logger.warning(f"Unsupported data_type: {data_type}")
            return ""

    def _save_file_data(
        self,
        file_data: bytes | dict[str, Any],
        cache_file: Path,
        data_type: str,
    ) -> None:
        """Save downloaded file data to cache.

        Args:
            file_data: Downloaded file content.
            cache_file: Path to cache file.
            data_type: Type of data being saved.
        """
        if data_type in ["reviews", "parsed_pdfs"]:
            with open(cache_file, "w", encoding="utf-8") as f:
                dump(file_data, f, indent=2)
        elif isinstance(file_data, bytes):
            with open(cache_file, "wb") as f:
                f.write(file_data)

    def _download_single_data_type(
        self,
        venue: str,
        split: str,
        data_type: str,
        paper_id: str,
        base_cache_path: Path,
        errors: list[str],
    ) -> bool:
        """Download a single data type for a paper.

        Args:
            venue: Conference venue.
            split: Data split.
            data_type: Type of data to download.
            paper_id: Paper identifier.
            base_cache_path: Base cache directory path.
            errors: List to append errors to.

        Returns:
            True if file was downloaded or already cached, False otherwise.
        """
        data_type_path = base_cache_path / data_type
        data_type_path.mkdir(parents=True, exist_ok=True)

        cache_filename = self._get_cache_filename(data_type, paper_id)
        if not cache_filename:
            return False

        cache_file = data_type_path / cache_filename

        if cache_file.exists():
            logger.debug(f"{data_type}/{paper_id} already cached")
            return True

        file_data = self.download_file(venue, split, data_type, paper_id)
        if file_data is None:
            errors.append(f"Failed to download {data_type}/{paper_id}")
            return False

        self._save_file_data(file_data, cache_file, data_type)
        logger.info(f"Cached {data_type}/{paper_id}")
        return True

    def _download_paper_all_types(
        self,
        venue: str,
        split: str,
        paper_id: str,
        base_cache_path: Path,
        errors: list[str],
    ) -> bool:
        """Download all data types for a single paper.

        Args:
            venue: Conference venue.
            split: Data split.
            paper_id: Paper identifier.
            base_cache_path: Base cache directory path.
            errors: List to append errors to.

        Returns:
            True if at least one file was downloaded successfully.
        """
        data_types = ["reviews", "parsed_pdfs", "pdfs"]
        paper_downloaded = False

        for data_type in data_types:
            success = self._download_single_data_type(
                venue, split, data_type, paper_id, base_cache_path, errors
            )
            if success and not paper_downloaded:
                paper_downloaded = True

        return paper_downloaded

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
        base_cache_path = self.cache_dir / venue / split
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

        max_papers = max_papers or self.config.max_papers_per_query
        paper_ids_to_download = available_paper_ids[:max_papers]
        logger.info(
            f"Will download {len(paper_ids_to_download)} of "
            f"{len(available_paper_ids)} available papers across all data types"
        )

        downloaded = 0
        errors: list[str] = []

        for paper_id in paper_ids_to_download:
            if self._download_paper_all_types(venue, split, paper_id, base_cache_path, errors):
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

    def _extract_text_from_parsed_data(self, parsed_data: dict[str, Any]) -> str:
        """Extract text content from parsed PDF data.

        Args:
            parsed_data: Parsed PDF JSON data.

        Returns:
            Concatenated text from all sections.
        """
        full_text: list[str] = []
        sections = parsed_data.get("metadata", {}).get("sections", [])
        for section in sections:
            if "text" in section:
                full_text.append(section["text"])
        return "\n".join(full_text).strip()

    def _load_parsed_file(self, parsed_file: Path) -> str | None:
        """Load and parse a single parsed PDF file.

        Args:
            parsed_file: Path to parsed PDF file.

        Returns:
            Extracted text content, or None if loading fails.
        """
        try:
            with open(parsed_file, encoding="utf-8") as f:
                parsed_data = load(f)
            return self._extract_text_from_parsed_data(parsed_data)
        except Exception as e:
            logger.warning(f"Failed to load/parse {parsed_file}: {e}")
            return None

    def _find_parsed_pdf_in_split(
        self,
        venue: str,
        split: str,
        paper_id: str,
    ) -> str | None:
        """Find and load parsed PDF content in a specific venue/split.

        Args:
            venue: Conference venue.
            split: Data split.
            paper_id: Paper identifier.

        Returns:
            Extracted text content, or None if not found.
        """
        parsed_pdfs_path = self.cache_dir / venue / split / "parsed_pdfs"
        if not parsed_pdfs_path.exists():
            return None

        parsed_files = sorted(parsed_pdfs_path.glob(f"{paper_id}.pdf.json"), reverse=True)
        if not parsed_files:
            return None

        return self._load_parsed_file(parsed_files[0])

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
                content = self._find_parsed_pdf_in_split(venue, split, paper_id)
                if content:
                    return content
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
                reviews = []
                for r in paper_data.get("reviews", []):
                    # Optional fields use .get() with "UNKNOWN" default
                    # Reason: Papers 304-308, 330 lack IMPACT field
                    optional_fields = [
                        "IMPACT",
                        "SUBSTANCE",
                        "APPROPRIATENESS",
                        "MEANINGFUL_COMPARISON",
                        "SOUNDNESS_CORRECTNESS",
                        "ORIGINALITY",
                        "CLARITY",
                    ]

                    # Log debug message when optional field is missing
                    for field in optional_fields:
                        if field not in r:
                            logger.debug(
                                f"Paper {paper_data.get('id', 'unknown')}: "
                                f"Optional field {field} missing, using UNKNOWN"
                            )

                    review = PeerReadReview(
                        impact=r.get("IMPACT", "UNKNOWN"),
                        substance=r.get("SUBSTANCE", "UNKNOWN"),
                        appropriateness=r.get("APPROPRIATENESS", "UNKNOWN"),
                        meaningful_comparison=r.get("MEANINGFUL_COMPARISON", "UNKNOWN"),
                        presentation_format=r.get("PRESENTATION_FORMAT", "Poster"),
                        comments=r.get("comments", ""),
                        soundness_correctness=r.get("SOUNDNESS_CORRECTNESS", "UNKNOWN"),
                        originality=r.get("ORIGINALITY", "UNKNOWN"),
                        recommendation=r.get("RECOMMENDATION", "UNKNOWN"),
                        clarity=r.get("CLARITY", "UNKNOWN"),
                        reviewer_confidence=r.get("REVIEWER_CONFIDENCE", "UNKNOWN"),
                        is_meta_review=r.get("is_meta_review"),
                    )
                    reviews.append(review)

                paper = PeerReadPaper(
                    paper_id=str(paper_data["id"]),
                    title=paper_data["title"],
                    abstract=paper_data["abstract"],
                    reviews=reviews,
                    review_histories=[
                        " ".join(map(str, h)) for h in paper_data.get("histories", [])
                    ],
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

    def _load_paper_from_path(self, cache_path: Path, paper_id: str) -> PeerReadPaper | None:
        """Load and validate a paper from a specific cache path.

        Args:
            cache_path: Path to the cached paper JSON file.
            paper_id: Paper identifier for logging.

        Returns:
            Validated PeerReadPaper, or None if loading fails.
        """
        try:
            with open(cache_path, encoding="utf-8") as f:
                data: dict[str, Any] = load(f)
            papers = self._validate_papers([data])
            return papers[0] if papers else None
        except Exception as e:
            logger.warning(f"Failed to load paper {paper_id}: {e}")
            return None

    def get_paper_by_id(self, paper_id: str) -> PeerReadPaper | None:
        """Get a specific paper by ID.

        Args:
            paper_id: Paper identifier.

        Returns:
            PeerReadPaper if found, None otherwise.
        """
        for venue in self.config.venues:
            for split in self.config.splits:
                cache_path = self.cache_dir / venue / split / "reviews" / f"{paper_id}.json"
                if not cache_path.exists():
                    continue

                paper = self._load_paper_from_path(cache_path, paper_id)
                if paper:
                    return paper

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
