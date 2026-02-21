"""
STORY-009 verification tests — test suite quality sweep.

These tests verify that the quality improvements listed in STORY-009 are in
place. They act as regression guards so the same issues cannot silently reappear.

RED phase: All assertions should initially describe the desired end-state and
will fail against the unmodified test suite. Once GREEN fixes are applied, they
pass.
"""

from __future__ import annotations

import ast
import threading
from pathlib import Path

import pytest

TESTS_ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(path: Path) -> ast.Module:
    """Return the AST for a test file."""
    return ast.parse(path.read_text())


def _collect_mock_calls(tree: ast.Module) -> list[ast.Call]:
    """Return every ast.Call node whose function is MagicMock or Mock."""
    calls: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # Handles: MagicMock(...) and Mock(...)
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name in ("MagicMock", "Mock"):
            calls.append(node)
    return calls


def _mock_has_spec(call: ast.Call) -> bool:
    """Return True when call has a keyword argument named 'spec'."""
    return any(kw.arg == "spec" for kw in call.keywords)


def _has_sys_path_insert(path: Path) -> bool:
    """Return True when the file contains sys.path.insert(...)."""
    tree = _parse(path)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "insert"
            and isinstance(func.value, ast.Attribute)
            and func.value.attr == "path"
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == "sys"
        ):
            return True
    return False


