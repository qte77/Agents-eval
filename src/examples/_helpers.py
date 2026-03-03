"""Shared utilities for example scripts."""

from typing import Any


def print_mas_result(output: dict[str, Any] | None) -> None:
    """Print MAS example result summary to stdout.

    Args:
        output: Result dict from app.main() with optional 'composite_result' key,
                or None if the run failed.
    """
    if output is not None:
        composite = output.get("composite_result")
        if composite is not None:
            print(f"Composite score  : {composite.composite_score:.3f}")
            print(f"Recommendation   : {composite.recommendation}")
            print(f"Tiers enabled    : {composite.tiers_enabled}")
        else:
            print("Run completed — no composite result produced (eval may be skipped).")
    else:
        print("Run completed — no result returned (download-only or error).")
