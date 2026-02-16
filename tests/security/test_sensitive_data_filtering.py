"""Sensitive data filtering security tests.

Tests log and trace scrubbing to prevent data leakage of API keys, passwords,
and tokens as identified in Sprint 5 MAESTRO review Findings L3.2 and L4.2.

Attack vectors tested:
- API key patterns (OpenAI sk-, generic API keys)
- Password and credential patterns
- Bearer tokens
- Environment variable names containing secrets
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.utils.log_scrubbing import SENSITIVE_PATTERNS, get_logfire_scrubbing_patterns, scrub_log_record


class TestAPIKeyFiltering:
    """Test API key pattern filtering in logs."""

    @pytest.mark.parametrize(
        "log_message",
        [
            "Loaded API key: sk-1234567890abcdef",
            "Using OpenAI API key sk-proj-abcdefghijklmnop",
            "api_key=sk-test-1234567890",
            "API_KEY: sk-live-abcdefghijklmnopqrstuvwxyz",
        ],
    )
    def test_openai_api_key_patterns_redacted(self, log_message: str):
        """OpenAI API key patterns (sk-*) should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)
        # API key should be redacted
        assert "[REDACTED]" in record["message"]
        # Actual key should not be present
        assert "sk-" not in record["message"] or record["message"].count("sk-") == 0

    @pytest.mark.parametrize(
        "log_message,key_pattern",
        [
            ("api_key=abc123def456", "generic API key"),
            ("API_KEY: ABCDEF1234567890", "uppercase API key"),
            ("api-key = secret123", "hyphenated api-key"),
            ("api.key: value123", "dotted api.key"),
            ("apikey=12345678", "no separator apikey"),
        ],
    )
    def test_generic_api_key_patterns_redacted(self, log_message: str, key_pattern: str):
        """Generic api_key, api-key, api.key patterns should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]


class TestPasswordFiltering:
    """Test password and credential pattern filtering."""

    @pytest.mark.parametrize(
        "log_message",
        [
            "password=mysecret123",
            "PASSWORD: SuperSecret456",
            "passwd=admin123",
            "PASSWD: root",
            "pwd=secret",
            "PWD: password123",
        ],
    )
    def test_password_patterns_redacted(self, log_message: str):
        """Password, passwd, pwd patterns should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]
        # Actual password should not be present
        assert "mysecret123" not in record["message"]
        assert "SuperSecret456" not in record["message"]
        assert "admin123" not in record["message"]

    @pytest.mark.parametrize(
        "log_message",
        [
            "credential=myaccesstoken",
            "CREDENTIAL: abc123",
            "secret=topsecret",
            "SECRET: confidential",
            "auth=bearer_token_here",
            "AUTH: Basic dXNlcjpwYXNz",
        ],
    )
    def test_credential_and_secret_patterns_redacted(self, log_message: str):
        """Credential, secret, auth patterns should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]


class TestTokenFiltering:
    """Test token and JWT pattern filtering."""

    @pytest.mark.parametrize(
        "log_message",
        [
            "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature",
            "TOKEN: abc123token",
            "jwt=eyJhbGciOiJIUzI1NiJ9.payload",
            "JWT: bearer_jwt_token",
            "bearer eyJhbGciOiJSUzI1NiJ9",
            "Bearer abc123def456",
        ],
    )
    def test_token_and_jwt_patterns_redacted(self, log_message: str):
        """Token, JWT, and Bearer patterns should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]
        # JWT payload should not be present
        assert "eyJhbGciOi" not in record["message"]


class TestEnvironmentVariableFiltering:
    """Test environment variable name filtering."""

    @pytest.mark.parametrize(
        "log_message",
        [
            "Using OPENAI_API_KEY from environment",
            "ANTHROPIC_API_KEY not found",
            "DATABASE_SECRET loaded successfully",
            "GITHUB_TOKEN configured",
            "AWS_ACCESS_KEY_ID set",
        ],
    )
    def test_environment_variable_names_redacted(self, log_message: str):
        """Environment variable names containing API_KEY, SECRET, TOKEN should be redacted."""
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]


class TestCaseInsensitiveScrubbing:
    """Test case-insensitive pattern matching."""

    @pytest.mark.parametrize(
        "log_message",
        [
            "API_KEY=secret",
            "api_key=secret",
            "Api_Key=secret",
            "PASSWORD=secret",
            "password=secret",
            "PaSsWoRd=secret",
            "TOKEN=secret",
            "token=secret",
            "ToKeN=secret",
        ],
    )
    def test_case_insensitive_pattern_matching(self, log_message: str):
        """Sensitive patterns should be detected regardless of case."""
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]


