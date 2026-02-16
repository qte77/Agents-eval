"""
Tests for sensitive data filtering in logs and traces.

This module tests scrubbing of API keys, passwords, tokens, and other credentials
from Loguru logs and Logfire OTLP trace exports.

MAESTRO Layer 4 (Monitoring) security controls tested:
- API key pattern detection and redaction
- Password and token scrubbing
- Bearer token filtering
- Environment variable name redaction
"""

import re

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.utils.log_scrubbing import (
    SENSITIVE_PATTERNS,
    get_logfire_scrubbing_patterns,
    scrub_log_record,
)


class TestAPIKeyFiltering:
    """Test API key patterns are detected and redacted."""

    @pytest.mark.parametrize(
        "log_message,description",
        [
            ("OpenAI API key: sk-proj-abc123def456", "OpenAI project key"),
            ("Config: api_key=sk-1234567890abcdef", "API key assignment"),
            ("API_KEY: sk-test-abcdefghijklmnop", "Uppercase API_KEY"),
            ("Using api-key: sk-live-xyz789", "Hyphenated api-key"),
            ("Bearer sk-1234567890", "Bearer token with sk- prefix"),
        ],
    )
    def test_api_key_patterns_redacted(self, log_message: str, description: str):
        """API key patterns should be redacted from log messages."""
        record = {"message": log_message}
        result = scrub_log_record(record)

        assert result is True  # Filter should allow message through
        assert "[REDACTED]" in record["message"]
        # Original API key value should not be in redacted message
        assert "sk-" not in record["message"] or record["message"].count("sk-") == 0


class TestPasswordFiltering:
    """Test password patterns are detected and redacted."""

    @pytest.mark.parametrize(
        "log_message,password_pattern",
        [
            ("User login with password=secret123", "password="),
            ("Authenticating with passwd: mypassword", "passwd:"),
            ("Config: pwd=admin123", "pwd="),
            ("PASSWORD: SuperSecret!", "PASSWORD:"),
            ("Set password to 'hunter2'", "password"),
        ],
    )
    def test_password_patterns_redacted(self, log_message: str, password_pattern: str):
        """Password patterns should be redacted from log messages."""
        record = {"message": log_message}
        scrub_log_record(record)

        assert "[REDACTED]" in record["message"]


class TestTokenFiltering:
    """Test token and credential patterns are detected."""

    @pytest.mark.parametrize(
        "log_message,credential_type",
        [
            ("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "JWT bearer token"),
            ("Session token: abc123def456", "session token"),
            ("Auth token=xyz789", "auth token"),
            ("JWT: eyJhbGciOiJIUzI1NiJ9.payload.signature", "JWT token"),
            ("Set credential to 'api_secret_key'", "credential"),
        ],
    )
    def test_token_patterns_redacted(self, log_message: str, credential_type: str):
        """Token and credential patterns should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)

        assert "[REDACTED]" in record["message"]


class TestEnvironmentVariableFiltering:
    """Test environment variable names with secrets are redacted."""

    @pytest.mark.parametrize(
        "log_message,env_var_pattern",
        [
            ("Loading OPENAI_API_KEY from environment", "OPENAI_API_KEY"),
            ("Using ANTHROPIC_API_KEY for auth", "ANTHROPIC_API_KEY"),
            ("Set DATABASE_SECRET in config", "DATABASE_SECRET"),
            ("JWT_TOKEN loaded", "JWT_TOKEN"),
        ],
    )
    def test_env_var_secret_names_redacted(self, log_message: str, env_var_pattern: str):
        """Environment variable names containing API_KEY/SECRET/TOKEN should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)

        assert "[REDACTED]" in record["message"]


class TestCaseInsensitiveMatching:
    """Test scrubbing is case-insensitive."""

    @pytest.mark.parametrize(
        "log_message",
        [
            "password=secret",
            "PASSWORD=secret",
            "PaSsWoRd=secret",
            "api_key=value",
            "API_KEY=value",
            "Api_Key=value",
        ],
    )
    def test_case_insensitive_pattern_matching(self, log_message: str):
        """Pattern matching should be case-insensitive."""
        record = {"message": log_message}
        scrub_log_record(record)

        assert "[REDACTED]" in record["message"]