def _collect_class_names(tree: ast.Module) -> set[str]:
    """Return set of top-level class names defined in the module."""
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def _class_has_only_pass(tree: ast.Module, class_name: str) -> bool:
    """Return True when class_name exists and its body is only a docstring / pass."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        # Filter out docstrings (Expr with Constant value)
        non_trivial = [
            stmt
            for stmt in node.body
            if not (
                isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
            )
            and not isinstance(stmt, ast.Pass)
        ]
        return len(non_trivial) == 0
    return False  # class not found → not a pass-only class


def _async_test_names(tree: ast.Module) -> list[str]:
    """Return names of all async test functions at module or class level."""
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name.startswith("test"):
            names.append(node.name)
    return names


def _has_asyncio_marker(tree: ast.Module, func_name: str) -> bool:
    """Return True when func_name has @pytest.mark.asyncio decorator."""
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
            and node.name == func_name
        ):
            for deco in node.decorator_list:
                # pytest.mark.asyncio
                if (
                    isinstance(deco, ast.Attribute)
                    and deco.attr == "asyncio"
                    and isinstance(deco.value, ast.Attribute)
                    and deco.value.attr == "mark"
                ):
                    return True
    return False


# ---------------------------------------------------------------------------
# AC1 — spec= on MagicMock / Mock in listed test files
# ---------------------------------------------------------------------------

_AC1_FILES = [
    TESTS_ROOT / "agents" / "test_rate_limit_handling.py",
    TESTS_ROOT / "agents" / "test_trace_collection_integration.py",
    TESTS_ROOT / "judge" / "test_evaluation_runner.py",
    TESTS_ROOT / "judge" / "test_llm_evaluation_managers.py",
    TESTS_ROOT / "judge" / "test_graph_analysis.py",
    TESTS_ROOT / "evals" / "test_evaluation_pipeline.py",
    TESTS_ROOT / "app" / "test_cli_baseline.py",
    TESTS_ROOT / "app" / "test_app.py",
    TESTS_ROOT / "gui" / "test_story013_ux_fixes.py",
    TESTS_ROOT / "gui" / "test_story007_gui_polish.py",
    TESTS_ROOT / "benchmark" / "test_sweep_runner.py",
]

# Exceptions: call sites where spec= is intentionally omitted (mock the mock itself)
# Each entry is (filename_stem, approximate_lineno_tolerance) — kept minimal.
_AC1_KNOWN_SPECLESS_OK: set[str] = set()


@pytest.mark.parametrize("test_file", _AC1_FILES, ids=lambda p: p.name)
def test_ac1_mock_calls_use_spec(test_file: Path) -> None:
    """AC1: Every MagicMock()/Mock() in listed files should have spec=ClassName."""
    if not test_file.exists():
        pytest.skip(f"{test_file} does not exist yet")

    tree = _parse(test_file)
    calls = _collect_mock_calls(tree)

    offenders = [c for c in calls if not _mock_has_spec(c)]

    assert offenders == [], (
        f"{test_file.name}: found {len(offenders)} MagicMock/Mock call(s) without spec=. "
        f"Add spec=ClassName to each (lines: "
        f"{[getattr(c, 'lineno', '?') for c in offenders]})"
    )


# ---------------------------------------------------------------------------
# AC2 — @pytest.mark.asyncio on async tests in test_judge_agent.py
# ---------------------------------------------------------------------------

_JUDGE_AGENT_FILE = TESTS_ROOT / "judge" / "test_judge_agent.py"


def test_ac2_async_tests_have_asyncio_marker() -> None:
    """AC2: All async test functions in test_judge_agent.py have @pytest.mark.asyncio."""
    if not _JUDGE_AGENT_FILE.exists():
        pytest.skip("test_judge_agent.py does not exist")

    tree = _parse(_JUDGE_AGENT_FILE)
    async_tests = _async_test_names(tree)

    missing = [t for t in async_tests if not _has_asyncio_marker(tree, t)]

    assert missing == [], (
        f"test_judge_agent.py: async test(s) missing @pytest.mark.asyncio: {missing}"
    )


# ---------------------------------------------------------------------------
# AC3 — thread-safety test uses Lock around counter increments
# ---------------------------------------------------------------------------

_TRACE_STORE_FILE = TESTS_ROOT / "judge" / "test_trace_store.py"


def test_ac3_thread_safety_test_uses_lock() -> None:
    """AC3: test_trace_store_is_thread_safe_for_mixed_operations uses threading.Lock."""
    if not _TRACE_STORE_FILE.exists():
        pytest.skip("test_trace_store.py does not exist")

    source = _TRACE_STORE_FILE.read_text()
    # The mixed-operations test must use a Lock to protect counter increments
    assert "threading.Lock" in source or "Lock()" in source, (
        "test_trace_store.py: test_trace_store_is_thread_safe_for_mixed_operations "
        "must use threading.Lock to protect counter increments"
    )


def test_ac3_thread_safety_asserts_counter_values() -> None:
    """AC3: mixed-operations test must assert final counter values (write_count, read_count)."""
    if not _TRACE_STORE_FILE.exists():
        pytest.skip("test_trace_store.py does not exist")

    source = _TRACE_STORE_FILE.read_text()
    # Must assert concrete counter values, not just the store length
    assert "write_count" in source and "read_count" in source, (
        "test_trace_store.py: mixed-operations test must assert write_count and read_count"
    )
    # Check that assertions exist on these counters
    assert "assert write_count" in source or "assert write_count[0]" in source, (
        "test_trace_store.py: must assert write_count final value"
    )
    assert "assert read_count" in source or "assert read_count[0]" in source, (
        "test_trace_store.py: must assert read_count final value"
    )


# ---------------------------------------------------------------------------
# AC4 — shared fixture extracted in test_metric_comparison_logging.py
# ---------------------------------------------------------------------------

_METRIC_COMPARISON_FILE = TESTS_ROOT / "evals" / "test_metric_comparison_logging.py"


def test_ac4_shared_fixture_extracted() -> None:
    """AC4: test_metric_comparison_logging.py should have a shared fixture for pipeline setup."""
    if not _METRIC_COMPARISON_FILE.exists():
        pytest.skip("test_metric_comparison_logging.py does not exist")

    tree = _parse(_METRIC_COMPARISON_FILE)

    # Should have at least one @pytest.fixture
    fixtures = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and any(
            (isinstance(d, ast.Attribute) and d.attr == "fixture")
            or (isinstance(d, ast.Name) and d.id == "fixture")
            for d in node.decorator_list
        )
    ]

    assert len(fixtures) >= 1, (
        "test_metric_comparison_logging.py: no @pytest.fixture found. "
        "Extract shared pipeline setup into a fixture."
    )


# ---------------------------------------------------------------------------
# AC5 — test_agent_factories_coverage.py merged and deleted
# ---------------------------------------------------------------------------

_FACTORIES_COVERAGE_FILE = TESTS_ROOT / "agents" / "test_agent_factories_coverage.py"
_FACTORIES_FILE = TESTS_ROOT / "agents" / "test_agent_factories.py"


def test_ac5_coverage_file_deleted() -> None:
    """AC5: test_agent_factories_coverage.py must be deleted after merge."""
    assert not _FACTORIES_COVERAGE_FILE.exists(), (
        "test_agent_factories_coverage.py still exists — merge its tests into "
        "test_agent_factories.py and delete the coverage file"
    )


def test_ac5_main_file_still_exists() -> None:
    """AC5: test_agent_factories.py must still exist after merge."""
    assert _FACTORIES_FILE.exists(), (
        "test_agent_factories.py was unexpectedly deleted"
    )


# ---------------------------------------------------------------------------
# AC6 — empty TestCompositeScorer class deleted
# ---------------------------------------------------------------------------

_COMPOSITE_SCORER_FILE = TESTS_ROOT / "evals" / "test_composite_scorer.py"


def test_ac6_empty_test_composite_scorer_class_deleted() -> None:
    """AC6: Empty TestCompositeScorer class must be removed from test_composite_scorer.py."""
    if not _COMPOSITE_SCORER_FILE.exists():
        pytest.skip("test_composite_scorer.py does not exist")

    tree = _parse(_COMPOSITE_SCORER_FILE)

    # The class must not exist OR must have at least one non-pass body statement
    if "TestCompositeScorer" in _collect_class_names(tree):
        assert not _class_has_only_pass(tree, "TestCompositeScorer"), (
            "test_composite_scorer.py: empty TestCompositeScorer class (with no test "
            "methods) must be deleted"
        )


# ---------------------------------------------------------------------------
# AC7 — sys.path.insert removed from integration/benchmark files
# ---------------------------------------------------------------------------

_AC7_FILES = [
    TESTS_ROOT / "integration" / "test_peerread_integration.py",
    TESTS_ROOT / "integration" / "test_enhanced_peerread_integration.py",
    TESTS_ROOT / "integration" / "test_peerread_real_dataset_validation.py",
    TESTS_ROOT / "benchmarks" / "test_performance_baselines.py",
]


@pytest.mark.parametrize("test_file", _AC7_FILES, ids=lambda p: p.name)
def test_ac7_no_sys_path_insert(test_file: Path) -> None:
    """AC7: Integration/benchmark test files must not use sys.path.insert."""
    if not test_file.exists():
        pytest.skip(f"{test_file} does not exist")

    assert not _has_sys_path_insert(test_file), (
        f"{test_file.name}: contains sys.path.insert() — remove it. "
        "The project should be installed via pyproject.toml / uv sync."
    )


# ---------------------------------------------------------------------------
# AC8 — stub test with `pass` body deleted from test_peerread_tools.py
# ---------------------------------------------------------------------------

_PEERREAD_TOOLS_FILE = TESTS_ROOT / "agents" / "test_peerread_tools.py"


def test_ac8_stub_test_deleted() -> None:
    """AC8: test_generate_review_template_with_truncation stub (pass body) must be deleted."""
    if not _PEERREAD_TOOLS_FILE.exists():
        pytest.skip("test_peerread_tools.py does not exist")

    source = _PEERREAD_TOOLS_FILE.read_text()
    # The stub method is in class TestContentTruncation
    # It has a `pass` body with no real assertion
    # We verify the stub is gone by checking for the specific pass-only implementation
    # in the ContentTruncation class context
    tree = _parse(_PEERREAD_TOOLS_FILE)

    stub_found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != "TestContentTruncation":
            continue
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name != "test_generate_review_template_with_truncation":
                continue
            # Check if body is trivially pass (only docstrings/Expr(Constant) + pass)
            non_trivial = [
                s
                for s in item.body
                if not (
                    isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                )
                and not isinstance(s, ast.Pass)
            ]
            if len(non_trivial) == 0:
                stub_found = True

    assert not stub_found, (
        "test_peerread_tools.py: stub test "
        "TestContentTruncation.test_generate_review_template_with_truncation "
        "with `pass` body must be deleted (AC8)"
    )


# ---------------------------------------------------------------------------
# AC9 — test_datasets_peerread_coverage.py merged and deleted
# ---------------------------------------------------------------------------

_PEERREAD_COVERAGE_FILE = TESTS_ROOT / "data_utils" / "test_datasets_peerread_coverage.py"
_PEERREAD_MAIN_FILE = TESTS_ROOT / "data_utils" / "test_datasets_peerread.py"


def test_ac9_coverage_file_deleted() -> None:
    """AC9: test_datasets_peerread_coverage.py must be deleted after merge."""
    assert not _PEERREAD_COVERAGE_FILE.exists(), (
        "test_datasets_peerread_coverage.py still exists — merge its tests into "
        "test_datasets_peerread.py and delete the coverage file"
    )


def test_ac9_main_file_still_exists() -> None:
    """AC9: test_datasets_peerread.py must still exist after merge."""
    assert _PEERREAD_MAIN_FILE.exists(), (
        "test_datasets_peerread.py was unexpectedly deleted"
    )
