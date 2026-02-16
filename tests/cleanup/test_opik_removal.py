"""Tests for Opik code removal (STORY-001).

Verifies that all Opik-related code, configuration, Docker infrastructure,
documentation, and test files have been removed from the project.
"""

import subprocess
from pathlib import Path


def test_opik_instrumentation_file_deleted() -> None:
    """Verify opik_instrumentation.py is deleted."""
    opik_file = Path("src/app/agents/opik_instrumentation.py")
    assert not opik_file.exists(), "opik_instrumentation.py should be deleted"


def test_opik_config_class_removed() -> None:
    """Verify OpikConfig class is removed from load_configs.py."""
    # This test will fail initially because OpikConfig still exists
    from app.utils.load_configs import load_config  # noqa: F401

    # Try importing OpikConfig - should fail after removal
    try:
        from app.utils.load_configs import OpikConfig  # noqa: F401

        assert False, "OpikConfig class should be removed from load_configs.py"
    except ImportError:
        pass  # Expected after removal


def test_docker_compose_opik_deleted() -> None:
    """Verify docker-compose.opik.yaml is deleted."""
    docker_file = Path("docker-compose.opik.yaml")
    assert not docker_file.exists(), "docker-compose.opik.yaml should be deleted"


def test_makefile_opik_targets_removed() -> None:
    """Verify Makefile Opik targets are removed."""
    makefile = Path("Makefile")
    content = makefile.read_text()

    opik_targets = [
        "setup_opik",
        "setup_opik_env",
        "start_opik",
        "stop_opik",
        "clean_opik",
        "status_opik",
    ]

    for target in opik_targets:
        assert (
            target not in content
        ), f"Makefile should not contain {target} target"


def test_env_example_opik_vars_removed() -> None:
    """Verify .env.example has Opik variables removed."""
    env_file = Path(".env.example")
    content = env_file.read_text()

    opik_vars = ["OPIK_URL_OVERRIDE", "OPIK_WORKSPACE", "OPIK_PROJECT_NAME"]

    for var in opik_vars:
        assert var not in content, f".env.example should not contain {var}"


def test_gitignore_opik_entries_removed() -> None:
    """Verify .gitignore has Opik entries removed."""
    gitignore = Path(".gitignore")
    content = gitignore.read_text()

    assert "opik/" not in content, ".gitignore should not contain opik/ entry"
    assert (
        ".opik_install_reported" not in content
    ), ".gitignore should not contain .opik_install_reported entry"


def test_opik_howto_doc_deleted() -> None:
    """Verify Opik setup/usage documentation is deleted."""
    doc_file = Path("docs/howtos/opik-setup-usage-integration.md")
    assert not doc_file.exists(), "Opik howto documentation should be deleted"


def test_opik_integration_test_deleted() -> None:
    """Verify Opik integration test file is deleted."""
    test_file = Path("tests/integration/test_opik_integration.py")
    assert not test_file.exists(), "Opik integration test should be deleted"


def test_opik_metrics_test_deleted() -> None:
    """Verify Opik metrics test file is deleted."""
    test_file = Path("tests/evals/test_opik_metrics.py")
    assert not test_file.exists(), "Opik metrics test should be deleted"


def test_contributing_opik_references_removed() -> None:
    """Verify CONTRIBUTING.md has Opik references removed."""
    contributing = Path("CONTRIBUTING.md")
    content = contributing.read_text().lower()

    # Check for opik-related terms (case-insensitive)
    assert "opik" not in content, "CONTRIBUTING.md should not contain Opik references"


def test_no_opik_imports_in_src() -> None:
    """Verify no remaining Opik imports or references in src/app/."""
    # Use grep to search for opik references (case-insensitive)
    result = subprocess.run(
        ["grep", "-ri", "opik", "src/app/"],
        capture_output=True,
        text=True,
    )

    # grep returns 1 when no matches found (success for us)
    # grep returns 0 when matches found (failure for us)
    assert (
        result.returncode == 1
    ), f"Found Opik references in src/app/:\n{result.stdout}"


def test_logfire_config_intact() -> None:
    """Verify LogfireConfig remains intact (not accidentally removed)."""
    from app.utils.load_configs import LogfireConfig  # noqa: F401

    # Should import successfully
    assert LogfireConfig is not None, "LogfireConfig should still exist"
