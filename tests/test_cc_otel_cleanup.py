"""Test that cc_otel module has been completely removed.

This test ensures the orphaned cc_otel module (Sprint 6 STORY-006) has been
deleted and no references remain in the codebase.
"""

import subprocess
from pathlib import Path


def test_cc_otel_module_deleted() -> None:
    """Verify src/app/cc_otel/ directory has been deleted."""
    cc_otel_dir = Path("src/app/cc_otel")
    assert not cc_otel_dir.exists(), (
        f"cc_otel module still exists at {cc_otel_dir}. "
        "This orphaned module should have been deleted (STORY-006)."
    )


def test_cc_otel_tests_deleted() -> None:
    """Verify tests/cc_otel/ directory has been deleted."""
    cc_otel_tests_dir = Path("tests/cc_otel")
    assert not cc_otel_tests_dir.exists(), (
        f"cc_otel tests still exist at {cc_otel_tests_dir}. "
        "These tests should have been deleted along with the module (STORY-006)."
    )


def test_no_cc_otel_imports_in_src() -> None:
    """Verify no imports of cc_otel remain in src/app/."""
    # Use grep to search for any cc_otel references in source code
    result = subprocess.run(
        ["grep", "-r", "cc_otel", "src/app/", "--include=*.py"],
        capture_output=True,
        text=True,
    )

    # grep returns 1 when no matches found (success), 0 when matches found
    assert result.returncode == 1, (
        f"Found cc_otel references in src/app/:\n{result.stdout}\n"
        "All cc_otel imports should have been removed (STORY-006)."
    )


def test_no_cc_otel_imports_in_tests() -> None:
    """Verify no imports of cc_otel remain in tests/."""
    # Use grep to search for any cc_otel references in test code
    result = subprocess.run(
        ["grep", "-r", "cc_otel", "tests/", "--include=*.py"],
        capture_output=True,
        text=True,
    )

    # grep returns 1 when no matches found (success), 0 when matches found
    assert result.returncode == 1, (
        f"Found cc_otel references in tests/:\n{result.stdout}\n"
        "All cc_otel imports should have been removed (STORY-006)."
    )


def test_cc_otel_not_importable() -> None:
    """Verify cc_otel module cannot be imported."""
    try:
        import app.cc_otel  # type: ignore  # noqa: F401

        # If import succeeds, test fails
        raise AssertionError(
            "app.cc_otel module is still importable. "
            "This module should have been deleted (STORY-006)."
        )
    except ModuleNotFoundError:
        # Expected: module should not exist
        pass
