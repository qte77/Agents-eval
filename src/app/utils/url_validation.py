"""
URL validation and SSRF prevention utilities.

This module provides URL validation functionality to prevent SSRF (Server-Side Request Forgery)
attacks by enforcing HTTPS-only and domain allowlisting for all external requests.

CVE Context:
- CVE-2026-25580: PydanticAI SSRF vulnerability allowing information disclosure via malicious
  URLs in message history. This module mitigates the vulnerability by validating all URLs
  before HTTP requests.
"""

# Allowed domains for external HTTP requests
# This allowlist prevents SSRF attacks against internal services
ALLOWED_DOMAINS: frozenset[str] = frozenset([
    "raw.githubusercontent.com",  # PeerRead dataset downloads
    "arxiv.org",                   # arXiv paper repository
    "api.openai.com",              # OpenAI API
    "api.anthropic.com",           # Anthropic API
    "api.cerebras.ai",             # Cerebras API
])


def validate_url(url: str) -> str:
    """
    Validate URL for SSRF protection.

    Enforces HTTPS-only and domain allowlisting to prevent SSRF attacks.

    Args:
        url: URL to validate.

    Returns:
        The validated URL if it passes all checks.

    Raises:
        ValueError: If URL fails validation (non-HTTPS, blocked domain, malformed).

    Examples:
        >>> validate_url("https://raw.githubusercontent.com/data.json")
        'https://raw.githubusercontent.com/data.json'

        >>> validate_url("http://evil.com/secrets")
        Traceback (most recent call last):
            ...
        ValueError: Only HTTPS URLs allowed

        >>> validate_url("https://169.254.169.254/metadata")
        Traceback (most recent call last):
            ...
        ValueError: URL domain not allowed: 169.254.169.254
    """
    from urllib.parse import urlparse

    # Validate input is not empty or whitespace-only
    if not url or not url.strip():
        raise ValueError("URL cannot be empty or whitespace-only")

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Malformed URL: {e}") from e

    # Enforce HTTPS-only
    if parsed.scheme != "https":
        raise ValueError("Only HTTPS URLs allowed")

    # Extract domain (netloc without port/credentials)
    # netloc format: [user[:password]@]host[:port]
    netloc = parsed.netloc
    if not netloc:
        raise ValueError("URL must contain a domain")

    # Remove credentials if present (user:pass@domain)
    if "@" in netloc:
        netloc = netloc.split("@")[-1]

    # Remove port if present (domain:port)
    domain = netloc.split(":")[0]

    # Check domain against allowlist
    if domain not in ALLOWED_DOMAINS:
        # Error message contains only domain, not full URL (prevents log injection)
        raise ValueError(f"URL domain not allowed: {domain}")

    return url
