"""
PeerRead agent tools for multi-agent system integration.

This module provides agent tools that enable the manager agent to interact
with the PeerRead dataset for paper retrieval, querying, and review evaluation.
"""

import time
from collections.abc import Awaitable, Callable
from json import dump
from pathlib import Path
from typing import TypeVar

from markitdown import MarkItDown
from pydantic import BaseModel
from pydantic_ai import Agent, ModelRetry, RunContext

from app.data_models.peerread_models import (
    GeneratedReview,
    PeerReadPaper,
    PeerReadReview,
    ReviewGenerationResult,
)
from app.data_utils.datasets_peerread import PeerReadLoader, load_peerread_config
from app.data_utils.review_persistence import ReviewPersistence
from app.judge.trace_processors import get_trace_collector
from app.utils.log import logger
from app.utils.paths import get_review_template_path
from app.utils.prompt_sanitization import (
    sanitize_paper_abstract,
    sanitize_paper_content,
    sanitize_paper_title,
)


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
    # Reason: LLMs hallucinate URLs for paper PDFs; reject them defensively instead of crashing
    if isinstance(pdf_path, str) and pdf_path.startswith(("http://", "https://")):
        return (
            f"Error: URLs are not supported. "
            f"Use paper_id with get_paper_content instead. Received: {pdf_path}"
        )

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


T = TypeVar("T")


async def _traced_tool_call(  # noqa: UP047
    agent_id: str,
    tool_name: str,
    context: str,
    fn: Callable[[], Awaitable[T]],
    error_cls: type[Exception] = ModelRetry,
    error_msg: str = "",
) -> T:
    """Execute an async tool function with tracing and error handling.

    Wraps tool business logic with standardized timing, trace logging,
    and error handling to eliminate boilerplate across PeerRead tools.

    Args:
        agent_id: Agent identifier for trace logging.
        tool_name: Name of the tool being called.
        context: Context string for trace logging (e.g., "paper_id=123").
        fn: Zero-arg async callable containing the tool's business logic.
        error_cls: Exception type to wrap unexpected errors (default: ModelRetry).
        error_msg: Prefix for the error message on unexpected failures.

    Returns:
        T: The result from the tool's business logic.

    Raises:
        ModelRetry: Re-raised if the business logic raises it.
        error_cls: Wraps any other exception with the provided error_msg.
    """
    start_time = time.perf_counter()
    trace_collector = get_trace_collector()
    success = False

    try:
        result = await fn()
        success = True
        return result
    except ModelRetry:
        raise
    except Exception as e:
        logger.error(f"Error in {tool_name}: {e}")
        msg = f"{error_msg}: {str(e)}" if error_msg else str(e)
        raise error_cls(msg)
    finally:
        duration = time.perf_counter() - start_time
        trace_collector.log_tool_call(
            agent_id=agent_id,
            tool_name=tool_name,
            success=success,
            duration=duration,
            context=context,
        )


