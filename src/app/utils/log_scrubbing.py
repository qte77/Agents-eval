"""Log scrubbing patterns and sensitive data filtering.

This module provides scrubbing patterns and filters to redact sensitive data
from two independent output channels:

1. **Loguru** (file/console logs): Uses ``scrub_log_record()`` filter with the
   full ``SENSITIVE_PATTERNS`` set, since Loguru has no built-in scrubbing.
2. **Logfire** (OTLP trace export): Has built-in default patterns covering
   password, secret, credential, api_key, jwt, session, cookie, csrf, ssn,
   credit_card. We only supply *extra* patterns Logfire doesn't cover.

Security features:
- Pattern-based redaction for common secret types
- Loguru filter function for file sink integration
- Logfire extra patterns (additive, not duplicating built-in defaults)
- Case-insensitive pattern matching
"""

import re
from typing import Any

# Patterns already covered by Logfire's built-in scrubbing defaults:
#   password, passwd, mysql_pwd, secret, credential, auth (excl. "authors"),
#   private[._-]?key, api[._-]?key, session, cookie, csrf, xsrf, jwt, ssn,
#   social[._-]?security, credit[._-]?card
#
# See: https://logfire.pydantic.dev/docs/how-to-guides/scrubbing/

# Patterns NOT covered by Logfire defaults — supplied as extra_patterns
LOGFIRE_EXTRA_PATTERNS: frozenset[str] = frozenset(
    [
        r"bearer\s+\S+",  # Bearer token headers
        r"sk-\S+",  # OpenAI API key format
        r"password\s+to\s+['\"]?\S+",  # Natural language: "password to 'hunter2'"
        r"credential\s+to\s+['\"]?\S+",  # Natural language: "credential to 'val'"
        r"\b[A-Z_]+API_KEY\b",  # Env var names like OPENAI_API_KEY
        r"\b[A-Z_]+SECRET\b",  # Env var names like DATABASE_SECRET
        r"\b[A-Z_]+TOKEN\b",  # Env var names like JWT_TOKEN
    ]
)

# Full pattern set for Loguru (which has no built-in scrubbing).
# Includes both Logfire-default-covered patterns and our extras.
SENSITIVE_PATTERNS: frozenset[str] = frozenset(
    [
        # Assignment patterns (covered by Logfire defaults, needed for Loguru)
        r"password\s*[=:]\s*\S+",
        r"passwd\s*[=:]\s*\S+",
        r"pwd\s*[=:]\s*\S+",
        r"secret\s*[=:]\s*\S+",
        r"credential\s*[=:]\s*\S+",
        r"auth\s*[=:]\s*\S+",
        r"api[._-]?key\s*[=:]\s*\S+",
        r"token\s*[=:]\s*\S+",
        r"jwt\s*[=:]\s*\S+",
        # Extra patterns (not in Logfire defaults)
        *LOGFIRE_EXTRA_PATTERNS,
    ]
)


def scrub_log_record(record: dict[str, Any]) -> bool:
    """Scrub sensitive data from Loguru log record.

    This function is intended to be used as a Loguru filter. It modifies
    the log record in-place by replacing sensitive patterns with [REDACTED].
    Uses the full SENSITIVE_PATTERNS set since Loguru has no built-in scrubbing.

    Args:
        record: Loguru log record dict with 'message' key.

    Returns:
        bool: Always True to allow the (scrubbed) record to pass through.

    Example:
        >>> logger.add("file.log", filter=scrub_log_record)
    """
    message = record.get("message", "")

    for pattern in SENSITIVE_PATTERNS:
        message = re.sub(pattern, "[REDACTED]", message, flags=re.IGNORECASE)

    record["message"] = message
    return True


def get_logfire_scrubbing_patterns() -> list[str]:
    """Get extra scrubbing patterns for Logfire trace export.

    Returns only patterns NOT already covered by Logfire's built-in defaults.
    These are passed to ``logfire.ScrubbingOptions(extra_patterns=...)``.

    Returns:
        list[str]: List of regex pattern strings for Logfire extra scrubbing.

    Example:
        >>> import logfire
        >>> patterns = get_logfire_scrubbing_patterns()
        >>> logfire.configure(scrubbing=logfire.ScrubbingOptions(extra_patterns=patterns))
    """
    return list(LOGFIRE_EXTRA_PATTERNS)