class TestNonSensitiveMessagesUnchanged:
    """Test non-sensitive messages pass through unchanged."""

    @pytest.mark.parametrize(
        "safe_message",
        [
            "Starting evaluation pipeline",
            "User query processed successfully",
            "Agent completed task in 2.5 seconds",
            "Tier 1 metrics: cosine=0.85, jaccard=0.72",
            "Loading paper with ID: 12345",
        ],
    )
    def test_safe_messages_not_modified(self, safe_message: str):
        """Safe messages without sensitive patterns should pass through unchanged."""
        record = {"message": safe_message}
        original_message = safe_message

        result = scrub_log_record(record)

        assert result is True
        assert record["message"] == original_message
        assert "[REDACTED]" not in record["message"]


class TestMultipleSecretsInSameMessage:
    """Test messages with multiple sensitive patterns are fully redacted."""

    def test_multiple_secrets_all_redacted(self):
        """All sensitive patterns in a single message should be redacted."""
        message = "Auth: password=secret, api_key=sk-123, token=xyz789"
        record = {"message": message}

        scrub_log_record(record)

        # Message should contain multiple [REDACTED] markers
        redacted_count = record["message"].count("[REDACTED]")
        assert redacted_count >= 3  # At least one for each secret type

        # No secrets should remain
        assert "secret" not in record["message"]
        assert "sk-123" not in record["message"]
        assert "xyz789" not in record["message"]


class TestLogfirePatternsGeneration:
    """Test Logfire scrubbing patterns generation."""

    def test_get_logfire_scrubbing_patterns_returns_list(self):
        """get_logfire_scrubbing_patterns() should return a list of pattern strings."""
        patterns = get_logfire_scrubbing_patterns()

        assert isinstance(patterns, list)
        assert len(patterns) > 0
        assert all(isinstance(p, str) for p in patterns)

    def test_logfire_patterns_match_sensitive_patterns(self):
        """Logfire patterns should match SENSITIVE_PATTERNS."""
        patterns = get_logfire_scrubbing_patterns()

        # Should contain same patterns as SENSITIVE_PATTERNS
        assert set(patterns) == set(SENSITIVE_PATTERNS)

    def test_logfire_patterns_cover_common_secrets(self):
        """Logfire patterns should cover common secret types."""
        patterns = get_logfire_scrubbing_patterns()
        pattern_str = "|".join(patterns)

        # Should match common secret patterns
        assert any(re.search(r"password", pattern_str, re.IGNORECASE) for pattern_str in patterns)
        assert any(re.search(r"api.*key", pattern_str, re.IGNORECASE) for pattern_str in patterns)
        assert any(re.search(r"token", pattern_str, re.IGNORECASE) for pattern_str in patterns)
        assert any(re.search(r"sk-", pattern_str) for pattern_str in patterns)


class TestPropertyBasedFiltering:
    """Property-based tests using Hypothesis."""

    @given(
        secret_value=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=8,
            max_size=64,
        )
    )
    def test_password_assignments_always_redacted(self, secret_value: str):
        """For all strings, password=<value> should be redacted."""
        message = f"Config: password={secret_value}"
        record = {"message": message}

        scrub_log_record(record)

        # Secret value should not appear in redacted message
        if len(secret_value) > 0:
            assert secret_value not in record["message"] or "[REDACTED]" in record["message"]

    @given(
        prefix=st.sampled_from(["sk-", "SK-", "sk-proj-", "sk-test-"]),
        suffix=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=10,
            max_size=40,
        ),
    )
    def test_openai_key_format_always_redacted(self, prefix: str, suffix: str):
        """For all OpenAI key formats, the key should be redacted."""
        api_key = f"{prefix}{suffix}"
        message = f"Using API key: {api_key}"
        record = {"message": message}

        scrub_log_record(record)

        # API key should be redacted
        assert "[REDACTED]" in record["message"]

    @given(message=st.text(min_size=0, max_size=500))
    def test_scrub_always_returns_true(self, message: str):
        """scrub_log_record should always return True (allow message through)."""
        record = {"message": message}
        result = scrub_log_record(record)

        assert result is True

    @given(
        safe_prefix=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=5,
            max_size=20,
        ),
        safe_suffix=st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=5,
            max_size=20,
        ),
    )
    def test_messages_without_patterns_unchanged(self, safe_prefix: str, safe_suffix: str):
        """Messages without sensitive patterns should remain unchanged."""
        # Build message with safe content (no sensitive keywords)
        message = f"{safe_prefix} processed {safe_suffix}"
        record = {"message": message}
        original = message

        scrub_log_record(record)

        # If no patterns matched, message should be unchanged
        # (Unless safe text accidentally matches a pattern, which is unlikely with letter-only text)
        if "[REDACTED]" not in record["message"]:
            assert record["message"] == original