def add_peerread_tools_to_agent(agent: Agent[None, BaseModel], agent_id: str = "manager"):
    """Add PeerRead dataset tools to an agent.

    Args:
        agent: The agent to which PeerRead tools will be added.
        agent_id: The agent identifier for tracing (default: "manager").
    """

    @agent.tool
    async def get_peerread_paper(ctx: RunContext[None], paper_id: str) -> PeerReadPaper:  # type: ignore[reportUnusedFunction]
        """Get a specific paper from the PeerRead dataset.

        Only call this tool when the user explicitly asks about a specific paper.
        Do NOT call for greetings, general questions, or non-paper queries.

        Args:
            paper_id: Unique identifier for the paper (e.g. '104', '305').

        Returns:
            PeerReadPaper with title, abstract, and reviews.
        """

        async def _fn() -> PeerReadPaper:
            config = load_peerread_config()
            loader = PeerReadLoader(config)
            paper = loader.get_paper_by_id(paper_id)
            if not paper:
                raise ModelRetry(f"Paper {paper_id} not found in PeerRead dataset")
            logger.info(f"Retrieved paper {paper_id}: {paper.title[:50]}...")
            return paper

        return await _traced_tool_call(
            agent_id=agent_id,
            tool_name="get_peerread_paper",
            context=f"paper_id={paper_id}",
            fn=_fn,
            error_msg="Failed to retrieve paper",
        )

    @agent.tool
    async def query_peerread_papers(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None], venue: str = "", min_reviews: int = 1
    ) -> list[PeerReadPaper]:
        """Query papers from PeerRead dataset with filters.

        Only call this tool when the user explicitly asks to search or list papers.
        Do NOT call for greetings, general questions, or non-paper queries.

        Args:
            venue: Filter by conference venue (empty for all venues).
            min_reviews: Minimum number of reviews required per paper.

        Returns:
            List of PeerReadPaper objects matching the criteria.
        """

        async def _fn() -> list[PeerReadPaper]:
            config = load_peerread_config()
            loader = PeerReadLoader(config)
            papers = loader.query_papers(
                venue=venue if venue else None,
                min_reviews=min_reviews,
                limit=config.max_papers_per_query,
            )
            logger.info(f"Found {len(papers)} papers matching criteria")
            return papers

        return await _traced_tool_call(
            agent_id=agent_id,
            tool_name="query_peerread_papers",
            context=f"venue={venue},min_reviews={min_reviews}",
            fn=_fn,
            error_msg="Failed to query papers",
        )

    @agent.tool
    async def get_paper_content(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        paper_id: str,
    ) -> str:
        """Get the full text content of a paper from the local PeerRead dataset.

        Returns full paper text using a fallback chain: parsed JSON → raw PDF → abstract.
        Use this tool to read a paper's body text for analysis or review generation.

        Note: Requires `paper_id` (e.g. "1105.1072"), NOT a file path or URL.

        Args:
            paper_id: Unique identifier for the paper (e.g. "1105.1072").
                      Do NOT pass a URL or file path.

        Returns:
            str: Full paper text content from the local PeerRead dataset.
        """

        async def _fn() -> str:
            config = load_peerread_config()
            loader = PeerReadLoader(config)
            paper = loader.get_paper_by_id(paper_id)
            if not paper:
                raise ValueError(f"Paper {paper_id} not found in PeerRead dataset")
            content = _load_paper_content_with_fallback(ctx, loader, paper_id, paper.abstract)
            logger.info(f"Retrieved content for paper {paper_id}")
            return content

        return await _traced_tool_call(
            agent_id=agent_id,
            tool_name="get_paper_content",
            context=f"paper_id={paper_id}",
            fn=_fn,
            error_cls=ValueError,
            error_msg="Failed to retrieve paper content",
        )


def _truncate_paper_content(abstract: str, body: str, max_length: int) -> str:
    """Truncate paper content to fit within max_length while preserving abstract.

    Args:
        abstract: The paper abstract (always preserved).
        body: The full body content to be truncated if necessary.
        max_length: Maximum total character length.

    Returns:
        str: Content with abstract preserved and body truncated if needed.
    """
    # Reason: Always preserve abstract as it contains critical paper summary
    abstract_section = f"Abstract:\n{abstract}\n\n"
    full_content = abstract_section + body

    if len(full_content) <= max_length:
        return full_content

    # Calculate available space for body after abstract
    available_for_body = max_length - len(abstract_section) - len("\n[TRUNCATED]")

    if available_for_body <= 0:
        logger.warning(
            f"Content truncation: abstract alone exceeds max_length. "
            f"Original: {len(full_content)} chars, Limit: {max_length} chars"
        )
        return abstract_section + "[TRUNCATED]"

    truncated_body = body[:available_for_body]
    result = abstract_section + truncated_body + "\n[TRUNCATED]"

    logger.warning(
        f"Content truncated: {len(full_content)} chars -> {len(result)} chars (limit: {max_length})"
    )

    return result


