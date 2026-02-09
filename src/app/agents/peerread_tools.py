"""
PeerRead agent tools for multi-agent system integration.

This module provides agent tools that enable the manager agent to interact
with the PeerRead dataset for paper retrieval, querying, and review evaluation.
"""

from json import dump
from pathlib import Path

from markitdown import MarkItDown
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.data_models.peerread_models import (
    GeneratedReview,
    PeerReadPaper,
    PeerReadReview,
    ReviewGenerationResult,
)
from app.data_utils.datasets_peerread import PeerReadLoader, load_peerread_config
from app.data_utils.review_persistence import ReviewPersistence
from app.utils.log import logger
from app.utils.paths import get_review_template_path


def read_paper_pdf(
    ctx: RunContext[None] | None,
    pdf_path: str | Path,
) -> str:
    """Read text content from a PDF file using MarkItDown.

    Note: MarkItDown extracts the entire PDF content as a single text block.
    Page-level extraction is not supported by the underlying library.

    Args:
        ctx: RunContext (unused but required for tool compatibility).
        pdf_path: Path to the PDF file.

    Returns:
        str: Extracted text content from the entire PDF in Markdown format.

    Raises:
        FileNotFoundError: If the PDF file doesn't exist.
        ValueError: If the file is not a PDF or conversion fails.
    """
    if isinstance(pdf_path, str):
        pdf_file = Path(pdf_path)
    else:
        pdf_file = pdf_path
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_file}")
    if pdf_file.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {pdf_file}")

    try:
        md_converter = MarkItDown()
        result = md_converter.convert(pdf_file)
        logger.info(f"Extracted text from {pdf_file}")
        return result.text_content.strip()

    except Exception as e:
        logger.error(f"Error reading PDF with MarkItDown: {e}")
        raise ValueError(f"Failed to read PDF: {str(e)}")


def add_peerread_tools_to_manager(manager_agent: Agent[None, BaseModel]):
    """Add PeerRead dataset tools to the manager agent.

    Args:
        manager_agent: The manager agent to which PeerRead tools will be added.
    """

    @manager_agent.tool
    async def get_peerread_paper(ctx: RunContext[None], paper_id: str) -> PeerReadPaper:  # type: ignore[reportUnusedFunction]
        """Get a specific paper from the PeerRead dataset.

        Args:
            paper_id: Unique identifier for the paper.

        Returns:
            PeerReadPaper with title, abstract, and reviews.
        """
        try:
            config = load_peerread_config()
            loader = PeerReadLoader(config)

            paper = loader.get_paper_by_id(paper_id)
            if not paper:
                raise ValueError(f"Paper {paper_id} not found in PeerRead dataset")

            logger.info(f"Retrieved paper {paper_id}: {paper.title[:50]}...")
            return paper

        except Exception as e:
            logger.error(f"Error retrieving paper: {e}")
            raise ValueError(f"Failed to retrieve paper: {str(e)}")

    @manager_agent.tool
    async def query_peerread_papers(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None], venue: str = "", min_reviews: int = 1
    ) -> list[PeerReadPaper]:
        """Query papers from PeerRead dataset with filters.

        Args:
            venue: Filter by conference venue (empty for all venues).
            min_reviews: Minimum number of reviews required per paper.

        Returns:
            List of PeerReadPaper objects matching the criteria.
        """
        try:
            config = load_peerread_config()
            loader = PeerReadLoader(config)

            # Query papers with filters
            papers = loader.query_papers(
                venue=venue if venue else None,
                min_reviews=min_reviews,
                limit=config.max_papers_per_query,
            )

            logger.info(f"Found {len(papers)} papers matching criteria")
            return papers

        except Exception as e:
            logger.error(f"Error querying papers: {e}")
            raise ValueError(f"Failed to query papers: {str(e)}")

    @manager_agent.tool
    async def read_paper_pdf_tool(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        pdf_path: str,
    ) -> str:
        """Read text content from a PDF file using MarkItDown.

        Note: MarkItDown extracts the entire PDF content as a single text block.
        Page-level extraction is not supported by the underlying library.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            str: Extracted text content from the entire PDF in Markdown format.
        """
        return read_paper_pdf(ctx, pdf_path)


