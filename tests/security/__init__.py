"""Security-focused test suite for Agents-eval.

This package contains comprehensive security tests validating:
- SSRF prevention (URL validation, domain allowlisting)
- Prompt injection protection (input sanitization, length limits)
- Sensitive data filtering (log scrubbing, trace redaction)
- Input size limits (DoS prevention for plugins)
- Tool registration security (authorization, scope validation)

These tests were created in response to Sprint 5 MAESTRO security review findings.
"""
