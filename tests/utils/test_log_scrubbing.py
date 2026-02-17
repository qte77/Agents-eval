"""Tests for log scrubbing patterns and sensitive data filtering.

Verifies that Loguru filters and Logfire scrubbing patterns correctly redact
sensitive data from logs and traces while preserving non-sensitive content.
"""

import re

from hypothesis import given
from hypothesis import strategies as st


class TestSensitivePatterns:
    """Test the sensitive data pattern definitions."""

    def test_sensitive_patterns_exist(self):
        """Sensitive patterns list should be defined."""
        from app.utils.log_scrubbing import SENSITIVE_PATTERNS

        assert isinstance(SENSITIVE_PATTERNS, (list, tuple, frozenset))
        assert len(SENSITIVE_PATTERNS) > 0

    def test_sensitive_patterns_include_key_types(self):
        """Sensitive patterns should include common secret types."""
        from app.utils.log_scrubbing import SENSITIVE_PATTERNS

        # Convert to lowercase for case-insensitive check
        patterns_str = " ".join(str(p) for p in SENSITIVE_PATTERNS).lower()

        # Must include patterns for these categories
        assert any(keyword in patterns_str for keyword in ["password", "passwd", "pwd"]), (
            "Missing password patterns"
        )
        assert any(keyword in patterns_str for keyword in ["secret", "credential"]), (
            "Missing secret/credential patterns"
        )
        assert any(keyword in patterns_str for keyword in ["api", "key", "token"]), (
            "Missing API key/token patterns"
        )


class TestLogRecordScrubbing:
    """Test Loguru log record scrubbing function."""

    def test_scrub_log_record_redacts_api_key(self):
        """Log messages containing API keys should be redacted."""
        from app.utils.log_scrubbing import scrub_log_record

        record = {"message": "Using API key: sk-1234567890abcdef"}
        result = scrub_log_record(record)

        assert result is True  # Record was modified
        assert "sk-1234567890abcdef" not in record["message"]
        assert "[REDACTED]" in record["message"]

    def test_scrub_log_record_redacts_password(self):
        """Log messages containing passwords should be redacted."""
        from app.utils.log_scrubbing import scrub_log_record

        record = {"message": "Login failed for password=supersecret123"}
        result = scrub_log_record(record)

        assert result is True
        assert "supersecret123" not in record["message"]
        assert "[REDACTED]" in record["message"]

    def test_scrub_log_record_redacts_bearer_token(self):
        """Log messages with Bearer tokens should be redacted."""
        from app.utils.log_scrubbing import scrub_log_record

        record = {"message": "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        result = scrub_log_record(record)

        assert result is True
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record["message"]
        assert "[REDACTED]" in record["message"]

    def test_scrub_log_record_preserves_normal_messages(self):
        """Non-sensitive log messages should pass through unchanged."""
        from app.utils.log_scrubbing import scrub_log_record

        record = {"message": "Processing paper ID 12345"}
        original_message = record["message"]
        result = scrub_log_record(record)

        assert result is True
        assert record["message"] == original_message
        assert "[REDACTED]" not in record["message"]

    def test_scrub_log_record_redacts_env_var_names(self):
        """Environment variable names containing sensitive keywords should be redacted."""
        from app.utils.log_scrubbing import scrub_log_record

        record = {"message": "Set environment variable: OPENAI_API_KEY"}
        result = scrub_log_record(record)

        assert result is True
        assert "OPENAI_API_KEY" not in record["message"] or "[REDACTED]" in record["message"]

    @given(
        secret_value=st.text(
            alphabet=st.characters(blacklist_categories=("Cs", "Cc")),
            min_size=8,
            max_size=64,
        ).filter(lambda s: "[REDACTED]" not in s)  # Exclude edge case
    )
    def test_scrub_log_record_property_any_message_with_api_key_pattern(self, secret_value: str):
        """Property test: any message with 'api_key=' should be redacted."""
        from app.utils.log_scrubbing import scrub_log_record

        record = {"message": f"Config loaded with api_key={secret_value}"}
        original_message = record["message"]
        scrub_log_record(record)

        # The pattern 'api_key=' should be matched and redacted
        assert "[REDACTED]" in record["message"]
        # The original message should be modified
        assert record["message"] != original_message


class TestLogfireScrubbingPatterns:
    """Test Logfire scrubbing pattern configuration."""

    def test_get_logfire_scrubbing_patterns_returns_list(self):
        """Logfire scrubbing patterns should return a list or dict."""
        from app.utils.log_scrubbing import get_logfire_scrubbing_patterns

        patterns = get_logfire_scrubbing_patterns()

        # Logfire.configure expects scrubbing parameter as list or dict
        assert isinstance(patterns, (list, dict))

    def test_logfire_patterns_include_key_fields(self):
        """Logfire scrubbing patterns should include common sensitive field names."""
        from app.utils.log_scrubbing import get_logfire_scrubbing_patterns

        patterns = get_logfire_scrubbing_patterns()

        # Convert to string representation for flexible checking
        patterns_str = str(patterns).lower()

        # Must include patterns for these field names
        assert any(
            keyword in patterns_str for keyword in ["password", "secret", "api", "key", "token"]
        ), "Logfire patterns missing common sensitive fields"

    def test_logfire_patterns_compatible_with_configure(self):
        """Logfire scrubbing patterns should be compatible with logfire.configure()."""
        from app.utils.log_scrubbing import get_logfire_scrubbing_patterns

        patterns = get_logfire_scrubbing_patterns()

        # If it's a list, elements should be strings or regex patterns
        if isinstance(patterns, list):
            for pattern in patterns:
                assert isinstance(pattern, (str, re.Pattern))

        # If it's a dict, should have valid scrubbing config structure
        elif isinstance(patterns, dict):
            # Common Logfire scrubbing config keys
            assert any(
                key in patterns for key in ["callback", "extra", "patterns", "redaction_text"]
            )
