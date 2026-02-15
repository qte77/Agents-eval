"""
Tests for migration cleanup (STORY-008).

Verifies that:
- All imports use new judge.* paths
- No deprecated files remain
- FIXME comments are resolved
"""

import ast
from pathlib import Path


def test_no_evals_imports_in_source():
    """All source files should use app.judge.* imports, not app.evals.*."""
    src_dir = Path("src")
    evals_imports = []

    for py_file in src_dir.rglob("*.py"):
        if py_file.is_file():
            content = py_file.read_text()
            try:
                tree = ast.parse(content, filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("app.judge."):
                            evals_imports.append(f"{py_file}:{node.lineno} - {node.module}")
            except SyntaxError:
                # Skip unparseable files
                pass

    assert not evals_imports, (
        f"Found {len(evals_imports)} imports from app.judge.* that should use app.judge.*:\n"
        + "\n".join(evals_imports[:10])
    )


def test_no_evals_imports_in_tests():
    """All test files should use app.judge.* imports, not app.evals.*."""
    tests_dir = Path("tests")
    evals_imports = []

    for py_file in tests_dir.rglob("*.py"):
        if py_file.is_file():
            content = py_file.read_text()
            try:
                tree = ast.parse(content, filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("app.judge."):
                            evals_imports.append(f"{py_file}:{node.lineno} - {node.module}")
            except SyntaxError:
                # Skip unparseable files
                pass

    assert not evals_imports, (
        f"Found {len(evals_imports)} imports from app.judge.* that should use app.judge.*:\n"
        + "\n".join(evals_imports[:10])
    )


def test_no_duplicate_peerread_tools():
    """Duplicate peerread_tools.py should be removed."""
    duplicate = Path("src/app/agents/peerread_tools.py")
    canonical = Path("src/app/tools/peerread_tools.py")

    assert canonical.exists(), "Canonical peerread_tools.py should exist at src/app/tools/"
    assert not duplicate.exists(), (
        "Duplicate peerread_tools.py at src/app/agents/ should be removed. "
        "Canonical location is src/app/tools/peerread_tools.py"
    )


def test_no_deprecated_config_json():
    """Deprecated config/config_eval.json should be removed."""
    deprecated_config = Path("config/config_eval.json")
    assert not deprecated_config.exists(), (
        "Deprecated config/config_eval.json should be removed. "
        "Configuration is now managed via pydantic-settings."
    )


def test_no_evals_module():
    """Old app.evals module should be completely removed."""
    evals_dir = Path("src/app/evals")
    assert not evals_dir.exists(), (
        "Old app.evals/ directory should be removed. "
        "All evaluation code has been migrated to app.judge/"
    )


def test_error_handling_context_fixmes_resolved():
    """FIXME comments for error_handling_context should be resolved."""
    agent_system = Path("src/app/agents/agent_system.py")
    content = agent_system.read_text()

    # Lines 443, 514, 583 should not have FIXME comments about error_handling_context
    fixme_lines = []
    for i, line in enumerate(content.splitlines(), 1):
        if "FIXME" in line and "error_handling_context" in line.lower():
            fixme_lines.append(f"Line {i}: {line.strip()}")

    assert not fixme_lines, (
        f"Found {len(fixme_lines)} unresolved FIXME comments for error_handling_context:\n"
        + "\n".join(fixme_lines)
    )
