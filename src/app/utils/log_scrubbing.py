"""Log scrubbing patterns and sensitive data filtering.

This module provides scrubbing patterns and filters to redact sensitive data
from logs (Loguru) and traces (Logfire). Prevents data leakage of API keys,
passwords, tokens, and other credentials in log files and OTLP trace exports.

Security features:
- Pattern-based redaction for common secret types
- Loguru filter function for file sink integration
- Logfire scrubbing patterns for OTLP export
- Case-insensitive pattern matching
"""

import re
from typing import Any

# Sensitive data patterns for detection and redaction
# These patterns match common secret types in log messages
SENSITIVE_PATTERNS = frozenset(
    [
        r"password\s*[=:]\s*\S+",
        r"passwd\s*[=:]\s*\S+",
        r"pwd\s*[=:]\s*\S+",
        r"secret\s*[=:]\s*\S+",
        r"credential\s*[=:]\s*\S+",
        r"auth\s*[=:]\s*\S+",
        r"api[._-]?key\s*[=:]\s*\S+",
        r"token\s*[=:]\s*\S+",
        r"jwt\s*[=:]\s*\S+",
        r"bearer\s+\S+",
        r"sk-[a-zA-Z0-9]+",  # OpenAI API key format
        # Environment variable patterns
        r"\b[A-Z_]+API_KEY\b",
        r"\b[A-Z_]+SECRET\b",
        r"\b[A-Z_]+TOKEN\b",
    ]
)


def scrub_log_record(record: dict[str, Any]) -> bool:
    """Scrub sensitive data from Loguru log record.

    This function is intended to be used as a Loguru filter. It modifies
    the log record in-place by replacing sensitive patterns with [REDACTED].

    Args:
        record: Loguru log record dict with 'message' key.

    Returns:
        bool: Always True to allow the (scrubbed) record to pass through.

    Example:
        >>> logger.add("file.log", filter=scrub_log_record)
    """
    message = record.get("message", "")

    # Apply all patterns with case-insensitive matching
    for pattern in SENSITIVE_PATTERNS:
        # Use re.IGNORECASE for case-insensitive matching
        message = re.sub(pattern, "[REDACTED]", message, flags=re.IGNORECASE)

    record["message"] = message
    return True


def get_logfire_scrubbing_patterns() -> list[str]:
    """Get scrubbing patterns for Logfire trace export.

    Returns pattern strings for use with logfire.ScrubbingOptions(extra_patterns=...).
    These patterns are combined with Logfire's default patterns and redact sensitive
    data in OTLP trace exports to Phoenix.

    Returns:
        list[str]: List of regex pattern strings for Logfire scrubbing.

    Example:
        >>> import logfire
        >>> patterns = get_logfire_scrubbing_patterns()
        >>> logfire.configure(scrubbing=logfire.ScrubbingOptions(extra_patterns=patterns))
    """
    # Return pattern strings (Logfire handles compilation and case-insensitivity)
    return list(SENSITIVE_PATTERNS)
