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

import sys
from pathlib import Path

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
