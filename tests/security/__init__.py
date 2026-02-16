"""Security test suite.

This package contains security-focused tests validating security controls
and testing attack vectors identified in the Sprint 5 MAESTRO security review.

Test modules:
- test_ssrf_prevention: SSRF attack vector testing
- test_prompt_injection: Prompt injection attack testing
- test_sensitive_data_filtering: Log/trace data scrubbing tests
- test_input_size_limits: DoS prevention via input size limits
- test_tool_registration: Tool registration authorization tests
"""
