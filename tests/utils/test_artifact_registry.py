"""Tests for ArtifactRegistry singleton.

Verifies register, summary, reset, empty state, and thread safety
of the artifact path registry used for end-of-run summaries.
"""

from pathlib import Path


class TestArtifactRegistry:
    """Tests for ArtifactRegistry behavior."""

    def setup_method(self) -> None:
        """Reset global registry before each test."""
        from app.utils.artifact_registry import _reset_global_registry

        _reset_global_registry()

    def test_register_and_summary(self, tmp_path: Path) -> None:
        """Registered artifacts appear in summary with label and absolute path."""
        from app.utils.artifact_registry import get_artifact_registry

        log_path = tmp_path / "log.txt"
        report_path = tmp_path / "report.md"

        registry = get_artifact_registry()
        registry.register("Log file", log_path)
        registry.register("Report", report_path)

        summary = registry.summary()
        assert len(summary) == 2
        assert summary[0] == ("Log file", log_path)
        assert summary[1] == ("Report", report_path)

    def test_summary_returns_absolute_paths(self) -> None:
        """Paths in summary are absolute (AC5)."""
        from app.utils.artifact_registry import get_artifact_registry

        registry = get_artifact_registry()
        registry.register("Trace", Path("relative/trace.jsonl"))

        summary = registry.summary()
        assert len(summary) == 1
        label, path = summary[0]
        assert label == "Trace"
        assert path.is_absolute()

    def test_empty_summary(self) -> None:
        """Empty registry returns empty list (AC4)."""
        from app.utils.artifact_registry import get_artifact_registry

        registry = get_artifact_registry()
        assert registry.summary() == []

    def test_reset_clears_entries(self, tmp_path: Path) -> None:
        """Reset clears all registered artifacts."""
        from app.utils.artifact_registry import get_artifact_registry

        registry = get_artifact_registry()
        registry.register("File", tmp_path / "file.txt")
        assert len(registry.summary()) == 1

        registry.reset()
        assert registry.summary() == []

    def test_singleton_returns_same_instance(self) -> None:
        """get_artifact_registry returns the same instance on repeated calls."""
        from app.utils.artifact_registry import get_artifact_registry

        r1 = get_artifact_registry()
        r2 = get_artifact_registry()
        assert r1 is r2

    def test_format_summary_block_with_artifacts(self) -> None:
        """format_summary_block produces labeled output block (AC3)."""
        from app.utils.artifact_registry import get_artifact_registry

        registry = get_artifact_registry()
        registry.register("Log", Path("/logs/run.log"))
        registry.register("Report", Path("/results/report.md"))

        block = registry.format_summary_block()
        assert "Artifacts written" in block
        assert "/logs/run.log" in block
        assert "/results/report.md" in block
        assert "Log" in block
        assert "Report" in block

    def test_format_summary_block_empty(self) -> None:
        """format_summary_block prints 'No artifacts written' when empty (AC4)."""
        from app.utils.artifact_registry import get_artifact_registry

        registry = get_artifact_registry()
        block = registry.format_summary_block()
        assert "No artifacts written" in block

    def test_thread_safety(self, tmp_path: Path) -> None:
        """Concurrent registration does not lose entries."""
        import threading

        from app.utils.artifact_registry import get_artifact_registry

        registry = get_artifact_registry()
        errors: list[Exception] = []

        def register_batch(prefix: str, count: int) -> None:
            try:
                for i in range(count):
                    registry.register(f"{prefix}-{i}", tmp_path / prefix / f"{i}.txt")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register_batch, args=(f"t{t}", 50)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert len(registry.summary()) == 200
