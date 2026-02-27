"""Artifact registry for tracking output paths during CLI runs.

Provides a thread-safe singleton registry where components register
file paths they write during execution. At run end, the registry
produces a summary block listing all artifacts and their locations.

Example:
    >>> from app.utils.artifact_registry import get_artifact_registry
    >>> registry = get_artifact_registry()
    >>> registry.register("Log file", Path("logs/run.log"))
    >>> print(registry.format_summary_block())
"""

import threading
from pathlib import Path


class ArtifactRegistry:
    """Thread-safe registry for tracking artifact output paths.

    Components call ``register()`` during execution to record what
    files they wrote. At run end, ``format_summary_block()`` produces
    a human-readable summary for stdout and logging.
    """

    def __init__(self) -> None:
        """Initialize empty registry with thread lock."""
        self._entries: list[tuple[str, Path]] = []
        self._lock = threading.Lock()

    def register(self, label: str, path: Path) -> None:
        """Register an artifact path with a descriptive label.

        Args:
            label: Human-readable category (e.g., "Log file", "Report").
            path: Path to the artifact file or directory.
        """
        abs_path = path if path.is_absolute() else path.resolve()
        with self._lock:
            self._entries.append((label, abs_path))

    def summary(self) -> list[tuple[str, Path]]:
        """Return all registered artifacts as (label, absolute_path) tuples.

        Returns:
            List of (label, path) tuples in registration order.
        """
        with self._lock:
            return list(self._entries)

    def reset(self) -> None:
        """Clear all registered artifacts."""
        with self._lock:
            self._entries.clear()

    def format_summary_block(self) -> str:
        """Format a human-readable summary block for stdout.

        Returns:
            Multi-line string with artifact listing, or a
            "No artifacts written" message if the registry is empty.
        """
        entries = self.summary()
        if not entries:
            return "No artifacts written"

        lines = ["", "Artifacts written:"]
        for label, path in entries:
            lines.append(f"  {label}: {path}")
        return "\n".join(lines)


# Global singleton instance
_global_registry: ArtifactRegistry | None = None
_registry_lock = threading.Lock()


def get_artifact_registry() -> ArtifactRegistry:
    """Get or create the global ArtifactRegistry singleton.

    Returns:
        The global ArtifactRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = ArtifactRegistry()
        return _global_registry


def _reset_global_registry() -> None:  # pyright: ignore[reportUnusedFunction]
    """Reset the global registry (for testing only)."""
    global _global_registry
    with _registry_lock:
        _global_registry = None
