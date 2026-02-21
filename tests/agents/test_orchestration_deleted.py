"""Tests verifying orchestration.py dead code has been removed (STORY-001).

Confirms the module is deleted and no imports reference it across
the codebase, per Review F5 and YAGNI principle.
"""

import importlib
import pathlib

import pytest


# Root directories for scanning
SRC_ROOT = pathlib.Path(__file__).resolve().parents[2] / "src"
TESTS_ROOT = pathlib.Path(__file__).resolve().parents[2] / "tests"


class TestOrchestrationModuleDeleted:
    """Verify orchestration.py dead code module is fully removed."""

    def test_orchestration_file_does_not_exist(self):
        """AC1: src/app/agents/orchestration.py must be deleted."""
        orchestration_path = SRC_ROOT / "app" / "agents" / "orchestration.py"
        assert not orchestration_path.exists(), (
            f"Dead code module still exists: {orchestration_path}"
        )

    def test_orchestration_module_not_importable(self):
        """AC2: The module must not be importable."""
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("app.agents.orchestration")

    def test_no_orchestration_imports_in_src(self):
        """AC2: No imports of orchestration remain in src/."""
        violations = []
        for py_file in SRC_ROOT.rglob("*.py"):
            content = py_file.read_text()
            for i, line in enumerate(content.splitlines(), 1):
                if "orchestration" in line.lower() and "import" in line.lower():
                    # Skip comments
                    stripped = line.strip()
                    if not stripped.startswith("#"):
                        violations.append(f"{py_file}:{i}: {stripped}")
        assert not violations, (
            f"Found orchestration imports in src/:\n" + "\n".join(violations)
        )

    def test_no_orchestration_imports_in_tests(self):
        """AC2: No imports of orchestration remain in tests/.

        Excludes this test file itself since we reference the module name
        in strings and comments.
        """
        this_file = pathlib.Path(__file__).resolve()
        violations = []
        for py_file in TESTS_ROOT.rglob("*.py"):
            if py_file.resolve() == this_file:
                continue
            content = py_file.read_text()
            for i, line in enumerate(content.splitlines(), 1):
                if "from app.agents.orchestration" in line or "import orchestration" in line:
                    stripped = line.strip()
                    if not stripped.startswith("#"):
                        violations.append(f"{py_file}:{i}: {stripped}")
        assert not violations, (
            f"Found orchestration imports in tests/:\n" + "\n".join(violations)
        )
