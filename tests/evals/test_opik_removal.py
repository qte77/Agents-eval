"""Tests to verify complete removal of Opik tracing infrastructure.

This module ensures that:
1. OpikConfig references are removed from evaluation_pipeline.py
2. @track decorators are removed
3. opik_instrumentation.py is deleted
4. No Opik imports remain in the codebase (except deprecated OpikConfig for backward compatibility)
"""

import ast
from pathlib import Path


def test_evaluation_pipeline_has_no_opik_imports():
    """Test that evaluation_pipeline.py has no Opik imports."""
    pipeline_path = Path("src/app/evals/evaluation_pipeline.py")
    assert pipeline_path.exists(), "evaluation_pipeline.py should exist"

    content = pipeline_path.read_text()

    # Check for Opik imports
    assert "from opik import" not in content, "Should not import from opik"
    assert "import opik" not in content, "Should not import opik"
    assert "from app.utils.load_configs import OpikConfig" not in content, (
        "Should not import OpikConfig"
    )


def test_evaluation_pipeline_has_no_opik_decorator():
    """Test that evaluation_pipeline.py has no @track decorators."""
    pipeline_path = Path("src/app/evals/evaluation_pipeline.py")
    content = pipeline_path.read_text()

    # Parse AST to check for @track decorator usage
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    assert decorator.id != "track", (
                        f"Function {node.name} should not use @track decorator"
                    )
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    assert decorator.func.id != "track", (
                        f"Function {node.name} should not use @track() decorator"
                    )


def test_evaluation_pipeline_has_no_opik_config_usage():
    """Test that evaluation_pipeline.py has no OpikConfig references."""
    pipeline_path = Path("src/app/evals/evaluation_pipeline.py")
    content = pipeline_path.read_text()

    # Check for OpikConfig usage
    assert "OpikConfig" not in content, "Should not reference OpikConfig"
    assert "opik_config" not in content, "Should not have opik_config variable"
    assert "_apply_opik_decorator" not in content, "Should not have _apply_opik_decorator method"
    assert "_record_opik_metadata" not in content, "Should not have _record_opik_metadata method"


def test_opik_instrumentation_file_deleted():
    """Test that opik_instrumentation.py is deleted."""
    opik_file = Path("src/app/agents/opik_instrumentation.py")
    assert not opik_file.exists(), "opik_instrumentation.py should be deleted"


def test_opik_available_variable_removed():
    """Test that OPIK_AVAILABLE variable is removed from evaluation_pipeline.py."""
    pipeline_path = Path("src/app/evals/evaluation_pipeline.py")
    content = pipeline_path.read_text()

    assert "OPIK_AVAILABLE" not in content, "Should not have OPIK_AVAILABLE variable"


def test_track_fallback_decorator_removed():
    """Test that track fallback decorator is removed from evaluation_pipeline.py."""
    pipeline_path = Path("src/app/evals/evaluation_pipeline.py")
    content = pipeline_path.read_text()

    # Check for track fallback implementation
    assert "def track(**kwargs" not in content, "Should not have track fallback decorator"
