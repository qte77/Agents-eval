"""Tests verifying all 8 example modules import without error.

Purpose: Smoke-test that every example in src/examples/ can be imported and
         has the expected module-level attributes (docstring, run_example or
         main function). No actual execution is performed.
Setup: No mocks needed — import-only.
Expected behavior: All 8 modules import cleanly; each exposes a callable
                   named run_example or a __main__ block.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Absolute path to the examples directory
_EXAMPLES_DIR = Path(__file__).parent.parent.parent / "src" / "examples"

# All 8 example modules that must be importable
_EXAMPLE_MODULES = [
    "basic_evaluation",
    "judge_settings_customization",
    "engine_comparison",
    "mas_single_agent",
    "mas_multi_agent",
    "cc_solo",
    "cc_teams",
    "sweep_benchmark",
]


def _import_example(module_name: str):
    """Import an example module by name from the examples directory.

    Args:
        module_name: Stem of the Python file (without .py).

    Returns:
        The imported module object.

    Raises:
        FileNotFoundError: If the example file does not exist.
        ImportError: If the module cannot be imported.
    """
    file_path = _EXAMPLES_DIR / f"{module_name}.py"
    if not file_path.exists():
        raise FileNotFoundError(f"Example not found: {file_path}")

    # Use a unique key to avoid collisions with previously imported modules
    unique_key = f"_example_importable_{module_name}"
    spec = importlib.util.spec_from_file_location(unique_key, file_path)
    assert spec is not None, f"Cannot create spec for {file_path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_key] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


class TestAllExampleModulesImportable:
    """Verify all 8 example modules can be imported without errors."""

    @pytest.mark.parametrize("module_name", _EXAMPLE_MODULES)
    def test_module_imports_without_error(self, module_name: str) -> None:
        """Each example imports cleanly with no ImportError or syntax error.

        Args:
            module_name: Name of the example module to test.
        """
        # Act: import the module (should not raise)
        module = _import_example(module_name)

        # Assert: module object was returned
        assert module is not None, f"Module {module_name} returned None after import"

    @pytest.mark.parametrize("module_name", _EXAMPLE_MODULES)
    def test_module_has_docstring(self, module_name: str) -> None:
        """Each example has a module-level docstring.

        Args:
            module_name: Name of the example module to test.
        """
        module = _import_example(module_name)

        # Assert: module docstring exists and is non-empty
        assert module.__doc__ is not None, f"{module_name} is missing a module docstring"
        assert len(module.__doc__.strip()) > 0, f"{module_name} has an empty module docstring"

    @pytest.mark.parametrize("module_name", _EXAMPLE_MODULES)
    def test_module_has_docstring_sections(self, module_name: str) -> None:
        """Each new example docstring contains required sections: Purpose, Prerequisites,
        Expected output, Usage.

        The three original examples (basic_evaluation, judge_settings_customization,
        engine_comparison) already follow a compatible structure and are excluded from
        the strict section check.

        Args:
            module_name: Name of the example module to test.
        """
        # Original three examples are exempt from strict section check
        original_examples = {"basic_evaluation", "judge_settings_customization", "engine_comparison"}
        if module_name in original_examples:
            pytest.skip(f"{module_name} is a legacy example — section check skipped")

        module = _import_example(module_name)
        docstring = module.__doc__ or ""

        required_sections = ["Purpose", "Prerequisites", "Expected output", "Usage"]
        for section in required_sections:
            assert section in docstring, (
                f"{module_name} docstring is missing '{section}' section"
            )

    @pytest.mark.parametrize("module_name", _EXAMPLE_MODULES)
    def test_module_has_run_example_or_main(self, module_name: str) -> None:
        """Each example exposes a callable named run_example or main, or has a __main__ block.

        Args:
            module_name: Name of the example module to test.
        """
        module = _import_example(module_name)

        has_run_example = callable(getattr(module, "run_example", None))
        has_main = callable(getattr(module, "main", None))

        # Also accept examples that only use a __main__ block (e.g. judge_settings_customization)
        file_path = _EXAMPLES_DIR / f"{module_name}.py"
        source = file_path.read_text()
        has_main_block = '__name__ == "__main__"' in source or "__name__ == '__main__'" in source

        assert has_run_example or has_main or has_main_block, (
            f"{module_name} must define 'run_example()', 'main()', or a __main__ block"
        )


class TestNewExampleFiles:
    """Additional structural checks for the 5 new example files."""

    @pytest.mark.parametrize(
        "module_name",
        ["mas_single_agent", "mas_multi_agent", "cc_solo", "cc_teams", "sweep_benchmark"],
    )
    def test_example_file_exists(self, module_name: str) -> None:
        """The example Python file exists on disk.

        Args:
            module_name: Example file stem to check.
        """
        file_path = _EXAMPLES_DIR / f"{module_name}.py"
        assert file_path.exists(), f"Missing example file: {file_path}"

    def test_cc_examples_have_availability_check(self) -> None:
        """CC examples (cc_solo, cc_teams) include a check_cc_available guard."""
        for module_name in ("cc_solo", "cc_teams"):
            file_path = _EXAMPLES_DIR / f"{module_name}.py"
            source = file_path.read_text()
            assert "check_cc_available" in source, (
                f"{module_name}.py must call check_cc_available() for CC guard"
            )

    def test_cc_examples_use_build_cc_query(self) -> None:
        """CC examples (cc_solo, cc_teams) use build_cc_query() for query construction."""
        for module_name in ("cc_solo", "cc_teams"):
            file_path = _EXAMPLES_DIR / f"{module_name}.py"
            source = file_path.read_text()
            assert "build_cc_query" in source, (
                f"{module_name}.py must use build_cc_query() for CC query construction"
            )

    def test_sweep_example_uses_tempdir(self) -> None:
        """Sweep example uses a temporary directory for output_dir."""
        file_path = _EXAMPLES_DIR / "sweep_benchmark.py"
        source = file_path.read_text()
        # Should use tempfile or tmp_path
        assert "tempfile" in source or "mkdtemp" in source or "TemporaryDirectory" in source, (
            "sweep_benchmark.py must use a temp directory for output_dir"
        )

    def test_readme_documents_all_8_examples(self) -> None:
        """src/examples/README.md references all 8 example module names."""
        readme_path = _EXAMPLES_DIR / "README.md"
        assert readme_path.exists(), "src/examples/README.md is missing"
        readme_content = readme_path.read_text()

        expected_names = [
            "basic_evaluation",
            "judge_settings_customization",
            "engine_comparison",
            "mas_single_agent",
            "mas_multi_agent",
            "cc_solo",
            "cc_teams",
            "sweep_benchmark",
        ]
        for name in expected_names:
            assert name in readme_content, (
                f"README.md is missing documentation for '{name}'"
            )
