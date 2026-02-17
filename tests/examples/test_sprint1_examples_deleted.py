"""Tests verifying Sprint 1-era examples and generic PydanticAI tutorials are deleted.

Purpose: Confirm that outdated example files using deprecated APIs have been removed.
Setup: No external dependencies required — purely filesystem checks.
Expected behavior: All listed files and directories must not exist.
Mock strategy: None needed — filesystem assertions only.
"""

from pathlib import Path

# Root of src/examples/ directory
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "src" / "examples"


class TestDeprecatedEvaluationExamplesDeleted:
    """Verify Sprint 1-era evaluation examples using deprecated dict-based API are removed."""

    def test_run_evaluation_example_deleted(self) -> None:
        """run_evaluation_example.py uses deprecated dict-based execution_trace API."""
        # Arrange
        target = EXAMPLES_DIR / "run_evaluation_example.py"
        # Act / Assert
        assert not target.exists(), (
            f"Deprecated file must be deleted: {target}"
        )

    def test_run_evaluation_example_simple_deleted(self) -> None:
        """run_evaluation_example_simple.py uses deprecated dict-based execution_trace API."""
        # Arrange
        target = EXAMPLES_DIR / "run_evaluation_example_simple.py"
        # Act / Assert
        assert not target.exists(), (
            f"Deprecated file must be deleted: {target}"
        )


class TestGenericAgentExamplesDeleted:
    """Verify generic PydanticAI tutorial files with no project value are removed."""

    def test_run_simple_agent_no_tools_deleted(self) -> None:
        """run_simple_agent_no_tools.py is a generic PydanticAI tutorial."""
        # Arrange
        target = EXAMPLES_DIR / "run_simple_agent_no_tools.py"
        # Act / Assert
        assert not target.exists(), (
            f"Generic tutorial must be deleted: {target}"
        )

    def test_run_simple_agent_system_deleted(self) -> None:
        """run_simple_agent_system.py is a generic PydanticAI tutorial."""
        # Arrange
        target = EXAMPLES_DIR / "run_simple_agent_system.py"
        # Act / Assert
        assert not target.exists(), (
            f"Generic tutorial must be deleted: {target}"
        )

    def test_run_simple_agent_tools_deleted(self) -> None:
        """run_simple_agent_tools.py is a generic PydanticAI tutorial."""
        # Arrange
        target = EXAMPLES_DIR / "run_simple_agent_tools.py"
        # Act / Assert
        assert not target.exists(), (
            f"Generic tutorial must be deleted: {target}"
        )


class TestSupportingFilesDeleted:
    """Verify supporting files and directories for deleted examples are removed."""

    def test_utils_directory_deleted(self) -> None:
        """src/examples/utils/ contains support modules for deleted examples."""
        # Arrange
        target = EXAMPLES_DIR / "utils"
        # Act / Assert
        assert not target.exists(), (
            f"Utils directory must be deleted: {target}"
        )

    def test_config_json_deleted(self) -> None:
        """config.json is a supporting configuration file for deleted examples."""
        # Arrange
        target = EXAMPLES_DIR / "config.json"
        # Act / Assert
        assert not target.exists(), (
            f"Config file must be deleted: {target}"
        )


class TestNoRemainingImports:
    """Verify no remaining imports reference deleted example modules."""

    def test_no_imports_from_examples_in_src(self) -> None:
        """No src/ file should import from examples modules."""
        # Arrange
        src_dir = Path(__file__).parent.parent.parent / "src"
        deleted_modules = [
            "run_evaluation_example",
            "run_evaluation_example_simple",
            "run_simple_agent_no_tools",
            "run_simple_agent_system",
            "run_simple_agent_tools",
        ]
        violations: list[str] = []

        # Act
        for py_file in src_dir.rglob("*.py"):
            # Skip the examples directory itself (already being deleted)
            if "examples" in py_file.parts:
                continue
            content = py_file.read_text()
            for module in deleted_modules:
                if f"from examples.{module}" in content or f"import {module}" in content:
                    violations.append(f"{py_file}: references {module}")

        # Assert
        assert not violations, (
            "Found imports of deleted example modules:\n" + "\n".join(violations)
        )