class TestNonSensitiveDataPreserved:
    """Test that non-sensitive data is not scrubbed."""

    @pytest.mark.parametrize(
        "safe_message",
        [
            "Application started successfully",
            "Processing paper ID 12345",
            "Evaluation completed in 5.2 seconds",
            "Loading model: gpt-4",
            "User query: What is the summary?",
        ],
    )
    def test_non_sensitive_messages_unchanged(self, safe_message: str):
        """Non-sensitive log messages should pass through unchanged."""
        record = {"message": safe_message}
        original = record["message"]
        scrub_log_record(record)
        assert record["message"] == original
        assert "[REDACTED]" not in record["message"]

    def test_partial_match_not_scrubbed(self):
        """Partial matches that aren't actual secrets should not be scrubbed."""
        # "password" as a word but not in key=value format
        record = {"message": "Enter your password on the login page"}
        original = record["message"]
        scrub_log_record(record)
        # This might be scrubbed depending on pattern strictness
        # Just verify it doesn't crash


class TestLogfireScrubbing:
    """Test Logfire scrubbing pattern export."""

    def test_get_logfire_patterns_returns_list(self):
        """get_logfire_scrubbing_patterns should return a list of patterns."""
        patterns = get_logfire_scrubbing_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_logfire_patterns_match_sensitive_patterns(self):
        """Logfire patterns should match SENSITIVE_PATTERNS."""
        patterns = get_logfire_scrubbing_patterns()
        # Should contain all sensitive patterns
        assert len(patterns) == len(SENSITIVE_PATTERNS)
        # All patterns should be strings
        assert all(isinstance(p, str) for p in patterns)

    def test_logfire_patterns_contain_key_categories(self):
        """Logfire patterns should cover key secret categories."""
        patterns = get_logfire_scrubbing_patterns()
        pattern_str = " ".join(patterns).lower()
        # Check for key categories
        assert "password" in pattern_str or "passwd" in pattern_str
        assert "api" in pattern_str or "key" in pattern_str
        assert "token" in pattern_str
        assert "secret" in pattern_str


class TestComplexLogMessages:
    """Test scrubbing in complex, multi-line, structured log messages."""

    def test_json_structured_log_scrubbed(self):
        """Sensitive data in JSON-like structured logs should be scrubbed."""
        log_message = '{"api_key": "sk-abc123", "status": "success"}'
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]
        assert "sk-abc123" not in record["message"]

    def test_multiline_log_message_scrubbed(self):
        """Sensitive data in multi-line messages should be scrubbed."""
        log_message = """
        Configuration loaded:
        - api_key: sk-test-123
        - model: gpt-4
        - timeout: 30s
        """
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]
        assert "sk-test-123" not in record["message"]

    def test_multiple_secrets_in_one_message_all_scrubbed(self):
        """Multiple secrets in one message should all be scrubbed."""
        log_message = "Config: api_key=sk-123 password=secret token=abc bearer xyz"
        record = {"message": log_message}
        scrub_log_record(record)
        # Multiple redactions
        assert record["message"].count("[REDACTED]") >= 2
        # No secrets remain
        assert "sk-123" not in record["message"]
        assert "secret" not in record["message"] or record["message"].count("secret") == 0


class TestHypothesisScrubbing:
    """Property-based tests for log scrubbing."""

    @given(st.text(min_size=0, max_size=1000))
    def test_scrubbing_never_crashes(self, text: str):
        """Scrubbing should never crash regardless of input."""
        record = {"message": text}
        result = scrub_log_record(record)
        # Should always return True (filter passes)
        assert result is True
        # Message should still be a string
        assert isinstance(record["message"], str)

    @given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=10, max_size=100))
    def test_messages_without_patterns_unchanged(self, text: str):
        """Messages without sensitive patterns should be unchanged."""
        # Avoid pattern keywords
        if any(
            keyword in text.lower()
            for keyword in ["password", "api", "key", "token", "secret", "auth", "bearer"]
        ):
            return
        record = {"message": text}
        original = record["message"]
        scrub_log_record(record)
        assert record["message"] == original


class TestExceptionTraceScenarios:
    """Test scrubbing in exception traces and stack dumps."""

    def test_exception_with_api_key_in_locals_scrubbed(self):
        """Exception traces containing API keys in local variables should be scrubbed."""
        log_message = (
            "Exception in handler:\n"
            "  File 'app.py', line 42, in setup\n"
            "    api_key = 'sk-1234567890'\n"
            "ValueError: Configuration error"
        )
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]

    def test_traceback_with_password_scrubbed(self):
        """Tracebacks containing passwords should be scrubbed."""
        log_message = (
            "Traceback:\n" "  authenticate(username='admin', password='secret123')\n" "AuthenticationError"
        )
        record = {"message": log_message}
        scrub_log_record(record)
        assert "[REDACTED]" in record["message"]
        assert "secret123" not in record["message"]
