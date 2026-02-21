"""Prompt input sanitization with length limits and XML delimiter wrapping.

This module provides functions to sanitize user-controlled content before
interpolation into LLM prompts. It prevents prompt injection attacks by:
1. Truncating content to configurable length limits
2. Wrapping content in XML delimiters to separate data from instructions
3. Preserving content integrity (no escaping needed for LLM consumption)

Security features:
- Length-limited inputs prevent token-based DoS
- XML delimiters provide clear instruction/data separation
- No format string interpolation vulnerabilities
"""


def sanitize_for_prompt(content: str, max_length: int, delimiter: str = "content") -> str:
    """Sanitize content for inclusion in LLM prompts.

    Args:
        content: User-controlled content to sanitize.
        max_length: Maximum content length before truncation.
        delimiter: XML tag name for wrapping (default: "content").

    Returns:
        str: Sanitized content wrapped in XML delimiters, truncated if needed.

    Example:
        >>> sanitize_for_prompt("user input", max_length=100)
        '<content>user input</content>'
    """
    # Truncate if content exceeds max_length
    truncated = content[:max_length] if len(content) > max_length else content

    # Wrap in XML delimiters
    return f"<{delimiter}>{truncated}</{delimiter}>"


def sanitize_paper_title(title: str) -> str:
    """Sanitize paper title with 500 character limit.

    Args:
        title: Paper title from PeerRead dataset or user input.

    Returns:
        str: Sanitized title wrapped in <paper_title> delimiters.
    """
    return sanitize_for_prompt(title, max_length=500, delimiter="paper_title")


def sanitize_paper_abstract(abstract: str) -> str:
    """Sanitize paper abstract with 5000 character limit.

    Args:
        abstract: Paper abstract from PeerRead dataset.

    Returns:
        str: Sanitized abstract wrapped in <paper_abstract> delimiters.
    """
    return sanitize_for_prompt(abstract, max_length=5000, delimiter="paper_abstract")


def sanitize_paper_content(content: str, max_length: int = 50000) -> str:
    """Sanitize paper body content with format string injection protection.

    Unlike other sanitize functions, this also escapes curly braces to prevent
    Python str.format() injection when the content is interpolated into templates.
    Paper body content is adversary-controlled (raw PDF text) and may contain
    format string placeholders like {tone} or {0.__class__}.

    Args:
        content: Paper body content from PDF extraction.
        max_length: Maximum length of the escaped content before truncation
            (default: 50000). Applied after brace escaping, so the original
            content may be shorter than max_length when braces are present.

    Returns:
        str: Content with braces escaped, wrapped in <paper_content> delimiters.
    """
    # Reason: Escape braces BEFORE truncation to prevent splitting a {{ pair
    escaped = content.replace("{", "{{").replace("}", "}}")
    return sanitize_for_prompt(escaped, max_length=max_length, delimiter="paper_content")


def sanitize_review_text(review: str) -> str:
    """Sanitize review text with 50000 character limit.

    Args:
        review: Generated review text or user input.

    Returns:
        str: Sanitized review wrapped in <review_text> delimiters.
    """
    return sanitize_for_prompt(review, max_length=50000, delimiter="review_text")
