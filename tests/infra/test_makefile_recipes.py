"""
Tests for Makefile recipes validation (STORY-002).

Validates that Phoenix Docker recipe contains required volume mounts,
port mappings, restart policy, and force-remove flags.
"""

import re
from pathlib import Path


def test_phoenix_recipe_has_volume_mount():
    """Test that start_phoenix recipe includes volume mount for data persistence."""
    makefile_path = Path(__file__).parent.parent.parent / "Makefile"
    content = makefile_path.read_text()

    # Find start_phoenix target
    phoenix_section = _extract_phoenix_recipe(content)

    # Should contain -v flag with phoenix_data volume
    assert "-v" in phoenix_section, "Phoenix recipe missing volume mount flag"
    assert "phoenix_data" in phoenix_section, "Phoenix recipe missing phoenix_data volume"


def test_phoenix_recipe_has_grpc_port():
    """Test that start_phoenix recipe exposes gRPC port 4317."""
    makefile_path = Path(__file__).parent.parent.parent / "Makefile"
    content = makefile_path.read_text()

    phoenix_section = _extract_phoenix_recipe(content)

    # Should expose port 4317 for gRPC
    assert "4317" in phoenix_section, "Phoenix recipe missing gRPC port 4317"
    assert phoenix_section.count("-p") >= 2, "Phoenix recipe should have at least 2 port mappings"


def test_phoenix_recipe_has_restart_policy():
    """Test that start_phoenix recipe includes restart policy."""
    makefile_path = Path(__file__).parent.parent.parent / "Makefile"
    content = makefile_path.read_text()

    phoenix_section = _extract_phoenix_recipe(content)

    # Should have --restart unless-stopped
    assert "--restart" in phoenix_section, "Phoenix recipe missing restart policy"
    assert "unless-stopped" in phoenix_section, "Phoenix recipe should use 'unless-stopped' policy"


def test_phoenix_recipe_has_force_remove():
    """Test that start_phoenix recipe removes existing container first."""
    makefile_path = Path(__file__).parent.parent.parent / "Makefile"
    content = makefile_path.read_text()

    phoenix_section = _extract_phoenix_recipe(content)

    # Should remove existing container before starting
    # Either 'docker rm -f' or 'docker rm' followed by docker run
    assert "docker rm" in phoenix_section or "rm -f" in phoenix_section, (
        "Phoenix recipe should remove existing container"
    )


def _extract_phoenix_recipe(makefile_content: str) -> str:
    """Extract the start_phoenix recipe section from Makefile."""
    # Find start_phoenix target and grab lines until next target
    lines = makefile_content.split("\n")
    phoenix_lines = []
    in_phoenix = False

    for line in lines:
        if "start_phoenix:" in line:
            in_phoenix = True
            phoenix_lines.append(line)
        elif in_phoenix:
            # Stop at next target (line starting with word followed by colon)
            if re.match(r"^[a-z_]+:", line):
                break
            phoenix_lines.append(line)

    return "\n".join(phoenix_lines)