def _load_paper_content_with_fallback(
    ctx: RunContext[None],
    loader: PeerReadLoader,
    paper_id: str,
    paper_abstract: str,
) -> str:
    """Load paper content with PDF fallback strategy."""
    paper_content = loader.load_parsed_pdf_content(paper_id)
    if paper_content:
        return paper_content

    logger.warning(f"No parsed PDF content found for paper {paper_id}. Attempting to read raw PDF.")
    raw_pdf_path = loader.get_raw_pdf_path(paper_id)

    if not raw_pdf_path:
        logger.warning(f"No raw PDF found for paper {paper_id}. Using abstract as fallback.")
        return paper_abstract

    try:
        paper_content = read_paper_pdf(ctx, raw_pdf_path)
        logger.info(f"Successfully read raw PDF for paper {paper_id}.")
        return paper_content
    except Exception as e:
        logger.warning(
            f"Failed to read raw PDF for paper {paper_id}: {e}. Using abstract as fallback."
        )
        return paper_abstract


def _load_and_format_template(
    paper_title: str,
    paper_abstract: str,
    paper_content: str,
    tone: str,
    review_focus: str,
    max_content_length: int,
) -> str:
    """Load review template and format with paper information.

    Args:
        paper_title: Title of the paper.
        paper_abstract: Abstract of the paper.
        paper_content: Full body content of the paper.
        tone: Review tone.
        review_focus: Review focus type.
        max_content_length: Maximum content length for truncation.

    Returns:
        str: Formatted review template with truncated content if needed.
    """
    template_path = get_review_template_path()

    try:
        with open(template_path, encoding="utf-8") as f:
            template_content = f.read()

        # Truncate paper content before formatting into template
        truncated_content = _truncate_paper_content(
            paper_abstract, paper_content, max_content_length
        )

        # Sanitize user-controlled content before template formatting
        # This prevents format string injection attacks while preserving template compatibility
        sanitized_title = sanitize_paper_title(paper_title)
        sanitized_abstract = sanitize_paper_abstract(paper_abstract)
        sanitized_content = sanitize_paper_content(truncated_content)

        # Safe to use .format() here since all user inputs are sanitized:
        # - title/abstract: XML-wrapped
        # - paper content: braces escaped + XML-wrapped (prevents format string injection)
        return template_content.format(
            paper_title=sanitized_title,
            paper_abstract=sanitized_abstract,
            paper_full_content=sanitized_content,
            tone=tone,
            review_focus=review_focus,
        )
    except FileNotFoundError:
        logger.error(f"Review template file not found at {template_path}")
        raise ValueError(f"Review template configuration file missing: {template_path}")
    except Exception as e:
        logger.error(f"Error loading review template: {e}")
        raise ValueError(f"Failed to load review template: {str(e)}")


