"""Shared pytest configuration for all tests.

BDD Test Structure Template
============================
All tests in this project follow the Arrange/Act/Assert (BDD) pattern.

Test file header (docstring):
    - Purpose: What the module under test does
    - Setup/Mock strategy: Which dependencies are mocked and why
    - Expected behavior: Key invariants the tests verify

Test class structure:
    class TestSomething:
        \"""Tests for SomeComponent functionality.

        Setup: Brief description of fixtures/mocks used.
        Expected behavior: Key invariants verified by this class.
        \"""

        @pytest.fixture
        def subject(self):
            \"""Fixture providing SomeComponent instance.\"""
            return SomeComponent()

Test method structure:
    def test_does_something(self, subject):
        \"""Given <context>, when <action>, should <expected outcome>.

        Arrange: Setup description.
        Act: Action description.
        Assert: What is verified.
        \"""
        # Arrange
        ...
        # Act
        result = subject.do_something(...)
        # Assert
        assert result == expected_value

Mock strategy guidelines:
    - Mock external I/O (HTTP requests, file system writes, databases)
    - Use real objects for pure functions and data models
    - Use @patch("module.under.test.ClassName") for constructor-level mocking
    - Use tmp_path fixture for tests that write to disk
"""

import os
import sys
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

# Reason: weave bundles sentry_sdk and calls sentry_sdk.init() with a hardcoded
# DSN at import time, causing network requests to o151352.ingest.us.sentry.io.
# Neutralize sentry_sdk.init before any library can call it.
os.environ.setdefault("WEAVE_DISABLED", "true")
os.environ.setdefault("SENTRY_DSN", "")
import sentry_sdk  # noqa: E402

sentry_sdk.init(dsn="")

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def capture_registered_tools(register_fn: Callable, agent_id: str = "test") -> dict:
    """Register agent tools via a capture decorator and return them by name.

    Shared helper for tests that need to capture tools registered by
    add_peerread_tools_to_agent or add_peerread_review_tools_to_agent.

    Args:
        register_fn: The add_*_tools_to_agent function to call.
        agent_id: Agent ID passed to the registration function.

    Returns:
        dict: Mapping of tool function name to the captured function.
    """
    mock_agent = Mock()
    captured: list = []

    def capture_tool(func):
        captured.append(func)
        return func

    mock_agent.tool = capture_tool
    register_fn(mock_agent, agent_id=agent_id)
    return {fn.__name__: fn for fn in captured}