def add_peerread_review_tools_to_manager(
    manager_agent: Agent[None, BaseModel], max_content_length: int = 15000
):
    """Add PeerRead review generation and persistence tools to the manager agent.

    Args:
        manager_agent: The manager agent to which review tools will be added.
        max_content_length: The maximum number of characters to include in the prompt.
    """

    @manager_agent.tool
    async def generate_paper_review_content_from_template(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        paper_id: str,
        review_focus: str = "comprehensive",
        tone: str = "professional",
    ) -> str:
        """Create a review template for a specific paper.

        WARNING: This function does NOT generate actual reviews. It creates a
        structured template that would need to be filled in manually or by
        another AI system. This is a demonstration/template function only.

        Args:
            paper_id: Unique identifier for the paper being reviewed.
            review_focus: Type of review (comprehensive, technical, high-level).
            tone: Tone of the review (professional, constructive, critical).

        Returns:
            str: Review template with paper information and placeholder sections
                 that need to be manually completed.
        """
        try:
            config = load_peerread_config()
            loader = PeerReadLoader(config)
            paper = loader.get_paper_by_id(paper_id)

            if not paper:
                raise ValueError(f"Paper {paper_id} not found in PeerRead dataset")

            # Load paper content for the template
            paper_content_for_template = loader.load_parsed_pdf_content(paper_id)

            if not paper_content_for_template:
                logger.warning(
                    f"No parsed PDF content found for paper {paper_id}. Attempting to read raw PDF."
                )
                raw_pdf_path = loader.get_raw_pdf_path(paper_id)
                if raw_pdf_path:
                    try:
                        paper_content_for_template = read_paper_pdf(ctx, raw_pdf_path)
                        logger.info(f"Successfully read raw PDF for paper {paper_id}.")
                    except Exception as e:
                        logger.warning(
                            f"Failed to read raw PDF for paper {paper_id}: {e}. Using abstract as fallback."
                        )
                        paper_content_for_template = paper.abstract
                else:
                    logger.warning(
                        f"No raw PDF found for paper {paper_id}. Using abstract as fallback."
                    )
                    paper_content_for_template = paper.abstract

            # Use centralized path resolution for template
            template_path = get_review_template_path()

            try:
                with open(template_path, encoding="utf-8") as f:
                    template_content = f.read()
                # TODO max content length handling for models
                # full_input_contenxt_len > max_content_length

                # Format the template with paper information including full content
                review_template = template_content.format(
                    paper_title=paper.title,
                    paper_abstract=paper.abstract,
                    paper_full_content=paper_content_for_template,
                    tone=tone,
                    review_focus=review_focus,
                )

            except FileNotFoundError:
                logger.error(f"Review template file not found at {template_path}")
                raise ValueError(f"Review template configuration file missing: {template_path}")
            except Exception as e:
                logger.error(f"Error loading review template: {e}")
                raise ValueError(f"Failed to load review template: {str(e)}")

            logger.info(f"Created review template for paper {paper_id} (NOT a real review)")
            return review_template

        except Exception as e:
            logger.error(f"Error creating review template: {e}")
            raise ValueError(f"Failed to create review template: {str(e)}")

    @manager_agent.tool
    async def save_paper_review(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        paper_id: str,
        review_text: str,
        recommendation: str = "",
        confidence: float = 0.0,
    ) -> str:
        """Save agent-generated review to persistent storage.

        Args:
            paper_id: Unique identifier for the paper being reviewed.
            review_text: Review text generated by the agent.
            recommendation: Review recommendation (accept/reject/etc).
            confidence: Confidence score for the review (0.0-1.0).

        Returns:
            str: Path to the saved review file.
        """
        try:
            # Create PeerReadReview object
            review = PeerReadReview(
                impact="N/A",
                substance="N/A",
                appropriateness="N/A",
                meaningful_comparison="N/A",
                presentation_format="N/A",
                comments=review_text,
                soundness_correctness="N/A",
                originality="N/A",
                recommendation=recommendation or "N/A",
                clarity="N/A",
                reviewer_confidence=str(confidence) if confidence > 0 else "N/A",
            )

            # Save to persistent storage
            persistence = ReviewPersistence()
            filepath = persistence.save_review(paper_id, review)

            logger.info(f"Saved review for paper {paper_id} to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving paper review: {e}")
            raise ValueError(f"Failed to save review: {str(e)}")

    @manager_agent.tool
    async def save_structured_review(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        paper_id: str,
        structured_review: GeneratedReview,
    ) -> str:
        """Save a structured review object to persistent storage.

        Args:
            paper_id: Unique identifier for the paper being reviewed.
            structured_review: GeneratedReview object with validated fields.

        Returns:
            str: Path to the saved review file.
        """
        try:
            from datetime import UTC, datetime

            # Convert structured review to PeerReadReview format for persistence
            peerread_format = structured_review.to_peerread_format()
            # Create PeerReadReview with proper type conversion
            review = PeerReadReview(
                impact=peerread_format["IMPACT"] or "N/A",
                substance=peerread_format["SUBSTANCE"] or "N/A",
                appropriateness=peerread_format["APPROPRIATENESS"] or "N/A",
                meaningful_comparison=peerread_format["MEANINGFUL_COMPARISON"] or "N/A",
                presentation_format=peerread_format["PRESENTATION_FORMAT"] or "Poster",
                comments=peerread_format["comments"] or "No comments provided",
                soundness_correctness=peerread_format["SOUNDNESS_CORRECTNESS"] or "N/A",
                originality=peerread_format["ORIGINALITY"] or "N/A",
                recommendation=peerread_format["RECOMMENDATION"] or "N/A",
                clarity="N/A",
                reviewer_confidence=peerread_format["REVIEWER_CONFIDENCE"] or "N/A",
                is_meta_review=None,
            )

            # Save to persistent storage
            persistence = ReviewPersistence()
            filepath = persistence.save_review(paper_id, review)

            # Also save the original structured format for validation
            timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
            result = ReviewGenerationResult(
                paper_id=paper_id,
                review=structured_review,
                timestamp=timestamp,
                model_info="GPT-4o via PydanticAI",
            )

            # Save structured version alongside
            structured_path = filepath.replace(".json", "_structured.json")
            with open(structured_path, "w", encoding="utf-8") as f:
                dump(result.model_dump(), f, indent=2, ensure_ascii=False)

            logger.info(f"Saved structured review for paper {paper_id} to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving structured review: {e}")
            raise ValueError(f"Failed to save structured review: {str(e)}")