def add_peerread_review_tools_to_agent(
    agent: Agent[None, BaseModel],
    agent_id: str = "manager",
    max_content_length: int = 15000,
):
    """Add PeerRead review generation and persistence tools to an agent.

    Args:
        agent: The agent to which review tools will be added.
        agent_id: The agent identifier for tracing (default: "manager").
        max_content_length: The maximum number of characters to include in the prompt.
    """

    @agent.tool
    async def generate_paper_review_content_from_template(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        paper_id: str,
        review_focus: str = "comprehensive",
        tone: str = "professional",
    ) -> str:
        """Create a review template for a specific paper.

        Only call this tool when the user explicitly asks to review a paper.
        Do NOT call for greetings, general questions, or non-paper queries.

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

        async def _fn() -> str:
            config = load_peerread_config()
            loader = PeerReadLoader(config)
            paper = loader.get_paper_by_id(paper_id)
            if not paper:
                raise ModelRetry(f"Paper {paper_id} not found in PeerRead dataset")
            paper_content = _load_paper_content_with_fallback(ctx, loader, paper_id, paper.abstract)
            review_template = _load_and_format_template(
                paper.title, paper.abstract, paper_content, tone, review_focus, max_content_length
            )
            logger.info(f"Created review template for paper {paper_id} (NOT a real review)")
            return review_template

        return await _traced_tool_call(
            agent_id=agent_id,
            tool_name="generate_paper_review_content_from_template",
            context=f"paper_id={paper_id},focus={review_focus}",
            fn=_fn,
            error_msg="Failed to create review template",
        )

    @agent.tool
    async def save_paper_review(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        paper_id: str,
        review_text: str,
        recommendation: str = "",
        confidence: float = 0.0,
    ) -> str:
        """Save agent-generated review to persistent storage.

        Only call this tool after generating a review the user requested.
        Do NOT call for greetings, general questions, or non-paper queries.

        Args:
            paper_id: Unique identifier for the paper being reviewed.
            review_text: Review text generated by the agent.
            recommendation: Review recommendation (accept/reject/etc).
            confidence: Confidence score for the review (0.0-1.0).

        Returns:
            str: Path to the saved review file.
        """

        async def _fn() -> str:
            review = PeerReadReview(
                comments=review_text,
                recommendation=recommendation if recommendation else "UNKNOWN",
                reviewer_confidence=str(confidence) if confidence > 0 else "UNKNOWN",
            )
            persistence = ReviewPersistence()
            filepath = persistence.save_review(paper_id, review)
            logger.info(f"Saved review for paper {paper_id} to {filepath}")
            return filepath

        return await _traced_tool_call(
            agent_id=agent_id,
            tool_name="save_paper_review",
            context=f"paper_id={paper_id}",
            fn=_fn,
            error_cls=ValueError,
            error_msg="Failed to save review",
        )

    @agent.tool
    async def save_structured_review(  # type: ignore[reportUnusedFunction]
        ctx: RunContext[None],
        paper_id: str,
        structured_review: GeneratedReview,
    ) -> str:
        """Save a structured review object to persistent storage.

        Only call this tool after generating a review the user requested.
        Do NOT call for greetings, general questions, or non-paper queries.

        Args:
            paper_id: Unique identifier for the paper being reviewed.
            structured_review: GeneratedReview object with validated fields.

        Returns:
            str: Path to the saved review file.
        """

        async def _fn() -> str:
            from datetime import UTC, datetime

            peerread_format = structured_review.to_peerread_format()
            review = PeerReadReview.model_validate(peerread_format)

            persistence = ReviewPersistence()
            filepath = persistence.save_review(paper_id, review)

            timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
            result = ReviewGenerationResult(
                paper_id=paper_id,
                review=structured_review,
                timestamp=timestamp,
                model_info="GPT-4o via PydanticAI",
            )

            structured_path = filepath.replace(".json", "_structured.json")
            with open(structured_path, "w", encoding="utf-8") as f:
                dump(result.model_dump(), f, indent=2, ensure_ascii=False)

            logger.info(f"Saved structured review for paper {paper_id} to {filepath}")
            return filepath

        return await _traced_tool_call(
            agent_id=agent_id,
            tool_name="save_structured_review",
            context=f"paper_id={paper_id}",
            fn=_fn,
            error_cls=ValueError,
            error_msg="Failed to save structured review",
        )


# Backward compatibility alias
def add_peerread_review_tools_to_manager(
    manager_agent: Agent[None, BaseModel], max_content_length: int = 15000
):
    """Backward compatibility wrapper for add_peerread_review_tools_to_agent.

    Deprecated: Use add_peerread_review_tools_to_agent instead.

    Args:
        manager_agent: The manager agent to which review tools will be added.
        max_content_length: The maximum number of characters to include in the prompt.
    """
    return add_peerread_review_tools_to_agent(
        manager_agent, agent_id="manager", max_content_length=max_content_length
    )
